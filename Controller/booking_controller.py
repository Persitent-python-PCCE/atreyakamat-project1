# Controller/booking_controller.py
#
# BookingController — handles HTTP requests for booking, checkout, and cancellation operations.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Services.booking_service import BookingService
from Controller.auth_guards import role_required

booking_bp = Blueprint("booking_bp", __name__)
booking_service = BookingService()


@booking_bp.post("/checkout/preview")
@jwt_required()
def preview_checkout():
    """Calculate and preview checkout amounts for active seat holds or general admission, addons, and promo."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    promo_code = data.get("promo_code")
    selected_addons = data.get("selected_addons", {})
    quantity = data.get("quantity")

    if not event_id:
        return jsonify({"success": False, "message": "event_id is required"}), 400

    result = booking_service.get_checkout_preview(
        user_id=user_id,
        event_id=int(event_id),
        promo_code=promo_code,
        selected_addons=selected_addons,
        quantity=quantity,
    )
    return jsonify(result), result.get("status", 200)


@booking_bp.post("/checkout/confirm")
@booking_bp.post("/bookings")
@jwt_required()
def confirm_booking():
    """Confirm booking in one atomic database transaction with hold consumption / GA tickets, promo, 2% reward, and ticket generation."""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    promo_code = data.get("promo_code")
    selected_addons = data.get("selected_addons", {})
    quantity = data.get("quantity")

    if not event_id:
        return jsonify({"success": False, "message": "event_id is required"}), 400

    result = booking_service.confirm_booking(
        user_id=user_id,
        event_id=int(event_id),
        selected_addons=selected_addons,
        promo_code=promo_code,
        quantity=quantity,
    )
    return jsonify(result), result.get("status", 200)


@booking_bp.post("/bookings/<int:booking_id>/cancel")
@jwt_required()
def cancel_booking(booking_id):
    """Customer or Admin cancellation of an eligible booking."""
    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role", "customer")
    is_admin = (current_role == "admin")

    result = booking_service.cancel_booking(
        booking_id=booking_id,
        user_id=current_user_id,
        is_admin=is_admin,
    )
    return jsonify(result), result.get("status", 200)


@booking_bp.post("/bookings/<int:booking_id>/send-confirmation")
@jwt_required()
def send_booking_email(booking_id):
    """Trigger sending or resending booking confirmation email (Owner or Admin only)."""
    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role", "customer")
    is_admin = (current_role == "admin")

    from Services.email_service import EmailService
    email_svc = EmailService()
    result = email_svc.resend_booking_confirmation(
        booking_id=booking_id,
        user_id=current_user_id,
        is_admin=is_admin,
    )
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
