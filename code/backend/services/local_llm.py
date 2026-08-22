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
        """Basic heuristic fallback when Gemini is unavailable. Qualitative only."""
        note = "Fallback analysis - limited accuracy"
        if analysis_type == "face":
            return {
                "observations": [note],
                "swelling": {"level": "medium", "areas": []},
                "muscle_tension": {"level": "medium", "areas": []},
                "skin_quality": {"status": "fair", "issues": []},
                "focus_areas": [
                    {"area": "skincare", "priority": "medium", "reason": note},
                ],
            }
        elif analysis_type == "body":
            return {
                "observations": [note],
                "asymmetries": [],
                "missing_muscles": [],
                "posture_notes": [],
                "focus_areas": [
                    {"area": "training", "priority": "medium", "reason": note},
                ],
            }
        elif analysis_type == "skin":
            return {
                "skin_type": "unknown",
                "problems": [],
                "hydration_status": "adequate",
                "observations": [note],
            }
        elif analysis_type == "hair":
            return {
                "hairline_status": "stable",
                "density_status": "normal",
                "recommendations": ["Consult a professional for accurate analysis"],
                "observations": [note],
            }
        return {"error": f"Unknown analysis type: {analysis_type}", "observations": [note]}
