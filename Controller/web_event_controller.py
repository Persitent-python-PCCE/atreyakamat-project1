# Controller/web_event_controller.py
#
# WebEventController — handles HTML pages for browsing and viewing events.
#
# Routes:
#   GET /events               -> Browse and search events
#   GET /events/<event_id>    -> View event details

from flask import Blueprint, render_template, request
from Services.event_service import EventService
from Services.category_service import CategoryService
from Services.venue_service import VenueService

web_event_bp = Blueprint("web_event_bp", __name__)
event_service = EventService()
category_service = CategoryService()
venue_service = VenueService()


@web_event_bp.route("/events")
def list_events():
    """Browse events with optional keyword search."""
    search_query = request.args.get("search") or request.args.get("q") or ""
    if search_query.strip():
        result = event_service.search_events(search_query.strip())
    else:
        result = event_service.get_all_events()

    events = result.get("data", []) if result.get("success") else []
    return render_template("events/events.html", events=events, search_query=search_query)


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
        "events/event_detail.html",
        event=event,
        category=category,
        venue=venue,
    )
