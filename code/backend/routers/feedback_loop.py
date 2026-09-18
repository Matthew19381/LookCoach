from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from ..database import get_db
from ..services.feedback_loop import (
    SmartFeedbackLoop,
    FeedbackTriggerType,
    FeedbackActionType,
    FeedbackSeverity,
    create_feedback_loop_report,
)
from ..models.consistency import AdherenceLog

router = APIRouter()


@router.post("/analyze")
async def analyze_feedback_loop(
    progress_logs: Optional[List[Dict]] = Body(default=None),
    interaction_data: Optional[Dict] = Body(default=None),
    timeline_data: Optional[Dict] = Body(default=None),
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """
    Analyze feedback triggers and generate recommendations.
    
    This endpoint checks for:
    1. No measurable effects over time
    2. User antagonism signals (skip rate, negative feedback)
    """
    feedback_loop = SmartFeedbackLoop(db, user_id)
    
    # Get default data if not provided
    if progress_logs is None:
        # Get recent progress logs from database
        cutoff = datetime.now() - timedelta(days=30)  # Last 30 days
        logs = db.query(AdherenceLog).filter(
            AdherenceLog.user_id == user_id,
            AdherenceLog.date >= cutoff,
        ).order_by(AdherenceLog.date.desc()).all()
        
        progress_logs = [log.to_dict() for log in logs]
    
    if interaction_data is None:
        # Default interaction data (would come from user interaction tracking)
        interaction_data = {
            'skip_rate': 0.0,  # Would be calculated from user behavior
            'negative_feedback_count': 0,
            'failing_protocols': [],
        }
    
    if timeline_data is None:
        # Default timeline data
        timeline_data = {
            'expected_weekly_progress': 0.1,  # 10% per week
        }
    
    analysis = feedback_loop.analyze_feedback_loop(
        progress_logs=progress_logs,
        interaction_data=interaction_data,
        timeline_data=timeline_data,
    )
    
    return {
        "analysis": analysis,
        "report": create_feedback_loop_report(analysis),
    }


@router.post("/execute-action")
async def execute_feedback_action(
    action_type: str = Body(..., description="Type of action to execute"),
    context: Optional[Dict] = Body(default=None),
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """
    Execute a feedback action.
    
    Available actions:
    - reduce_protocols: Reduce number of active protocols
    - recompose_plan: Recompose plan using ROI Engine
    - pause_protocol: Temporarily pause specific protocol
    - adjust_timeline: Adjust expected timeline for effects
    - escalate_support: Escalate to human support
    """
    try:
        action = FeedbackActionType(action_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action_type: {action_type}. Available: {[a.value for a in FeedbackActionType]}"
        )
    
    feedback_loop = SmartFeedbackLoop(db, user_id)
    
    if context is None:
        context = {}
    
    result = feedback_loop.execute_feedback_action(action, context)
    
    return {
        "result": result,
        "success": result["success"],
        "message": result["message"],
    }


@router.get("/triggers")
async def get_feedback_triggers(
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """
    Get current feedback trigger status for all users.
    """
    feedback_loop = SmartFeedbackLoop(db, user_id)
    
    # Get current data
    cutoff = datetime.now() - timedelta(days=30)
    progress_logs = [log.to_dict() for log in db.query(AdherenceLog).filter(
        AdherenceLog.user_id == user_id,
        AdherenceLog.date >= cutoff,
    ).all()]
    
    interaction_data = {
        'skip_rate': 0.0,  # Would be calculated from actual user behavior
        'negative_feedback_count': 0,
        'failing_protocols': [],
    }
    
    timeline_data = {
        'expected_weekly_progress': 0.1,
    }
    
    analysis = feedback_loop.analyze_feedback_loop(
        progress_logs=progress_logs,
        interaction_data=interaction_data,
        timeline_data=timeline_data,
    )
    
    return {
        "triggers": analysis["triggers"],
        "overall_severity": analysis["overall_severity"].value,
        "has_triggers": len(analysis["triggers"]) > 0,
    }


@router.get("/report")
async def get_feedback_report(
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """
    Generate a human-readable feedback loop report.
    """
    # Get analysis data
    analysis_response = await analyze_feedback_loop(
        user_id=user_id,
        db=db,
    )
    
    return {
        "report": analysis_response["report"],
        "analysis": analysis_response["analysis"],
    }


@router.get("/thresholds")
async def get_feedback_thresholds():
    """
    Get current feedback loop thresholds and configuration.
    """
    return {
        "no_effects_threshold_days": SmartFeedbackLoop.NO_EFFECTS_THRESHOLD_DAYS,
        "skip_rate_threshold": SmartFeedbackLoop.SKIP_RATE_THRESHOLD,
        "negative_feedback_threshold": SmartFeedbackLoop.NEGATIVE_FEEDBACK_THRESHOLD,
        "multiple_failures_threshold": SmartFeedbackLoop.MULTIPLE_FAILURES_THRESHOLD,
        "available_actions": [action.value for action in FeedbackActionType],
        "available_triggers": [trigger.value for trigger in FeedbackTriggerType],
        "severity_levels": [severity.value for severity in FeedbackSeverity],
    }


@router.post("/thresholds")
async def update_feedback_thresholds(
    no_effects_threshold_days: Optional[int] = Body(default=None),
    skip_rate_threshold: Optional[float] = Body(default=None),
    negative_feedback_threshold: Optional[int] = Body(default=None),
    multiple_failures_threshold: Optional[int] = Body(default=None),
):
    """
    Update feedback loop thresholds.
    
    Note: This creates a new instance with updated thresholds.
    In production, this would update configuration in database.
    """
    # This is a simplified implementation
    # In production, you'd store these thresholds in the database
    return {
        "message": "Thresholds updated (simulation - actual persistence not implemented)",
        "updated_thresholds": {
            "no_effects_threshold_days": no_effects_threshold_days,
            "skip_rate_threshold": skip_rate_threshold,
            "negative_feedback_threshold": negative_feedback_threshold,
            "multiple_failures_threshold": multiple_failures_threshold,
        }
    }