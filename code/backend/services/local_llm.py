import os
import httpx

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


class LocalLLMService:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL
        self.api_url = f"{self.base_url}/api/generate"

    def generate_text(self, prompt: str, model: str = None) -> str:
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
            return ""

    def analyze_image_fallback(self, image_bytes: bytes, analysis_type: str) -> dict:
        """Basic heuristic fallback when Gemini is unavailable."""
        if analysis_type == "face":
            return {
                "proportions": {"score": 50, "ratios": {}, "symmetry": 50},
                "swelling": {"level": 30, "areas": []},
                "muscle_tension": {"level": 30, "areas": []},
                "skin_quality": {"score": 50, "issues": []},
                "overall_face_score": 50,
                "note": "Fallback analysis - limited accuracy",
            }
        elif analysis_type == "body":
            return {
                "proportions": {"v_taper": 50, "shoulder_waist_ratio": 1.5, "score": 50},
                "asymmetries": [],
                "missing_muscles": [],
                "overall_body_score": 50,
                "note": "Fallback analysis - limited accuracy",
            }
        elif analysis_type == "skin":
            return {
                "skin_type": "unknown",
                "problems": [],
                "hydration": 50,
                "overall_skin_score": 50,
                "note": "Fallback analysis - limited accuracy",
            }
        elif analysis_type == "hair":
            return {
                "density": 50,
                "hairline": {"type": "unknown", "recession": 0},
                "thickness": 50,
                "recommendations": ["Consult a professional for accurate analysis"],
                "overall_hair_score": 50,
                "note": "Fallback analysis - limited accuracy",
            }
        return {"error": "Unknown analysis type", "overall_score": 50}
