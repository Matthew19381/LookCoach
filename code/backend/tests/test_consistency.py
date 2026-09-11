from datetime import datetime, timedelta
from services.consistency_tracker import (
    ConsistencyTracker,
    ProtocolType,
    DifficultyLevel,
    AdherenceLevel,
    ADHERENCE_THRESHOLDS,
    MINIMUM_EFFECTIVE_DOSE,
    calculate_overall_consistency_score,
)


def test_consistency_tracker_basic():
    """Test basic tracker initialization."""
    tracker = ConsistencyTracker()
    assert tracker.user_id == 1


def test_adherence_rate_no_history():
    """Test adherence rate with no history returns 1.0 (neutral start)."""
    tracker = ConsistencyTracker()
    rate = tracker.calculate_adherence_rate(ProtocolType.SKINCARE_MORNING, 28)
    assert rate == 1.0


def test_adherence_level_mapping():
    """Test adherence rate to level mapping."""
    tracker = ConsistencyTracker()

    assert tracker.get_adherence_level(0.95) == AdherenceLevel.EXCELLENT
    assert tracker.get_adherence_level(0.85) == AdherenceLevel.GOOD
    assert tracker.get_adherence_level(0.65) == AdherenceLevel.MODERATE
    assert tracker.get_adherence_level(0.35) == AdherenceLevel.LOW
    assert tracker.get_adherence_level(0.15) == AdherenceLevel.CRITICAL

    # Boundary tests
    assert tracker.get_adherence_level(0.90) == AdherenceLevel.EXCELLENT
    assert tracker.get_adherence_level(0.75) == AdherenceLevel.GOOD
    assert tracker.get_adherence_level(0.50) == AdherenceLevel.MODERATE
    assert tracker.get_adherence_level(0.25) == AdherenceLevel.LOW


def test_recommended_difficulty_basic():
    """Test recommended difficulty based on adherence level."""
    tracker = ConsistencyTracker()

    # Mock high adherence (EXCELLENT)
    tracker.calculate_adherence_rate = lambda pt, days: 0.95
    diff = tracker.get_recommended_difficulty(ProtocolType.TRAINING, DifficultyLevel.FULL)
    assert diff == DifficultyLevel.FULL

    # Mock GOOD adherence
    tracker.calculate_adherence_rate = lambda pt, days: 0.80
    diff = tracker.get_recommended_difficulty(ProtocolType.TRAINING, DifficultyLevel.FULL)
    assert diff == DifficultyLevel.FULL

    # Mock MODERATE adherence
    tracker.calculate_adherence_rate = lambda pt, days: 0.60
    diff = tracker.get_recommended_difficulty(ProtocolType.TRAINING, DifficultyLevel.FULL)
    assert diff == DifficultyLevel.REDUCED

    # Mock LOW adherence
    tracker.calculate_adherence_rate = lambda pt, days: 0.35
    diff = tracker.get_recommended_difficulty(ProtocolType.TRAINING, DifficultyLevel.FULL)
    assert diff == DifficultyLevel.MINIMUM

    # Mock CRITICAL adherence
    tracker.calculate_adherence_rate = lambda pt, days: 0.10
    diff = tracker.get_recommended_difficulty(ProtocolType.TRAINING, DifficultyLevel.FULL)
    assert diff == DifficultyLevel.SURVIVAL


def test_hysteresis_prevents_bounce():
    """Test hysteresis prevents rapid difficulty bouncing."""
    tracker = ConsistencyTracker()

    # Currently at REDUCED, adherence is MODERATE (should stay REDUCED)
    tracker.calculate_adherence_rate = lambda pt, days: 0.60
    diff = tracker.get_recommended_difficulty(ProtocolType.TRAINING, DifficultyLevel.REDUCED)
    assert diff == DifficultyLevel.REDUCED  # Should not bounce to FULL

    # Currently at MINIMUM, adherence is EXCELLENT but 14-day not sustained
    tracker.calculate_adherence_rate = lambda pt, days: 0.95
    # But 14-day is also 0.95
    diff = tracker.get_recommended_difficulty(ProtocolType.TRAINING, DifficultyLevel.MINIMUM)
    assert diff == DifficultyLevel.REDUCED  # Should only increase one step


def test_minimum_effective_protocol():
    """Test minimum effective protocol retrieval."""
    tracker = ConsistencyTracker()

    # Skincare morning at different difficulties
    full = tracker.get_minimum_effective_protocol(ProtocolType.SKINCARE_MORNING, DifficultyLevel.FULL)
    assert "cleanser" in full
    assert "antioxidant" in full
    assert "hydration" in full
    assert "spf" in full

    reduced = tracker.get_minimum_effective_protocol(ProtocolType.SKINCARE_MORNING, DifficultyLevel.REDUCED)
    assert "cleanser" in reduced
    assert "spf" in reduced
    assert "hydration" in reduced
    assert "antioxidant" not in reduced  # Dropped at reduced

    minimum = tracker.get_minimum_effective_protocol(ProtocolType.SKINCARE_MORNING, DifficultyLevel.MINIMUM)
    assert "cleanser" in minimum
    assert "spf" in minimum
    assert len(minimum) == 2

    survival = tracker.get_minimum_effective_protocol(ProtocolType.SKINCARE_MORNING, DifficultyLevel.SURVIVAL)
    assert "splash_water" in survival
    assert "spf" in survival


def test_training_minimum_effective():
    """Test training minimum effective protocols."""
    tracker = ConsistencyTracker()

    full = tracker.get_minimum_effective_protocol(ProtocolType.TRAINING, DifficultyLevel.FULL)
    assert "full_session" in full
    assert "accessory_work" in full

    minimum = tracker.get_minimum_effective_protocol(ProtocolType.TRAINING, DifficultyLevel.MINIMUM)
    assert "1_main_lift" in minimum
    assert "bodyweight" in minimum

    survival = tracker.get_minimum_effective_protocol(ProtocolType.TRAINING, DifficultyLevel.SURVIVAL)
    assert "walk_15min" in survival
    assert "stretch_5min" in survival


def test_get_all_protocols_status():
    """Test getting status for all protocols."""
    tracker = ConsistencyTracker()
    tracker.calculate_adherence_rate = lambda pt, days: 0.85  # GOOD for all

    status = tracker.get_all_protocols_status()

    assert len(status) == 6  # All 6 protocol types
    for pt_key, data in status.items():
        assert "adherence_rate" in data
        assert "adherence_level" in data
        assert "recommended_difficulty" in data
        assert "minimum_effective_protocol" in data
        assert "needs_reduction" in data
        # At 85% adherence, should be FULL difficulty, no reduction needed
        assert data["recommended_difficulty"] == "full"
        assert data["needs_reduction"] is False


def test_consistency_summary_thriving():
    """Test consistency summary at thriving level."""
    tracker = ConsistencyTracker()
    tracker.calculate_adherence_rate = lambda pt, days: 0.95

    summary = tracker.get_consistency_summary(28)

    assert summary["average_adherence"] == 0.95
    assert summary["system_status"] == "thriving"
    assert summary["protocols_needing_reduction"] == 0
    assert "message" in summary


def test_consistency_summary_stable():
    """Test consistency summary at stable level."""
    tracker = ConsistencyTracker()
    tracker.calculate_adherence_rate = lambda pt, days: 0.80

    summary = tracker.get_consistency_summary(28)

    assert summary["average_adherence"] == 0.80
    assert summary["system_status"] == "stable"


def test_consistency_summary_adjusting():
    """Test consistency summary at adjusting level."""
    tracker = ConsistencyTracker()
    tracker.calculate_adherence_rate = lambda pt, days: 0.60

    summary = tracker.get_consistency_summary(28)

    assert summary["average_adherence"] == 0.60
    assert summary["system_status"] == "adjusting"
    assert summary["protocols_needing_reduction"] == 6  # All protocols below 75%


def test_consistency_summary_minimum_effective():
    """Test consistency summary at minimum effective level."""
    tracker = ConsistencyTracker()
    tracker.calculate_adherence_rate = lambda pt, days: 0.35

    summary = tracker.get_consistency_summary(28)

    assert summary["average_adherence"] == 0.35
    assert summary["system_status"] == "minimum_effective"


def test_consistency_summary_survival():
    """Test consistency summary at survival level."""
    tracker = ConsistencyTracker()
    tracker.calculate_adherence_rate = lambda pt, days: 0.10

    summary = tracker.get_consistency_summary(28)

    assert summary["average_adherence"] == 0.10
    assert summary["system_status"] == "survival"


def test_system_messages_supportive():
    """Test that system messages are supportive, not shaming."""
    tracker = ConsistencyTracker()

    # Check all status messages don't contain shaming language
    for status in ["thriving", "stable", "adjusting", "minimum_effective", "survival"]:
        tracker.calculate_adherence_rate = lambda pt, days: 0.5 if status == "adjusting" else 0.1
        summary = tracker.get_consistency_summary(28)
        message = summary["message"].lower()

        # No shaming words (but "not failure" is supportive framing)
        assert "failed" not in message
        assert "lazy" not in message
        assert "shame" not in message
        assert "guilt" not in message
        assert "punish" not in message
        assert "bad" not in message
        # "failure" is allowed only as "not failure" (supportive reframing)
        if "failure" in message:
            assert "not failure" in message

        # Supportive language present
        supportive_words = ["normal", "adaptation", "kind", "showing up", "matters", "focus", "calibrated", "optimize"]
        assert any(word in message for word in supportive_words), f"Message for {status} lacks supportive language: {message}"


def test_overall_consistency_score():
    """Test weighted overall consistency score calculation."""
    rates = {
        ProtocolType.SKINCARE_MORNING: 0.9,
        ProtocolType.SKINCARE_EVENING: 0.8,
        ProtocolType.TRAINING: 0.7,
        ProtocolType.SLEEP: 0.85,
        ProtocolType.NUTRITION: 0.75,
        ProtocolType.STRESS: 0.6,
    }

    score = calculate_overall_consistency_score(rates)

    # Weights: skincare_am=0.15, skincare_pm=0.15, training=0.30, sleep=0.20, nutrition=0.10, stress=0.10
    expected = (0.9*0.15 + 0.8*0.15 + 0.7*0.30 + 0.85*0.20 + 0.75*0.10 + 0.6*0.10) / 1.0
    assert abs(score - expected) < 0.001


def test_overall_consistency_score_partial():
    """Test overall consistency score with partial protocols - missing default to 1.0."""
    rates = {
        ProtocolType.TRAINING: 0.8,
        ProtocolType.SLEEP: 0.9,
    }

    score = calculate_overall_consistency_score(rates)

    # Missing protocols default to 1.0
    # Weights: skincare_am=0.15, skincare_pm=0.15, training=0.30, sleep=0.20, nutrition=0.10, stress=0.10
    expected = (1.0*0.15 + 1.0*0.15 + 0.8*0.30 + 0.9*0.20 + 1.0*0.10 + 1.0*0.10) / 1.0
    assert abs(score - expected) < 0.001


def test_adherence_thresholds_complete():
    """Test all adherence thresholds are defined."""
    expected_levels = [AdherenceLevel.EXCELLENT, AdherenceLevel.GOOD, AdherenceLevel.MODERATE, AdherenceLevel.LOW, AdherenceLevel.CRITICAL]
    for level in expected_levels:
        assert level in ADHERENCE_THRESHOLDS

    # Thresholds should be descending
    assert ADHERENCE_THRESHOLDS[AdherenceLevel.EXCELLENT] > ADHERENCE_THRESHOLDS[AdherenceLevel.GOOD]
    assert ADHERENCE_THRESHOLDS[AdherenceLevel.GOOD] > ADHERENCE_THRESHOLDS[AdherenceLevel.MODERATE]
    assert ADHERENCE_THRESHOLDS[AdherenceLevel.MODERATE] > ADHERENCE_THRESHOLDS[AdherenceLevel.LOW]
    assert ADHERENCE_THRESHOLDS[AdherenceLevel.LOW] > ADHERENCE_THRESHOLDS[AdherenceLevel.CRITICAL]


def test_minimum_effective_dose_complete():
    """Test all protocol types have minimum effective dose definitions."""
    for pt in ProtocolType:
        assert pt in MINIMUM_EFFECTIVE_DOSE
        for dl in DifficultyLevel:
            assert dl in MINIMUM_EFFECTIVE_DOSE[pt]
            assert len(MINIMUM_EFFECTIVE_DOSE[pt][dl]) > 0


def test_pattern_alert_consecutive_misses():
    """Test pattern alert for consecutive missed days."""
    tracker = ConsistencyTracker()

    # Mock 3+ consecutive misses
    tracker.get_adherence_history = lambda pt, days: [
        {"completed": False, "date": (datetime.now() - timedelta(days=i)).isoformat()}
        for i in range(3)
    ]

    should_alert, message = tracker.should_trigger_pattern_alert(ProtocolType.TRAINING)
    assert should_alert is True
    assert "3 consecutive missed days" in message


def test_pattern_alert_low_adherence():
    """Test pattern alert for sustained low adherence."""
    tracker = ConsistencyTracker()

    # Mock 14-day rate < 50%
    tracker.calculate_adherence_rate = lambda pt, days: 0.4 if days == 14 else 0.6
    tracker.get_adherence_history = lambda pt, days: [
        {"completed": True, "date": (datetime.now() - timedelta(days=i)).isoformat()}
        for i in range(5)
    ]

    should_alert, message = tracker.should_trigger_pattern_alert(ProtocolType.TRAINING)
    assert should_alert is True
    assert "adherence 40% over 14 days" in message


def test_pattern_alert_no_alert_when_good():
    """Test no pattern alert when adherence is good."""
    tracker = ConsistencyTracker()

    tracker.get_adherence_history = lambda pt, days: [
        {"completed": True, "date": (datetime.now() - timedelta(days=i)).isoformat()}
        for i in range(10)
    ]
    tracker.calculate_adherence_rate = lambda pt, days: 0.85

    should_alert, message = tracker.should_trigger_pattern_alert(ProtocolType.TRAINING)
    assert should_alert is False


def test_log_adherence_record():
    """Test logging adherence creates proper record."""
    tracker = ConsistencyTracker()

    record = tracker.log_adherence(
        protocol_type=ProtocolType.SKINCARE_MORNING,
        completed=True,
        difficulty_level=DifficultyLevel.FULL,
        notes="Felt good",
    )

    assert record["protocol_type"] == "skincare_morning"
    assert record["completed"] is True
    assert record["difficulty_level"] == "full"
    assert record["notes"] == "Felt good"
    assert "user_id" in record
    assert "date" in record
    assert "logged_at" in record


def test_difficulty_order():
    """Test difficulty level ordering for hysteresis."""
    order = [
        DifficultyLevel.SURVIVAL,
        DifficultyLevel.MINIMUM,
        DifficultyLevel.REDUCED,
        DifficultyLevel.FULL,
    ]

    assert order.index(DifficultyLevel.SURVIVAL) < order.index(DifficultyLevel.MINIMUM)
    assert order.index(DifficultyLevel.MINIMUM) < order.index(DifficultyLevel.REDUCED)
    assert order.index(DifficultyLevel.REDUCED) < order.index(DifficultyLevel.FULL)