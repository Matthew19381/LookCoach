from .lifestyle_status import status_from_issues


class StressEngine:
    """Manage stress impact on looks (cortisol, skin, hair)."""

    STRESS_EFFECTS = {
        "cortisol_spike": {
            "name": "Skok kortyzolu",
            "looks_impact": "Trądzik, ścieńczenie skóry, wypadanie włosów",
            "signs": ["acne flare", "oily skin", "hair shedding"],
        },
        "stress_skin": {
            "name": "Skóra a stres",
            "looks_impact": "Szarość, wypryski, wolne gojenie",
            "signs": ["dull complexion", "slow wound healing", "dark circles"],
        },
        "tension_face": {
            "name": "Napięcie twarzy",
            "looks_impact": "Zmarszczki mimiczne, napięta żuchwa, zmęczony wygląd",
            "signs": ["frown lines", "clenched jaw", "crow's feet"],
        },
    }

    RELAXATION_TECHNIQUES = {
        "box_breathing": {
            "name": "Oddech pudełkowy",
            "duration": "5 min",
            "looks_benefit": "Obniża kortyzol, zapobiega trądzikowi ze stresu",
        },
        "progressive_relaxation": {
            "name": "Progresywna relaksacja mięśni",
            "duration": "10 min",
            "looks_benefit": "Rozluźnia twarz, łagodzi rysy",
        },
        "meditation": {
            "name": "Medytacja uważności",
            "duration": "15 min",
            "looks_benefit": "Obniża kortyzol, skóra wygląda świeżej",
        },
        "face_massage": {
            "name": "Masaż twarzy na stres",
            "duration": "5 min",
            "looks_benefit": "Rozluźnia żuchwę, zmniejsza opuchliznę",
        },
    }

    @staticmethod
    def analyze_stress(stress_data: dict) -> dict:
        """Analyze stress and recommend relaxation for looks."""
        result = {
            "status": None,
            "status_label": None,
            "effects": [],
            "recommendations": [],
        }

        if not stress_data:
            return result

        level = stress_data.get("level", "low")  # low, medium, high
        physical_signs = stress_data.get("physical_signs", [])

        # Check physical signs
        if "acne" in physical_signs or "oily skin" in physical_signs:
            result["effects"].append(StressEngine.STRESS_EFFECTS["cortisol_spike"])
        if "dull skin" in physical_signs or "dark circles" in physical_signs:
            result["effects"].append(StressEngine.STRESS_EFFECTS["stress_skin"])
        if "frown lines" in physical_signs or "jaw tension" in physical_signs:
            result["effects"].append(StressEngine.STRESS_EFFECTS["tension_face"])

        # High stress alone is "needs attention"; medium counts as one issue.
        issues = len(result["effects"]) + {"medium": 1, "high": 3}.get(level, 0)
        result.update(status_from_issues(issues))

        # Recommendations
        if level in ["medium", "high"]:
            result["recommendations"].append("Oddech pudełkowy 3 razy dziennie")
            result["recommendations"].append("10 min progressive muscle relaxation before bed")
        if "jaw tension" in physical_signs:
            result["recommendations"].append("Masaż twarzy i ciepły okład na żuchwę")
        if "acne" in physical_signs:
            result["recommendations"].append("Obniż kortyzol: sen 8 h, mniej cukru, medytacja")

        return result

    @staticmethod
    def get_techniques() -> list:
        """Get relaxation techniques for looks."""
        return list(StressEngine.RELAXATION_TECHNIQUES.values())
