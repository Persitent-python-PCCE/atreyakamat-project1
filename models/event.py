from datetime import datetime

from app import db
from models.base_model import BaseModel


class Event(BaseModel):
    __tablename__ = "events"

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=True)
    poster = db.Column(db.String(255), nullable=True)
    booking_open = db.Column(db.Boolean, nullable=False, default=True)
    status = db.Column(db.String(20), nullable=False, default="draft")
    requires_seats = db.Column(db.Boolean, nullable=False, default=True)
    base_price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    category = db.relationship("Category", back_populates="events")
    venue = db.relationship("Venue", back_populates="events")
    creator = db.relationship("User", back_populates="created_events")

    event_addons = db.relationship("EventAddon", back_populates="event", cascade="all, delete-orphan")
    seat_holds = db.relationship("SeatHold", back_populates="event", cascade="all, delete-orphan")
    bookings = db.relationship("Booking", back_populates="event", cascade="all, delete-orphan")
    event_reschedules = db.relationship("EventReschedule", back_populates="event", cascade="all, delete-orphan")
    uploaded_files = db.relationship("UploadedFile", back_populates="event", cascade="all, delete-orphan")