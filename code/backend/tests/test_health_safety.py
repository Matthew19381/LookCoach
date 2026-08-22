"""Health Safety Layer tests (NEURO_PLAN F-3 / LC-8).

Covers hard contraindication blocks and high-risk disclaimers across
at least 3 contraindication scenarios.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.parent
CODE_DIR = BACKEND_DIR.parent
sys.path.insert(0, str(CODE_DIR))

from backend.services.health_safety import (
    apply_high_risk_disclaimer,
    apply_safety_filter,
    check_contraindications,
)
from backend.services.evidence_engine import EVIDENCE_DB


def _entry(eid):
    return next(e for e in EVIDENCE_DB if e["id"] == eid)


class TestCheckContraindications:
    def test_pregnancy_blocks_retinol(self):
        warnings = check_contraindications("skincare_002", {"health": {"pregnancy": True}})
        assert len(warnings) == 1
        assert "pregnancy" in warnings[0]

    def test_heart_disease_blocks_minoxidil(self):
        warnings = check_contraindications("hair_001", {"health": {"heart_disease": True}})
        assert warnings

    def test_kidney_disease_blocks_high_protein_and_water_targets(self):
        assert check_contraindications("nutrition_001", {"health": {"kidney_disease": True}})
        assert check_contraindications("nutrition_003", {"health": {"kidney_disease": True}})

    def test_shoulder_injury_blocks_face_pulls_and_overhead_press(self):
        profile = {"health": {"shoulder_injury": True}}
        assert check_contraindications("posture_002", profile)
        assert check_contraindications("training_004", profile)

    def test_healthy_profile_no_warnings(self):
        assert check_contraindications("skincare_002", {"health": {}}) == []
        assert check_contraindications("hair_001", {"health": {"pregnancy": False}}) == []

    def test_unknown_recommendation_returns_empty(self):
        assert check_contraindications("no_such_id", {"health": {"pregnancy": True}}) == []


class TestHighRiskDisclaimers:
    def test_retinol_has_disclaimer_even_for_healthy_users(self):
        assert "dermatologist" in apply_high_risk_disclaimer("skincare_002")

    def test_minoxidil_has_doctor_disclaimer(self):
        assert apply_high_risk_disclaimer("hair_001")

    def test_low_risk_item_has_no_disclaimer(self):
        assert apply_high_risk_disclaimer("sleep_001") is None


class TestApplySafetyFilter:
    RECS = [
        _entry("skincare_002"),  # retinol: pregnancy contra + disclaimer
        _entry("hair_001"),      # minoxidil: heart disease contra + disclaimer
        _entry("nutrition_001"), # high protein: kidney contra
        _entry("sleep_001"),     # safe, no disclaimer
    ]

    def test_pregnant_user_never_receives_retinol_unwarned_or_at_all(self):
        out = apply_safety_filter(self.RECS, {"health": {"pregnancy": True}})
        ids = [r["id"] for r in out]
        assert "skincare_002" not in ids  # hard-blocked entirely
        assert "sleep_001" in ids

    def test_all_contraindicated_items_dropped(self):
        profile = {"health": {"heart_disease": True, "kidney_disease": True}}
        out = apply_safety_filter(self.RECS, profile)
        ids = [r["id"] for r in out]
        assert "hair_001" not in ids
        assert "nutrition_001" not in ids
        assert "skincare_002" in ids  # no personal contra -> kept with disclaimer
        retinol = next(r for r in out if r["id"] == "skincare_002")
        assert any("dermatologist" in w for w in retinol["warnings"])

    def test_healthy_user_gets_everything_with_disclaimers_where_needed(self):
        out = apply_safety_filter(self.RECS, {"health": {}})
        assert len(out) == len(self.RECS)
        by_id = {r["id"]: r for r in out}
        assert by_id["skincare_002"]["warnings"]
        assert "warnings" not in by_id["sleep_001"]
