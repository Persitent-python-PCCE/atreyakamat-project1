# Controller/notification_controller.py
#
# NotificationController — handles HTTP requests for user notifications.
#
# Flow:
#     HTTP Request -> NotificationController -> NotificationService -> NotificationDAO -> MySQL

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Services.notification_service import NotificationService
from Controller.auth_guards import role_required

notification_bp = Blueprint("notification_bp", __name__)
notification_service = NotificationService()


@notification_bp.get("/notifications/my")
@jwt_required()
def get_my_notifications():
    """List all notifications for the authenticated user."""
    current_user_id = int(get_jwt_identity())
    result = notification_service.get_user_notifications(current_user_id)
    return jsonify(result), result.get("status", 200)


@notification_bp.get("/users/<int:user_id>/notifications")
@jwt_required()
def list_user_notifications(user_id):
    """List all notifications for a specific user (Owner or Admin)."""
    current_user_id = int(get_jwt_identity())
    current_role = get_jwt().get("role")

    if current_role != "admin" and current_user_id != user_id:
        return jsonify({
            "success": False,
            "message": "You do not have permission to access this resource"
        }), 403

    result = notification_service.get_user_notifications(user_id)
    return jsonify(result), result.get("status", 200)


@notification_bp.post("/notifications")
@jwt_required()
@role_required("admin")
def create_notification():
    """Create a new notification (Admin only)."""
    data = request.get_json(silent=True) or {}
    result = notification_service.create_notification(data)
    return jsonify(result), result.get("status", 200)


@notification_bp.put("/notifications/<int:notification_id>/read")
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    result = notification_service.mark_as_read(notification_id)
    return jsonify(result), result.get("status", 200)
