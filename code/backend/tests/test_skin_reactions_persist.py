"""F-1 (LC-2): logged skin reactions are stored and change tolerance/sensitivity.

Until 2026-09-27 log_reaction stored nothing and get_reaction_history returned
[], so tolerance was always "none" and the adaptive routine never adapted."""

import tempfile

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import get_db
from backend.models.base import Base
from backend.routers import skincare

engine = create_engine(f"sqlite:///{tempfile.mktemp(suffix='.db')}", connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
Local = sessionmaker(bind=engine)
app = FastAPI()
app.include_router(skincare.router, prefix="/api/v1/skincare")


def _db():
    db = Local()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _db
client = TestClient(app)


def test_reactions_raise_tolerance_level():
    ing = "Vitamin C 10-20%"
    assert client.get(f"/api/v1/skincare/tolerance/{ing}", params={"user_id": 5}).json()["tolerance_level"] == "none"
    for sev in ("high", "high"):
        r = client.post(
            "/api/v1/skincare/reaction/log",
            params={"ingredient": ing, "reaction": "redness", "severity": sev, "user_id": 5},
        )
        assert r.status_code == 200
    body = client.get(f"/api/v1/skincare/tolerance/{ing}", params={"user_id": 5}).json()
    assert body["tolerance_level"] == "high"
    # another user is unaffected
    assert client.get(f"/api/v1/skincare/tolerance/{ing}", params={"user_id": 6}).json()["tolerance_level"] == "none"
