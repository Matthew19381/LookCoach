import json
from models.user import User
from models.profile import UserProfile
from models.photo import Photo
from models.analysis import Analysis
from models.recommendation import Recommendation
from models.progress import ProgressLog

def test_user_creation(db_session):
    user = User()
    db_session.add(user)
    db_session.commit()
    assert user.id is not None

def test_profile_creation(db_session):
    user = User()
    db_session.add(user)
    db_session.commit()

    profile = UserProfile(user_id=user.id, goals=json.dumps({'face': 0.4}), lifestyle=json.dumps({'sleep': 7}))
    db_session.add(profile)
    db_session.commit()

    assert profile.id is not None
    assert json.loads(profile.goals)["face"] == 0.4
    assert json.loads(profile.lifestyle)["sleep"] == 7

def test_profile_get_set_methods(db_session):
    user = User()
    db_session.add(user)
    db_session.commit()

    profile = UserProfile(user_id=user.id)
    profile.set_goals({'body': 0.3, 'skin': 0.3})
    profile.set_lifestyle({'stress': 5})
    db_session.add(profile)
    db_session.commit()

    assert profile.get_goals()["body"] == 0.3
    assert profile.get_lifestyle()["stress"] == 5

def test_profile_mode_field(db_session):
    # Test default mode
    user1 = User()
    db_session.add(user1)
    db_session.commit()

    profile = UserProfile(user_id=user1.id)
    db_session.add(profile)
    db_session.commit()
    assert profile.mode == "free"

    # Test custom mode
    user2 = User()
    db_session.add(user2)
    db_session.commit()

    profile_maintenance = UserProfile(user_id=user2.id, mode="maintenance")
    db_session.add(profile_maintenance)
    db_session.commit()
    assert profile_maintenance.mode == "maintenance"

    # Test improvement mode
    user3 = User()
    db_session.add(user3)
    db_session.commit()

    profile_improvement = UserProfile(user_id=user3.id, mode="improvement")
    db_session.add(profile_improvement)
    db_session.commit()
    assert profile_improvement.mode == "improvement"

def test_photo_creation(db_session):
    user = User()
    db_session.add(user)
    db_session.commit()

    photo = Photo(user_id=user.id, photo_type="front", file_path="/tmp/test.jpg", analysis_status="pending")
    db_session.add(photo)
    db_session.commit()

    assert photo.id is not None
    assert photo.photo_type == "front"

def test_analysis_creation(db_session):
    user = User()
    db_session.add(user)
    db_session.commit()

    photo = Photo(user_id=user.id, photo_type="front", file_path="/tmp/test.jpg")
    db_session.add(photo)
    db_session.commit()

    analysis = Analysis(photo_id=photo.id)
    analysis.set_face_data({'observations': ['clear skin'], 'swelling': {'level': 'low'}})
    db_session.add(analysis)
    db_session.commit()

    assert analysis.id is not None
    assert analysis.get_face_data()["swelling"]["level"] == "low"

def test_recommendation_creation(db_session):
    user = User()
    db_session.add(user)
    db_session.commit()

    rec = Recommendation(
        user_id=user.id,
        category="skincare",
        name="Test Product",
        evidence_level="RCT",
        effect_size=0.8,
        time_to_effect=4,
        roi_score=0.2,
    )
    db_session.add(rec)
    db_session.commit()

    assert rec.id is not None
    assert rec.evidence_level == "RCT"

def test_progress_log_creation(db_session):
    user = User()
    db_session.add(user)
    db_session.commit()

    progress = ProgressLog(user_id=user.id, look_score_change=5.5)
    db_session.add(progress)
    db_session.commit()

    assert progress.id is not None
    assert progress.look_score_change == 5.5
