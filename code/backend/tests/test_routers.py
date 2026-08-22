import sys
from pathlib import Path

# Add parent of backend to path so 'backend' is a package
BACKEND_DIR = Path(__file__).parent.parent
CODE_DIR = BACKEND_DIR.parent  # This is 'code/'
sys.path.insert(0, str(CODE_DIR))

# Now we can import backend as a package
import importlib
import os

# Change to backend directory for relative file paths
os.chdir(BACKEND_DIR)

# Import backend modules
from backend.database import get_db, init_db
from backend.models.base import Base

# Import all models so they register with Base.metadata
from backend.models import user, profile, photo, analysis, recommendation, progress

# Create test app (don't use main.app to avoid lifespan issues)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    yield

test_app = FastAPI(title="LookCoach Test API", lifespan=lifespan)
test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from backend.routers import photos, analysis, recommendations, progress, profile, skincare
from backend.routers import video_learning, event_mode, confidence, experiments
from backend.routers import aesthetic_training, posture, nutrition, sleep, stress

test_app.include_router(photos.router, prefix="/api/photos")
test_app.include_router(analysis.router, prefix="/api/analysis")
test_app.include_router(recommendations.router, prefix="/api/recommendations")
test_app.include_router(progress.router, prefix="/api/progress")
test_app.include_router(profile.router, prefix="/api/profile")
test_app.include_router(skincare.router, prefix="/api/skincare")
test_app.include_router(video_learning.router, prefix="/api/video-learning")
test_app.include_router(event_mode.router, prefix="/api/event-mode")
test_app.include_router(confidence.router, prefix="/api/confidence")
test_app.include_router(experiments.router, prefix="/api/experiments")
test_app.include_router(aesthetic_training.router, prefix="/api/aesthetic-training")
test_app.include_router(posture.router, prefix="/api/posture")
test_app.include_router(nutrition.router, prefix="/api/nutrition")
test_app.include_router(sleep.router, prefix="/api/sleep")
test_app.include_router(stress.router, prefix="/api/stress")

# Override get_db to use test database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import tempfile
import os

# Use file-based DB to avoid :memory: issues
TEST_DB_FILE = tempfile.mktemp(suffix='.db')
TEST_DB_URL = f"sqlite:///{TEST_DB_FILE}"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(bind=test_engine)


def get_test_db() -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the dependency
test_app.dependency_overrides[get_db] = get_test_db

# Create tables
Base.metadata.create_all(bind=test_engine)
print(f"Created tables: {list(Base.metadata.tables.keys())}")

from fastapi.testclient import TestClient
client = TestClient(test_app)

from fastapi.testclient import TestClient
client = TestClient(test_app)


# ========== PHOTOS ROUTER ==========
class TestPhotosRouter:
    def test_upload_photo_no_file(self):
        response = client.post("/api/photos/upload")
        assert response.status_code == 422

    def test_get_photos_empty(self):
        response = client.get("/api/photos/?user_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ========== ANALYSIS ROUTER ==========
class TestAnalysisRouter:
    def test_get_latest_analysis(self):
        response = client.get("/api/analysis/latest?user_id=1")
        assert response.status_code == 200

    def test_analyze_photo_not_found(self):
        response = client.post("/api/analysis/analyze/999")
        assert response.status_code == 404

    def test_analyze_photo_happy_path(self):
        """Happy path: existing photo with real file on disk + mocked vision service."""
        from datetime import datetime
        from unittest.mock import patch
        from backend.models.photo import Photo

        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        tmp.write(b"\xff\xd8fakejpegdata")
        tmp.close()
        db = TestSessionLocal()
        photo = Photo(
            user_id=1,
            photo_type="front",
            file_path=tmp.name,
            uploaded_at=datetime.utcnow(),
        )
        db.add(photo)
        db.commit()
        photo_id = photo.id
        db.close()

        fake_face_data = {
            "observations": ["mild puffiness in cheeks"],
            "swelling": {"level": "medium", "areas": ["cheeks"]},
            "muscle_tension": {"level": "low", "areas": []},
            "skin_quality": {"status": "good", "issues": []},
            "focus_areas": [{"area": "skincare", "priority": "medium", "reason": "hydration"}],
        }
        with patch(
            "backend.routers.analysis.VISION_SERVICE.analyze_face",
            return_value=fake_face_data,
        ):
            response = client.post(f"/api/analysis/analyze/{photo_id}")

        os.unlink(tmp.name)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["message"] == "Analysis complete"
        assert isinstance(body["analysis_id"], int)

    def test_latest_analysis_has_no_numeric_person_scores(self):
        """/api/analysis/latest must not expose numeric attractiveness ratings (LC-9)."""
        response = client.get("/api/analysis/latest?user_id=1")
        assert response.status_code == 200
        body = response.json()
        for banned in ("overall_score", "overall_face_score", "overall_body_score",
                       "overall_skin_score", "overall_hair_score"):
            assert banned not in body
        for section in ("face", "body", "skin", "hair"):
            data = body.get(section)
            if isinstance(data, dict):
                for key in data:
                    assert "overall" not in key.lower() or "score" not in key.lower()

    def test_analyze_photo_missing_file_fails_gracefully(self):
        """Photo row exists but file_path points nowhere -> 500 with status 'failed'."""
        from datetime import datetime
        from backend.models.photo import Photo

        db = TestSessionLocal()
        photo = Photo(
            user_id=1,
            photo_type="front",
            file_path="Z:/nonexistent/path/photo.jpg",
            uploaded_at=datetime.utcnow(),
        )
        db.add(photo)
        db.commit()
        photo_id = photo.id
        db.close()

        response = client.post(f"/api/analysis/analyze/{photo_id}")
        assert response.status_code == 500


# ========== RECOMMENDATIONS ROUTER ==========
class TestRecommendationsRouter:
    def test_get_recommendations(self):
        response = client.get("/api/recommendations/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# ========== PROGRESS ROUTER ==========
class TestProgressRouter:
    def test_get_timeline(self):
        response = client.get("/api/progress/timeline?user_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_compare_photos(self):
        response = client.post("/api/progress/compare", json={
            "photo_before_id": 1,
            "photo_after_id": 2
        })
        assert response.status_code in [200, 404]


# ========== PROFILE ROUTER ==========
class TestProfileRouter:
    def test_get_profile(self):
        response = client.get("/api/profile/?user_id=1")
        assert response.status_code == 200

    def test_update_profile(self):
        response = client.put("/api/profile/?user_id=1", json={
            "goals": {"primary": "looks_maxxing"},
            "lifestyle": {"sleep_hours": 7}
        })
        assert response.status_code == 200


# ========== SKINCARE ROUTER ==========
class TestSkincareRouter:
    def test_get_routine(self):
        response = client.get("/api/skincare/routine?user_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "morning" in data or "evening" in data


# ========== VIDEO LEARNING ROUTER ==========
class TestVideoLearningRouter:
    def test_get_recommended_videos(self):
        response = client.get("/api/video-learning/videos/recommended?user_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_search_videos(self):
        response = client.get("/api/video-learning/videos?query=posture")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ========== EVENT MODE ROUTER ==========
class TestEventModeRouter:
    def test_generate_event_plan(self):
        from datetime import date, timedelta
        # Event date must be in the future (router rejects past dates)
        future = (date.today() + timedelta(days=30)).isoformat()
        response = client.post("/api/event-mode/plan", json={
            "event_date": future,
            "event_type": "wedding"
        })
        assert response.status_code == 200

    def test_get_event_tips(self):
        response = client.get("/api/event-mode/tips/wedding")
        assert response.status_code == 200


# ========== CONFIDENCE ROUTER ==========
class TestConfidenceRouter:
    def test_analyze_confidence(self):
        response = client.get("/api/confidence/analyze?user_id=1")
        assert response.status_code == 200

    def test_get_action_plan(self):
        response = client.get("/api/confidence/action-plan")
        assert response.status_code == 200

    def test_attractiveness_impact(self):
        response = client.get("/api/confidence/attractiveness-impact?confidence_score=70&presence_score=70")
        assert response.status_code == 200


# ========== EXPERIMENTS ROUTER ==========
class TestExperimentsRouter:
    def test_get_templates(self):
        response = client.get("/api/experiments/templates")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_active_experiments(self):
        response = client.get("/api/experiments/active?user_id=1")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ========== AESTHETIC TRAINING ROUTER ==========
class TestAestheticTrainingRouter:
    def test_get_plans(self):
        response = client.get("/api/aesthetic-training/plans")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_generate_plan(self):
        response = client.post("/api/aesthetic-training/plan", json={
            "goal": "v_taper",
            "fitness_level": "beginner"
        })
        assert response.status_code == 200

    def test_get_exercises(self):
        response = client.get("/api/aesthetic-training/exercises")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_analyze_physique(self):
        response = client.post("/api/aesthetic-training/analyze", json={
            "analysis": {
                "body": {"v_taper_score": 40, "posture_score": 50}
            }
        })
        assert response.status_code == 200


# ========== POSTURE ROUTER ==========
class TestPostureRouter:
    def test_get_issues(self):
        response = client.get("/api/posture/issues")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_detect_issues(self):
        response = client.post("/api/posture/detect", json={
            "analysis": {"head_position": "forward", "shoulder_position": "forward"}
        })
        assert response.status_code == 200

    def test_get_correction_plan(self):
        issues_resp = client.get("/api/posture/issues")
        issues = issues_resp.json()
        if len(issues) > 0:
            issue_id = issues[0]["id"]
            response = client.get(f"/api/posture/correction/{issue_id}")
            assert response.status_code == 200

    def test_full_assessment(self):
        response = client.post("/api/posture/assess", json={
            "analysis": {"head_position": "forward", "shoulder_position": "forward"}
        })
        assert response.status_code == 200


# ========== NUTRITION ROUTER ==========
class TestNutritionRouter:
    def test_get_factors(self):
        response = client.get("/api/nutrition/factors")
        assert response.status_code == 200

    def test_get_recommendations(self):
        response = client.get("/api/nutrition/recommendations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_meal_plan(self):
        response = client.get("/api/nutrition/meal-plan/pre_event")
        assert response.status_code == 200

    def test_analyze_diet(self):
        response = client.post("/api/nutrition/analyze", json={
            "diet_log": {"calories": 2000, "protein": 150}
        })
        assert response.status_code == 200


# ========== SLEEP ROUTER ==========
class TestSleepRouter:
    def test_get_factors(self):
        response = client.get("/api/sleep/factors")
        assert response.status_code == 200

    def test_analyze_sleep(self):
        response = client.post("/api/sleep/analyze", json={
            "sleep_data": {"hours": 6, "quality": "poor"}
        })
        assert response.status_code == 200

    def test_get_pre_event_tips(self):
        response = client.get("/api/sleep/pre-event/general")
        assert response.status_code == 200


# ========== STRESS ROUTER ==========
class TestStressRouter:
    def test_get_effects(self):
        response = client.get("/api/stress/effects")
        assert response.status_code == 200

    def test_get_techniques(self):
        response = client.get("/api/stress/techniques")
        assert response.status_code == 200

    def test_analyze_stress(self):
        response = client.post("/api/stress/analyze", json={
            "stress_data": {"level": "high", "triggers": ["work"]}
        })
        assert response.status_code == 200
