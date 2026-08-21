# Controller/notification_controller.py
#
# NotificationController — handles HTTP requests for user notifications.
#
# Flow:
#     HTTP Request -> NotificationController -> NotificationService -> NotificationDAO -> MySQL

from flask import Blueprint, request, jsonify
from Services.notification_service import NotificationService

notification_bp = Blueprint("notification_bp", __name__)
notification_service = NotificationService()


@notification_bp.get("/users/<int:user_id>/notifications")
def list_user_notifications(user_id):
    """List all notifications for a specific user."""
    result = notification_service.get_user_notifications(user_id)
    return jsonify(result), result.get("status", 200)


@notification_bp.post("/notifications")
def create_notification():
    """Create a new notification."""
    data = request.get_json(silent=True) or {}
    result = notification_service.create_notification(data)
    return jsonify(result), result.get("status", 200)


@notification_bp.put("/notifications/<int:notification_id>/read")
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    result = notification_service.mark_as_read(notification_id)
    return jsonify(result), result.get("status", 200)
