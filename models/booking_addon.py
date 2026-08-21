from app import db
from models.base_model import BaseModel


class BookingAddon(BaseModel):
    __tablename__ = "booking_addons"

    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    addon_id = db.Column(db.Integer, db.ForeignKey("event_addons.id"), nullable=False)

    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    booking = db.relationship("Booking", back_populates="booking_addons")
    addon = db.relationship("EventAddon", back_populates="booking_addons")