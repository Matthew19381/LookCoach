import os
import httpx

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


class LocalLLMService:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL
        self.api_url = f"{self.base_url}/api/generate"
        self.openrouter = None

    def _get_openrouter(self):
        if self.openrouter is None:
            from .openrouter import OpenRouterService
            self.openrouter = OpenRouterService()
        return self.openrouter

    def generate_text(self, prompt: str, model: str = None, use_openrouter: bool = True) -> str:
        """Generate text with fallback: Ollama → OpenRouter → hardcoded."""
        # Try Ollama first
        try:
            response = httpx.post(
                self.api_url,
                json={
                    "model": model or self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            print(f"Ollama call failed: {e}")

        # Try OpenRouter as fallback
        if use_openrouter:
            try:
                return self._get_openrouter().generate_text(prompt, model)
            except Exception as e:
                print(f"OpenRouter fallback failed: {e}")

        # Final hardcoded fallback
        return ""

    def analyze_image_fallback(self, image_bytes: bytes, analysis_type: str) -> dict:
        """No AI available: say so - never invent a state.

        Until 2026-11-02 this returned fixed observations ("swelling: medium",
        "skin: fair") that looked like a real analysis and drove recommendations
        (and would have sent a sodium limit to Dieta). The caller sees
        `fallback: True` and refuses to store the result."""
        return {
            "fallback": True,
            "analysis_type": analysis_type,
            "observations": ["Analiza AI niedostępna - brak wyniku"],
        }
