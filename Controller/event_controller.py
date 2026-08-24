# Controller/event_controller.py
#
# EventController — handles HTTP requests for event operations.
#
# Flow:
#     HTTP Request -> EventController -> EventService -> EventDAO -> Event Model -> MySQL

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from Services.event_service import EventService
from Controller.auth_guards import role_required

from api.schemas import EventCreateRequestSchema, EventUpdateRequestSchema, validate_payload

event_bp = Blueprint("event_bp", __name__)
event_service = EventService()


@event_bp.post("")
@jwt_required()
@role_required("admin")
def create_event():
    """Create a new event (Admin only)."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(EventCreateRequestSchema, data)
    if err_resp:
        return err_resp

    # If created_by is omitted, automatically assign current authenticated admin ID
    if "created_by" not in validated_data:
        validated_data["created_by"] = int(get_jwt_identity())

    result = event_service.create_event(validated_data)
    return jsonify(result), result.get("status", 200)


# Specific GET endpoints placed before parameterized /<id> (Public)
@event_bp.get("/upcoming")
def list_upcoming_events():
    """List all upcoming events (Public)."""
    result = event_service.get_upcoming_events()
    return jsonify(result), result.get("status", 200)


@event_bp.get("/category/<int:category_id>")
def list_events_by_category(category_id):
    """List events under a specific category (Public)."""
    result = event_service.get_events_by_category(category_id)
    return jsonify(result), result.get("status", 200)


@event_bp.get("/search")
def search_events():
    """Search events by title keyword (Public)."""
    term = request.args.get("q", "")
    result = event_service.search_events(term)
    return jsonify(result), result.get("status", 200)


@event_bp.get("")
def list_events():
    """List all events (Public)."""
    result = event_service.get_all_events()
    return jsonify(result), result.get("status", 200)


@event_bp.get("/<int:event_id>")
def get_event(event_id):
    """Get a single event by id (Public)."""
    result = event_service.get_event_by_id(event_id)
    return jsonify(result), result.get("status", 200)


@event_bp.put("/<int:event_id>")
@jwt_required()
@role_required("admin")
def update_event(event_id):
    """Update an event (Admin only)."""
    data = request.get_json(silent=True) or {}
    validated_data, err_resp = validate_payload(EventUpdateRequestSchema, data, partial=True)
    if err_resp:
        return err_resp
    result = event_service.update_event(event_id, validated_data)
    return jsonify(result), result.get("status", 200)


@event_bp.delete("/<int:event_id>")
@jwt_required()
@role_required("admin")
def delete_event(event_id):
    """Delete an event (Admin only)."""
    result = event_service.delete_event(event_id)
    return jsonify(result), result.get("status", 200)
