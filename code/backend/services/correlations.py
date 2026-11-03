"""Qualitative correlations between habits and observed state (plan 5.3).

"In sessions after weeks with regular skincare, skin was more often 'good'
(3 of 4 vs 1 of 3)." Counts, never a score of the person (LC-9), and always
the caveat that correlation is not causation. Nothing is said until both
compared groups have MIN_PER_GROUP photo sessions.

Sources:
- skincare routine adherence in the 14 days before each front photo (local),
- stress from `affect` on any module's events in the 3 days before (hub),
  passed in as `stress_by_day` so the engine stays testable and offline.
"""
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from ..models.analysis import Analysis
from ..models.consistency import AdherenceLog, ProtocolTypeEnum
from ..models.photo import Photo

MIN_PER_GROUP = 2
ADHERENCE_WINDOW = 14
REGULAR = 0.7
STRESS_WINDOW = 3
CAVEAT = "To zbieżność w Twoich danych, nie dowód przyczyny — przy małej liczbie sesji może być przypadkowa."

GOOD_SKIN = {"good"}
LOW_SWELLING = {"low"}


def _front_sessions(db: Session, user_id: int) -> list[tuple[datetime, dict]]:
    photos = (
        db.query(Photo)
        .filter(Photo.user_id == user_id, Photo.photo_type == "front", Photo.analysis_status == "done")
        .order_by(Photo.uploaded_at)
        .all()
    )
    out = []
    for photo in photos:
        analysis = db.query(Analysis).filter(Analysis.photo_id == photo.id).first()
        face = analysis.get_face_data() if analysis else {}
        if face and photo.uploaded_at is not None:
            out.append((photo.uploaded_at, face))
    return out


def _skincare_rate(db: Session, user_id: int, before: datetime) -> float | None:
    start = before - timedelta(days=ADHERENCE_WINDOW)
    logs = (
        db.query(AdherenceLog)
        .filter(
            AdherenceLog.user_id == user_id,
            AdherenceLog.protocol_type.in_([ProtocolTypeEnum.SKINCARE_MORNING, ProtocolTypeEnum.SKINCARE_EVENING]),
            AdherenceLog.date >= start, AdherenceLog.date < before,
        )
        .all()
    )
    if not logs:
        return None
    return sum(1 for log in logs if log.completed) / len(logs)


def _compare(groups: dict[str, list[bool]]) -> tuple[int, int, int, int] | None:
    a, b = groups.get("yes", []), groups.get("no", [])
    if len(a) < MIN_PER_GROUP or len(b) < MIN_PER_GROUP:
        return None
    return sum(a), len(a), sum(b), len(b)


SODIUM_WINDOW = 2
HIGH_SODIUM_MG = 2300


def find(db: Session, user_id: int, stress_by_day: dict[date, float] | None = None,
         sodium_by_day: dict[date, float] | None = None) -> dict:
    sessions = _front_sessions(db, user_id)
    insights = []

    # 1. skincare regularity -> skin state
    groups: dict[str, list[bool]] = {"yes": [], "no": []}
    for when, face in sessions:
        rate = _skincare_rate(db, user_id, when)
        status = (face.get("skin_quality") or {}).get("status")
        if rate is None or not status:
            continue
        groups["yes" if rate >= REGULAR else "no"].append(status in GOOD_SKIN)
    cmp = _compare(groups)
    if cmp and cmp[0] / cmp[1] != cmp[2] / cmp[3]:
        better = cmp[0] / cmp[1] > cmp[2] / cmp[3]
        insights.append({
            "area": "Skóra a regularna pielęgnacja",
            "text": (
                f"Po tygodniach z regularną pielęgnacją skóra była „dobra” w {cmp[0]} z {cmp[1]} sesji, "
                f"przy nieregularnej — w {cmp[2]} z {cmp[3]}."
                + ("" if better else " Tu regularność nie szła w parze z lepszym stanem — warto przyjrzeć się produktom.")
            ),
            "sessions": cmp[1] + cmp[3],
        })

    # 2. stress -> facial swelling
    if stress_by_day:
        groups = {"yes": [], "no": []}
        for when, face in sessions:
            days = [when.date() - timedelta(days=d) for d in range(1, STRESS_WINDOW + 1)]
            values = [stress_by_day[d] for d in days if d in stress_by_day]
            level = (face.get("swelling") or {}).get("level")
            if not values or not level:
                continue
            groups["yes" if sum(values) / len(values) >= 3.5 else "no"].append(level not in LOW_SWELLING)
        cmp = _compare(groups)
        if cmp and cmp[0] / cmp[1] != cmp[2] / cmp[3]:
            insights.append({
                "area": "Obrzęk a stres",
                "text": (
                    f"Po dniach z wysokim stresem obrzęk twarzy był średni lub wysoki w {cmp[0]} z {cmp[1]} sesji, "
                    f"po spokojniejszych — w {cmp[2]} z {cmp[3]}."
                ),
                "sessions": cmp[1] + cmp[3],
            })

    # 3. sodium (Dieta meal_logged) -> facial swelling
    if sodium_by_day:
        groups = {"yes": [], "no": []}
        for when, face in sessions:
            days = [when.date() - timedelta(days=d) for d in range(1, SODIUM_WINDOW + 1)]
            values = [sodium_by_day[d] for d in days if d in sodium_by_day]
            level = (face.get("swelling") or {}).get("level")
            if not values or not level:
                continue
            groups["yes" if max(values) >= HIGH_SODIUM_MG else "no"].append(level not in LOW_SWELLING)
        cmp = _compare(groups)
        if cmp and cmp[0] / cmp[1] != cmp[2] / cmp[3]:
            insights.append({
                "area": "Obrzęk a sód",
                "text": (
                    f"Po dniach z dużą ilością sodu (≥{HIGH_SODIUM_MG} mg wg Diety) obrzęk był średni lub wysoki "
                    f"w {cmp[0]} z {cmp[1]} sesji, po pozostałych — w {cmp[2]} z {cmp[3]}."
                ),
                "sessions": cmp[1] + cmp[3],
            })

    return {
        "insights": insights,
        "caveat": CAVEAT if insights else None,
        "front_sessions": len(sessions),
        "needed_per_group": MIN_PER_GROUP,
    }


def stress_from_events(events: list[dict]) -> dict[date, float]:
    """Hub events -> mean stress (1-5) per day from their `affect`."""
    per_day: dict[date, list[float]] = {}
    for e in events:
        affect = e.get("affect") or {}
        stress = affect.get("stress")
        ts = e.get("timestamp")
        if not isinstance(stress, (int, float)) or not ts:
            continue
        day = datetime.fromisoformat(str(ts).replace("Z", "+00:00")).date()
        per_day.setdefault(day, []).append(float(stress))
    return {d: sum(v) / len(v) for d, v in per_day.items()}


def sodium_from_events(events: list[dict]) -> dict[date, float]:
    """Dieta meal_logged events -> total sodium (mg) per day."""
    per_day: dict[date, float] = {}
    for e in events:
        if e.get("module") != "dieta" or e.get("event_type") != "meal_logged":
            continue
        data = e.get("data") or {}
        sodium = data.get("sodium_mg")
        raw_day = data.get("date") or e.get("timestamp")
        if not isinstance(sodium, (int, float)) or not raw_day:
            continue
        day = datetime.fromisoformat(str(raw_day).replace("Z", "+00:00")).date()
        per_day[day] = per_day.get(day, 0.0) + float(sodium)
    return per_day
