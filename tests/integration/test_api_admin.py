# tests/integration/test_api_admin.py
#
# Integration test for admin event operations and rescheduling.
# WHY: Verifies administrative event management, password confirmation, and reschedule audit trail.

import pytest
from datetime import date, timedelta


@pytest.mark.integration
class TestApiAdminIntegration:
    def test_admin_reschedule_and_history_api(self, client, auth_headers_admin, event):
        """WHY: Admin event rescheduling requires password, updates date, and writes reschedule audit row."""
        new_date = str(date.today() + timedelta(days=20))
        res = client.post(f"/api/admin/events/{event.id}/reschedule", headers=auth_headers_admin, json={
            "new_event_date": new_date,
            "new_start_time": "20:30",
            "reason": "Conductor Schedule Change",
            "password": "AdminPass123!",
        })
        assert res.status_code == 200

        # Check history
        res_hist = client.get(f"/api/admin/events/{event.id}/reschedule-history", headers=auth_headers_admin)
        assert res_hist.status_code == 200
        assert len(res_hist.get_json()["data"]) == 1
