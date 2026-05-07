from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text, Float, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), nullable=False)  # skincare, training, nutrition, sleep, stress
    name = Column(String(100), nullable=False)
    description = Column(Text)
    evidence_level = Column(String(20))  # RCT, meta, observational, expert
    effect_size = Column(Float)  # 0.0 - 1.0
    time_to_effect = Column(Integer)  # weeks
    roi_score = Column(Float, default=0.0)
    priority = Column(Integer, default=0)
    is_done = Column(String(1), default="N")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="recommendations")
