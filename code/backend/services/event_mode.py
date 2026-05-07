class EventModeEngine:
    """Prepare for a specific event/date by optimizing face, skin, water, sleep, diet."""

    @staticmethod
    def generate_event_plan(event_date: str, event_type: str, current_analysis: dict) -> dict:
        """
        Generate a plan for an upcoming event.
        event_type: 'party', 'photoshoot', 'date', 'wedding', 'general'
        """
        from datetime import datetime, date
        try:
            target = datetime.strptime(event_date, "%Y-%m-%d").date()
            today = date.today()
            days_until = (target - today).days
        except:
            days_until = 7  # default 1 week

        if days_until < 0:
            return {"error": "Event date is in the past"}

        plan = {
            "event_type": event_type,
            "days_until_event": days_until,
            "daily_actions": [],
            "timeline": [],
            "emergency_day_of": [],
        }

        # Generate daily actions based on days until event
        for day in range(max(1, days_until), 0, -1):
            actions = []

            # Every day: hydration, sleep, basic skincare
            actions.append("Drink 3L water")
            actions.append("Sleep 8+ hours")
            actions.append("Apply SPF 30+ (morning)")
            actions.append("Remove makeup before bed")

            # 3+ days: add serums
            if day <= days_until and day >= days_until - 3:
                actions.append("Vitamin C serum (morning)")
                actions.append("Niacinamide (evening)")

            # 2 days before: reduce sodium
            if day == 2:
                actions.append("Reduce sodium intake (no salty foods)")
                actions.append("No alcohol")
                actions.append("Cold water face rinses (2x day)")

            # 1 day before: intensive
            if day == 1:
                actions.append("Gua sha facial massage (10 min)")
                actions.append("Lymphatic drainage")
                actions.append("Sleep with head slightly elevated")
                actions.append("No carbs after 6pm (reduce face puffiness)")

            # Day of event
            if day == 0:
                plan["emergency_day_of"] = [
                    "Cold water splash 30 min before event",
                    "Light moisturizer + primer",
                    "Gua sha quick touch-up",
                    "Stay hydrated - sip water throughout event",
                ]
                continue

            plan["timeline"].append({
                "days_before": day,
                "actions": actions,
            })

        # Reverse timeline so day 1 is first
        plan["timeline"] = list(reversed(plan["timeline"]))

        # Event-type specific tips
        if event_type == "photoshoot":
            plan["tips"] = [
                "Avoid trying new products within 7 days of shoot",
                "Test your makeup look 3 days before",
                "Bring blotting papers for shine control",
            ]
        elif event_type == "date":
            plan["tips"] = [
                "Get a fresh haircut 3-5 days before",
                "Use a light, natural fragrance",
                "Practice good posture - stand tall!",
            ]
        elif event_type == "wedding":
            plan["tips"] = [
                "Start prep 30 days before if possible",
                "Book professional facial 1 week before",
                "Avoid alcohol 3 days before",
                "Sleep extra well the week of",
            ]
        else:
            plan["tips"] = [
                "Stay consistent with your skincare routine",
                "Get good sleep the week before",
                "Stay hydrated",
            ]

        return plan
