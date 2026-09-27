from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .base import Base


class SkinReaction(Base):
    """Logged skin reaction to an ingredient (F-1 / LC-2 adaptive skincare)."""

    __tablename__ = "skin_reactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, default=1)
    ingredient = Column(String, nullable=False, index=True)
    reaction = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # low / medium / high
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
