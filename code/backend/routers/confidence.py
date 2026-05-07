from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.confidence_presence import ConfidencePresenceEngine

router = APIRouter()


@router.get("/analyze")
async def analyze_confidence(user_id: int = 1, db: Session = Depends(get_db)):
    # In full version, would fetch user's latest photo analysis
    dummy_analysis = {
        "face": {"muscle_tension": {"level": 40}, "swelling": {"level": 30}},
        "body": {"proportions": {"v_taper": 45}, "asymmetries": []},
    }

    posture = ConfidencePresenceEngine.analyze_posture_indicators(dummy_analysis)
    facial = ConfidencePresenceEngine.analyze_facial_expressions(dummy_analysis)

    return {
        "posture": posture,
        "facial": facial,
        "overall_confidence": (posture["overall_score"] + facial["overall_score"]) / 2,
    }


@router.get("/action-plan")
async def get_action_plan():
    return {
        "plan": ConfidencePresenceEngine.get_confidence_action_plan(),
    }


@router.get("/attractiveness-impact")
async def get_attractiveness_impact(confidence_score: float = 70, presence_score: float = 70):
    return ConfidencePresenceEngine.calculate_attractiveness_impact(confidence_score, presence_score)
