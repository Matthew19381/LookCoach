from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile import UserProfile
from ..services.evidence_engine import EvidenceEngine
from ..services.roi_engine import ROIEngine
from ..services.health_safety import apply_safety_filter

router = APIRouter()


@router.get("/")
async def get_recommendations(limit: int = 10, user_id: int = 1, db: Session = Depends(get_db)):
    # Simplified - in full version would fetch user analysis
    user_analysis = {"face": {}, "body": {}, "skin": {}, "hair": {}}

    profile_row = (
        db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    )
    user_profile = {"health": profile_row.get_health() if profile_row else {}}

    recs = EvidenceEngine.get_recommendations(user_analysis, user_profile)
    recs = ROIEngine.rank_recommendations(recs)
    recs = apply_safety_filter(recs, user_profile)

    return recs[:limit]
