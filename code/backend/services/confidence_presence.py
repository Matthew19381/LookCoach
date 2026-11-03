

class ConfidencePresenceEngine:
    """Analyze body language, facial expressions, and provide confidence recommendations."""

    @staticmethod
    def analyze_posture_indicators(photo_analysis: dict) -> dict:
        """Analyze posture indicators from qualitative body analysis."""
        result = {
            "status": "unknown",
            "issues": [],
            "recommendations": [],
        }

        body = photo_analysis.get("body") or {}
        if not body:
            return result

        asymmetries = [
            a for a in body.get("asymmetries", [])
            if isinstance(a, dict) and a.get("severity") in ("moderate", "significant")
        ]
        posture_notes = body.get("posture_notes", [])

        for note in posture_notes:
            result["issues"].append(str(note))
        if asymmetries:
            result["issues"].append(f"Wykryto asymetrie ({len(asymmetries)} obszary)")

        has_issues = bool(result["issues"])
        result["status"] = "needs_work" if has_issues else "good"

        if has_issues:
            result["recommendations"].extend([
                "Wall slides 3×10 dziennie",
                "Cofanie brody przy wysuniętej głowie",
                "Face pull na górną część pleców",
            ])
        else:
            result["recommendations"].extend([
                "Utrzymuj nawyki dobrej postawy",
                "Regularna mobilność",
            ])

        return result

    @staticmethod
    def analyze_facial_expressions(face_analysis: dict) -> dict:
        """Analyze facial state for confidence perception."""
        result = {
            "status": "unknown",
            "expression": "neutral",
            "issues": [],
            "recommendations": [],
        }

        face = face_analysis.get("face") or {}
        if not face:
            return result

        muscle_tension = face.get("muscle_tension", {})
        tension_level = muscle_tension.get("level") if isinstance(muscle_tension, dict) else None

        swelling = face.get("swelling", {})
        swelling_level = swelling.get("level") if isinstance(swelling, dict) else None

        if tension_level == "high":
            result["issues"].append("Duże napięcie mięśni twarzy — wyglądasz na zestresowanego")
            result["recommendations"].extend([
                "Progresywna relaksacja mięśni",
                "Masaż twarzy na rozluźnienie",
                "Ćwiczenia rozluźniające żuchwę",
            ])

        if swelling_level in ("medium", "high"):
            result["issues"].append("Opuchnięta twarz wpływa na odbiór")
            result["recommendations"].append("Mniej soli 2 dni przed ważnym wydarzeniem")

        result["status"] = "needs_work" if result["issues"] else "good"

        # Micro-habits
        result["micro_habits"] = [
            "Kontakt wzrokowy przez większość rozmowy",
            "Uśmiech także oczami, nie tylko ustami",
            "Broda równolegle do podłogi",
            "Unikaj zamkniętej postawy",
        ]

        return result

    @staticmethod
    def get_confidence_action_plan() -> list:
        """Get a 7-day confidence building plan."""
        return [
            {
                "day": 1,
                "focus": "Świadomość postawy",
                "actions": [
                    "Przypomnienie o postawie co godzinę",
                    "Przed spotkaniem 2 min otwartej, swobodnej postawy",
                    "5 min chodzenia z książką na głowie",
                ],
            },
            {
                "day": 2,
                "focus": "Kontakt wzrokowy",
                "actions": [
                    "2 min ćwiczenia kontaktu wzrokowego przed lustrem",
                    "Patrz na przemian w oczy i nasadę nosa",
                    "Nagraj, jak mówisz — sprawdź ruch oczu",
                ],
            },
            {
                "day": 3,
                "focus": "Rozluźnienie twarzy",
                "actions": [
                    "Rozluźnienie żuchwy: język przy podniebieniu",
                    "Ćwiczenia rozluźniające czoło",
                    "Gua sha lub masaż twarzy przed snem",
                ],
            },
            {
                "day": 4,
                "focus": "Głos i oddech",
                "actions": [
                    "Ćwiczenia oddechu przeponowego",
                    "Mruczenie dla rezonansu głosu",
                    "Nagraj notatkę głosową i posłuchaj",
                ],
            },
            {
                "day": 5,
                "focus": "Przestrzeń i obecność",
                "actions": [
                    "Siedząc, zajmuj swobodnie miejsce",
                    "Chodź spokojnym, pewnym krokiem",
                    "Gesty — ćwicz otwarte dłonie",
                ],
            },
            {
                "day": 6,
                "focus": "Utrwalenie",
                "actions": [
                    "Przed wyjściem spójrz na całą sylwetkę",
                    "Nagraj, jak wchodzisz do pokoju",
                    "Zapisz, co chcesz poprawić",
                ],
            },
            {
                "day": 7,
                "focus": "Podsumowanie i plan",
                "actions": [
                    "Obejrzyj nagranie z dnia 6",
                    "Porównaj z dniem 1, jeśli nagrałeś",
                    "Wybierz 3 nawyki na kolejne tygodnie",
                ],
            },
        ]
