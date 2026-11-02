import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.photo import Photo
from ..paths import UPLOAD_DIR, photo_path, photo_url
from ..services.gemini_vision import forget_image
from ..services.wellbeing_guard import assess, signal_hub_if_needed
from ..services.photo_storage import MAX_UPLOAD_BYTES, InvalidPhoto, quality_check, sanitize_image

router = APIRouter()


@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    photo_type: str = Form(...),
    user_id: int = Form(1),
    db: Session = Depends(get_db),
):
    if photo_type not in ["front", "side", "back"]:
        raise HTTPException(400, "photo_type must be front, side, or back")

    # Read one byte past the limit so an oversized upload is rejected without
    # loading arbitrarily large files into memory.
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    try:
        clean, ext = sanitize_image(content)
    except InvalidPhoto as e:
        raise HTTPException(400, str(e)) from e

    # Server-chosen name: nothing from the client's file name reaches the disk.
    file_path = UPLOAD_DIR / f"{photo_type}_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path.write_bytes(clean)

    photo = Photo(
        user_id=user_id,
        photo_type=photo_type,
        file_path=str(file_path),
        analysis_status="pending",
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    wellbeing = assess(db, user_id)
    signal_hub_if_needed(db, user_id, wellbeing)

    return {
        "id": photo.id,
        "photo_type": photo.photo_type,
        "url": f"/uploads/{file_path.name}",
        "status": photo.analysis_status,
        # Plan 4.9: tell the user right away if the photo is unusable
        "quality": quality_check(clean),
        # Plan 5.6: gentle note when photos are taken very often
        "wellbeing": wellbeing,
    }


@router.get("/")
async def list_photos(user_id: int = 1, db: Session = Depends(get_db)):
    photos = db.query(Photo).filter(Photo.user_id == user_id).all()
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


@router.delete("/{photo_id}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """Delete the photo file, its analyses (ORM cascade) and its cached AI results."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(404, "Photo not found")
    path = photo_path(photo.file_path)
    if path.exists():
        forget_image(path.read_bytes())
        path.unlink(missing_ok=True)
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted"}
