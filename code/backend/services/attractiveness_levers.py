class AttractivenessLevers:
    """Detect the highest-impact improvement lever from qualitative analysis state.

    Works on categorical observations (low/medium/high, good/fair/needs_attention),
    NOT numeric attractiveness ratings of the person.
    """

    HIGH_SWELLING = ("medium", "high")
    POOR_SKIN_STATUS = ("needs_attention",)

    @staticmethod
    def detect_lever(face_data: dict, body_data: dict, skin_data: dict, hair_data: dict) -> dict:
        """Detect primary lever based on qualitative analysis data."""
        if face_data:
            swelling = face_data.get("swelling", {})
            if isinstance(swelling, dict) and swelling.get("level") in AttractivenessLevers.HIGH_SWELLING:
                return {
                    "primary_lever": "facial_swelling",
                    "secondary_levers": ["sleep", "nutrition", "stress"],
                    "reason": "Facial swelling detected",
                }

            skin_quality = face_data.get("skin_quality", {})
            if isinstance(skin_quality, dict) and skin_quality.get("status") in AttractivenessLevers.POOR_SKIN_STATUS:
                return {
                    "primary_lever": "skin_texture",
                    "secondary_levers": ["skincare", "hydration", "nutrition"],
                    "reason": "Skin needs attention",
                }

        if body_data:
            missing = body_data.get("missing_muscles", [])
            high_priority = [
                m for m in missing
                if isinstance(m, dict) and m.get("priority") == "high"
            ]
            asymmetries = [
                a for a in body_data.get("asymmetries", [])
                if isinstance(a, dict) and a.get("severity") == "significant"
            ]
            if high_priority or asymmetries:
                return {
                    "primary_lever": "body_proportion",
                    "secondary_levers": ["training", "nutrition"],
                    "reason": "Body development areas detected",
                }

        if skin_data:
            problems = skin_data.get("problems", [])
            significant = [
                p for p in problems
                if isinstance(p, dict) and p.get("severity") in ("moderate", "significant")
            ]
            if len(significant) > 1:
                return {
                    "primary_lever": "skin_texture",
                    "secondary_levers": ["skincare", "nutrition", "hydration"],
                    "reason": "Multiple skin problems detected",
                }

        if hair_data:
            hairline_status = hair_data.get("hairline_status", "stable")
            density_status = hair_data.get("density_status", "normal")
            if hairline_status != "stable" or density_status == "thin":
                return {
                    "primary_lever": "hair_thinning",
                    "secondary_levers": ["hair", "nutrition", "stress"],
                    "reason": "Hair thinning or recession detected",
                }

        # Fall back to explicit focus_areas if the AI provided any with high priority
        for section in (face_data, body_data):
            for area in (section or {}).get("focus_areas", []):
                if isinstance(area, dict) and area.get("priority") == "high":
                    return {
                        "primary_lever": area.get("area", "general"),
                        "secondary_levers": ["sleep", "nutrition", "skincare"],
                        "reason": area.get("reason", "High priority focus area from analysis"),
                    }

        return {
            "primary_lever": "general",
            "secondary_levers": ["sleep", "nutrition", "training", "skincare"],
            "reason": "No specific issues detected - focus on overall improvement",
        }
