from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.photo import Photo
from ..models.progress import ProgressLog

router = APIRouter()


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
            "url": f"/uploads/{Path(p.file_path).name}",
            "uploaded_at": p.uploaded_at.isoformat(),
            "status": p.analysis_status,
        }
        for p in photos
    ]


@router.post("/compare")
async def compare_photos(body: dict, db: Session = Depends(get_db)):
    photo_before_id = body.get("photo_before_id")
    photo_after_id = body.get("photo_after_id")

    if not photo_before_id or not photo_after_id:
        return {"error": "Missing photo IDs"}

    before = db.query(Photo).filter(Photo.id == photo_before_id).first()
    after = db.query(Photo).filter(Photo.id == photo_after_id).first()

    if not before or not after:
        return {"error": "Photos not found"}

    return {
        "before": {"id": before.id, "url": f"/uploads/{Path(before.file_path).name}"},
        "after": {"id": after.id, "url": f"/uploads/{Path(after.file_path).name}"},
        "delta_score": 0.0,
    }
