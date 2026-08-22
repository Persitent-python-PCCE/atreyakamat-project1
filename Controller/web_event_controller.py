# Controller/web_event_controller.py
#
# WebEventController — handles HTML pages for browsing events, viewing details,
# and the interactive Seat Selection & 1-minute Seat Hold workflow.
#
# Routes:
#   GET  /events                                     -> Explore and search events
#   GET  /events/<event_id>                          -> View event details
#   GET  /events/<event_id>/seats                    -> Seat selection & seat map page
#   GET  /events/<event_id>/book                     -> Alias for seat selection
#   POST /events/<event_id>/seats/<seat_id>/hold     -> Hold seat action
#   POST /events/<event_id>/seats/<seat_id>/release  -> Release seat action
#   GET  /events/<event_id>/checkout                 -> Continue to checkout placeholder

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from Services.event_service import EventService
from Services.category_service import CategoryService
from Services.venue_service import VenueService
from Services.seat_service import SeatService
from Controller.auth_guards import get_current_user_info

web_event_bp = Blueprint("web_event_bp", __name__)
event_service = EventService()
category_service = CategoryService()
venue_service = VenueService()
seat_service = SeatService()


@web_event_bp.route("/events")
def list_events():
    """Browse events with optional keyword search and category filter."""
    search_query = (request.args.get("search") or request.args.get("q") or "").strip()
    category_filter = (request.args.get("category") or "").strip()

    # Load categories for filter tabs
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

    # Load category and venue for display
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

    # Load seat map for this event and user
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


@web_event_bp.route("/events/<int:event_id>/checkout")
def checkout_placeholder(event_id):
    """Placeholder checkout page leading from seat selection."""
    current_user = get_current_user_info()
    if not current_user:
        return redirect(url_for("web_auth_bp.web_login"))

    event_res = event_service.get_event_by_id(event_id)
    if not event_res.get("success"):
        return render_template("error.html", message="Event not found", status_code=404), 404

    event = event_res.get("data", {})

    # Fetch currently held seats by this user
    holds_res = seat_service.get_user_active_holds(user_id=current_user["id"], event_id=event_id)
    held_items = holds_res.get("data", []) if holds_res.get("success") else []

    if not held_items:
        return redirect(url_for("web_event_bp.select_seats", event_id=event_id))

    return render_template(
        "events/checkout_preview.html",
        event=event,
        holds=held_items,
        user=current_user,
    )
