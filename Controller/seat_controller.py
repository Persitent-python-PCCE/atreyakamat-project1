# Controller/seat_controller.py
#
# SeatController — handles HTTP REST API requests for seats and 1-minute seat holds.
#
# Routes:
#   GET  /api/venues/<venue_id>/seats
#   GET  /api/events/<event_id>/seats
#   GET  /api/events/<event_id>/seat-map
#   POST /api/events/<event_id>/seats/<seat_id>/hold
#   POST /api/events/<event_id>/seats/<seat_id>/release
#   GET  /api/seats/my-holds

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from Services.seat_service import SeatService
from Services.event_service import EventService

seat_bp = Blueprint("seat_bp", __name__)
seat_service = SeatService()
event_service = EventService()


@seat_bp.get("/venues/<int:venue_id>/seats")
def list_seats_by_venue(venue_id):
    """List all configured seats for a venue."""
    result = seat_service.get_seats_by_venue(venue_id)
    return jsonify(result), result.get("status", 200)


@seat_bp.get("/events/<int:event_id>/seats")
@seat_bp.get("/events/<int:event_id>/seat-map")
def get_event_seat_map(event_id):
    """Get dynamic seat map for an event with availability and hold states."""
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = int(identity)
    except Exception:
        pass

    result = seat_service.get_event_seat_map(event_id, user_id=user_id)
    return jsonify(result), result.get("status", 200)


@seat_bp.post("/events/<int:event_id>/seats/<int:seat_id>/hold")
@jwt_required()
def hold_seat(event_id, seat_id):
    """Place a 1-minute hold on a seat for the authenticated user."""
    user_id = int(get_jwt_identity())
    result = seat_service.hold_seat(event_id=event_id, seat_id=seat_id, user_id=user_id)
    return jsonify(result), result.get("status", 200)


@seat_bp.post("/events/<int:event_id>/seats/<int:seat_id>/release")
@jwt_required()
def release_seat(event_id, seat_id):
    """Release a held seat for the authenticated user."""
    user_id = int(get_jwt_identity())
    result = seat_service.release_seat_hold(event_id=event_id, seat_id=seat_id, user_id=user_id)
    return jsonify(result), result.get("status", 200)


@seat_bp.get("/seats/my-holds")
@jwt_required()
def get_my_holds():
    """List all active holds for the authenticated user."""
    user_id = int(get_jwt_identity())
    event_id = request.args.get("event_id", type=int)
    result = seat_service.get_user_active_holds(user_id=user_id, event_id=event_id)
    return jsonify(result), result.get("status", 200)
