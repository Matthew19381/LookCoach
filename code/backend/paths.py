"""Filesystem locations anchored to the backend directory, not to the CWD.

Before 2026-11-02 `uploads/` and `.cache/` were relative to the CWD: started from
`code/` the photos landed in `code/uploads` (not git-ignored), and in Docker
(WORKDIR /app) in `/app/uploads`, outside the `uploads` volume mounted at
`/app/backend/uploads` - photos vanished with the container.
Env overrides exist for tests (and for anyone who wants the data elsewhere).
"""
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = Path(os.getenv("LOOKCOACH_UPLOAD_DIR") or BACKEND_DIR / "uploads")
CACHE_DIR = Path(os.getenv("LOOKCOACH_CACHE_DIR") or BACKEND_DIR / ".cache")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def photo_path(stored: str) -> Path:
    """Resolve a Photo.file_path. Old rows hold CWD-relative 'uploads/x.jpg';
    the file name is the stable part, so look it up in UPLOAD_DIR. An absolute
    path that exists is used as is."""
    p = Path(stored)
    if p.is_absolute() and p.exists():
        return p
    return UPLOAD_DIR / p.name


def photo_url(stored: str) -> str:
    return f"/uploads/{Path(stored).name}"
