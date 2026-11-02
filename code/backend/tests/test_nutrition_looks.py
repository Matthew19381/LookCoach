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

    def test_factor_water(self):
        factors = NutritionLooksEngine.FACTORS
        if "water_intake" in factors:
            assert "3 l" in factors["water_intake"]["recommendation"]

    def test_factor_sodium(self):
        factors = NutritionLooksEngine.FACTORS
        if "sodium" in factors:
            assert "1500 mg" in factors["sodium"]["recommendation"]

    def test_recommendations_not_empty(self):
        recs = NutritionLooksEngine.get_recommendations()
        assert len(recs) > 0
        for rec in recs:
            assert len(rec["recommendation"]) > 0

    def test_no_meal_plans_in_lookcoach(self):
        """LC-4: meal plans belong to Dieta."""
        assert not hasattr(NutritionLooksEngine, "get_meal_plan")
        assert not hasattr(NutritionLooksEngine, "MEAL_TIMING")
