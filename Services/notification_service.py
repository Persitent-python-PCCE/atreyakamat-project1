# Services/notification_service.py
#
# Business logic for in-app notifications.
#
# SCOPE for THIS phase: basic CRUD + mark-as-read.
# No automatic notification system yet — notifications are created on
# demand by a route, and will later be created by Service flows
# (booking confirm, reschedule, etc.) when those flows are added.

from DAO import NotificationDAO
from models.notification import Notification
from api.serializers import notification_to_dict
from Services._result import ok, fail


class NotificationService:
    def __init__(self):
        self.notification_dao = NotificationDAO()

    def create_notification(self, data: dict) -> dict:
        required = ("user_id", "title", "message", "notification_type")
        for f in required:
            v = data.get(f)
            if v is None or (isinstance(v, str) and not v.strip()):
                return fail(f"Missing required field: {f}", 400)

        n = Notification(
            user_id=data["user_id"],
            title=data["title"],
            message=data["message"],
            notification_type=data["notification_type"],
            is_read=bool(data.get("is_read", False)),
        )
        try:
            saved = self.notification_dao.create_notification(n)
        except Exception:
            return fail("Could not create notification", 500)
        return ok("Notification created",
                  notification_to_dict(saved), status=201)

    def get_user_notifications(self, user_id: int) -> dict:
        rows = self.notification_dao.get_user_notifications(user_id)
        return ok("Notifications retrieved",
                  [notification_to_dict(n) for n in rows])

    def get_unread_notifications(self, user_id: int) -> dict:
        rows = self.notification_dao.get_unread_notifications(user_id)
        return ok("Unread notifications retrieved",
                  [notification_to_dict(n) for n in rows])

    def get_notification_by_id(self, notification_id: int) -> dict:
        n = self.notification_dao.get_notification_by_id(notification_id)
        if n is None:
            return fail("Notification not found", 404)
        return ok("Notification retrieved", notification_to_dict(n))

    def mark_as_read(self, notification_id: int) -> dict:
        n = self.notification_dao.get_notification_by_id(notification_id)
        if n is None:
            return fail("Notification not found", 404)
        try:
            self.notification_dao.mark_as_read(n)
        except Exception:
            return fail("Could not mark notification as read", 500)
        return ok("Notification marked as read", notification_to_dict(n))

    def delete_notification(self, notification_id: int) -> dict:
        n = self.notification_dao.get_notification_by_id(notification_id)
        if n is None:
            return fail("Notification not found", 404)
        try:
            self.notification_dao.delete_notification(n)
        except Exception:
            return fail("Could not delete notification", 500)
        return ok("Notification deleted")
