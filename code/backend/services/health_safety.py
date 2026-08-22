"""Health Safety Layer (NEURO_PLAN F-3 / LC-8).

Checks recommendations against user health profile:
- hard contraindication match -> recommendation is dropped from the list
- high-risk items (retinoids, minoxidil, peels...) get a mandatory
  "consult a professional" disclaimer even for healthy users
"""

from .evidence_engine import EVIDENCE_DB

# EVIDENCE_DB contraindications value -> UserProfile.health JSON flag
CONTRAINDICATION_FLAGS = {
    "pregnancy": "pregnancy",
    "heart_disease": "heart_disease",
    "kidney_disease": "kidney_disease",
    "back_injury": "back_injury",
    "shoulder_injury": "shoulder_injury",
    "knee_injury": "knee_injury",
    "sensitive_skin": "sensitive_skin",
}

# Items that always warrant professional supervision, regardless of health flags.
HIGH_RISK_DISCLAIMERS = {
    "skincare_002": "Consult a dermatologist before starting retinoids.",
    "hair_001": "Consult a doctor before starting minoxidil.",
    "skincare_005": "Consult a dermatologist before chemical peels.",
}


def check_contraindications(recommendation_id: str, user_profile: dict) -> list[str]:
    """Return hard-block reasons if the recommendation conflicts with the
    user's health profile. Empty list means no contraindication found."""
    entry = next((e for e in EVIDENCE_DB if e["id"] == recommendation_id), None)
    if not entry:
        return []

    health = (user_profile or {}).get("health") or {}
    contra_raw = entry.get("contraindications") or "none"
    warnings = []
    for flag in (f.strip() for f in contra_raw.split(",")):
        if not flag or flag == "none":
            continue
        health_key = CONTRAINDICATION_FLAGS.get(flag)
        if health_key and health.get(health_key):
            warnings.append(
                f"Contraindication: {flag.replace('_', ' ')} — "
                f"consult your doctor before starting {entry['name']}"
            )
    return warnings


def apply_high_risk_disclaimer(recommendation_id: str) -> str | None:
    """Mandatory disclaimer text for high-risk items, None otherwise."""
    return HIGH_RISK_DISCLAIMERS.get(recommendation_id)


def apply_safety_filter(recommendations: list, user_profile: dict) -> list:
    """Drop contraindicated items; attach disclaimers to the rest."""
    safe = []
    for rec in recommendations:
        blocks = check_contraindications(rec.get("id", ""), user_profile)
        if blocks:
            continue  # hard block — never shown to this user

        disclaimer = apply_high_risk_disclaimer(rec.get("id", ""))
        warnings = [disclaimer] if disclaimer else []
        if warnings:
            rec = dict(rec)
            rec["warnings"] = warnings
        safe.append(rec)
    return safe
