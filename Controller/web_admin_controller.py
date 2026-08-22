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
from Controller.auth_guards import get_current_user_info

web_admin_bp = Blueprint("web_admin_bp", __name__, url_prefix="/admin")
user_service = UserService()
event_service = EventService()
venue_service = VenueService()
category_service = CategoryService()
booking_service = BookingService()


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

    events = event_service.get_all_events().get("data", [])
    upcoming = event_service.get_upcoming_events().get("data", [])
    venues = venue_service.get_all_venues().get("data", [])
    categories = category_service.get_all_categories().get("data", [])

    stats = {
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

    events = event_service.get_all_events().get("data", [])
    return render_template("admin/events/index.html", events=events)


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
        status = request.form.get("status", "published")
        base_price = request.form.get("base_price") or 0.0

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

    event_res = event_service.get_event_by_id(event_id)
    if not event_res.get("success"):
        return render_template("error.html", message="Event not found", status_code=404), 404

    event = event_res.get("data", {})
    categories = category_service.get_all_categories().get("data", [])
    venues = venue_service.get_all_venues().get("data", [])
    error = None

    if request.method == "POST":
        data = {
            "title": request.form.get("title", "").strip(),
            "category_id": int(request.form.get("category_id")),
            "venue_id": int(request.form.get("venue_id")),
            "event_date": request.form.get("event_date"),
            "start_time": request.form.get("start_time"),
            "end_time": request.form.get("end_time") or None,
            "description": request.form.get("description", "").strip(),
            "poster": request.form.get("poster", "").strip() or None,
            "booking_open": request.form.get("booking_open") in ["1", "true", "on"],
            "requires_seats": request.form.get("requires_seats") in ["1", "true", "on"],
            "base_price": float(request.form.get("base_price") or 0.0),
            "status": request.form.get("status", "published"),
        }

        res = event_service.update_event(event_id, data)
        if res.get("success"):
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
    return render_template("admin/venues.html", venues=venues)


@web_admin_bp.route("/bookings")
def admin_bookings():
    """Bookings management overview."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    return render_template("admin/bookings.html")


@web_admin_bp.route("/analytics")
def admin_analytics():
    """Analytics placeholder page."""
    admin_user, err_resp = _require_admin()
    if err_resp:
        return err_resp

    return render_template("admin/analytics.html")
