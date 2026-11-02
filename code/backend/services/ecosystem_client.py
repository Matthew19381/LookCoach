"""Data from other modules, read through the hub (plan 3.8, D3).

LookCoach does not ask the user again for what other modules already know:
- ForgeBody `measurement_logged` (weight, body fat, waist...) and `workout_completed`,
- Dieta `weight_logged`,
- `affect` (mood/energy/stress 1-5) attached to any module's event (contract v2).

Source: hub `GET /api/v1/integrations/events` with this module's X-Module-Key
(System-Glowny H-5). The last good result is stored (EcosystemSnapshot) and
served when the hub is unreachable, marked as such.

Numbers here are the user's own measurements, shown as such - never turned
into a rating of the person (LC-9).
"""
import json
import os
from datetime import datetime, timedelta, timezone
from statistics import mean

import httpx
from sqlalchemy.orm import Session

from ..models.ecosystem_snapshot import EcosystemSnapshot

MEASUREMENT_FIELDS = ("weight_kg", "body_fat_pct", "waist_cm", "chest_cm", "hips_cm", "arm_cm", "thigh_cm")
FIELD_PL = {
    "weight_kg": "Waga (kg)",
    "body_fat_pct": "Tkanka tłuszczowa (%)",
    "waist_cm": "Talia (cm)",
    "chest_cm": "Klatka (cm)",
    "hips_cm": "Biodra (cm)",
    "arm_cm": "Ramię (cm)",
    "thigh_cm": "Udo (cm)",
}


def _hub_url() -> str:
    return os.getenv("SYSTEM_GLOWNY_HUB_URL", "http://localhost:8000").rstrip("/")


def _trend_word(first: float, last: float, tolerance: float) -> str:
    if last - first > tolerance:
        return "rośnie"
    if first - last > tolerance:
        return "spada"
    return "stabilnie"


def _measurements(events: list[dict]) -> dict | None:
    """Latest value + direction since the oldest event in the window, per field."""
    if not events:
        return None
    out = {}
    for field in MEASUREMENT_FIELDS:
        values = [e["data"][field] for e in events if isinstance(e.get("data", {}).get(field), (int, float))]
        if not values:
            continue
        tolerance = 0.5 if field != "body_fat_pct" else 0.3
        out[field] = {
            "label": FIELD_PL[field],
            "latest": values[-1],
            "trend": _trend_word(values[0], values[-1], tolerance) if len(values) > 1 else None,
        }
    return {"last_logged": events[-1].get("timestamp"), "values": out} if out else None


def _weights(events: list[dict]) -> dict | None:
    values = [e["data"]["weight_kg"] for e in events if isinstance(e.get("data", {}).get("weight_kg"), (int, float))]
    if not values:
        return None
    return {
        "latest_kg": values[-1],
        "trend": _trend_word(values[0], values[-1], 0.5) if len(values) > 1 else None,
        "entries": len(values),
    }


def _level(avg: float) -> str:
    return "niski" if avg < 2.5 else "średni" if avg < 3.5 else "wysoki"


def _affect(events: list[dict]) -> dict | None:
    snaps = [e["affect"] for e in events if isinstance(e.get("affect"), dict)]
    if not snaps:
        return None
    out = {"samples": len(snaps)}
    for key, label in (("stress", "stress"), ("energy", "energy"), ("mood", "mood")):
        vals = [s[key] for s in snaps if isinstance(s.get(key), (int, float))]
        if vals:
            out[label] = _level(mean(vals))
    return out


async def fetch_overview(user_id: int, transport: httpx.AsyncBaseTransport | None = None) -> dict:
    """Read the hub. Raises httpx.HTTPError on any hub/network problem."""
    now = datetime.now(timezone.utc)
    key = os.getenv("MODULE_KEY")
    headers = {"X-Module-Key": key} if key else {}

    async def events(client: httpx.AsyncClient, days: int, **params) -> list[dict]:
        query = {"user_id": str(user_id), "since": (now - timedelta(days=days)).isoformat(), "limit": 200, **params}
        resp = await client.get(f"{_hub_url()}/api/v1/integrations/events", params=query, headers=headers)
        resp.raise_for_status()
        return resp.json()

    async with httpx.AsyncClient(timeout=5.0, transport=transport) as client:
        measurements = await events(client, 120, module="forge-body", event_type="measurement_logged")
        workouts = await events(client, 7, module="forge-body", event_type="workout_completed")
        weights = await events(client, 60, module="dieta", event_type="weight_logged")
        recent = await events(client, 7)

    return {
        "forge_body": {
            "measurements": _measurements(measurements),
            "workouts_last_7_days": len(workouts),
        },
        "dieta": {"weight": _weights(weights)},
        "affect_last_7_days": _affect(recent),
    }


async def get_overview(db: Session, user_id: int, transport: httpx.AsyncBaseTransport | None = None) -> dict:
    """Fresh data from the hub, else the last snapshot, else 'unavailable'."""
    row = db.query(EcosystemSnapshot).filter(EcosystemSnapshot.user_id == user_id).first()
    try:
        data = await fetch_overview(user_id, transport=transport)
    except (httpx.HTTPError, ValueError) as e:
        if row:
            return {"source": "cache", "fetched_at": row.fetched_at.isoformat() if row.fetched_at else None,
                    "error": str(e)[:200], **json.loads(row.data)}
        return {"source": "unavailable", "error": str(e)[:200]}
    if not row:
        row = EcosystemSnapshot(user_id=user_id)
        db.add(row)
    row.data = json.dumps(data, ensure_ascii=False)
    row.fetched_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    return {"source": "hub", "fetched_at": row.fetched_at.isoformat(), **data}
