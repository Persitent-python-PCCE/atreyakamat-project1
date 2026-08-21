# Controller/home_controller.py
#
# HomeController — handles the public landing page and health check.

from flask import Blueprint, render_template
from Services.event_service import EventService

home_bp = Blueprint("home_bp", __name__)
event_service = EventService()


@home_bp.route("/")
def index():
    """Render the homepage with featured upcoming events."""
    events_result = event_service.get_upcoming_events()
    upcoming_events = events_result.get("data", []) if events_result.get("success") else []
    return render_template("home.html", events=upcoming_events, title="SeatMeUp - Book Your Seats")


@home_bp.route("/health")
def health():
    """Simple health check endpoint."""
    return {"status": "ok", "project": "SeatMeUp"}
