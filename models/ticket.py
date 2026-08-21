from datetime import datetime

from app import db
from models.base_model import BaseModel


class Ticket(BaseModel):
    __tablename__ = "tickets"

    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False, unique=True)

    ticket_token = db.Column(db.String(150), nullable=False, unique=True)
    ticket_status = db.Column(db.String(20), nullable=False, default="valid")
    qr_data = db.Column(db.String(500), nullable=True)
    issued_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)
    expired_at = db.Column(db.DateTime, nullable=True)

    booking = db.relationship("Booking", back_populates="ticket")
    ticket_verifications = db.relationship(
        "TicketVerification", back_populates="ticket"
    )