from datetime import datetime

from app import db
from models.base_model import BaseModel


class TicketVerification(BaseModel):
    __tablename__ = "ticket_verifications"

    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)

    verification_status = db.Column(db.String(20), nullable=False)
    verified_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    ticket = db.relationship("Ticket", back_populates="ticket_verifications")