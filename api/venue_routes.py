# api/venue_routes.py
#
# CONTROLLER for venues.
#
#   POST   /api/venues
#   GET    /api/venues
#   GET    /api/venues/<id>
#   PUT    /api/venues/<id>
#   DELETE /api/venues/<id>

from flask import Blueprint, request, jsonify

from Services import VenueService

venue_bp = Blueprint("venue_bp", __name__)
venue_service = VenueService()


@venue_bp.post("")
def create_venue():
    data = request.get_json(silent=True) or {}
    result = venue_service.create_venue(data)
    return jsonify(result), result.get("status", 200)


@venue_bp.get("")
def list_venues():
    result = venue_service.get_all_venues()
    return jsonify(result), result.get("status", 200)


@venue_bp.get("/<int:venue_id>")
def get_venue(venue_id):
    result = venue_service.get_venue_by_id(venue_id)
    return jsonify(result), result.get("status", 200)


@venue_bp.put("/<int:venue_id>")
def update_venue(venue_id):
    data = request.get_json(silent=True) or {}
    result = venue_service.update_venue(venue_id, data)
    return jsonify(result), result.get("status", 200)


@venue_bp.delete("/<int:venue_id>")
def delete_venue(venue_id):
    result = venue_service.delete_venue(venue_id)
    return jsonify(result), result.get("status", 200)
