
class PostureCorrectionEngine:
    """Detect and correct posture issues affecting looks."""

    POSTURE_ISSUES = {
        "forward_head": {
            "name": "Wysunięta głowa",
            "description": "Głowa wysunięta do przodu, napięta szyja",
            "looks_impact": "Optycznie skraca szyję, zaciera zarys żuchwy",
            "severity_signs": ["chin_forward", "neck_strain", "rounded_shoulders"],
        },
        "rounded_shoulders": {
            "name": "Zaokrąglone barki",
            "description": "Barki uciekają do przodu, klatka się zapada",
            "looks_impact": "Zmniejsza efekt sylwetki V, klatka wygląda na mniejszą",
            "severity_signs": ["shoulders_forward", "chest_collapsed", "upper_back_tight"],
        },
        "anterior_pelvic_tilt": {
            "name": "Przodopochylenie miednicy",
            "description": "Miednica pochylona do przodu, pogłębiona lordoza",
            "looks_impact": "Osłabia zarys pośladków, optycznie skraca nogi",
            "severity_signs": ["lower_back_arch", "glutes_weak", "hamstrings_tight"],
        },
        "swayback": {
            "name": "Plecy wklęsłe (swayback)",
            "description": "Tułów odchyla się do tyłu w kompensacji",
            "looks_impact": "Zaburza linię sylwetki, optycznie obniża wzrost",
            "severity_signs": ["torso_backward", "hips_forward", "knees_locked"],
        },
    }

    CORRECTIONS = {
        "forward_head": [
            {"exercise": "Cofanie brody (chin tuck)", "sets": "3x10", "focus": "Głębokie zginacze szyi"},
            {"exercise": "Wall slides (ślizgi przy ścianie)", "sets": "3x12", "focus": "Ustawienie barków"},
            {"exercise": "Face pull (przyciąganie liny do twarzy)", "sets": "3x15", "focus": "Tylne aktony barków + górna część pleców"},
        ],
        "rounded_shoulders": [
            {"exercise": "Face pull (przyciąganie liny do twarzy)", "sets": "4x12", "focus": "Aktywacja tylnych aktonów barków"},
            {"exercise": "Ściąganie drążka", "sets": "3x10", "focus": "Najszersze grzbietu + obniżenie barków"},
            {"exercise": "Otwieranie klatki", "sets": "3x15", "focus": "Rozciąganie piersiowych"},
        ],
        "anterior_pelvic_tilt": [
            {"exercise": "Mostki biodrowe", "sets": "3x15", "focus": "Aktywacja pośladków"},
            {"exercise": "Martwy ciąg", "sets": "3x8", "focus": "Taśma tylna"},
            {"exercise": "Rozciąganie zginaczy bioder", "sets": "2x30s", "focus": "Mobilność bioder"},
        ],
        "swayback": [
            {"exercise": "Deska (plank)", "sets": "3x30s", "focus": "Stabilizacja tułowia"},
            {"exercise": "Martwy ciąg", "sets": "3x8", "focus": "Taśma tylna"},
            {"exercise": "Stanie przy ścianie", "sets": "3x60s", "focus": "Ustawienie kręgosłupa"},
        ],
    }

    @staticmethod
    def detect_issues(body_analysis: dict) -> list:
        """Detect posture issues from body analysis."""
        issues = []
        if not body_analysis:
            return issues
        # Stored vision analyses keep these under "posture" (BODY_PROMPT);
        # older callers pass them at the top level.
        nested = body_analysis.get("posture")
        if isinstance(nested, dict):
            body_analysis = {**nested, **body_analysis}

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
            return {"error": "Nie znaleziono problemu"}
        return {
            "issue": issue_id,
            "info": PostureCorrectionEngine.POSTURE_ISSUES.get(issue_id, {}),
            "corrections": PostureCorrectionEngine.CORRECTIONS[issue_id],
        }

    @staticmethod
    def full_assessment(body_analysis: dict) -> dict:
        """Full posture assessment with a correction plan."""
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
                "Co 30 min sprawdź postawę (przypomnienie w telefonie)",
                "Śpij na poduszce właściwej wysokości (nie za wysokiej)",
                "Codziennie rozciągaj klatkę i zginacze bioder",
                "Ruszaj się — nie siedź dłużej niż godzinę bez przerwy",
            ],
        }
