"""Plan 4.1-4.8: style advice is qualitative, labelled, and respects health flags."""
from backend.services.style_advisor import style_advice

FACE = {
    "face_shape": "round",
    "brows": {"density": "sparse", "symmetry": "symmetric", "unibrow": True},
    "beard": {"present": True, "density": "sparse", "evenness": "patchy", "neckline": "undefined"},
    "eye_area": {"dark_circles": "mild", "puffiness": "marked"},
    "glasses": True,
    "skin_undertone": "cool",
}
LEVELS = {"porada stylistyczna", "hipoteza", "rct", "expert", "blokada"}


def _all_items(advice):
    items = []
    for key, value in advice.items():
        if isinstance(value, list):
            items += value
    items += advice["hair"]["notes"] + advice["hair"]["proposals"]
    return items


def test_every_item_has_a_level_and_no_scores():
    advice = style_advice({"face": FACE, "hair": {"hair_type": "wavy"}, "body": {"proportions": {}}}, {}, {})
    for item in _all_items(advice):
        assert item["level"] in LEVELS
        assert "score" not in item


def test_round_face_hairstyles_and_barber_text():
    hair = style_advice({"face": FACE, "hair": {}}, {}, {})["hair"]
    assert len(hair["proposals"]) == 3
    assert all(p["tell_barber"] for p in hair["proposals"])
    assert any(n["level"] == "hipoteza" for n in hair["notes"])  # face-shape matching is a convention


def test_styling_time_limits_proposals():
    hair = style_advice({"face": FACE, "hair": {}}, {"styling_minutes": 5}, {})["hair"]
    assert hair["proposals"] and all(p["styling_minutes"] <= 5 for p in hair["proposals"])


def test_thinning_puts_short_cuts_first_and_links_evidence():
    hair = style_advice({"face": FACE, "hair": {"hairline_status": "moderate_recession"}}, {}, {})["hair"]
    assert hair["proposals"][0]["name"] == "Krótko, równo"
    assert any(n.get("evidence_id") == "hair_001" for n in hair["notes"])


def test_brows_unibrow_and_sparse():
    brows = style_advice({"face": FACE}, {}, {})["brows"]
    texts = " ".join(i["text"] for i in brows)
    assert "między brwiami" in texts and "nie wyskubuj" in texts


def test_beard_minoxidil_blocked_with_heart_disease():
    """LC-8."""
    beard = style_advice({"face": FACE}, {}, {"heart_disease": True})["beard"]
    assert any(i["level"] == "blokada" for i in beard)
    assert not any("Minoksydyl miejscowo" in i["text"] for i in beard)


def test_kidney_disease_skips_sodium_tip():
    eyes = style_advice({"face": FACE}, {}, {"kidney_disease": True})["eyes"]
    assert not any(i.get("evidence_id") == "nutrition_002" for i in eyes)


def test_colors_are_always_hypothesis():
    colors = style_advice({"face": FACE}, {}, {})["colors"]
    assert colors and all(c["level"] == "hipoteza" for c in colors)


def test_no_photos_no_advice():
    advice = style_advice({"face": None, "hair": None, "body": None}, {}, {})
    assert advice["hair"] is None and advice["brows"] == [] and advice["clothing"] == []


def test_teeth_advice_from_optional_smile_photo():
    """Plan 4.6 (D12)."""
    advice = style_advice({"face": FACE, "smile": {"discoloration": "marked", "gums": "redness"}}, {}, {})
    texts = " ".join(i["text"] for i in advice["teeth"])
    assert "higienizacja" in texts and "dziąseł" in texts
    assert style_advice({"face": FACE}, {}, {})["teeth"] == []  # no smile photo -> nothing
