from datetime import datetime

from app import db
from models.base_model import BaseModel


class SeatHold(BaseModel):
    __tablename__ = "seat_holds"

    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey("seats.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    hold_token = db.Column(db.String(100), nullable=False, unique=True)
    held_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")

    event = db.relationship("Event", back_populates="seat_holds")
    seat = db.relationship("Seat", back_populates="seat_holds")
    user = db.relationship("User", back_populates="seat_holds")