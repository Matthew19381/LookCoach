"""What other modules should do for the user's looks goals (plan 3.2 / 3.4, LC-4).

LookCoach does not write training plans or diets. It turns the qualitative
analysis into *needs* that ForgeBody and Dieta act on:
- training_needs  -> `aesthetic_priority` for ForgeBody (muscle groups in
  ForgeBody's own vocabulary, see ForgeBody routers/directives.py),
- nutrition_needs -> `nutrition_needs` for Dieta (only items with evidence or
  an explicit hypothesis flag; Health Safety applied, LC-8).
"""
import re

# ForgeBody's lookcoach_to_internal keys
FORGEBODY_GROUPS = (
    "side_delts", "rear_delts", "upper_chest", "lower_chest", "lats_width",
    "biceps_peak", "triceps_long", "quads", "glutes", "calves", "abs",
)

# free-text muscle names from the vision model -> ForgeBody groups
_SYNONYMS: list[tuple[str, tuple[str, ...]]] = [
    (r"rear|posterior delt", ("rear_delts",)),
    (r"delt|shoulder", ("side_delts",)),
    (r"upper chest|upper pec|clavicular", ("upper_chest",)),
    (r"lower chest|lower pec", ("lower_chest",)),
    (r"chest|pec", ("upper_chest",)),
    (r"lat|back width|v.?taper", ("lats_width",)),
    (r"bicep", ("biceps_peak",)),
    (r"tricep|arm", ("triceps_long",)),
    (r"quad|thigh|leg", ("quads",)),
    (r"glute|butt|hip", ("glutes",)),
    (r"calf|calves", ("calves",)),
    (r"abs|abdom|core", ("abs",)),
]

DEFAULT_WEEKS = 4


def _groups_for(name: str) -> tuple[str, ...]:
    text = name.lower().strip()
    if text in FORGEBODY_GROUPS:
        return (text,)
    for pattern, groups in _SYNONYMS:
        if re.search(pattern, text):
            return groups
    return ()


def training_needs(body: dict | None) -> dict | None:
    """Muscle groups to prioritise, or None when the analysis gives no reason to."""
    if not body:
        return None
    groups: list[str] = []
    reasons: list[str] = []

    for m in body.get("missing_muscles", []) or []:
        if not isinstance(m, dict) or m.get("priority") not in ("high", "medium"):
            continue
        mapped = _groups_for(str(m.get("muscle", "")))
        for g in mapped:
            if g not in groups:
                groups.append(g)
        if mapped:
            reasons.append(f"{m.get('muscle')} ({m.get('priority')})")

    raw_posture = body.get("posture")
    posture: dict = raw_posture if isinstance(raw_posture, dict) else {}
    if posture.get("shoulder_position") == "forward" or posture.get("head_position") == "forward":
        # Rounded shoulders / forward head: upper-back accessories (face pulls etc.)
        if "rear_delts" not in groups:
            groups.append("rear_delts")
        reasons.append("postawa: wysunięte barki/głowa")

    if not groups:
        return None
    return {
        "muscle_groups": groups,
        "duration_weeks": DEFAULT_WEEKS,
        "reason": "Analiza zdjęcia (LookCoach): " + ", ".join(reasons),
        # posture_002 = Face Pulls (expert level) - closest EVIDENCE_DB entry
        "evidence_level": "expert",
    }


def nutrition_needs(face: dict | None, skin: dict | None, health: dict | None) -> dict | None:
    """Needs for Dieta, each with its evidence id; None when nothing applies."""
    face, skin, health = face or {}, skin or {}, health or {}
    items: list[dict] = []
    payload: dict = {}

    swelling = (face.get("swelling") or {}).get("level") if isinstance(face.get("swelling"), dict) else None
    if swelling in ("medium", "high") and not health.get("kidney_disease"):
        payload["sodium_limit_mg"] = 2300
        items.append({
            "need": "sodium_limit_mg", "value": 2300, "evidence_id": "nutrition_002",
            "evidence_level": "expert", "reason": f"obrzęk twarzy: {swelling}",
        })

    problems = [p for p in skin.get("problems", []) or [] if isinstance(p, dict)]
    acne = [p for p in problems if "acne" in str(p.get("issue", "")).lower()
            and p.get("severity") in ("moderate", "significant")]
    if acne:
        payload["low_glycemic_load"] = True
        items.append({
            "need": "low_glycemic_load", "value": True, "evidence_id": "nutrition_005",
            "evidence_level": "rct", "reason": f"trądzik: {acne[0].get('severity')}",
        })

    if not items:
        return None
    payload["items"] = items
    payload["reason"] = "Analiza zdjęcia (LookCoach): " + "; ".join(i["reason"] for i in items)
    if health.get("kidney_disease"):
        payload["note"] = "Choroba nerek: bez zaleceń dot. sodu i wody (LC-8)."
    return payload
