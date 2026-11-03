class NutritionLooksEngine:
    """Nutrition recommendations for looks optimization."""

    # Nutrition factors affecting looks
    FACTORS = {
        "water_intake": {
            "name": "Nawodnienie",
            "looks_impact": "Nawilżenie skóry, mniej opuchlizny",
            "recommendation": "Pij 2,5–3 l dziennie",
            "timing": "Rozłożone na cały dzień",
        },
        "sodium": {
            "name": "Mniej sodu",
            "looks_impact": "Mniej opuchlizny twarzy",
            "recommendation": "Poniżej 1500 mg dziennie",
            "timing": "Zwłaszcza 24 h przed wydarzeniem",
        },
        "sugar": {
            "name": "Mniej cukru",
            "looks_impact": "Czystsza skóra, mniej stanów zapalnych",
            "recommendation": "<25g added sugar/day",
            "timing": "Stałe ograniczanie",
        },
        "protein": {
            "name": "Białko",
            "looks_impact": "Zdrowe włosy, napięcie mięśni",
            "recommendation": "1.6-2.0g per kg bodyweight",
            "timing": "20-30g per meal",
        },
        "omega3": {
            "name": "Kwasy omega-3",
            "looks_impact": "Świeża skóra, gęstsze włosy",
            "recommendation": "2-3g/day from fish or supplements",
            "timing": "Z najtłustszym posiłkiem",
        },
        "zinc": {
            "name": "Cynk",
            "looks_impact": "Mniej trądziku, szybsze gojenie skóry",
            "recommendation": "15-30mg/day",
            "timing": "Z jedzeniem",
        },
    }


    @staticmethod
    def get_recommendations(user_profile: dict = None) -> list:
        """Get nutrition recommendations based on user profile."""
        recs = []
        for factor_id, info in NutritionLooksEngine.FACTORS.items():
            recs.append({
                "factor": factor_id,
                **info,
            })
        return recs
