from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    photo_type = Column(String(10), nullable=False)  # front, side, back
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    analysis_status = Column(String(20), default="pending")  # pending, processing, done, failed

    user = relationship("User", backref="photos")
