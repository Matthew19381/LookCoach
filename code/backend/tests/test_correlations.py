"""Plan 5.3: qualitative correlations, only with enough sessions, always with a caveat."""
from datetime import datetime, timedelta

import backend.models  # noqa: F401
from backend.models.analysis import Analysis
from backend.models.consistency import AdherenceLog, ProtocolTypeEnum
from backend.models.photo import Photo
from backend.services.correlations import find, sodium_from_events, stress_from_events

NOW = datetime.now()


def _session(db, days_ago, skin=None, swelling=None):
    photo = Photo(user_id=1, photo_type="front", file_path="uploads/c.jpg", analysis_status="done",
                  uploaded_at=NOW - timedelta(days=days_ago))
    db.add(photo)
    db.commit()
    a = Analysis(photo_id=photo.id)
    face = {}
    if skin:
        face["skin_quality"] = {"status": skin}
    if swelling:
        face["swelling"] = {"level": swelling}
    a.set_face_data(face)
    db.add(a)
    db.commit()


def _routine(db, days_ago_from, days_ago_to, completed):
    for d in range(days_ago_to, days_ago_from + 1):
        db.add(AdherenceLog(user_id=1, protocol_type=ProtocolTypeEnum.SKINCARE_MORNING,
                            date=NOW - timedelta(days=d), completed=completed))
    db.commit()


def test_nothing_with_too_few_sessions(db_session):
    _session(db_session, 1, skin="good")
    result = find(db_session, 1)
    assert result["insights"] == [] and result["caveat"] is None


def test_skincare_regularity_vs_skin(db_session):
    # two sessions after regular weeks (good skin), two after irregular weeks (fair skin)
    _routine(db_session, 100, 87, True)
    _session(db_session, 86, skin="good")
    _routine(db_session, 80, 67, True)
    _session(db_session, 66, skin="good")
    _routine(db_session, 60, 47, False)
    _session(db_session, 46, skin="fair")
    _routine(db_session, 40, 27, False)
    _session(db_session, 26, skin="fair")
    result = find(db_session, 1)
    (insight,) = result["insights"]
    assert "w 2 z 2 sesji" in insight["text"] and "w 0 z 2" in insight["text"]
    assert "nie dowód przyczyny" in result["caveat"]
    assert not any(ch in insight["text"] for ch in ("/10", "%"))


def test_stress_vs_swelling(db_session):
    for days, swelling in ((40, "high"), (30, "medium"), (20, "low"), (10, "low")):
        _session(db_session, days, swelling=swelling)
    stress = {}
    for days, level in ((40, 5), (30, 4), (20, 1), (10, 2)):
        for back in (1, 2):
            stress[(NOW - timedelta(days=days + back)).date()] = level
    (insight,) = find(db_session, 1, stress)["insights"]
    assert insight["area"] == "Obrzęk a stres"
    assert "w 2 z 2 sesji" in insight["text"] and "w 0 z 2" in insight["text"]


def test_stress_from_hub_events():
    events = [
        {"timestamp": "2026-10-01T08:00:00Z", "affect": {"stress": 4}},
        {"timestamp": "2026-10-01T20:00:00Z", "affect": {"stress": 2}},
        {"timestamp": "2026-10-02T08:00:00Z", "data": {}},
    ]
    result = stress_from_events(events)
    assert list(result.values()) == [3.0]


def test_sodium_vs_swelling_from_dieta_events(db_session):
    for days, swelling in ((40, "high"), (30, "medium"), (20, "low"), (10, "low")):
        _session(db_session, days, swelling=swelling)
    events = []
    for days, mg in ((40, 1600), (30, 1500), (20, 500), (10, 400)):
        day = (NOW - timedelta(days=days + 1)).date().isoformat()
        events += [{"module": "dieta", "event_type": "meal_logged", "data": {"date": day, "sodium_mg": mg}}] * 2
    events.append({"module": "forge-body", "event_type": "meal_logged", "data": {"date": day, "sodium_mg": 9999}})
    sodium = sodium_from_events(events)
    assert max(sodium.values()) == 3200
    (insight,) = find(db_session, 1, sodium_by_day=sodium)["insights"]
    assert insight["area"] == "Obrzęk a sód"
    assert "w 2 z 2 sesji" in insight["text"] and "w 0 z 2" in insight["text"]
