# api/seat_routes.py
#
# CONTROLLER for seats.
#
# URL prefix for this blueprint is `/api` (see api/__init__.py), so the full
# paths are:
#
#   GET /api/venues/<venue_id>/seats       -> list all seats of a venue
#   GET /api/events/<event_id>/seats       -> list seats available for an event

from flask import Blueprint, jsonify

from Services import SeatService, EventService

seat_bp = Blueprint("seat_bp", __name__)
seat_service = SeatService()
event_service = EventService()


@seat_bp.get("/venues/<int:venue_id>/seats")
def list_seats_by_venue(venue_id):
    result = seat_service.get_seats_by_venue(venue_id)
    return jsonify(result), result.get("status", 200)


@seat_bp.get("/events/<int:event_id>/seats")
def list_seats_for_event(event_id):
    """Return the basic available-seat list for an event.

    The event_id needs to exist; we look up the event via EventService and,
    if found, return that venue's active seats via SeatService. This is the
    beginner-friendly cross-model coordination: the controller composes two
    services instead of one of them secretly calling the other's DAO.
    """
    event_result = event_service.get_event_by_id(event_id)
    if not event_result["success"]:
        # Event not found -> 404, pass through as-is.
        return jsonify(event_result), event_result.get("status", 404)

    venue_id = event_result["data"]["venue_id"]
    result = seat_service.get_available_seats(venue_id)
    return jsonify(result), result.get("status", 200)
