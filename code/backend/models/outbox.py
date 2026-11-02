from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .base import Base


class OutboxEvent(Base):
    """Event waiting to be (or already) delivered to the System-Główny hub (plan 3.1).

    `timestamp` is fixed when the event is queued: the hub deduplicates on
    module+user+type+timestamp, so retries are idempotent.
    """

    __tablename__ = "outbox_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, default=1)
    event_type = Column(String(100), nullable=False)
    data = Column(Text, nullable=False, default="{}")  # JSON
    timestamp = Column(String(64), nullable=False)  # ISO, sent as-is
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending | sent | failed
    attempts = Column(Integer, nullable=False, default=0)
    next_attempt_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    hub_response = Column(Text, nullable=True)  # JSON of the hub's answer (plan_item, rules...)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
