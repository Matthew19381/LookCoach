from fastapi import APIRouter
from ..services.nutrition_looks import NutritionLooksEngine

router = APIRouter()

@router.get("/factors")
async def get_factors():
    """List all nutrition factors affecting looks."""
    return NutritionLooksEngine.FACTORS

@router.get("/recommendations")
async def get_recommendations():
    """Get nutrition recommendations."""
    return NutritionLooksEngine.get_recommendations()

# /meal-plan and /analyze removed 2026-11-02 (LC-4, D3): meal plans and the food
# log belong to Dieta. LookCoach sends needs (sodium limit, low glycemic load) to
# Dieta via the hub - GET/POST /ecosystem/needs. The /analyze form was also
# broken (sent water/sugar/veg, read water_liters/sodium_mg).
