# tests/unit/test_auth_service.py
#
# Pure unit tests for AuthService.
# WHY: Authentication and JWT generation are foundational security layers.
# We must ensure passwords are hashed, deactivated accounts are blocked,
# and invalid credentials return 401.

import pytest
from unittest.mock import MagicMock
from werkzeug.security import generate_password_hash

from Services.auth_service import AuthService
from models.user import User


@pytest.mark.unit
class TestAuthService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.auth_service = AuthService()
        self.mock_user_dao = MagicMock()
        self.auth_service.user_dao = self.mock_user_dao

    def test_register_success(self):
        """WHY: Valid registration must hash passwords and persist default customer role."""
        self.mock_user_dao.get_user_by_email.return_value = None
        fake_user = User(id=1, name="Alice", email="alice@test.com", password_hash="hashed_pw", role="customer")
        self.mock_user_dao.create_user.return_value = fake_user

        data = {"name": "Alice", "email": "alice@test.com", "password": "securepassword123"}
        res = self.auth_service.register(data)

        assert res["success"] is True
        assert res["status"] == 201
        assert res["data"]["email"] == "alice@test.com"
        assert "password_hash" not in res["data"]
        self.mock_user_dao.create_user.assert_called_once()

    @pytest.mark.parametrize("missing_field, payload", [
        ("name", {"email": "b@test.com", "password": "pw"}),
        ("email", {"name": "Bob", "password": "pw"}),
        ("password", {"name": "Bob", "email": "b@test.com"}),
    ])
    def test_register_missing_required_fields_fails(self, missing_field, payload):
        """WHY: Parameterized validation ensures missing credentials fail with 400 before DB access."""
        res = self.auth_service.register(payload)
        assert res["success"] is False
        assert res["status"] == 400
        assert missing_field in res["message"]

    def test_register_duplicate_email_fails(self):
        """WHY: Duplicate email must be rejected with 409 Conflict to protect account uniqueness."""
        self.mock_user_dao.get_user_by_email.return_value = User(id=2, email="taken@test.com")

        res = self.auth_service.register({"name": "Bob", "email": "taken@test.com", "password": "pw"})
        assert res["success"] is False
        assert res["status"] == 409
        assert "already registered" in res["message"]

    def test_login_success(self, app):
        """WHY: Legitimate credentials must return a valid JWT token and user profile."""
        fake_user = User(
            id=1,
            email="charlie@test.com",
            password_hash=generate_password_hash("mypassword"),
            role="customer",
            is_active=True,
        )
        self.mock_user_dao.get_user_by_email.return_value = fake_user

        with app.test_request_context():
            res = self.auth_service.login("charlie@test.com", "mypassword")
            assert res["success"] is True
            assert res["status"] == 200
            assert "token" in res["data"]
            assert res["data"]["user"]["email"] == "charlie@test.com"

    def test_login_wrong_password(self, app):
        """WHY: Incorrect password must fail with 401 Unauthorized without leaking password details."""
        fake_user = User(
            id=1,
            email="charlie@test.com",
            password_hash=generate_password_hash("correct_password"),
            role="customer",
            is_active=True,
        )
        self.mock_user_dao.get_user_by_email.return_value = fake_user

        with app.test_request_context():
            res = self.auth_service.login("charlie@test.com", "wrong_pw")
            assert res["success"] is False
            assert res["status"] == 401
            assert "Invalid email or password" in res["message"]

    def test_login_unknown_email(self, app):
        """WHY: Non-existent email must return 401 with generic error to prevent user enumeration."""
        self.mock_user_dao.get_user_by_email.return_value = None

        with app.test_request_context():
            res = self.auth_service.login("ghost@test.com", "pw")
            assert res["success"] is False
            assert res["status"] == 401

    def test_login_inactive_user(self, app):
        """WHY: Inactive/banned users must be blocked with 403 Forbidden even with correct password."""
        fake_user = User(
            id=2,
            email="disabled@test.com",
            password_hash=generate_password_hash("pw"),
            role="customer",
            is_active=False,
        )
        self.mock_user_dao.get_user_by_email.return_value = fake_user

        with app.test_request_context():
            res = self.auth_service.login("disabled@test.com", "pw")
            assert res["success"] is False
            assert res["status"] == 403
            assert "inactive" in res["message"].lower()

    def test_get_me_success(self):
        """WHY: Authenticated profile lookup must return serialized user dict."""
        fake_user = User(id=7, name="David", email="david@test.com", role="customer", is_active=True)
        self.mock_user_dao.get_user_by_id.return_value = fake_user

        res = self.auth_service.get_me(7)
        assert res["success"] is True
        assert res["data"]["email"] == "david@test.com"

    def test_get_me_missing_user(self):
        """WHY: Non-existent user lookup returns 404."""
        self.mock_user_dao.get_user_by_id.return_value = None

        res = self.auth_service.get_me(999)
        assert res["success"] is False
        assert res["status"] == 404
