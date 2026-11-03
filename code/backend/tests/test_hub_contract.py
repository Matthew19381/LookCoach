"""Plan 7.6: what LookCoach sends to / returns for the hub matches the hub's schemas.

The models below mirror System-Glowny backend/services/schemas.py (ModuleEvent,
ModuleSummary subset) and docs/INTEGRACJA-MODULOW.md §1.1, §1.1a, §1.2, §1.5.
If the hub contract changes, update them together with the hub.
"""
import asyncio
import json
import re
from datetime import datetime
from typing import Any, Optional

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.models  # noqa: F401
from backend.database import get_db
from backend.models.base import Base
from backend.routers import summary
from backend.services import outbox
from backend.services.integration_publisher import IntegrationPublisher


class HubModuleEvent(BaseModel):  # System-Glowny services/schemas.py
    model_config = ConfigDict(extra="forbid")
    event_type: str
    module: str
    user_id: str
    timestamp: datetime
    data: dict[str, Any] = Field(default_factory=dict)
    duration_seconds: Optional[int] = None
    score: Optional[float] = None
    tags: list[str] = Field(default_factory=list)
    affect: Optional[dict[str, int]] = None
    evidence_id: Optional[str] = None
    plan_item_id: Optional[str] = None


class SuggestedItem(BaseModel):  # §1.1a
    model_config = ConfigDict(extra="forbid")
    title: str
    intention_cue: Optional[str] = None
    scheduled_time: Optional[str] = None
    estimated_minutes: Optional[int] = None
    priority: Optional[int] = None
    complete_on: list[str] = Field(default_factory=list)
    includes_due_reviews: bool = False


COMPLETE_ON = re.compile(r"^[a-z_]+(:[a-z_]+=[A-Za-z0-9_.-]+)?$")
ROUTABLE = {"aesthetic_priority", "nutrition_needs", "body_image_signal"}  # hub routers/directives.py


def test_published_event_body_is_a_valid_hub_module_event():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        captured["key"] = request.headers.get("X-Module-Key")
        return httpx.Response(200, json={"status": "published"})

    real = httpx.AsyncClient

    class Patched(real):
        def __init__(self, *a, **kw):
            super().__init__(*a, **{**kw, "transport": httpx.MockTransport(handler)})

    import backend.services.integration_publisher as ip
    original = ip.httpx.AsyncClient
    ip.httpx.AsyncClient = Patched
    try:
        asyncio.run(IntegrationPublisher(module_key="k").publish(
            "module_directive", "1",
            {"target_module": "forge-body", "directive": "aesthetic_priority", "payload": {"muscle_groups": ["glutes"]}},
            timestamp="2026-11-02T10:00:00Z",
        ))
    finally:
        ip.httpx.AsyncClient = original

    event = HubModuleEvent(**captured["body"])
    assert event.module == "lookcoach" and captured["key"] == "k"
    assert event.data["directive"] in ROUTABLE and isinstance(event.data["payload"], dict)


def test_every_queued_event_type_is_valid_for_the_hub(db_session):
    for event_type, data in (
        ("protocol_done", {"protocol_id": "skincare_morning"}),
        ("state_observation", {"observation_type": "photo_session", "labels": {}}),
        ("module_directive", {"target_module": "dieta", "directive": "nutrition_needs", "payload": {}}),
    ):
        row = outbox.enqueue(db_session, event_type, data)
        HubModuleEvent(event_type=row.event_type, module="lookcoach", user_id="1",
                       timestamp=row.timestamp, data=json.loads(row.data))


def _summary_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Local = sessionmaker(bind=engine)
    app = FastAPI()
    app.include_router(summary.router, prefix="/api/v1")

    def _db():
        db = Local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _db
    return TestClient(app), Local


def test_summary_matches_hub_contract():
    client, Local = _summary_client()
    db = Local()
    outbox.enqueue(db, "protocol_done", {"protocol_id": "skincare_morning"})
    db.close()

    body = client.get("/api/v1/summary", params={"user_id": "1"}).json()
    assert set(body) == {"module", "user_id", "date", "summary", "events", "wellbeing_contribution"}
    assert body["module"] == "lookcoach" and body["wellbeing_contribution"] is None
    datetime.fromisoformat(body["date"])
    events = [HubModuleEvent(**e) for e in body["events"]]
    assert [e.event_type for e in events] == ["protocol_done"]
    for item in body["summary"]["suggested_items"]:
        parsed = SuggestedItem(**item)
        assert all(COMPLETE_ON.match(token) for token in parsed.complete_on)
    assert len(body["summary"]["suggested_items"]) <= 3
