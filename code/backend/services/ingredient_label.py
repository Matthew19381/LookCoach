"""Product ingredient lists (INCI): parse, find actives, flag irritants, check conflicts.

Deterministic and local - the photo scan only uses AI to read the label text
(gemini_vision.read_ingredient_label); everything below works for pasted text too.

Actives map to the SKINCARE_INGREDIENTS catalogue names so rotation, conflict checks
and tolerance (logged skin reactions) use the same vocabulary as the routine.
"""

import re

# (INCI fragment, lowercase) -> catalogue name. Order matters: specific before generic.
ACTIVE_PATTERNS: list[tuple[str, str]] = [
    ("retinal", "Retinaldehyde"),
    ("retinaldehyde", "Retinaldehyde"),
    ("hydroxypinacolone retinoate", "Retinol 0.25-1%"),
    ("retinyl", "Retinol 0.25-1%"),
    ("retinol", "Retinol 0.25-1%"),
    ("tretinoin", "Retinol 0.25-1%"),
    ("adapalene", "Retinol 0.25-1%"),
    ("ascorbic acid", "Vitamin C 10-20%"),
    ("ascorbyl", "Vitamin C 10-20%"),
    ("ascorbate", "Vitamin C 10-20%"),
    ("niacinamide", "Niacinamide 5-10%"),
    ("glycolic acid", "AHA (Glycolic Acid)"),
    ("mandelic acid", "AHA (Glycolic Acid)"),
    ("lactic acid", "Lactic Acid"),
    ("salicylic acid", "BHA (Salicylic Acid)"),
    ("betaine salicylate", "BHA (Salicylic Acid)"),
    ("azelaic acid", "Azelaic Acid"),
    ("azeloyl", "Azelaic Acid"),
    ("benzoyl peroxide", "Benzoyl Peroxide"),
    ("sodium hyaluronate", "Hyaluronic Acid"),
    ("hyaluronic acid", "Hyaluronic Acid"),
    ("ceramide", "Ceramide Moisturizer"),
    ("squalane", "Squalane Oil"),
    ("zinc pca", "Zinc PCA"),
    ("tocopherol", "Vitamin E"),
    ("madecassoside", "Madecassoside"),
    ("centella asiatica", "Centella Asiatica"),
    ("asiaticoside", "Centella Asiatica"),
    ("peptide", "Peptide Serum"),
    ("palmitoyl", "Peptide Serum"),
]

# Common irritation triggers worth knowing about - information, not a verdict.
FLAG_PATTERNS: list[tuple[str, str]] = [
    ("parfum", "zapach (parfum) — częsty powód podrażnień wrażliwej skóry"),
    ("fragrance", "zapach (fragrance) — częsty powód podrażnień wrażliwej skóry"),
    ("alcohol denat", "alkohol denaturowany — może przesuszać"),
    ("limonene", "limonen (alergen zapachowy)"),
    ("linalool", "linalol (alergen zapachowy)"),
    ("citral", "cytral (alergen zapachowy)"),
    ("eugenol", "eugenol (alergen zapachowy)"),
    ("methylisothiazolinone", "metyloizotiazolinon — silny alergen konserwujący"),
]

HEADER = re.compile(r"^\s*(ingredients|inci|skład|sklad|zutaten|composition)\s*[:：]\s*", re.I)


def parse_inci(text: str) -> list[str]:
    """Split a label into ingredients: commas/semicolons/bullets, header and '*' notes removed."""
    text = HEADER.sub("", text.replace("\n", " "))
    parts = re.split(r"[,;•·]|\s\|\s", text)
    out = []
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip(" .*\t")
        if 1 < len(p) < 120:
            out.append(p)
    return out


def analyze_ingredients(ingredients: list[str]) -> dict:
    """{"actives": [{"name", "inci", "position"}], "flags": [str]} (position = order on the label, 1-based)."""
    actives: dict[str, dict] = {}
    flags: list[str] = []
    for i, ing in enumerate(ingredients, 1):
        low = ing.lower()
        for pat, name in ACTIVE_PATTERNS:
            if pat in low:
                actives.setdefault(name, {"name": name, "inci": ing, "position": i})
                break
        for pat, msg in FLAG_PATTERNS:
            if pat in low and msg not in flags:
                flags.append(msg)
    return {"actives": list(actives.values()), "flags": flags}


def concentration_hint(position: int, total: int) -> str:
    """INCI lists above 1 % in descending order; the tail is usually <1 %. A rough hint only."""
    if total and position > max(6, total * 0.6):
        return "prawdopodobnie niskie stężenie (koniec listy)"
    return ""
