import json
from datetime import date as date_type
from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..database import get_db
from ..models.analysis import Analysis
from ..models.consistency import AdherenceLog, ProtocolTypeEnum
from ..models.photo import Photo
from ..models.recommendation import Recommendation
from ..models.integration_event import IntegrationEvent

router = APIRouter()

# Daily routines offered to the hub's day plan; each is ticked off there by the
# protocol_done event that /consistency/adherence/log publishes.
ROUTINES = {
    "skincare_morning": ("Pielęgnacja rano", "rano po umyciu twarzy"),
    "skincare_evening": ("Pielęgnacja wieczorem", "wieczorem przed snem"),
}
TRACKED_WINDOW_DAYS = 14


TITLE_MAX = 100


def _with_steps(title: str, steps: list) -> str:
    """'Pielęgnacja rano: Umyj twarz…, Krem z filtrem…' capped for the hub's list."""
    if not steps:
        return title
    full = f"{title}: " + ", ".join(s.name for s in steps)
    return full if len(full) <= TITLE_MAX else full[:TITLE_MAX - 1].rstrip(" ,") + "…"


def _suggested_items(db: Session, user_id: int, day: date_type) -> list[dict]:
    """Routines the user chose: a slot of their saved routine with steps planned
    for `day` (2026-10-15), or one they tracked in the last 14 days - and only
    if not logged for `day` yet. Nothing is pushed on anyone: with no saved
    routine and no entries the hub gets no item."""
    from ..services.my_routine import SLOTS, steps_for_day, survival_mode, user_steps

    start = datetime.combine(day - timedelta(days=TRACKED_WINDOW_DAYS), time.min)
    end = datetime.combine(day + timedelta(days=1), time.min)
    logs = db.query(AdherenceLog).filter(
        AdherenceLog.user_id == user_id,
        AdherenceLog.protocol_type.in_([ProtocolTypeEnum(p) for p in ROUTINES]),
        AdherenceLog.date >= start, AdherenceLog.date < end,
    ).all()
    tracked = {log.protocol_type.value for log in logs}
    done_today = {log.protocol_type.value for log in logs if log.date.date() == day}
    survival = survival_mode(db, user_id)
    steps = user_steps(db, user_id)
    planned = steps_for_day(steps, day, survival)
    if steps:
        # A saved routine decides: a slot with nothing planned today is not offered
        wanted = {SLOTS[slot] for slot, rows in planned.items() if rows}
    else:
        wanted = tracked
    by_protocol = {SLOTS[slot]: rows for slot, rows in planned.items()}
    return [
        {
            "title": _with_steps(title + (" (wersja bazowa)" if survival else ""), by_protocol.get(protocol, [])),
            "intention_cue": cue,
            "estimated_minutes": 2 if survival else 5,
            "priority": 2,
            "complete_on": [f"protocol_done:protocol_id={protocol}"],
        }
        for protocol, (title, cue) in ROUTINES.items()
        if protocol in wanted and protocol not in done_today
    ]


def _day(raw: str) -> date_type:
    try:
        return date_type.fromisoformat(raw)
    except ValueError:
        return date_type.today()


@router.get("/summary")
async def get_summary(
    user_id: str = Query(...),
    date: str = Query(None),
    db: Session = Depends(get_db),
):
    """System-Główny integration contract: cross-module status snapshot."""
    target_date = date or date_type.today().isoformat()

    try:
        numeric_user_id = int(user_id)
    except ValueError:
        numeric_user_id = -1

    photos_analyzed_today = (
        db.query(Analysis)
        .join(Photo, Analysis.photo_id == Photo.id)
        .filter(Photo.user_id == numeric_user_id)
        .filter(func.date(Analysis.created_at) == target_date)
        .count()
    )

    active_recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == numeric_user_id)
        .filter(Recommendation.is_done == "N")
        .count()
    )

    focus_area = None
    latest_analysis = (
        db.query(Analysis)
        .join(Photo, Analysis.photo_id == Photo.id)
        .filter(Photo.user_id == numeric_user_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )
    if latest_analysis and latest_analysis.attractiveness_lever:
        try:
            lever = json.loads(latest_analysis.attractiveness_lever)
            focus_area = lever.get("primary_lever")
        except (ValueError, TypeError):
            focus_area = None

    events = (
        db.query(IntegrationEvent)
        .filter(IntegrationEvent.user_id == user_id)
        .order_by(IntegrationEvent.received_at.desc())
        .limit(20)
        .all()
    )

    return {
        "module": "lookcoach",
        "user_id": user_id,
        "date": target_date,
        "summary": {
            "photos_analyzed_today": photos_analyzed_today,
            "active_recommendations": active_recommendations,
            "focus_area": focus_area,
            "suggested_items": _suggested_items(db, numeric_user_id, _day(target_date)),
        },
        "events": [
            {
                "source_module": e.source_module,
                "event_type": e.event_type,
                "timestamp": e.timestamp,
                "payload": json.loads(e.payload) if e.payload else {},
            }
            for e in events
        ],
    }
