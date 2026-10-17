from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from .base import Base


class RoutineStep(Base):
    """One step of the user's own skincare routine (owner request 2026-10-15:
    "tworzenie rutyny i podgląd co dzisiaj ma być")."""

    __tablename__ = "routine_steps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True, default=1)
    slot = Column(String, nullable=False)  # morning | evening
    position = Column(Integer, nullable=False, default=0)
    name = Column(String, nullable=False)
    product_id = Column(Integer, nullable=True)  # skincare_products.id, optional
    weekdays = Column(String, nullable=False, default="0123456")  # Mon=0 .. Sun=6
    essential = Column(Boolean, nullable=False, default=False)  # kept in survival mode
    active = Column(Boolean, nullable=False, default=True)
    evidence_key = Column(String, nullable=True)  # key in services/routine_defaults.EVIDENCE
    note = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
