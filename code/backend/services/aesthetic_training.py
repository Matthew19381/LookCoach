from typing import Dict

class AestheticTrainingEngine:
    """Generate minimal effective aesthetic training plans prioritizing V-taper."""

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
    PLANS = {
        "v_taper": {
            "name": "V-Taper Program",
            "description": "Prioritize lats, shoulders, chest - minimize legs",
            "frequency": "4x/week",
            "duration_weeks": 8,
            "priorities": ["lats", "shoulders", "upper_chest"],
            "avoid": ["high_volume_legs", "bulky_exercises"],
            "weekly_schedule": {
                "monday": ["lat_pulldowns", "lateral_raises", "incline_press"],
                "tuesday": ["face_pulls", "squats"],
                "thursday": ["pull_ups", "lateral_raises", "incline_press"],
                "friday": ["deadlifts", "face_pulls"],
            },
        },
        "posture_fix": {
            "name": "Posture Correction Program",
            "description": "Strengthen posterior chain, open chest",
            "frequency": "5x/week",
            "duration_weeks": 6,
            "priorities": ["rear_delts", "upper_back", "core"],
            "avoid": ["chest_dominant", "slouching_habits"],
            "weekly_schedule": {
                "monday": ["face_pulls", "deadlifts", "core"],
                "tuesday": ["squats", "lateral_raises"],
                "wednesday": ["pull_ups", "face_pulls"],
                "thursday": ["deadlifts", "core"],
                "friday": ["face_pulls", "squats"],
            },
        },
        "balanced": {
            "name": "Balanced Aesthetic",
            "description": "Proportional muscle development",
            "frequency": "4x/week",
            "duration_weeks": 10,
            "priorities": ["lats", "chest", "shoulders", "legs"],
            "avoid": [],
            "weekly_schedule": {
                "monday": ["pull_ups", "incline_press"],
                "tuesday": ["squats", "lateral_raises"],
                "thursday": ["lat_pulldowns", "incline_press"],
                "friday": ["deadlifts", "face_pulls"],
            },
        },
    }

    @staticmethod
    def generate_plan(goal: str, fitness_level: str = "beginner") -> Dict:
        """Generate aesthetic training plan based on goal."""
        plan = AestheticTrainingEngine.PLANS.get(goal)
        if not plan:
            plan = AestheticTrainingEngine.PLANS["balanced"]

        # Adjust for fitness level
        if fitness_level == "beginner":
            plan["notes"] = "Start with lighter weights. Focus on form."
            plan["reps"] = "12-15"
        elif fitness_level == "intermediate":
            plan["notes"] = "Progressive overload. Increase weight weekly."
            plan["reps"] = "8-12"
        else:
            plan["notes"] = "Advanced techniques: dropsets, supersets."
            plan["reps"] = "6-10"

        return plan

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
