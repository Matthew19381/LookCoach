from .lifestyle_status import status_from_issues


def _bedtime_minutes(value: str) -> int | None:
    """'HH:MM' -> minutes on an evening axis (01:00 -> 25*60), None if unparsable.

    Bedtimes were compared as strings until 2026-11-02, so "22:30" > "00:00"
    counted as "after midnight" and "01:00" <= "23:00" as an early night."""
    try:
        hours, minutes = (int(x) for x in str(value).split(":")[:2])
    except ValueError:
        return None
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        return None
    total = hours * 60 + minutes
    return total + 24 * 60 if hours < 12 else total


class SleepEngine:
    """Optimize sleep for looks (skin repair, hormone regulation)."""

    SLEEP_FACTORS = {
        "duration": {
            "name": "Sleep Duration",
            "looks_impact": "Skin repair, dark circles, puffiness",
            "optimal": "7-9 hours",
            "poor": "<6 hours",
        },
        "quality": {
            "name": "Sleep Quality",
            "looks_impact": "Skin glow, eye brightness, mood",
            "optimal": "Deep, uninterrupted",
            "poor": "Fragmented, light sleep",
        },
        "timing": {
            "name": "Sleep Timing",
            "looks_impact": "Circadian rhythm, hormone production",
            "optimal": "10PM-6AM",
            "poor": "After midnight",
        },
        "pillow_height": {
            "name": "Pillow Height",
            "looks_impact": "Neck posture, jawline definition",
            "optimal": "Medium height (10-12cm)",
            "poor": "Too high (chin tuck) or too low (neck strain)",
        },
    }

    PRE_EVENT_TIPS = {
        "party": [
            "Sleep 8+ hours 2 nights before",
            "Avoid alcohol 24h before",
            "Sleep on back with medium pillow",
            "No screens 1h before bed",
        ],
        "photoshoot": [
            "Sleep 9 hours night before",
            "Cool room (18-20°C)",
            "Silk pillowcase to reduce friction",
            "Elevate head slightly (reduces morning puffiness)",
        ],
        "date": [
            "Sleep 8 hours 2 nights before",
            "Hydrate well before bed",
            "Avoid salty foods day before",
            "Morning facial massage after wake",
        ],
        "wedding": [
            "Sleep 9 hours for 3 nights before",
            "Consistent sleep schedule 1 week before",
            "No alcohol 48h before",
            "Back sleeping with proper pillow support",
        ],
        "general": [
            "7-9 hours nightly",
            "Consistent sleep/wake times",
            "Cool, dark, quiet room",
            "No caffeine after 2PM",
        ],
    }

    @staticmethod
    def analyze_sleep(sleep_data: dict) -> dict:
        """Analyze sleep and recommend improvements for looks."""
        result = {
            "status": None,
            "status_label": None,
            "issues": [],
            "recommendations": [],
        }

        if not sleep_data:
            return result

        duration = sleep_data.get("hours", 0)
        quality = sleep_data.get("quality", "poor")
        bedtime = _bedtime_minutes(sleep_data.get("bedtime", "00:00"))

        # Issues
        if duration < 7:
            result["issues"].append("Insufficient sleep (<7h)")
        if quality in ["poor", "light"]:
            result["issues"].append("Poor sleep quality")
        if bedtime is not None and bedtime > 24 * 60:
            result["issues"].append("Late bedtime (after midnight)")
        if not sleep_data.get("back_sleeping"):
            result["issues"].append("Not sleeping on back")

        # Recommendations
        if duration < 7:
            result["recommendations"].append("Increase sleep to 7-9 hours")
        if quality in ["poor", "light"]:
            result["recommendations"].append("Improve sleep quality - dark room, no screens 1h before")
        if bedtime is not None and bedtime > 23 * 60:
            result["recommendations"].append("Move bedtime earlier (10-11PM)")
        if not sleep_data.get("back_sleeping"):
            result["recommendations"].append("Try back sleeping for posture + puffiness reduction")

        result.update(status_from_issues(len(result["issues"])))
        return result

    @staticmethod
    def get_pre_event_tips(event_type: str) -> list:
        """Get sleep tips for specific event type."""
        return SleepEngine.PRE_EVENT_TIPS.get(event_type, SleepEngine.PRE_EVENT_TIPS["general"])
