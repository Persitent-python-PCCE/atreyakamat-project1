from datetime import datetime

from app import db
from models.base_model import BaseModel


class EmailLog(BaseModel):
    __tablename__ = "email_logs"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=True)

    recipient_email = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    email_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="email_logs")
    booking = db.relationship("Booking", back_populates="email_logs")