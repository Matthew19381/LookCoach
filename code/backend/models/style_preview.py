from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class StylePreviewLog(Base):
    """One paid image-generation call (plan 4.13) - for the daily limit. The image itself is not stored."""

    __tablename__ = "style_preview_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=1)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # hair | beard
    option: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # ok | error
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
