import unittest.mock as mock
from services.posture_correction import PostureCorrectionEngine


class TestPostureCorrectionEngine:
    """Comprehensive tests for PostureCorrectionEngine."""

    def test_posture_issues_available(self):
        """Test that POSTURE_ISSUES class variable exists."""
        issues = PostureCorrectionEngine.POSTURE_ISSUES
        assert len(issues) > 0
        for key, issue in issues.items():
            assert "name" in issue
            assert "description" in issue

    def test_corrections_available(self):
        """Test that CORRECTIONS class variable exists."""
        corrections = PostureCorrectionEngine.CORRECTIONS
        assert len(corrections) > 0

    def test_detect_issues_forward_head(self):
        body_analysis = {
            "head_position": "forward",
            "shoulder_position": "forward"
        }
        issues = PostureCorrectionEngine.detect_issues(body_analysis)
        assert isinstance(issues, list)

    def test_detect_issues_empty(self):
        issues = PostureCorrectionEngine.detect_issues({})
        assert isinstance(issues, list)

    def test_detect_issues_none(self):
        body_analysis = {
            "head_position": "neutral",
            "shoulder_position": "neutral"
        }
        issues = PostureCorrectionEngine.detect_issues(body_analysis)
        assert isinstance(issues, list)

    def test_get_correction_plan(self):
        result = PostureCorrectionEngine.get_correction_plan("forward_head")
        assert isinstance(result, dict)

    def test_get_correction_plan_invalid(self):
        result = PostureCorrectionEngine.get_correction_plan("invalid_issue")
        assert isinstance(result, dict)

    def test_full_assessment(self):
        analysis = {
            "head_position": "forward",
            "shoulder_position": "forward"
        }
        result = PostureCorrectionEngine.full_assessment(analysis)
        assert isinstance(result, dict)
        assert "issues" in result

    def test_full_assessment_empty(self):
        result = PostureCorrectionEngine.full_assessment({})
        assert isinstance(result, dict)

    def test_correction_exercises_count(self):
        """Test that corrections have exercises."""
        for issue_id in ["forward_head", "rounded_shoulders"]:
            plan = PostureCorrectionEngine.get_correction_plan(issue_id)
            if "exercises" in plan:
                assert len(plan["exercises"]) >= 1

    def test_issue_severity(self):
        """Test that issues can have severity levels."""
        issues = PostureCorrectionEngine.POSTURE_ISSUES
        for issue in issues.values():
            if "severity" in issue:
                assert issue["severity"] in ["low", "medium", "high"]

    def test_forward_head_corrections(self):
        plan = PostureCorrectionEngine.get_correction_plan("forward_head")
        assert isinstance(plan, dict)

    def test_multiple_issues_detection(self):
        body_analysis = {
            "head_position": "forward",
            "shoulder_position": "forward"
        }
        issues = PostureCorrectionEngine.detect_issues(body_analysis)
        assert len(issues) >= 1

    def test_all_issues_from_class_var(self):
        """Get all issues from POSTURE_ISSUES class variable."""
        issues = PostureCorrectionEngine.POSTURE_ISSUES
        assert len(issues) > 0
        for issue_id, issue in issues.items():
            assert "name" in issue
            assert "description" in issue
            assert "looks_impact" in issue

    def test_corrections_structure(self):
        """Verify corrections have proper structure."""
        corrections = PostureCorrectionEngine.CORRECTIONS
        for issue_id, exercises in corrections.items():
            assert isinstance(exercises, list)
            if len(exercises) > 0:
                assert "exercise" in exercises[0]
                assert "sets" in exercises[0]
