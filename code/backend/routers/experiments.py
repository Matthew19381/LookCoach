import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.experiment import Experiment

router = APIRouter()


class ExperimentCreate(BaseModel):
    template_id: str
    custom_name: str = None
    user_id: int = 1


class DailyLog(BaseModel):
    experiment_id: str
    day: int
    rating: int  # 1-10
    notes: str = ""


def _get_row_or_404(db: Session, experiment_id: str) -> Experiment:
    row = db.query(Experiment).filter(Experiment.experiment_id == experiment_id).first()
    if not row:
        raise HTTPException(404, "Experiment not found")
    return row


@router.get("/templates")
async def get_templates():
    from ..services.experiment_engine import PersonalExperimentEngine
    return PersonalExperimentEngine.get_templates()


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    from ..services.experiment_engine import PersonalExperimentEngine
    template = PersonalExperimentEngine.get_template(template_id)
    if not template:
        raise HTTPException(404, "Template not found")
    return template


@router.post("/start")
async def start_experiment(body: ExperimentCreate, db: Session = Depends(get_db)):
    from ..services.experiment_engine import PersonalExperimentEngine
    result = PersonalExperimentEngine.start_experiment(
        body.template_id, body.user_id, body.custom_name
    )
    if "error" in result:
        raise HTTPException(400, result["error"])

    row = Experiment(
        experiment_id=result["id"],
        user_id=body.user_id,
        template_id=result["template_id"],
        name=result["name"],
        status=result["status"],
        data=json.loads(json.dumps(result)),
    )
    db.add(row)
    db.commit()
    return result


@router.get("/active")
async def get_active_experiments(user_id: int = 1, db: Session = Depends(get_db)):
    rows = (
        db.query(Experiment)
        .filter(Experiment.user_id == user_id)
        .filter(Experiment.status == "active")
        .all()
    )
    return [row.data for row in rows]


@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    return _get_row_or_404(db, experiment_id).data


@router.post("/log")
async def log_daily(body: DailyLog, db: Session = Depends(get_db)):
    row = _get_row_or_404(db, body.experiment_id)

    from ..services.experiment_engine import PersonalExperimentEngine
    # Copy BEFORE the engine mutates: SQLAlchemy skips the UPDATE if the
    # committed snapshot object is mutated in place and then reassigned.
    data = json.loads(json.dumps(row.data))
    updated = PersonalExperimentEngine.log_daily(data, body.day, body.rating, body.notes)
    row.data = updated
    db.commit()
    return {"message": "Logged", "day": body.day}


@router.get("/{experiment_id}/results")
async def get_results(experiment_id: str, db: Session = Depends(get_db)):
    row = _get_row_or_404(db, experiment_id)

    from ..services.experiment_engine import PersonalExperimentEngine
    return PersonalExperimentEngine.analyze_results(row.data)


@router.post("/{experiment_id}/finish")
async def finish_experiment(experiment_id: str, db: Session = Depends(get_db)):
    row = _get_row_or_404(db, experiment_id)

    from ..services.experiment_engine import PersonalExperimentEngine
    updated = PersonalExperimentEngine.analyze_results(row.data)
    data = dict(row.data)
    if "error" not in updated:
        data["results"] = updated
    data["status"] = "completed"
    row.data = data
    row.status = "completed"
    db.commit()
    return updated
