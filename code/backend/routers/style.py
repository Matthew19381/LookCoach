"""Plan 4.1-4.8: hair, brows, beard, eye area, glasses, clothing, colours."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.profile import UserProfile
from ..services.analysis_store import load_latest_analysis
from ..services.style_advisor import style_advice

router = APIRouter()


@router.get("")
def get_style_advice(user_id: int = 1, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    goals = profile.get_goals() if profile else {}
    health = profile.get_health() if profile else {}
    return style_advice(load_latest_analysis(db, user_id), goals, health)
