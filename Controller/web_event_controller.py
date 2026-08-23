# Controller/web_event_controller.py
#
# WebEventController — handles HTML pages for browsing events, details,
# interactive seat selection, checkout, promo application, and booking confirmation.

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from Services.event_service import EventService
from Services.category_service import CategoryService
from Services.venue_service import VenueService
from Services.seat_service import SeatService
from Services.booking_service import BookingService
from Services.promo_service import PromoCodeService
from DAO import EventAddonDAO
from Controller.auth_guards import get_current_user_info

web_event_bp = Blueprint("web_event_bp", __name__)
event_service = EventService()
category_service = CategoryService()
venue_service = VenueService()
seat_service = SeatService()
booking_service = BookingService()
promo_service = PromoCodeService()
event_addon_dao = EventAddonDAO()


@web_event_bp.route("/events")
def list_events():
    """Browse events with optional keyword search and category filter."""
    search_query = (request.args.get("search") or request.args.get("q") or "").strip()
    category_filter = (request.args.get("category") or "").strip()

    cat_result = category_service.get_all_categories()
    categories = cat_result.get("data", []) if cat_result.get("success") else []

    if category_filter:
        result = event_service.get_events_by_category(category_filter)
    elif search_query:
        result = event_service.search_events(search_query)
    else:
        result = event_service.get_all_events()

    events = result.get("data", []) if result.get("success") else []

    return render_template(
        "events/index.html",
        events=events,
        categories=categories,
        search_query=search_query,
        active_category=category_filter,
    )


@web_event_bp.route("/events/<int:event_id>")
def event_detail(event_id):
    """View details of a single event."""
    result = event_service.get_event_by_id(event_id)
    if not result.get("success"):
        return render_template("error.html", message="Event not found", status_code=404), 404

    event = result.get("data", {})

    category = None
    venue = None
    if event.get("category_id"):
        cat_res = category_service.get_category_by_id(event["category_id"])
        if cat_res.get("success"):
            category = cat_res.get("data")

    if event.get("venue_id"):
        ven_res = venue_service.get_venue_by_id(event["venue_id"])
        if ven_res.get("success"):
            venue = ven_res.get("data")

    return render_template(
        "events/details.html",
        event=event,
        category=category,
        venue=venue,
    )


@web_event_bp.route("/events/<int:event_id>/seats")
@web_event_bp.route("/events/<int:event_id>/book")
def select_seats(event_id):
    """Seat Selection page showing visual seat map and 1-minute holds."""
    current_user = get_current_user_info()
    if not current_user:
        return redirect(url_for("web_auth_bp.web_login", next=f"/events/{event_id}/seats"))

    event_res = event_service.get_event_by_id(event_id)
    if not event_res.get("success"):
        return render_template("error.html", message="Event not found", status_code=404), 404

    event = event_res.get("data", {})

    seat_map_res = seat_service.get_event_seat_map(event_id, user_id=current_user["id"])
    seat_data = seat_map_res.get("data", {}) if seat_map_res.get("success") else {"seats": [], "summary": {}}

    venue_res = venue_service.get_venue_by_id(event.get("venue_id"))
    venue = venue_res.get("data") if venue_res.get("success") else None

    return render_template(
        "events/seat_selection.html",
        event=event,
        venue=venue,
        seats=seat_data.get("seats", []),
        summary=seat_data.get("summary", {}),
    )


@web_event_bp.route("/events/<int:event_id>/seats/<int:seat_id>/hold", methods=["POST"])
def web_hold_seat(event_id, seat_id):
    """Web action to hold a seat for 1 minute."""
    current_user = get_current_user_info()
    if not current_user:
        if request.is_json:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return redirect(url_for("web_auth_bp.web_login"))

    result = seat_service.hold_seat(event_id=event_id, seat_id=seat_id, user_id=current_user["id"])

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(result), result.get("status", 200)

    return redirect(url_for("web_event_bp.select_seats", event_id=event_id))


@web_event_bp.route("/events/<int:event_id>/seats/<int:seat_id>/release", methods=["POST"])
def web_release_seat(event_id, seat_id):
    """Web action to release a held seat."""
    current_user = get_current_user_info()
    if not current_user:
        if request.is_json:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return redirect(url_for("web_auth_bp.web_login"))

    result = seat_service.release_seat_hold(event_id=event_id, seat_id=seat_id, user_id=current_user["id"])

    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(result), result.get("status", 200)

    return redirect(url_for("web_event_bp.select_seats", event_id=event_id))


# ---------------------------------------------------------------- #
# CHECKOUT & BOOKING WEB PAGES
# ---------------------------------------------------------------- #
@web_event_bp.route("/events/<int:event_id>/checkout", methods=["GET", "POST"])
def checkout_page(event_id):
    """Checkout page: Review order, select add-ons, apply promo code, view 2% cashback, and confirm booking."""
    current_user = get_current_user_info()
    if not current_user:
        return redirect(url_for("web_auth_bp.web_login", next=f"/events/{event_id}/checkout"))

    # Extract user selections from query parameters or POST form
    promo_code = (request.form.get("promo_code") or request.args.get("promo_code") or "").strip()

    selected_addons = {}
    if request.method == "POST":
        for key, val in request.form.items():
            if key.startswith("addon_"):
                addon_id = key.replace("addon_", "")
                try:
                    qty = int(val)
                    if qty > 0:
                        selected_addons[addon_id] = qty
                except ValueError:
                    pass
    else:
        for key, val in request.args.items():
            if key.startswith("addon_"):
                addon_id = key.replace("addon_", "")
                try:
                    qty = int(val)
                    if qty > 0:
                        selected_addons[addon_id] = qty
                except ValueError:
                    pass

    # Process Confirm Booking POST action
    if request.method == "POST" and request.form.get("action") == "confirm_booking":
        booking_result = booking_service.confirm_booking(
            user_id=current_user["id"],
            event_id=event_id,
            selected_addons=selected_addons,
            promo_code=promo_code if promo_code else None,
        )

        if booking_result.get("success"):
            ref = booking_result["data"]["booking_reference"]
            return redirect(url_for("web_event_bp.booking_success", booking_reference=ref))
        else:
            error_msg = booking_result.get("message", "Booking confirmation failed")
            # If hold expired, redirect to seat selection with message
            if "expired" in error_msg.lower() or "hold" in error_msg.lower():
                flash(error_msg, "error")
                return redirect(url_for("web_event_bp.select_seats", event_id=event_id))

            # Otherwise re-render checkout with error
            calc_res = booking_service.get_checkout_preview(
                user_id=current_user["id"],
                event_id=event_id,
                promo_code=promo_code if promo_code else None,
                selected_addons=selected_addons,
            )
            calc_data = calc_res.get("data", {}) if calc_res.get("success") else {}
            event_res = event_service.get_event_by_id(event_id)
            event = event_res.get("data", {})
            return render_template(
                "events/checkout.html",
                event=event,
                checkout=calc_data,
                user=current_user,
                promo_code=promo_code,
                error=error_msg,
            )

    # Calculate live checkout preview
    calc_res = booking_service.get_checkout_preview(
        user_id=current_user["id"],
        event_id=event_id,
        promo_code=promo_code if promo_code else None,
        selected_addons=selected_addons,
    )

    if not calc_res.get("success"):
        # If no active holds or hold expired, redirect back to seat selection
        flash(calc_res.get("message", "Seat hold expired or unavailable"), "warning")
        return redirect(url_for("web_event_bp.select_seats", event_id=event_id))

    calc_data = calc_res.get("data", {})
    event_res = event_service.get_event_by_id(event_id)
    event = event_res.get("data", {})

    return render_template(
        "events/checkout.html",
        event=event,
        checkout=calc_data,
        user=current_user,
        promo_code=promo_code,
        error=None,
    )


@web_event_bp.route("/bookings/<string:booking_reference>")
@web_event_bp.route("/events/booking-success/<string:booking_reference>")
def booking_success(booking_reference):
    """Booking success confirmation page."""
    current_user = get_current_user_info()
    if not current_user:
        return redirect(url_for("web_auth_bp.web_login"))

    result = booking_service.get_booking_by_reference(booking_reference)
    if not result.get("success"):
        return render_template("error.html", message="Booking not found", status_code=404), 404

    booking_data = result.get("data", {})

    # Check ownership
    if current_user["role"] != "admin" and booking_data.get("user_id") != current_user["id"]:
        return render_template("error.html", message="You do not have permission to view this booking", status_code=403), 403

    return render_template(
        "events/booking_success.html",
        booking=booking_data,
        user=current_user,
    )


@web_event_bp.route("/my-bookings")
def my_bookings():
    """Customer My Bookings list page."""
    current_user = get_current_user_info()
    if not current_user:
        return redirect(url_for("web_auth_bp.web_login", next="/my-bookings"))

    result = booking_service.get_user_bookings(current_user["id"])
    bookings = result.get("data", []) if result.get("success") else []

    return render_template(
        "events/my_bookings.html",
        bookings=bookings,
        user=current_user,
    )


# ---------------------------------------------------------------- #
# TICKET VIEW & QR CODE VERIFICATION ROUTES
# ---------------------------------------------------------------- #
@web_event_bp.route("/tickets/<string:ticket_token>")
def view_ticket(ticket_token):
    """Customer-facing View Ticket page with QR Code."""
    current_user = get_current_user_info()
    if not current_user:
        return redirect(url_for("web_auth_bp.web_login", next=f"/tickets/{ticket_token}"))

    from Services.ticket_service import TicketService
    ticket_svc = TicketService()
    res = ticket_svc.get_ticket_details_by_token(ticket_token)
    if not res.get("success"):
        return render_template("error.html", message="Ticket not found", status_code=404), 404

    ticket_data = res["data"]
    # Check ownership
    booking_res = booking_service.get_booking_by_id(ticket_data["booking_id"])
    if booking_res.get("success"):
        b_data = booking_res["data"]
        if current_user["role"] != "admin" and b_data.get("user_id") != current_user["id"]:
            return render_template("error.html", message="You do not have permission to view this ticket", status_code=403), 403

    return render_template(
        "tickets/view.html",
        ticket=ticket_data,
        user=current_user,
    )


@web_event_bp.route("/bookings/<string:booking_reference>/ticket")
def view_ticket_by_booking(booking_reference):
    """Redirect to ticket view from booking reference."""
    booking_res = booking_service.get_booking_by_reference(booking_reference)
    if not booking_res.get("success"):
        return render_template("error.html", message="Booking not found", status_code=404), 404

    b_data = booking_res["data"]
    token = b_data.get("ticket_token")
    if not token:
        # Generate ticket if not already generated
        from Services.ticket_service import TicketService
        ticket_svc = TicketService()
        t_res = ticket_svc.create_ticket_for_booking(b_data["id"])
        if t_res.get("success"):
            token = t_res["data"]["ticket_token"]
        else:
            return render_template("error.html", message="Ticket could not be generated", status_code=500), 500

    return redirect(url_for("web_event_bp.view_ticket", ticket_token=token))


@web_event_bp.route("/verify/<string:ticket_token>")
def verify_ticket_web(ticket_token):
    """Door scanner verification route for ticket tokens."""
    from Services.ticket_service import TicketService
    ticket_svc = TicketService()
    result = ticket_svc.validate_and_verify_ticket(ticket_token, mark_as_used=True)

    if result.get("success"):
        # Success: Show clear Ticket Verified Successfully page
        return render_template(
            "tickets/verified.html",
            verification=result["data"],
        )
    else:
        # Failure: Redirect/Render existing common failure page with error message
        status_code = result.get("status", 400)
        return render_template(
            "error.html",
            message=result.get("message", "Ticket verification failed"),
            status_code=status_code,
        ), status_code
