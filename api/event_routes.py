# api/event_routes.py
#
# CONTROLLER for events. Route ordering note: special fixed-string GET routes
# (/upcoming, /category/<int>, /search) must be declared BEFORE /<int:event_id>,
# or Flask would match the int path first.
#
# Endpoints:
#   POST   /api/events
#   GET    /api/events
#   GET    /api/events/<id>
#   PUT    /api/events/<id>
#   DELETE /api/events/<id>
#   GET    /api/events/upcoming
#   GET    /api/events/category/<category_id>
#   GET    /api/events/search?q=<search_term>

from flask import Blueprint, request, jsonify

from Services import EventService

event_bp = Blueprint("event_bp", __name__)
event_service = EventService()


@event_bp.post("")
def create_event():
    data = request.get_json(silent=True) or {}
    result = event_service.create_event(data)
    return jsonify(result), result.get("status", 200)


# --- special GET routes (declared first on purpose) ---
@event_bp.get("/upcoming")
def list_upcoming_events():
    result = event_service.get_upcoming_events()
    return jsonify(result), result.get("status", 200)


@event_bp.get("/category/<int:category_id>")
def list_events_by_category(category_id):
    result = event_service.get_events_by_category(category_id)
    return jsonify(result), result.get("status", 200)


@event_bp.get("/search")
def search_events():
    term = request.args.get("q", "")
    result = event_service.search_events(term)
    return jsonify(result), result.get("status", 200)


@event_bp.get("")
def list_events():
    result = event_service.get_all_events()
    return jsonify(result), result.get("status", 200)


@event_bp.get("/<int:event_id>")
def get_event(event_id):
    result = event_service.get_event_by_id(event_id)
    return jsonify(result), result.get("status", 200)


@event_bp.put("/<int:event_id>")
def update_event(event_id):
    data = request.get_json(silent=True) or {}
    result = event_service.update_event(event_id, data)
    return jsonify(result), result.get("status", 200)


@event_bp.delete("/<int:event_id>")
def delete_event(event_id):
    result = event_service.delete_event(event_id)
    return jsonify(result), result.get("status", 200)
