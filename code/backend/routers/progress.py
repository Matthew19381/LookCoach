from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.photo import Photo
from ..models.analysis import Analysis
from ..paths import photo_url
from ..services.correlations import find, stress_from_events
from ..services.ecosystem_client import fetch_recent_events
from ..services.state_labels import compare_labels, state_labels

router = APIRouter()


class CompareRequest(BaseModel):
    photo_before_id: int
    photo_after_id: int


@router.get("/timeline")
async def get_timeline(user_id: int = 1, db: Session = Depends(get_db)):
    photos = (
        db.query(Photo)
        .filter(Photo.user_id == user_id)
        .order_by(Photo.uploaded_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "photo_type": p.photo_type,
            "url": photo_url(p.file_path),
            "uploaded_at": p.uploaded_at.isoformat(),
            "status": p.analysis_status,
        }
        for p in photos
    ]


@router.post("/compare")
async def compare_photos(body: CompareRequest, user_id: int = 1, db: Session = Depends(get_db)):
    """Two photos side by side + qualitative state changes from their analyses.

    No score: until 2026-11-02 this returned `delta_score: 0.0` and the UI drew
    a made-up "Look Score" line (LC-9)."""
    before = db.query(Photo).filter(Photo.id == body.photo_before_id, Photo.user_id == user_id).first()
    after = db.query(Photo).filter(Photo.id == body.photo_after_id, Photo.user_id == user_id).first()

    if not before or not after:
        raise HTTPException(404, "Photos not found")

    def side(photo: Photo) -> dict:
        return {
            "id": photo.id,
            "url": photo_url(photo.file_path),
            "photo_type": photo.photo_type,
            "uploaded_at": photo.uploaded_at.isoformat() if photo.uploaded_at else None,
        }

    def labels(photo: Photo) -> dict:
        analysis = db.query(Analysis).filter(Analysis.photo_id == photo.id).first()
        return state_labels(analysis)

    return {
        "before": side(before),
        "after": side(after),
        "same_type": before.photo_type == after.photo_type,
        "changes": compare_labels(labels(before), labels(after)),
    }


@router.get("/states")
def state_timeline(user_id: int = 1, limit: int = 8, db: Session = Depends(get_db)):
    """Plan 5.1: how the observed state changed, in words (replaces the 'Look Score' line).

    One column per analysed photo (newest last), one row per label."""
    photos = (
        db.query(Photo)
        .filter(Photo.user_id == user_id, Photo.analysis_status == "done")
        .order_by(Photo.uploaded_at.desc(), Photo.id.desc())
        .limit(limit)
        .all()
    )[::-1]
    sessions = []
    for photo in photos:
        analysis = db.query(Analysis).filter(Analysis.photo_id == photo.id).first()
        labels = state_labels(analysis)
        if labels:
            sessions.append({
                "photo_id": photo.id,
                "photo_type": photo.photo_type,
                "date": photo.uploaded_at.isoformat() if photo.uploaded_at else None,
                "labels": labels,
            })
    areas = []
    for session in sessions:
        for area in session["labels"]:
            if area not in areas:
                areas.append(area)
    return {"sessions": sessions, "areas": areas}


@router.get("/correlations")
async def correlations(user_id: int = 1, db: Session = Depends(get_db)):
    """Plan 5.3: what goes together in your data (counts + caveat, no scores)."""
    try:
        stress = stress_from_events(await fetch_recent_events(user_id))
        stress_source = "hub"
    except Exception:  # hub down / no key: local correlations still work
        stress, stress_source = None, "unavailable"
    return {**find(db, user_id, stress), "stress_source": stress_source}
