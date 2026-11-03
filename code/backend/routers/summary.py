import json
from datetime import date as date_type
from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..database import get_db
from ..models.analysis import Analysis
from ..models.consistency import AdherenceLog, ProtocolTypeEnum
from ..models.directive_state import DirectiveState
from ..models.photo import Photo
from ..models.recommendation import Recommendation
from ..models.outbox import OutboxEvent

router = APIRouter()

# Daily routines offered to the hub's day plan; each is ticked off there by the
# protocol_done event that /consistency/adherence/log publishes.
ROUTINES = {
    "skincare_morning": ("Pielęgnacja rano", "rano po umyciu twarzy"),
    "skincare_evening": ("Pielęgnacja wieczorem", "wieczorem przed snem"),
}
TRACKED_WINDOW_DAYS = 14


def _suggested_items(db: Session, user_id: int, day: date_type) -> list[dict]:
    """Only routines the user actually tracks (logged in the last 14 days) and
    has not logged for `day` yet - no protocol is pushed on anyone."""
    start = datetime.combine(day - timedelta(days=TRACKED_WINDOW_DAYS), time.min)
    end = datetime.combine(day + timedelta(days=1), time.min)
    logs = db.query(AdherenceLog).filter(
        AdherenceLog.user_id == user_id,
        AdherenceLog.protocol_type.in_([ProtocolTypeEnum(p) for p in ROUTINES]),
        AdherenceLog.date >= start, AdherenceLog.date < end,
    ).all()
    tracked = {log.protocol_type.value for log in logs}
    done_today = {log.protocol_type.value for log in logs if log.date.date() == day}
    state = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()
    survival = bool(state and state.survival_mode)
    items = [
        {
            "title": title + (" (wersja bazowa)" if survival else ""),
            "intention_cue": cue,
            "estimated_minutes": 2 if survival else 5,
            "priority": 2,
            "complete_on": [f"protocol_done:protocol_id={protocol}"],
        }
        for protocol, (title, cue) in ROUTINES.items()
        if protocol in tracked and protocol not in done_today
    ]
    photo_item = _photo_session_item(db, user_id, day, survival)
    if photo_item:
        items.append(photo_item)
    return items[:3]  # hub contract: max 3 per module


# Plan 3.10: control photos every PHOTO_INTERVAL_DAYS - regular enough to see a
# trend, rare enough not to feed compulsive checking (LC-9). Only for users who
# already took photos; never in survival mode.
PHOTO_INTERVAL_DAYS = 14


def _photo_session_item(db: Session, user_id: int, day: date_type, survival: bool) -> dict | None:
    if survival:
        return None
    last = (
        db.query(func.max(Photo.uploaded_at))
        .filter(Photo.user_id == user_id, Photo.analysis_status == "done")
        .scalar()
    )
    if last is None or (day - last.date()).days < PHOTO_INTERVAL_DAYS:
        return None
    return {
        "title": "Zdjęcia kontrolne (przód i bok)",
        "intention_cue": "rano, to samo światło i miejsce co ostatnio",
        "estimated_minutes": 5,
        "priority": 3,
        "complete_on": ["state_observation:observation_type=photo_session"],
    }


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

    # Hub contract 1.1: `events` are the module's OWN events in format 1.2. Until
    # 2026-11-02 this echoed events received FROM other modules, in the old shape -
    # the hub skipped them as invalid.
    day_start = f"{target_date}T00:00:00"
    day_end = f"{target_date}T23:59:59.999999Z"
    own = (
        db.query(OutboxEvent)
        .filter(OutboxEvent.user_id == numeric_user_id, OutboxEvent.status != "failed")
        .filter(OutboxEvent.timestamp >= day_start, OutboxEvent.timestamp <= day_end)
        .order_by(OutboxEvent.id.desc())
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
                "event_type": e.event_type,
                "module": "lookcoach",
                "user_id": user_id,
                "timestamp": e.timestamp,
                "data": json.loads(e.data),
            }
            for e in reversed(own)
        ],
        "wellbeing_contribution": None,  # contract: null until the Affect Engine gives an honest basis
    }
