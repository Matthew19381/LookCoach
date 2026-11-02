"""Plan 2.1: upload accepts only real images, strips metadata, names files itself."""
import io

import pytest
from PIL import Image

from backend.services.photo_storage import MAX_UPLOAD_BYTES, InvalidPhoto, sanitize_image


def _jpeg_with_gps(size=(40, 20), orientation=None) -> bytes:
    img = Image.new("RGB", size, (200, 100, 50))
    exif = Image.Exif()
    exif[0x010F] = "PhoneMaker"  # Make
    gps = exif.get_ifd(0x8825)
    gps[1] = "N"
    gps[2] = (52.0, 13.0, 0.0)  # GPSLatitude
    if orientation:
        exif[0x0112] = orientation
    out = io.BytesIO()
    img.save(out, format="JPEG", exif=exif)
    return out.getvalue()


def test_html_disguised_as_jpg_is_rejected():
    with pytest.raises(InvalidPhoto):
        sanitize_image(b"<html><script>alert(1)</script></html>")


def test_empty_file_is_rejected():
    with pytest.raises(InvalidPhoto):
        sanitize_image(b"")


def test_too_large_is_rejected():
    with pytest.raises(InvalidPhoto, match="za duże"):
        sanitize_image(b"\xff\xd8" + b"0" * MAX_UPLOAD_BYTES)


def test_gif_is_rejected():
    out = io.BytesIO()
    Image.new("RGB", (4, 4)).save(out, format="GIF")
    with pytest.raises(InvalidPhoto):
        sanitize_image(out.getvalue())


def test_exif_and_gps_are_removed():
    raw = _jpeg_with_gps()
    assert Image.open(io.BytesIO(raw)).getexif().get_ifd(0x8825)  # precondition
    clean, ext = sanitize_image(raw)
    assert ext == "jpg"
    exif = Image.open(io.BytesIO(clean)).getexif()
    assert not exif.get_ifd(0x8825)
    assert 0x010F not in exif


def test_exif_rotation_is_applied_before_stripping():
    """Orientation 6 = rotate 90 deg: the stored photo must be upright without EXIF."""
    clean, _ = sanitize_image(_jpeg_with_gps(size=(40, 20), orientation=6))
    assert Image.open(io.BytesIO(clean)).size == (20, 40)


def test_png_keeps_png():
    out = io.BytesIO()
    Image.new("RGBA", (8, 8)).save(out, format="PNG")
    _, ext = sanitize_image(out.getvalue())
    assert ext == "png"


def test_delete_photo_removes_file_analysis_and_cache(db_session, monkeypatch):
    """Plan 2.4: nothing of a deleted photo stays behind."""
    from backend.models.analysis import Analysis
    from backend.models.photo import Photo
    from backend.paths import UPLOAD_DIR, photo_path
    from backend.services import gemini_vision

    raw, _ = sanitize_image(_jpeg_with_gps())
    file = UPLOAD_DIR / "front_1_del.jpg"
    file.write_bytes(raw)
    cache = __import__("pathlib").Path(gemini_vision._cache_key(raw, gemini_vision.FACE_PROMPT[:50]))
    cache.write_text("{}")

    photo = Photo(user_id=1, photo_type="front", file_path=str(file))
    db_session.add(photo)
    db_session.commit()
    a = Analysis(photo_id=photo.id)
    a.set_face_data({"swelling": {"level": "low"}})
    db_session.add(a)
    db_session.commit()

    import asyncio
    from backend.routers.photos import delete_photo
    asyncio.run(delete_photo(photo.id, db=db_session))

    assert not photo_path(str(file)).exists()
    assert not cache.exists()
    assert db_session.query(Analysis).count() == 0


def test_startup_removes_orphaned_analyses(monkeypatch):
    from sqlalchemy import create_engine, text
    from backend import database
    from backend.models.base import Base
    import backend.models  # noqa: F401  registers tables

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO analyses (photo_id) VALUES (12345)"))
    monkeypatch.setattr(database, "engine", engine)
    assert database.remove_orphaned_analyses() == 1
    assert database.remove_orphaned_analyses() == 0
