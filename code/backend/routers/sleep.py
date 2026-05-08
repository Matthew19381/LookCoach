from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.sleep_engine import SleepEngine

router = APIRouter()

class SleepDataRequest(BaseModel):
    sleep_data: dict

class EventSleepRequest(BaseModel):
    event_type: str = "general"

@router.get("/factors")
async def get_factors():
    """List all sleep factors affecting looks."""
    return SleepEngine.SLEEP_FACTORS

@router.post("/analyze")
async def analyze_sleep(body: SleepDataRequest):
    """Analyze sleep and recommend improvements."""
    return SleepEngine.analyze_sleep(body.sleep_data)

@router.get("/pre-event/{event_type}")
async def get_pre_event_tips(event_type: str = "general"):
    """Get sleep tips for specific event type."""
    return SleepEngine.get_pre_event_tips(event_type)
