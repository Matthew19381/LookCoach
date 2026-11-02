from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .base import Base


class StylePreviewLog(Base):
    """One paid image-generation call (plan 4.13) - for the daily limit. The image itself is not stored."""

    __tablename__ = "style_preview_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, default=1)
    kind = Column(String(20), nullable=False)  # hair | beard
    option = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False)  # ok | error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
