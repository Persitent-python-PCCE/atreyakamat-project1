from datetime import datetime

from app import db
from models.base_model import BaseModel


class EventAddon(BaseModel):
    __tablename__ = "event_addons"

    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    available_quantity = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    event = db.relationship("Event", back_populates="event_addons")
    booking_addons = db.relationship("BookingAddon", back_populates="addon")