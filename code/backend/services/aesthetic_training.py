from typing import Dict

class AestheticTrainingEngine:
    """Exercise education + qualitative physique focus. Plans live in ForgeBody (LC-4)."""

    # Exercise database for aesthetic goals
    EXERCISES = {
        "pull_ups": {
            "name": "Pull-ups",
            "target": "lats, biceps",
            "aesthetic_impact": "V-taper width",
            "difficulty": "intermediate",
            "equipment": "pull-up bar",
        },
        "lat_pulldowns": {
            "name": "Lat Pulldowns",
            "target": "lats",
            "aesthetic_impact": "V-taper width",
            "difficulty": "beginner",
            "equipment": "gym",
        },
        "lateral_raises": {
            "name": "Lateral Raises",
            "target": "side delts",
            "aesthetic_impact": "shoulder width",
            "difficulty": "beginner",
            "equipment": "dumbbells",
        },
        "face_pulls": {
            "name": "Face Pulls",
            "target": "rear delts, upper back",
            "aesthetic_impact": "posture + shoulder balance",
            "difficulty": "beginner",
            "equipment": "cable",
        },
        "incline_press": {
            "name": "Incline Dumbbell Press",
            "target": "upper chest",
            "aesthetic_impact": "chest fullness",
            "difficulty": "intermediate",
            "equipment": "dumbbells",
        },
        "squats": {
            "name": "Squats",
            "target": "quads, glutes",
            "aesthetic_impact": "leg shape + glute development",
            "difficulty": "beginner",
            "equipment": "bodyweight/dumbbells",
        },
        "deadlifts": {
            "name": "Deadlifts",
            "target": "posterior chain",
            "aesthetic_impact": "overall muscle + posture",
            "difficulty": "intermediate",
            "equipment": "barbell/dumbbells",
        },
    }

    # Training plans by goal
    @staticmethod
    def get_exercise_info(exercise_id: str) -> Dict:
        """Get exercise details."""
        return AestheticTrainingEngine.EXERCISES.get(exercise_id, {})

    @staticmethod
    def analyze_physique(analysis: Dict) -> Dict:
        """Training focus from the qualitative body analysis (LC-9: no scores).

        Until 2026-11-02 this read `v_taper_score`/`posture_score`, numbers the
        vision prompt never returns - so it always reported 0 and always told
        everyone to work on the V-taper."""
        result: Dict = {"focus": [], "recommendations": []}
        body = (analysis or {}).get("body") or {}
        for m in body.get("missing_muscles", []):
            if isinstance(m, dict) and m.get("priority") in ("high", "medium") and m.get("muscle"):
                result["focus"].append({"muscle": m["muscle"], "priority": m["priority"]})
        for a in body.get("asymmetries", []):
            if isinstance(a, dict) and a.get("severity") in ("moderate", "significant"):
                result["recommendations"].append(
                    f"Asymetria ({a.get('part', 'ciało')}): ćwiczenia jednostronne, skonsultuj w ForgeBody"
                )
        if result["focus"]:
            names = ", ".join(f["muscle"] for f in result["focus"])
            result["recommendations"].append(f"Priorytet akcesoriów w ForgeBody: {names}")
        return result
