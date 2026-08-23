# tests/controllers/test_auth_controller.py
#
# Controller tests for Authentication API endpoints (/api/auth/*).
# WHY: Verifies registration, login, and current-user (/api/auth/me) endpoint behaviors.

import pytest


@pytest.mark.controller
class TestAuthController:
    def test_register_and_login_api_flow(self, client):
        """WHY: Complete registration and login cycle issues JWT token to newly created account."""
        # 1. Register
        res_reg = client.post("/api/auth/register", json={
            "name": "Integration User",
            "email": "int_user@test.com",
            "password": "Password123!",
        })
        assert res_reg.status_code == 201
        assert res_reg.get_json()["success"] is True

        # 2. Login
        res_login = client.post("/api/auth/login", json={
            "email": "int_user@test.com",
            "password": "Password123!",
        })
        assert res_login.status_code == 200
        token = res_login.get_json()["data"]["token"]
        assert token is not None

        # 3. Access Protected /me Endpoint
        res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 200
        assert res_me.get_json()["data"]["email"] == "int_user@test.com"

    def test_login_invalid_credentials_returns_401(self, client):
        """WHY: Invalid password returns 401 Unauthorized via API response."""
        res = client.post("/api/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "wrongpassword",
        })
        assert res.status_code == 401
        assert res.get_json()["success"] is False
