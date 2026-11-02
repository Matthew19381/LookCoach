from services.sleep_engine import SleepEngine


class TestSleepEngine:
    """Comprehensive tests for SleepEngine."""

    def test_factors_available(self):
        """Test that SLEEP_FACTORS class variable exists."""
        factors = SleepEngine.SLEEP_FACTORS
        assert len(factors) > 0
        for key, factor in factors.items():
            assert "name" in factor
            assert "looks_impact" in factor
            assert "optimal" in factor

    def test_analyze_sleep_good(self):
        sleep_data = {"hours": 8, "quality": "deep", "bedtime": "22:30", "back_sleeping": True}
        result = SleepEngine.analyze_sleep(sleep_data)
        assert "status" in result and "score" not in result
        assert result["status"] == "good"
        assert result["status_label"] == "dobry"

    def test_analyze_sleep_poor(self):
        sleep_data = {"hours": 4, "quality": "light", "timing": "2AM"}
        result = SleepEngine.analyze_sleep(sleep_data)
        assert "status" in result and "score" not in result
        assert result["status"] == "needs_attention"
        assert len(result["issues"]) >= 3

    def test_analyze_sleep_empty(self):
        result = SleepEngine.analyze_sleep({})
        assert "status" in result and "score" not in result

    def test_get_pre_event_tips_party(self):
        result = SleepEngine.get_pre_event_tips("party")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_pre_event_tips_wedding(self):
        result = SleepEngine.get_pre_event_tips("wedding")
        assert isinstance(result, list)

    def test_get_pre_event_tips_invalid(self):
        result = SleepEngine.get_pre_event_tips("invalid")
        assert isinstance(result, list)

    def test_factor_duration(self):
        factors = SleepEngine.SLEEP_FACTORS
        if "duration" in factors:
            assert "7-9" in factors["duration"]["optimal"]

    def test_factor_timing(self):
        factors = SleepEngine.SLEEP_FACTORS
        if "timing" in factors:
            assert "10PM" in factors["timing"]["optimal"] or "11PM" in factors["timing"]["optimal"]

    def test_sleep_score_range(self):
        """Verify sleep status is one of the qualitative categories (no X/100)."""
        for hours in [4, 6, 8, 10]:
            sleep_data = {"hours": hours, "quality": "deep", "timing": "10PM"}
            result = SleepEngine.analyze_sleep(sleep_data)
            assert "status" in result and "score" not in result
            assert result["status"] in {None, "good", "needs_improvement", "needs_attention"}

    def test_sleep_issues_detection(self):
        sleep_data = {"hours": 4, "quality": "light", "timing": "3AM"}
        result = SleepEngine.analyze_sleep(sleep_data)
        assert "issues" in result
        assert len(result["issues"]) > 0

    def test_prepare_event_tips_available(self):
        """Test that PRE_EVENT_TIPS class variable exists."""
        assert len(SleepEngine.PRE_EVENT_TIPS) > 0
        for key, tips in SleepEngine.PRE_EVENT_TIPS.items():
            assert isinstance(tips, list)

    def test_analyze_sleep_consistency(self):
        sleep_data = {"hours": 8, "quality": "deep", "timing": "10PM", "consistent": True}
        result = SleepEngine.analyze_sleep(sleep_data)
        assert "status" in result and "score" not in result

    def test_pillow_height_factor(self):
        factors = SleepEngine.SLEEP_FACTORS
        if "pillow_height" in factors:
            factor = factors["pillow_height"]
            assert "10-12cm" in factor["optimal"] or "medium" in factor["optimal"].lower()


def test_bedtime_is_compared_as_time_not_text():
    """22:30 is before midnight, 01:00 after (string compare got both wrong)."""
    early = SleepEngine.analyze_sleep({"hours": 8, "quality": "deep", "bedtime": "22:30", "back_sleeping": True})
    late = SleepEngine.analyze_sleep({"hours": 8, "quality": "deep", "bedtime": "01:00", "back_sleeping": True})
    assert "Late bedtime (after midnight)" not in early["issues"]
    assert "Late bedtime (after midnight)" in late["issues"]
