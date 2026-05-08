import unittest.mock as mock
from services.experiment_engine import PersonalExperimentEngine
from datetime import datetime, timedelta


class TestPersonalExperimentEngine:
    """Comprehensive tests for PersonalExperimentEngine."""

    def test_get_templates(self):
        result = PersonalExperimentEngine.get_templates()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_templates_structure(self):
        templates = PersonalExperimentEngine.get_templates()
        for template in templates:
            assert "category" in template
            assert "description" in template
            assert "duration_days" in template

    def test_get_template(self):
        result = PersonalExperimentEngine.get_template("skincare_vitamin_c")
        assert isinstance(result, dict)
        if "name" in result:
            assert "Vitamin C" in result["name"]

    def test_get_template_invalid(self):
        result = PersonalExperimentEngine.get_template("invalid_template_123")
        assert result == {} or result is None

    def test_start_experiment(self):
        result = PersonalExperimentEngine.start_experiment(
            template_id="skincare_vitamin_c",
            user_id=1
        )
        assert isinstance(result, dict)

    def test_start_experiment_invalid_template(self):
        result = PersonalExperimentEngine.start_experiment(
            template_id="invalid_template",
            user_id=1
        )
        assert "error" in result or "success" in result

    def test_analyze_results(self):
        experiment = {"id": "test_123", "template_id": "skincare_vitamin_c"}
        result = PersonalExperimentEngine.analyze_results(experiment)
        assert isinstance(result, dict)

    def test_get_recommendation(self):
        experiment_result = {"status": "completed", "best_variant": "A"}
        result = PersonalExperimentEngine.get_recommendation(experiment_result)
        assert isinstance(result, str)

    def test_template_count(self):
        templates = PersonalExperimentEngine.get_templates()
        assert len(templates) >= 3

    def test_template_categories(self):
        templates = PersonalExperimentEngine.get_templates()
        categories = set(t["category"] for t in templates)
        assert "skincare" in categories

    def test_experiment_duration(self):
        templates = PersonalExperimentEngine.get_templates()
        for template in templates:
            assert template["duration_days"] > 0

    def test_variant_count(self):
        templates = PersonalExperimentEngine.get_templates()
        for template in templates:
            assert len(template.get("variants", [])) >= 2

    def test_log_daily(self):
        experiment = {"id": "test_123", "template_id": "skincare_vitamin_c"}
        result = PersonalExperimentEngine.log_daily(
            experiment=experiment,
            day=1,
            rating=7,
            notes="Feeling good"
        )
        assert isinstance(result, dict)

    def test_template_has_metric(self):
        templates = PersonalExperimentEngine.get_templates()
        for template in templates:
            assert "metric" in template
            assert "measurement" in template
