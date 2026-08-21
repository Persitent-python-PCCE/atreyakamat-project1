# api/booking_routes.py
#
# CONTROLLER for bookings.
#
# URL prefix for this blueprint is `/api` (see api/__init__.py), so the full
# paths are:
#
#   POST   /api/bookings                       create a booking
#   GET    /api/bookings/<id>
#   GET    /api/bookings/reference/<reference>
#   GET    /api/users/<user_id>/bookings
#   PUT    /api/bookings/<id>
#   DELETE /api/bookings/<id>
#
# Booking workflows (totals, holds release, ticket creation, cashback,
# email) are deferred to a later phase. This controller exposes the basic
# row operations only.

from flask import Blueprint, request, jsonify

from Services import BookingService

booking_bp = Blueprint("booking_bp", __name__)
booking_service = BookingService()


@booking_bp.post("/bookings")
def create_booking():
    data = request.get_json(silent=True) or {}
    result = booking_service.create_booking(data)
    return jsonify(result), result.get("status", 200)


@booking_bp.get("/bookings/<int:booking_id>")
def get_booking(booking_id):
    result = booking_service.get_booking_by_id(booking_id)
    return jsonify(result), result.get("status", 200)


@booking_bp.get("/bookings/reference/<string:reference>")
def get_booking_by_reference(reference):
    result = booking_service.get_booking_by_reference(reference)
    return jsonify(result), result.get("status", 200)


@booking_bp.get("/users/<int:user_id>/bookings")
def list_user_bookings(user_id):
    result = booking_service.get_user_bookings(user_id)
    return jsonify(result), result.get("status", 200)


@booking_bp.put("/bookings/<int:booking_id>")
def update_booking(booking_id):
    data = request.get_json(silent=True) or {}
    result = booking_service.update_booking(booking_id, data)
    return jsonify(result), result.get("status", 200)


@booking_bp.delete("/bookings/<int:booking_id>")
def delete_booking(booking_id):
    result = booking_service.delete_booking(booking_id)
    return jsonify(result), result.get("status", 200)
