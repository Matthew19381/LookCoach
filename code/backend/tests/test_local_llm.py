import unittest.mock as mock
from services.local_llm import LocalLLMService

def test_local_llm_init():
    llm = LocalLLMService()
    assert llm.base_url == "http://localhost:11434"
    assert llm.model == "llama3"

def test_local_llm_custom_init():
    llm = LocalLLMService(base_url="http://test:1234", model="mistral")
    assert llm.base_url == "http://test:1234"
    assert llm.model == "mistral"
    assert llm.api_url == "http://test:1234/api/generate"

def test_generate_text_success():
    llm = LocalLLMService()
    mock_response = mock.MagicMock()
    mock_response.json.return_value = {"response": "Test response"}
    mock_response.raise_for_status = mock.MagicMock()

    with mock.patch.object(llm, 'api_url', create=True):
        with mock.patch('services.local_llm.httpx.post', return_value=mock_response):
            result = llm.generate_text("Test prompt")
            assert result == "Test response"

def test_generate_text_failure():
    llm = LocalLLMService()
    with mock.patch('services.local_llm.httpx.post', side_effect=Exception("Connection error")):
        result = llm.generate_text("Test prompt")
        assert result == ""

def test_analyze_image_fallback_face():
    llm = LocalLLMService()
    result = llm.analyze_image_fallback(b"fake_image", "face")
    assert "swelling" in result
    assert "observations" in result
    assert result["swelling"]["level"] in ("low", "medium", "high")

def test_analyze_image_fallback_body():
    llm = LocalLLMService()
    result = llm.analyze_image_fallback(b"fake_image", "body")
    assert "asymmetries" in result
    assert "posture_notes" in result

def test_analyze_image_fallback_skin():
    llm = LocalLLMService()
    result = llm.analyze_image_fallback(b"fake_image", "skin")
    assert "skin_type" in result
    assert "hydration_status" in result

def test_analyze_image_fallback_hair():
    llm = LocalLLMService()
    result = llm.analyze_image_fallback(b"fake_image", "hair")
    assert "hairline_status" in result
    assert "density_status" in result

def test_analyze_image_fallback_unknown():
    llm = LocalLLMService()
    result = llm.analyze_image_fallback(b"fake_image", "unknown")
    assert "error" in result
