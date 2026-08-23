# tests/unit/test_notification_service.py
#
# Pure unit tests for NotificationService with mocked NotificationDAO.
# WHY: In-app notifications alert buyers about bookings, cancellations, and schedule updates.

import pytest
from unittest.mock import MagicMock
from Services.notification_service import NotificationService
from models.notification import Notification


@pytest.mark.unit
class TestNotificationService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.notif_service = NotificationService()
        self.mock_dao = MagicMock()
        self.notif_service.notification_dao = self.mock_dao

    def test_create_notification(self):
        """WHY: Creating notification persists in-app notification row."""
        fake_n = Notification(id=1, user_id=5, title="Booking Confirmed", message="Enjoy!", notification_type="booking")
        self.mock_dao.create_notification.return_value = fake_n

        res = self.notif_service.create_notification({
            "user_id": 5, "title": "Booking Confirmed", "message": "Enjoy!", "notification_type": "booking"
        })
        assert res["success"] is True
        assert res["data"]["title"] == "Booking Confirmed"

    def test_get_user_notifications(self):
        """WHY: Users retrieve their in-app notifications."""
        self.mock_dao.get_user_notifications.return_value = [
            Notification(id=1, user_id=5, title="N1", is_read=False),
            Notification(id=2, user_id=5, title="N2", is_read=True),
        ]
        res = self.notif_service.get_user_notifications(5)
        assert res["success"] is True
        assert len(res["data"]) == 2

    def test_mark_as_read(self):
        """WHY: Marking notification sets is_read flag."""
        fake_n = Notification(id=3, user_id=10, is_read=False)
        self.mock_dao.get_notification_by_id.return_value = fake_n

        res = self.notif_service.mark_as_read(3)
        assert res["success"] is True
        self.mock_dao.mark_as_read.assert_called_once_with(fake_n)

    def test_mark_as_read_missing_returns_404(self):
        """WHY: Non-existent notification returns 404."""
        self.mock_dao.get_notification_by_id.return_value = None
        res = self.notif_service.mark_as_read(999)
        assert res["success"] is False
        assert res["status"] == 404
