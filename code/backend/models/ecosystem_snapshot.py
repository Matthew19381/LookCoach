from datetime import datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class EcosystemSnapshot(Base):
    """Last data read from other modules via the hub (plan 3.8) - fallback when the hub is down."""

    __tablename__ = "ecosystem_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    data: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON overview
    fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
