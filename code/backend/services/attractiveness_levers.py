class AttractivenessLevers:
    @staticmethod
    def detect_lever(face_data: dict, body_data: dict, skin_data: dict, hair_data: dict) -> dict:
        """Detect primary attractiveness lever based on analysis data."""
        scores = {}

        if face_data:
            swelling = face_data.get("swelling", {})
            if isinstance(swelling, dict):
                swelling_level = swelling.get("level", 0)
                if swelling_level > 50:
                    return {
                        "primary_lever": "facial_swelling",
                        "secondary_levers": ["sleep", "nutrition", "stress"],
                        "reason": "High facial swelling detected",
                    }

            skin_quality = face_data.get("skin_quality", {})
            if isinstance(skin_quality, dict):
                skin_score = skin_quality.get("score", 50)
                if skin_score < 40:
                    return {
                        "primary_lever": "skin_texture",
                        "secondary_levers": ["skincare", "hydration", "nutrition"],
                        "reason": "Low skin quality score",
                    }

        if body_data:
            proportions = body_data.get("proportions", {})
            if isinstance(proportions, dict):
                v_taper = proportions.get("v_taper", 50)
                if v_taper < 40:
                    return {
                        "primary_lever": "body_proportion",
                        "secondary_levers": ["training", "nutrition"],
                        "reason": "V-taper needs improvement",
                    }

        if skin_data:
            skin_type = skin_data.get("skin_type", "")
            problems = skin_data.get("problems", [])
            if len(problems) > 2:
                return {
                    "primary_lever": "skin_texture",
                    "secondary_levers": ["skincare", "nutrition", "hydration"],
                    "reason": "Multiple skin problems detected",
                }

        if hair_data:
            density = hair_data.get("density", 50)
            hairline = hair_data.get("hairline", {})
            recession = hairline.get("recession", 0) if isinstance(hairline, dict) else 0
            if density < 40 or recession > 50:
                return {
                    "primary_lever": "hair_thinning",
                    "secondary_levers": ["hair", "nutrition", "stress"],
                    "reason": "Hair thinning or recession detected",
                }

        return {
            "primary_lever": "general",
            "secondary_levers": ["sleep", "nutrition", "training", "skincare"],
            "reason": "No specific issues detected - focus on overall improvement",
        }
