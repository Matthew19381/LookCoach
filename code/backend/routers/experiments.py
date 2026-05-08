from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()

# In-memory experiment storage (in production, would use database)
EXPERIMENTS = {}


class ExperimentCreate(BaseModel):
    template_id: str
    custom_name: str = None
    user_id: int = 1


class DailyLog(BaseModel):
    experiment_id: str
    day: int
    rating: int  # 1-10
    notes: str = ""


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
async def start_experiment(body: ExperimentCreate):
    from ..services.experiment_engine import PersonalExperimentEngine
    result = PersonalExperimentEngine.start_experiment(
        body.template_id, body.user_id, body.custom_name
    )
    if "error" in result:
        raise HTTPException(400, result["error"])

    # Store in memory (in production: save to DB)
    EXPERIMENTS[result["id"]] = result
    return result


@router.get("/{experiment_id}")
async def get_experiment(experiment_id: str):
    if experiment_id not in EXPERIMENTS:
        raise HTTPException(404, "Experiment not found")
    return EXPERIMENTS[experiment_id]


@router.post("/log")
async def log_daily(body: DailyLog):
    if body.experiment_id not in EXPERIMENTS:
        raise HTTPException(404, "Experiment not found")

    experiment = EXPERIMENTS[body.experiment_id]
    from ..services.experiment_engine import PersonalExperimentEngine
    updated = PersonalExperimentEngine.log_daily(
        experiment, body.day, body.rating, body.notes
    )
    EXPERIMENTS[body.experiment_id] = updated
    return {"message": "Logged", "day": body.day}


@router.get("/{experiment_id}/results")
async def get_results(experiment_id: str):
    if experiment_id not in EXPERIMENTS:
        raise HTTPException(404, "Experiment not found")

    experiment = EXPERIMENTS[experiment_id]
    from ..services.experiment_engine import PersonalExperimentEngine
    return PersonalExperimentEngine.analyze_results(experiment)


@router.get("/active")
async def get_active_experiments(user_id: int = 1):
    return [
        exp for exp in EXPERIMENTS.values()
        if exp["user_id"] == user_id and exp["status"] == "active"
    ]


@router.post("/{experiment_id}/finish")
async def finish_experiment(experiment_id: str):
    if experiment_id not in EXPERIMENTS:
        raise HTTPException(404, "Experiment not found")

    EXPERIMENTS[experiment_id]["status"] = "completed"
    from ..services.experiment_engine import PersonalExperimentEngine
    return PersonalExperimentEngine.analyze_results(EXPERIMENTS[experiment_id])
