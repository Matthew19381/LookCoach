import json


class ConfidencePresenceEngine:
    """Analyze body language, facial expressions, and provide confidence recommendations."""

    @staticmethod
    def analyze_posture_indicators(photo_analysis: dict) -> dict:
        """Analyze posture indicators from qualitative body analysis."""
        result = {
            "status": "unknown",
            "issues": [],
            "recommendations": [],
        }

        body = photo_analysis.get("body") or {}
        if not body:
            return result

        asymmetries = [
            a for a in body.get("asymmetries", [])
            if isinstance(a, dict) and a.get("severity") in ("moderate", "significant")
        ]
        posture_notes = body.get("posture_notes", [])

        for note in posture_notes:
            result["issues"].append(str(note))
        if asymmetries:
            result["issues"].append(f"Body asymmetries detected ({len(asymmetries)} areas)")

        has_issues = bool(result["issues"])
        result["status"] = "needs_work" if has_issues else "good"

        if has_issues:
            result["recommendations"].extend([
                "Practice wall slides (3x10 reps daily)",
                "Chin tucks for forward head posture",
                "Face pulls for upper back strength",
            ])
        else:
            result["recommendations"].extend([
                "Maintain good posture habits",
                "Regular mobility work",
            ])

        return result

    @staticmethod
    def analyze_facial_expressions(face_analysis: dict) -> dict:
        """Analyze facial state for confidence perception."""
        result = {
            "status": "unknown",
            "expression": "neutral",
            "issues": [],
            "recommendations": [],
        }

        face = face_analysis.get("face") or {}
        if not face:
            return result

        muscle_tension = face.get("muscle_tension", {})
        tension_level = muscle_tension.get("level") if isinstance(muscle_tension, dict) else None

        swelling = face.get("swelling", {})
        swelling_level = swelling.get("level") if isinstance(swelling, dict) else None

        if tension_level == "high":
            result["issues"].append("High facial muscle tension - appears stressed")
            result["recommendations"].extend([
                "Practice progressive muscle relaxation",
                "Facial massage to release tension",
                "Jaw release exercises",
            ])

        if swelling_level in ("medium", "high"):
            result["issues"].append("Facial puffiness affects presence")
            result["recommendations"].append("Reduce sodium 2 days before important events")

        result["status"] = "needs_work" if result["issues"] else "good"

        # Micro-habits
        result["micro_habits"] = [
            "Maintain eye contact 60-70% of conversation",
            "Smile with eyes (Duchenne smile) not just mouth",
            "Keep chin parallel to ground",
            "Take up space - avoid closed postures",
        ]

        return result

    @staticmethod
    def get_confidence_action_plan() -> list:
        """Get a 7-day confidence building plan."""
        return [
            {
                "day": 1,
                "focus": "Posture Awareness",
                "actions": [
                    "Set hourly posture check reminder",
                    "Practice power pose for 2 min before meetings",
                    "Walk with book on head for 5 min",
                ],
            },
            {
                "day": 2,
                "focus": "Eye Contact",
                "actions": [
                    "Practice eye contact in mirror for 2 min",
                    "Try 'triangle gaze' - look at both eyes and bridge",
                    "Record yourself speaking, check eye movement",
                ],
            },
            {
                "day": 3,
                "focus": "Facial Relaxation",
                "actions": [
                    "Jaw release: tongue on roof of mouth",
                    "Forehead smoothing exercises",
                    "Gua sha or facial massage before bed",
                ],
            },
            {
                "day": 4,
                "focus": "Voice & Breathing",
                "actions": [
                    "Diaphragmatic breathing exercises",
                    "Humming for vocal resonance",
                    "Record voice memo, listen for confidence",
                ],
            },
            {
                "day": 5,
                "focus": "Space & Presence",
                "actions": [
                    "Practice taking up space while sitting",
                    "Walk with deliberate, slow strides",
                    "Hand gestures - practice open palm gestures",
                ],
            },
            {
                "day": 6,
                "focus": "Integration",
                "actions": [
                    "Full body check before leaving house",
                    "Record video of yourself entering a room",
                    "Note areas needing improvement",
                ],
            },
            {
                "day": 7,
                "focus": "Review & Plan",
                "actions": [
                    "Review video from day 6",
                    "Compare with day 1 if recorded",
                    "Set 3 weekly confidence habits to maintain",
                ],
            },
        ]

    @staticmethod
    def calculate_attractiveness_impact(confidence_score: float, presence_score: float) -> dict:
        """Calculate how confidence affects perceived attractiveness."""
        # Confidence boosts perceived attractiveness by up to 20%
        base_impact = 0.20
        confidence_factor = confidence_score / 100
        presence_factor = presence_score / 100

        attractiveness_boost = (confidence_factor * 0.6 + presence_factor * 0.4) * base_impact * 100

        return {
            "confidence_score": confidence_score,
            "presence_score": presence_score,
            "attractiveness_boost_pct": round(attractiveness_boost, 1),
            "perception_change": (
                "Significant boost" if attractiveness_boost > 15
                else "Moderate boost" if attractiveness_boost > 8
                else "Mild boost" if attractiveness_boost > 3
                else "Minimal impact"
            ),
            "tip": "Confidence is the #1 most attractive quality - work on it daily!",
        }
