"""Photos and AI answers about them never land inside the public repo (2026-10-15).

Before, they went to CWD-relative uploads/ and .cache/; the starter runs the
backend from code/, so a commit could have published face photos.
"""
import importlib
import subprocess
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

storage = importlib.import_module("backend.storage")
database = importlib.import_module("backend.database")
Base = importlib.import_module("backend.models.base").Base
importlib.import_module("backend.models")
photos = importlib.import_module("backend.routers.photos")

REPO = storage.PROJECT_ROOT
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64  # bytes only; no real photo in this public repo


def test_data_dir_is_outside_repo():
    assert REPO not in storage.DATA_DIR.parents
    assert storage.UPLOAD_DIR.parent == storage.DATA_DIR
    assert storage.CACHE_DIR.parent == storage.DATA_DIR


@pytest.mark.parametrize("inside", ["", "code", "code/uploads", "code/backend/.cache"])
def test_folder_inside_repo_is_refused(inside):
    with pytest.raises(storage.StorageConfigError):
        storage.resolve_data_dir(str(REPO / inside))


def test_relative_path_is_refused():
    with pytest.raises(storage.StorageConfigError):
        storage.resolve_data_dir("uploads")


def test_parent_traversal_into_repo_is_refused(tmp_path):
    sneaky = REPO / "code" / ".." / "code" / "uploads"
    with pytest.raises(storage.StorageConfigError):
        storage.resolve_data_dir(str(sneaky))


def test_empty_setting_uses_default_outside_repo():
    path = storage.resolve_data_dir("")
    assert path == storage.DEFAULT_DATA_DIR.resolve()
    assert REPO not in path.parents


def test_folder_outside_repo_is_accepted(tmp_path):
    assert storage.resolve_data_dir(str(tmp_path / "LookCoach-prywatne")) == (tmp_path / "LookCoach-prywatne").resolve()


def test_ai_cache_uses_private_folder():
    gv = importlib.import_module("backend.services.gemini_vision")
    key = Path(gv._cache_key(b"x", "face"))
    assert key.parent == storage.CACHE_DIR


def _client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)

    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(photos.router, prefix="/api/v1/photos")
    app.dependency_overrides[database.get_db] = override
    return TestClient(app)


def _untracked_in_repo() -> str:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=REPO, capture_output=True, text=True,
    )
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    return "\n".join(line for line in out.stdout.splitlines() if line.startswith("??"))


def test_upload_lands_outside_repo_and_delete_removes_it():
    before = _untracked_in_repo()
    client = _client()
    r = client.post(
        "/api/v1/photos/upload",
        files={"file": ("twarz.jpg", JPEG, "image/jpeg")},
        data={"photo_type": "front", "user_id": "1"},
    )
    assert r.status_code == 200, r.text
    saved = list(storage.UPLOAD_DIR.glob("front_1_*.jpg"))
    assert saved and saved[0].read_bytes() == JPEG
    assert REPO not in saved[0].resolve().parents
    assert _untracked_in_repo() == before  # nothing new for git to pick up

    r = client.delete(f"/api/v1/photos/{r.json()['id']}")
    assert r.status_code == 200
    assert not saved[0].exists()


def test_gitignore_covers_uploads_and_cache_anywhere():
    for path in ("code/uploads/x.jpg", "code/.cache/x.json", "uploads/x.jpg", "code/backend/uploads/x.jpg"):
        r = subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO)
        if r.returncode == 128:
            pytest.skip("not a git checkout")
        assert r.returncode == 0, f"{path} is not ignored"
