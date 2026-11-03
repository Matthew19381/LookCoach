from fastapi import APIRouter
from pydantic import BaseModel
from ..services.aesthetic_training import AestheticTrainingEngine

router = APIRouter()

class PhysiqueAnalysisRequest(BaseModel):
    analysis: dict

# /plans and /plan removed 2026-11-02 (LC-4): LookCoach does not write training
# plans - it sends the muscle priorities to ForgeBody (GET/POST /ecosystem/needs).

@router.get("/exercises")
async def get_exercises():
    """List all available exercises."""
    return AestheticTrainingEngine.EXERCISES

@router.post("/analyze")
async def analyze_physique(body: PhysiqueAnalysisRequest):
    """Analyze physique and recommend training focus."""
    result = AestheticTrainingEngine.analyze_physique(body.analysis)
    return result
