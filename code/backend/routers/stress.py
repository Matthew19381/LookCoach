from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.stress_engine import StressEngine

router = APIRouter()

class StressDataRequest(BaseModel):
    stress_data: dict

@router.get("/effects")
async def get_effects():
    """List all stress effects on looks."""
    return StressEngine.STRESS_EFFECTS

@router.get("/techniques")
async def get_techniques():
    """Get relaxation techniques for looks."""
    return StressEngine.get_techniques()

@router.post("/analyze")
async def analyze_stress(body: StressDataRequest):
    """Analyze stress and recommend relaxation for looks."""
    return StressEngine.analyze_stress(body.stress_data)
