from datetime import datetime

from app import db
from models.base_model import BaseModel


class PromoCodeUsage(BaseModel):
    __tablename__ = "promo_code_usages"

    promo_code_id = db.Column(
        db.Integer, db.ForeignKey("promo_codes.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)

    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    used_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    promo_code = db.relationship("PromoCode", back_populates="promo_code_usages")
    user = db.relationship("User", back_populates="promo_code_usages")
    booking = db.relationship("Booking", back_populates="promo_code_usage")