"""Plan 2.5: export everything / delete everything."""
import io
import json
import zipfile
from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.models  # noqa: F401
from backend.database import get_db
from backend.models.analysis import Analysis
from backend.models.base import Base
from backend.models.experiment import Experiment
from backend.models.integration_event import IntegrationEvent
from backend.models.photo import Photo
from backend.models.profile import UserProfile
from backend.paths import UPLOAD_DIR
from backend.routers import data

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

app = FastAPI()
app.include_router(data.router, prefix="/api/v1/data")
def _db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _db
client = TestClient(app)


def _seed(user_id: int) -> str:
    db = Session()
    file = UPLOAD_DIR / f"front_{user_id}_privacy.jpg"
    file.write_bytes(b"\xff\xd8 not decoded here")
    photo = Photo(user_id=user_id, photo_type="front", file_path=str(file), uploaded_at=datetime.now())
    db.add(photo)
    db.commit()
    a = Analysis(photo_id=photo.id)
    a.set_face_data({"swelling": {"level": "low"}})
    db.add_all([
        a,
        UserProfile(user_id=user_id, health=json.dumps({"pregnancy": False})),
        Experiment(experiment_id=f"exp-{user_id}", user_id=user_id, template_id="t"),
        IntegrationEvent(source_module="hub", event_type="t", user_id=str(user_id), timestamp="t", payload="{}"),
    ])
    db.commit()
    db.close()
    return file.name


def test_export_contains_all_tables_and_photos():
    name = _seed(501)
    response = client.get("/api/v1/data/export?user_id=501")
    assert response.status_code == 200
    zf = zipfile.ZipFile(io.BytesIO(response.content))
    assert f"zdjecia/{name}" in zf.namelist()
    tables = json.loads(zf.read("dane.json"))["tables"]
    assert len(tables["photos"]) == 1
    assert len(tables["analyses"]) == 1
    assert len(tables["user_profiles"]) == 1
    assert len(tables["integration_events"]) == 1


def test_delete_requires_confirmation():
    assert client.delete("/api/v1/data?user_id=502").status_code == 400


def test_delete_removes_everything_of_that_user_only():
    name = _seed(503)
    _seed(504)
    response = client.delete("/api/v1/data?user_id=503&confirm=USUN-WSZYSTKO")
    assert response.status_code == 200
    assert not (UPLOAD_DIR / name).exists()
    db = Session()
    assert db.query(Photo).filter(Photo.user_id == 503).count() == 0
    assert db.query(UserProfile).filter(UserProfile.user_id == 503).count() == 0
    assert db.query(IntegrationEvent).filter(IntegrationEvent.user_id == "503").count() == 0
    assert db.query(Photo).filter(Photo.user_id == 504).count() == 1
    photo_ids = {p.id for p in db.query(Photo).all()}
    assert all(a.photo_id in photo_ids for a in db.query(Analysis).all())  # no orphans left
    other = db.query(Photo).filter(Photo.user_id == 504).one()
    assert db.query(Analysis).filter(Analysis.photo_id == other.id).count() == 1
    db.close()
