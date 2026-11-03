from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class PushSubscription(Base):
    """A browser's Web Push subscription (plan 5.5)."""

    __tablename__ = "push_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=1)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    p256dh: Mapped[str] = mapped_column(String(200), nullable=False)
    auth: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReminderSettings(Base):
    __tablename__ = "reminder_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    morning_time: Mapped[str] = mapped_column(String(5), default="07:30")  # HH:MM local
    evening_time: Mapped[str] = mapped_column(String(5), default="21:30")
    photo_reminders: Mapped[bool] = mapped_column(Boolean, default=True)


class ReminderLog(Base):
    """Which reminder was sent on which day - each at most once a day."""

    __tablename__ = "reminder_logs"
    __table_args__ = (UniqueConstraint("user_id", "kind", "day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False)
