"""Outgoing event queue to the System-Główny hub (plan 3.1).

Before 2026-11-02 an event was sent once from a background task; with the hub
down (or restarting) it was simply lost. Now every event is stored first and
delivered by `deliver_pending` - right after queueing and then periodically
(worker started in main.lifespan). The hub deduplicates on
module+user+type+timestamp and the timestamp is fixed at queueing time, so a
retry after a lost response cannot create a duplicate.

Failure handling:
- no MODULE_KEY / 401 (configuration): stays pending, retried hourly - fixing
  the .env must not lose the events;
- network error / 5xx / 429: exponential backoff (1, 2, 4 ... min, max 6 h),
  `failed` after MAX_ATTEMPTS;
- other 4xx (contract error): `failed` at once - a retry cannot fix it.
"""
import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..models.outbox import OutboxEvent
from .integration_publisher import (
    VALID_EVENT_TYPES,
    ConfigurationError,
    IntegrationPublisher,
    PublishError,
)

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 12
MAX_BACKOFF = timedelta(hours=6)
CONFIG_RETRY = timedelta(hours=1)


def _now() -> datetime:
    """Naive UTC: SQLite stores datetimes without a zone, comparisons must match."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def enqueue(db: Session, event_type: str, data: dict, user_id: int = 1) -> OutboxEvent:
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Unknown event type: {event_type}")
    row = OutboxEvent(
        user_id=user_id,
        event_type=event_type,
        data=json.dumps(data, ensure_ascii=False),
        timestamp=_now().isoformat() + "Z",
        status="pending",
        attempts=0,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _backoff(attempts: int) -> timedelta:
    return min(timedelta(minutes=2 ** max(attempts - 1, 0)), MAX_BACKOFF)


async def deliver_pending(db: Session, publisher_factory=IntegrationPublisher, limit: int = 50) -> dict:
    """Try to deliver due pending events. Returns {"sent", "retry", "failed"} counts."""
    now = _now()
    due = (
        db.query(OutboxEvent)
        .filter(OutboxEvent.status == "pending")
        .filter(or_(OutboxEvent.next_attempt_at.is_(None), OutboxEvent.next_attempt_at <= now))
        .order_by(OutboxEvent.id)
        .limit(limit)
        .all()
    )
    counts = {"sent": 0, "retry": 0, "failed": 0}
    if not due:
        return counts

    try:
        publisher = publisher_factory(timeout=5.0)
    except ConfigurationError as e:
        for row in due:
            row.last_error = str(e)
            row.next_attempt_at = now + CONFIG_RETRY
        db.commit()
        counts["retry"] = len(due)
        return counts

    for row in due:
        row.attempts += 1
        try:
            response = await publisher.publish(
                row.event_type, str(row.user_id), json.loads(row.data), timestamp=row.timestamp,
            )
        except ConfigurationError as e:  # 401 - wrong key
            row.last_error = str(e)
            row.next_attempt_at = now + CONFIG_RETRY
            counts["retry"] += 1
        except PublishError as e:
            row.last_error = str(e)
            permanent = e.status_code is not None and 400 <= e.status_code < 500 and e.status_code != 429
            if permanent or row.attempts >= MAX_ATTEMPTS:
                row.status = "failed"
                counts["failed"] += 1
                logger.warning("Hub event %s (%s) failed permanently: %s", row.id, row.event_type, e)
            else:
                row.next_attempt_at = now + _backoff(row.attempts)
                counts["retry"] += 1
        else:
            row.status = "sent"
            row.sent_at = now
            row.last_error = None
            row.hub_response = json.dumps(response, ensure_ascii=False, default=str)[:4000]
            counts["sent"] += 1
        db.commit()
    return counts


async def deliver_in_new_session(bind=None) -> dict:
    """For BackgroundTasks / the periodic worker: the request session is closed by then.

    `bind`: engine of the request's session (keeps tests on their own DB);
    None = the app database."""
    from sqlalchemy.orm import sessionmaker

    from ..database import SessionLocal

    db = sessionmaker(bind=bind)() if bind is not None else SessionLocal()
    try:
        return await deliver_pending(db)
    except Exception:  # the worker must never die on one bad run
        logger.exception("Outbox delivery run failed")
        return {}
    finally:
        db.close()


def status_summary(db: Session, user_id: int = 1) -> dict:
    """For the 'Połączenia' panel (plan 3.12)."""
    base = db.query(OutboxEvent).filter(OutboxEvent.user_id == user_id)
    last = base.order_by(OutboxEvent.id.desc()).limit(10).all()
    return {
        "pending": base.filter(OutboxEvent.status == "pending").count(),
        "failed": base.filter(OutboxEvent.status == "failed").count(),
        "recent": [
            {
                "event_type": r.event_type,
                "status": r.status,
                "attempts": r.attempts,
                "timestamp": r.timestamp,
                "last_error": r.last_error,
                "data": json.loads(r.data),
            }
            for r in last
        ],
    }

