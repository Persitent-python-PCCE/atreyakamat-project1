from datetime import datetime

from app import db
from models.base_model import BaseModel


class UploadedFile(BaseModel):
    __tablename__ = "uploaded_files"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="uploaded_files")
    event = db.relationship("Event", back_populates="uploaded_files")