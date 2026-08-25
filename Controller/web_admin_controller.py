# Controller/web_admin_controller.py
#
# WebAdminController — handles Admin Dashboard and Event CRUD management.
#
# Routes:
#   GET /admin/dashboard
#   GET /admin/events
#   GET/POST /admin/events/create
#   GET/POST /admin/events/<event_id>/edit
#   POST /admin/events/<event_id>/delete
#   GET /admin/categories
#   GET /admin/venues
#   GET /admin/bookings
#   GET /admin/analytics

from flask import Blueprint, render_template, request, redirect, url_for
from Services.user_service import UserService
from Services.event_service import EventService
from Services.venue_service import VenueService
from Services.category_service import CategoryService
from Services.booking_service import BookingService
from Services.seat_service import SeatService
from Services.promo_service import PromoCodeService
from Services.analytics_service import AnalyticsService
from Controller.auth_guards import get_current_user_info

web_admin_bp = Blueprint("web_admin_bp", __name__, url_prefix="/admin")
user_service = UserService()
event_service = EventService()
venue_service = VenueService()
category_service = CategoryService()
booking_service = BookingService()
seat_service = SeatService()
promo_service = PromoCodeService()
analytics_service = AnalyticsService()


def _require_admin():
    """Helper to verify current web user is an admin.
    Returns (current_user, None) if authorized, or (None, redirect/error response) if not.
    """
    current_user = get_current_user_info()
    if not current_user:
        return None, redirect(url_for("web_auth_bp.web_login"))
    if current_user.get("role") != "admin":
        return None, (
            render_template(
                "error.html",
                message="You do not have permission to access this resource",
                status_code=403,
            ),
            403,
        )
    return current_user, None


@web_admin_bp.route("/dashboard")
def admin_dashboard():
    """Admin Dashboard showing database overview counts."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    users = user_service.get_all_users().get("data", [])
    events = event_service.get_all_events().get("data", [])
    upcoming = event_service.get_upcoming_events().get("data", [])
    venues = venue_service.get_all_venues().get("data", [])
    categories = category_service.get_all_categories().get("data", [])

    stats = {
        "total_users": len(users),
        "total_events": len(events),
        "upcoming_events": len(upcoming),
        "total_categories": len(categories),
        "total_venues": len(venues),
    }

    return render_template("admin/dashboard.html", stats=stats, recent_events=events[:5])


@web_admin_bp.route("/events")
def admin_events():
    """List all events with management actions."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    events = event_service.get_all_events(include_unpublished=True).get("data", [])
    return render_template("admin/events/index.html", events=events)


@web_admin_bp.route("/events/<int:event_id>/operations", methods=["GET"])
def event_operations(event_id):
    """Event Operations Dashboard for a single selected event."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    ops_res = analytics_service.get_event_operations(event_id)
    if not ops_res.get("success"):
        return render_template("error.html", message=ops_res.get("message", "Event not found"), status_code=404), 404

    ops_data = ops_res.get("data", {})
    return render_template("admin/events/operations.html", ops=ops_data)


@web_admin_bp.route("/events/create", methods=["GET", "POST"])
def create_event():
    """Create a new event."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    error = None
    categories = category_service.get_all_categories().get("data", [])
    venues = venue_service.get_all_venues().get("data", [])

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category_id = request.form.get("category_id")
        venue_id = request.form.get("venue_id")
        event_date = request.form.get("event_date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time") or None
        description = request.form.get("description", "").strip()
        poster = request.form.get("poster", "").strip() or None
        booking_open = request.form.get("booking_open") == "1" or request.form.get("booking_open") == "true" or request.form.get("booking_open") == "on"
        requires_seats = request.form.get("requires_seats") == "1" or request.form.get("requires_seats") == "true" or request.form.get("requires_seats") == "on"
        status = request.form.get("status", "unpublished")
        base_price = request.form.get("base_price") or 0.0

        if status not in ("published", "unpublished"):
            error = "Invalid status. Allowed: published, unpublished"
            return render_template("admin/events/create.html", categories=categories, venues=venues, error=error)

        # Handle local file upload
        poster_file = request.files.get("poster_file")
        uploaded_file_id = None
        if poster_file and poster_file.filename != "":
            from Services.uploaded_file_service import UploadedFileService
            file_res = UploadedFileService().save_poster(poster_file, event_id=None, user_id=admin_user["id"])
            if not file_res.get("success"):
                error = file_res.get("message")
                return render_template(
                    "admin/events/create.html",
                    categories=categories,
                    venues=venues,
                    error=error,
                )
            poster = file_res["data"]["file_path"]
            uploaded_file_id = file_res["data"]["id"]

        data = {
            "title": title,
            "category_id": int(category_id) if category_id else None,
            "venue_id": int(venue_id) if venue_id else None,
            "created_by": admin_user["id"],
            "event_date": event_date,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "poster": poster,
            "booking_open": booking_open,
            "requires_seats": requires_seats,
            "status": status,
            "base_price": float(base_price),
        }

        res = event_service.create_event(data)
        if res.get("success"):
            # Update uploaded file with correct event_id
            if uploaded_file_id:
                from models.uploaded_file import UploadedFile
                from app import db
                db_file = UploadedFile.query.get(uploaded_file_id)
                if db_file:
                    db_file.event_id = res["data"]["id"]
                    db.session.commit()
            
            # Invalidate cache
            from Services.cache_service import invalidate_analytics_cache
            invalidate_analytics_cache()

            return redirect(url_for("web_admin_bp.admin_events"))
        else:
            error = res.get("message")

    return render_template(
        "admin/events/create.html",
        categories=categories,
        venues=venues,
        error=error,
    )


@web_admin_bp.route("/events/<int:event_id>/edit", methods=["GET", "POST"])
def edit_event(event_id):
    """Edit an existing event."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    event_res = event_service.get_event_by_id(event_id, include_unpublished=True)
    if not event_res.get("success"):
        return render_template("error.html", message="Event not found", status_code=404), 404

    event = event_res.get("data", {})
    categories = category_service.get_all_categories().get("data", [])
    venues = venue_service.get_all_venues().get("data", [])
    error = None

    if request.method == "POST":
        poster = request.form.get("poster", "").strip() or event.get("poster")
        
        # Handle local file upload
        poster_file = request.files.get("poster_file")
        if poster_file and poster_file.filename != "":
            from Services.uploaded_file_service import UploadedFileService
            file_res = UploadedFileService().save_poster(poster_file, event_id=event_id, user_id=admin_user["id"])
            if not file_res.get("success"):
                error = file_res.get("message")
                return render_template(
                    "admin/events/edit.html",
                    event=event,
                    categories=categories,
                    venues=venues,
                    error=error,
                )
            poster = file_res["data"]["file_path"]

        status_val = request.form.get("status", "unpublished")
        if status_val not in ("published", "unpublished"):
            error = "Invalid status. Allowed: published, unpublished"
            return render_template(
                "admin/events/edit.html",
                event=event,
                categories=categories,
                venues=venues,
                error=error,
            )

        data = {
            "title": request.form.get("title", "").strip(),
            "category_id": int(request.form.get("category_id")),
            "venue_id": int(request.form.get("venue_id")),
            "event_date": request.form.get("event_date"),
            "start_time": request.form.get("start_time"),
            "end_time": request.form.get("end_time") or None,
            "description": request.form.get("description", "").strip(),
            "poster": poster,
            "booking_open": request.form.get("booking_open") in ["1", "true", "on"],
            "requires_seats": request.form.get("requires_seats") in ["1", "true", "on"],
            "base_price": float(request.form.get("base_price") or 0.0),
            "status": status_val,
        }

        res = event_service.update_event(event_id, data)
        if res.get("success"):
            # Invalidate cache
            from Services.cache_service import invalidate_analytics_cache
            invalidate_analytics_cache()

            return redirect(url_for("web_admin_bp.admin_events"))
        else:
            error = res.get("message")

    return render_template(
        "admin/events/edit.html",
        event=event,
        categories=categories,
        venues=venues,
        error=error,
    )


@web_admin_bp.route("/events/<int:event_id>/reschedule", methods=["GET", "POST"])
def reschedule_event(event_id):
    """Reschedule an existing event with admin password confirmation."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    from Services.event_reschedule_service import EventRescheduleService
    reschedule_service = EventRescheduleService()

    event_res = event_service.get_event_by_id(event_id)
    if not event_res.get("success"):
        return render_template("error.html", message="Event not found", status_code=404), 404

    event = event_res.get("data", {})
    history_res = reschedule_service.get_reschedule_history(event_id)
    history = history_res.get("data", []) if history_res.get("success") else []
    error = None

    if request.method == "POST":
        new_event_date = request.form.get("new_event_date", "").strip()
        new_start_time = request.form.get("new_start_time", "").strip()
        new_end_time = request.form.get("new_end_time", "").strip() or None
        reason = request.form.get("reason", "").strip()
        password = request.form.get("password", "").strip()

        if not password:
            error = "Admin password confirmation is required."
        else:
            result = reschedule_service.reschedule_event(
                event_id=event_id,
                admin_id=admin_user["id"],
                password=password,
                new_event_date=new_event_date,
                new_start_time=new_start_time,
                new_end_time=new_end_time,
                reason=reason,
            )
            if result.get("success"):
                summary = result.get("data", {})
                event_res = event_service.get_event_by_id(event_id)
                event = event_res.get("data", event)
                history_res = reschedule_service.get_reschedule_history(event_id)
                history = history_res.get("data", []) if history_res.get("success") else []
                return render_template(
                    "admin/events/reschedule.html",
                    event=event,
                    history=history,
                    summary=summary,
                    error=None,
                )
            else:
                error = result.get("message", "Rescheduling failed.")

    return render_template(
        "admin/events/reschedule.html",
        event=event,
        history=history,
        summary=None,
        error=error,
    )


@web_admin_bp.route("/events/<int:event_id>/delete", methods=["POST"])
def delete_event(event_id):
    """Delete an event via POST."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    event_service.delete_event(event_id)
    return redirect(url_for("web_admin_bp.admin_events"))


@web_admin_bp.route("/categories")
def admin_categories():
    """Categories management overview."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    categories = category_service.get_all_categories().get("data", [])
    return render_template("admin/categories.html", categories=categories)


@web_admin_bp.route("/venues")
def admin_venues():
    """Venues management overview."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    venues = venue_service.get_all_venues().get("data", [])
    error = request.args.get("error")
    success = request.args.get("success")
    return render_template("admin/venues.html", venues=venues, error=error, success=success)


@web_admin_bp.route("/venues/create", methods=["GET", "POST"])
def create_venue():
    """Create a new venue."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    error = None
    if request.method == "POST":
        data = {
            "name": request.form.get("name", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city": request.form.get("city", "").strip(),
            "state": request.form.get("state", "").strip(),
            "capacity": request.form.get("capacity", "0"),
            "venue_type": request.form.get("venue_type", "seated"),
        }

        res = venue_service.create_venue(data)
        if res.get("success"):
            venue_id = res.get("data", {}).get("id")
            if request.form.get("generate_seats") == "1" or request.form.get("generate_default_seats") == "1":
                num_rows = min(10, max(2, int(request.form.get("initial_rows", 5) or 5)))
                seats_per_row = min(20, max(2, int(request.form.get("initial_seats_per_row", 10) or 10)))
                seat_service.generate_seats_grid(venue_id, num_rows=num_rows, seats_per_row=seats_per_row)
            return redirect(url_for("web_admin_bp.admin_venues", success="Venue created successfully"))
        else:
            error = res.get("message")

    return render_template("admin/venues/create.html", error=error)


@web_admin_bp.route("/venues/<int:venue_id>/edit", methods=["GET", "POST"])
def edit_venue(venue_id):
    """Edit an existing venue."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    venue_res = venue_service.get_venue_by_id(venue_id)
    if not venue_res.get("success"):
        return render_template("error.html", message="Venue not found", status_code=404), 404

    venue = venue_res.get("data", {})
    error = None

    if request.method == "POST":
        data = {
            "name": request.form.get("name", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city": request.form.get("city", "").strip(),
            "state": request.form.get("state", "").strip(),
            "capacity": request.form.get("capacity", "0"),
            "venue_type": request.form.get("venue_type", "seated"),
        }

        res = venue_service.update_venue(venue_id, data)
        if res.get("success"):
            return redirect(url_for("web_admin_bp.admin_venues", success="Venue updated successfully"))
        else:
            error = res.get("message")

    return render_template("admin/venues/edit.html", venue=venue, error=error)


@web_admin_bp.route("/venues/<int:venue_id>/delete", methods=["POST"])
def delete_venue(venue_id):
    """Delete a venue."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    res = venue_service.delete_venue(venue_id)
    if not res.get("success"):
        return redirect(url_for("web_admin_bp.admin_venues", error=res.get("message")))
    return redirect(url_for("web_admin_bp.admin_venues", success="Venue deleted successfully"))


@web_admin_bp.route("/venues/<int:venue_id>/seats", methods=["GET"])
def venue_seats(venue_id):
    """View and configure seats for a venue."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    venue_res = venue_service.get_venue_by_id(venue_id)
    if not venue_res.get("success"):
        return render_template("error.html", message="Venue not found", status_code=404), 404

    venue = venue_res.get("data", {})
    seats_res = seat_service.get_seats_by_venue(venue_id)
    seats = seats_res.get("data", [])

    error = request.args.get("error")
    success = request.args.get("success")

    return render_template(
        "admin/venues/seats.html",
        venue=venue,
        seats=seats,
        error=error,
        success=success,
    )


@web_admin_bp.route("/venues/<int:venue_id>/seats/generate", methods=["POST"])
def generate_venue_seats(venue_id):
    """Generate a grid of seats for a venue."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    num_rows = int(request.form.get("num_rows", 5) or 5)
    seats_per_row = int(request.form.get("seats_per_row", 10) or 10)
    section_name = request.form.get("section_name", "Orchestra").strip()
    seat_type = request.form.get("seat_type", "standard").strip()
    price = float(request.form.get("price", 0.0) or 0.0)

    res = seat_service.generate_seats_grid(
        venue_id=venue_id,
        num_rows=num_rows,
        seats_per_row=seats_per_row,
        section_name=section_name,
        seat_type=seat_type,
        price=price,
    )
    if not res.get("success"):
        return redirect(url_for("web_admin_bp.venue_seats", venue_id=venue_id, error=res.get("message")))
    return redirect(url_for("web_admin_bp.venue_seats", venue_id=venue_id, success=res.get("message")))


@web_admin_bp.route("/venues/<int:venue_id>/seats/create", methods=["POST"])
def create_single_seat(venue_id):
    """Create a single seat for a venue."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    seat_number = request.form.get("seat_number", "").strip()
    section_name = request.form.get("section_name", "General").strip()
    seat_type = request.form.get("seat_type", "standard").strip()
    price = float(request.form.get("price", 0.0) or 0.0)

    res = seat_service.create_seat({
        "venue_id": venue_id,
        "seat_number": seat_number,
        "section_name": section_name,
        "seat_type": seat_type,
        "price": price,
        "is_active": True,
    })
    if not res.get("success"):
        return redirect(url_for("web_admin_bp.venue_seats", venue_id=venue_id, error=res.get("message")))
    return redirect(url_for("web_admin_bp.venue_seats", venue_id=venue_id, success=f"Seat {seat_number} added successfully"))


@web_admin_bp.route("/venues/<int:venue_id>/seats/<int:seat_id>/delete", methods=["POST"])
def delete_single_seat(venue_id, seat_id):
    """Delete a single seat."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    res = seat_service.delete_seat(seat_id)
    if not res.get("success"):
        return redirect(url_for("web_admin_bp.venue_seats", venue_id=venue_id, error=res.get("message")))
    return redirect(url_for("web_admin_bp.venue_seats", venue_id=venue_id, success="Seat deleted successfully"))


@web_admin_bp.route("/venues/<int:venue_id>/seats/clear", methods=["POST"])
def clear_all_seats(venue_id):
    """Clear all seats for a venue."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    res = seat_service.clear_venue_seats(venue_id)
    if not res.get("success"):
        return redirect(url_for("web_admin_bp.venue_seats", venue_id=venue_id, error=res.get("message")))
    return redirect(url_for("web_admin_bp.venue_seats", venue_id=venue_id, success=res.get("message")))


@web_admin_bp.route("/bookings")
def admin_bookings():
    """Bookings management overview."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    bookings_res = booking_service.booking_dao.get_all_bookings()
    all_bookings = []
    for b in bookings_res:
        ev = event_service.get_event_by_id(b.event_id).get("data", {})
        u = user_service.get_user_by_id(b.user_id).get("data", {})
        all_bookings.append({
            "id": b.id,
            "booking_reference": b.booking_reference,
            "event_title": ev.get("title", "Event"),
            "customer_name": u.get("name", "User"),
            "customer_email": u.get("email", ""),
            "total_amount": float(b.total_amount),
            "cashback_amount": float(b.cashback_amount),
            "status": b.status,
            "booked_at": str(b.booked_at)[:10] if b.booked_at else "",
        })

    return render_template("admin/bookings.html", bookings=all_bookings)


@web_admin_bp.route("/analytics")
def admin_analytics():
    """Admin Analytics dashboard with real database metrics."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    days_param = request.args.get("days")
    days = int(days_param) if days_param and days_param.isdigit() else None

    from Services.analytics_service import AnalyticsService
    analytics_service = AnalyticsService()
    analytics_res = analytics_service.get_full_analytics(days=days)
    analytics_data = analytics_res.get("data", {})

    return render_template(
        "admin/analytics.html",
        summary=analytics_data.get("summary", {}),
        top_events=analytics_data.get("top_events", []),
        revenue_by_category=analytics_data.get("revenue_by_category", []),
        sales_over_time=analytics_data.get("sales_over_time", []),
        filter_days=days,
    )


@web_admin_bp.route("/promos")
def admin_promos():
    """Admin Promo Code management page."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    promos_res = promo_service.get_all_promos()
    promos = promos_res.get("data", [])
    return render_template(
        "admin/promos.html",
        promos=promos,
        error=request.args.get("error"),
        success=request.args.get("success"),
    )


@web_admin_bp.route("/promos/create", methods=["POST"])
def admin_create_promo():
    """Create a new promo code via web form."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    code = request.form.get("code", "").strip().upper()
    description = request.form.get("description", "").strip()
    discount_type = request.form.get("discount_type", "percentage")
    discount_value_str = request.form.get("discount_value", "0")
    min_amount_str = request.form.get("minimum_booking_amount", "0")
    max_uses_str = request.form.get("max_uses", "")

    try:
        discount_value = float(discount_value_str)
        min_amount = float(min_amount_str) if min_amount_str else 0.0
        max_uses = int(max_uses_str) if max_uses_str and max_uses_str.isdigit() else None
    except ValueError:
        return redirect(url_for("web_admin_bp.admin_promos", error="Invalid numeric values provided"))

    payload = {
        "code": code,
        "description": description or None,
        "discount_type": discount_type,
        "discount_value": discount_value,
        "minimum_booking_amount": min_amount,
        "max_uses": max_uses,
        "is_active": True,
    }

    res = promo_service.create_promo(payload)
    if not res.get("success"):
        return redirect(url_for("web_admin_bp.admin_promos", error=res.get("message")))
    return redirect(url_for("web_admin_bp.admin_promos", success=f"Promo code '{code}' created successfully"))


@web_admin_bp.route("/promos/<int:promo_id>/toggle", methods=["POST"])
def admin_toggle_promo(promo_id):
    """Toggle promo code active state."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    promo = promo_service.get_promo_by_id(promo_id).get("data", {})
    if not promo:
        return redirect(url_for("web_admin_bp.admin_promos", error="Promo code not found"))

    new_state = not promo.get("is_active", True)
    res = promo_service.update_promo(promo_id, {"is_active": new_state})
    if not res.get("success"):
        return redirect(url_for("web_admin_bp.admin_promos", error=res.get("message")))
    status_label = "activated" if new_state else "deactivated"
    return redirect(url_for("web_admin_bp.admin_promos", success=f"Promo code {status_label}"))


@web_admin_bp.route("/promos/<int:promo_id>/delete", methods=["POST"])
def admin_delete_promo(promo_id):
    """Delete a promo code."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    res = promo_service.delete_promo(promo_id)
    if not res.get("success"):
        return redirect(url_for("web_admin_bp.admin_promos", error=res.get("message")))
    return redirect(url_for("web_admin_bp.admin_promos", success="Promo code deleted successfully"))
