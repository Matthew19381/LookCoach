from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON

from .base import Base


class Experiment(Base):
    """Personal A/B experiment started by a user."""

    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False, default=1)
    template_id = Column(String, nullable=False)
    name = Column(String, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    # Full experiment dict produced/consumed by PersonalExperimentEngine
    data = Column(JSON, default=dict)
