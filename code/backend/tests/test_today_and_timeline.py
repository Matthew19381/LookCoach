"""Plan 5.4 ('Dziś') and 5.1 (state timeline in words)."""
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.models  # noqa: F401
from backend.database import get_db
from backend.models.analysis import Analysis
from backend.models.base import Base
from backend.models.directive_state import DirectiveState
from backend.models.photo import Photo
from backend.routers import progress, today

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
Local = sessionmaker(bind=engine)
app = FastAPI()
app.include_router(today.router, prefix="/api/v1/today")
app.include_router(progress.router, prefix="/api/v1/progress")


def _db():
    db = Local()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _db
client = TestClient(app)


def _analysed(user_id, ptype, days_ago, face=None):
    db = Local()
    photo = Photo(user_id=user_id, photo_type=ptype, file_path="uploads/t.jpg", analysis_status="done",
                  uploaded_at=datetime.now() - timedelta(days=days_ago))
    db.add(photo)
    db.commit()
    a = Analysis(photo_id=photo.id)
    a.set_face_data(face or {})
    db.add(a)
    db.commit()
    db.close()


def test_today_without_photos():
    data = client.get("/api/v1/today?user_id=701").json()
    assert data["has_photos"] is False and data["actions"] == [] and data["state"] == {}
    assert data["wellbeing"]["level"] == "ok"


def test_today_with_old_photos_suggests_session_and_shows_state():
    _analysed(702, "front", 20, {"swelling": {"level": "low"}})
    db = Local()
    db.add(DirectiveState(user_id=702, priority="skincare"))
    db.commit()
    db.close()
    data = client.get("/api/v1/today?user_id=702").json()
    assert data["next_photos_in_days"] == 0
    assert any(a["title"].startswith("Zdjęcia kontrolne") for a in data["actions"])
    assert data["state"]["Obrzęk twarzy"] == "niski"
    assert data["directives"]["priority"] == "skincare"
    assert data["ecosystem"] is None  # no hub call on the start page


def test_state_timeline_in_words():
    _analysed(703, "front", 30, {"swelling": {"level": "medium"}})
    _analysed(703, "front", 2, {"swelling": {"level": "low"}})
    data = client.get("/api/v1/progress/states?user_id=703").json()
    assert data["areas"] == ["Obrzęk twarzy"]
    assert [s["labels"]["Obrzęk twarzy"] for s in data["sessions"]] == ["średni", "niski"]
