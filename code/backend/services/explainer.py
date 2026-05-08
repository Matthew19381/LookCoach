import os
from .local_llm import LocalLLMService
from .openrouter import OpenRouterService

AI_SERVICE = os.getenv("AI_SERVICE", "openrouter").lower()  # gemini, openrouter, ollama


class ExplainableAI:
    def __init__(self):
        self.llm = None
        self.openrouter = None

    def _get_llm(self):
        if self.llm is None:
            self.llm = LocalLLMService()
        return self.llm

    def _get_openrouter(self):
        if self.openrouter is None:
            self.openrouter = OpenRouterService()
        return self.openrouter

    def quick_summary(self, recommendation: dict) -> str:
        name = recommendation.get("name", "")
        effect = recommendation.get("effect_size", 0)
        time = recommendation.get("time_to_effect", 0)
        evidence = recommendation.get("evidence_level", "")
        return f"{name}: {effect*100:.0f}% effectiveness in {time} weeks (evidence: {evidence})"

    def deep_dive_lesson(self, recommendation: dict) -> str:
        prompt = f"""Explain in detail why "{recommendation.get('name', '')}" is recommended:
- What does it do?
- Why is it effective (effect size: {recommendation.get('effect_size', 0)})?
- How long until results ({recommendation.get('time_to_effect', 0)} weeks)?
- Evidence level: {recommendation.get('evidence_level', '')}
- Any contraindications: {recommendation.get('contraindications', 'none')}

Provide a mini-lesson (2-3 paragraphs) teaching the user about this recommendation."""

        # Try selected AI service first
        if AI_SERVICE == "openrouter":
            try:
                return self._get_openrouter().generate_text(prompt)
            except Exception as e:
                print(f"OpenRouter failed: {e}")

        elif AI_SERVICE == "gemini":
            try:
                return self._get_llm().generate_text(prompt, use_openrouter=True)
            except Exception as e:
                print(f"Gemini/LocalLLM failed: {e}")

        # Fallback chain: selected -> OpenRouter -> Ollama
        try:
            return self._get_llm().generate_text(prompt, use_openrouter=True)
        except Exception as e:
            print(f"Fallback chain failed: {e}")

        # Final hardcoded fallback
        name = recommendation.get("name", "this recommendation")
        effect = recommendation.get("effect_size", 0) * 100
        time = recommendation.get("time_to_effect", 0)
        return f"{name} is recommended for its {effect:.0f}% effectiveness within {time} weeks. Consistent application is key to seeing results. Consult skincare or fitness professionals for personalized advice."
