import json

class PostureCorrectionEngine:
    """Detect and correct posture issues affecting looks."""

    POSTURE_ISSUES = {
        "forward_head": {
            "name": "Forward Head Posture",
            "description": "Head protrudes forward, creating neck strain",
            "looks_impact": "Shortens neck appearance, weakens jawline definition",
            "severity_signs": ["chin_forward", "neck_strain", "rounded_shoulders"],
        },
        "rounded_shoulders": {
            "name": "Rounded Shoulders",
            "description": "Shoulders roll forward, collapsing chest",
            "looks_impact": "Reduces V-taper, makes chest look smaller",
            "severity_signs": ["shoulders_forward", "chest_collapsed", "upper_back_tight"],
        },
        "anterior_pelvic_tilt": {
            "name": "Anterior Pelvic Tilt",
            "description": "Pelvis tilts forward, increasing lower back arch",
            "looks_impact": "Weakens glute appearance, shortens legs visually",
            "severity_signs": ["lower_back_arch", "glutes_weak", "hamstrings_tight"],
        },
        "swayback": {
            "name": "Swayback",
            "description": "Upper body leans backward to compensate",
            "looks_impact": "Disrupts clean silhouette, reduces height appearance",
            "severity_signs": ["torso_backward", "hips_forward", "knees_locked"],
        },
    }

    CORRECTIONS = {
        "forward_head": [
            {"exercise": "Chin Tucks", "sets": "3x10", "focus": "Deep neck flexors"},
            {"exercise": "Wall Slides", "sets": "3x12", "focus": "Shoulder alignment"},
            {"exercise": "Face Pulls", "sets": "3x15", "focus": "Rear delts + upper back"},
        ],
        "rounded_shoulders": [
            {"exercise": "Face Pulls", "sets": "4x12", "focus": "Rear delt activation"},
            {"exercise": "Lat Pulldowns", "sets": "3x10", "focus": "Lats + shoulder depression"},
            {"exercise": "Chest Openers", "sets": "3x15", "focus": "Pectoral stretch"},
        ],
        "anterior_pelvic_tilt": [
            {"exercise": "Glute Bridges", "sets": "3x15", "focus": "Glute activation"},
            {"exercise": "Deadlifts", "sets": "3x8", "focus": "Posterior chain"},
            {"exercise": "Hip Flexor Stretch", "sets": "2x30s", "focus": "Hip mobility"},
        ],
        "swayback": [
            {"exercise": "Plank", "sets": "3x30s", "focus": "Core stability"},
            {"exercise": "Deadlifts", "sets": "3x8", "focus": "Posterior chain"},
            {"exercise": "Wall Stand", "sets": "3x60s", "focus": "Spinal alignment"},
        ],
    }

    @staticmethod
    def detect_issues(body_analysis: dict) -> list:
        """Detect posture issues from body analysis."""
        issues = []
        if not body_analysis:
            return issues

        # Check for forward head posture
        if body_analysis.get("head_position") == "forward":
            issues.append({
                "issue": "forward_head",
                **PostureCorrectionEngine.POSTURE_ISSUES["forward_head"]
            })

        # Check for rounded shoulders
        if body_analysis.get("shoulder_position") == "forward":
            issues.append({
                "issue": "rounded_shoulders",
                **PostureCorrectionEngine.POSTURE_ISSUES["rounded_shoulders"]
            })

        # Check for pelvic tilt
        if body_analysis.get("pelvic_tilt") == "anterior":
            issues.append({
                "issue": "anterior_pelvic_tilt",
                **PostureCorrectionEngine.POSTURE_ISSUES["anterior_pelvic_tilt"]
            })

        return issues

    @staticmethod
    def get_correction_plan(issue_id: str) -> dict:
        """Get correction exercises for an issue."""
        if issue_id not in PostureCorrectionEngine.CORRECTIONS:
            return {"error": "Issue not found"}
        return {
            "issue": issue_id,
            "info": PostureCorrectionEngine.POSTURE_ISSUES.get(issue_id, {}),
            "corrections": PostureCorrectionEngine.CORRECTIONS[issue_id],
        }

    @staticmethod
    def full_assessment(body_analysis: dict) -> dict:
        """Full posture assessment với correction plan."""
        issues = PostureCorrectionEngine.detect_issues(body_analysis)
        plan = []
        for issue in issues:
            correction = PostureCorrectionEngine.get_correction_plan(issue["issue"])
            plan.append(correction)

        return {
            "issues_detected": len(issues),
            "issues": issues,
            "correction_plan": plan,
            "daily_habits": [
                "Check posture every 30 min with phone reminder",
                "Sleep with proper pillow height (not too high)",
                "Stretch chest + hip flexors daily",
                "Stay active - avoid sitting >1hr at a time",
            ],
        }
