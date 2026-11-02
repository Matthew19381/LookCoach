from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.analysis_store import load_latest_analysis
from ..services.posture_correction import PostureCorrectionEngine

router = APIRouter()

class BodyAnalysisRequest(BaseModel):
    analysis: dict

@router.get("/issues")
async def list_issues():
    """List all posture issues."""
    return [
        {"id": k, **v}
        for k, v in PostureCorrectionEngine.POSTURE_ISSUES.items()
    ]

@router.post("/detect")
async def detect_issues(body: BodyAnalysisRequest):
    """Detect posture issues from body analysis."""
    issues = PostureCorrectionEngine.detect_issues(body.analysis)
    return {"issues": issues, "count": len(issues)}

@router.get("/correction/{issue_id}")
async def get_correction(issue_id: str):
    """Get correction plan for an issue."""
    result = PostureCorrectionEngine.get_correction_plan(issue_id)
    if "error" in result:
        from fastapi import HTTPException
        raise HTTPException(404, result["error"])
    return result

@router.post("/assess")
async def full_assessment(body: BodyAnalysisRequest):
    """Full posture assessment with correction plan."""
    result = PostureCorrectionEngine.full_assessment(body.analysis)
    return result


@router.get("/assessment")
async def assessment_from_latest(user_id: int = 1, db: Session = Depends(get_db)):
    """Posture assessment from the user's latest side photo analysis.

    The page used to POST a hard-coded `mockAnalysis` (forward head + shoulders)
    so everyone got the same two issues (fixed 2026-11-02)."""
    body = load_latest_analysis(db, user_id)["body"]
    if not body:
        return {
            "has_analysis": False,
            "message": "Brak analizy zdjęcia z boku — zrób je, żeby ocenić postawę.",
        }
    return {"has_analysis": True, **PostureCorrectionEngine.full_assessment(body)}
