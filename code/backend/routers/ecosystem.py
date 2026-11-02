"""Plan 3.8 / 3.12: what other modules know about the user, and the state of the hub link."""
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.directive_state import DirectiveState
from ..services import outbox
from ..services.ecosystem_client import get_overview
from ..services.ecosystem_dispatch import dispatch_needs, needs_overview

router = APIRouter()


@router.get("/overview")
async def ecosystem_overview(user_id: int = 1, db: Session = Depends(get_db)):
    return await get_overview(db, user_id)


@router.get("/connection")
def connection_status(user_id: int = 1, db: Session = Depends(get_db)):
    """'Połączenia' panel: queued/failed events, last ones sent, hub directives in force."""
    state = db.query(DirectiveState).filter(DirectiveState.user_id == user_id).first()
    return {
        "outbox": outbox.status_summary(db, user_id),
        "directives": {
            "survival_mode": bool(state and state.survival_mode),
            "priority": state.priority if state else None,
            "quiet_hours": (
                {"from": state.quiet_hours_from, "to": state.quiet_hours_to}
                if state and state.quiet_hours_from else None
            ),
        },
    }


@router.get("/needs")
def get_needs(user_id: int = 1, db: Session = Depends(get_db)):
    """What LookCoach asks ForgeBody / Dieta for (LC-4: needs, not plans)."""
    return needs_overview(db, user_id)


@router.post("/needs/send")
def send_needs(background_tasks: BackgroundTasks, force: bool = False, user_id: int = 1,
               db: Session = Depends(get_db)):
    queued = dispatch_needs(db, user_id, force=force)
    if queued:
        background_tasks.add_task(outbox.deliver_in_new_session, db.get_bind())
    return {"queued": queued}
