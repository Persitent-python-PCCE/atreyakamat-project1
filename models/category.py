from datetime import datetime

from app import db
from models.base_model import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    events = db.relationship("Event", back_populates="category")