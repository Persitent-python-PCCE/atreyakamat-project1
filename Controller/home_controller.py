# Controller/home_controller.py
#
# HomeController — handles the public landing page and health check.

from flask import Blueprint, render_template
from Services.event_service import EventService
from Services.category_service import CategoryService

home_bp = Blueprint("home_bp", __name__)
event_service = EventService()
category_service = CategoryService()


@home_bp.route("/")
def index():
    """Render the homepage with hero, search, categories, and upcoming events."""
    events_result = event_service.get_upcoming_events()
    upcoming_events = events_result.get("data", []) if events_result.get("success") else []

    categories_result = category_service.get_all_categories()
    categories = categories_result.get("data", []) if categories_result.get("success") else []

    return render_template(
        "home.html",
        events=upcoming_events,
        categories=categories,
        title="SeatMeUp - Smart Event Ticket Booking & Seat Selection",
    )


@home_bp.route("/health")
def health():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "SeatMeUp"}
