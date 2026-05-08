from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.nutrition_looks import NutritionLooksEngine

router = APIRouter()

class DietLogRequest(BaseModel):
    diet_log: dict

class MealPlanRequest(BaseModel):
    plan_type: str = "pre_event"

@router.get("/factors")
async def get_factors():
    """List all nutrition factors affecting looks."""
    return NutritionLooksEngine.FACTORS

@router.get("/recommendations")
async def get_recommendations():
    """Get nutrition recommendations."""
    return NutritionLooksEngine.get_recommendations()

@router.get("/meal-plan/{plan_type}")
async def get_meal_plan(plan_type: str = "pre_event"):
    """Get meal timing plan for looks."""
    return NutritionLooksEngine.get_meal_plan(plan_type)

@router.post("/analyze")
async def analyze_diet(body: DietLogRequest):
    """Analyze diet and recommend improvements."""
    return NutritionLooksEngine.analyze_diet(body.diet_log)
