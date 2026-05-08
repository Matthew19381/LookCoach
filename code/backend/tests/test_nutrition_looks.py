import unittest.mock as mock
from services.nutrition_looks import NutritionLooksEngine


class TestNutritionLooksEngine:
    """Comprehensive tests for NutritionLooksEngine."""

    def test_factors_available(self):
        """Test that FACTORS class variable exists."""
        factors = NutritionLooksEngine.FACTORS
        assert len(factors) > 0
        for key, factor in factors.items():
            assert "name" in factor
            assert "looks_impact" in factor
            assert "recommendation" in factor

    def test_get_recommendations(self):
        result = NutritionLooksEngine.get_recommendations()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_recommendations_structure(self):
        recs = NutritionLooksEngine.get_recommendations()
        for rec in recs:
            assert "factor" in rec
            assert "name" in rec
            assert "recommendation" in rec

    def test_analyze_diet_basic(self):
        diet_log = {
            "calories": 2000,
            "protein": 150,
            "water_liters": 2.5,
            "sodium_mg": 2000
        }
        result = NutritionLooksEngine.analyze_diet(diet_log)
        assert "score" in result
        assert "issues" in result
        assert "recommendations" in result

    def test_analyze_diet_low_water(self):
        diet_log = {
            "calories": 2000,
            "protein": 150,
            "water_liters": 1.0,
            "sodium_mg": 2000
        }
        result = NutritionLooksEngine.analyze_diet(diet_log)
        assert "score" in result
        assert result["score"] < 80

    def test_analyze_diet_empty(self):
        result = NutritionLooksEngine.analyze_diet({})
        assert "score" in result

    def test_get_meal_plan_pre_event(self):
        result = NutritionLooksEngine.get_meal_plan("pre_event")
        assert isinstance(result, dict)

    def test_get_meal_plan_day_of(self):
        result = NutritionLooksEngine.get_meal_plan("day_of")
        assert isinstance(result, dict)

    def test_get_meal_plan_invalid(self):
        result = NutritionLooksEngine.get_meal_plan("invalid_type")
        assert isinstance(result, dict)

    def test_factor_water(self):
        factors = NutritionLooksEngine.FACTORS
        if "water_intake" in factors:
            assert "3L" in factors["water_intake"]["recommendation"]

    def test_factor_sodium(self):
        factors = NutritionLooksEngine.FACTORS
        if "sodium" in factors:
            assert "<" in factors["sodium"]["recommendation"]

    def test_diet_score_range(self):
        """Verify diet scores are in valid range."""
        diet_log = {"calories": 2500, "protein": 200, "water_liters": 3.5, "sodium_mg": 1000}
        result = NutritionLooksEngine.analyze_diet(diet_log)
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_recommendations_not_empty(self):
        recs = NutritionLooksEngine.get_recommendations()
        assert len(recs) > 0
        for rec in recs:
            assert len(rec["recommendation"]) > 0

    def test_analyze_diet_high_protein(self):
        diet_log = {
            "calories": 2500,
            "protein": 200,
            "water_liters": 3.0,
            "sodium_mg": 1500
        }
        result = NutritionLooksEngine.analyze_diet(diet_log)
        assert "score" in result
        assert result["score"] > 50

    def test_meal_timing_available(self):
        """Test that MEAL_TIMING class variable exists."""
        assert len(NutritionLooksEngine.MEAL_TIMING) > 0
