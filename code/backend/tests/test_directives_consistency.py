"""Consistency Tracker reads real adherence (was a placeholder returning []) and
the hub survival_mode directive forces the SURVIVAL level (INT-3)."""

import tempfile
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import get_db
from backend.models.base import Base
from backend.routers import consistency, directives
from backend.services.consistency_tracker import ConsistencyTracker, DifficultyLevel, ProtocolType

engine = create_engine(f"sqlite:///{tempfile.mktemp(suffix='.db')}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
Local = sessionmaker(bind=engine)

app = FastAPI()
app.include_router(consistency.router, prefix="/api/v1/consistency")
app.include_router(directives.router, prefix="/api/v1/directives")


def _db():
    db = Local()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _db
client = TestClient(app)


def _log(user_id, completed_flags, protocol="skincare_morning"):
    for i, done in enumerate(completed_flags):
        day = (datetime.now() - timedelta(days=len(completed_flags) - i)).date().isoformat()
        r = client.post(
            "/api/v1/consistency/adherence/log",
            params={"protocol_type": protocol, "completed": done, "date": day, "user_id": user_id},
        )
        assert r.status_code == 200, r.text


def test_low_adherence_now_reduces_difficulty():
    _log(11, [True, False, False, False, False, False, True, False])  # 25 %
    r = client.get(
        "/api/v1/consistency/difficulty/recommended",
        params={"protocol_type": "skincare_morning", "user_id": 11},
    ).json()
    assert r["needs_reduction"] is True and r["recommended_difficulty"] == "minimum"


def test_rate_comes_from_the_database():
    _log(12, [True, True, False, True])
    rate = client.get(
        "/api/v1/consistency/adherence/rate", params={"protocol_type": "skincare_morning", "user_id": 12}
    ).json()
    assert round(rate["adherence_rate"], 2) == 0.75


def test_consecutive_misses_trigger_pattern_alert():
    db = Local()
    _log(13, [True, False, False, False], protocol="sleep")
    alert, msg = ConsistencyTracker(db, 13).should_trigger_pattern_alert(ProtocolType.SLEEP)
    db.close()
    assert alert and "3 consecutive" in msg


def test_survival_directive_forces_survival_level():
    uid = 14
    body = {"directive": "survival_mode", "enabled": True, "user_id": uid}
    assert client.post("/api/v1/directives", json=body).status_code == 200
    r = client.get(
        "/api/v1/consistency/difficulty/recommended",
        params={"protocol_type": "skincare_morning", "user_id": uid},
    ).json()
    assert r["recommended_difficulty"] == DifficultyLevel.SURVIVAL.value
    assert r["minimum_effective_protocol"] == ["splash_water", "spf"]

    client.post("/api/v1/directives", json={**body, "enabled": False})
    assert client.get(f"/api/v1/directives/{uid}").json()["survival_mode"] is False


def test_hub_field_names_and_unknown_directive():
    client.post("/api/v1/directives", json={"directive": "quiet_hours", "from": "22:00", "to": "06:30", "user_id": 15})
    assert client.get("/api/v1/directives/15").json()["quiet_hours"] == {"from": "22:00", "to": "06:30"}
    assert client.post("/api/v1/directives", json={"directive": "x"}).status_code == 422
