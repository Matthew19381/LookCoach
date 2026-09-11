from datetime import datetime
from typing import Optional
from enum import Enum


class ProtocolType(str, Enum):
    SKINCARE_MORNING = "skincare_morning"
    SKINCARE_EVENING = "skincare_evening"
    TRAINING = "training"
    SLEEP = "sleep"
    NUTRITION = "nutrition"
    STRESS = "stress"


class AdherenceLevel(str, Enum):
    EXCELLENT = "excellent"      # >= 90%
    GOOD = "good"                # 75-89%
    MODERATE = "moderate"        # 50-74%
    LOW = "low"                  # 25-49%
    CRITICAL = "critical"        # < 25%


class DifficultyLevel(str, Enum):
    FULL = "full"                # 100% - standard plan
    REDUCED = "reduced"          # 75% - moderate reduction
    MINIMUM = "minimum"          # 50% - minimum effective dose
    SURVIVAL = "survival"        # 25% - absolute basics only


# Thresholds based on Lally 2010 (habit formation) and behavioral activation principles
ADHERENCE_THRESHOLDS = {
    AdherenceLevel.EXCELLENT: 0.90,
    AdherenceLevel.GOOD: 0.75,
    AdherenceLevel.MODERATE: 0.50,
    AdherenceLevel.LOW: 0.25,
    AdherenceLevel.CRITICAL: 0.0,
}

# Minimum effective dose reductions per protocol type
MINIMUM_EFFECTIVE_DOSE = {
    ProtocolType.SKINCARE_MORNING: {
        DifficultyLevel.FULL: ["cleanser", "antioxidant", "hydration", "spf"],
        DifficultyLevel.REDUCED: ["cleanser", "spf", "hydration"],
        DifficultyLevel.MINIMUM: ["cleanser", "spf"],
        DifficultyLevel.SURVIVAL: ["splash_water", "spf"],
    },
    ProtocolType.SKINCARE_EVENING: {
        DifficultyLevel.FULL: ["cleanser", "treatment", "hydration", "barrier"],
        DifficultyLevel.REDUCED: ["cleanser", "treatment", "hydration"],
        DifficultyLevel.MINIMUM: ["cleanser", "hydration"],
        DifficultyLevel.SURVIVAL: ["splash_water", "moisturizer"],
    },
    ProtocolType.TRAINING: {
        DifficultyLevel.FULL: ["full_session", "accessory_work", "progression"],
        DifficultyLevel.REDUCED: ["main_lifts", "reduced_volume"],
        DifficultyLevel.MINIMUM: ["1_main_lift", "bodyweight"],
        DifficultyLevel.SURVIVAL: ["walk_15min", "stretch_5min"],
    },
    ProtocolType.SLEEP: {
        DifficultyLevel.FULL: ["8h_target", "consistent_schedule", "wind_down"],
        DifficultyLevel.REDUCED: ["7h_target", "consistent_wake"],
        DifficultyLevel.MINIMUM: ["consistent_wake_time"],
        DifficultyLevel.SURVIVAL: ["any_sleep"],
    },
    ProtocolType.NUTRITION: {
        DifficultyLevel.FULL: ["protein_target", "vegetables", "hydration", "sodium_limit"],
        DifficultyLevel.REDUCED: ["protein_target", "hydration"],
        DifficultyLevel.MINIMUM: ["protein_target"],
        DifficultyLevel.SURVIVAL: ["eat_something"],
    },
    ProtocolType.STRESS: {
        DifficultyLevel.FULL: ["meditation", "breathing", "nature", "social"],
        DifficultyLevel.REDUCED: ["breathing_5min", "short_walk"],
        DifficultyLevel.MINIMUM: ["breathing_2min"],
        DifficultyLevel.SURVIVAL: ["one_deep_breath"],
    },
}


class ConsistencyTracker:
    """
    Consistency Tracker + Minimum Effective System (LC-7 / FB-5).

    Core principle: Adherence drives plan difficulty.
    When adherence drops below threshold → reduce difficulty (minimum effective dose),
    never "motivate harder" or add guilt/shame.

    Based on: Lally 2010 (single miss doesn't break habit),
    Behavioral Activation (Cuijpers 2007; Ekers 2014),
    ForgeBody FB-5 (adherence as first-class metric).
    """

    def __init__(self, db_session=None, user_id: int = 1):
        self.db = db_session
        self.user_id = user_id

    def log_adherence(
        self,
        protocol_type: ProtocolType,
        completed: bool,
        date: Optional[datetime] = None,
        difficulty_level: DifficultyLevel = DifficultyLevel.FULL,
        notes: str = "",
    ) -> dict:
        """Log whether a protocol was completed on a given day."""
        if date is None:
            date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        record = {
            "user_id": self.user_id,
            "protocol_type": protocol_type.value,
            "date": date.isoformat(),
            "completed": completed,
            "difficulty_level": difficulty_level.value,
            "notes": notes,
            "logged_at": datetime.now().isoformat(),
        }

        # In full implementation, this would persist to DB
        return record

    def get_adherence_history(
        self,
        protocol_type: ProtocolType,
        days: int = 28,
    ) -> list[dict]:
        """Get adherence history for a protocol type."""
        # In full implementation, this would query DB
        # Return empty list for now - placeholder
        return []

    def calculate_adherence_rate(
        self,
        protocol_type: ProtocolType,
        days: int = 28,
    ) -> float:
        """Calculate adherence rate (0.0-1.0) over the last N days."""
        history = self.get_adherence_history(protocol_type, days)
        if not history:
            return 1.0  # No history = assume perfect (neutral start)

        completed = sum(1 for h in history if h.get("completed", False))
        total = len(history)
        return completed / total if total > 0 else 1.0

    def get_adherence_level(self, rate: float) -> AdherenceLevel:
        """Map adherence rate to adherence level."""
        if rate >= ADHERENCE_THRESHOLDS[AdherenceLevel.EXCELLENT]:
            return AdherenceLevel.EXCELLENT
        elif rate >= ADHERENCE_THRESHOLDS[AdherenceLevel.GOOD]:
            return AdherenceLevel.GOOD
        elif rate >= ADHERENCE_THRESHOLDS[AdherenceLevel.MODERATE]:
            return AdherenceLevel.MODERATE
        elif rate >= ADHERENCE_THRESHOLDS[AdherenceLevel.LOW]:
            return AdherenceLevel.LOW
        return AdherenceLevel.CRITICAL

    def get_recommended_difficulty(
        self,
        protocol_type: ProtocolType,
        current_difficulty: DifficultyLevel = DifficultyLevel.FULL,
    ) -> DifficultyLevel:
        """
        Determine recommended difficulty based on recent adherence.

        Core rule (LC-7/FB-5):
        - Adherence >= 75% → maintain or increase difficulty
        - Adherence 50-74% → reduce one level
        - Adherence 25-49% → reduce two levels (minimum effective dose)
        - Adherence < 25% → survival mode

        Never increases difficulty if adherence < 75%.
        Only increases after sustained >= 90% for 2+ weeks.
        """
        rate = self.calculate_adherence_rate(protocol_type, 28)
        level = self.get_adherence_level(rate)

        # Map adherence level to target difficulty
        target_map = {
            AdherenceLevel.EXCELLENT: DifficultyLevel.FULL,
            AdherenceLevel.GOOD: DifficultyLevel.FULL,
            AdherenceLevel.MODERATE: DifficultyLevel.REDUCED,
            AdherenceLevel.LOW: DifficultyLevel.MINIMUM,
            AdherenceLevel.CRITICAL: DifficultyLevel.SURVIVAL,
        }

        target = target_map[level]

        # Hysteresis: don't bounce up/down rapidly
        # Only increase if current is already at target and adherence is EXCELLENT
        difficulty_order = [
            DifficultyLevel.SURVIVAL,
            DifficultyLevel.MINIMUM,
            DifficultyLevel.REDUCED,
            DifficultyLevel.FULL,
        ]

        current_idx = difficulty_order.index(current_difficulty)
        target_idx = difficulty_order.index(target)

        if target_idx > current_idx:
            # Want to increase - only allow if EXCELLENT adherence sustained
            if level == AdherenceLevel.EXCELLENT:
                # Check 14-day rate for sustained excellence
                rate_14 = self.calculate_adherence_rate(protocol_type, 14)
                if rate_14 >= ADHERENCE_THRESHOLDS[AdherenceLevel.EXCELLENT]:
                    return difficulty_order[min(current_idx + 1, target_idx)]
            return current_difficulty  # Stay at current

        return target  # Reduce or maintain

    def get_minimum_effective_protocol(
        self,
        protocol_type: ProtocolType,
        difficulty: DifficultyLevel,
    ) -> list[str]:
        """Get the minimum effective protocol steps for given difficulty."""
        return MINIMUM_EFFECTIVE_DOSE.get(protocol_type, {}).get(difficulty, [])

    def get_all_protocols_status(self) -> dict:
        """Get adherence status and recommended difficulty for all protocol types."""
        status = {}
        for protocol_type in ProtocolType:
            rate = self.calculate_adherence_rate(protocol_type, 28)
            level = self.get_adherence_level(rate)
            current_diff = DifficultyLevel.FULL  # Would come from user preferences
            recommended_diff = self.get_recommended_difficulty(protocol_type, current_diff)
            min_protocol = self.get_minimum_effective_protocol(protocol_type, recommended_diff)

            status[protocol_type.value] = {
                "adherence_rate": round(rate, 2),
                "adherence_level": level.value,
                "current_difficulty": current_diff.value,
                "recommended_difficulty": recommended_diff.value,
                "minimum_effective_protocol": min_protocol,
                "needs_reduction": recommended_diff != DifficultyLevel.FULL,
            }

        return status

    def get_consistency_summary(self, days: int = 28) -> dict:
        """Get overall consistency summary across all protocols."""
        all_status = self.get_all_protocols_status()

        total_protocols = len(all_status)
        protocols_needing_reduction = sum(1 for s in all_status.values() if s["needs_reduction"])
        avg_adherence = sum(s["adherence_rate"] for s in all_status.values()) / total_protocols

        # Overall system status
        if avg_adherence >= 0.9:
            system_status = "thriving"
        elif avg_adherence >= 0.75:
            system_status = "stable"
        elif avg_adherence >= 0.5:
            system_status = "adjusting"
        elif avg_adherence >= 0.25:
            system_status = "minimum_effective"
        else:
            system_status = "survival"

        return {
            "period_days": days,
            "average_adherence": round(avg_adherence, 2),
            "system_status": system_status,
            "total_protocols": total_protocols,
            "protocols_needing_reduction": protocols_needing_reduction,
            "protocols": all_status,
            "message": self._get_system_message(system_status),
        }

    def _get_system_message(self, status: str) -> str:
        """Get supportive message based on system status."""
        messages = {
            "thriving": "Consistency is excellent. Your plan is well-calibrated.",
            "stable": "Good consistency. Minor adjustments may help optimize.",
            "adjusting": "Some protocols need difficulty reduction. This is normal adaptation, not failure.",
            "minimum_effective": "Running minimum effective protocols. Focus on showing up, not perfection.",
            "survival": "Survival mode active. Absolute basics only. Be kind to yourself — showing up matters.",
        }
        return messages.get(status, "Tracking consistency...")

    def get_weekly_adherence_trend(self, protocol_type: ProtocolType, weeks: int = 4) -> list[dict]:
        """Get weekly adherence trend for visualization."""
        # Placeholder - would query DB with weekly grouping
        return []

    def should_trigger_pattern_alert(self, protocol_type: ProtocolType) -> tuple[bool, str]:
        """
        Check if adherence pattern warrants alert to Mentalność (MP-2).

        Pattern alert criteria (aligned with Mentalność MP-2):
        - 3+ consecutive missed days on any protocol
        - Adherence < 50% for 2+ weeks
        - Multiple protocols declining simultaneously
        """
        # Check consecutive misses
        history = self.get_adherence_history(protocol_type, 21)
        consecutive_misses = 0
        for h in reversed(history):  # Most recent first
            if not h.get("completed", False):
                consecutive_misses += 1
            else:
                break

        if consecutive_misses >= 3:
            return True, f"{protocol_type.value}: {consecutive_misses} consecutive missed days"

        # Check 2-week adherence
        rate_14 = self.calculate_adherence_rate(protocol_type, 14)
        if rate_14 < 0.5:
            return True, f"{protocol_type.value}: adherence {rate_14:.0%} over 14 days"

        return False, ""


def calculate_overall_consistency_score(protocol_rates: dict[ProtocolType, float]) -> float:
    """
    Calculate weighted overall consistency score.
    Weights based on NEURO_PLAN LC-7 priority and ForgeBody FB-5.
    """
    weights = {
        ProtocolType.SKINCARE_MORNING: 0.15,
        ProtocolType.SKINCARE_EVENING: 0.15,
        ProtocolType.TRAINING: 0.30,
        ProtocolType.SLEEP: 0.20,
        ProtocolType.NUTRITION: 0.10,
        ProtocolType.STRESS: 0.10,
    }

    total_weight = sum(weights.values())
    weighted_sum = sum(
        protocol_rates.get(pt, 1.0) * w
        for pt, w in weights.items()
    )

    return weighted_sum / total_weight if total_weight > 0 else 1.0