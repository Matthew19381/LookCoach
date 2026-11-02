from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.photo import Photo
from ..paths import photo_url

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
async def compare_photos(body: CompareRequest, db: Session = Depends(get_db)):
    before = db.query(Photo).filter(Photo.id == body.photo_before_id).first()
    after = db.query(Photo).filter(Photo.id == body.photo_after_id).first()

    if not before or not after:
        raise HTTPException(404, "Photos not found")

    return {
        "before": {"id": before.id, "url": photo_url(before.file_path)},
        "after": {"id": after.id, "url": photo_url(after.file_path)},
        "delta_score": 0.0,
    }
