import json


EVIDENCE_DB = [
    {"id": "skincare_001", "name": "Niacinamide 5-10%", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.7, "time_to_effect": 4, "study_url": "", "contraindications": "none"},
    {"id": "skincare_002", "name": "Retinol 0.25-1%", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.85, "time_to_effect": 12, "study_url": "", "contraindications": "pregnancy"},
    {"id": "skincare_003", "name": "Vitamin C 10-20%", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.65, "time_to_effect": 8, "study_url": "", "contraindications": "none"},
    {"id": "skincare_004", "name": "Hyaluronic Acid", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.6, "time_to_effect": 2, "study_url": "", "contraindications": "none"},
    {"id": "skincare_005", "name": "AHA/BHA Peels", "category": "skincare", "evidence_level": "meta", "effect_size": 0.75, "time_to_effect": 6, "study_url": "", "contraindications": "sensitive_skin"},
    {"id": "skincare_006", "name": "SPF 30+ Daily", "category": "skincare", "evidence_level": "RCT", "effect_size": 0.9, "time_to_effect": 1, "study_url": "", "contraindications": "none"},
    {"id": "skincare_007", "name": "Gentle Cleansing", "category": "skincare", "evidence_level": "expert", "effect_size": 0.4, "time_to_effect": 2, "study_url": "", "contraindications": "none"},
    {"id": "training_001", "name": "V-Taper Training", "category": "training", "evidence_level": "RCT", "effect_size": 0.8, "time_to_effect": 12, "study_url": "", "contraindications": "injuries"},
    {"id": "training_002", "name": "Deadlifts", "category": "training", "evidence_level": "RCT", "effect_size": 0.7, "time_to_effect": 10, "study_url": "", "contraindications": "back_injury"},
    {"id": "training_003", "name": "Pull-ups", "category": "training", "evidence_level": "RCT", "effect_size": 0.75, "time_to_effect": 8, "study_url": "", "contraindications": "shoulder_injury"},
    {"id": "training_004", "name": "Overhead Press", "category": "training", "evidence_level": "RCT", "effect_size": 0.65, "time_to_effect": 10, "study_url": "", "contraindications": "shoulder_injury"},
    {"id": "training_005", "name": "Squats", "category": "training", "evidence_level": "RCT", "effect_size": 0.7, "time_to_effect": 8, "study_url": "", "contraindications": "knee_injury"},
    {"id": "nutrition_001", "name": "High Protein (1.6g/kg)", "category": "nutrition", "evidence_level": "RCT", "effect_size": 0.7, "time_to_effect": 4, "study_url": "", "contraindications": "kidney_disease"},
    {"id": "nutrition_002", "name": "Low Sodium (<2300mg)", "category": "nutrition", "evidence_level": "RCT", "effect_size": 0.6, "time_to_effect": 2, "study_url": "", "contraindications": "none"},
    {"id": "nutrition_003", "name": "Water 3L/day", "category": "nutrition", "evidence_level": "RCT", "effect_size": 0.5, "time_to_effect": 3, "study_url": "", "contraindications": "kidney_disease"},
    {"id": "nutrition_004", "name": "Zinc Supplement", "category": "nutrition", "evidence_level": "RCT", "effect_size": 0.4, "time_to_effect": 8, "study_url": "", "contraindications": "none"},
    {"id": "sleep_001", "name": "8h Sleep", "category": "sleep", "evidence_level": "RCT", "effect_size": 0.8, "time_to_effect": 1, "study_url": "", "contraindications": "none"},
    {"id": "sleep_002", "name": "Consistent Schedule", "category": "sleep", "evidence_level": "RCT", "effect_size": 0.6, "time_to_effect": 7, "study_url": "", "contraindications": "none"},
    {"id": "stress_001", "name": "Meditation 10min", "category": "stress", "evidence_level": "RCT", "effect_size": 0.5, "time_to_effect": 14, "study_url": "", "contraindications": "none"},
    {"id": "stress_002", "name": "Cold Exposure", "category": "stress", "evidence_level": "meta", "effect_size": 0.6, "time_to_effect": 7, "study_url": "", "contraindications": "heart_disease"},
    {"id": "beauty_001", "name": "Gua Sha Massage", "category": "beauty_technique", "evidence_level": "observational", "effect_size": 0.5, "time_to_effect": 4, "study_url": "", "contraindications": "none"},
    {"id": "beauty_002", "name": "Lymphatic Drainage", "category": "beauty_technique", "evidence_level": "RCT", "effect_size": 0.6, "time_to_effect": 2, "study_url": "", "contraindications": "none"},
    {"id": "beauty_003", "name": "Cold Water Face", "category": "beauty_technique", "evidence_level": "meta", "effect_size": 0.55, "time_to_effect": 1, "study_url": "", "contraindications": "none"},
    {"id": "hair_001", "name": "Minoxidil 5%", "category": "hair", "evidence_level": "RCT", "effect_size": 0.8, "time_to_effect": 24, "study_url": "", "contraindications": "heart_disease"},
    {"id": "hair_002", "name": "Rosemary Oil", "category": "hair", "evidence_level": "RCT", "effect_size": 0.5, "time_to_effect": 12, "study_url": "", "contraindications": "none"},
    {"id": "hair_003", "name": "Scalp Massage", "category": "hair", "evidence_level": "observational", "effect_size": 0.4, "time_to_effect": 8, "study_url": "", "contraindications": "none"},
    {"id": "posture_001", "name": "Chin Tucks", "category": "posture", "evidence_level": "RCT", "effect_size": 0.6, "time_to_effect": 6, "study_url": "", "contraindications": "none"},
    {"id": "posture_002", "name": "Face Pulls", "category": "posture", "evidence_level": "RCT", "effect_size": 0.65, "time_to_effect": 8, "study_url": "", "contraindications": "shoulder_injury"},
    {"id": "posture_003", "name": "Wall Angels", "category": "posture", "evidence_level": "observational", "effect_size": 0.5, "time_to_effect": 6, "study_url": "", "contraindications": "none"},
]


class EvidenceEngine:
    @staticmethod
    def get_recommendations(user_analysis: dict, user_profile: dict) -> list:
        """Filter and personalize recommendations based on user analysis and profile."""
        recommendations = []

        # Determine which categories to prioritize based on analysis
        face = user_analysis.get("face", {})
        body = user_analysis.get("body", {})
        skin = user_analysis.get("skin", {})
        hair = user_analysis.get("hair", {})

        # Prioritize based on scores
        priorities = []
        if face:
            priorities.append(("beauty_technique", face.get("overall_face_score", 50)))
            priorities.append(("posture", face.get("overall_face_score", 50)))
        if skin:
            priorities.append(("skincare", skin.get("overall_skin_score", 50)))
        if body:
            priorities.append(("training", body.get("overall_body_score", 50)))
        if hair:
            priorities.append(("hair", hair.get("overall_hair_score", 50)))

        # Always include basics
        priorities.append(("sleep", 50))
        priorities.append(("nutrition", 50))
        priorities.append(("stress", 50))

        # Sort by priority (lower score = higher priority)
        priorities.sort(key=lambda x: x[1])

        # Get unique categories in priority order
        seen_categories = set()
        for category, score in priorities:
            if category not in seen_categories:
                seen_categories.add(category)
                items = [e for e in EVIDENCE_DB if e["category"] == category]
                recommendations.extend(items)

        return recommendations
