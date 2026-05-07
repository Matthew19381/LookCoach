from services.roi_engine import ROIEngine
from services.evidence_engine import EvidenceEngine
from services.attractiveness_levers import AttractivenessLevers

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
    # Simulate low face score
    analysis = {"face": {"overall_face_score": 30}, "body": {}, "skin": {}, "hair": {}}
    profile = {}
    recs = EvidenceEngine.get_recommendations(analysis, profile)
    # Beauty techniques should be prioritized
    categories = [r["category"] for r in recs]
    assert "beauty_technique" in categories

def test_attractiveness_levers_face_swelling():
    face_data = {"swelling": {"level": 70}}
    lever = AttractivenessLevers.detect_lever(face_data, {}, {}, {})
    assert lever["primary_lever"] == "facial_swelling"

def test_attractiveness_levers_skin():
    face_data = {"skin_quality": {"score": 30}}
    lever = AttractivenessLevers.detect_lever(face_data, {}, {}, {})
    assert lever["primary_lever"] == "skin_texture"

def test_attractiveness_levers_body():
    body_data = {"proportions": {"v_taper": 30}}
    lever = AttractivenessLevers.detect_lever({}, body_data, {}, {})
    assert lever["primary_lever"] == "body_proportion"

def test_attractiveness_levers_hair():
    hair_data = {"density": 30, "hairline": {"recession": 60}}
    lever = AttractivenessLevers.detect_lever({}, {}, {}, hair_data)
    assert lever["primary_lever"] == "hair_thinning"

def test_attractiveness_levers_general():
    lever = AttractivenessLevers.detect_lever({}, {}, {}, {})
    assert lever["primary_lever"] == "general"
