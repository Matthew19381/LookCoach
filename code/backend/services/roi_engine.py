class ROIEngine:
    @staticmethod
    def calculate_roi(effect_size: float, time_weeks: int, feasibility: float = 1.0) -> float:
        """Calculate ROI score: effect_size / (time_weeks^1.5) * feasibility"""
        if time_weeks <= 0:
            return 0.0
        return (effect_size / (time_weeks ** 1.5)) * feasibility

    @staticmethod
    def rank_recommendations(recommendations: list) -> list:
        """Add roi_score to each recommendation and sort by it descending."""
        for rec in recommendations:
            rec["roi_score"] = ROIEngine.calculate_roi(
                rec.get("effect_size", 0.5),
                rec.get("time_to_effect", 4),
                1.0,
            )
        return sorted(recommendations, key=lambda x: x["roi_score"], reverse=True)
