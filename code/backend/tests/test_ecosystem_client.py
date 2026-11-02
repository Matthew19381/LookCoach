"""Plan 3.8: data from ForgeBody / Dieta / affect via the hub, with offline fallback."""
import asyncio

import httpx

import backend.models  # noqa: F401
from backend.services.ecosystem_client import get_overview


def _hub(handler_events):
    def handler(request: httpx.Request) -> httpx.Response:
        q = dict(request.url.params)
        assert q["user_id"] == "1"
        key = (q.get("module"), q.get("event_type"))
        return httpx.Response(200, json=handler_events.get(key, []))

    return httpx.MockTransport(handler)


EVENTS = {
    ("forge-body", "measurement_logged"): [
        {"timestamp": "2026-09-01T08:00:00Z", "data": {"weight_kg": 82.0, "waist_cm": 86.0}},
        {"timestamp": "2026-10-30T08:00:00Z", "data": {"weight_kg": 80.0, "waist_cm": 84.0, "body_fat_pct": None}},
    ],
    ("forge-body", "workout_completed"): [{"data": {}}, {"data": {}}, {"data": {}}],
    ("dieta", "weight_logged"): [{"data": {"weight_kg": 81.0}}, {"data": {"weight_kg": 80.8}}],
    (None, None): [
        {"data": {}, "affect": {"stress": 4, "energy": 2, "mood": 3}},
        {"data": {}, "affect": {"stress": 5, "energy": 2}},
        {"data": {}},
    ],
}


def test_overview_from_hub_and_snapshot(db_session):
    data = asyncio.run(get_overview(db_session, 1, transport=_hub(EVENTS)))
    assert data["source"] == "hub"
    m = data["forge_body"]["measurements"]["values"]
    assert m["waist_cm"] == {"label": "Talia (cm)", "latest": 84.0, "trend": "spada"}
    assert "body_fat_pct" not in m  # None is not a measurement
    assert data["forge_body"]["workouts_last_7_days"] == 3
    assert data["dieta"]["weight"] == {"latest_kg": 80.8, "trend": "stabilnie", "entries": 2}
    assert data["affect_last_7_days"] == {"samples": 2, "stress": "wysoki", "energy": "niski", "mood": "średni"}


def test_hub_down_serves_last_snapshot(db_session):
    asyncio.run(get_overview(db_session, 1, transport=_hub(EVENTS)))

    def down(request):
        raise httpx.ConnectError("refused", request=request)

    data = asyncio.run(get_overview(db_session, 1, transport=httpx.MockTransport(down)))
    assert data["source"] == "cache"
    assert data["forge_body"]["workouts_last_7_days"] == 3


def test_hub_down_without_snapshot(db_session):
    def down(request):
        return httpx.Response(503)

    data = asyncio.run(get_overview(db_session, 1, transport=httpx.MockTransport(down)))
    assert data["source"] == "unavailable"


def test_empty_ecosystem(db_session):
    data = asyncio.run(get_overview(db_session, 1, transport=_hub({})))
    assert data["forge_body"]["measurements"] is None
    assert data["dieta"]["weight"] is None
    assert data["affect_last_7_days"] is None
