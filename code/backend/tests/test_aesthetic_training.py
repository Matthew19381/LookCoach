import unittest.mock as mock
from services.aesthetic_training import AestheticTrainingEngine


class TestAestheticTrainingEngine:
    """Comprehensive tests for AestheticTrainingEngine."""

    def test_plans_available(self):
        """Test that PLANS class variable exists and has entries."""
        plans = AestheticTrainingEngine.PLANS
        assert isinstance(plans, dict)
        assert len(plans) > 0
        for goal, plan in plans.items():
            assert "name" in plan
            assert "description" in plan

    def test_exercises_available(self):
        """Test that EXERCISES class variable exists."""
        exercises = AestheticTrainingEngine.EXERCISES
        assert len(exercises) > 0
        for key, ex in exercises.items():
            assert "name" in ex
            assert "target" in ex

    def test_generate_plan_v_taper(self):
        result = AestheticTrainingEngine.generate_plan(
            goal="v_taper",
            fitness_level="beginner"
        )
        assert isinstance(result, dict)

    def test_generate_plan_posterior_chain(self):
        result = AestheticTrainingEngine.generate_plan(
            goal="posterior_chain",
            fitness_level="intermediate"
        )
        assert isinstance(result, dict)

    def test_generate_plan_invalid_goal(self):
        result = AestheticTrainingEngine.generate_plan(
            goal="invalid_goal",
            fitness_level="beginner"
        )
        assert isinstance(result, dict)

    def test_get_exercise_info(self):
        result = AestheticTrainingEngine.get_exercise_info("pull_ups")
        assert isinstance(result, dict)
        if "name" in result:
            assert "Pull" in result["name"]

    def test_get_exercise_info_invalid(self):
        result = AestheticTrainingEngine.get_exercise_info("invalid_exercise")
        assert result == {} or result is None

    def test_analyze_physique_v_taper_low(self):
        analysis = {"body": {"v_taper_score": 30, "posture_score": 50}}
        result = AestheticTrainingEngine.analyze_physique(analysis)
        assert isinstance(result, dict)

    def test_analyze_physique_v_taper_high(self):
        analysis = {"body": {"v_taper_score": 80, "posture_score": 75}}
        result = AestheticTrainingEngine.analyze_physique(analysis)
        assert isinstance(result, dict)

    def test_analyze_physique_empty(self):
        result = AestheticTrainingEngine.analyze_physique({})
        assert isinstance(result, dict)

    def test_generate_plan_fitness_levels(self):
        for level in ["beginner", "intermediate", "advanced"]:
            result = AestheticTrainingEngine.generate_plan(
                goal="v_taper",
                fitness_level=level
            )
            assert isinstance(result, dict)

    def test_exercise_database_keys(self):
        """Verify exercise database has expected entries."""
        exercises = AestheticTrainingEngine.EXERCISES
        expected = ["pull_ups", "lat_pulldowns", "lateral_raises"]
        for ex in expected:
            assert ex in exercises, f"Missing: {ex}"

    def test_exercise_equipment_variety(self):
        """Check that exercises have different equipment."""
        exercises = AestheticTrainingEngine.EXERCISES
        equipment = set(ex["equipment"] for ex in exercises.values())
        assert len(equipment) > 1

    def test_plan_goal_keys(self):
        """Verify common goals exist in PLANS."""
        plans = AestheticTrainingEngine.PLANS
        assert "v_taper" in plans
