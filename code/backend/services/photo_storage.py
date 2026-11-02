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


# --- Plan 4.9: photo quality check before analysis -------------------------
# Comparisons over time only make sense for usable photos. Thresholds are
# deliberately loose (flag only clearly bad photos): sharpness = variance of the
# edge map of a 512 px grayscale copy (calibrated 2026-11-02: sharp ~1800,
# blur radius 3 ~70, radius 4 ~30, flat 0).
MIN_SHORT_SIDE = 480
MIN_SHARPNESS = 30.0
MIN_BRIGHTNESS = 50
MAX_BRIGHTNESS = 215
MAX_CLIPPED = 0.25  # share of pixels at or above 250


def quality_check(content: bytes) -> dict:
    """{"ok": bool, "problems": [Polish messages], "metrics": {...}}."""
    from PIL import ImageFilter, ImageStat

    with Image.open(io.BytesIO(content)) as img:
        width, height = img.size
        gray = img.convert("L")
    problems = []
    if min(width, height) < MIN_SHORT_SIDE:
        problems.append(f"Za mała rozdzielczość ({width}×{height}) — zrób zdjęcie w pełnej rozdzielczości.")

    small = gray.copy()
    small.thumbnail((512, 512))
    stat = ImageStat.Stat(small)
    brightness = stat.mean[0]
    histogram = small.histogram()
    clipped = sum(histogram[250:]) / max(sum(histogram), 1)
    if brightness < MIN_BRIGHTNESS:
        problems.append("Zdjęcie jest za ciemne — stań przodem do okna lub włącz światło.")
    elif brightness > MAX_BRIGHTNESS or clipped > MAX_CLIPPED:
        problems.append("Zdjęcie jest prześwietlone — unikaj ostrego światła i lampy błyskowej.")

    edges = small.filter(ImageFilter.FIND_EDGES)
    w, h = edges.size
    if w > 8 and h > 8:
        edges = edges.crop((4, 4, w - 4, h - 4))
    sharpness = ImageStat.Stat(edges).var[0]
    if sharpness < MIN_SHARPNESS:
        problems.append("Zdjęcie jest nieostre — oprzyj telefon albo użyj samowyzwalacza.")

    return {
        "ok": not problems,
        "problems": problems,
        "metrics": {
            "width": width,
            "height": height,
            "brightness": round(brightness, 1),
            "sharpness": round(sharpness, 1),
        },
    }
