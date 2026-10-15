"""INT-3: directives from the System-Główny hub.

Hub contract: {"directive", "enabled", "value", "from", "to"}.
survival_mode sets every protocol to the SURVIVAL level of the Consistency
Tracker (e.g. skincare = rinse + SPF) until the hub switches it off.

plan_item_done (2026-10-15, hub contract INTEGRACJA-MODULOW.md §1.3a): a routine
ticked in the hub's day plan becomes an adherence entry here - before, a tick in
the hub never reached LookCoach and its trackers stayed empty. Unticking removes
only the entry the hub created. No protocol_done goes back: the hub item is done.
"""
from datetime import date as date_type
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.consistency import AdherenceLog, DifficultyLevelEnum, ProtocolTypeEnum
from ..models.directive_state import DirectiveState
from .integration import _verify_module_key
from .summary import ROUTINES  # the only routines the hub plan offers

router = APIRouter()

KNOWN = {"survival_mode", "priority", "quiet_hours", "plan_item_done"}
HUB_NOTE = "plan dnia huba"
_TOKEN_PREFIX = "protocol_done:protocol_id="


class DirectivePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    directive: str
    user_id: int = 1
    enabled: bool | None = None
    value: str | None = None
    from_: str | None = Field(None, alias="from")
    to: str | None = None
    # plan_item_done
    date: str | None = None
    item_id: int | None = None
    complete_on: list[str] = []


def _protocols(tokens: list[str]) -> list[ProtocolTypeEnum]:
    out = []
    for token in tokens:
        name = token.removeprefix(_TOKEN_PREFIX)
        if token.startswith(_TOKEN_PREFIX) and name in ROUTINES:
            out.append(ProtocolTypeEnum(name))
    return out


def _plan_item_done(payload: DirectivePayload, db: Session) -> dict:
    protocols = _protocols(payload.complete_on)
    if not protocols:
        raise HTTPException(status_code=422, detail="complete_on names no LookCoach protocol")
    try:
        day = date_type.fromisoformat(payload.date) if payload.date else date_type.today()
    except ValueError:
        raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD")
    start = datetime.combine(day, datetime.min.time())
    state = db.query(DirectiveState).filter(DirectiveState.user_id == payload.user_id).first()
    level = DifficultyLevelEnum.SURVIVAL if state and state.survival_mode else DifficultyLevelEnum.FULL
    note = f"{HUB_NOTE} #{payload.item_id}" if payload.item_id is not None else HUB_NOTE
    changed = 0
    for protocol in protocols:
        logs = db.query(AdherenceLog).filter(
            AdherenceLog.user_id == payload.user_id,
            AdherenceLog.protocol_type == protocol,
            AdherenceLog.date == start,
        ).all()
        if payload.enabled is not False:
            if not any(log.completed for log in logs):  # logged in LookCoach already -> keep one entry
                db.add(AdherenceLog(user_id=payload.user_id, protocol_type=protocol, date=start,
                                    completed=True, difficulty_level=level, notes=note))
                changed += 1
        else:
            for log in logs:
                if (log.notes or "").startswith(HUB_NOTE):
                    db.delete(log)
                    changed += 1
    db.commit()
    return {"status": "applied", "directive": "plan_item_done", "changed": changed}


@router.post("")
def apply_directive(
    payload: DirectivePayload,
    x_module_key: str | None = Header(None),
    db: Session = Depends(get_db),
):
    if payload.directive not in KNOWN:
        raise HTTPException(status_code=422, detail=f"Unknown directive: {payload.directive}")
    if payload.directive == "plan_item_done":
        # Writes the owner's data, so only the hub (holder of this module's key) may send it
        _verify_module_key(x_module_key)
        return _plan_item_done(payload, db)
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
