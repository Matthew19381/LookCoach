"""Export and permanent deletion of all of a user's data (plan 2.5).

Generic over the schema: every table with a `user_id` column is included, plus
`analyses` (linked through photos). A new table with `user_id` is covered
without touching this file. The `users` row itself is kept - it is only the id
shared with the hub.
"""
import io
import json
import zipfile
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.base import Base
from ..models.photo import Photo
from ..paths import photo_path
from .gemini_vision import forget_image

SKIP_TABLES = {"users"}


def _user_tables():
    return [
        t for t in Base.metadata.sorted_tables
        if "user_id" in t.c and t.name not in SKIP_TABLES
    ]


def _uid_value(table, user_id: int):
    # integration_events stores the hub's text id
    return str(user_id) if table.c.user_id.type.python_type is str else user_id


def _jsonable(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "value"):  # Enum
        return value.value
    return value


def _photo_ids(db: Session, user_id: int) -> list[int]:
    return [p.id for p in db.query(Photo).filter(Photo.user_id == user_id).all()]


def collect(db: Session, user_id: int) -> dict:
    """{table_name: [row dicts]} for everything that belongs to the user."""
    data: dict[str, list[dict]] = {}
    for table in _user_tables():
        rows = db.execute(select(table).where(table.c.user_id == _uid_value(table, user_id))).mappings()
        data[table.name] = [{k: _jsonable(v) for k, v in row.items()} for row in rows]
    analyses = Base.metadata.tables["analyses"]
    ids = _photo_ids(db, user_id)
    rows = db.execute(select(analyses).where(analyses.c.photo_id.in_(ids))).mappings() if ids else []
    data["analyses"] = [{k: _jsonable(v) for k, v in row.items()} for row in rows]
    return data


def export_zip(db: Session, user_id: int) -> bytes:
    data = collect(db, user_id)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "dane.json",
            json.dumps(
                {"module": "lookcoach", "user_id": user_id,
                 "exported_at": datetime.now().isoformat(timespec="seconds"), "tables": data},
                ensure_ascii=False, indent=2,
            ),
        )
        for photo in db.query(Photo).filter(Photo.user_id == user_id).all():
            path = photo_path(photo.file_path)
            if path.exists():
                zf.write(path, f"zdjecia/{path.name}")
    return buf.getvalue()


def delete_all(db: Session, user_id: int) -> dict:
    """Delete rows, photo files and cached AI results. Returns counts per table."""
    counts: dict[str, int] = {}
    for photo in db.query(Photo).filter(Photo.user_id == user_id).all():
        path = photo_path(photo.file_path)
        if path.exists():
            forget_image(path.read_bytes())
            path.unlink(missing_ok=True)
    analyses = Base.metadata.tables["analyses"]
    ids = _photo_ids(db, user_id)
    counts["analyses"] = db.execute(analyses.delete().where(analyses.c.photo_id.in_(ids))).rowcount if ids else 0
    # Children before parents (photos is referenced by progress_logs).
    for table in reversed(_user_tables()):
        result = db.execute(table.delete().where(table.c.user_id == _uid_value(table, user_id)))
        counts[table.name] = result.rowcount or 0
    db.commit()
    return counts
