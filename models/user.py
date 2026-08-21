from datetime import datetime

from app import db
from models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    phone = db.Column(db.String(30), nullable=True)
    id_document = db.Column(db.String(255), nullable=True)
    reward_balance = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    bookings = db.relationship("Booking", back_populates="user")
    seat_holds = db.relationship("SeatHold", back_populates="user")
    promo_code_usages = db.relationship("PromoCodeUsage", back_populates="user")
    reward_transactions = db.relationship("RewardTransaction", back_populates="user")
    notifications = db.relationship("Notification", back_populates="user")
    uploaded_files = db.relationship("UploadedFile", back_populates="user")
    email_logs = db.relationship("EmailLog", back_populates="user")
    created_events = db.relationship(
        "Event", back_populates="creator", foreign_keys="Event.created_by"
    )
    event_reschedules = db.relationship(
        "EventReschedule", back_populates="admin"
    )
