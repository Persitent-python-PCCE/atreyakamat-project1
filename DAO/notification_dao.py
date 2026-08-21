# DAO/notification_dao.py
#
# NotificationDAO — Data Access Object for the `notifications` table.
# A Notification is an in-app message for a user (booking confirmed,
# ticket ready, event rescheduled, etc.).

from app import db
from models.notification import Notification


class NotificationDAO:
    """Database operations for the Notification model."""

    def create_notification(
        self, notification: Notification
    ) -> Notification:
        """Insert a new notification row.

        The Service sets user_id, title, message, notification_type, is_read.
        """
        try:
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception:
            db.session.rollback()
            raise

    def get_notification_by_id(self, notification_id: int) -> Notification | None:
        """Load one notification by its primary key."""
        return db.session.get(Notification, notification_id)

    def get_user_notifications(self, user_id: int) -> list[Notification]:
        """Return all notifications for a user, newest first."""
        return (
            Notification.query
            .filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    def get_unread_notifications(self, user_id: int) -> list[Notification]:
        """Return only unread notifications for a user (newest first)."""
        return (
            Notification.query
            .filter_by(user_id=user_id, is_read=False)
            .order_by(Notification.created_at.desc())
            .all()
        )

    def mark_as_read(self, notification: Notification) -> Notification:
        """Mark a single notification as read and persist.

        The Service can also just set notification.is_read = True and call
        update_notification; this is a convenience wrapper.
        """
        notification.is_read = True
        try:
            db.session.commit()
            return notification
        except Exception:
            db.session.rollback()
            raise

    def update_notification(self, notification: Notification) -> Notification:
        """Commit changes the Service already applied to `notification`."""
        try:
            db.session.commit()
            return notification
        except Exception:
            db.session.rollback()
            raise

    def delete_notification(self, notification: Notification) -> bool:
        """Delete the given notification row. Returns True on success."""
        try:
            db.session.delete(notification)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
