from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .base import Base


class IntegrationEvent(Base):
    """Event received from another module of the System-Główny ecosystem."""

    __tablename__ = "integration_events"

    id = Column(Integer, primary_key=True, index=True)
    source_module = Column(String(50), nullable=False)  # e.g. "systemglowny", "linguaai"
    event_type = Column(String(100), nullable=False)
    user_id = Column(String(64), nullable=False)
    timestamp = Column(String(64))  # ISO string supplied by the sending module
    payload = Column(Text)  # JSON blob
    received_at = Column(DateTime(timezone=True), server_default=func.now())
