"""Plan 3.2-3.6: analysis -> needs for ForgeBody / Dieta, queued only on change."""
import json
from datetime import datetime

import backend.models  # noqa: F401
from backend.models.analysis import Analysis
from backend.models.outbox import OutboxEvent
from backend.models.photo import Photo
from backend.models.profile import UserProfile
from backend.services.ecosystem_dispatch import dispatch_needs
from backend.services.goal_router import FORGEBODY_GROUPS, nutrition_needs, training_needs


def test_missing_muscles_map_to_forgebody_vocabulary():
    needs = training_needs({
        "missing_muscles": [
            {"muscle": "delts", "priority": "high"},
            {"muscle": "Upper chest", "priority": "medium"},
            {"muscle": "calves", "priority": "low"},  # low -> ignored
        ],
    })
    assert needs["muscle_groups"] == ["side_delts", "upper_chest"]
    assert set(needs["muscle_groups"]) <= set(FORGEBODY_GROUPS)
    assert needs["duration_weeks"] == 4


def test_forward_posture_adds_rear_delts():
    needs = training_needs({"posture": {"shoulder_position": "forward"}})
    assert needs["muscle_groups"] == ["rear_delts"]


def test_nothing_to_do_returns_none():
    assert training_needs({"missing_muscles": [], "posture": {"head_position": "neutral"}}) is None
    assert training_needs(None) is None
    assert nutrition_needs({}, {}, {}) is None


def test_swelling_gives_sodium_limit_and_acne_low_gl():
    needs = nutrition_needs(
        {"swelling": {"level": "high"}},
        {"problems": [{"issue": "acne", "severity": "moderate"}]},
        {},
    )
    assert needs["sodium_limit_mg"] == 2300
    assert needs["low_glycemic_load"] is True
    assert {i["evidence_id"] for i in needs["items"]} == {"nutrition_002", "nutrition_005"}


def test_kidney_disease_blocks_sodium_target():
    """LC-8."""
    needs = nutrition_needs({"swelling": {"level": "high"}}, {}, {"kidney_disease": True})
    assert needs is None


def _analysed_side_photo(db, user_id, body):
    photo = Photo(user_id=user_id, photo_type="side", file_path="uploads/s.jpg",
                  uploaded_at=datetime.now(), analysis_status="done")
    db.add(photo)
    db.commit()
    a = Analysis(photo_id=photo.id)
    a.set_body_data(body)
    db.add(a)
    db.commit()


def test_dispatch_queues_once_and_again_only_on_change(db_session):
    _analysed_side_photo(db_session, 1, {"missing_muscles": [{"muscle": "delts", "priority": "high"}]})
    assert dispatch_needs(db_session, 1) == ["aesthetic_priority"]
    assert dispatch_needs(db_session, 1) == []  # same needs -> nothing new

    row = db_session.query(OutboxEvent).one()
    data = json.loads(row.data)
    assert row.event_type == "module_directive"
    assert data["target_module"] == "forge-body"
    assert data["payload"]["muscle_groups"] == ["side_delts"]

    _analysed_side_photo(db_session, 1, {"missing_muscles": [{"muscle": "lats", "priority": "high"}]})
    assert dispatch_needs(db_session, 1) == ["aesthetic_priority"]


def test_dispatch_respects_health_flags(db_session):
    db_session.add(UserProfile(user_id=2, health=json.dumps({"kidney_disease": True})))
    photo = Photo(user_id=2, photo_type="front", file_path="uploads/f.jpg",
                  uploaded_at=datetime.now(), analysis_status="done")
    db_session.add(photo)
    db_session.commit()
    a = Analysis(photo_id=photo.id)
    a.set_face_data({"swelling": {"level": "high"}})
    db_session.add(a)
    db_session.commit()
    assert dispatch_needs(db_session, 2) == []
