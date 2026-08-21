# Services/reward_service.py
#
# Business logic for reward transactions (the audit log of every change to
# a user's reward_balance).
#
# SCOPE for THIS phase:
#   - create a reward transaction row (the caller supplies all fields)
#   - read one / list by user / list by booking
#   - delete (rare)
#
# What this service does NOT do in this phase:
#   - compute 2% cashback on a booking and round it
#   - update the user's reward_balance atomically with the insert
#   - any validation that `transaction_type` is 'credit' or 'debit'
#
# Those live in the later booking-confirm workflow.

from DAO import RewardTransactionDAO
from models.reward_transaction import RewardTransaction
from api.serializers import _ser
from Services._result import ok, fail


def reward_to_dict(r):
    return {
        "id": r.id,
        "user_id": r.user_id,
        "booking_id": r.booking_id,
        "transaction_type": r.transaction_type,
        "amount": _ser(r.amount),
        "description": r.description,
        "created_at": _ser(r.created_at),
    }


class RewardService:
    def __init__(self):
        self.reward_dao = RewardTransactionDAO()

    def create_transaction(self, data: dict) -> dict:
        if data.get("user_id") is None:
            return fail("Missing required field: user_id", 400)
        if not data.get("transaction_type"):
            return fail("Missing required field: transaction_type", 400)
        if data.get("amount") is None:
            return fail("Missing required field: amount", 400)

        txn = RewardTransaction(
            user_id=data["user_id"],
            booking_id=data.get("booking_id"),
            transaction_type=data["transaction_type"],
            amount=data["amount"],
            description=data.get("description"),
        )
        try:
            saved = self.reward_dao.create_transaction(txn)
        except Exception:
            return fail("Could not create reward transaction", 500)
        return ok("Reward transaction created",
                  reward_to_dict(saved), status=201)

    def get_transaction_by_id(self, transaction_id: int) -> dict:
        r = self.reward_dao.get_transaction_by_id(transaction_id)
        if r is None:
            return fail("Reward transaction not found", 404)
        return ok("Reward transaction retrieved", reward_to_dict(r))

    def get_transactions_by_user(self, user_id: int) -> dict:
        rows = self.reward_dao.get_transactions_by_user(user_id)
        return ok("User reward history retrieved",
                  [reward_to_dict(r) for r in rows])

    def get_transactions_by_booking(self, booking_id: int) -> dict:
        rows = self.reward_dao.get_transactions_by_booking(booking_id)
        return ok("Booking reward transactions retrieved",
                  [reward_to_dict(r) for r in rows])

    def delete_transaction(self, transaction_id: int) -> dict:
        r = self.reward_dao.get_transaction_by_id(transaction_id)
        if r is None:
            return fail("Reward transaction not found", 404)
        try:
            self.reward_dao.delete_transaction(r)
        except Exception:
            return fail("Could not delete reward transaction", 500)
        return ok("Reward transaction deleted")
