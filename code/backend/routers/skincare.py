from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.skincare_engine import SkincareEngine

router = APIRouter()

SKINCARE_ENGINE = SkincareEngine()


@router.get("/routine")
async def get_skincare_routine(
    user_id: int = 1,
    db: Session = Depends(get_db),
    include_adaptations: bool = Query(True, description="Include skin reaction adaptations"),
    include_rotation: bool = Query(True, description="Include ingredient rotation recommendations"),
    include_conflicts: bool = Query(True, description="Include ingredient conflict checks"),
    include_evidence: bool = Query(True, description="Include evidence summary"),
):
    # Simplified - in full version would fetch user analysis from DB
    skin_analysis = {"skin_type": "combination", "problems": []}
    lifestyle = {"sleep": 7, "stress": 5}

    routine = SKINCARE_ENGINE.generate_adaptive_routine(
        skin_analysis=skin_analysis,
        lifestyle=lifestyle
    )

    if include_conflicts:
        routine["conflicts"] = SKINCARE_ENGINE.check_ingredient_conflicts(routine)

    if include_evidence:
        routine["evidence_summary"] = SKINCARE_ENGINE.get_evidence_summary(routine)

    return routine


@router.post("/routine/adaptive")
async def get_adaptive_skincare_routine(
    skin_analysis: dict,
    lifestyle: dict,
    current_routine: dict = None,
    reaction_history: list = None,
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Generate adaptive routine with full context."""
    engine = SkincareEngine(db_session=db, user_id=user_id)

    routine = engine.generate_adaptive_routine(
        skin_analysis=skin_analysis,
        lifestyle=lifestyle,
        reaction_history=reaction_history,
        current_routine=current_routine
    )

    routine["conflicts"] = engine.check_ingredient_conflicts(routine)
    routine["evidence_summary"] = engine.get_evidence_summary(routine)

    return routine


@router.post("/reaction/log")
async def log_skin_reaction(
    ingredient: str,
    reaction: str,
    severity: str,
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Log a skin reaction to an ingredient."""
    engine = SkincareEngine(db_session=db, user_id=user_id)
    record = engine.reaction_tracker.log_reaction(ingredient, reaction, severity)
    return {"status": "logged", "record": record}


@router.get("/rotation/recommendations")
async def get_rotation_recommendations(
    current_routine: dict,
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get ingredient rotation recommendations for current routine."""
    engine = SkincareEngine(db_session=db, user_id=user_id)
    recommendations = engine.rotation_manager.get_rotation_recommendations(current_routine)
    return {"recommendations": recommendations}


@router.get("/tolerance/{ingredient}")
async def get_ingredient_tolerance(
    ingredient: str,
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get tolerance level for a specific ingredient."""
    engine = SkincareEngine(db_session=db, user_id=user_id)
    tolerance = engine.reaction_tracker.get_tolerance_level(ingredient)
    overall = engine.reaction_tracker.get_overall_sensitivity()
    return {
        "ingredient": ingredient,
        "tolerance_level": tolerance,
        "overall_sensitivity": overall
    }