import logging

from fastapi import APIRouter, BackgroundTasks, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..services.integration_publisher import IntegrationPublisher
from ..services.consistency_tracker import (
    ConsistencyTracker,
    ProtocolType,
    DifficultyLevel,
    calculate_overall_consistency_score,
)
from ..models.consistency import (
    AdherenceLog,
    ProtocolAdherence,
    ConsistencyMetrics,
    ProtocolTypeEnum,
    DifficultyLevelEnum,
    AdherenceLevelEnum,
)

router = APIRouter()
logger = logging.getLogger(__name__)



def _tracker(db: Session, user_id: int) -> ConsistencyTracker:
    """Per request: history comes from AdherenceLog, survival_mode from hub directives."""
    return ConsistencyTracker(db, user_id)


async def _publish_to_hub(user_id: int, protocol_type: str, completed: bool, difficulty_level: str) -> None:
    """INT-2: protocol_done / protocol_skipped to System-Glowny (its day plan ticks
    the routine off, its habit tracker counts it). Until 2026-10-04 the publisher
    existed but nothing called it. Never raises: logging here must not depend on the hub."""
    try:
        await IntegrationPublisher(timeout=3.0).publish(
            "protocol_done" if completed else "protocol_skipped",
            str(user_id),
            {"protocol_id": protocol_type, "difficulty_level": difficulty_level},
        )
    except Exception as e:  # no key, hub down, hub rejected - all non-fatal
        logger.warning("Hub event for %s not published: %s", protocol_type, e)


@router.post("/adherence/log")
async def log_adherence(
    protocol_type: str,
    completed: bool,
    background_tasks: BackgroundTasks,
    date: Optional[str] = None,
    difficulty_level: str = "full",
    notes: str = "",
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Log adherence for a protocol on a specific date."""
    try:
        pt = ProtocolType(protocol_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid protocol_type: {protocol_type}")

    try:
        dl = DifficultyLevel(difficulty_level)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty_level: {difficulty_level}")

    parsed_date = None
    if date:
        try:
            parsed_date = datetime.fromisoformat(date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format.")

    # Log using tracker (in-memory for now)
    _tracker(db, user_id).log_adherence(
        protocol_type=pt,
        completed=completed,
        date=parsed_date,
        difficulty_level=dl,
        notes=notes,
    )

    # Also persist to DB
    db_record = AdherenceLog(
        user_id=user_id,
        protocol_type=ProtocolTypeEnum(protocol_type),
        date=parsed_date or datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        completed=completed,
        difficulty_level=DifficultyLevelEnum(difficulty_level),
        notes=notes,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    # Only today's entries go to the hub: a back-filled day would tick today's
    # plan item, and the hub dedups by timestamp (two protocols of one past
    # day would collide on midnight).
    if parsed_date is None or parsed_date.date() == datetime.now().date():
        background_tasks.add_task(_publish_to_hub, user_id, protocol_type, completed, difficulty_level)

    return {"status": "logged", "record": db_record.to_dict()}


@router.get("/adherence/history")
async def get_adherence_history(
    protocol_type: str,
    days: int = Query(28, ge=1, le=365),
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get adherence history for a protocol type."""
    try:
        ProtocolType(protocol_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid protocol_type: {protocol_type}")

    cutoff = datetime.now() - timedelta(days=days)
    logs = db.query(AdherenceLog).filter(
        and_(
            AdherenceLog.user_id == user_id,
            AdherenceLog.protocol_type == ProtocolTypeEnum(protocol_type),
            AdherenceLog.date >= cutoff,
        )
    ).order_by(AdherenceLog.date.desc()).all()

    return {
        "protocol_type": protocol_type,
        "days": days,
        "logs": [log.to_dict() for log in logs],
    }


@router.get("/adherence/rate")
async def get_adherence_rate(
    protocol_type: str,
    days: int = Query(28, ge=1, le=365),
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Calculate adherence rate for a protocol type."""
    try:
        pt = ProtocolType(protocol_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid protocol_type: {protocol_type}")

    rate = _tracker(db, user_id).calculate_adherence_rate(pt, days)
    level = _tracker(db, user_id).get_adherence_level(rate)

    return {
        "protocol_type": protocol_type,
        "days": days,
        "adherence_rate": round(rate, 3),
        "adherence_level": level.value,
    }


@router.get("/difficulty/recommended")
async def get_recommended_difficulty(
    protocol_type: str,
    current_difficulty: str = "full",
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get recommended difficulty based on adherence."""
    try:
        pt = ProtocolType(protocol_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid protocol_type: {protocol_type}")

    try:
        cd = DifficultyLevel(current_difficulty)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid current_difficulty: {current_difficulty}")

    recommended = _tracker(db, user_id).get_recommended_difficulty(pt, cd)
    min_protocol = _tracker(db, user_id).get_minimum_effective_protocol(pt, recommended)

    return {
        "protocol_type": protocol_type,
        "current_difficulty": current_difficulty,
        "recommended_difficulty": recommended.value,
        "minimum_effective_protocol": min_protocol,
        "needs_reduction": recommended != DifficultyLevel.FULL,
    }


@router.get("/protocols/status")
async def get_all_protocols_status(
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get adherence status and recommended difficulty for all protocols."""
    status = _tracker(db, user_id).get_all_protocols_status()
    return {"protocols": status}


@router.get("/summary")
async def get_consistency_summary(
    days: int = Query(28, ge=7, le=90),
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get overall consistency summary across all protocols."""
    summary = _tracker(db, user_id).get_consistency_summary(days)
    return summary


@router.get("/minimum-effective/{protocol_type}")
async def get_minimum_effective_protocol(
    protocol_type: str,
    difficulty: str = "full",
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Get minimum effective protocol steps for a given difficulty."""
    try:
        pt = ProtocolType(protocol_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid protocol_type: {protocol_type}")

    try:
        dl = DifficultyLevel(difficulty)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid difficulty: {difficulty}")

    protocol = _tracker(db, user_id).get_minimum_effective_protocol(pt, dl)

    return {
        "protocol_type": protocol_type,
        "difficulty": difficulty,
        "minimum_effective_protocol": protocol,
    }


@router.post("/recalculate")
async def recalculate_metrics(
    days: int = Query(28, ge=7, le=90),
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Recalculate and persist aggregated adherence metrics."""
    cutoff = datetime.now() - timedelta(days=days)
    period_start = cutoff.replace(hour=0, minute=0, second=0, microsecond=0)
    period_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)

    protocol_rates = {}

    for pt_enum in ProtocolTypeEnum:
        logs = db.query(AdherenceLog).filter(
            and_(
                AdherenceLog.user_id == user_id,
                AdherenceLog.protocol_type == pt_enum,
                AdherenceLog.date >= cutoff,
            )
        ).all()

        total = len(logs)
        completed = sum(1 for log in logs if log.completed)
        rate = completed / total if total > 0 else 1.0
        protocol_rates[ProtocolType(pt_enum.value)] = rate

        # Calculate streaks
        consecutive_misses = 0
        current_streak = 0
        longest_streak = 0

        for log in sorted(logs, key=lambda x: x.date, reverse=True):
            if not log.completed:
                consecutive_misses += 1
                current_streak = 0
            else:
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)
                if consecutive_misses > 0:
                    break

        # Determine adherence level
        if rate >= 0.9:
            level = AdherenceLevelEnum.EXCELLENT
        elif rate >= 0.75:
            level = AdherenceLevelEnum.GOOD
        elif rate >= 0.5:
            level = AdherenceLevelEnum.MODERATE
        elif rate >= 0.25:
            level = AdherenceLevelEnum.LOW
        else:
            level = AdherenceLevelEnum.CRITICAL

        # Get current difficulty (from latest log or default)
        latest_log = db.query(AdherenceLog).filter(
            and_(
                AdherenceLog.user_id == user_id,
                AdherenceLog.protocol_type == pt_enum,
            )
        ).order_by(AdherenceLog.date.desc()).first()

        current_diff = DifficultyLevelEnum.FULL
        if latest_log:
            current_diff = latest_log.difficulty_level

        # Get recommended difficulty
        recommended_diff = _tracker(db, user_id).get_recommended_difficulty(
            ProtocolType(pt_enum.value),
            DifficultyLevel(current_diff.value),
        )

        # Upsert ProtocolAdherence
        existing = db.query(ProtocolAdherence).filter(
            and_(
                ProtocolAdherence.user_id == user_id,
                ProtocolAdherence.protocol_type == pt_enum,
                ProtocolAdherence.period_start == period_start,
            )
        ).first()

        if existing:
            existing.period_end = period_end
            existing.period_days = days
            existing.total_scheduled = total
            existing.total_completed = completed
            existing.adherence_rate = rate
            existing.adherence_level = level
            existing.current_difficulty = current_diff
            existing.recommended_difficulty = DifficultyLevelEnum(recommended_diff.value)
            existing.consecutive_misses = consecutive_misses
            existing.longest_streak = longest_streak
            existing.current_streak = current_streak
        else:
            new_metric = ProtocolAdherence(
                user_id=user_id,
                protocol_type=pt_enum,
                period_start=period_start,
                period_end=period_end,
                period_days=days,
                total_scheduled=total,
                total_completed=completed,
                adherence_rate=rate,
                adherence_level=level,
                current_difficulty=current_diff,
                recommended_difficulty=DifficultyLevelEnum(recommended_diff.value),
                consecutive_misses=consecutive_misses,
                longest_streak=longest_streak,
                current_streak=current_streak,
            )
            db.add(new_metric)

    # Calculate overall consistency
    overall_score = calculate_overall_consistency_score(protocol_rates)
    avg_adherence = sum(protocol_rates.values()) / len(protocol_rates)
    protocols_needing_reduction = sum(
        1 for r in protocol_rates.values() if r < 0.75
    )

    if avg_adherence >= 0.9:
        system_status = "thriving"
    elif avg_adherence >= 0.75:
        system_status = "stable"
    elif avg_adherence >= 0.5:
        system_status = "adjusting"
    elif avg_adherence >= 0.25:
        system_status = "minimum_effective"
    else:
        system_status = "survival"

    # Upsert ConsistencyMetrics
    existing_metrics = db.query(ConsistencyMetrics).filter(
        and_(
            ConsistencyMetrics.user_id == user_id,
            ConsistencyMetrics.period_start == period_start,
        )
    ).first()

    if existing_metrics:
        existing_metrics.period_end = period_end
        existing_metrics.period_days = days
        existing_metrics.overall_consistency_score = overall_score
        existing_metrics.system_status = system_status
        existing_metrics.protocols_tracked = len(protocol_rates)
        existing_metrics.protocols_needing_reduction = protocols_needing_reduction
        existing_metrics.average_adherence = avg_adherence
    else:
        new_metrics = ConsistencyMetrics(
            user_id=user_id,
            period_start=period_start,
            period_end=period_end,
            period_days=days,
            overall_consistency_score=overall_score,
            system_status=system_status,
            protocols_tracked=len(protocol_rates),
            protocols_needing_reduction=protocols_needing_reduction,
            average_adherence=avg_adherence,
        )
        db.add(new_metrics)

    db.commit()

    return {
        "status": "recalculated",
        "period_days": days,
        "overall_consistency_score": round(overall_score, 3),
        "system_status": system_status,
        "average_adherence": round(avg_adherence, 3),
        "protocols_needing_reduction": protocols_needing_reduction,
    }


@router.get("/pattern-alert")
async def check_pattern_alerts(
    user_id: int = 1,
    db: Session = Depends(get_db),
):
    """Check if any protocol adherence patterns warrant alert to Mentalność."""
    alerts = []

    for pt_enum in ProtocolTypeEnum:
        should_alert, message = _tracker(db, user_id).should_trigger_pattern_alert(
            ProtocolType(pt_enum.value)
        )
        if should_alert:
            alerts.append({
                "protocol_type": pt_enum.value,
                "message": message,
                "severity": "warning",
            })

    return {
        "alerts": alerts,
        "has_alerts": len(alerts) > 0,
    }