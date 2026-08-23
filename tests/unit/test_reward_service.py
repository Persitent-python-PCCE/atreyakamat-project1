# tests/unit/test_reward_service.py
#
# Pure unit tests for RewardService with mocked RewardTransactionDAO and UserDAO.
# WHY: RewardService manages customer cashback credits and ledger history.

import pytest
from unittest.mock import MagicMock
from Services.reward_service import RewardService
from models.reward_transaction import RewardTransaction
from models.user import User


@pytest.mark.unit
class TestRewardService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.reward_service = RewardService()
        self.mock_reward_dao = MagicMock()
        self.reward_service.reward_dao = self.mock_reward_dao

    def test_create_transaction_success(self):
        """WHY: Adding reward transaction increases user reward balance in ledger."""
        fake_tx = RewardTransaction(id=1, user_id=1, booking_id=5, transaction_type="cashback_credit", amount=2.00)
        self.mock_reward_dao.create_transaction.return_value = fake_tx

        res = self.reward_service.create_transaction({
            "user_id": 1, "booking_id": 5, "transaction_type": "cashback_credit", "amount": 2.00
        })
        assert res["success"] is True
        assert res["data"]["amount"] == 2.00

    def test_get_transactions_by_user(self):
        """WHY: User can view complete reward transaction history."""
        self.mock_reward_dao.get_transactions_by_user.return_value = [
            RewardTransaction(id=1, user_id=1, transaction_type="cashback_credit", amount=5.00),
            RewardTransaction(id=2, user_id=1, transaction_type="reversal", amount=-2.00),
        ]
        res = self.reward_service.get_transactions_by_user(1)
        assert res["success"] is True
        assert len(res["data"]) == 2
