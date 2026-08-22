import json
import os

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.integration_event import IntegrationEvent as IntegrationEventModel

router = APIRouter()


class IntegrationEvent(BaseModel):
    source_module: str
    event_type: str
    user_id: str
    timestamp: str
    payload: dict = {}


def _verify_module_key(x_module_key: str | None) -> None:
    expected_key = os.getenv("MODULE_KEY")
    if not expected_key or not x_module_key or x_module_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid X-Module-Key")


@router.post("/event")
async def receive_event(
    event: IntegrationEvent,
    x_module_key: str | None = Header(None),
    db: Session = Depends(get_db),
):
    """Receive an event from another System-Główny module (auth via X-Module-Key)."""
    _verify_module_key(x_module_key)
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


@router.get("/output")
async def integration_output(module: str = "", user_id: int = 1, db: Session = Depends(get_db)):
    """Return recommendations for external system."""
    return {"module": module, "recommendations": []}
