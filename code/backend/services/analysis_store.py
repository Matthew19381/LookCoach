"""Latest stored analysis of a user, merged across photo types.

One place for "what do we know about the user's current state". Before
2026-11-02 recommendations and confidence used an empty/dummy analysis and the
posture page sent a hard-coded `mockAnalysis` from the browser.
"""
from sqlalchemy.orm import Session

from ..models.analysis import Analysis
from ..models.photo import Photo

# Which analysis sections each photo type fills (see routers/analysis.py).
# D1 (2026-11-02): front = face + skin + hairline; back = crown only. Hair is
# merged from the newest front (hairline, type) and newest back (crown) photo.
SECTIONS_BY_TYPE = {
    "front": ("face", "skin", "hair"),
    "side": ("body",),
    "back": ("hair",),
    "smile": ("smile",),  # optional (plan 4.6)
}

_GETTERS = {
    "face": Analysis.get_face_data,
    "body": Analysis.get_body_data,
    "skin": Analysis.get_skin_data,
    "hair": Analysis.get_hair_data,
    "smile": Analysis.get_smile_data,
}


def load_latest_analysis(db: Session, user_id: int) -> dict:
    """{"face", "body", "skin", "hair", "smile": dict | None, "photos_analyzed": int}.

    Each section comes from the newest analysed photo of the type that fills it.
    """
    photos = (
        db.query(Photo)
        .filter(Photo.user_id == user_id, Photo.analysis_status == "done")
        .order_by(Photo.uploaded_at.desc(), Photo.id.desc())
        .all()
    )
    result: dict = {"face": None, "body": None, "skin": None, "hair": None, "smile": None}
    seen: set[tuple[str, str]] = set()  # (photo_type, section) already taken from a newer photo
    for photo in photos:
        sections = [s for s in SECTIONS_BY_TYPE.get(photo.photo_type, ()) if (photo.photo_type, s) not in seen]
        if not sections:
            continue
        analysis = db.query(Analysis).filter(Analysis.photo_id == photo.id).first()
        if not analysis:
            continue
        for section in sections:
            data = _GETTERS[section](analysis)
            if not data:
                continue
            seen.add((photo.photo_type, section))
            if section == "hair" and result["hair"]:
                # the other view's newest photo: fill only what is still missing
                result["hair"] = {**data, **result["hair"]}
            else:
                result[section] = result[section] or data
    result["photos_analyzed"] = len(photos)
    return result


def has_any(analysis: dict) -> bool:
    return any(analysis.get(s) for s in ("face", "body", "skin", "hair"))
