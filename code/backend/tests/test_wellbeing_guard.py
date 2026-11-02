"""Plan 5.6: frequent photo checking -> gentle note, pause, one signal per week for Mentalność."""
import json
from datetime import datetime, timedelta, timezone

import backend.models  # noqa: F401
from backend.models.outbox import OutboxEvent
from backend.models.photo import Photo
from backend.services.wellbeing_guard import assess, signal_hub_if_needed

NOW = datetime.now(timezone.utc).replace(tzinfo=None)


def _photos(db, user_id, items):
    for ptype, hours_ago in items:
        db.add(Photo(user_id=user_id, photo_type=ptype, file_path="uploads/x.jpg",
                     uploaded_at=NOW - timedelta(hours=hours_ago)))
    db.commit()


def test_normal_use_is_ok(db_session):
    _photos(db_session, 1, [("front", 1), ("side", 1), ("back", 1)])
    result = assess(db_session, 1, now=NOW)
    assert result["level"] == "ok" and result["message"] is None


def test_four_days_a_week_is_a_notice(db_session):
    _photos(db_session, 1, [("front", 24 * d + 1) for d in range(4)])
    result = assess(db_session, 1, now=NOW)
    assert result["level"] == "notice" and "powoli" in result["message"]


def test_same_view_three_times_a_day_is_concern(db_session):
    _photos(db_session, 1, [("front", 1), ("front", 3), ("front", 5)])
    result = assess(db_session, 1, now=NOW)
    assert result["level"] == "concern" and "same_view_repeated_24h" in result["signals"]
    assert "psychologiem" in result["message"]


def test_almost_daily_is_concern(db_session):
    _photos(db_session, 1, [("front", 24 * d + 1) for d in range(6)])
    assert assess(db_session, 1, now=NOW)["level"] == "concern"


def test_hub_signal_once_per_week(db_session):
    _photos(db_session, 1, [("front", 1), ("front", 2), ("front", 3)])
    result = assess(db_session, 1, now=NOW)
    assert signal_hub_if_needed(db_session, 1, result) is True
    assert signal_hub_if_needed(db_session, 1, result) is False
    rows = {r.event_type: json.loads(r.data) for r in db_session.query(OutboxEvent).all()}
    assert set(rows) == {"state_observation", "module_directive"}
    assert rows["state_observation"]["observation_type"] == "photo_checking_pattern"
    assert rows["module_directive"]["target_module"] == "mentalnosc"
    assert rows["module_directive"]["directive"] == "body_image_signal"


def test_ok_sends_nothing(db_session):
    assert signal_hub_if_needed(db_session, 1, {"level": "ok", "signals": []}) is False
    assert db_session.query(OutboxEvent).count() == 0
