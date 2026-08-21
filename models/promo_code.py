from datetime import datetime

from app import db
from models.base_model import BaseModel


class PromoCode(BaseModel):
    __tablename__ = "promo_codes"

    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    discount_type = db.Column(db.String(20), nullable=False)
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    minimum_booking_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    max_uses = db.Column(db.Integer, nullable=True)
    used_count = db.Column(db.Integer, nullable=False, default=0)
    valid_from = db.Column(db.DateTime, nullable=True)
    valid_until = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    promo_code_usages = db.relationship("PromoCodeUsage", back_populates="promo_code")