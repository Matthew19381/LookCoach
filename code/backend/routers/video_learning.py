from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.video_learning import VideoLearningEngine

router = APIRouter()


@router.get("/videos")
async def get_all_videos(technique: str = None, query: str = None):
    if technique:
        return VideoLearningEngine.get_videos_for_technique(technique)
    if query:
        return VideoLearningEngine.search_videos(query)
    return VideoLearningEngine.get_videos_for_analysis({}, {}, {})


@router.get("/videos/recommended")
async def get_recommended_videos(user_id: int = 1, db: Session = Depends(get_db)):
    # In full version, would fetch user's latest analysis
    return VideoLearningEngine.get_videos_for_analysis(
        {"overall_face_score": 60},
        {"overall_skin_score": 55},
        {"density": 50}
    )
