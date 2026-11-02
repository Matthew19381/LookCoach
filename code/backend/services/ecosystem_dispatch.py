"""After an analysis: tell the ecosystem what changed (plan 3.3, 3.5, 3.6).

- `module_directive` events: the hub forwards them to `target_module`
  (System-Glowny H-1). Sent only when the needs differ from the last ones sent
  for that module, so re-analysing a photo does not spam ForgeBody/Dieta.
- `state_observation`: qualitative labels of the session (no scores, LC-9);
  the hub's day plan can tick "photo session" off with it (plan 3.10).
"""
import json

from sqlalchemy.orm import Session

from ..models.outbox import OutboxEvent
from ..models.profile import UserProfile
from . import outbox
from .analysis_store import load_latest_analysis
from .goal_router import nutrition_needs, training_needs

TARGETS = {
    "aesthetic_priority": "forge-body",
    "nutrition_needs": "dieta",
}


def _last_sent_payload(db: Session, user_id: int, directive: str) -> dict | None:
    rows = (
        db.query(OutboxEvent)
        .filter(OutboxEvent.user_id == user_id, OutboxEvent.event_type == "module_directive")
        .filter(OutboxEvent.status != "failed")
        .order_by(OutboxEvent.id.desc())
        .all()
    )
    for row in rows:
        data = json.loads(row.data)
        if data.get("directive") == directive:
            return data.get("payload")
    return None


def current_needs(db: Session, user_id: int) -> dict[str, dict | None]:
    latest = load_latest_analysis(db, user_id)
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    health = profile.get_health() if profile else {}
    return {
        "aesthetic_priority": training_needs(latest["body"]),
        "nutrition_needs": nutrition_needs(latest["face"], latest["skin"], health),
    }


def dispatch_needs(db: Session, user_id: int) -> list[str]:
    """Queue directives whose content changed. Returns the directive names queued."""
    queued = []
    for directive, payload in current_needs(db, user_id).items():
        if payload is None or payload == _last_sent_payload(db, user_id, directive):
            continue
        outbox.enqueue(
            db,
            "module_directive",
            {
                "target_module": TARGETS[directive],
                "directive": directive,
                "payload": payload,
                "reason": payload.get("reason", ""),
            },
            user_id=user_id,
        )
        queued.append(directive)
    return queued


def observe_session(db: Session, user_id: int, photo_type: str, labels: dict[str, str]) -> None:
    outbox.enqueue(
        db,
        "state_observation",
        {"observation_type": "photo_session", "photo_type": photo_type, "labels": labels},
        user_id=user_id,
    )
