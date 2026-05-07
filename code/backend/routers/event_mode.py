from fastapi import APIRouter, Depends
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()


class EventPlanRequest(BaseModel):
    event_date: str  # YYYY-MM-DD
    event_type: str = "general"  # party, photoshoot, date, wedding


@router.post("/plan")
async def generate_event_plan(body: EventPlanRequest, user_id: int = 1, db: Session = Depends(get_db)):
    from ..services.event_mode import EventModeEngine

    if body.days_until_event < 0:
        raise HTTPException(400, "Event date must be in the future")

    # In full version, would fetch user's latest analysis
    current_analysis = {}

    plan = EventModeEngine.generate_event_plan(
        body.event_date, body.event_type, current_analysis
    )

    if "error" in plan:
        raise HTTPException(400, plan["error"])

    return plan


@router.get("/tips/{event_type}")
async def get_event_tips(event_type: str):
    from ..services.event_mode import EventModeEngine
    plan = EventModeEngine.generate_event_plan("2026-01-01", event_type, {})
    return {
        "event_type": event_type,
        "tips": plan.get("tips", []),
    }
