"""Plan 4.1-4.8: hair, brows, beard, eye area, glasses, clothing, colours."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile import UserProfile
from ..services.analysis_store import load_latest_analysis
from ..services.style_advisor import style_advice
from ..services.style_preview import BEARD_OPTIONS, PreviewError, generate_preview

router = APIRouter()


@router.get("")
def get_style_advice(user_id: int = 1, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    goals = profile.get_goals() if profile else {}
    health = profile.get_health() if profile else {}
    return style_advice(load_latest_analysis(db, user_id), goals, health)


class PreviewRequest(BaseModel):
    kind: Literal["hair", "beard"]
    option: str


@router.get("/preview/options")
def preview_options(user_id: int = 1, db: Session = Depends(get_db)):
    """What can be previewed: the current hairstyle proposals + fixed beard forms."""
    return {"hair": list(_hair_options(db, user_id)), "beard": list(BEARD_OPTIONS)}


@router.post("/preview")
def preview(body: PreviewRequest, user_id: int = 1, db: Session = Depends(get_db)):
    """Plan 4.13 (D8): optional, paid, limited; the image is not stored."""
    allowed = _hair_options(db, user_id) if body.kind == "hair" else BEARD_OPTIONS
    try:
        return generate_preview(db, user_id, body.kind, body.option, allowed)
    except PreviewError as e:
        raise HTTPException(e.status, e.message) from e


def _hair_options(db: Session, user_id: int) -> dict[str, str]:
    advice = get_style_advice(user_id, db)
    hair = advice.get("hair") or {}
    return {p["name"]: f"{p['name']} - {p['tell_barber']}" for p in hair.get("proposals", [])}
