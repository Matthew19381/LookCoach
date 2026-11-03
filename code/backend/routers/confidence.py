from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.analysis_store import has_any, load_latest_analysis
from ..services.confidence_presence import ConfidencePresenceEngine

router = APIRouter()


@router.get("/analyze")
async def analyze_confidence(user_id: int = 1, db: Session = Depends(get_db)):
    """Posture/facial indicators from the user's latest analysis.

    Until 2026-11-02 this analysed a hard-coded `dummy_analysis`, so everyone
    saw the same "medium tension" result."""
    latest = load_latest_analysis(db, user_id)
    if not has_any(latest):
        return {
            "has_analysis": False,
            "message": "Brak analizy zdjęć — zrób zdjęcia przód i bok, żeby zobaczyć wskazówki.",
            "posture": None,
            "facial": None,
        }
    return {
        "has_analysis": True,
        "posture": ConfidencePresenceEngine.analyze_posture_indicators(latest),
        "facial": ConfidencePresenceEngine.analyze_facial_expressions(latest),
    }


@router.get("/action-plan")
async def get_action_plan():
    return {
        "plan": ConfidencePresenceEngine.get_confidence_action_plan(),
    }

# /attractiveness-impact removed 2026-11-02: it claimed confidence raises
# attractiveness "by up to 20%" with no source (LC-1) and returned a percentage
# of attractiveness (LC-9).
