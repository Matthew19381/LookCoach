"""INT-3: directives from the System-Główny hub.

Hub contract: {"directive", "enabled", "value", "from", "to"}.
survival_mode sets every protocol to the SURVIVAL level of the Consistency
Tracker (e.g. skincare = rinse + SPF) until the hub switches it off.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directive_state import DirectiveState

router = APIRouter()

KNOWN = {"survival_mode", "priority", "quiet_hours"}


class DirectivePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    directive: str
    user_id: int = 1
    enabled: bool | None = None
    value: str | None = None
    from_: str | None = Field(None, alias="from")
    to: str | None = None


@router.post("")
def apply_directive(payload: DirectivePayload, db: Session = Depends(get_db)):
    if payload.directive not in KNOWN:
        raise HTTPException(status_code=422, detail=f"Unknown directive: {payload.directive}")
    state = db.query(DirectiveState).filter(DirectiveState.user_id == payload.user_id).first()
    if not state:
        state = DirectiveState(user_id=payload.user_id)
        db.add(state)
    on = payload.enabled is not False
    if payload.directive == "survival_mode":
        state.survival_mode = bool(payload.enabled)
    elif payload.directive == "priority":
        state.priority = payload.value if on else None
    else:
        state.quiet_hours_from = payload.from_ if on else None
        state.quiet_hours_to = payload.to if on else None
    db.commit()
    return {"status": "applied", "directive": payload.directive}


@router.get("/{user_id}")
def directive_status(user_id: int, db: Session = Depends(get_db)):
    s = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()
    return {
        "survival_mode": bool(s and s.survival_mode),
        "priority": s.priority if s else None,
        "quiet_hours": {"from": s.quiet_hours_from, "to": s.quiet_hours_to} if s and s.quiet_hours_from else None,
    }
