# Controller/booking_controller.py
#
# BookingController — handles HTTP requests for booking operations.
#
# Flow:
#     HTTP Request -> BookingController -> BookingService -> BookingDAO -> Booking Model -> MySQL

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Services.booking_service import BookingService
from Controller.auth_guards import role_required

booking_bp = Blueprint("booking_bp", __name__)
booking_service = BookingService()


@booking_bp.post("/bookings")
@jwt_required()
def create_booking():
    """Create a new booking for the authenticated user."""
    data = request.get_json(silent=True) or {}
    # Enforce user ownership: user_id always comes from the verified JWT identity
    data["user_id"] = int(get_jwt_identity())

    result = booking_service.create_booking(data)
    return jsonify(result), result.get("status", 200)


@booking_bp.get("/bookings/my")
@jwt_required()
def get_my_bookings():
    """Get all bookings belonging to the currently authenticated user."""
    current_user_id = int(get_jwt_identity())
    result = booking_service.get_user_bookings(current_user_id)
    return jsonify(result), result.get("status", 200)


@booking_bp.get("/bookings/<int:booking_id>")
@jwt_required()
def get_booking(booking_id):
    """Get a booking by id (Must be owner or admin)."""
    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    result = booking_service.get_booking_by_id(booking_id)
    if not result.get("success"):
        return jsonify(result), result.get("status", 404)

    # Check ownership
    booking_data = result.get("data", {})
    if current_role != "admin" and booking_data.get("user_id") != current_user_id:
        return jsonify({
            "success": False,
            "message": "You do not have permission to access this resource"
        }), 403

    return jsonify(result), result.get("status", 200)


@booking_bp.get("/bookings/reference/<string:reference>")
@jwt_required()
def get_booking_by_reference(reference):
    """Get a booking by reference."""
    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    result = booking_service.get_booking_by_reference(reference)
    if not result.get("success"):
        return jsonify(result), result.get("status", 404)

    booking_data = result.get("data", {})
    if current_role != "admin" and booking_data.get("user_id") != current_user_id:
        return jsonify({
            "success": False,
            "message": "You do not have permission to access this resource"
        }), 403

    return jsonify(result), result.get("status", 200)


@booking_bp.get("/users/<int:user_id>/bookings")
@jwt_required()
def list_user_bookings(user_id):
    """List all bookings for a user (Must be owner or admin)."""
    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    if current_role != "admin" and current_user_id != user_id:
        return jsonify({
            "success": False,
            "message": "You do not have permission to access this resource"
        }), 403

    result = booking_service.get_user_bookings(user_id)
    return jsonify(result), result.get("status", 200)


@booking_bp.put("/bookings/<int:booking_id>")
@jwt_required()
@role_required("admin")
def update_booking(booking_id):
    """Update a booking (Admin only)."""
    data = request.get_json(silent=True) or {}
    result = booking_service.update_booking(booking_id, data)
    return jsonify(result), result.get("status", 200)


@booking_bp.delete("/bookings/<int:booking_id>")
@jwt_required()
@role_required("admin")
def delete_booking(booking_id):
    """Delete a booking (Admin only)."""
    result = booking_service.delete_booking(booking_id)
    return jsonify(result), result.get("status", 200)
