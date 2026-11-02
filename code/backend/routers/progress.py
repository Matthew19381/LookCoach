from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.photo import Photo
from ..models.analysis import Analysis
from ..paths import photo_url
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
