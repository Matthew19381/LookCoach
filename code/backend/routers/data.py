"""Privacy: download everything LookCoach stores about you, or delete it for good."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.data_privacy import delete_all, export_zip

router = APIRouter()

CONFIRM_PHRASE = "USUN-WSZYSTKO"


@router.get("/export")
def export_data(user_id: int = 1, db: Session = Depends(get_db)):
    """ZIP: dane.json (all tables) + zdjecia/ (photo files)."""
    return Response(
        content=export_zip(db, user_id),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="lookcoach-dane-{user_id}.zip"'},
    )


@router.delete("")
def delete_data(confirm: str = "", user_id: int = 1, db: Session = Depends(get_db)):
    """Permanent - requires ?confirm=USUN-WSZYSTKO so it cannot happen by accident."""
    if confirm != CONFIRM_PHRASE:
        raise HTTPException(400, f"Aby usunąć wszystkie dane, potwierdź frazą {CONFIRM_PHRASE}.")
    return {"status": "deleted", "deleted_rows": delete_all(db, user_id)}
