# Controller/venue_controller.py
#
# VenueController — handles HTTP requests for venue operations.
#
# Flow:
#     HTTP Request -> VenueController -> VenueService -> VenueDAO -> Venue Model -> MySQL

from flask import Blueprint, request, jsonify
from Services.venue_service import VenueService

venue_bp = Blueprint("venue_bp", __name__)
venue_service = VenueService()


@venue_bp.post("")
def create_venue():
    """Create a new venue.

    Request Body (JSON):
        name (required), address (required), city, state, capacity, venue_type
    """
    data = request.get_json(silent=True) or {}
    result = venue_service.create_venue(data)
    return jsonify(result), result.get("status", 200)


@venue_bp.get("")
def list_venues():
    """List all venues."""
    result = venue_service.get_all_venues()
    return jsonify(result), result.get("status", 200)


@venue_bp.get("/<int:venue_id>")
def get_venue(venue_id):
    """Get a single venue by id."""
    result = venue_service.get_venue_by_id(venue_id)
    return jsonify(result), result.get("status", 200)


@venue_bp.put("/<int:venue_id>")
def update_venue(venue_id):
    """Update a venue."""
    data = request.get_json(silent=True) or {}
    result = venue_service.update_venue(venue_id, data)
    return jsonify(result), result.get("status", 200)


@venue_bp.delete("/<int:venue_id>")
def delete_venue(venue_id):
    """Delete a venue."""
    result = venue_service.delete_venue(venue_id)
    return jsonify(result), result.get("status", 200)
