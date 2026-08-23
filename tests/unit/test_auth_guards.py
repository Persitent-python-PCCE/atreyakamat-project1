# tests/unit/test_auth_guards.py
#
# Pure unit tests for Controller auth guards (role_required and get_current_user_info).
# WHY: Verifies Role-Based Access Control (RBAC):
#   1. Admin-only endpoints return 200 for admins and 403 Forbidden for customers.
#   2. Identity helper extracts claims accurately from active JWT.

import pytest
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from Controller.auth_guards import role_required, get_current_user_info


@pytest.mark.unit
class TestAuthGuards:
    @pytest.fixture(autouse=True)
    def setup_guard_app(self):
        self.app = Flask(__name__)
        self.app.config["JWT_SECRET_KEY"] = "test-secret"
        self.jwt = JWTManager(self.app)

        @self.app.route("/admin-only")
        @role_required("admin")
        def admin_route():
            return jsonify({"status": "admin_granted"})

        @self.app.route("/multi-role")
        @role_required("admin", "manager")
        def multi_route():
            return jsonify({"status": "multi_granted"})

        @self.app.route("/whoami")
        def whoami_route():
            info = get_current_user_info()
            return jsonify(info or {})

        self.client = self.app.test_client()

    def test_admin_access_allowed(self):
        """WHY: role_required('admin') permits admin token access."""
        with self.app.app_context():
            token = create_access_token(identity="1", additional_claims={"role": "admin", "name": "A", "email": "a@t.com"})

        res = self.client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.get_json()["status"] == "admin_granted"

    def test_customer_access_blocked_403(self):
        """WHY: role_required('admin') blocks customer token with 403 Forbidden."""
        with self.app.app_context():
            token = create_access_token(identity="2", additional_claims={"role": "customer", "name": "C", "email": "c@t.com"})

        res = self.client.get("/admin-only", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403
        assert res.get_json()["success"] is False

    def test_get_current_user_info_helper(self):
        """WHY: get_current_user_info extracts user identity and claims from JWT."""
        with self.app.app_context():
            token = create_access_token(identity="5", additional_claims={"role": "customer", "name": "Bob", "email": "bob@test.com"})

        res = self.client.get("/whoami", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["id"] == 5
        assert data["role"] == "customer"
        assert data["name"] == "Bob"
