from fastapi import APIRouter, Depends
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.profile import UserProfile

router = APIRouter()

# LC-5 / NEURO_PLAN: the event protocol is a bundle of plausible habits, not a
# tested intervention - it must say so (CLAUDE.md claimed it did; until
# 2026-11-02 neither backend nor UI marked it).
HYPOTHESIS = {
    "evidence_level": "hipoteza",
    "disclaimer": (
        "Protokół przed wydarzeniem to HIPOTEZA: zestaw rozsądnych nawyków, nie "
        "przebadana interwencja. Efekty krótkoterminowe są niepewne i indywidualne. "
        "Nie testuj nowych kosmetyków tuż przed wydarzeniem."
    ),
}

# LC-8: water/sodium targets are a contraindication with kidney disease.
_KIDNEY_UNSAFE = ("water", "sodium", "hydrated")


def _apply_health(plan: dict, health: dict) -> dict:
    if not health.get("kidney_disease"):
        return plan
    def keep(action: str) -> bool:
        return not any(word in action.lower() for word in _KIDNEY_UNSAFE)
    plan["timeline"] = [
        {**day, "actions": [a for a in day["actions"] if keep(a)]} for day in plan.get("timeline", [])
    ]
    plan["emergency_day_of"] = [a for a in plan.get("emergency_day_of", []) if keep(a)]
    plan.setdefault("warnings", []).append(
        "Choroba nerek: usunięto zalecenia dot. ilości wody i sodu — ustal je z lekarzem."
    )
    return plan


class EventPlanRequest(BaseModel):
    event_date: str  # YYYY-MM-DD
    event_type: str = "general"  # party, photoshoot, date, wedding


@router.post("/plan")
async def generate_event_plan(body: EventPlanRequest, user_id: int = 1, db: Session = Depends(get_db)):
    from ..services.event_mode import EventModeEngine
    from datetime import datetime

    # Calculate days until event
    from datetime import date
    event_date = datetime.strptime(body.event_date, "%Y-%m-%d").date()
    days_until = (event_date - date.today()).days

    if days_until < 0:
        raise HTTPException(400, "Event date must be in the future")

    plan = EventModeEngine.generate_event_plan(body.event_date, body.event_type, {})

    if "error" in plan:
        raise HTTPException(400, plan["error"])

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    plan = _apply_health(plan, profile.get_health() if profile else {})
    return {**plan, **HYPOTHESIS}


@router.get("/tips/{event_type}")
async def get_event_tips(event_type: str):
    from ..services.event_mode import EventModeEngine
    plan = EventModeEngine.generate_event_plan("2026-01-01", event_type, {})
    return {
        "event_type": event_type,
        "tips": plan.get("tips", []),
        **HYPOTHESIS,
    }
