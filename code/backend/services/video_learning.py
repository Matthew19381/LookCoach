import json

YOUTUBE_API_KEY = None  # Set in .env

# Video database for beauty techniques
VIDEO_DB = [
    {
        "id": "gua_sha_1",
        "title": "Gua Sha Facial Massage Tutorial",
        "technique": "gua sha",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "duration": "12:34",
        "channel": "Skincare Pro",
        "description": "Learn proper gua sha technique for facial drainage and sculpting",
    },
    {
        "id": "lymphatic_1",
        "title": "Lymphatic Drainage for Face Sculpting",
        "technique": "lymphatic_drainage",
        "url": "https://www.youtube.com/watch?v=example1",
        "duration": "15:20",
        "channel": "Beauty Master",
        "description": "Step-by-step lymphatic drainage massage for reducing facial puffiness",
    },
    {
        "id": "cold_water_1",
        "title": "Cold Water Therapy for Skin Tightening",
        "technique": "cold_water",
        "url": "https://www.youtube.com/watch?v=example2",
        "duration": "8:45",
        "channel": "Natural Beauty",
        "description": "How cold water exposure improves skin tone and reduces inflammation",
    },
    {
        "id": "muscle_tension_1",
        "title": "Release Facial Muscle Tension",
        "technique": "muscle_tension",
        "url": "https://www.youtube.com/watch?v=example3",
        "duration": "10:15",
        "channel": "Face Yoga",
        "description": "Exercises to release jaw, forehead and eye area tension",
    },
    {
        "id": "hair_volume_1",
        "title": "Hair Styling for Maximum Volume",
        "technique": "hair_styling",
        "url": "https://www.youtube.com/watch?v=example4",
        "duration": "14:30",
        "channel": "Hair Art",
        "description": "Techniques for adding volume and style to thin hair",
    },
    {
        "id": "hair_care_1",
        "title": "Scalp Massage for Hair Growth",
        "technique": "hair_care",
        "url": "https://www.youtube.com/watch?v=example5",
        "duration": "11:20",
        "channel": "Healthy Hair",
        "description": "Daily scalp massage routine to stimulate hair growth",
    },
]


class VideoLearningEngine:
    @staticmethod
    def get_videos_for_technique(technique: str) -> list:
        """Get videos for a specific beauty technique."""
        return [v for v in VIDEO_DB if v["technique"] == technique]

    @staticmethod
    def get_videos_for_analysis(face_data: dict, skin_data: dict, hair_data: dict) -> list:
        """Get recommended videos based on analysis results."""
        recommended = []

        # Face: gua sha, lymphatic drainage, muscle tension
        if face_data:
            recommended.extend([v for v in VIDEO_DB if v["technique"] in ["gua_sha", "lymphatic_drainage", "muscle_tension"]])

        # Skin: cold water therapy
        if skin_data:
            recommended.extend([v for v in VIDEO_DB if v["technique"] == "cold_water"])

        # Hair: styling and care
        if hair_data:
            recommended.extend([v for v in VIDEO_DB if v["technique"] in ["hair_styling", "hair_care"]])

        # Remove duplicates
        seen = set()
        unique = []
        for v in recommended:
            if v["id"] not in seen:
                seen.add(v["id"])
                unique.append(v)
        return unique

    @staticmethod
    def search_videos(query: str) -> list:
        """Search videos by query string."""
        query_lower = query.lower()
        return [
            v for v in VIDEO_DB
            if query_lower in v["title"].lower() or query_lower in v["description"].lower()
        ]
