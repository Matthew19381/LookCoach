import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.photo import Photo
from ..models.analysis import Analysis
from ..services.gemini_vision import GeminiVisionService
from ..services.attractiveness_levers import AttractivenessLevers

router = APIRouter()

VISION_SERVICE = GeminiVisionService()


@router.get("/latest")
async def get_latest_analysis(user_id: int = 1, db: Session = Depends(get_db)):
    photos = (
        db.query(Photo)
        .filter(Photo.user_id == user_id, Photo.analysis_status == "done")
        .all()
    )

    if not photos:
        return {
            "face": None,
            "body": None,
            "skin": None,
            "hair": None,
            "overall_score": 0.0,
            "lever": None,
            "photos_analyzed": 0,
        }

    result = {}
    photo_map = {p.photo_type: p for p in photos}
    scores = []

    for ptype in ["front", "side", "back"]:
        if ptype in photo_map:
            analysis = (
                db.query(Analysis).filter(Analysis.photo_id == photo_map[ptype].id).first()
            )
            if analysis:
                if ptype == "front":
                    face = analysis.get_face_data()
                    result["face"] = face
                    if face:
                        scores.append(face.get("overall_face_score", 0))
                elif ptype == "side":
                    body = analysis.get_body_data()
                    result["body"] = body
                    if body:
                        scores.append(body.get("overall_body_score", 0))
                elif ptype == "back":
                    skin = analysis.get_skin_data()
                    hair = analysis.get_hair_data()
                    result["skin"] = skin
                    result["hair"] = hair
                    if skin:
                        scores.append(skin.get("overall_skin_score", 0))
                    if hair:
                        scores.append(hair.get("overall_hair_score", 0))

    overall = sum(scores) / len(scores) if scores else 0.0
    lever = AttractivenessLevers.detect_lever(
        result.get("face"), result.get("body"), result.get("skin"), result.get("hair")
    )

    return {
        **result,
        "overall_score": round(overall, 1),
        "lever": lever,
        "photos_analyzed": len(photos),
    }


@router.post("/analyze/{photo_id}")
async def analyze_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(404, "Photo not found")

    photo.analysis_status = "processing"
    db.commit()

    try:
        image_bytes = Path(photo.file_path).read_bytes()
        analysis = Analysis(photo_id=photo.id)

        if photo.photo_type == "front":
            data = VISION_SERVICE.analyze_face(image_bytes)
            analysis.set_face_data(data or {})
            analysis.overall_score = (data or {}).get("overall_face_score", 0)
        elif photo.photo_type == "side":
            data = VISION_SERVICE.analyze_body(image_bytes)
            analysis.set_body_data(data or {})
            analysis.overall_score = (data or {}).get("overall_body_score", 0)
        elif photo.photo_type == "back":
            skin_data = VISION_SERVICE.analyze_skin(image_bytes)
            hair_data = VISION_SERVICE.analyze_hair(image_bytes)
            analysis.set_skin_data(skin_data or {})
            analysis.set_hair_data(hair_data or {})
            s = (skin_data or {}).get("overall_skin_score", 0)
            h = (hair_data or {}).get("overall_hair_score", 0)
            analysis.overall_score = (s + h) / 2

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

        return {"message": "Analysis complete", "analysis_id": analysis.id}
    except Exception as e:
        photo.analysis_status = "failed"
        db.commit()
        raise HTTPException(500, f"Analysis failed: {str(e)}")
