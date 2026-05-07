SKINCARE_INGREDIENTS = [
    {"name": "Gentle Cleanser", "type": "cleanse", "frequency": "daily", "rotatable": False},
    {"name": "SPF 30+", "type": "protect", "frequency": "daily_AM", "rotatable": False},
    {"name": "Vitamin C 10-20%", "type": "antioxidant", "frequency": "daily_AM", "rotatable": True},
    {"name": "Niacinamide 5-10%", "type": "balance", "frequency": "daily", "rotatable": True},
    {"name": "Hyaluronic Acid", "type": "hydrate", "frequency": "daily", "rotatable": False},
    {"name": "Glycerin", "type": "hydrate", "frequency": "daily", "rotatable": False},
    {"name": "Retinol 0.25-1%", "type": "anti_aging", "frequency": "2-3x_week_PM", "rotatable": True},
    {"name": "Retinaldehyde", "type": "anti_aging", "frequency": "2-3x_week_PM", "rotatable": True},
    {"name": "AHA (Glycolic Acid)", "type": "exfoliate", "frequency": "1-2x_week_PM", "rotatable": True},
    {"name": "BHA (Salicylic Acid)", "type": "acne", "frequency": "1-3x_week_PM", "rotatable": True},
    {"name": "Azelaic Acid", "type": "acne", "frequency": "2-3x_week", "rotatable": True},
    {"name": "Peptide Serum", "type": "anti_aging", "frequency": "daily_PM", "rotatable": True},
    {"name": "Ceramide Moisturizer", "type": "barrier", "frequency": "daily", "rotatable": False},
    {"name": "Squalane Oil", "type": "moisturize", "frequency": "daily_PM", "rotatable": False},
    {"name": "Zinc PCA", "type": "acne", "frequency": "daily_AM", "rotatable": True},
    {"name": "Vitamin E", "type": "antioxidant", "frequency": "daily_PM", "rotatable": True},
    {"name": "Centella Asiatica", "type": "soothe", "frequency": "daily", "rotatable": False},
    {"name": "Niacinamide + Zinc", "type": "balance", "frequency": "daily_AM", "rotatable": True},
    {"name": "Lactic Acid", "type": "exfoliate", "frequency": "1x_week_PM", "rotatable": True},
    {"name": "Madecassoside", "type": "repair", "frequency": "daily_PM", "rotatable": False},
]


class SkincareEngine:
    @staticmethod
    def generate_routine(skin_analysis: dict, lifestyle: dict) -> dict:
        """Generate morning and evening skincare routines based on skin analysis."""
        skin_type = skin_analysis.get("skin_type", "combination")
        problems = skin_analysis.get("problems", [])

        morning = []
        evening = []

        # Always cleanse
        morning.append("Gentle Cleanser")
        evening.append("Gentle Cleanser")

        # Morning: Vitamin C + SPF
        morning.append("Vitamin C 10-20%")
        morning.append("Niacinamide 5-10%")
        morning.append("Hyaluronic Acid")
        morning.append("SPF 30+")

        # Evening: based on skin type and problems
        evening.append("Hyaluronic Acid")

        # Acne
        has_acne = any(p.get("issue", "") in ["acne", "breakouts", "blackheads"] for p in problems)
        if has_acne:
            evening.append("BHA (Salicylic Acid)")
            evening.append("Zinc PCA")
            evening.append("Azelaic Acid")
        else:
            evening.append("Retinol 0.25-1%")
            evening.append("Peptide Serum")

        # Dryness
        if skin_type in ["dry", "combination"]:
            evening.append("Ceramide Moisturizer")
            evening.append("Squalane Oil")
            morning.append("Glycerin")

        # Aging concerns
        evening.append("Vitamin E")

        # Soothing
        morning.append("Centella Asiatica")
        evening.append("Madecassoside")

        # Rotation note
        rotation_note = (
            "Rotate actives every 3-4 months. "
            "Start Retinol/BHA 1x/week, gradually increase. "
            "Always patch test new products."
        )

        return {
            "morning": morning,
            "evening": evening,
            "skin_type": skin_type,
            "notes": rotation_note,
        }
