"""Plan 5.4: the 'Dziś' start page - what to do today, nothing to configure."""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.analysis import Analysis
from ..models.directive_state import DirectiveState
from ..models.photo import Photo
from ..services.ecosystem_client import cached_overview
from ..services.state_labels import state_labels
from ..services.wellbeing_guard import assess
from .summary import PHOTO_INTERVAL_DAYS, _suggested_items

router = APIRouter()


@router.get("")
def today(user_id: int = 1, db: Session = Depends(get_db)):
    day = date.today()
    state = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()
    last_photo = (
        db.query(func.max(Photo.uploaded_at))
        .filter(Photo.user_id == user_id, Photo.analysis_status == "done")
        .scalar()
    )
    next_photos_in = None
    if last_photo is not None:
        next_photos_in = max(PHOTO_INTERVAL_DAYS - (day - last_photo.date()).days, 0)

    return {
        "date": day.isoformat(),
        "actions": _suggested_items(db, user_id, day),
        "directives": {
            "survival_mode": bool(state and state.survival_mode),
            "priority": state.priority if state else None,
        },
        "state": _latest_labels(db, user_id),
        "next_photos_in_days": next_photos_in,
        "wellbeing": assess(db, user_id),
        "ecosystem": cached_overview(db, user_id),
        "has_photos": last_photo is not None,
    }


def _latest_labels(db: Session, user_id: int) -> dict[str, str]:
    """Labels of the newest analysed photo of each view, merged."""
    labels: dict[str, str] = {}
    for ptype in ("front", "side", "back"):
        photo = (
            db.query(Photo)
            .filter(Photo.user_id == user_id, Photo.photo_type == ptype, Photo.analysis_status == "done")
            .order_by(Photo.uploaded_at.desc(), Photo.id.desc())
            .first()
        )
        if photo:
            analysis = db.query(Analysis).filter(Analysis.photo_id == photo.id).first()
            labels.update(state_labels(analysis))
    return labels

