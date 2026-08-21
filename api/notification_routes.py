# api/notification_routes.py
#
# CONTROLLER for in-app notifications.
#
# URL prefix for this blueprint is `/api`, so the full paths are:
#
#   GET  /api/users/<user_id>/notifications   list a user's notifications
#   POST /api/notifications                  create a notification
#   PUT  /api/notifications/<id>/read         mark a notification as read

from flask import Blueprint, request, jsonify

from Services import NotificationService

notification_bp = Blueprint("notification_bp", __name__)
notification_service = NotificationService()


@notification_bp.get("/users/<int:user_id>/notifications")
def list_user_notifications(user_id):
    result = notification_service.get_user_notifications(user_id)
    return jsonify(result), result.get("status", 200)


@notification_bp.post("/notifications")
def create_notification():
    data = request.get_json(silent=True) or {}
    result = notification_service.create_notification(data)
    return jsonify(result), result.get("status", 200)


@notification_bp.put("/notifications/<int:notification_id>/read")
def mark_notification_read(notification_id):
    result = notification_service.mark_as_read(notification_id)
    return jsonify(result), result.get("status", 200)
