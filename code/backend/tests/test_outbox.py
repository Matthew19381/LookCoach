"""Plan 3.1: outgoing hub events are queued and retried, never silently lost."""
import asyncio
import json

import pytest

import backend.models  # noqa: F401
from backend.models.outbox import OutboxEvent
from backend.services import outbox
from backend.services.integration_publisher import ConfigurationError, PublishError


class FakePublisher:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def __call__(self, timeout=5.0):  # used as factory
        return self

    async def publish(self, event_type, user_id, data, timestamp=None):
        self.calls.append((event_type, user_id, data, timestamp))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _run(db, pub):
    return asyncio.run(outbox.deliver_pending(db, publisher_factory=pub))


def _due_now(db):
    for row in db.query(OutboxEvent).all():
        row.next_attempt_at = None
    db.commit()


def test_success_marks_sent_and_keeps_timestamp(db_session):
    row = outbox.enqueue(db_session, "protocol_done", {"protocol_id": "skincare_morning"})
    pub = FakePublisher([{"status": "published", "plan_item": None}])
    assert _run(db_session, pub) == {"sent": 1, "retry": 0, "failed": 0}
    db_session.refresh(row)
    assert row.status == "sent"
    assert pub.calls[0][3] == row.timestamp  # fixed at queue time -> hub dedup works
    assert json.loads(row.hub_response)["status"] == "published"


def test_network_error_is_retried_with_backoff_then_sent(db_session):
    row = outbox.enqueue(db_session, "protocol_done", {"protocol_id": "x"})
    pub = FakePublisher([PublishError("connection refused"), {"status": "duplicate"}])
    assert _run(db_session, pub)["retry"] == 1
    db_session.refresh(row)
    assert row.status == "pending" and row.next_attempt_at is not None
    assert _run(db_session, pub) == {"sent": 0, "retry": 0, "failed": 0}  # not due yet
    _due_now(db_session)
    assert _run(db_session, pub)["sent"] == 1  # "duplicate" from the hub also counts as delivered


def test_contract_error_fails_at_once(db_session):
    row = outbox.enqueue(db_session, "protocol_done", {"protocol_id": "x"})
    _run(db_session, FakePublisher([PublishError("Hub returned 422", status_code=422)]))
    db_session.refresh(row)
    assert row.status == "failed"


def test_server_error_gives_up_after_max_attempts(db_session):
    row = outbox.enqueue(db_session, "protocol_done", {"protocol_id": "x"})
    pub = FakePublisher([PublishError("503", status_code=503)] * outbox.MAX_ATTEMPTS)
    for _ in range(outbox.MAX_ATTEMPTS):
        _due_now(db_session)
        _run(db_session, pub)
    db_session.refresh(row)
    assert row.status == "failed" and row.attempts == outbox.MAX_ATTEMPTS


def test_bad_key_keeps_event_pending(db_session):
    row = outbox.enqueue(db_session, "protocol_done", {"protocol_id": "x"})
    _run(db_session, FakePublisher([ConfigurationError("401")]))
    db_session.refresh(row)
    assert row.status == "pending" and "401" in row.last_error


def test_missing_key_keeps_everything_pending(db_session):
    outbox.enqueue(db_session, "protocol_done", {"protocol_id": "x"})

    def no_key(timeout=5.0):
        raise ConfigurationError("MODULE_KEY not configured")

    assert _run(db_session, no_key)["retry"] == 1
    assert db_session.query(OutboxEvent).one().status == "pending"


def test_unknown_event_type_is_rejected(db_session):
    with pytest.raises(ValueError):
        outbox.enqueue(db_session, "made_up", {})
