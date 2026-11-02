"""What the assistant knows about the user (plan 8.1). Text and labels only - never photos."""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..models.directive_state import DirectiveState
from ..models.experiment import Experiment
from ..models.profile import UserProfile
from .analysis_store import has_any, load_latest_analysis
from .attractiveness_levers import AttractivenessLevers
from .consistency_tracker import ConsistencyTracker
from .ecosystem_client import cached_overview
from .evidence_engine import EvidenceEngine
from .health_safety import apply_safety_filter
from .roi_engine import ROIEngine
from .wellbeing_guard import assess


def _labels(section: dict | None, keys: tuple[str, ...]) -> dict:
    section = section or {}
    out = {}
    for key in keys:
        value = section.get(key)
        if value not in (None, "", [], {}):
            out[key] = value
    return out


def build_context(db: Session, user_id: int) -> dict:
    latest = load_latest_analysis(db, user_id)
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    goals = profile.get_goals() if profile else {}
    health = profile.get_health() if profile else {}
    directives = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()

    analysis = {s: latest[s] or {} for s in ("face", "body", "skin", "hair")}
    lever = AttractivenessLevers.detect_lever(*analysis.values()) if has_any(latest) else None
    recs = EvidenceEngine.get_recommendations({**analysis, "lever": lever, "goal_focus": goals.get("focus", [])},
                                              {"health": health})
    recs = apply_safety_filter(ROIEngine.rank_recommendations(recs, profile.mode if profile else "free"),
                               {"health": health})[:6]

    try:
        adherence = {
            k: {"level": v["adherence_level"], "recommended_difficulty": v["recommended_difficulty"]}
            for k, v in ConsistencyTracker(db, user_id).get_all_protocols_status().items()
        }
    except Exception:  # tracker problems must not break the chat
        adherence = {}

    since = datetime.now() - timedelta(days=60)
    experiments = [
        {"name": e.name or e.template_id, "status": e.status}
        for e in db.query(Experiment).filter(Experiment.user_id == user_id, Experiment.created_at >= since).all()
    ]

    return {
        "analysis": {
            "photos_analyzed": latest["photos_analyzed"],
            "face": _labels(analysis["face"], ("swelling", "skin_quality", "face_shape", "brows", "beard", "eye_area")),
            "skin": _labels(analysis["skin"], ("skin_type", "problems", "hydration_status")),
            "hair": _labels(analysis["hair"], ("hairline_status", "density_status", "hair_type", "crown_density")),
            "body": _labels(analysis["body"], ("posture", "missing_muscles", "proportions")),
        },
        "main_focus": lever,
        "recommendations": [
            {"id": r["id"], "name": r["name"], "evidence_level": r.get("evidence_level"),
             "warnings": r.get("warnings", [])}
            for r in recs
        ],
        "goals": goals,
        "health_flags": [k for k, v in health.items() if v],
        "routine_adherence": adherence,
        "experiments_last_60_days": experiments,
        "hub_directives": {
            "survival_mode": bool(directives and directives.survival_mode),
            "priority": directives.priority if directives else None,
        },
        "other_modules": cached_overview(db, user_id),
        "photo_checking": assess(db, user_id)["level"],
    }
