import json

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

    # Meal timing for looks
    MEAL_TIMING = {
        "pre_event": {
            "name": "Pre-Event Nutrition",
            "timing": "24-48h before",
            "actions": [
                "Reduce sodium to <1000mg",
                "Drink 3L water",
                "Avoid alcohol 48h before",
                "Sleep 8+ hours 2 nights before",
            ],
        },
        "day_of": {
            "name": "Day-Of Event",
            "timing": "Morning of event",
            "actions": [
                "Drink 500ml water on waking",
                "Light meal - avoid bloat",
                "No dairy 8h before (reduces puffiness)",
                "Green tea - reduces water retention",
            ],
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

    @staticmethod
    def get_meal_plan(plan_type: str = "pre_event") -> dict:
        """Get meal timing plan."""
        return NutritionLooksEngine.MEAL_TIMING.get(plan_type, {})

    @staticmethod
    def analyze_diet(diet_log: dict) -> dict:
        """Analyze diet and recommend improvements for looks."""
        result = {
            "score": 0,
            "issues": [],
            "recommendations": [],
        }

        if not diet_log:
            return result

        # Check water intake
        water = diet_log.get("water_liters", 0)
        if water < 2.0:
            result["issues"].append("Low water intake")
            result["recommendations"].append("Increase to 2.5-3L daily")
        elif water > 4.0:
            result["issues"].append("Excessive water (risk of imbalance)")
            result["recommendations"].append("Reduce to 3L daily")

        # Check sodium
        sodium = diet_log.get("sodium_mg", 0)
        if sodium > 2300:
            result["issues"].append("High sodium (puffiness risk)")
            result["recommendations"].append("Reduce to <1500mg/day")

        # Calculate score
        score = 50
        if water >= 2.5:
            score += 20
        if sodium < 1500:
            score += 15
        if diet_log.get("protein_g", 0) > 100:
            score += 15

        result["score"] = min(score, 100)
        return result
