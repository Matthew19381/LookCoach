from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.evidence_engine import EvidenceEngine
from ..services.roi_engine import ROIEngine

router = APIRouter()


@router.get("/")
async def get_recommendations(limit: int = 10, user_id: int = 1, db: Session = Depends(get_db)):
    # Simplified - in full version would fetch user analysis
    user_analysis = {"face": {}, "body": {}, "skin": {}, "hair": {}}
    user_profile = {}

    recs = EvidenceEngine.get_recommendations(user_analysis, user_profile)
    recs = ROIEngine.rank_recommendations(recs)

    return recs[:limit]
