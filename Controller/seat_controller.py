# Controller/seat_controller.py
#
# SeatController — handles HTTP requests for seat operations.
#
# Flow:
#     HTTP Request -> SeatController -> SeatService / EventService -> SeatDAO / EventDAO -> MySQL

from flask import Blueprint, jsonify
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
def list_seats_for_event(event_id):
    """List active seats for the venue hosting the given event."""
    event_result = event_service.get_event_by_id(event_id)
    if not event_result.get("success"):
        return jsonify(event_result), event_result.get("status", 404)

    venue_id = event_result["data"]["venue_id"]
    result = seat_service.get_available_seats(venue_id)
    return jsonify(result), result.get("status", 200)
