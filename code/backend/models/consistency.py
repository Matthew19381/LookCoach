from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, String, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import enum


class ProtocolTypeEnum(str, enum.Enum):
    SKINCARE_MORNING = "skincare_morning"
    SKINCARE_EVENING = "skincare_evening"
    TRAINING = "training"
    SLEEP = "sleep"
    NUTRITION = "nutrition"
    STRESS = "stress"


class DifficultyLevelEnum(str, enum.Enum):
    FULL = "full"
    REDUCED = "reduced"
    MINIMUM = "minimum"
    SURVIVAL = "survival"


class AdherenceLevelEnum(str, enum.Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    LOW = "low"
    CRITICAL = "critical"


class AdherenceLog(Base):
    """Daily adherence log for each protocol type."""
    __tablename__ = "adherence_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    protocol_type = Column(SQLEnum(ProtocolTypeEnum), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    completed = Column(Boolean, nullable=False, default=False)
    difficulty_level = Column(SQLEnum(DifficultyLevelEnum), nullable=False, default=DifficultyLevelEnum.FULL)
    notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="adherence_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "protocol_type": self.protocol_type.value,
            "date": self.date.isoformat() if self.date else None,
            "completed": self.completed,
            "difficulty_level": self.difficulty_level.value,
            "notes": self.notes,
        }


class ProtocolAdherence(Base):
    """Aggregated adherence metrics per protocol per period."""
    __tablename__ = "protocol_adherence"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    protocol_type = Column(SQLEnum(ProtocolTypeEnum), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)
    period_days = Column(Integer, nullable=False)
    total_scheduled = Column(Integer, nullable=False, default=0)
    total_completed = Column(Integer, nullable=False, default=0)
    adherence_rate = Column(Float, nullable=False, default=1.0)
    adherence_level = Column(SQLEnum(AdherenceLevelEnum), nullable=False, default=AdherenceLevelEnum.EXCELLENT)
    current_difficulty = Column(SQLEnum(DifficultyLevelEnum), nullable=False, default=DifficultyLevelEnum.FULL)
    recommended_difficulty = Column(SQLEnum(DifficultyLevelEnum), nullable=False, default=DifficultyLevelEnum.FULL)
    consecutive_misses = Column(Integer, nullable=False, default=0)
    longest_streak = Column(Integer, nullable=False, default=0)
    current_streak = Column(Integer, nullable=False, default=0)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="protocol_adherence")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "protocol_type": self.protocol_type.value,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "period_days": self.period_days,
            "total_scheduled": self.total_scheduled,
            "total_completed": self.total_completed,
            "adherence_rate": self.adherence_rate,
            "adherence_level": self.adherence_level.value,
            "current_difficulty": self.current_difficulty.value,
            "recommended_difficulty": self.recommended_difficulty.value,
            "consecutive_misses": self.consecutive_misses,
            "longest_streak": self.longest_streak,
            "current_streak": self.current_streak,
        }


class ConsistencyMetrics(Base):
    """Overall consistency metrics snapshot."""
    __tablename__ = "consistency_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)
    period_days = Column(Integer, nullable=False)
    overall_consistency_score = Column(Float, nullable=False, default=1.0)
    system_status = Column(String(50), nullable=False, default="thriving")
    protocols_tracked = Column(Integer, nullable=False, default=0)
    protocols_needing_reduction = Column(Integer, nullable=False, default=0)
    average_adherence = Column(Float, nullable=False, default=1.0)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="consistency_metrics")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "period_days": self.period_days,
            "overall_consistency_score": self.overall_consistency_score,
            "system_status": self.system_status,
            "protocols_tracked": self.protocols_tracked,
            "protocols_needing_reduction": self.protocols_needing_reduction,
            "average_adherence": self.average_adherence,
        }