# tests/integration/test_api_auth.py
#
# Integration test for complete user authentication, role enforcement, and token workflow.
# WHY: Verifies registration, login, token extraction, and access verification in a unified multi-step flow.

import pytest


@pytest.mark.integration
class TestApiAuthIntegration:
    def test_complete_auth_lifecycle(self, client):
        """WHY: End-to-end verification of registration, login, and authorization validation."""
        # 1. Register
        res1 = client.post("/api/auth/register", json={
            "name": "E2E User",
            "email": "e2e@seatmeup.com",
            "password": "Password123!",
        })
        assert res1.status_code == 201

        # 2. Login
        res2 = client.post("/api/auth/login", json={
            "email": "e2e@seatmeup.com",
            "password": "Password123!",
        })
        assert res2.status_code == 200
        token = res2.get_json()["data"]["token"]

        # 3. Access Protected Endpoint
        res3 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res3.status_code == 200
        assert res3.get_json()["data"]["email"] == "e2e@seatmeup.com"

        # 4. Access Admin Endpoint as Customer -> 403 Forbidden
        res4 = client.get("/api/admin/analytics", headers={"Authorization": f"Bearer {token}"})
        assert res4.status_code == 403
