

# Evidence database — audited against NEURO_PLAN §4 (A1-A10), 2026-08-23.
# Policy: entries claiming "RCT"/"meta" MUST carry a verifiable study_url;
# anything without one is downgraded to observational/expert until a real
# source is attached. Enforced by scripts/verify_evidence_db.py.
def _pmid(pmid):
    return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"


EVIDENCE_DB = [
    # --- skincare ---
    {"id": "skincare_001", "name": "Niacinamide 5-10%", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.7, "time_to_effect": 12, "study_url": _pmid(16029679), "study_ref": "Bissett 2005, Dermatol Surg (n=50, split-face)", "contraindications": "none"},
    {"id": "skincare_002", "name": "Retinol 0.25-1%", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.85, "time_to_effect": 12, "study_url": _pmid(17515510), "study_ref": "Kafi 2007, Arch Dermatol (n=36, 0.4% retinol)", "contraindications": "pregnancy"},
    {"id": "skincare_003", "name": "Witamina C 10–20%", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.65, "time_to_effect": 12, "study_url": _pmid(10522500), "study_ref": "Traikovich 1999, Arch Otolaryngol (n=19, split-face)", "contraindications": "none"},
    {"id": "skincare_004", "name": "Kwas hialuronowy", "category": "skincare", "evidence_level": "expert", "effect_size": 0.6, "time_to_effect": 2, "study_url": "", "contraindications": "none"},
    {"id": "skincare_005", "name": "Kwasy AHA/BHA (peeling)", "category": "skincare", "evidence_level": "observational", "effect_size": 0.75, "time_to_effect": 6, "study_url": "", "contraindications": "sensitive_skin"},
    {"id": "skincare_006", "name": "SPF 30+ codziennie", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.9, "time_to_effect": 24, "study_url": _pmid(23732711), "study_ref": "Hughes 2013, Ann Intern Med (n=903, 4.5y)", "contraindications": "none"},
    {"id": "skincare_007", "name": "Delikatne oczyszczanie", "category": "skincare", "evidence_level": "expert", "effect_size": 0.4, "time_to_effect": 2, "study_url": "", "contraindications": "none"},
    # --- training (A5: hypertrophy depends on volume/intensity, not exercise per se — no per-exercise RCTs) ---
    {"id": "training_001", "name": "Trening sylwetki V", "category": "training", "evidence_level": "expert", "effect_size": 0.8, "time_to_effect": 12, "study_url": "", "contraindications": "injuries"},
    {"id": "training_002", "name": "Martwy ciąg", "category": "training", "evidence_level": "expert", "effect_size": 0.7, "time_to_effect": 10, "study_url": "", "contraindications": "back_injury"},
    {"id": "training_003", "name": "Podciąganie", "category": "training", "evidence_level": "expert", "effect_size": 0.75, "time_to_effect": 8, "study_url": "", "contraindications": "shoulder_injury"},
    {"id": "training_004", "name": "Wyciskanie nad głowę", "category": "training", "evidence_level": "expert", "effect_size": 0.65, "time_to_effect": 10, "study_url": "", "contraindications": "shoulder_injury"},
    {"id": "training_005", "name": "Przysiady", "category": "training", "evidence_level": "expert", "effect_size": 0.7, "time_to_effect": 8, "study_url": "", "contraindications": "knee_injury"},
    # --- nutrition ---
    {"id": "nutrition_001", "name": "Więcej białka (1,6 g/kg)", "category": "nutrition", "evidence_level": "meta", "effect_size": 0.7, "time_to_effect": 12, "study_url": _pmid(28698222), "study_ref": "Morton 2018, Br J Sports Med (49 studies, n=1863)", "contraindications": "kidney_disease"},
    {"id": "nutrition_002", "name": "Mniej sodu (<2300 mg)", "category": "nutrition", "evidence_level": "expert", "effect_size": 0.6, "time_to_effect": 2, "study_url": "", "contraindications": "none"},
    {"id": "nutrition_003", "name": "Woda 3 l/dzień", "category": "nutrition", "evidence_level": "observational", "effect_size": 0.5, "time_to_effect": 4, "study_url": _pmid(26345226), "study_ref": "Palma 2015, Clin Cosmet Investig Dermatol (n=49; effect mainly at low baseline intake)", "contraindications": "kidney_disease"},
    {"id": "nutrition_005", "name": "Dieta o niskim ładunku glikemicznym (trądzik)", "category": "nutrition", "evidence_level": "RCT", "effect_size": 0.5, "time_to_effect": 12, "study_url": _pmid(17616769), "study_ref": "Smith 2007, Am J Clin Nutr (RCT, n=43 men 15-25; fewer lesions vs control, partly confounded by weight loss) - verified on PubMed 2026-11-02", "contraindications": "none"},
    {"id": "nutrition_004", "name": "Suplementacja cynku", "category": "nutrition", "evidence_level": "expert", "effect_size": 0.4, "time_to_effect": 8, "study_url": "", "contraindications": "none"},
    # --- sleep ---
    {"id": "sleep_001", "name": "Bez niedoboru snu (8 h)", "category": "sleep", "evidence_level": "RCT", "effect_size": 0.8, "time_to_effect": 1, "study_url": _pmid(21156746), "study_ref": "Axelsson 2010, BMJ (crossover; directional effect on perceived attractiveness, no % magnitude)", "contraindications": "none"},
    {"id": "sleep_002", "name": "Stałe pory snu", "category": "sleep", "evidence_level": "observational", "effect_size": 0.6, "time_to_effect": 7, "study_url": "", "contraindications": "none"},
    # --- stress ---
    {"id": "stress_001", "name": "Medytacja 10 min", "category": "stress", "evidence_level": "meta", "effect_size": 0.38, "time_to_effect": 8, "study_url": _pmid(24395196), "study_ref": "Goyal 2014, JAMA Intern Med (47 trials; anxiety ES 0.38 [0.12-0.64] at 8 weeks)", "contraindications": "none"},
    {"id": "stress_002", "name": "Ekspozycja na zimno", "category": "stress", "evidence_level": "observational", "effect_size": 0.6, "time_to_effect": 7, "study_url": "", "contraindications": "heart_disease"},
    # --- beauty techniques (A8: cosmetology/observational evidence only) ---
    {"id": "beauty_001", "name": "Masaż gua sha", "category": "beauty_technique", "evidence_level": "observational", "effect_size": 0.4, "time_to_effect": 4, "study_url": "", "contraindications": "none"},
    {"id": "beauty_002", "name": "Drenaż limfatyczny", "category": "beauty_technique", "evidence_level": "observational", "effect_size": 0.4, "time_to_effect": 2, "study_url": "", "contraindications": "none"},
    {"id": "beauty_003", "name": "Zimna woda na twarz", "category": "beauty_technique", "evidence_level": "expert", "effect_size": 0.55, "time_to_effect": 1, "study_url": "", "contraindications": "none"},
    # --- hair ---
    {"id": "hair_001", "name": "Minoxidil 5%", "category": "hair", "evidence_level": "RCT", "effect_size": 0.8, "time_to_effect": 48, "study_url": _pmid(12196747), "study_ref": "Olsen 2002, J Am Acad Dermatol (n=393, 48 weeks)", "contraindications": "heart_disease"},
    {"id": "hair_002", "name": "Olejek rozmarynowy", "category": "hair", "evidence_level": "RCT", "effect_size": 0.45, "time_to_effect": 24, "study_url": _pmid(25842469), "study_ref": "Panahi 2015, SKINmed — SMALL single-blind comparative trial (n=100) vs minoxidil 2%; comparable efficacy at 6 months; NEEDS REPLICATION (A7)", "contraindications": "none"},
    {"id": "hair_003", "name": "Masaż skóry głowy", "category": "hair", "evidence_level": "observational", "effect_size": 0.4, "time_to_effect": 8, "study_url": "", "contraindications": "none"},
    # --- posture (no appearance-outcome RCTs; standard physiotherapy exercises) ---
    {"id": "posture_001", "name": "Cofanie brody (chin tuck)", "category": "posture", "evidence_level": "expert", "effect_size": 0.6, "time_to_effect": 6, "study_url": "", "contraindications": "none"},
    {"id": "posture_002", "name": "Face pull (przyciąganie liny do twarzy)", "category": "posture", "evidence_level": "expert", "effect_size": 0.65, "time_to_effect": 8, "study_url": "", "contraindications": "shoulder_injury"},
    {"id": "posture_003", "name": "Anioły przy ścianie", "category": "posture", "evidence_level": "observational", "effect_size": 0.5, "time_to_effect": 6, "study_url": "", "contraindications": "none"},
]


class EvidenceEngine:
    PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
    DEFAULT_CATEGORIES = ["sleep", "nutrition", "stress"]
    # Profile goals.focus (plan 4.12) -> EVIDENCE_DB categories
    GOAL_CATEGORIES = {
        "skin": ("skincare",),
        "hair": ("hair",),
        "face": ("beauty_technique",),
        "body": ("training",),
        "posture": ("posture",),
        "style": (),
    }
    # AttractivenessLevers.primary_lever -> EVIDENCE_DB category
    LEVER_CATEGORY = {
        "skin_texture": "skincare",
        "hair_thinning": "hair",
        "body_proportion": "training",
    }

    @staticmethod
    def get_recommendations(user_analysis: dict, user_profile: dict) -> list:
        """Filter and personalize recommendations based on qualitative focus areas."""
        recommendations = []

        # Collect categories from analysis focus_areas, ordered by priority
        priorities = []  # (rank, category) — lower rank = higher priority
        for section in ("face", "body", "skin", "hair"):
            for area in (user_analysis.get(section) or {}).get("focus_areas", []):
                if not isinstance(area, dict):
                    continue
                category = area.get("area")
                rank = EvidenceEngine.PRIORITY_RANK.get(area.get("priority"), 1)
                if category:
                    priorities.append((rank, category))

        # The detected lever (skin/hair problems produce no focus_areas in the
        # prompts): its primary area is high priority, secondary ones medium.
        known = {e["category"] for e in EVIDENCE_DB}
        lever = user_analysis.get("lever") or {}
        primary = lever.get("primary_lever")
        primary = EvidenceEngine.LEVER_CATEGORY.get(primary, primary)
        if primary in known:
            priorities.append((0, primary))
        for category in lever.get("secondary_levers", []):
            if category in known:
                priorities.append((1, category))

        # The user's own goals (plan 4.12) - right after the hub priority
        for area in user_analysis.get("goal_focus", []):
            for category in EvidenceEngine.GOAL_CATEGORIES.get(area, ()):
                priorities.append((-1, category))

        # Hub directive `priority` (e.g. "skincare") outranks everything (plan 3.7)
        hub_priority = user_analysis.get("hub_priority")
        if hub_priority in known:
            priorities.append((-2, hub_priority))

        # Always include basics at default priority
        for cat in EvidenceEngine.DEFAULT_CATEGORIES:
            priorities.append((1, cat))

        priorities.sort(key=lambda x: x[0])

        # Get unique categories in priority order
        # Copies: ROIEngine adds fields to each item, and mutating EVIDENCE_DB
        # itself would leak one request's state into the next.
        seen_categories = set()
        for rank, category in priorities:
            if category not in seen_categories:
                seen_categories.add(category)
                items = [{**e, "priority_rank": rank} for e in EVIDENCE_DB if e["category"] == category]
                recommendations.extend(items)

        return recommendations
