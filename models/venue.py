from datetime import datetime

from app import db
from models.base_model import BaseModel


class Venue(BaseModel):
    __tablename__ = "venues"

    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    venue_type = db.Column(db.String(50), nullable=False, default="seated")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    events = db.relationship("Event", back_populates="venue")
    seats = db.relationship("Seat", back_populates="venue", cascade="all, delete-orphan")