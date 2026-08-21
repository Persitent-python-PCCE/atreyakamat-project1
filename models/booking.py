from datetime import datetime

from app import db
from models.base_model import BaseModel


class Booking(BaseModel):
    __tablename__ = "bookings"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    booking_reference = db.Column(db.String(100), nullable=False, unique=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    cashback_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    status = db.Column(db.String(20), nullable=False, default="pending")
    booked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="bookings")
    event = db.relationship("Event", back_populates="bookings")
    booking_items = db.relationship("BookingItem", back_populates="booking")
    booking_addons = db.relationship("BookingAddon", back_populates="booking")
    ticket = db.relationship("Ticket", back_populates="booking", uselist=False)
    promo_code_usage = db.relationship(
        "PromoCodeUsage", back_populates="booking", uselist=False
    )
    reward_transactions = db.relationship(
        "RewardTransaction", back_populates="booking"
    )
    email_logs = db.relationship("EmailLog", back_populates="booking")