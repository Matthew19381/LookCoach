from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .base import Base


class DirectiveState(Base):
    """Latest directives from the System-Główny hub (INT-3)."""

    __tablename__ = "directive_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    survival_mode = Column(Boolean, default=False)
    priority = Column(String, nullable=True)
    quiet_hours_from = Column(String, nullable=True)
    quiet_hours_to = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
