import json

class StressEngine:
    """Manage stress impact on looks (cortisol, skin, hair)."""

    STRESS_EFFECTS = {
        "cortisol_spike": {
            "name": "Cortisol Spike",
            "looks_impact": "Acne, skin thinning, hair loss",
            "signs": ["acne flare", "oily skin", "hair shedding"],
        },
        "stress_skin": {
            "name": "Stress Skin",
            "looks_impact": "Dullness, breakouts, slow healing",
            "signs": ["dull complexion", "slow wound healing", "dark circles"],
        },
        "tension_face": {
            "name": "Facial Tension",
            "looks_impact": "Frown lines, jaw tension, tired look",
            "signs": ["frown lines", "clenched jaw", "crow's feet"],
        },
    }

    RELAXATION_TECHNIQUES = {
        "box_breathing": {
            "name": "Box Breathing",
            "duration": "5 min",
            "looks_benefit": "Reduces cortisol, prevents stress acne",
        },
        "progressive_relaxation": {
            "name": "Progressive Muscle Relaxation",
            "duration": "10 min",
            "looks_benefit": "Releases facial tension, softens features",
        },
        "meditation": {
            "name": "Mindfulness Meditation",
            "duration": "15 min",
            "looks_benefit": "Lowers cortisol, improves skin glow",
        },
        "face_massage": {
            "name": "Stress Face Massage",
            "duration": "5 min",
            "looks_benefit": "Releases jaw tension, reduces puffiness",
        },
    }

    @staticmethod
    def analyze_stress(stress_data: dict) -> dict:
        """Analyze stress and recommend relaxation for looks."""
        result = {
            "score": 0,
            "effects": [],
            "recommendations": [],
        }

        if not stress_data:
            return result

        level = stress_data.get("level", "low")  # low, medium, high
        sources = stress_data.get("sources", [])
        physical_signs = stress_data.get("physical_signs", [])

        # Score calculation (lower stress = higher score)
        score = 100
        if level == "medium":
            score -= 30
        elif level == "high":
            score -= 50

        # Check physical signs
        if "acne" in physical_signs or "oily skin" in physical_signs:
            score -= 15
            result["effects"].append(StressEngine.STRESS_EFFECTS["cortisol_spike"])
        if "dull skin" in physical_signs or "dark circles" in physical_signs:
            score -= 15
            result["effects"].append(StressEngine.STRESS_EFFECTS["stress_skin"])
        if "frown lines" in physical_signs or "jaw tension" in physical_signs:
            score -= 10
            result["effects"].append(StressEngine.STRESS_EFFECTS["tension_face"])

        result["score"] = max(score, 0)

        # Recommendations
        if level in ["medium", "high"]:
            result["recommendations"].append("Practice box breathing 3x/day")
            result["recommendations"].append("10 min progressive muscle relaxation before bed")
        if "jaw tension" in physical_signs:
            result["recommendations"].append("Face massage + warm compress for jaw")
        if "acne" in physical_signs:
            result["recommendations"].append("Lower cortisol: sleep 8h, no sugar, meditation")

        return result

    @staticmethod
    def get_techniques() -> list:
        """Get relaxation techniques for looks."""
        return list(StressEngine.RELAXATION_TECHNIQUES.values())
