"""The user's own skincare routine and what it asks for on a given day
(owner request 2026-10-15). Shared by routers/skincare.py (LookCoach view)
and routers/summary.py (items for the hub's day plan)."""

from datetime import date as date_type
from datetime import datetime, time, timedelta

from sqlalchemy.orm import Session

from ..models.consistency import AdherenceLog, ProtocolTypeEnum
from ..models.directive_state import DirectiveState
from ..models.routine_step import RoutineStep
from .routine_defaults import DEFAULT_STEPS, EVIDENCE

SLOTS = {"morning": "skincare_morning", "evening": "skincare_evening"}


def step_out(row: RoutineStep) -> dict:
    return {"id": row.id, "slot": row.slot, "position": row.position, "name": row.name,
            "product_id": row.product_id, "weekdays": row.weekdays, "essential": row.essential,
            "active": row.active, "note": row.note, "evidence_key": row.evidence_key,
            "evidence": EVIDENCE.get(row.evidence_key or "")}


def default_out() -> list[dict]:
    """The proposal, shaped like saved steps but without ids."""
    out, pos = [], {}
    for slot, name, key, essential, active, weekdays, note in DEFAULT_STEPS:
        pos[slot] = pos.get(slot, -1) + 1
        out.append({"id": None, "slot": slot, "position": pos[slot], "name": name, "product_id": None,
                    "weekdays": weekdays, "essential": essential, "active": active, "note": note,
                    "evidence_key": key, "evidence": EVIDENCE[key]})
    return out


def user_steps(db: Session, user_id: int) -> list[RoutineStep]:
    return (db.query(RoutineStep).filter(RoutineStep.user_id == user_id)
            .order_by(RoutineStep.slot.desc(), RoutineStep.position, RoutineStep.id).all())  # morning first


def create_default(db: Session, user_id: int) -> bool:
    """Save the proposal as the user's routine; never touches an existing one."""
    if db.query(RoutineStep).filter(RoutineStep.user_id == user_id).first():
        return False
    for s in default_out():
        db.add(RoutineStep(user_id=user_id, slot=s["slot"], position=s["position"], name=s["name"],
                           weekdays=s["weekdays"], essential=s["essential"], active=s["active"], note=s["note"],
                           evidence_key=s["evidence_key"]))
    db.commit()
    return True


def survival_mode(db: Session, user_id: int) -> bool:
    state = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()
    return bool(state and state.survival_mode)


def steps_for_day(steps: list, day: date_type, survival: bool) -> dict[str, list]:
    """Active steps planned for the weekday; in survival mode only the essential
    ones (or the first step when none is marked)."""
    out = {}
    for slot in SLOTS:
        planned = [s for s in steps if s.slot == slot and s.active and str(day.weekday()) in (s.weekdays or "")]
        if survival and planned:
            planned = [s for s in planned if s.essential] or planned[:1]
        out[slot] = planned
    return out


def done_on(db: Session, user_id: int, day: date_type) -> set[str]:
    start = datetime.combine(day, time.min)
    rows = db.query(AdherenceLog).filter(
        AdherenceLog.user_id == user_id,
        AdherenceLog.protocol_type.in_([ProtocolTypeEnum(p) for p in SLOTS.values()]),
        AdherenceLog.completed.is_(True),
        AdherenceLog.date >= start, AdherenceLog.date < start + timedelta(days=1),
    ).all()
    return {r.protocol_type.value for r in rows}
