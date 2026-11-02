from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directive_state import DirectiveState
from ..models.profile import UserProfile
from ..services.analysis_store import has_any, load_latest_analysis
from ..services.attractiveness_levers import AttractivenessLevers
from ..services.evidence_engine import EvidenceEngine
from ..services.roi_engine import ROIEngine
from ..services.health_safety import apply_safety_filter

router = APIRouter()


@router.get("/")
async def get_recommendations(limit: int = 10, user_id: int = 1, db: Session = Depends(get_db)):
    # Until 2026-11-02 this was an always-empty analysis, so every user got the
    # same default categories regardless of their photos.
    latest = load_latest_analysis(db, user_id)
    user_analysis = {s: latest[s] or {} for s in ("face", "body", "skin", "hair")}
    if has_any(latest):
        user_analysis["lever"] = AttractivenessLevers.detect_lever(
            user_analysis["face"], user_analysis["body"], user_analysis["skin"], user_analysis["hair"],
        )

    directives = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()
    if directives and directives.priority:
        user_analysis["hub_priority"] = directives.priority

    profile_row = (
        db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    )
    user_profile = {"health": profile_row.get_health() if profile_row else {}}
    user_mode = profile_row.mode if profile_row else "free"

    recs = EvidenceEngine.get_recommendations(user_analysis, user_profile)
    recs = ROIEngine.rank_recommendations(recs, user_mode)
    recs = apply_safety_filter(recs, user_profile)

    return recs[:limit]
