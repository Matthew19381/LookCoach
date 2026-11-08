"""Strona "Wideo": techniki z uczciwym linkiem do wyszukiwania na YouTube.

Do 2026-11-08 VIDEO_DB zawierał 6 zmyślonych filmów: jeden link prowadził do
teledysku (watch?v=dQw4w9WgXcQ), pięć do nieistniejących `watch?v=example1..5`,
a kanały ("Skincare Pro", "Beauty Master"...) i długości były wymyślone.
Technika gua sha była zapisana jako "gua sha", a filtr szukał "gua_sha", więc
nigdy nie była polecana.

Teraz każda pozycja to technika z linkiem do WYNIKÓW wyszukiwania YouTube (nie do
konkretnego filmu, którego nikt nie sprawdził) i z poziomem dowodu wg LC-1:
- techniki pielęgnacyjne bez badań klinicznych na wygląd są oznaczone `[HIPOTEZA]`,
- porady fryzjerskie są oznaczone jako porada stylistyczna (nie twierdzenie naukowe).
Źródła sprawdzone 2026-11-08 (PubMed).
"""
from urllib.parse import quote_plus


def _search_url(phrase: str) -> str:
    return "https://www.youtube.com/results?search_query=" + quote_plus(phrase)


VIDEO_DB = [
    {
        "id": "gua_sha",
        "title": "Gua sha (masaż twarzy płytką)",
        "technique": "gua_sha",
        "search_phrase": "gua sha twarz instrukcja",
        "evidence_level": "hipoteza",
        "evidence_note": "[HIPOTEZA] Brak badań klinicznych pokazujących wpływ na wygląd twarzy.",
        "description": "Technika masażu płytką. Traktuj jako przyjemny rytuał, nie sposób na zmianę rysów.",
    },
    {
        "id": "lymphatic_drainage",
        "title": "Drenaż limfatyczny twarzy",
        "technique": "lymphatic_drainage",
        "search_phrase": "drenaż limfatyczny twarzy instrukcja",
        "evidence_level": "hipoteza",
        "evidence_note": "[HIPOTEZA] Brak badań z grupą kontrolną na poranny obrzęk twarzy u zdrowych osób.",
        "description": "Delikatny masaż w kierunku węzłów chłonnych. Sen i mniej soli mają lepiej opisany wpływ na obrzęk.",
    },
    {
        "id": "cold_water",
        "title": "Zimna woda na twarz",
        "technique": "cold_water",
        "search_phrase": "zimna woda na twarz rano",
        "evidence_level": "hipoteza",
        "evidence_note": "[HIPOTEZA] Brak badań klinicznych na napięcie skóry.",
        "description": "Prosty nawyk poranny. Nie zastępuje kremu z filtrem.",
    },
    {
        "id": "facial_exercise",
        "title": "Ćwiczenia mięśni twarzy",
        "technique": "muscle_tension",
        "search_phrase": "ćwiczenia mięśni twarzy",
        "evidence_level": "hipoteza",
        "evidence_note": (
            "[HIPOTEZA] Jedna mała próba bez grupy kontrolnej: 16 kobiet 40–65 lat, 20 tygodni, "
            "pełniejsze policzki w ocenie dermatologów (Alam 2018, JAMA Dermatol). U mężczyzn brak danych."
        ),
        "study_url": "https://pubmed.ncbi.nlm.nih.gov/29299598/",
        "description": "Ćwiczenia napinania mięśni twarzy, ok. 30 minut dziennie w badaniu.",
    },
    {
        "id": "hair_styling",
        "title": "Układanie włosów (objętość)",
        "technique": "hair_styling",
        "search_phrase": "męskie włosy układanie objętość",
        "evidence_level": "porada_stylistyczna",
        "evidence_note": "Porada stylistyczna, nie twierdzenie naukowe.",
        "description": "Suszarka, kierunek suszenia i lekki produkt do stylizacji.",
    },
    {
        "id": "scalp_massage",
        "title": "Masaż skóry głowy",
        "technique": "hair_care",
        "search_phrase": "masaż skóry głowy instrukcja",
        "evidence_level": "hipoteza",
        "evidence_note": (
            "[HIPOTEZA] Mała próba: 9 mężczyzn, 4 minuty dziennie przez 24 tygodnie, grubsze włosy "
            "(Koyama 2016, Eplasty). Bez grupy kontrolnej; wymaga potwierdzenia."
        ),
        "study_url": "https://pubmed.ncbi.nlm.nih.gov/26904154/",
        "description": "Ugniatanie i rozciąganie skóry głowy palcami.",
    },
]

for _v in VIDEO_DB:
    _v["url"] = _search_url(_v["search_phrase"])
    _v["kind"] = "youtube_search"


class VideoLearningEngine:
    @staticmethod
    def get_videos_for_technique(technique: str) -> list:
        """Techniques with the given technique key."""
        return [v for v in VIDEO_DB if v["technique"] == technique]

    @staticmethod
    def get_videos_for_analysis(face_data: dict, skin_data: dict, hair_data: dict) -> list:
        """Techniques matching the parts present in the latest analysis."""
        wanted: list[str] = []
        if face_data:
            wanted += ["gua_sha", "lymphatic_drainage", "muscle_tension"]
        if skin_data:
            wanted += ["cold_water"]
        if hair_data:
            wanted += ["hair_styling", "hair_care"]
        return [v for v in VIDEO_DB if v["technique"] in wanted]

    @staticmethod
    def search_videos(query: str) -> list:
        """Search techniques by title, description or search phrase."""
        q = query.lower().strip()
        if not q:
            return []
        return [
            v for v in VIDEO_DB
            if q in v["title"].lower() or q in v["description"].lower() or q in v["search_phrase"].lower()
        ]
