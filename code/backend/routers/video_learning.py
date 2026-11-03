from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.analysis_store import load_latest_analysis
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
    # Until 2026-11-02 this used hard-coded sample data for everyone.
    latest = load_latest_analysis(db, user_id)
    return VideoLearningEngine.get_videos_for_analysis(
        latest["face"] or {}, latest["skin"] or {}, latest["hair"] or {},
    )
