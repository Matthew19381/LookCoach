"""The user's own skincare routine and today's view (owner request 2026-10-15:
"tworzenie rutyny i podgląd co dzisiaj ma być"). Before, the routine page showed
a generated routine that could not be saved, and with an empty database the
hub's day plan got no skincare item at all."""

import tempfile
from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import get_db
from backend.models.base import Base
from backend.routers import consistency, directives, skincare, summary
from backend.services.routine_defaults import DEFAULT_STEPS, EVIDENCE

engine = create_engine(f"sqlite:///{tempfile.mktemp(suffix='.db')}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
Local = sessionmaker(bind=engine)

app = FastAPI()
app.include_router(skincare.router, prefix="/api/v1/skincare")
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

MONDAY = date(2026, 10, 12)


def _today(uid, day=MONDAY):
    return client.get("/api/v1/skincare/today", params={"user_id": uid, "date": day.isoformat()}).json()


def _slot(view, slot):
    return next(s for s in view["slots"] if s["slot"] == slot)


def _hub_items(uid, day=MONDAY):
    r = client.get("/api/v1/summary", params={"user_id": uid, "date": day.isoformat()})
    return r.json()["summary"]["suggested_items"]


def _save_default(uid):
    return client.post("/api/v1/skincare/my-routine/default", params={"user_id": uid}).json()


def test_every_default_step_has_a_source_and_rct_ones_a_link():
    for step in DEFAULT_STEPS:
        ev = EVIDENCE[step[2]]
        assert ev["ref"]
        if ev["level"].startswith("RCT"):
            assert ev["url"].startswith("https://")


def test_without_saved_routine_the_proposal_is_shown_but_nothing_is_planned():
    r = client.get("/api/v1/skincare/my-routine", params={"user_id": 50}).json()
    assert r["saved"] is False
    names = [s["name"] for s in r["steps"] if s["active"]]
    assert any("SPF 30+" in n for n in names)
    assert all(s["evidence"]["ref"] for s in r["steps"])
    assert not any(s["active"] for s in r["steps"] if s["evidence_key"] in ("retinol", "niacinamide"))

    view = _today(50)
    assert view["has_routine"] is False and all(s["steps"] == [] for s in view["slots"])
    assert _hub_items(50) == []  # no routine is pushed on anyone


def test_saving_the_default_plans_today_and_reaches_the_hub():
    r = _save_default(51)
    assert r["created"] is True and len(r["steps"]) == len(DEFAULT_STEPS)
    assert _save_default(51)["created"] is False  # second click changes nothing
    assert len(client.get("/api/v1/skincare/my-routine", params={"user_id": 51}).json()["steps"]) == len(DEFAULT_STEPS)

    view = _today(51)
    morning = [s["name"] for s in _slot(view, "morning")["steps"]]
    assert len(morning) == 2 and "SPF 30+" in morning[1]  # wash, then sunscreen; serum is off
    assert len(_slot(view, "evening")["steps"]) == 2  # retinol is off

    titles = [i["title"] for i in _hub_items(51)]
    assert len(titles) == 2
    assert titles == ["Pielęgnacja rano: Umyj twarz, Krem z filtrem SPF 30+",
                      "Pielęgnacja wieczorem: Umyj twarz łagodnym żelem, Krem nawilżający"]


def test_done_in_lookcoach_marks_the_slot_and_drops_it_from_the_hub():
    _save_default(52)
    today = date.today()
    client.post("/api/v1/consistency/adherence/log",
                params={"protocol_type": "skincare_morning", "completed": True, "user_id": 52})
    view = _today(52, today)
    assert _slot(view, "morning")["done"] is True and _slot(view, "evening")["done"] is False
    assert [i["complete_on"] for i in _hub_items(52, today)] == [["protocol_done:protocol_id=skincare_evening"]]


def test_hub_tick_shows_as_done_in_lookcoach(monkeypatch):
    monkeypatch.setenv("MODULE_KEY", "k")
    _save_default(53)
    today = date.today().isoformat()
    r = client.post("/api/v1/directives", headers={"X-Module-Key": "k"},
                    json={"directive": "plan_item_done", "enabled": True, "user_id": "53", "date": today,
                          "item_id": 1, "title": "x", "complete_on": ["protocol_done:protocol_id=skincare_evening"]})
    assert r.status_code == 200, r.text
    assert _slot(_today(53, date.today()), "evening")["done"] is True


def test_own_steps_weekdays_and_switching_off():
    uid = 54
    add = client.post("/api/v1/skincare/my-routine/steps", params={"user_id": uid},
                      json={"slot": "evening", "name": "Retinol", "weekdays": "02"})
    assert add.status_code == 201
    step = add.json()
    assert step["position"] == 0 and step["evidence"] is None
    client.post("/api/v1/skincare/my-routine/steps", params={"user_id": uid},
                json={"slot": "evening", "name": "Krem", "essential": True})

    assert [s["name"] for s in _slot(_today(uid, MONDAY), "evening")["steps"]] == ["Retinol", "Krem"]
    assert [s["name"] for s in _slot(_today(uid, MONDAY + timedelta(days=1)), "evening")["steps"]] == ["Krem"]
    # Only evening is planned: the hub gets no morning item
    assert [i["complete_on"][0].split("=")[1] for i in _hub_items(uid)] == ["skincare_evening"]

    r = client.patch(f"/api/v1/skincare/my-routine/steps/{step['id']}", params={"user_id": uid},
                     json={"active": False, "name": "  Retinol 0,3%  "})
    assert r.status_code == 200 and r.json()["name"] == "Retinol 0,3%" and r.json()["active"] is False
    assert [s["name"] for s in _slot(_today(uid), "evening")["steps"]] == ["Krem"]

    assert client.delete(f"/api/v1/skincare/my-routine/steps/{step['id']}", params={"user_id": uid}).status_code == 200
    # Someone else's step cannot be changed or deleted
    other = client.get("/api/v1/skincare/my-routine", params={"user_id": uid}).json()["steps"][0]["id"]
    assert client.delete(f"/api/v1/skincare/my-routine/steps/{other}", params={"user_id": 99}).status_code == 404
    assert client.patch(f"/api/v1/skincare/my-routine/steps/{other}", params={"user_id": 99},
                        json={"name": "x"}).status_code == 404
    # A user with own steps does not get the default on top
    assert _save_default(uid)["created"] is False


def test_all_steps_off_means_no_hub_item_even_if_tracked():
    uid = 55
    sid = client.post("/api/v1/skincare/my-routine/steps", params={"user_id": uid},
                      json={"slot": "morning", "name": "SPF"}).json()["id"]
    client.patch(f"/api/v1/skincare/my-routine/steps/{sid}", params={"user_id": uid}, json={"active": False})
    client.post("/api/v1/consistency/adherence/log",
                params={"protocol_type": "skincare_morning", "completed": True, "user_id": uid,
                        "date": (date.today() - timedelta(days=1)).isoformat()})
    assert _hub_items(uid, date.today()) == []


def test_survival_mode_keeps_only_essential_steps():
    uid = 56
    _save_default(uid)
    client.post("/api/v1/directives", json={"directive": "survival_mode", "enabled": True, "user_id": uid})
    view = _today(uid)
    assert view["survival_mode"] is True
    assert [s["essential"] for s in _slot(view, "morning")["steps"]] == [True]  # SPF only
    assert [s["essential"] for s in _slot(view, "evening")["steps"]] == [True]  # wash only
    items = _hub_items(uid)
    assert len(items) == 2 and items[0]["title"] == "Pielęgnacja rano (wersja bazowa): Krem z filtrem SPF 30+"
    assert all("(wersja bazowa)" in i["title"] and i["estimated_minutes"] == 2 for i in items)


def test_survival_mode_without_essential_steps_keeps_the_first_one():
    uid = 57
    for name in ("A", "B"):
        client.post("/api/v1/skincare/my-routine/steps", params={"user_id": uid}, json={"slot": "morning", "name": name})
    client.post("/api/v1/directives", json={"directive": "survival_mode", "enabled": True, "user_id": uid})
    assert [s["name"] for s in _slot(_today(uid), "morning")["steps"]] == ["A"]


def test_long_titles_are_capped():
    uid = 58
    client.post("/api/v1/skincare/my-routine/steps", params={"user_id": uid},
                json={"slot": "morning", "name": "Bardzo długi krok " * 10})
    title = _hub_items(uid)[0]["title"]
    assert len(title) <= summary.TITLE_MAX and title.endswith("…")


def test_bad_input_is_rejected():
    p = {"user_id": 59}
    assert client.post("/api/v1/skincare/my-routine/steps", params=p, json={"slot": "noon", "name": "x"}).status_code == 422
    assert client.post("/api/v1/skincare/my-routine/steps", params=p, json={"slot": "morning", "name": "  "}).status_code == 422
    assert client.post("/api/v1/skincare/my-routine/steps", params=p,
                       json={"slot": "morning", "name": "x", "weekdays": "17"}).status_code == 422
    assert client.get("/api/v1/skincare/today", params={**p, "date": "17.10.2026"}).status_code == 422
