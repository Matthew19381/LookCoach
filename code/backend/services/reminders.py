"""Push reminders (plan 5.5): morning/evening routine and control photos.

Rules: only routines the user actually tracks and has not logged today (same
source as the hub's day plan, summary._suggested_items), photos only when the
14-day interval is due, never inside hub `quiet_hours`, shorter wording in
`survival_mode`, each kind at most once a day. Sending is skipped silently
without VAPID keys in .env (scripts/generate_vapid_keys.py makes them).
"""
import logging
import os
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models.directive_state import DirectiveState
from ..models.push import PushSubscription, ReminderLog, ReminderSettings
from . import webpush

logger = logging.getLogger(__name__)


def _minutes(hhmm: str | None) -> int | None:
    try:
        h, m = (int(x) for x in str(hhmm).split(":")[:2])
        return h * 60 + m
    except ValueError:
        return None


def in_quiet_hours(now_min: int, start: str | None, end: str | None) -> bool:
    a, b = _minutes(start), _minutes(end)
    if a is None or b is None:
        return False
    return a <= now_min < b if a < b else (now_min >= a or now_min < b)  # across midnight


def settings_for(db: Session, user_id: int) -> ReminderSettings:
    row = db.query(ReminderSettings).filter(ReminderSettings.user_id == user_id).first()
    if not row:
        row = ReminderSettings(user_id=user_id, enabled=True, morning_time="07:30",
                               evening_time="21:30", photo_reminders=True)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def due(db: Session, user_id: int, now: datetime) -> list[dict]:
    """Reminders that should go out now (not yet sent today)."""
    from ..routers.summary import _suggested_items  # same rules as the hub day plan

    settings = settings_for(db, user_id)
    if not settings.enabled:
        return []
    state = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()
    now_min = now.hour * 60 + now.minute
    if state and in_quiet_hours(now_min, state.quiet_hours_from, state.quiet_hours_to):
        return []
    survival = bool(state and state.survival_mode)
    sent = {r.kind for r in db.query(ReminderLog).filter(ReminderLog.user_id == user_id,
                                                         ReminderLog.day == now.date()).all()}
    items = {i["complete_on"][0]: i for i in _suggested_items(db, user_id, now.date())}
    out = []

    def add(kind: str, at: str, title: str, body: str, url: str) -> None:
        start = _minutes(at)
        if kind not in sent and start is not None and now_min >= start:
            out.append({"kind": kind, "title": title, "body": body, "url": url})

    morning = items.get("protocol_done:protocol_id=skincare_morning")
    if morning:
        add("skincare_morning", settings.morning_time, "Pielęgnacja rano",
            "Wersja minimum: umyj i SPF." if survival else "Twoja poranna rutyna czeka.", "/consistency")
    evening = items.get("protocol_done:protocol_id=skincare_evening")
    if evening:
        add("skincare_evening", settings.evening_time, "Pielęgnacja wieczorem",
            "Wersja minimum: tylko oczyszczanie." if survival else "Pora na wieczorną rutynę.", "/consistency")
    if settings.photo_reminders and items.get("state_observation:observation_type=photo_session"):
        add("photo_session", settings.morning_time, "Zdjęcia kontrolne",
            "Minęły 2 tygodnie — zrób zdjęcia w tym samym świetle co ostatnio.", "/photos")
    return out


def run(db: Session, now: datetime | None = None, send=webpush.send) -> int:
    """Send due reminders to every subscribed user. Returns notifications sent."""
    private = os.getenv("VAPID_PRIVATE_KEY")
    subject = os.getenv("VAPID_SUBJECT", "mailto:lookcoach@localhost")
    if not private:
        return 0
    key = webpush.load_vapid_private(private)
    now = now or datetime.now()
    sent = 0
    for user_id in {s.user_id for s in db.query(PushSubscription).all()}:
        reminders = due(db, user_id, now)
        if not reminders:
            continue
        subs = db.query(PushSubscription).filter(PushSubscription.user_id == user_id).all()
        for reminder in reminders:
            try:
                db.add(ReminderLog(user_id=user_id, kind=reminder["kind"], day=now.date()))
                db.commit()
            except IntegrityError:  # another worker run already sent it
                db.rollback()
                continue
            for sub in subs:
                try:
                    send({"endpoint": sub.endpoint, "keys": {"p256dh": sub.p256dh, "auth": sub.auth}},
                         {k: reminder[k] for k in ("title", "body", "url")}, key, subject)
                    sent += 1
                except webpush.SubscriptionGone:
                    db.delete(sub)
                    db.commit()
                except Exception:
                    logger.exception("Push to subscription %s failed", sub.id)
    return sent


def run_in_new_session() -> int:
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        return run(db)
    except Exception:
        logger.exception("Reminder run failed")
        return 0
    finally:
        db.close()

