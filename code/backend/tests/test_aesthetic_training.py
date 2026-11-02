from services.aesthetic_training import AestheticTrainingEngine


class TestAestheticTrainingEngine:
    """Comprehensive tests for AestheticTrainingEngine."""

    def test_exercises_available(self):
        """Test that EXERCISES class variable exists."""
        exercises = AestheticTrainingEngine.EXERCISES
        assert len(exercises) > 0
        for key, ex in exercises.items():
            assert "name" in ex
            assert "target" in ex

    def test_get_exercise_info(self):
        result = AestheticTrainingEngine.get_exercise_info("pull_ups")
        assert isinstance(result, dict)
        if "name" in result:
            assert "Pull" in result["name"]

    def test_get_exercise_info_invalid(self):
        result = AestheticTrainingEngine.get_exercise_info("invalid_exercise")
        assert result == {} or result is None

    def test_analyze_physique_uses_missing_muscles_no_scores(self):
        analysis = {"body": {
            "missing_muscles": [{"muscle": "delts", "priority": "high"}, {"muscle": "calves", "priority": "low"}],
            "asymmetries": [{"part": "shoulders", "severity": "moderate"}],
        }}
        result = AestheticTrainingEngine.analyze_physique(analysis)
        assert result["focus"] == [{"muscle": "delts", "priority": "high"}]
        assert any("shoulders" in r for r in result["recommendations"])
        assert not any("score" in k for k in result)

    def test_analyze_physique_empty(self):
        result = AestheticTrainingEngine.analyze_physique({})
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

