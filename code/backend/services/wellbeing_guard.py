"""Compulsive photo checking detector (plan 5.6, NEURO_PLAN §5 / LC-9).

Looks change slowly; checking them many times a day or almost every day is a
known pattern in body dysmorphic concerns. LookCoach does not diagnose - it
slows down, says so kindly, and (once a week at most) sends a signal to the
hub for the Mentalność module.

Levels:
- "ok"
- "notice": photos on 4+ different days in the last 7 - a gentle note
- "concern": the same view 3+ times in 24 h, 9+ photos in 24 h, or photos on 6+
  of the last 7 days - analysis needs an explicit confirmation, hub is told.
"""
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from ..models.outbox import OutboxEvent
from ..models.photo import Photo
from . import outbox

NOTICE_DAYS = 4
CONCERN_DAYS = 6
CONCERN_SAME_VIEW_24H = 3
CONCERN_TOTAL_24H = 9
SIGNAL_EVERY = timedelta(days=7)

MESSAGES = {
    "notice": (
        "Zmiany wyglądu zachodzą powoli — zdjęcia co 2–4 tygodnie pokażą więcej niż codzienne. "
        "Następną sesję warto zrobić za kilka dni."
    ),
    "concern": (
        "Robisz ostatnio bardzo dużo zdjęć. Częste sprawdzanie wyglądu potrafi zwiększać niepokój zamiast "
        "go zmniejszać. Może zrobisz przerwę od zdjęć na kilka dni? Jeśli myśli o wyglądzie są uciążliwe, "
        "warto porozmawiać z psychologiem — moduł Mentalność może w tym pomóc."
    ),
}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def assess(db: Session, user_id: int, now: datetime | None = None) -> dict:
    now = now or _now()
    week = (
        db.query(Photo)
        .filter(Photo.user_id == user_id, Photo.uploaded_at >= now - timedelta(days=7))
        .all()
    )
    week = [p for p in week if p.uploaded_at is not None]
    day = [p for p in week if p.uploaded_at and p.uploaded_at >= now - timedelta(hours=24)]
    days_with_photos = len({p.uploaded_at.date() for p in week if p.uploaded_at})
    per_view_24h: dict[str, int] = {}
    for p in day:
        per_view_24h[p.photo_type] = per_view_24h.get(p.photo_type, 0) + 1

    signals = []
    if max(per_view_24h.values(), default=0) >= CONCERN_SAME_VIEW_24H:
        signals.append("same_view_repeated_24h")
    if len(day) >= CONCERN_TOTAL_24H:
        signals.append("many_photos_24h")
    if days_with_photos >= CONCERN_DAYS:
        signals.append("almost_daily")
    level = "concern" if signals else ("notice" if days_with_photos >= NOTICE_DAYS else "ok")
    if level == "notice":
        signals.append("frequent_days")
    return {
        "level": level,
        "message": MESSAGES.get(level),
        "signals": signals,
        "photos_last_7_days": len(week),
        "days_with_photos_last_7_days": days_with_photos,
    }


def signal_hub_if_needed(db: Session, user_id: int, result: dict) -> bool:
    """Tell the hub and Mentalność at most once per SIGNAL_EVERY."""
    if result["level"] != "concern":
        return False
    since = _now() - SIGNAL_EVERY
    recent = (
        db.query(OutboxEvent)
        .filter(OutboxEvent.user_id == user_id, OutboxEvent.event_type == "state_observation",
                OutboxEvent.created_at >= since)
        .all()
    )
    if any(json.loads(r.data).get("observation_type") == "photo_checking_pattern" for r in recent):
        return False
    outbox.enqueue(db, "state_observation", {
        "observation_type": "photo_checking_pattern",
        "level": "concern",
        "signals": result["signals"],
        "target_hint": "mentalnosc",
    }, user_id=user_id)
    # H-6: delivered to Mentalność by the hub (module_directive, System-Glowny §1.5) -
    # it shows a gentle card in its check-in until acknowledged.
    outbox.enqueue(db, "module_directive", {
        "target_module": "mentalnosc",
        "directive": "body_image_signal",
        "reason": "Bardzo częste sprawdzanie wyglądu albo cierpienie z powodu wyglądu (LookCoach)",
        "payload": {"level": "concern", "signals": result["signals"]},
    }, user_id=user_id)
    return True
