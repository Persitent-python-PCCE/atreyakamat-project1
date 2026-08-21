# Controller/booking_controller.py
#
# BookingController — handles HTTP requests for booking operations.
#
# Flow:
#     HTTP Request -> BookingController -> BookingService -> BookingDAO -> Booking Model -> MySQL

from flask import Blueprint, request, jsonify
from Services.booking_service import BookingService

booking_bp = Blueprint("booking_bp", __name__)
booking_service = BookingService()


@booking_bp.post("/bookings")
def create_booking():
    """Create a new booking."""
    data = request.get_json(silent=True) or {}
    result = booking_service.create_booking(data)
    return jsonify(result), result.get("status", 200)


@booking_bp.get("/bookings/<int:booking_id>")
def get_booking(booking_id):
    """Get a booking by id."""
    result = booking_service.get_booking_by_id(booking_id)
    return jsonify(result), result.get("status", 200)


@booking_bp.get("/bookings/reference/<string:reference>")
def get_booking_by_reference(reference):
    """Get a booking by its unique reference string."""
    result = booking_service.get_booking_by_reference(reference)
    return jsonify(result), result.get("status", 200)


@booking_bp.get("/users/<int:user_id>/bookings")
def list_user_bookings(user_id):
    """List all bookings for a user."""
    result = booking_service.get_user_bookings(user_id)
    return jsonify(result), result.get("status", 200)


@booking_bp.put("/bookings/<int:booking_id>")
def update_booking(booking_id):
    """Update a booking."""
    data = request.get_json(silent=True) or {}
    result = booking_service.update_booking(booking_id, data)
    return jsonify(result), result.get("status", 200)


@booking_bp.delete("/bookings/<int:booking_id>")
def delete_booking(booking_id):
    """Delete a booking."""
    result = booking_service.delete_booking(booking_id)
    return jsonify(result), result.get("status", 200)
