from datetime import datetime

from app import db
from models.base_model import BaseModel


class RewardTransaction(BaseModel):
    __tablename__ = "reward_transactions"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=True)

    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reward_transactions")
    booking = db.relationship("Booking", back_populates="reward_transactions")