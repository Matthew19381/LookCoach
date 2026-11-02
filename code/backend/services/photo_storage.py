"""Validation and sanitising of uploaded photos (plan 2.1).

Body photos are sensitive. Until 2026-11-02 the upload stored whatever bytes
came in, under the extension from the client's file name - an `.html` file was
served back from /uploads on the app's own origin, and phone photos kept their
EXIF GPS position.

Now: the content must decode as JPEG/PNG/WEBP (checked by Pillow, not by the
name), size is capped, and the image is re-encoded - which drops all metadata
(EXIF incl. GPS) - after applying the EXIF rotation so the photo stays upright.
HEIC is not accepted (Pillow cannot read it without pillow-heif); browsers
usually convert iPhone photos to JPEG on upload.
"""
import io

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_PIXELS = 40_000_000  # ~ 7300 x 5500; above that it is not a phone photo

# Pillow format -> (stored extension, save kwargs)
ALLOWED = {
    "JPEG": ("jpg", {"quality": 92, "optimize": True}),
    "PNG": ("png", {"optimize": True}),
    "WEBP": ("webp", {"quality": 92}),
}


class InvalidPhoto(ValueError):
    """Message is safe to show to the user (Polish)."""


def sanitize_image(content: bytes) -> tuple[bytes, str]:
    """Return (clean image bytes without metadata, extension) or raise InvalidPhoto."""
    if not content:
        raise InvalidPhoto("Plik jest pusty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise InvalidPhoto(f"Zdjęcie jest za duże (limit {MAX_UPLOAD_BYTES // (1024 * 1024)} MB).")
    try:
        with Image.open(io.BytesIO(content)) as probe:
            fmt = probe.format
            width, height = probe.size
            probe.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError) as e:
        raise InvalidPhoto("To nie jest obsługiwany obraz (dozwolone: JPEG, PNG, WEBP).") from e
    if fmt not in ALLOWED:
        raise InvalidPhoto("Nieobsługiwany format zdjęcia (dozwolone: JPEG, PNG, WEBP).")
    if width * height > MAX_PIXELS:
        raise InvalidPhoto("Zdjęcie ma zbyt dużą rozdzielczość.")

    ext, save_kwargs = ALLOWED[fmt]
    # verify() leaves the image unusable - open again to re-encode.
    with Image.open(io.BytesIO(content)) as img:
        img = ImageOps.exif_transpose(img)
        if fmt == "JPEG" and img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        out = io.BytesIO()
        # No exif=/pnginfo= passed -> metadata (EXIF, GPS, XMP, text chunks) is dropped.
        img.save(out, format=fmt, **save_kwargs)
    return out.getvalue(), ext
