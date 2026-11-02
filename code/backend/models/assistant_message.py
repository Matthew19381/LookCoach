from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .base import Base


class AssistantMessage(Base):
    """One turn of the LookCoach assistant conversation (plan 8.2)."""

    __tablename__ = "assistant_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, default=1)
    role = Column(String(16), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    actions = Column(Text, nullable=True)  # JSON list of proposed actions (assistant only)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
