import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..security import require_module_key
from ..models.integration_event import IntegrationEvent as IntegrationEventModel

router = APIRouter()


class IntegrationEvent(BaseModel):
    source_module: str
    event_type: str
    user_id: str
    timestamp: str
    payload: dict = {}


@router.post("/event")
async def receive_event(
    event: IntegrationEvent,
    db: Session = Depends(get_db),
    _auth: None = Depends(require_module_key),
):
    """Receive an event from another System-Główny module (auth via X-Module-Key)."""
    record = IntegrationEventModel(
        source_module=event.source_module,
        event_type=event.event_type,
        user_id=event.user_id,
        timestamp=event.timestamp,
        payload=json.dumps(event.payload),
    )
    db.add(record)
    db.commit()
    return {"status": "received", "event_type": event.event_type}


@router.get("/events")
async def list_events(user_id: str, db: Session = Depends(get_db)):
    """List stored integration events for a user (verification/debug endpoint)."""
    events = (
        db.query(IntegrationEventModel)
        .filter(IntegrationEventModel.user_id == user_id)
        .order_by(IntegrationEventModel.received_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": e.id,
            "source_module": e.source_module,
            "event_type": e.event_type,
            "user_id": e.user_id,
            "timestamp": e.timestamp,
            "payload": json.loads(e.payload) if e.payload else {},
            "received_at": e.received_at.isoformat() if e.received_at else None,
        }
        for e in events
    ]


# GET /output removed 2026-11-02: it always returned an empty list and nothing called it.
