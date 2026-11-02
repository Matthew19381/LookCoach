"""Profile: goals (plan 4.12), health flags for the Health Safety Layer (LC-8), mode.

Until 2026-11-02 there was no UI for any of it - the health flags that block
retinol in pregnancy or minoxidil with heart disease could not be set - and
PUT created `User()` with the next free id instead of `user_id`.
"""
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile import UserProfile
from ..models.user import User
from ..services.health_safety import CONTRAINDICATION_FLAGS

router = APIRouter()

FocusArea = Literal["skin", "hair", "face", "body", "posture", "style"]


class Goals(BaseModel):
    focus: list[FocusArea] = Field(default_factory=list, description="What the user wants to improve")
    deadline: str | None = Field(None, description="YYYY-MM-DD, e.g. an event")
    minutes_per_day: int | None = Field(None, ge=0, le=180)
    styling_minutes: int | None = Field(None, ge=0, le=60, description="Time for hair styling (plan 4.2)")
    constraints: str | None = Field(None, max_length=500, description="Work/sport constraints for style advice")


class Health(BaseModel):
    pregnancy: bool = False
    heart_disease: bool = False
    kidney_disease: bool = False
    back_injury: bool = False
    shoulder_injury: bool = False
    knee_injury: bool = False
    sensitive_skin: bool = False


class ProfileUpdate(BaseModel):
    goals: Goals | None = None
    health: Health | None = None
    lifestyle: dict | None = None
    mode: Literal["free", "maintenance", "improvement"] | None = None
    discipline_score: int | None = Field(None, ge=0, le=100)


def _out(profile: UserProfile | None) -> dict:
    if not profile:
        return {"goals": Goals().model_dump(), "health": Health().model_dump(), "lifestyle": {},
                "mode": "free", "discipline_score": 50}
    return {
        "goals": {**Goals().model_dump(), **profile.get_goals()},
        "health": {**Health().model_dump(), **profile.get_health()},
        "lifestyle": profile.get_lifestyle(),
        "mode": profile.mode or "free",
        "discipline_score": profile.discipline_score,
    }


@router.get("/")
async def get_profile(user_id: int = 1, db: Session = Depends(get_db)):
    return _out(db.query(UserProfile).filter(UserProfile.user_id == user_id).first())


@router.put("/")
async def update_profile(body: ProfileUpdate, user_id: int = 1, db: Session = Depends(get_db)):
    if not db.get(User, user_id):
        db.add(User(id=user_id))
        db.flush()
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)

    if body.goals is not None:
        profile.set_goals(body.goals.model_dump())
    if body.health is not None:
        profile.set_health(body.health.model_dump())
    if body.lifestyle is not None:
        profile.set_lifestyle(body.lifestyle)
    if body.mode is not None:
        profile.mode = body.mode
    if body.discipline_score is not None:
        profile.discipline_score = body.discipline_score

    db.commit()
    db.refresh(profile)
    return _out(profile)


assert set(Health.model_fields) == set(CONTRAINDICATION_FLAGS), "Health flags must match LC-8 flags"
