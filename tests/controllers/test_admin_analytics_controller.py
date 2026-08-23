# tests/controllers/test_admin_analytics_controller.py
#
# Controller tests for Admin Analytics API endpoints (/api/admin/analytics).
# WHY: Analytics contain business-sensitive revenue and user data.
# Must enforce admin authorization (200) and block customers with 403 Forbidden.

import pytest


@pytest.mark.controller
class TestAdminAnalyticsController:
    def test_analytics_dashboard_admin_access(self, client, auth_headers_admin):
        """WHY: Authenticated admin can access GET /api/admin/analytics."""
        res = client.get("/api/admin/analytics", headers=auth_headers_admin)
        assert res.status_code == 200
        assert "summary" in res.get_json()["data"]
        assert "total_events" in res.get_json()["data"]["summary"]

    def test_analytics_dashboard_customer_blocked_403(self, client, auth_headers_customer):
        """WHY: Customer role is blocked with 403 Forbidden from accessing admin analytics."""
        res = client.get("/api/admin/analytics", headers=auth_headers_customer)
        assert res.status_code == 403
