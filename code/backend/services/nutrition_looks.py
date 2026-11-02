class NutritionLooksEngine:
    """Nutrition recommendations for looks optimization."""

    # Nutrition factors affecting looks
    FACTORS = {
        "water_intake": {
            "name": "Water Intake",
            "looks_impact": "Skin hydration, puffiness reduction",
            "recommendation": "Drink 2.5-3L daily",
            "timing": "Spread throughout day",
        },
        "sodium": {
            "name": "Sodium Reduction",
            "looks_impact": "Reduces facial puffiness",
            "recommendation": "Keep <1500mg/day",
            "timing": "Especially 24h before events",
        },
        "sugar": {
            "name": "Sugar Reduction",
            "looks_impact": "Clearer skin, reduces inflammation",
            "recommendation": "<25g added sugar/day",
            "timing": "Consistent reduction",
        },
        "protein": {
            "name": "Protein Intake",
            "looks_impact": "Hair health, muscle tone",
            "recommendation": "1.6-2.0g per kg bodyweight",
            "timing": "20-30g per meal",
        },
        "omega3": {
            "name": "Omega-3 Fatty Acids",
            "looks_impact": "Skin glow, hair thickness",
            "recommendation": "2-3g/day from fish or supplements",
            "timing": "With fattest meal",
        },
        "zinc": {
            "name": "Zinc",
            "looks_impact": "Acne reduction, skin healing",
            "recommendation": "15-30mg/day",
            "timing": "With food",
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
