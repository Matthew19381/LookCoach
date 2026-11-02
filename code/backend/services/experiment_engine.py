import uuid
from datetime import datetime, timedelta


class PersonalExperimentEngine:
    """Run personal experiments to find what works best for you."""

    # Predefined experiment templates
    EXPERIMENT_TEMPLATES = {
        "skincare_vitamin_c": {
            "name": "Serum z witaminą C",
            "category": "skincare",
            "description": "Sprawdź działanie serum z witaminą C przez 14 dni",
            "duration_days": 14,
            "variants": [
                {"name": "10% Vitamin C", "routine": {"morning": ["Vitamin C 10%"]}},
                {"name": "20% Vitamin C", "routine": {"morning": ["Vitamin C 20%"]}},
                {"name": "Bez witaminy C (kontrola)", "routine": {"morning": []}},
            ],
            "metric": "skin_brightness",
            "measurement": "self_rated (1-10 scale)",
        },
        "skincare_retinol": {
            "name": "Stężenie retinolu",
            "category": "skincare",
            "description": "Porównaj różne stężenia retinolu",
            "duration_days": 28,
            "variants": [
                {"name": "0.25% Retinol", "routine": {"evening": ["Retinol 0.25%"]}},
                {"name": "0.5% Retinol", "routine": {"evening": ["Retinol 0.5%"]}},
                {"name": "1% Retinol", "routine": {"evening": ["Retinol 1%"]}},
            ],
            "metric": "skin_texture",
            "measurement": "self_rated + photo comparison",
        },
        "diet_water": {
            "name": "Ilość wody",
            "category": "diet",
            "description": "Sprawdź, czy więcej wody zmienia skórę",
            "duration_days": 14,
            "variants": [
                {"name": "2L water/day", "instruction": "2 l wody dziennie"},
                {"name": "3L water/day", "instruction": "3 l wody dziennie"},
                {"name": "4L water/day", "instruction": "4 l wody dziennie"},
            ],
            "metric": "skin_hydration",
            "measurement": "self_rated + skin plumpness",
        },
        "technique_gua_sha": {
            "name": "Jak często gua sha",
            "category": "technique",
            "description": "Sprawdź różną częstotliwość masażu gua sha",
            "duration_days": 21,
            "variants": [
                {"name": "Codziennie (7×/tydz.)", "frequency": "daily"},
                {"name": "3x/week", "frequency": "3x_week"},
                {"name": "1x/week (control)", "frequency": "1x_week"},
            ],
            "metric": "facial_puffiness",
            "measurement": "morning face check + photos",
        },
        "diet_sodium": {
            "name": "Mniej soli",
            "category": "diet",
            "description": "Sprawdź, czy mniej soli zmniejsza opuchliznę twarzy",
            "duration_days": 7,
            "variants": [
                {"name": "Zwykła ilość soli", "max_sodium": 2300},
                {"name": "Mało sodu (<1500 mg)", "max_sodium": 1500},
            ],
            "metric": "facial_puffiness",
            "measurement": "morning face check + photo",
        },
    }

    @staticmethod
    def get_templates() -> list:
        return [v for k, v in PersonalExperimentEngine.EXPERIMENT_TEMPLATES.items()]

    @staticmethod
    def get_template(template_id: str) -> dict:
        return PersonalExperimentEngine.EXPERIMENT_TEMPLATES.get(template_id)

    @staticmethod
    def start_experiment(template_id: str, user_id: int, custom_name: str = None) -> dict:
        template = PersonalExperimentEngine.EXPERIMENT_TEMPLATES.get(template_id)
        if not template:
            return {"error": "Nie znaleziono szablonu"}

        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=template["duration_days"])

        return {
            "id": f"exp_{user_id}_{uuid.uuid4().hex[:12]}",
            "user_id": user_id,
            "template_id": template_id,
            "name": custom_name or template["name"],
            "category": template["category"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration_days": template["duration_days"],
            "variants": template["variants"],
            "current_variant": 0,
            "metric": template["metric"],
            "measurement": template["measurement"],
            "daily_logs": [],
            "status": "active",
            "results": None,
        }

    @staticmethod
    def log_daily(experiment: dict, day: int, rating: int, notes: str = "") -> dict:
        """Log daily progress for an experiment."""
        if "daily_logs" not in experiment:
            experiment["daily_logs"] = []

        experiment["daily_logs"].append({
            "day": day,
            "rating": rating,
            "notes": notes,
            "date": datetime.now().date().isoformat(),
        })

        return experiment

    @staticmethod
    def analyze_results(experiment: dict) -> dict:
        """Analyze experiment results and pick the best variant."""
        logs = experiment.get("daily_logs", [])
        if not logs:
            return {"error": "Brak wpisów"}

        # Group ratings by variant (rotate variants each day)
        variant_count = len(experiment.get("variants", []))
        if variant_count == 0:
            return {"error": "Brak wariantów"}

        variant_ratings = {i: [] for i in range(variant_count)}

        for log in logs:
            day = log["day"]
            # Simple rotation: variant = (day - 1) % variant_count
            variant_idx = (day - 1) % variant_count
            if 0 <= variant_idx < variant_count:
                variant_ratings[variant_idx].append(log["rating"])

        # Calculate averages
        variant_averages = {}
        for idx, ratings in variant_ratings.items():
            if ratings:
                variant_averages[idx] = {
                    "variant_name": experiment["variants"][idx]["name"],
                    "average_rating": sum(ratings) / len(ratings),
                    "sample_size": len(ratings),
                }

        # Find winner
        winner = None
        for idx, data in variant_averages.items():
            if winner is None or data["average_rating"] > variant_averages[winner]["average_rating"]:
                winner = idx

        return {
            "experiment_id": experiment.get("id"),
            "variant_results": variant_averages,
            "winner": {
                "index": winner,
                "name": experiment["variants"][winner]["name"] if winner is not None else "N/A",
                "average_rating": variant_averages[winner]["average_rating"] if winner is not None else 0,
            } if winner is not None else {"index": -1, "name": "Za mało danych", "average_rating": 0},
            "conclusion": f"Najlepszy wariant: {experiment['variants'][winner]['name'] if winner is not None else 'brak'} - zostań przy nim!" if winner is not None else "Potrzeba więcej danych",
        }

    @staticmethod
    def get_recommendation(experiment_result: dict) -> str:
        """Get recommendation based on experiment results."""
        winner = experiment_result.get("winner", {})
        if winner.get("index") == -1:
            return "Kontynuuj eksperyment, żeby wynik był pewniejszy."

        return f"Zostań przy '{winner.get('name', 'zwycięskim wariancie')}' - średnia ocena dnia {winner.get('average_rating', 0):.1f}/10."
