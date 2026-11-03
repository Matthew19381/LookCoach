from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    photo_type: Mapped[str] = mapped_column(String(10), nullable=False)  # front, side, back
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
    analysis_status: Mapped[str | None] = mapped_column(String(20), default="pending")  # pending, processing, done, failed

    user = relationship("User", backref="photos")
