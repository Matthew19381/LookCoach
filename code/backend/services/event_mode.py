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
        except ValueError:
            days_until = 7  # default 1 week

        if days_until < 0:
            return {"error": "Data wydarzenia już minęła"}

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
            actions.append("Wypij 3 l wody")
            actions.append("Śpij 8+ godzin")
            actions.append("Rano SPF 30+")
            actions.append("Zmyj makijaż przed snem")

            # 3+ days: add serums
            if day <= days_until and day >= days_until - 3:
                actions.append("Rano serum z witaminą C")
                actions.append("Wieczorem niacynamid")

            # 2 days before: reduce sodium
            if day == 2:
                actions.append("Mniej soli (bez słonych potraw)")
                actions.append("Bez alkoholu")
                actions.append("Płukanie twarzy zimną wodą (2× dziennie)")

            # 1 day before: intensive
            if day == 1:
                actions.append("Masaż twarzy gua sha (10 min)")
                actions.append("Drenaż limfatyczny")
                actions.append("Śpij z lekko uniesioną głową")
                actions.append("Lżejsza kolacja (mniej opuchlizny rano — hipoteza)")

            # Day of event
            if day == 0:
                plan["emergency_day_of"] = [
                    "Zimna woda na twarz 30 min przed wydarzeniem",
                    "Lekki krem nawilżający + baza",
                    "Krótko gua sha",
                    "Pij wodę małymi łykami w trakcie",
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
                "Nie testuj nowych kosmetyków na 7 dni przed sesją",
                "Przetestuj makijaż 3 dni wcześniej",
                "Weź bibułki matujące",
            ]
        elif event_type == "date":
            plan["tips"] = [
                "Get a fresh haircut 3-5 days before",
                "Lekki, naturalny zapach",
                "Pamiętaj o wyprostowanej postawie",
            ]
        elif event_type == "wedding":
            plan["tips"] = [
                "Jeśli możesz, zacznij przygotowania 30 dni wcześniej",
                "Zabieg na twarz u kosmetyczki tydzień przed",
                "Bez alkoholu 3 dni przed",
                "Zadbaj o sen w tygodniu wydarzenia",
            ]
        else:
            plan["tips"] = [
                "Trzymaj się swojej rutyny pielęgnacji",
                "Get good sleep the week before",
                "Pamiętaj o nawodnieniu",
            ]

        return plan
