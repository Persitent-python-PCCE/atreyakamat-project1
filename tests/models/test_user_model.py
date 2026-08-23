# tests/models/test_user_model.py
#
# SQLAlchemy Model test for User model.
# WHY: Verifies default column values, nullable constraints, and role enum consistency.

import pytest
from models.user import User


@pytest.mark.model
class TestUserModel:
    def test_user_model_fields_and_defaults(self, db_session):
        """WHY: User model defaults role to 'customer', is_active to True, and reward_balance to 0.00."""
        user = User(
            name="Alice Model",
            email="alice_model@example.com",
            password_hash="pbkdf2:sha256:fakehash",
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.role == "customer"
        assert user.is_active is True
        assert float(user.reward_balance) == 0.00
        assert user.created_at is not None
        assert user.updated_at is not None
