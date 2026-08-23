# tests/unit/test_user_service.py
#
# Pure unit tests for UserService with mocked UserDAO.
# WHY: Verifies CRUD business operations and ensures duplicate email collisions are caught.

import pytest
from unittest.mock import MagicMock
from Services.user_service import UserService
from models.user import User


@pytest.mark.unit
class TestUserService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.user_service = UserService()
        self.mock_dao = MagicMock()
        self.user_service.user_dao = self.mock_dao

    def test_get_user_by_id_found(self):
        """WHY: Valid user ID lookup returns serialized dictionary."""
        fake_user = User(id=1, name="John", email="john@test.com", role="customer", is_active=True)
        self.mock_dao.get_user_by_id.return_value = fake_user

        res = self.user_service.get_user_by_id(1)
        assert res["success"] is True
        assert res["data"]["name"] == "John"

    def test_get_user_by_id_not_found(self):
        """WHY: Missing user lookup returns 404."""
        self.mock_dao.get_user_by_id.return_value = None
        res = self.user_service.get_user_by_id(999)
        assert res["success"] is False
        assert res["status"] == 404

    def test_create_user_success(self):
        """WHY: User creation with valid fields hashes password and returns 201."""
        self.mock_dao.get_user_by_email.return_value = None
        fake_saved = User(id=5, name="Newbie", email="newbie@test.com", password_hash="hashed_pw", role="customer", is_active=True)
        self.mock_dao.create_user.return_value = fake_saved

        res = self.user_service.create_user({
            "name": "Newbie",
            "email": "newbie@test.com",
            "password_hash": "hashed_pw",
        })
        assert res["success"] is True
        assert res["status"] == 201
        assert res["data"]["id"] == 5

    def test_create_user_duplicate_email(self):
        """WHY: Re-registering an existing email must fail with 409 Conflict."""
        self.mock_dao.get_user_by_email.return_value = User(id=2, email="exists@test.com")
        res = self.user_service.create_user({
            "name": "Test",
            "email": "exists@test.com",
            "password_hash": "hashed_pw",
        })
        assert res["success"] is False
        assert res["status"] == 409

    def test_update_user_fields(self):
        """WHY: Partial profile updates modify allowed fields while preserving unedited attributes."""
        fake_user = User(id=1, name="Old Name", phone="111-2222")
        self.mock_dao.get_user_by_id.return_value = fake_user

        res = self.user_service.update_user(1, {"name": "New Name", "phone": "333-4444"})
        assert res["success"] is True
        assert fake_user.name == "New Name"
        assert fake_user.phone == "333-4444"
        self.mock_dao.update_user.assert_called_once_with(fake_user)

    def test_delete_user_success(self):
        """WHY: Deleting user delegates to DAO correctly."""
        fake_user = User(id=1)
        self.mock_dao.get_user_by_id.return_value = fake_user

        res = self.user_service.delete_user(1)
        assert res["success"] is True
        self.mock_dao.delete_user.assert_called_once_with(fake_user)
