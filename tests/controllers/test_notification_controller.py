# tests/controllers/test_notification_controller.py
#
# Controller tests for Notification API endpoints (/api/notifications/*).
# WHY: Verifies user retrieval of their in-app alerts and marking notifications as read.

import pytest
from models.notification import Notification


@pytest.mark.controller
class TestNotificationController:
    def test_get_and_read_notifications_api(self, client, db_session, customer_user, auth_headers_customer):
        """WHY: Customer can query their notifications and update read status."""
        notif = Notification(
            user_id=customer_user.id,
            title="Ticket Confirmed",
            message="You are ready!",
            notification_type="ticket",
            is_read=False,
        )
        db_session.add(notif)
        db_session.commit()

        # 1. Get my notifications
        res_list = client.get("/api/notifications/my", headers=auth_headers_customer)
        assert res_list.status_code == 200
        assert len(res_list.get_json()["data"]) == 1

        # 2. Mark as read
        res_read = client.put(f"/api/notifications/{notif.id}/read", headers=auth_headers_customer)
        assert res_read.status_code == 200
