from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.profile import UserProfile

router = APIRouter()


@router.get("/")
async def get_profile(user_id: int = 1, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"goals": {}, "lifestyle": {}, "discipline_score": 50}

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return {"goals": {}, "lifestyle": {}, "discipline_score": 50}

    return {
        "goals": profile.get_goals(),
        "lifestyle": profile.get_lifestyle(),
        "discipline_score": profile.discipline_score,
    }


@router.put("/")
async def update_profile(body: dict, user_id: int = 1, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User()
        db.add(user)
        db.commit()
        db.refresh(user)

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    if "goals" in body:
        profile.set_goals(body["goals"])
    if "lifestyle" in body:
        profile.set_lifestyle(body["lifestyle"])
    if "discipline_score" in body:
        profile.discipline_score = body["discipline_score"]

    db.commit()
    db.refresh(profile)

    return {
        "goals": profile.get_goals(),
        "lifestyle": profile.get_lifestyle(),
        "discipline_score": profile.discipline_score,
    }
