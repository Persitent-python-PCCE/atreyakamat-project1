from datetime import datetime

from app import db
from models.base_model import BaseModel


class Seat(BaseModel):
    __tablename__ = "seats"

    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)

    seat_number = db.Column(db.String(50), nullable=False)
    section_name = db.Column(db.String(100), nullable=True)
    seat_type = db.Column(db.String(20), nullable=False, default="standard")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    venue = db.relationship("Venue", back_populates="seats")
    seat_holds = db.relationship("SeatHold", back_populates="seat")
    booking_items = db.relationship("BookingItem", back_populates="seat")