from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.aesthetic_training import AestheticTrainingEngine

router = APIRouter()

class TrainingPlanRequest(BaseModel):
    goal: str = "v_taper"
    fitness_level: str = "beginner"

class PhysiqueAnalysisRequest(BaseModel):
    analysis: dict

@router.get("/plans")
async def get_available_plans():
    """List available training plans."""
    return [
        {"id": k, "name": v["name"], "description": v["description"]}
        for k, v in AestheticTrainingEngine.PLANS.items()
    ]

@router.post("/plan")
async def generate_plan(body: TrainingPlanRequest):
    """Generate training plan based on goal."""
    plan = AestheticTrainingEngine.generate_plan(body.goal, body.fitness_level)
    return plan

@router.get("/exercises")
async def get_exercises():
    """List all available exercises."""
    return AestheticTrainingEngine.EXERCISES

@router.post("/analyze")
async def analyze_physique(body: PhysiqueAnalysisRequest):
    """Analyze physique and recommend training focus."""
    result = AestheticTrainingEngine.analyze_physique(body.analysis)
    return result
