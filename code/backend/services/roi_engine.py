# Confidence mapping per evidence level — used to derive the ROI range width.
# Internal sorting still uses the point estimate; the UI shows the category.
EVIDENCE_CONFIDENCE = {
    "rct": "high",
    "meta": "high",
    "observational": "moderate",
    "expert": "low",
}

# Relative half-width of the reported range around the point estimate.
RANGE_WIDTH = {
    "high": 0.15,
    "moderate": 0.35,
    "low": 0.50,
}


class ROIEngine:
    @staticmethod
    def calculate_roi(effect_size: float, time_weeks: int, feasibility: float = 1.0) -> float:
        """Calculate ROI score: effect_size / (time_weeks^1.5) * feasibility"""
        if time_weeks <= 0:
            return 0.0
        return (effect_size / (time_weeks ** 1.5)) * feasibility

    @staticmethod
    def rank_recommendations(recommendations: list) -> list:
        """Add ROI point estimate + uncertainty range to each recommendation and
        sort by point estimate descending.

        The point estimate is a heuristic for internal ranking only — it must not
        be shown to users as a precise number. Consumers should render
        roi_score_low/roi_score_high or the qualitative `confidence` field.
        """
        for rec in recommendations:
            point = ROIEngine.calculate_roi(
                rec.get("effect_size", 0.5),
                rec.get("time_to_effect", 4),
                1.0,
            )
            confidence = EVIDENCE_CONFIDENCE.get(
                (rec.get("evidence_level") or "").lower(), "low"
            )
            width = RANGE_WIDTH[confidence]
            rec["roi_score"] = round(point, 3)  # internal sorting key
            rec["roi_score_point_estimate"] = rec["roi_score"]
            rec["roi_score_low"] = max(0.0, round(point * (1 - width), 2))
            rec["roi_score_high"] = round(point * (1 + width), 2)
            rec["confidence"] = confidence
        return sorted(recommendations, key=lambda x: x["roi_score"], reverse=True)
