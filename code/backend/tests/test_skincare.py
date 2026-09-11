from services.skincare_engine import (
    SkincareEngine,
    SkinReactionTracker,
    IngredientRotationManager,
    SKINCARE_INGREDIENTS,
    TOLERANCE_LEVELS,
    ROTATION_SCHEDULE,
)


def test_skincare_engine_basic_routine():
    """Test basic routine generation still works."""
    routine = SkincareEngine.generate_routine({"skin_type": "dry"}, {"sleep": 7})
    assert "morning" in routine
    assert "evening" in routine
    assert len(routine["morning"]) > 0
    assert len(routine["evening"]) > 0
    assert routine["skin_type"] == "dry"


def test_adaptive_routine_basic():
    """Test adaptive routine generation."""
    engine = SkincareEngine()
    routine = engine.generate_adaptive_routine(
        skin_analysis={"skin_type": "combination", "problems": []},
        lifestyle={"sleep": 7, "stress": 5}
    )
    assert "morning" in routine
    assert "evening" in routine
    assert "sensitivity_level" in routine
    assert "adaptations" in routine
    assert "rotation_recommendations" in routine
    assert "notes" in routine


def test_adaptive_routine_morning_has_spf():
    """Test morning routine always includes SPF."""
    engine = SkincareEngine()
    routine = engine.generate_adaptive_routine(
        skin_analysis={"skin_type": "combination", "problems": []},
        lifestyle={}
    )
    assert "SPF 30+" in routine["morning"]


def test_adaptive_routine_acne_track():
    """Test acne track in evening routine."""
    engine = SkincareEngine()
    routine = engine.generate_adaptive_routine(
        skin_analysis={
            "skin_type": "oily",
            "problems": [{"issue": "acne"}, {"issue": "breakouts"}]
        },
        lifestyle={}
    )
    # Should include BHA for acne in evening
    bha_items = [item for item in routine["evening"] if "BHA" in item or "Salicylic" in item]
    assert len(bha_items) > 0, f"BHA not found in evening: {routine['evening']}"
    # Zinc PCA should be in evening for acne
    zinc_items = [item for item in routine["evening"] if "Zinc" in item]
    assert len(zinc_items) > 0, f"Zinc not found in evening: {routine['evening']}"


def test_adaptive_routine_aging_track():
    """Test anti-aging track with retinoid."""
    engine = SkincareEngine()
    routine = engine.generate_adaptive_routine(
        skin_analysis={"skin_type": "dry", "problems": []},
        lifestyle={}
    )
    # Should include some form of retinoid for aging
    has_retinoid = any("Retinol" in item or "Retinaldehyde" in item for item in routine["evening"])
    assert has_retinoid, f"Retinoid not found in evening: {routine['evening']}"


def test_adaptive_routine_dry_skin():
    """Test dry skin gets hydrating ingredients."""
    engine = SkincareEngine()
    routine = engine.generate_adaptive_routine(
        skin_analysis={"skin_type": "dry"},
        lifestyle={}
    )
    assert "Hyaluronic Acid" in routine["morning"]
    assert "Ceramide Moisturizer" in routine["evening"]
    assert "Squalane Oil" in routine["evening"]


def test_sensitivity_none_allows_retinoid():
    """Test no sensitivity allows standard retinoid."""
    engine = SkincareEngine()
    routine = engine.generate_adaptive_routine(
        skin_analysis={"skin_type": "normal", "problems": []},
        lifestyle={}
    )
    has_retinoid = any("Retinol" in item or "Retinaldehyde" in item for item in routine["evening"])
    assert has_retinoid


def test_sensitivity_high_avoids_retinoid():
    """Test high sensitivity avoids retinoids and exfoliants."""
    engine = SkincareEngine()
    # Mock high sensitivity
    engine.reaction_tracker.get_overall_sensitivity = lambda: "high"
    engine.reaction_tracker.get_tolerance_level = lambda x: "high" if "Retinol" in x or "Retinaldehyde" in x or "BHA" in x or "AHA" in x else "none"

    routine = engine.generate_adaptive_routine(
        skin_analysis={"skin_type": "normal", "problems": []},
        lifestyle={}
    )

    has_retinoid = any("Retinol" in item or "Retinaldehyde" in item for item in routine["evening"])
    has_exfoliant = any("AHA" in item or "BHA" in item or "Salicylic" in item or "Glycolic" in item or "Lactic" in item for item in routine["evening"])

    assert not has_retinoid, f"Retinoid should be avoided with high sensitivity: {routine['evening']}"
    assert not has_exfoliant, f"Exfoliant should be avoided with high sensitivity: {routine['evening']}"
    assert "WYSOKA WRAPŁIWOŚĆ" in routine["notes"]


def test_sensitivity_medium_reduces_frequency():
    """Test medium sensitivity reduces retinoid frequency."""
    engine = SkincareEngine()
    engine.reaction_tracker.get_overall_sensitivity = lambda: "medium"
    engine.reaction_tracker.get_tolerance_level = lambda x: "medium" if "Retinol" in x else "none"

    routine = engine.generate_adaptive_routine(
        skin_analysis={"skin_type": "normal", "problems": []},
        lifestyle={}
    )

    # Should have retinoid but with reduced frequency note
    retinoid_items = [item for item in routine["evening"] if "Retinol" in item or "Retinaldehyde" in item]
    assert len(retinoid_items) > 0
    # Check adaptations mention reduced frequency
    assert any("1x_2weeks" in str(a) or "2x_week" in str(a) for a in routine["adaptations"])


def test_ingredient_conflicts_retinoid_exfoliant():
    """Test conflict detection: retinoid + exfoliant."""
    engine = SkincareEngine()
    routine = {
        "morning": ["Gentle Cleanser", "Vitamin C 10-20%", "SPF 30+"],
        "evening": ["Gentle Cleanser", "Retinol 0.25-1%", "AHA (Glycolic Acid)", "Ceramide Moisturizer"]
    }
    conflicts = engine.check_ingredient_conflicts(routine)

    retinoid_exfoliant_conflicts = [c for c in conflicts if c["type"] == "irritation_risk"]
    assert len(retinoid_exfoliant_conflicts) > 0
    assert retinoid_exfoliant_conflicts[0]["severity"] == "high"


def test_ingredient_conflicts_vit_c_exfoliant():
    """Test conflict detection: Vitamin C + exfoliant."""
    engine = SkincareEngine()
    routine = {
        "morning": ["Gentle Cleanser", "Vitamin C 10-20%", "AHA (Glycolic Acid)", "SPF 30+"],
        "evening": ["Gentle Cleanser", "Ceramide Moisturizer"]
    }
    conflicts = engine.check_ingredient_conflicts(routine)

    ph_conflicts = [c for c in conflicts if c["type"] == "ph_conflict"]
    assert len(ph_conflicts) > 0
    assert ph_conflicts[0]["severity"] == "medium"


def test_evidence_summary():
    """Test evidence summary generation."""
    engine = SkincareEngine()
    routine = {
        "morning": ["Gentle Cleanser", "Vitamin C 10-20%", "SPF 30+"],
        "evening": ["Gentle Cleanser", "Retinol 0.25-1%", "Ceramide Moisturizer"]
    }
    summary = engine.get_evidence_summary(routine)

    assert "RCT" in summary
    assert summary["RCT"] >= 2  # Vitamin C, Retinol, SPF all have RCT evidence
    assert len(summary["ingredients"]) >= 3


def test_tolerance_tracker():
    """Test SkinReactionTracker tolerance level determination."""
    tracker = SkinReactionTracker()

    # No history = none
    assert tracker.get_tolerance_level("Retinol 0.25-1%") == "none"
    assert tracker.get_overall_sensitivity() == "none"

    # Test with mocked history
    tracker.get_reaction_history = lambda days: [
        {"ingredient": "Retinol 0.25-1%", "severity": "high"},
        {"ingredient": "Retinol 0.25-1%", "severity": "high"},
    ]
    assert tracker.get_tolerance_level("Retinol 0.25-1%") == "high"

    # Medium tolerance
    tracker.get_reaction_history = lambda days: [
        {"ingredient": "Retinol 0.25-1%", "severity": "medium"},
        {"ingredient": "Retinol 0.25-1%", "severity": "medium"},
        {"ingredient": "Retinol 0.25-1%", "severity": "medium"},
    ]
    assert tracker.get_tolerance_level("Retinol 0.25-1%") == "medium"

    # Low tolerance
    tracker.get_reaction_history = lambda days: [
        {"ingredient": "Retinol 0.25-1%", "severity": "medium"},
    ]
    assert tracker.get_tolerance_level("Retinol 0.25-1%") == "low"


def test_overall_sensitivity():
    """Test overall sensitivity calculation."""
    tracker = SkinReactionTracker()

    # No history
    assert tracker.get_overall_sensitivity() == "none"

    # High sensitivity
    tracker.get_reaction_history = lambda days: [
        {"severity": "high"}, {"severity": "high"}, {"severity": "high"}
    ] + [{"severity": "low"} for _ in range(7)]
    assert tracker.get_overall_sensitivity() == "high"

    # Medium sensitivity
    tracker.get_reaction_history = lambda days: [
        {"severity": "high"}, {"severity": "medium"}, {"severity": "medium"}, {"severity": "medium"}, {"severity": "medium"}
    ]
    assert tracker.get_overall_sensitivity() == "medium"

    # Low sensitivity
    tracker.get_reaction_history = lambda days: [
        {"severity": "low"}, {"severity": "low"}
    ]
    assert tracker.get_overall_sensitivity() == "low"


def test_rotation_manager_should_rotate():
    """Test rotation manager cycle detection."""
    manager = IngredientRotationManager()

    # No history = don't rotate
    assert manager.should_rotate("Retinol 0.25-1%", "retinoid") == (False, "no_history")

    # Within cycle = don't rotate
    manager.get_ingredient_history = lambda ing, days: [
        {"date": "2026-08-01T00:00:00"}  # ~4 weeks ago, cycle is 12 weeks
    ]
    assert manager.should_rotate("Retinol 0.25-1%", "retinoid") == (False, "within_cycle")

    # Cycle complete = rotate
    manager.get_ingredient_history = lambda ing, days: [
        {"date": "2026-01-01T00:00:00"}  # ~34 weeks ago, cycle is 12 weeks
    ]
    assert manager.should_rotate("Retinol 0.25-1%", "retinoid") == (True, "cycle_complete")


def test_rotation_recommendations():
    """Test rotation recommendations for current routine."""
    manager = IngredientRotationManager()

    # Mock history for retinoid (cycle complete)
    manager.get_ingredient_history = lambda ing, days: [
        {"date": "2026-01-01T00:00:00"}
    ] if "Retinol" in ing else []

    current_routine = {
        "morning": ["Gentle Cleanser", "Vitamin C 10-20%", "SPF 30+"],
        "evening": ["Gentle Cleanser", "Retinol 0.25-1%", "Ceramide Moisturizer"]
    }

    recs = manager.get_rotation_recommendations(current_routine)
    assert len(recs) > 0
    assert any(r["ingredient"] == "Retinol 0.25-1%" for r in recs)
    assert any(r["reason"] == "cycle_complete" for r in recs)


def test_select_retinoid():
    """Test retinoid selection logic."""
    engine = SkincareEngine()

    # No sensitivity - should pick retinol with standard freq
    retinoid, freq = engine._select_retinoid("none")
    assert retinoid == "Retinol 0.25-1%"
    assert freq == "1x_week"

    # High sensitivity - should avoid
    engine.reaction_tracker.get_tolerance_level = lambda x: "high"
    retinoid, freq = engine._select_retinoid("high")
    assert retinoid is None
    assert freq == "avoid"

    # Medium sensitivity
    engine.reaction_tracker.get_tolerance_level = lambda x: "medium" if "Retinol" in x else "none"
    retinoid, freq = engine._select_retinoid("medium")
    assert retinoid in ["Retinol 0.25-1%", "Retinaldehyde"]
    assert freq == "1x_2weeks"


def test_skincare_ingredients_have_required_fields():
    """Test all skincare ingredients have required fields."""
    for ingredient in SKINCARE_INGREDIENTS:
        assert "name" in ingredient
        assert "type" in ingredient
        assert "frequency" in ingredient
        assert "rotatable" in ingredient
        assert "irritation_risk" in ingredient


def test_tolerance_levels_complete():
    """Test tolerance levels have all required configs."""
    for level, config in TOLERANCE_LEVELS.items():
        assert "retinoid_start_freq" in config
        assert "exfoliant_start_freq" in config
        assert "max_retinoid_freq" in config
        assert "max_exfoliant_freq" in config


def test_rotation_schedule_complete():
    """Test rotation schedule has all categories."""
    expected_categories = ["retinoid", "exfoliant", "vitamin_c", "niacinamide", "peptide"]
    for cat in expected_categories:
        assert cat in ROTATION_SCHEDULE
        assert "cycle_weeks" in ROTATION_SCHEDULE[cat]
        assert "min_rest_weeks" in ROTATION_SCHEDULE[cat]
        assert "max_concurrent" in ROTATION_SCHEDULE[cat]