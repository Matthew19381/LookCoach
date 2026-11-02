"""Plan 8: the assistant follows LC-9/LC-1/LC-8/LC-4 - checked with a fake model (no real API calls)."""
import json
from datetime import datetime

import pytest

import backend.models  # noqa: F401
from backend.models.analysis import Analysis
from backend.models.assistant_message import AssistantMessage
from backend.models.outbox import OutboxEvent
from backend.models.photo import Photo
from backend.models.profile import UserProfile
from backend.services import assistant


class FakeLLM:
    def __init__(self, reply):
        self.reply = reply
        self.messages = None

    def __call__(self, messages):
        self.messages = messages
        return self.reply


def _seed(db):
    db.add(UserProfile(user_id=1, health=json.dumps({"pregnancy": True}), goals=json.dumps({"focus": ["skin"]})))
    photo = Photo(user_id=1, photo_type="front", file_path="uploads/a.jpg", analysis_status="done",
                  uploaded_at=datetime.now())
    db.add(photo)
    db.commit()
    a = Analysis(photo_id=photo.id)
    a.set_face_data({"swelling": {"level": "medium"}, "face_shape": "oval"})
    db.add(a)
    db.commit()


def test_context_and_rules_reach_the_model(db_session):
    _seed(db_session)
    llm = FakeLLM('{"reply": "Zacznij od SPF codziennie (RCT).", "actions": [{"type": "open_page", "path": "/skincare"}]}')
    result = assistant.chat(db_session, 1, "Od czego zacząć?", llm=llm)
    assert result["reply"].startswith("Zacznij od SPF")
    assert result["actions"] == [{"type": "open_page", "path": "/skincare", "label": "Otwórz stronę"}]
    system, context = llm.messages[0]["content"], json.loads(llm.messages[1]["content"].split("\n", 1)[1])
    assert "Nigdy nie oceniasz atrakcyjności" in system and "Nie układasz planów treningowych" in system
    assert context["health_flags"] == ["pregnancy"]
    assert "skincare_002" not in {r["id"] for r in context["recommendations"]}  # retinol blocked (LC-8)
    assert context["analysis"]["face"]["face_shape"] == "oval"


def test_numeric_rating_is_replaced(db_session):
    result = assistant.chat(db_session, 1, "Ile mam punktów?", llm=FakeLLM('{"reply": "Oceniam Cię na 7/10."}'))
    assert "7/10" not in result["reply"] and "lc9_replaced" in result["flags"]


@pytest.mark.parametrize("text", ["Twoja atrakcyjność to 65", "To da +20% atrakcyjności"])
def test_other_rating_forms_are_replaced(db_session, text):
    result = assistant.chat(db_session, 1, "?", llm=FakeLLM(json.dumps({"reply": text})))
    assert "lc9_replaced" in result["flags"]


def test_distress_gets_gentle_note_and_one_hub_signal(db_session):
    llm = FakeLLM('{"reply": "Jestem tu."}')
    first = assistant.chat(db_session, 1, "Jestem brzydki, nienawidzę swojej twarzy", llm=llm)
    assistant.chat(db_session, 1, "Ciągle sprawdzam w lustro", llm=llm)
    assert first["reply"].startswith("Słyszę, że wygląd") and "distress" in first["flags"]
    signals = [r for r in db_session.query(OutboxEvent).all()
               if json.loads(r.data).get("observation_type") == "photo_checking_pattern"]
    assert len(signals) == 1


def test_unknown_or_unsafe_actions_are_dropped(db_session):
    raw = json.dumps({"reply": "ok", "actions": [
        {"type": "delete_everything"}, {"type": "open_page", "path": "http://evil"},
        {"type": "send_needs"}, {"type": "start_experiment", "template_id": "cold_water"},
    ]})
    result = assistant.chat(db_session, 1, "?", llm=FakeLLM(raw))
    assert [a["type"] for a in result["actions"]] == ["send_needs", "start_experiment"]  # unsafe removed, max 2


def test_plain_text_reply_is_accepted_and_history_kept(db_session):
    assistant.chat(db_session, 1, "Cześć", llm=FakeLLM("Cześć! W czym pomóc?"))
    llm = FakeLLM('{"reply": "Drugie"}')
    assistant.chat(db_session, 1, "Druga wiadomość", llm=llm)
    roles = [m["role"] for m in llm.messages[2:]]
    assert roles == ["user", "assistant", "user"]
    assert db_session.query(AssistantMessage).count() == 4
    assert assistant.clear(db_session, 1) == 4
