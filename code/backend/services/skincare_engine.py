from datetime import datetime
from typing import Optional

SKINCARE_INGREDIENTS = [
    {"name": "Gentle Cleanser", "type": "cleanse", "frequency": "daily", "rotatable": False, "irritation_risk": "none"},
    {"name": "SPF 30+", "type": "protect", "frequency": "daily_AM", "rotatable": False, "irritation_risk": "none", "evidence": "RCT", "source": "Hughes 2013, Ann Intern Med (PMID 23732711)"},
    {"name": "Vitamin C 10-20%", "type": "antioxidant", "frequency": "daily_AM", "rotatable": True, "irritation_risk": "low", "evidence": "RCT", "source": "Traikovich 1999, Arch Otolaryngol (PMID 10522500)"},
    {"name": "Niacinamide 5-10%", "type": "balance", "frequency": "daily", "rotatable": True, "irritation_risk": "low", "evidence": "RCT", "source": "Bissett 2005, Dermatol Surg (PMID 16029679)"},
    {"name": "Hyaluronic Acid", "type": "hydrate", "frequency": "daily", "rotatable": False, "irritation_risk": "none"},
    {"name": "Glycerin", "type": "hydrate", "frequency": "daily", "rotatable": False, "irritation_risk": "none"},
    {"name": "Retinol 0.25-1%", "type": "anti_aging", "frequency": "2-3x_week_PM", "rotatable": True, "irritation_risk": "high", "evidence": "RCT", "source": "Kafi 2007, Arch Dermatol (PMID 17515510)", "retinoid_class": True},
    {"name": "Retinaldehyde", "type": "anti_aging", "frequency": "2-3x_week_PM", "rotatable": True, "irritation_risk": "medium", "evidence": "RCT", "retinoid_class": True},
    {"name": "AHA (Glycolic Acid)", "type": "exfoliate", "frequency": "1-2x_week_PM", "rotatable": True, "irritation_risk": "medium", "exfoliant_class": True},
    {"name": "BHA (Salicylic Acid)", "type": "acne", "frequency": "1-3x_week_PM", "rotatable": True, "irritation_risk": "low", "exfoliant_class": True},
    {"name": "Azelaic Acid", "type": "acne", "frequency": "2-3x_week", "rotatable": True, "irritation_risk": "low", "evidence": "RCT"},
    {"name": "Peptide Serum", "type": "anti_aging", "frequency": "daily_PM", "rotatable": True, "irritation_risk": "none"},
    {"name": "Ceramide Moisturizer", "type": "barrier", "frequency": "daily", "rotatable": False, "irritation_risk": "none"},
    {"name": "Squalane Oil", "type": "moisturize", "frequency": "daily_PM", "rotatable": False, "irritation_risk": "none"},
    {"name": "Zinc PCA", "type": "acne", "frequency": "daily_AM", "rotatable": True, "irritation_risk": "low"},
    {"name": "Vitamin E", "type": "antioxidant", "frequency": "daily_PM", "rotatable": True, "irritation_risk": "none"},
    {"name": "Centella Asiatica", "type": "soothe", "frequency": "daily", "rotatable": False, "irritation_risk": "none"},
    {"name": "Niacinamide + Zinc", "type": "balance", "frequency": "daily_AM", "rotatable": True, "irritation_risk": "low"},
    {"name": "Lactic Acid", "type": "exfoliate", "frequency": "1x_week_PM", "rotatable": True, "irritation_risk": "low", "exfoliant_class": True},
    {"name": "Madecassoside", "type": "repair", "frequency": "daily_PM", "rotatable": False, "irritation_risk": "none"},
]

IRRITATION_SIGNALS = [
    "czerwień", "swelling", "pieczenie", "szczypienie", "poczerwienienie",
    "pogorszenie_luszczenia", "nowe_wysipy", "pogorszenie_akne",
    "suchosc_skrajna", "nadwrazliwosc", "reakcja_alergiczna"
]

ROTATION_SCHEDULE = {
    "retinoid": {"cycle_weeks": 12, "min_rest_weeks": 4, "max_concurrent": 1},
    "exfoliant": {"cycle_weeks": 8, "min_rest_weeks": 2, "max_concurrent": 1},
    "vitamin_c": {"cycle_weeks": 16, "min_rest_weeks": 4, "max_concurrent": 1},
    "niacinamide": {"cycle_weeks": 20, "min_rest_weeks": 4, "max_concurrent": 1},
    "peptide": {"cycle_weeks": 24, "min_rest_weeks": 8, "max_concurrent": 1},
}

TOLERANCE_LEVELS = {
    "none": {"retinoid_start_freq": "1x_week", "exfoliant_start_freq": "1x_week", "max_retinoid_freq": "3x_week", "max_exfoliant_freq": "2x_week"},
    "low": {"retinoid_start_freq": "1x_week", "exfoliant_start_freq": "1x_week", "max_retinoid_freq": "3x_week", "max_exfoliant_freq": "2x_week"},
    "medium": {"retinoid_start_freq": "1x_2weeks", "exfoliant_start_freq": "1x_week", "max_retinoid_freq": "2x_week", "max_exfoliant_freq": "1x_week"},
    "high": {"retinoid_start_freq": "avoid", "exfoliant_start_freq": "avoid", "max_retinoid_freq": "avoid", "max_exfoliant_freq": "avoid"},
}


class SkinReactionTracker:
    def __init__(self, db_session=None, user_id: int = 1):
        self.db = db_session
        self.user_id = user_id

    def log_reaction(self, ingredient: str, reaction: str, severity: str, date: Optional[datetime] = None) -> dict:
        """Log a skin reaction to an ingredient."""
        if date is None:
            date = datetime.now()
        reaction_record = {
            "ingredient": ingredient,
            "reaction": reaction,
            "severity": severity,
            "date": date.isoformat(),
            "user_id": self.user_id
        }
        return reaction_record

    def get_reaction_history(self, days: int = 90) -> list:
        """Get reaction history for the last N days."""
        return []

    def get_tolerance_level(self, ingredient: str) -> str:
        """Determine tolerance level for an ingredient based on reaction history."""
        history = self.get_reaction_history(180)
        ingredient_reactions = [r for r in history if r.get("ingredient") == ingredient]

        if not ingredient_reactions:
            return "none"

        severe_count = sum(1 for r in ingredient_reactions if r.get("severity") == "high")
        medium_count = sum(1 for r in ingredient_reactions if r.get("severity") == "medium")

        if severe_count >= 2 or (severe_count >= 1 and medium_count >= 2):
            return "high"
        elif severe_count >= 1 or medium_count >= 3:
            return "medium"
        elif medium_count >= 1:
            return "low"
        return "none"

    def get_overall_sensitivity(self) -> str:
        """Get overall skin sensitivity level."""
        history = self.get_reaction_history(180)
        if not history:
            return "none"

        severe_count = sum(1 for r in history if r.get("severity") == "high")
        medium_count = sum(1 for r in history if r.get("severity") == "medium")
        total_reactions = len(history)

        if severe_count >= 3 or total_reactions >= 10:
            return "high"
        elif severe_count >= 1 or medium_count >= 4 or total_reactions >= 5:
            return "medium"
        elif total_reactions >= 1:
            return "low"
        return "none"


class IngredientRotationManager:
    def __init__(self, db_session=None, user_id: int = 1):
        self.db = db_session
        self.user_id = user_id

    def get_ingredient_history(self, ingredient: str, days: int = 365) -> list:
        """Get usage history for an ingredient."""
        return []

    def should_rotate(self, ingredient: str, category: str) -> tuple[bool, str]:
        """Determine if an ingredient should be rotated out."""
        history = self.get_ingredient_history(ingredient, 365)

        if not history:
            return False, "no_history"

        last_used = history[-1].get("date") if history else None
        if not last_used:
            return False, "no_date"

        last_used_dt = datetime.fromisoformat(last_used)
        weeks_since = (datetime.now() - last_used_dt).days / 7

        schedule = ROTATION_SCHEDULE.get(category, {"cycle_weeks": 12})
        cycle_weeks = schedule.get("cycle_weeks", 12)

        if weeks_since >= cycle_weeks:
            return True, "cycle_complete"

        return False, "within_cycle"

    def get_rotation_recommendations(self, current_routine: dict) -> list:
        """Get recommendations for ingredient rotation."""
        recommendations = []

        all_ingredients = current_routine.get("morning", []) + current_routine.get("evening", [])

        for ingredient_name in all_ingredients:
            ingredient_data = next((i for i in SKINCARE_INGREDIENTS if i["name"] == ingredient_name), None)
            if not ingredient_data or not ingredient_data.get("rotatable"):
                continue

            category = self._get_rotation_category(ingredient_data)
            should_rotate, reason = self.should_rotate(ingredient_name, category)

            if should_rotate:
                alternatives = self._get_alternatives(ingredient_data, current_routine)
                recommendations.append({
                    "ingredient": ingredient_name,
                    "reason": reason,
                    "category": category,
                    "alternatives": alternatives,
                    "priority": "high" if reason == "cycle_complete" else "medium"
                })

        return recommendations

    def _get_rotation_category(self, ingredient: dict) -> str:
        if ingredient.get("retinoid_class"):
            return "retinoid"
        if ingredient.get("exfoliant_class"):
            return "exfoliant"
        if ingredient["type"] == "antioxidant" and "Vitamin C" in ingredient["name"]:
            return "vitamin_c"
        if "Niacinamide" in ingredient["name"]:
            return "niacinamide"
        if ingredient["type"] == "anti_aging" and "Peptide" in ingredient["name"]:
            return "peptide"
        return "other"

    def _get_alternatives(self, ingredient: dict, current_routine: dict) -> list:
        """Get alternative ingredients for rotation."""
        current_names = set(current_routine.get("morning", []) + current_routine.get("evening", []))
        ingredient_type = ingredient["type"]

        alternatives = [
            i["name"] for i in SKINCARE_INGREDIENTS
            if i["type"] == ingredient_type
            and i.get("rotatable", False)
            and i["name"] not in current_names
            and i["name"] != ingredient["name"]
        ]
        return alternatives[:3]


class SkincareEngine:
    def __init__(self, db_session=None, user_id: int = 1):
        self.db = db_session
        self.user_id = user_id
        self.reaction_tracker = SkinReactionTracker(db_session, user_id)
        self.rotation_manager = IngredientRotationManager(db_session, user_id)

    @staticmethod
    def generate_routine(skin_analysis: dict, lifestyle: dict) -> dict:
        """Generate basic morning and evening skincare routines (legacy method)."""
        engine = SkincareEngine()
        return engine.generate_adaptive_routine(skin_analysis, lifestyle)

    def generate_adaptive_routine(
        self,
        skin_analysis: dict,
        lifestyle: dict,
        reaction_history: Optional[list] = None,
        current_routine: Optional[dict] = None
    ) -> dict:
        """Generate adaptive skincare routine with reaction adaptation and rotation."""
        skin_type = skin_analysis.get("skin_type", "combination")
        problems = skin_analysis.get("problems", [])
        sensitivity = self.reaction_tracker.get_overall_sensitivity()

        morning = []
        evening = []
        adaptations = []
        rotation_notes = []

        morning.append("Gentle Cleanser")
        evening.append("Gentle Cleanser")

        # Morning: Antioxidant + SPF (always)
        vit_c_tolerance = self.reaction_tracker.get_tolerance_level("Vitamin C 10-20%")
        if vit_c_tolerance != "high":
            morning.append("Vitamin C 10-20%")
        else:
            adaptations.append("Vitamin C pominięty (wysoka wrażliwość) - rozważ niacynamid jako antyoksydant")
            morning.append("Niacinamide 5-10%")

        niacinamide_tolerance = self.reaction_tracker.get_tolerance_level("Niacinamide 5-10%")
        if niacinamide_tolerance != "high":
            if "Niacinamide 5-10%" not in morning:
                morning.append("Niacinamide 5-10%")
        else:
            adaptations.append("Niacinamide pominięty (wysoka wrażliwość)")

        morning.append("Hyaluronic Acid")
        morning.append("SPF 30+")
        morning.append("Centella Asiatica")

        # Evening: Based on skin type, problems, and tolerance
        evening.append("Hyaluronic Acid")

        has_acne = any(p.get("issue", "") in ["acne", "breakouts", "blackheads"] for p in problems)

        if has_acne:
            bha_tolerance = self.reaction_tracker.get_tolerance_level("BHA (Salicylic Acid)")
            if bha_tolerance != "high":
                evening.append("BHA (Salicylic Acid)")
                evening.append("Zinc PCA")
            else:
                adaptations.append("BHA pominięty (wysoka wrażliwość) - użyj kwasu azelowego")
                evening.append("Azelaic Acid")
                evening.append("Zinc PCA")

            azelaic_tolerance = self.reaction_tracker.get_tolerance_level("Azelaic Acid")
            if azelaic_tolerance != "high" and "Azelaic Acid" not in evening:
                evening.append("Azelaic Acid")
        else:
            # Anti-aging track with retinoid adaptation
            retinoid_choice, retinoid_freq = self._select_retinoid(sensitivity)
            if retinoid_choice:
                evening.append(f"{retinoid_choice} ({retinoid_freq})")
                adaptations.append(f"Retinoid: {retinoid_choice} z częstotliwością {retinoid_freq} (wrażliwość: {sensitivity})")

            peptide_tolerance = self.reaction_tracker.get_tolerance_level("Peptide Serum")
            if peptide_tolerance != "high":
                evening.append("Peptide Serum")

        # Hydration/barrier based on skin type
        if skin_type in ["dry", "combination"]:
            evening.append("Ceramide Moisturizer")
            evening.append("Squalane Oil")
            morning.append("Glycerin")
        elif skin_type == "oily":
            evening.append("Ceramide Moisturizer")

        evening.append("Vitamin E")
        evening.append("Madecassoside")

        # Rotation recommendations
        if current_routine:
            rotation_recs = self.rotation_manager.get_rotation_recommendations(current_routine)
            for rec in rotation_recs:
                rotation_notes.append(
                    f"Rotacja: {rec['ingredient']} ({rec['reason']}) → alternatywy: {', '.join(rec['alternatives']) or 'brak'}"
                )

        # Build rotation note
        rotation_note = self._build_rotation_note(sensitivity, rotation_notes, adaptations)

        return {
            "morning": morning,
            "evening": evening,
            "skin_type": skin_type,
            "sensitivity_level": sensitivity,
            "adaptations": adaptations,
            "rotation_recommendations": rotation_notes,
            "notes": rotation_note,
            "generated_at": datetime.now().isoformat()
        }

    def _select_retinoid(self, sensitivity: str) -> tuple[Optional[str], str]:
        """Select appropriate retinoid and frequency based on sensitivity."""
        tol = TOLERANCE_LEVELS.get(sensitivity, TOLERANCE_LEVELS["none"])

        if tol["retinoid_start_freq"] == "avoid":
            return None, "avoid"

        retinoid_tolerance = self.reaction_tracker.get_tolerance_level("Retinol 0.25-1%")
        retinal_tolerance = self.reaction_tracker.get_tolerance_level("Retinaldehyde")

        if retinoid_tolerance == "high" and retinal_tolerance == "high":
            return None, "avoid"
        elif retinoid_tolerance == "high":
            return "Retinaldehyde", tol["retinoid_start_freq"]
        elif retinal_tolerance == "high":
            return "Retinol 0.25-1%", tol["retinoid_start_freq"]
        else:
            return "Retinol 0.25-1%", tol["retinoid_start_freq"]

    def _build_rotation_note(self, sensitivity: str, rotation_notes: list, adaptations: list) -> str:
        parts = []

        if sensitivity == "high":
            parts.append("WYSOKA WRAPŁIWOŚĆ: Unikaj retinoidów i kwasów eksfoliujących. Skup się na barierze (ceramidy, squalan, niacynamid jeśli tolerowany).")
        elif sensitivity == "medium":
            parts.append("ŚREDNIA WRAPŁIWOŚĆ: Retinoid 1x/2tyg, kwas 1x/tyg. Wprowadzaj powoli, zawsze patch test.")
        else:
            parts.append("Standardowa introdukcja: Retinoid 1x/tyg → zwiększaj co 2 tyg do 3x/tyg. Kwas 1x/tyg → 2x/tyg.")

        parts.append("Rotacja aktywów co 3-4 miesiące. Zawsze patch test nowych produktów.")

        if rotation_notes:
            parts.append("Zalecane rotacje: " + "; ".join(rotation_notes))

        if adaptations:
            parts.append("Adaptacje: " + "; ".join(adaptations))

        return " | ".join(parts)

    def check_ingredient_conflicts(self, routine: dict) -> list:
        """Check for ingredient conflicts in routine."""
        conflicts = []
        all_items = routine.get("morning", []) + routine.get("evening", [])

        has_retinoid = any("Retinol" in item or "Retinaldehyde" in item for item in all_items)
        has_aha = any("AHA" in item or "Glycolic" in item or "Lactic" in item for item in all_items)
        has_bha = any("BHA" in item or "Salicylic" in item for item in all_items)
        has_vit_c = any("Vitamin C" in item for item in all_items)
        has_benzoyl = any("Benzoyl" in item for item in all_items)

        if has_retinoid and (has_aha or has_bha):
            conflicts.append({
                "type": "irritation_risk",
                "ingredients": ["retinoid", "eksfoliant (AHA/BHA)"],
                "severity": "high",
                "message": "Retinoid + kwas eksfoliujący = wysokie ryzyko irritacji. Rozważ alternatywne dni lub jeden produkt."
            })

        if has_vit_c and (has_aha or has_bha):
            conflicts.append({
                "type": "ph_conflict",
                "ingredients": ["Vitamin C", "eksfoliant (AHA/BHA)"],
                "severity": "medium",
                "message": "Vitamin C (niskie pH) + kwas = możliwe pieczenie. Rozważ Vitamin C rano, kwas wieczorem."
            })

        if has_retinoid and has_benzoyl:
            conflicts.append({
                "type": "degradation",
                "ingredients": ["retinoid", "nadtlenek benzoilu"],
                "severity": "high",
                "message": "Nadtlenek benzoilu degraduje retinoid. Używaj w oddzielnych rutynach (rano/wieczór)."
            })

        return conflicts

    def get_evidence_summary(self, routine: dict) -> dict:
        """Get evidence summary for routine ingredients."""
        all_items = routine.get("morning", []) + routine.get("evening", [])
        summary = {"RCT": 0, "meta": 0, "observational": 0, "expert": 0, "ingredients": []}

        for item_name in all_items:
            ingredient = next((i for i in SKINCARE_INGREDIENTS if i["name"] == item_name), None)
            if ingredient and ingredient.get("evidence"):
                level = ingredient["evidence"]
                summary[level] = summary.get(level, 0) + 1
                summary["ingredients"].append({
                    "name": item_name,
                    "evidence_level": level,
                    "source": ingredient.get("source", "")
                })

        return summary