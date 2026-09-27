"""My products: INCI parsing, actives, conflicts, tolerance, usage -> rotation, label scan (owner request 2026-09-27)."""

import tempfile
from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import get_db
from backend.models.base import Base
from backend.routers import skincare
from backend.services.ingredient_label import analyze_ingredients, parse_inci

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

RETINOL = "Ingredients: Aqua, Glycerin, Squalane, Retinol, Tocopherol, Parfum, Linalool"
ACID = "Aqua, Glycolic Acid, Sodium Hydroxide, Niacinamide"


def test_parse_and_detect():
    ings = parse_inci(RETINOL)
    assert ings[0] == "Aqua" and "Retinol" in ings
    found = analyze_ingredients(ings)
    names = {a["name"] for a in found["actives"]}
    assert {"Retinol 0.25-1%", "Squalane Oil", "Vitamin E"} <= names
    assert any("zapach" in f for f in found["flags"]) and any("linalol" in f for f in found["flags"])


def test_conflict_only_when_new_product_brings_it():
    uid = 21
    r = client.post("/api/v1/skincare/products/parse", params={"user_id": uid}, json={"text": RETINOL, "name": "Serum R"})
    assert r.status_code == 200 and r.json()["conflicts"] == []
    client.post("/api/v1/skincare/products", params={"user_id": uid}, json={"name": "Serum R", "ingredients": parse_inci(RETINOL)})
    rep = client.post("/api/v1/skincare/products/parse", params={"user_id": uid}, json={"text": ACID}).json()
    assert any(c["type"] == "irritation_risk" for c in rep["conflicts"])  # retinoid + AHA


def test_tolerance_warning_from_logged_reactions():
    uid = 22
    for _ in range(2):
        client.post("/api/v1/skincare/reaction/log", params={"ingredient": "Retinol 0.25-1%", "reaction": "pieczenie", "severity": "high", "user_id": uid})
    rep = client.post("/api/v1/skincare/products/parse", params={"user_id": uid}, json={"text": RETINOL}).json()
    assert rep["tolerance_warnings"][0]["reaction_level"] == "high"


def test_usage_log_feeds_rotation():
    uid = 23
    p = client.post("/api/v1/skincare/products", params={"user_id": uid},
                    json={"name": "Retinol", "ingredients": ["Aqua", "Retinol"]}).json()
    start = date.today() - timedelta(weeks=13)
    for w in range(14):  # weekly use for 13 weeks -> retinoid cycle (12 weeks) complete
        client.post("/api/v1/skincare/usage/log", params={"user_id": uid},
                    json={"product_ids": [p["id"]], "date": (start + timedelta(weeks=w)).isoformat()})
    again = client.post("/api/v1/skincare/usage/log", params={"user_id": uid},
                        json={"product_ids": [p["id"]], "date": (start + timedelta(weeks=13)).isoformat()}).json()
    assert again["entries"] == 0  # idempotent per day
    rot = client.get("/api/v1/skincare/rotation/mine", params={"user_id": uid}).json()
    assert rot["recommendations"][0]["ingredient"] == "Retinol 0.25-1%"
    assert rot["recommendations"][0]["reason"] == "cycle_complete"


def test_short_use_does_not_rotate():
    uid = 24
    p = client.post("/api/v1/skincare/products", params={"user_id": uid},
                    json={"name": "R", "ingredients": ["Retinol"]}).json()
    client.post("/api/v1/skincare/usage/log", params={"user_id": uid}, json={"product_ids": [p["id"]]})
    assert client.get("/api/v1/skincare/rotation/mine", params={"user_id": uid}).json()["recommendations"] == []
    listed = client.get("/api/v1/skincare/products", params={"user_id": uid}).json()
    assert listed[0]["used_today"] is True


def test_scan_uses_ocr_then_local_analysis(monkeypatch):
    monkeypatch.setattr("backend.services.gemini_vision.GeminiVisionService.read_ingredient_label",
                        lambda self, b: {"product_name": "Krem X", "ingredients_text": ACID})
    r = client.post("/api/v1/skincare/products/scan", params={"user_id": 25},
                    files={"file": ("label.jpg", b"\xff\xd8fake", "image/jpeg")})
    assert r.status_code == 200 and r.json()["name"] == "Krem X"
    assert {"AHA (Glycolic Acid)", "Niacinamide 5-10%"} <= {a["name"] for a in r.json()["actives"]}

    monkeypatch.setattr("backend.services.gemini_vision.GeminiVisionService.read_ingredient_label",
                        lambda self, b: {"product_name": "", "ingredients_text": ""})
    bad = client.post("/api/v1/skincare/products/scan", params={"user_id": 25},
                      files={"file": ("label.jpg", b"\xff\xd8fake", "image/jpeg")})
    assert bad.status_code == 422


def test_openrouter_retries_unavailable_model(monkeypatch):
    import httpx

    from backend.services import openrouter as orr

    seen = []

    def fake_post(url, headers, json, timeout):
        seen.append(json["model"])
        code = 200 if json["model"] == orr.FALLBACK_MODEL else 404
        return httpx.Response(code, json={}, request=httpx.Request("POST", url))

    monkeypatch.setattr(orr.httpx, "post", fake_post)
    assert orr._post("http://x", {}, {"model": "retired/model"}, 5).status_code == 200
    assert seen == ["retired/model", orr.FALLBACK_MODEL]
