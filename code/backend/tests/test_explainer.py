from services.explainer import ExplainableAI
import unittest.mock as mock

def test_explainer_quick_summary():
    ai = ExplainableAI()
    rec = {'name': 'Test Product', 'effect_size': 0.7, 'time_to_effect': 4, 'evidence_level': 'RCT'}
    summary = ai.quick_summary(rec)
    assert 'Test Product' in summary
    assert '70%' in summary or '70.0%' in summary
    assert 'RCT' in summary

def test_explainer_deep_dive(monkeypatch):
    monkeypatch.setenv("AI_SERVICE", "gemini")
    from importlib import reload
    import services.explainer
    reload(services.explainer)
    from services.explainer import ExplainableAI, AI_SERVICE
    assert AI_SERVICE == "gemini"

    ai = ExplainableAI()
    rec = {'name': 'Retinol', 'effect_size': 0.85, 'time_to_effect': 12, 'evidence_level': 'RCT', 'contraindications': 'pregnancy'}
    with mock.patch.object(ai, '_get_llm') as mock_get_llm:
        mock_llm = mock.MagicMock()
        mock_llm.generate_text.return_value = 'This is a test lesson about Retinol.'
        mock_get_llm.return_value = mock_llm
        lesson = ai.deep_dive_lesson(rec)
        assert isinstance(lesson, str)
        assert len(lesson) > 0
