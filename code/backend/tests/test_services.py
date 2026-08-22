import unittest.mock as mock
from services.roi_engine import ROIEngine
from services.evidence_engine import EvidenceEngine
from services.attractiveness_levers import AttractivenessLevers
from services.skincare_engine import SkincareEngine
from services.confidence_presence import ConfidencePresenceEngine
from services.openrouter import OpenRouterService

def test_roi_calculate():
    roi = ROIEngine.calculate_roi(0.8, 4, 1.0)
    assert roi > 0
    assert roi == 0.8 / (4 ** 1.5)

def test_roi_calculate_zero_time():
    roi = ROIEngine.calculate_roi(0.8, 0, 1.0)
    assert roi == 0.0

def test_roi_rank():
    recs = [
        {'name': 'A', 'effect_size': 0.5, 'time_to_effect': 8, 'roi_score': 0},
        {'name': 'B', 'effect_size': 0.9, 'time_to_effect': 2, 'roi_score': 0},
        {'name': 'C', 'effect_size': 0.3, 'time_to_effect': 1, 'roi_score': 0},
    ]
    ranked = ROIEngine.rank_recommendations(recs)
    # ROI: B=0.318, C=0.3, A=0.022
    assert ranked[0]["name"] == "B"  # highest ROI
    assert ranked[0]["roi_score"] > ranked[1]["roi_score"]
    assert ranked[1]["name"] == "C"

def test_evidence_engine_get():
    # Empty dicts are falsy, so only sleep, nutrition, stress are added
    recs = EvidenceEngine.get_recommendations({}, {})
    assert len(recs) > 0
    categories = [r["category"] for r in recs]
    # For empty analysis, only sleep, nutrition, stress are prioritized
    assert "sleep" in categories
    assert "nutrition" in categories
    assert "stress" in categories

def test_evidence_engine_prioritization():
    # High-priority focus area from analysis drives category order
    analysis = {"face": {"focus_areas": [{"area": "beauty_technique", "priority": "high", "reason": "tension"}]},
                "body": {}, "skin": {}, "hair": {}}
    profile = {}
    recs = EvidenceEngine.get_recommendations(analysis, profile)
    categories = [r["category"] for r in recs]
    assert "beauty_technique" in categories
    # High-priority category comes before default basics (sleep/nutrition/stress)
    assert categories.index("beauty_technique") < categories.index("sleep")

def test_attractiveness_levers_face_swelling():
    face_data = {"swelling": {"level": "high"}}
    lever = AttractivenessLevers.detect_lever(face_data, {}, {}, {})
    assert lever["primary_lever"] == "facial_swelling"

def test_attractiveness_levers_skin():
    face_data = {"skin_quality": {"status": "needs_attention"}}
    lever = AttractivenessLevers.detect_lever(face_data, {}, {}, {})
    assert lever["primary_lever"] == "skin_texture"

def test_attractiveness_levers_body():
    body_data = {"missing_muscles": [{"muscle": "delts", "priority": "high"}]}
    lever = AttractivenessLevers.detect_lever({}, body_data, {}, {})
    assert lever["primary_lever"] == "body_proportion"

def test_attractiveness_levers_hair():
    hair_data = {"density_status": "thin", "hairline_status": "moderate_recession"}
    lever = AttractivenessLevers.detect_lever({}, {}, {}, hair_data)
    assert lever["primary_lever"] == "hair_thinning"

def test_attractiveness_levers_general():
    lever = AttractivenessLevers.detect_lever({}, {}, {}, {})
    assert lever["primary_lever"] == "general"


# ========== SKINCARE ENGINE TESTS ==========
def test_skincare_generate_routine_basic():
    skin_analysis = {"skin_type": "combination", "problems": []}
    lifestyle = {}
    routine = SkincareEngine.generate_routine(skin_analysis, lifestyle)
    assert "morning" in routine
    assert "evening" in routine
    assert len(routine["morning"]) > 0
    assert len(routine["evening"]) > 0


def test_skincare_generate_routine_acne():
    skin_analysis = {
        "skin_type": "oily",
        "problems": [{"issue": "acne"}, {"issue": "breakouts"}]
    }
    lifestyle = {}
    routine = SkincareEngine.generate_routine(skin_analysis, lifestyle)
    # Should include acne-fighting ingredients
    evening_str = " ".join(routine["evening"]).lower()
    assert "bha" in evening_str or "salicylic" in evening_str or "azelaic" in evening_str


def test_skincare_generate_routine_aging():
    skin_analysis = {
        "skin_type": "dry",
        "problems": [{"issue": "wrinkles"}, {"issue": "fine_lines"}]
    }
    lifestyle = {}
    routine = SkincareEngine.generate_routine(skin_analysis, lifestyle)
    # Should include anti-aging ingredients
    evening_str = " ".join(routine["evening"]).lower()
    assert "retinol" in evening_str or "retinaldehyde" in evening_str or "peptide" in evening_str


def test_skincare_generate_routine_with_lifestyle():
    skin_analysis = {"skin_type": "normal", "problems": []}
    lifestyle = {"sun_exposure": "high"}
    routine = SkincareEngine.generate_routine(skin_analysis, lifestyle)
    # Should include SPF in morning
    morning_str = " ".join(routine["morning"]).lower()
    assert "spf" in morning_str


# ========== CONFIDENCE PRESENCE TESTS ==========
def test_confidence_analyze_posture_good():
    photo_analysis = {
        "body": {
            "asymmetries": [],
            "posture_notes": [],
        }
    }
    result = ConfidencePresenceEngine.analyze_posture_indicators(photo_analysis)
    assert result["status"] == "good"
    assert isinstance(result["issues"], list)
    assert isinstance(result["recommendations"], list)


def test_confidence_analyze_posture_poor():
    photo_analysis = {
        "body": {
            "asymmetries": [
                {"part": "left_shoulder", "severity": "moderate"},
                {"part": "right_hip", "severity": "significant"},
            ],
        }
    }
    result = ConfidencePresenceEngine.analyze_posture_indicators(photo_analysis)
    assert result["status"] == "needs_work"
    assert len(result["issues"]) > 0
    assert len(result["recommendations"]) > 0


def test_confidence_analyze_posture_empty():
    photo_analysis = {}
    result = ConfidencePresenceEngine.analyze_posture_indicators(photo_analysis)
    assert result["status"] == "unknown"
    assert len(result["issues"]) == 0


def test_confidence_analyze_facial_expressions():
    photo_analysis = {
        "face": {
            "muscle_tension": {"level": "high"},
            "swelling": {"level": "medium"},
        }
    }
    result = ConfidencePresenceEngine.analyze_facial_expressions(photo_analysis)
    assert result["status"] == "needs_work"
    assert "expression" in result
    assert "micro_habits" in result


def test_confidence_get_action_plan():
    result = ConfidencePresenceEngine.get_confidence_action_plan()
    assert isinstance(result, list)
    assert len(result) == 7
    assert "day" in result[0]
    assert "focus" in result[0]
    assert "actions" in result[0]


def test_confidence_calculate_attractiveness_impact():
    result = ConfidencePresenceEngine.calculate_attractiveness_impact(70.0, 70.0)
    assert "confidence_score" in result
    assert "presence_score" in result
    assert "attractiveness_boost_pct" in result
    assert "perception_change" in result
    assert result["confidence_score"] == 70.0
    assert result["presence_score"] == 70.0


# ========== OPENROUTER SERVICE TESTS ==========
def test_openrouter_init():
    service = OpenRouterService(api_key="test-key", model="test-model")
    assert service.api_key == "test-key"
    assert service.model == "test-model"


def test_openrouter_generate_text_no_key(monkeypatch):
    service = OpenRouterService(api_key=None)
    result = service.generate_text("test prompt")
    assert result == ""


def test_openrouter_generate_text_with_mock(monkeypatch):
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "AI response"}}]
    }

    with mock.patch("httpx.post", return_value=mock_response) as mock_post:
        service = OpenRouterService(api_key="test-key")
        result = service.generate_text("test prompt")
        assert result == "AI response"
        mock_post.assert_called_once()


def test_openrouter_generate_json_with_mock(monkeypatch):
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"key": "value"}'}}]
    }

    with mock.patch("httpx.post", return_value=mock_response):
        service = OpenRouterService(api_key="test-key")
        result = service.generate_json("test prompt")
        assert isinstance(result, dict)
        assert result["key"] == "value"


def test_openrouter_generate_json_invalid_json(monkeypatch):
    mock_response = mock.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "not valid json"}}]
    }

    with mock.patch("httpx.post", return_value=mock_response):
        service = OpenRouterService(api_key="test-key")
        result = service.generate_json("test prompt")
        # Should return fallback dict on invalid JSON
        assert isinstance(result, dict)


def test_openrouter_api_error(monkeypatch):
    with mock.patch("httpx.post", side_effect=Exception("API Error")):
        service = OpenRouterService(api_key="test-key")
        result = service.generate_text("test prompt")
        assert result == ""
