from datetime import datetime

from app import db
from models.base_model import BaseModel


class EventReschedule(BaseModel):
    __tablename__ = "event_reschedules"

    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    old_event_date = db.Column(db.Date, nullable=False)
    old_start_time = db.Column(db.Time, nullable=False)
    new_event_date = db.Column(db.Date, nullable=False)
    new_start_time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    rescheduled_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    event = db.relationship("Event", back_populates="event_reschedules")
    admin = db.relationship("User", back_populates="event_reschedules")