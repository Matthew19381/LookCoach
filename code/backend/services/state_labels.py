"""Qualitative state labels extracted from a stored analysis (LC-9).

Only categorical fields the vision prompts already return - no numbers, no
scores of the person. Used to compare two photo sessions in words
("obrzęk: średni → niski") instead of the fake "Look Score" chart that was
removed 2026-11-02.
"""
from typing import Any

# (section, path, Polish label)
FIELDS: list[tuple[str, tuple[str, ...], str]] = [
    ("face", ("swelling", "level"), "Obrzęk twarzy"),
    ("face", ("muscle_tension", "level"), "Napięcie mięśni twarzy"),
    ("face", ("skin_quality", "status"), "Stan skóry twarzy"),
    ("skin", ("skin_type",), "Typ skóry"),
    ("skin", ("hydration_status",), "Nawilżenie skóry"),
    ("hair", ("hairline_status",), "Linia włosów"),
    ("hair", ("density_status",), "Gęstość włosów"),
    ("hair", ("crown_density",), "Czubek głowy"),
    ("face", ("brows", "density"), "Brwi — gęstość"),
    ("face", ("brows", "symmetry"), "Brwi — symetria"),
    ("face", ("beard", "density"), "Zarost — gęstość"),
    ("face", ("beard", "evenness"), "Zarost — równomierność"),
    ("face", ("eye_area", "dark_circles"), "Cienie pod oczami"),
    ("face", ("eye_area", "puffiness"), "Opuchnięcie pod oczami"),
    ("smile", ("discoloration",), "Zęby — przebarwienia"),
    ("smile", ("gums",), "Dziąsła"),
]

VALUE_PL = {
    "low": "niski",
    "medium": "średni",
    "high": "wysoki",
    "good": "dobry",
    "fair": "przeciętny",
    "needs_attention": "wymaga uwagi",
    "adequate": "wystarczające",
    "dry": "sucha",
    "oily": "tłusta",
    "combination": "mieszana",
    "normal": "normalna",
    "unknown": "nieznany",
    "stable": "stabilna",
    "mild_recession": "lekka recesja",
    "moderate_recession": "umiarkowana recesja",
    "advanced_recession": "zaawansowana recesja",
    "thin": "rzadkie",
    "full": "gęste",
    "thinning": "przerzedzenie",
    "unclear": "nie do oceny",
    "sparse": "rzadkie",
    "dense": "gęste",
    "symmetric": "symetryczne",
    "slight_asymmetry": "lekka asymetria",
    "clear_asymmetry": "wyraźna asymetria",
    "none": "brak",
    "even": "równomierny",
    "patchy": "nierównomierny",
    "not_applicable": "nie dotyczy",
    "mild": "lekkie",
    "marked": "wyraźne",
    "redness": "zaczerwienienie",
    "receding": "cofanie się",
}


def _dig(data: dict, path: tuple[str, ...]) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def state_labels(analysis) -> dict[str, str]:
    """{label: value_pl} for every categorical field present in the analysis."""
    if analysis is None:
        return {}
    sections = {
        "face": analysis.get_face_data(),
        "skin": analysis.get_skin_data(),
        "hair": analysis.get_hair_data(),
        "smile": analysis.get_smile_data(),
    }
    out: dict[str, str] = {}
    for section, path, label in FIELDS:
        value = _dig(sections.get(section) or {}, path)
        if isinstance(value, str) and value:
            out[label] = VALUE_PL.get(value, value)
    return out


def compare_labels(before: dict[str, str], after: dict[str, str]) -> list[dict[str, Any]]:
    """Side-by-side list for every label known in either session."""
    rows = []
    for _section, _path, label in FIELDS:
        if label in before or label in after:
            b, a = before.get(label), after.get(label)
            rows.append({"area": label, "before": b, "after": a, "changed": b != a})
    return rows
