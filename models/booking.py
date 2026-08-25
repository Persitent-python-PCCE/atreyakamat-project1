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
    idempotency_key = db.Column(db.String(128), nullable=True, unique=True, index=True)
    status = db.Column(db.String(20), nullable=False, default="pending")
    booked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="bookings")
    event = db.relationship("Event", back_populates="bookings")
    booking_items = db.relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")
    booking_addons = db.relationship("BookingAddon", back_populates="booking", cascade="all, delete-orphan")
    ticket = db.relationship("Ticket", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    promo_code_usage = db.relationship(
        "PromoCodeUsage", back_populates="booking", uselist=False, cascade="all, delete-orphan"
    )
    reward_transactions = db.relationship(
        "RewardTransaction", back_populates="booking", cascade="all, delete-orphan"
    )
    email_logs = db.relationship("EmailLog", back_populates="booking", cascade="all, delete-orphan")