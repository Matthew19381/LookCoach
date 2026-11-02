"""Plan 5.5: reminders follow the day plan rules, quiet hours, survival mode, once a day."""
from datetime import datetime, timedelta

import backend.models  # noqa: F401
from backend.models.consistency import AdherenceLog, ProtocolTypeEnum
from backend.models.directive_state import DirectiveState
from backend.models.photo import Photo
from backend.models.push import PushSubscription
from backend.services import reminders, webpush

TODAY = datetime(2026, 11, 2)


def _tracks_morning(db, user_id=1):
    db.add(AdherenceLog(user_id=user_id, protocol_type=ProtocolTypeEnum.SKINCARE_MORNING,
                        date=TODAY - timedelta(days=1), completed=True))
    db.commit()


def test_quiet_hours_across_midnight():
    assert reminders.in_quiet_hours(23 * 60, "22:00", "07:00")
    assert reminders.in_quiet_hours(6 * 60, "22:00", "07:00")
    assert not reminders.in_quiet_hours(8 * 60, "22:00", "07:00")
    assert reminders.in_quiet_hours(13 * 60, "12:00", "14:00")


def test_morning_reminder_only_for_tracked_routine_after_time(db_session):
    assert reminders.due(db_session, 1, TODAY.replace(hour=8)) == []  # not tracked -> nothing pushed
    _tracks_morning(db_session)
    assert reminders.due(db_session, 1, TODAY.replace(hour=7)) == []  # before 07:30
    (r,) = reminders.due(db_session, 1, TODAY.replace(hour=8))
    assert r["kind"] == "skincare_morning" and r["url"] == "/consistency"


def test_quiet_hours_and_survival(db_session):
    _tracks_morning(db_session)
    db_session.add(DirectiveState(user_id=1, survival_mode=True, quiet_hours_from="07:00", quiet_hours_to="09:00"))
    db_session.commit()
    assert reminders.due(db_session, 1, TODAY.replace(hour=8)) == []
    (r,) = reminders.due(db_session, 1, TODAY.replace(hour=10))
    assert r["body"].startswith("Wersja minimum")


def test_photo_reminder_when_due(db_session):
    db_session.add(Photo(user_id=1, photo_type="front", file_path="uploads/p.jpg", analysis_status="done",
                         uploaded_at=TODAY - timedelta(days=20)))
    db_session.commit()
    kinds = [r["kind"] for r in reminders.due(db_session, 1, TODAY.replace(hour=9))]
    assert kinds == ["photo_session"]


def test_run_sends_once_a_day_and_drops_gone_subscriptions(db_session, monkeypatch):
    monkeypatch.setenv("VAPID_PRIVATE_KEY", webpush.generate_vapid_keys()["VAPID_PRIVATE_KEY"])
    _tracks_morning(db_session)
    db_session.add_all([
        PushSubscription(user_id=1, endpoint="https://push.example/a", p256dh="x", auth="y"),
        PushSubscription(user_id=1, endpoint="https://push.example/gone", p256dh="x", auth="y"),
    ])
    db_session.commit()
    sent = []

    def fake_send(sub, payload, key, subject):
        if sub["endpoint"].endswith("gone"):
            raise webpush.SubscriptionGone
        sent.append((sub["endpoint"], payload["title"]))

    now = TODAY.replace(hour=8)
    assert reminders.run(db_session, now=now, send=fake_send) == 1
    assert reminders.run(db_session, now=now, send=fake_send) == 0  # once a day
    assert sent == [("https://push.example/a", "Pielęgnacja rano")]
    assert [s.endpoint for s in db_session.query(PushSubscription).all()] == ["https://push.example/a"]


def test_run_without_keys_does_nothing(db_session, monkeypatch):
    monkeypatch.delenv("VAPID_PRIVATE_KEY", raising=False)
    assert reminders.run(db_session, send=lambda *a: (_ for _ in ()).throw(AssertionError)) == 0
