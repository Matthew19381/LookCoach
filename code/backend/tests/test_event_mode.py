import unittest.mock as mock
from services.event_mode import EventModeEngine
from datetime import datetime, timedelta


class TestEventModeEngine:
    """Comprehensive tests for EventModeEngine."""

    def test_generate_event_plan_basic(self):
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        analysis = {"face": {}, "body": {}, "skin": {}}
        result = EventModeEngine.generate_event_plan(future_date, "party", analysis)
        assert "event_type" in result
        assert "days_until_event" in result

    def test_generate_event_plan_past_date(self):
        past_date = "2020-01-01"
        result = EventModeEngine.generate_event_plan(past_date, "party", {})
        assert "error" in result
        assert "past" in result["error"].lower()

    def test_generate_event_plan_invalid_date(self):
        result = EventModeEngine.generate_event_plan("invalid-date", "party", {})
        # Should handle gracefully with default
        assert "event_type" in result or "error" in result

    def test_generate_event_plan_wedding(self):
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        result = EventModeEngine.generate_event_plan(future_date, "wedding", {})
        assert result["event_type"] == "wedding"
        assert result["days_until_event"] == 30

    def test_generate_event_plan_photoshoot(self):
        future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        result = EventModeEngine.generate_event_plan(future_date, "photoshoot", {})
        assert result["event_type"] == "photoshoot"

    def test_generate_event_plan_date(self):
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = EventModeEngine.generate_event_plan(future_date, "date", {})
        assert result["event_type"] == "date"

    def test_generate_event_plan_general(self):
        future_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        result = EventModeEngine.generate_event_plan(future_date, "general", {})
        assert result["event_type"] == "general"

    def test_days_until_event_positive(self):
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        result = EventModeEngine.generate_event_plan(future_date, "party", {})
        assert result["days_until_event"] >= 0

    def test_with_analysis_data(self):
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        analysis = {
            "face": {"swelling": {"level": 60}},
            "skin": {"problems": [{"issue": "acne"}]}
        }
        result = EventModeEngine.generate_event_plan(future_date, "party", analysis)
        assert "event_type" in result

    def test_generate_event_plan_zero_days(self):
        future_date = datetime.now().strftime("%Y-%m-%d")
        result = EventModeEngine.generate_event_plan(future_date, "party", {})
        assert result["days_until_event"] >= 0
