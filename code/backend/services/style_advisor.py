"""Style advice from the qualitative analysis (plan 4.1-4.8).

Rule-based (no AI call, deterministic, testable). Every item carries its level:
- "porada stylistyczna" - grooming/style convention, not a health claim,
- "hipoteza" - plausible but weak/no evidence (e.g. colour seasons, D9),
- an EVIDENCE_DB id when a sourced entry backs it.
Nothing here rates the person (LC-9): advice works with shapes and states,
never with "better/worse looking". Health flags (LC-8) block risky items.
"""

STYLE = "porada stylistyczna"
HYPOTHESIS = "hipoteza"


def _item(text: str, level: str = STYLE, evidence_id: str | None = None, **extra) -> dict:
    out = {"text": text, "level": level}
    if evidence_id:
        out["evidence_id"] = evidence_id
    out.update(extra)
    return out


# --- 4.2 hair ---------------------------------------------------------------
# Hairstyles per face shape: (name, what to tell the barber/hairdresser, styling minutes)
HAIRSTYLES = {
    "oval": [
        ("Klasyczne cięcie z przedziałkiem", "boki krótko nożyczkami lub maszynką 3-4, góra 5-7 cm, naturalny przedziałek", 5),
        ("Krótka tekstura (crop)", "boki 2-3, góra 3-4 cm z teksturą, grzywka lekko na czoło", 3),
        ("Średnia długość zaczesana do tyłu", "boki 4-6 cm, góra 8-10 cm, stopniowanie bez ostrego przejścia", 8),
    ],
    "round": [
        ("Wyższa góra, krótkie boki", "boki krótko (fade lub 2), góra 6-8 cm uniesiona do góry — wydłuża twarz", 6),
        ("Quiff", "boki krótko, góra 7-9 cm, przód najdłuższy, układany do góry i do tyłu", 8),
        ("Asymetryczny przedziałek", "boki 3, góra 5-7 cm, wyraźny przedziałek z boku", 5),
    ],
    "square": [
        ("Krótkie klasyczne cięcie", "boki 2-3, góra 4-5 cm, miękkie przejścia — nie podkreślać kątów dodatkowo", 3),
        ("Tekstura z lekką grzywką", "boki 3, góra 5-6 cm cieniowana, przód lekko na czoło", 4),
        ("Średnie, luźne", "boki 4-5 cm, góra 7-9 cm, cieniowanie dla miękkości", 6),
    ],
    "oblong": [
        ("Grzywka na czoło", "boki nie za krótko (4-5), góra 5-6 cm, grzywka skraca optycznie twarz", 4),
        ("Średnia długość po bokach", "boki 5-6 cm, góra 6 cm — objętość po bokach, nie na górze", 6),
        ("Crop z grzywką", "boki 3, góra 3-4 cm, prosta grzywka", 3),
    ],
    "heart": [
        ("Średnia długość z objętością na dole", "boki 4-6 cm, góra 6-7 cm, bez wysokiej objętości na czubku", 6),
        ("Grzywka na bok", "boki 4, góra 6 cm, grzywka zaczesana na bok", 5),
        ("Luźne, dłuższe pasma", "całość 7-10 cm, cieniowanie do linii żuchwy", 8),
    ],
    "diamond": [
        ("Grzywka i pełniejsze boki", "boki 4-5 cm (nie za krótko), góra 5-7 cm z grzywką", 5),
        ("Teksturowany fringe", "boki 3-4, góra 5 cm, tekstura opadająca na czoło", 4),
        ("Zaczesanie do tyłu z objętością przy skroniach", "boki 4-5, góra 8 cm", 8),
    ],
}
THINNING_CUTS = [
    ("Krótko, równo", "całość krótko (maszynka 2-4 lub nożyczki 2-3 cm) — kontrast z linią włosów maleje", 2),
    ("Krótki crop z teksturą", "boki 2, góra 2-3 cm z teksturą do przodu, maskuje zakola", 3),
]
HAIR_TYPE_TIPS = {
    "curly": "Loki: nie przerzedzać degażówką na sucho; strzyc na długość, która pozwala lokom się ułożyć.",
    "coily": "Mocno kręcone: krem nawilżający bez spłukiwania; strzyżenie na sucho u kogoś, kto pracuje z takimi włosami.",
    "wavy": "Fale: pasta matowa lub sól morska podkreślą teksturę bez sztywności.",
    "straight": "Proste: puder/pasta dla objętości u nasady; przy gładkim efekcie — pomada.",
}


def hair_advice(face: dict, hair: dict, goals: dict) -> dict:
    shape = face.get("face_shape") or "unclear"
    minutes = goals.get("styling_minutes")
    thinning = (
        hair.get("hairline_status") in ("moderate_recession", "advanced_recession")
        or hair.get("density_status") == "thin"
        or hair.get("crown_density") == "thinning"
    )
    pool = list(THINNING_CUTS) if thinning else []
    pool += HAIRSTYLES.get(shape, HAIRSTYLES["oval"])
    if minutes is not None:
        fitting = [h for h in pool if h[2] <= minutes]
        pool = fitting or sorted(pool, key=lambda h: h[2])[:1]
    proposals = [
        {"name": name, "tell_barber": tell, "styling_minutes": mins, "level": STYLE}
        for name, tell, mins in pool[:3]
    ]
    notes = []
    if shape == "unclear":
        notes.append(_item("Kształt twarzy nie był czytelny na zdjęciu — propozycje są ogólne."))
    else:
        notes.append(_item(
            "Dopasowanie fryzury do kształtu twarzy to konwencja fryzjerska bez badań — traktuj jako punkt wyjścia.",
            HYPOTHESIS,
        ))
    tip = HAIR_TYPE_TIPS.get(hair.get("hair_type"))
    if tip:
        notes.append(_item(tip))
    if thinning:
        notes.append(_item(
            "Przerzedzenie: zobacz rekomendacje dla włosów (minoksydyl — RCT, wymaga konsultacji z lekarzem).",
            "rct", evidence_id="hair_001",
        ))
    if goals.get("constraints"):
        notes.append(_item(f"Uwzględnij swoje ograniczenia: {goals['constraints']}"))
    return {"proposals": proposals, "notes": notes, "preview_available": True}


# --- 4.1 brows --------------------------------------------------------------
def brows_advice(face: dict) -> list[dict]:
    brows = face.get("brows") or {}
    if not brows:
        return []
    out = []
    if brows.get("unibrow"):
        out.append(_item("Usuń włoski między brwiami (pęseta lub wosk) — tylko środek, bez zmiany kształtu łuku."))
    if brows.get("density") == "dense":
        out.append(_item("Gęste brwi: przytnij najdłuższe włoski nożyczkami po wyczesaniu do góry; regulować tylko nadmiar pod łukiem."))
    if brows.get("density") == "sparse":
        out.append(_item("Rzadkie brwi: nie wyskubuj; żel koloryzujący wypełnia bez efektu „rysowanych”."))
        out.append(_item(
            "Serum z bimatoprostem działa, ale jest lekiem na receptę — tylko po konsultacji z lekarzem.",
            HYPOTHESIS,
        ))
    if brows.get("symmetry") == "clear_asymmetry":
        out.append(_item("Wyraźna asymetria: pierwszą regulację zrób u stylisty brwi, potem tylko utrzymuj kształt."))
    if not out:
        out.append(_item("Brwi nie wymagają zmian — wystarczy wyczesanie i ewentualnie przezroczysty żel."))
    return out


# --- 4.3 beard --------------------------------------------------------------
BEARD_BY_SHAPE = {
    "round": "Dłuższa broda na brodzie, krótsze boki — wydłuża twarz.",
    "square": "Krótsza, zaokrąglona broda lub zarost 3-5 mm — łagodzi kąty żuchwy.",
    "oblong": "Pełniejsze boki, krótsza broda pod brodą — nie wydłużać twarzy.",
    "oval": "Pasuje większość form; zarost 3-10 mm z wyraźną linią szyi.",
    "heart": "Pełniejsza broda w dolnej części (np. full beard) — równoważy szersze czoło.",
    "diamond": "Broda z objętością na brodzie, krótkie boki.",
}


def beard_advice(face: dict, health: dict) -> list[dict]:
    beard = face.get("beard") or {}
    if not beard or not beard.get("present"):
        return []
    out = []
    shape_tip = BEARD_BY_SHAPE.get(face.get("face_shape"))
    if shape_tip:
        out.append(_item(shape_tip, HYPOTHESIS))
    if beard.get("neckline") == "undefined":
        out.append(_item("Wyznacz linię szyi: ok. dwa palce nad jabłkiem Adama, łuk do tyłu za uszy; poniżej golić."))
    if beard.get("evenness") == "patchy" or beard.get("density") == "sparse":
        out.append(_item("Nierówny lub rzadki zarost: noś krótko (3-6 mm) — przy tej długości luki są najmniej widoczne."))
        if health.get("heart_disease"):
            out.append(_item("Minoksydyl na brodę jest przeciwwskazany przy chorobie serca (LC-8).", "blokada"))
        else:
            out.append(_item(
                "Minoksydyl miejscowo na brodę: dowody ograniczone, skutki uboczne możliwe — tylko po konsultacji z lekarzem.",
                HYPOTHESIS,
            ))
    out.append(_item("Olejek lub balsam do brody po myciu — mniej swędzenia i suchej skóry pod zarostem."))
    return out


# --- 4.5 eye area -----------------------------------------------------------
def eye_advice(face: dict, health: dict) -> list[dict]:
    eyes = face.get("eye_area") or {}
    out = []
    if eyes.get("dark_circles") in ("mild", "marked") or eyes.get("puffiness") in ("mild", "marked"):
        out.append(_item(
            "Niedobór snu daje widocznie zmęczony wygląd (RCT) — 7-9 h snu to pierwszy krok.", "rct", evidence_id="sleep_001",
        ))
    if eyes.get("puffiness") in ("mild", "marked"):
        out.append(_item("Rano zimny okład 5 min.", "expert", evidence_id="beauty_003"))
        if not health.get("kidney_disease"):
            out.append(_item("Mniej soli wieczorem — opuchnięcie bywa związane z sodem.", "expert", evidence_id="nutrition_002"))
    if eyes.get("dark_circles") == "marked":
        out.append(_item("Wyraźne, stałe cienie mogą być genetyczne lub barwnikowe — dermatolog dobierze leczenie.", HYPOTHESIS))
    return out


# --- 4.7 glasses ------------------------------------------------------------
FRAMES = {
    "round": "Prostokątne lub kwadratowe oprawki — dodają kątów.",
    "square": "Okrągłe lub owalne oprawki — łagodzą kąty.",
    "oblong": "Wyższe oprawki, mocniejszy mostek — skracają optycznie twarz.",
    "oval": "Pasuje większość kształtów; oprawki szerokości twarzy.",
    "heart": "Oprawki szersze na dole lub bezramkowe, lekkie u góry.",
    "diamond": "Owalne lub z wyraźną górną krawędzią (browline).",
}


def glasses_advice(face: dict) -> list[dict]:
    if not face.get("glasses"):
        return []
    tip = FRAMES.get(face.get("face_shape"))
    return [_item(tip, HYPOTHESIS)] if tip else []


# --- 4.4 / 4.8 body and clothing ---------------------------------------------
def body_advice(body: dict) -> list[dict]:
    proportions = body.get("proportions") or {}
    out = []
    if proportions.get("shoulders_vs_hips") == "narrower":
        out.append(_item("Marynarki z lekko zaznaczonym ramieniem, koszulki z poziomym akcentem u góry; priorytet barków jest w ForgeBody."))
    if proportions.get("torso_vs_legs") == "long_torso":
        out.append(_item("Spodnie z wyższym stanem, krótsze góry — wydłużają nogi."))
    if proportions.get("torso_vs_legs") == "short_torso":
        out.append(_item("Niższy stan spodni, góry do linii bioder."))
    out.append(_item("Najwięcej zmienia dopasowanie: ramię koszuli kończy się na kości barkowej, długość rękawa do nadgarstka, spodnie bez fałd na dole."))
    return out


UNDERTONE_COLORS = {
    "warm": "Ciepłe barwy: oliwkowy, musztardowy, rdzawy, kremowy, brąz.",
    "cool": "Chłodne barwy: granat, szary, butelkowa zieleń, bordo, czysta biel.",
    "neutral": "Większość kolorów; przy twarzy unikaj bardzo jaskrawych neonów.",
}


def color_advice(face: dict) -> list[dict]:
    tip = UNDERTONE_COLORS.get(face.get("skin_undertone"))
    if not tip:
        return []
    return [_item(f"{tip} Dobór kolorów do „typu urody” nie ma potwierdzenia w badaniach — sprawdź, co Tobie pasuje.", HYPOTHESIS)]


def style_advice(latest: dict, profile_goals: dict, health: dict) -> dict:
    face = latest.get("face") or {}
    hair = latest.get("hair") or {}
    body = latest.get("body") or {}
    return {
        "hair": hair_advice(face, hair, profile_goals) if (face or hair) else None,
        "brows": brows_advice(face),
        "beard": beard_advice(face, health),
        "eyes": eye_advice(face, health),
        "glasses": glasses_advice(face),
        "clothing": body_advice(body) if body else [],
        "colors": color_advice(face),
        "has_front_photo": bool(face),
        "has_side_photo": bool(body),
    }
