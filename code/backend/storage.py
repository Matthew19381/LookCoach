"""Where LookCoach keeps private files: photos and cached AI answers about them.

They must never land inside the repository - it is public. Until 2026-10-15 both
went to CWD-relative "uploads"/".cache"; the ecosystem starter runs the backend
from code/, so they would have ended in code/uploads and code/.cache, which
.gitignore did not cover.

LOOKCOACH_DATA_DIR (absolute path, from env or the root .env) chooses the folder;
without it: ~/LookCoach-dane. A folder inside the repository is refused at import,
so a wrong setting stops the backend instead of exposing photos.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

DEFAULT_DATA_DIR = Path.home() / "LookCoach-dane"


class StorageConfigError(RuntimeError):
    pass


def resolve_data_dir(raw: str | None = None) -> Path:
    raw = (os.getenv("LOOKCOACH_DATA_DIR", "") if raw is None else raw).strip()
    path = Path(raw).expanduser() if raw else DEFAULT_DATA_DIR
    if not path.is_absolute():
        raise StorageConfigError(
            f"LOOKCOACH_DATA_DIR musi być ścieżką bezwzględną, jest: {raw!r}"
        )
    path = path.resolve()
    if path == PROJECT_ROOT or PROJECT_ROOT in path.parents:
        raise StorageConfigError(
            f"LOOKCOACH_DATA_DIR ({path}) leży w repozytorium {PROJECT_ROOT}, "
            "które jest publiczne - wybierz folder poza nim"
        )
    return path


DATA_DIR = resolve_data_dir()
UPLOAD_DIR = DATA_DIR / "uploads"
CACHE_DIR = DATA_DIR / "cache"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
