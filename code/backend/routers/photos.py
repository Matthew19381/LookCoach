import os
import time
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.photo import Photo

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    photo_type: str = Form(...),
    user_id: int = Form(1),
    db: Session = Depends(get_db),
):
    if photo_type not in ["front", "side", "back"]:
        raise HTTPException(400, "photo_type must be front, side, or back")

    file_ext = Path(file.filename).suffix or ".jpg"
    file_path = UPLOAD_DIR / f"{photo_type}_{user_id}_{int(time.time())}{file_ext}"

    content = await file.read()
    file_path.write_bytes(content)

    photo = Photo(
        user_id=user_id,
        photo_type=photo_type,
        file_path=str(file_path),
        analysis_status="pending",
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)

    return {
        "id": photo.id,
        "photo_type": photo.photo_type,
        "url": f"/uploads/{file_path.name}",
        "status": photo.analysis_status,
    }


@router.get("/")
async def list_photos(user_id: int = 1, db: Session = Depends(get_db)):
    photos = db.query(Photo).filter(Photo.user_id == user_id).all()
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


@router.delete("/{photo_id}")
async def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(404, "Photo not found")
    try:
        Path(photo.file_path).unlink(missing_ok=True)
    except Exception:
        pass
    db.delete(photo)
    db.commit()
    return {"message": "Photo deleted"}
