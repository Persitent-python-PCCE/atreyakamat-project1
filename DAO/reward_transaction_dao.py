# DAO/reward_transaction_dao.py
#
# RewardTransactionDAO — Data Access Object for the `reward_transactions`
# table. A RewardTransaction is every change to a user's reward balance.

from app import db
from models.reward_transaction import RewardTransaction


class RewardTransactionDAO:
    """Database operations for the RewardTransaction model."""

    def create_transaction(self, transaction: RewardTransaction) -> RewardTransaction:
        """Insert a new reward transaction row."""
        try:
            db.session.add(transaction)
            db.session.commit()
            return transaction
        except Exception:
            db.session.rollback()
            raise

    def get_transaction_by_id(self, transaction_id: int) -> RewardTransaction | None:
        """Load one reward transaction by its primary key."""
        return db.session.get(RewardTransaction, transaction_id)

    def get_transactions_by_user(self, user_id: int) -> list[RewardTransaction]:
        """Return the full reward history of a user."""
        return RewardTransaction.query.filter_by(user_id=user_id).all()

    def get_transactions_by_booking(self, booking_id: int) -> list[RewardTransaction]:
        """Return any reward transactions linked to a given booking
        (e.g. the 2% cashback entry)."""
        return RewardTransaction.query.filter_by(booking_id=booking_id).all()

    def update_transaction(self, transaction: RewardTransaction) -> RewardTransaction:
        """Commit changes the Service already applied to `transaction`."""
        try:
            db.session.commit()
            return transaction
        except Exception:
            db.session.rollback()
            raise

    def delete_transaction(self, transaction: RewardTransaction) -> bool:
        """Delete the given reward transaction row. Returns True on success."""
        try:
            db.session.delete(transaction)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
