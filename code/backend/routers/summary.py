import json
from datetime import date as date_type

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..database import get_db
from ..models.analysis import Analysis
from ..models.photo import Photo
from ..models.recommendation import Recommendation
from ..models.integration_event import IntegrationEvent

router = APIRouter()


@router.get("/summary")
async def get_summary(
    user_id: str = Query(...),
    date: str = Query(None),
    db: Session = Depends(get_db),
):
    """System-Główny integration contract: cross-module status snapshot."""
    target_date = date or date_type.today().isoformat()

    try:
        numeric_user_id = int(user_id)
    except ValueError:
        numeric_user_id = -1

    photos_analyzed_today = (
        db.query(Analysis)
        .join(Photo, Analysis.photo_id == Photo.id)
        .filter(Photo.user_id == numeric_user_id)
        .filter(func.date(Analysis.created_at) == target_date)
        .count()
    )

    active_recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == numeric_user_id)
        .filter(Recommendation.is_done == "N")
        .count()
    )

    focus_area = None
    latest_analysis = (
        db.query(Analysis)
        .join(Photo, Analysis.photo_id == Photo.id)
        .filter(Photo.user_id == numeric_user_id)
        .order_by(Analysis.created_at.desc())
        .first()
    )
    if latest_analysis and latest_analysis.attractiveness_lever:
        try:
            lever = json.loads(latest_analysis.attractiveness_lever)
            focus_area = lever.get("primary_lever")
        except (ValueError, TypeError):
            focus_area = None

    events = (
        db.query(IntegrationEvent)
        .filter(IntegrationEvent.user_id == user_id)
        .order_by(IntegrationEvent.received_at.desc())
        .limit(20)
        .all()
    )

    return {
        "module": "lookcoach",
        "user_id": user_id,
        "date": target_date,
        "summary": {
            "photos_analyzed_today": photos_analyzed_today,
            "active_recommendations": active_recommendations,
            "focus_area": focus_area,
        },
        "events": [
            {
                "source_module": e.source_module,
                "event_type": e.event_type,
                "timestamp": e.timestamp,
                "payload": json.loads(e.payload) if e.payload else {},
            }
            for e in events
        ],
    }
