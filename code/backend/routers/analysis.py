import json
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.photo import Photo
from ..models.analysis import Analysis
from ..paths import photo_path
from ..services.gemini_vision import GeminiVisionService
from ..services.analysis_store import has_any, load_latest_analysis
from ..services import outbox
from ..services.attractiveness_levers import AttractivenessLevers
from ..services.ecosystem_dispatch import dispatch_needs, observe_session
from ..services.state_labels import state_labels

router = APIRouter()
logger = logging.getLogger(__name__)

VISION_SERVICE = GeminiVisionService()


@router.get("/latest")
async def get_latest_analysis(user_id: int = 1, db: Session = Depends(get_db)):
    latest = load_latest_analysis(db, user_id)
    lever = None
    if has_any(latest):
        lever = AttractivenessLevers.detect_lever(
            latest["face"] or {}, latest["body"] or {}, latest["skin"] or {}, latest["hair"] or {},
        )
    return {**latest, "lever": lever}


@router.post("/analyze/{photo_id}")
async def analyze_photo(photo_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(404, "Photo not found")

    photo.analysis_status = "processing"
    db.commit()

    try:
        image_bytes = photo_path(photo.file_path).read_bytes()

        analysis = Analysis(photo_id=photo.id)

        if photo.photo_type == "front":
            data = VISION_SERVICE.analyze_face(image_bytes)
            analysis.set_face_data(data or {})
        elif photo.photo_type == "side":
            data = VISION_SERVICE.analyze_body(image_bytes)
            analysis.set_body_data(data or {})
        elif photo.photo_type == "back":
            skin_data = VISION_SERVICE.analyze_skin(image_bytes)
            hair_data = VISION_SERVICE.analyze_hair(image_bytes)
            analysis.set_skin_data(skin_data or {})
            analysis.set_hair_data(hair_data or {})

        lever = AttractivenessLevers.detect_lever(
            analysis.get_face_data(),
            analysis.get_body_data(),
            analysis.get_skin_data(),
            analysis.get_hair_data(),
        )
        analysis.attractiveness_lever = json.dumps(lever)

        db.add(analysis)
        photo.analysis_status = "done"
        db.commit()

        # Plan 3.3-3.6: share the new state with the hub / ForgeBody / Dieta.
        # Never fails the analysis itself - the outbox retries delivery later.
        try:
            observe_session(db, photo.user_id, photo.photo_type, state_labels(analysis))
            dispatch_needs(db, photo.user_id)
            background_tasks.add_task(outbox.deliver_in_new_session, db.get_bind())
        except Exception:
            logger.exception("Queueing ecosystem events after analysis %s failed", analysis.id)

        return {"message": "Analysis complete", "analysis_id": analysis.id}
    except Exception:
        # Details go to the log, not to the client (they can contain paths or
        # provider responses - plan 2.6).
        logger.exception("Analysis of photo %s failed", photo_id)
        db.rollback()
        photo.analysis_status = "failed"
        db.commit()
        raise HTTPException(500, "Analiza nie powiodła się. Spróbuj ponownie za chwilę.")
