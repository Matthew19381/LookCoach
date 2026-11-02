"""Hub day plan (2026-10-04): /summary offers tracked routines, /adherence/log
publishes protocol_done/protocol_skipped so the hub ticks them off itself."""

import tempfile
from datetime import date, datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import get_db
from backend.models.base import Base
from backend.models.directive_state import DirectiveState
from backend.models.outbox import OutboxEvent
from backend.routers import consistency, summary

engine = create_engine(f"sqlite:///{tempfile.mktemp(suffix='.db')}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
Local = sessionmaker(bind=engine)

app = FastAPI()
app.include_router(consistency.router, prefix="/api/v1/consistency")
app.include_router(summary.router, prefix="/api/v1")


def _db():
    db = Local()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _db
client = TestClient(app)


def _log(user_id, protocol, completed=True, day=None):
    params = {"protocol_type": protocol, "completed": completed, "user_id": user_id}
    if day:
        params["date"] = day
    r = client.post("/api/v1/consistency/adherence/log", params=params)
    assert r.status_code == 200, r.text


def _queued(user_id):
    db = Local()
    rows = db.query(OutboxEvent).filter(OutboxEvent.user_id == user_id).order_by(OutboxEvent.id).all()
    out = [(r.event_type, __import__("json").loads(r.data)["protocol_id"]) for r in rows]
    db.close()
    return out


def _suggested(user_id):
    return client.get("/api/v1/summary", params={"user_id": user_id}).json()["summary"]["suggested_items"]


def test_only_tracked_routines_not_done_today():
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    assert _suggested(501) == []  # nothing tracked -> nothing pushed into the plan

    _log(501, "skincare_morning", day=yesterday)
    _log(501, "skincare_evening", day=yesterday)
    items = _suggested(501)
    assert [i["title"] for i in items] == ["Pielęgnacja rano", "Pielęgnacja wieczorem"]
    assert items[0]["complete_on"] == ["protocol_done:protocol_id=skincare_morning"]
    assert _queued(501) == []  # back-filled days are not published

    _log(501, "skincare_morning")
    assert [i["title"] for i in _suggested(501)] == ["Pielęgnacja wieczorem"]
    assert _queued(501) == [("protocol_done", "skincare_morning")]


def test_skip_is_published_and_survival_shortens():
    _log(502, "skincare_evening", completed=False)
    assert _queued(502) == [("protocol_skipped", "skincare_evening")]

    db = Local()
    db.add(DirectiveState(user_id=503, survival_mode=True))
    db.commit()
    db.close()
    _log(503, "skincare_morning", day=(datetime.now() - timedelta(days=2)).date().isoformat())
    (item,) = [i for i in _suggested(503) if "rano" in i["title"]]
    assert item["title"] == "Pielęgnacja rano (wersja bazowa)" and item["estimated_minutes"] == 2


def test_without_key_events_stay_queued():
    # conftest blanks MODULE_KEY: delivery must not raise and must not lose the event
    _log(505, "skincare_morning")
    db = Local()
    row = db.query(OutboxEvent).filter(OutboxEvent.user_id == 505).one()
    assert row.status == "pending" and "MODULE_KEY" in (row.last_error or "")
    db.close()
