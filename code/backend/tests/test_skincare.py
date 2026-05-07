from services.skincare_engine import SkincareEngine

def test_skincare_routine_basic():
    routine = SkincareEngine.generate_routine({"skin_type": "dry"}, {"sleep": 7})
    assert "morning" in routine
    assert "evening" in routine
    assert len(routine["morning"]) > 0
    assert len(routine["evening"]) > 0
    assert routine["skin_type"] == "dry"

def test_skincare_routine_morning_has_spf():
    routine = SkincareEngine.generate_routine({"skin_type": "combination"}, {})
    assert "SPF 30+" in routine["morning"]

def test_skincare_routine_evening_acne():
    routine = SkincareEngine.generate_routine(
        {'skin_type': 'oily', 'problems': [{'issue': 'acne'}, {'issue': 'breakouts'}]},
        {}
    )
    # Should include BHA for acne in evening
    bha_items = [item for item in routine["evening"] if "BHA" in item or "Salicylic" in item]
    assert len(bha_items) > 0, f"BHA not found in evening: {routine['evening']}"
    # Zinc PCA should be in evening for acne
    zinc_items = [item for item in routine["evening"] if "Zinc" in item]
    assert len(zinc_items) > 0, f"Zinc not found in evening: {routine['evening']}"

def test_skincare_routine_evening_aging():
    routine = SkincareEngine.generate_routine(
        {"skin_type": "dry", "problems": []},
        {}
    )
    # Should include Retinol for aging
    assert any("Retinol" in item for item in routine["evening"])

def test_skincare_routine_dry_skin():
    routine = SkincareEngine.generate_routine(
        {"skin_type": "dry"},
        {}
    )
    # Should include hydrating ingredients
    assert "Hyaluronic Acid" in routine["morning"]
    assert "Ceramide Moisturizer" in routine["evening"]
    assert "Squalane Oil" in routine["evening"]

def test_skincare_routine_notes():
    routine = SkincareEngine.generate_routine({}, {})
    assert "notes" in routine
    assert "rotate" in routine["notes"].lower() or "rotation" in routine["notes"].lower()
