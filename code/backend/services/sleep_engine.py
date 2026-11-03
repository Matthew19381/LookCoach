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
            "name": "Długość snu",
            "looks_impact": "Regeneracja skóry, cienie, opuchlizna",
            "optimal": "7-9 hours",
            "poor": "<6 hours",
        },
        "quality": {
            "name": "Jakość snu",
            "looks_impact": "Świeża skóra, jasne oczy, nastrój",
            "optimal": "Głęboki, nieprzerywany",
            "poor": "Przerywany, płytki sen",
        },
        "timing": {
            "name": "Pora snu",
            "looks_impact": "Rytm dobowy, wydzielanie hormonów",
            "optimal": "10PM-6AM",
            "poor": "Po północy",
        },
        "pillow_height": {
            "name": "Wysokość poduszki",
            "looks_impact": "Postawa szyi, zarys żuchwy",
            "optimal": "Średnia wysokość (10–12 cm)",
            "poor": "Za wysoka (broda przy klatce) lub za niska (napięta szyja)",
        },
    }

    PRE_EVENT_TIPS = {
        "party": [
            "Śpij 8+ h przez 2 noce przed",
            "Bez alkoholu 24 h przed",
            "Śpij na plecach na średniej poduszce",
            "Bez ekranów godzinę przed snem",
        ],
        "photoshoot": [
            "Śpij 9 h noc przed",
            "Chłodny pokój (18–20°C)",
            "Jedwabna poszewka — mniej tarcia",
            "Lekko unieś głowę (mniej porannej opuchlizny)",
        ],
        "date": [
            "Śpij 8 h przez 2 noce przed",
            "Nawodnij się przed snem",
            "Dzień wcześniej unikaj słonych potraw",
            "Rano po przebudzeniu masaż twarzy",
        ],
        "wedding": [
            "Śpij 9 h przez 3 noce przed",
            "Stałe pory snu przez tydzień przed",
            "Bez alkoholu 48 h przed",
            "Spanie na plecach z odpowiednią poduszką",
        ],
        "general": [
            "7-9 hours nightly",
            "Stałe pory zasypiania i wstawania",
            "Chłodny, ciemny, cichy pokój",
            "Bez kofeiny po 14:00",
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
            result["issues"].append("Za krótki sen (<7 h)")
        if quality in ["poor", "light"]:
            result["issues"].append("Słaba jakość snu")
        if bedtime is not None and bedtime > 24 * 60:
            result["issues"].append("Późne zasypianie (po północy)")
        if not sleep_data.get("back_sleeping"):
            result["issues"].append("Sen nie na plecach")

        # Recommendations
        if duration < 7:
            result["recommendations"].append("Wydłuż sen do 7–9 godzin")
        if quality in ["poor", "light"]:
            result["recommendations"].append("Popraw jakość snu — ciemny pokój, bez ekranów godzinę przed")
        if bedtime is not None and bedtime > 23 * 60:
            result["recommendations"].append("Przesuń zasypianie wcześniej (22–23)")
        if not sleep_data.get("back_sleeping"):
            result["recommendations"].append("Spróbuj spać na plecach — postawa i mniej opuchlizny")

        result.update(status_from_issues(len(result["issues"])))
        return result

    @staticmethod
    def get_pre_event_tips(event_type: str) -> list:
        """Get sleep tips for specific event type."""
        return SleepEngine.PRE_EVENT_TIPS.get(event_type, SleepEngine.PRE_EVENT_TIPS["general"])
