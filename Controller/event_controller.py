# Controller/event_controller.py
#
# EventController — handles HTTP requests for event operations.
#
# Flow:
#     HTTP Request -> EventController -> EventService -> EventDAO -> Event Model -> MySQL

from flask import Blueprint, request, jsonify
from Services.event_service import EventService

event_bp = Blueprint("event_bp", __name__)
event_service = EventService()


@event_bp.post("")
def create_event():
    """Create a new event."""
    data = request.get_json(silent=True) or {}
    result = event_service.create_event(data)
    return jsonify(result), result.get("status", 200)


# Specific GET endpoints placed before parameterized /<id>
@event_bp.get("/upcoming")
def list_upcoming_events():
    """List all upcoming events."""
    result = event_service.get_upcoming_events()
    return jsonify(result), result.get("status", 200)


@event_bp.get("/category/<int:category_id>")
def list_events_by_category(category_id):
    """List events under a specific category."""
    result = event_service.get_events_by_category(category_id)
    return jsonify(result), result.get("status", 200)


@event_bp.get("/search")
def search_events():
    """Search events by title keyword."""
    term = request.args.get("q", "")
    result = event_service.search_events(term)
    return jsonify(result), result.get("status", 200)


@event_bp.get("")
def list_events():
    """List all events."""
    result = event_service.get_all_events()
    return jsonify(result), result.get("status", 200)


@event_bp.get("/<int:event_id>")
def get_event(event_id):
    """Get a single event by id."""
    result = event_service.get_event_by_id(event_id)
    return jsonify(result), result.get("status", 200)


@event_bp.put("/<int:event_id>")
def update_event(event_id):
    """Update an event."""
    data = request.get_json(silent=True) or {}
    result = event_service.update_event(event_id, data)
    return jsonify(result), result.get("status", 200)


@event_bp.delete("/<int:event_id>")
def delete_event(event_id):
    """Delete an event."""
    result = event_service.delete_event(event_id)
    return jsonify(result), result.get("status", 200)
