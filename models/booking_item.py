from app import db
from models.base_model import BaseModel


class BookingItem(BaseModel):
    __tablename__ = "booking_items"

    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey("seats.id"), nullable=True)

    item_type = db.Column(db.String(30), nullable=False, default="ticket")
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    booking = db.relationship("Booking", back_populates="booking_items")
    seat = db.relationship("Seat", back_populates="booking_items")