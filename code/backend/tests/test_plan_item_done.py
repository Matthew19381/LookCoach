"""A routine ticked in the hub's day plan becomes an adherence entry here
(directive plan_item_done, 2026-10-15). Before, the tick stayed in the hub."""

import tempfile
from datetime import date, datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import get_db
from backend.models.base import Base
from backend.models.consistency import AdherenceLog
from backend.routers import consistency, directives, summary

engine = create_engine(f"sqlite:///{tempfile.mktemp(suffix='.db')}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
Local = sessionmaker(bind=engine)

app = FastAPI()
app.include_router(consistency.router, prefix="/api/v1/consistency")
app.include_router(directives.router, prefix="/api/v1/directives")
app.include_router(summary.router, prefix="/api/v1")


def _db():
    db = Local()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _db
client = TestClient(app)

KEY = "klucz-testowy"
TODAY = date.today().isoformat()


@pytest.fixture(autouse=True)
def module_key(monkeypatch):
    monkeypatch.setenv("MODULE_KEY", KEY)


@pytest.fixture()
def published(monkeypatch):
    """Record every event LookCoach would send to the hub."""
    sent = []

    class Recorder:
        def __init__(self, *a, **k):
            pass

        async def publish(self, event_type, user_id, payload, timestamp=None):
            sent.append((event_type, payload))

    monkeypatch.setattr(consistency, "IntegrationPublisher", Recorder)
    return sent


def _tick(user_id, enabled=True, protocol="skincare_morning", day=TODAY, key=KEY, item_id=7):
    return client.post(
        "/api/v1/directives",
        json={"directive": "plan_item_done", "enabled": enabled, "user_id": str(user_id), "date": day,
              "item_id": item_id, "title": "Pielęgnacja rano",
              "complete_on": [f"protocol_done:protocol_id={protocol}"]},
        headers={"X-Module-Key": key} if key else {},
    )


def _logs(user_id, protocol="skincare_morning"):
    with Local() as db:
        return [(l.completed, l.notes, l.difficulty_level.value) for l in db.query(AdherenceLog).filter(
            AdherenceLog.user_id == user_id, AdherenceLog.protocol_type == protocol).all()]


def _history(user_id):
    return client.get("/api/v1/consistency/adherence/history",
                      params={"protocol_type": "skincare_morning", "user_id": user_id}).json()


def _suggested_titles(user_id):
    items = client.get("/api/v1/summary", params={"user_id": user_id}).json()["summary"]["suggested_items"]
    return [i["title"] for i in items]


def test_tick_in_hub_becomes_entry_and_nothing_goes_back(published):
    # Routine tracked yesterday -> the hub shows it today
    client.post("/api/v1/consistency/adherence/log",
                params={"protocol_type": "skincare_morning", "completed": True, "user_id": 31,
                        "date": (date.today() - timedelta(days=1)).isoformat()})
    assert "Pielęgnacja rano" in _suggested_titles(31)

    r = _tick(31)
    assert r.status_code == 200 and r.json()["changed"] == 1, r.text
    assert (True, "plan dnia huba #7", "full") in _logs(31)
    assert "Pielęgnacja rano" not in _suggested_titles(31)  # done today
    assert len(_history(31)["logs"]) == 2  # trackers see the hub tick
    assert published == []  # no protocol_done echo to the hub


def test_second_tick_or_entry_from_lookcoach_is_not_doubled(published):
    client.post("/api/v1/consistency/adherence/log",
                params={"protocol_type": "skincare_morning", "completed": True, "user_id": 32})
    assert _tick(32).json()["changed"] == 0
    assert _tick(32).json()["changed"] == 0
    assert len(_logs(32)) == 1


def test_untick_removes_only_the_hub_entry():
    _tick(33, protocol="skincare_evening")
    assert len(_logs(33, "skincare_evening")) == 1
    r = _tick(33, enabled=False, protocol="skincare_evening")
    assert r.status_code == 200 and r.json()["changed"] == 1
    assert _logs(33, "skincare_evening") == []

    # An entry made in LookCoach itself survives an untick in the hub
    client.post("/api/v1/consistency/adherence/log",
                params={"protocol_type": "skincare_evening", "completed": True, "user_id": 33})
    _tick(33, enabled=False, protocol="skincare_evening")
    assert len(_logs(33, "skincare_evening")) == 1


def test_survival_mode_logs_survival_level():
    client.post("/api/v1/directives", json={"directive": "survival_mode", "enabled": True, "user_id": 34})
    _tick(34)
    assert _logs(34)[0][2] == "survival"


def test_past_day_from_hub_lands_on_that_day():
    day = (date.today() - timedelta(days=2)).isoformat()
    _tick(35, day=day)
    with Local() as db:
        row = db.query(AdherenceLog).filter(AdherenceLog.user_id == 35).one()
    assert row.date.replace(tzinfo=None) == datetime.fromisoformat(day)


@pytest.mark.parametrize("key", [None, "zly-klucz"])
def test_without_the_module_key_nothing_is_written(key):
    r = _tick(36, key=key)
    assert r.status_code == 401
    assert _logs(36) == []


def test_unknown_protocol_or_bad_date_is_rejected():
    assert _tick(37, protocol="training").status_code == 422  # not a routine the hub plan offers
    assert _tick(37, protocol="nie-ma-takiej").status_code == 422
    assert _tick(37, day="15.10.2026").status_code == 422


def test_existing_directives_still_work_without_key(monkeypatch):
    r = client.post("/api/v1/directives", json={"directive": "priority", "value": "skóra", "user_id": 38})
    assert r.status_code == 200
