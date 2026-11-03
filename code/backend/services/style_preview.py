"""Preview of a hairstyle / beard on the user's own front photo (plan 4.13, D8).

Optional and paid (one image-generation call via OpenRouter). Safeguards:
- only options LookCoach itself proposed (no free text into the prompt),
- the prompt forbids changing the face, body or "beautifying" (LC-9: a
  preview of a haircut, not an improved version of the person),
- DAILY_LIMIT calls per day, the image is returned once and never stored.
"""
import base64
import os
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from ..models.photo import Photo
from ..models.style_preview import StylePreviewLog
from ..paths import photo_path

PREVIEW_MODEL = os.getenv("STYLE_PREVIEW_MODEL", "google/gemini-2.5-flash-image")
DAILY_LIMIT = int(os.getenv("STYLE_PREVIEW_DAILY_LIMIT", "5"))
API_URL = "https://openrouter.ai/api/v1/chat/completions"

WARNING = (
    "To wizualizacja fryzury/zarostu wygenerowana przez AI, a nie przewidywanie efektu ani cel do "
    "porównywania się. Twarz może wyglądać inaczej niż na zdjęciu — liczy się kształt i długość włosów."
)

BEARD_OPTIONS = {
    "zarost 3-5 mm": "even short stubble 3-5 mm with a clean neckline",
    "krótka broda 1-2 cm": "short full beard 1-2 cm, rounded, with a defined neckline",
    "gładko ogolony": "clean shaven face",
}


class PreviewError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def _today_count(db: Session, user_id: int) -> int:
    since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=1)
    return (
        db.query(StylePreviewLog)
        .filter(StylePreviewLog.user_id == user_id, StylePreviewLog.created_at >= since)
        .count()
    )


def _latest_front(db: Session, user_id: int) -> Photo | None:
    return (
        db.query(Photo)
        .filter(Photo.user_id == user_id, Photo.photo_type == "front", Photo.analysis_status == "done")
        .order_by(Photo.uploaded_at.desc(), Photo.id.desc())
        .first()
    )


def _prompt(kind: str, description: str) -> str:
    what = "hairstyle" if kind == "hair" else "facial hair"
    return (
        f"Edit this photo: change ONLY the {what} to: {description}. "
        "Keep the person's face, facial features, skin, body, expression, lighting and background exactly "
        "the same. Do not beautify, slim, smooth skin or alter any other feature. Photorealistic."
    )


def generate_preview(db: Session, user_id: int, kind: str, option: str, allowed: dict[str, str],
                     post=httpx.post) -> dict:
    """`allowed`: option name -> description (from the current advice). Returns a data URL."""
    if option not in allowed:
        raise PreviewError(422, "Podgląd jest dostępny tylko dla zaproponowanych opcji.")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise PreviewError(503, "Podgląd wymaga klucza OpenRouter w .env.")
    used = _today_count(db, user_id)
    if used >= DAILY_LIMIT:
        raise PreviewError(429, f"Limit {DAILY_LIMIT} podglądów na dobę został wykorzystany.")
    photo = _latest_front(db, user_id)
    path = photo_path(photo.file_path) if photo else None
    if not path or not path.exists():
        raise PreviewError(404, "Potrzebne jest przeanalizowane zdjęcie z przodu.")

    image_b64 = base64.b64encode(path.read_bytes()).decode()
    payload = {
        "model": PREVIEW_MODEL,
        "modalities": ["image", "text"],
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": _prompt(kind, allowed[option])},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
            ],
        }],
    }
    headers = {"Authorization": f"Bearer {api_key}", "X-Title": "LookCoach"}
    log = StylePreviewLog(user_id=user_id, kind=kind, option=option, status="error")
    db.add(log)
    try:
        response = post(API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        images = response.json()["choices"][0]["message"].get("images") or []
        url = images[0]["image_url"]["url"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as e:
        db.commit()
        raise PreviewError(502, "Generowanie podglądu nie powiodło się.") from e
    log.status = "ok"
    db.commit()
    return {"image": url, "warning": WARNING, "remaining_today": max(DAILY_LIMIT - used - 1, 0)}
