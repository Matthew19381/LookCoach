from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class AssistantMessage(Base):
    """One turn of the LookCoach assistant conversation (plan 8.2)."""

    __tablename__ = "assistant_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=1)
    role: Mapped[str] = mapped_column(String(16), nullable=False)  # user | assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    actions: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of proposed actions
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())
