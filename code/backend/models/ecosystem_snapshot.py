from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.sql import func

from .base import Base


class EcosystemSnapshot(Base):
    """Last data read from other modules via the hub (plan 3.8) - fallback when the hub is down."""

    __tablename__ = "ecosystem_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    data = Column(Text, nullable=False, default="{}")  # JSON overview
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
