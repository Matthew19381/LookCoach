from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.skincare_engine import SkincareEngine

router = APIRouter()

SKINCARE_ENGINE = SkincareEngine()


@router.get("/routine")
async def get_skincare_routine(user_id: int = 1, db: Session = Depends(get_db)):
    # Simplified - in full version would fetch user analysis
    skin_analysis = {"skin_type": "combination", "problems": []}
    lifestyle = {"sleep": 7, "stress": 5}

    routine = SKINCARE_ENGINE.generate_routine(skin_analysis, lifestyle)
    return routine
