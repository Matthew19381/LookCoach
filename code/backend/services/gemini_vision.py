import os
import json
import hashlib
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image
import io

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
AI_SERVICE = os.getenv("AI_SERVICE", "openrouter").lower()  # gemini, openrouter, ollama

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def _cache_key(image_bytes: bytes, analysis_type: str) -> str:
    h = hashlib.sha256(image_bytes + analysis_type.encode()).hexdigest()
    return str(CACHE_DIR / f"{h}.json")


def _get_from_cache(key: str):
    if Path(key).exists():
        return json.loads(Path(key).read_text())
    return None


def _save_to_cache(key: str, data: dict):
    Path(key).write_text(json.dumps(data, ensure_ascii=False, indent=2))


class GeminiVisionService:
    def __init__(self):
        self.client = None
        self.fallback = None
        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"Gemini init failed: {e}")
                self.client = None

    def _image_to_bytes(self, image_bytes: bytes) -> bytes:
        return image_bytes

    def _call_gemini(self, image_bytes: bytes, prompt: str) -> dict:
        if not self.client:
            return None

        cache_key = _cache_key(image_bytes, prompt[:50])
        cached = _get_from_cache(cache_key)
        if cached:
            return cached

        try:
            image = Image.open(io.BytesIO(image_bytes))
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)
            _save_to_cache(cache_key, data)
            return data
        except Exception as e:
            print(f"Gemini call failed: {e}")
            return None

    def analyze_face(self, image_bytes: bytes) -> dict:
        prompt = """Analyze this face photo for looks optimization. Return ONLY valid JSON with:
{
  "proportions": {"score": 0-100, "ratios": {}, "symmetry": 0-100},
  "swelling": {"level": 0-100, "areas": []},
  "muscle_tension": {"level": 0-100, "areas": []},
  "skin_quality": {"score": 0-100, "issues": []},
  "overall_face_score": 0-100
}
Respond ONLY with valid JSON."""
        # Try selected AI service first
        if AI_SERVICE == "openrouter":
            result = self._call_openrouter(image_bytes, prompt)
            if result:
                return result
        elif AI_SERVICE == "gemini":
            result = self._call_gemini(image_bytes, prompt)
            if result:
                return result

        # Fallback chain: Gemini -> OpenRouter -> Ollama
        result = self._call_gemini(image_bytes, prompt)
        if result:
            return result

        result = self._call_openrouter(image_bytes, prompt)
        if result:
            return result

        return self._fallback_face(image_bytes)

    def analyze_body(self, image_bytes: bytes) -> dict:
        prompt = """Analyze this body photo for aesthetics. Return ONLY valid JSON with:
{
  "proportions": {"v_taper": 0-100, "shoulder_waist_ratio": 0.0, "score": 0-100},
  "asymmetries": [{"part": "", "severity": 0-100}],
  "missing_muscles": [{"muscle": "", "priority": "high/medium/low"}],
  "overall_body_score": 0-100
}
Respond ONLY with valid JSON."""
        # Try selected AI service first
        if AI_SERVICE == "openrouter":
            result = self._call_openrouter(image_bytes, prompt)
            if result:
                return result
        elif AI_SERVICE == "gemini":
            result = self._call_gemini(image_bytes, prompt)
            if result:
                return result

        # Fallback chain: Gemini -> OpenRouter -> Ollama
        result = self._call_gemini(image_bytes, prompt)
        if result:
            return result

        result = self._call_openrouter(image_bytes, prompt)
        if result:
            return result

        return self._fallback_body(image_bytes)

    def analyze_skin(self, image_bytes: bytes) -> dict:
        prompt = """Analyze this skin photo. Return ONLY valid JSON with:
{
  "skin_type": "dry/oily/combination/normal",
  "problems": [{"issue": "", "severity": 0-100}],
  "hydration": 0-100,
  "overall_skin_score": 0-100
}
Respond ONLY with valid JSON."""
        # Try selected AI service first
        if AI_SERVICE == "openrouter":
            result = self._call_openrouter(image_bytes, prompt)
            if result:
                return result
        elif AI_SERVICE == "gemini":
            result = self._call_gemini(image_bytes, prompt)
            if result:
                return result

        # Fallback chain: Gemini -> OpenRouter -> Ollama
        result = self._call_gemini(image_bytes, prompt)
        if result:
            return result

        result = self._call_openrouter(image_bytes, prompt)
        if result:
            return result

        return self._fallback_skin(image_bytes)

    def analyze_hair(self, image_bytes: bytes) -> dict:
        prompt = """Analyze this hair photo. Return ONLY valid JSON with:
{
  "density": 0-100,
  "hairline": {"type": "", "recession": 0-100},
  "thickness": 0-100,
  "recommendations": [""],
  "overall_hair_score": 0-100
}
Respond ONLY with valid JSON."""
        # Try selected AI service first
        if AI_SERVICE == "openrouter":
            result = self._call_openrouter(image_bytes, prompt)
            if result:
                return result
        elif AI_SERVICE == "gemini":
            result = self._call_gemini(image_bytes, prompt)
            if result:
                return result

        # Fallback chain: Gemini -> OpenRouter -> Ollama
        result = self._call_gemini(image_bytes, prompt)
        if result:
            return result

        result = self._call_openrouter(image_bytes, prompt)
        if result:
            return result

        return self._fallback_hair(image_bytes)

    def _get_fallback(self):
        if self.fallback is None:
            from .local_llm import LocalLLMService
            self.fallback = LocalLLMService()
        return self.fallback

    def _get_openrouter(self):
        if not hasattr(self, 'openrouter'):
            from .openrouter import OpenRouterService
            self.openrouter = OpenRouterService()
        return self.openrouter

    def _call_openrouter(self, image_bytes: bytes, prompt: str) -> dict:
        """Try OpenRouter vision models as fallback."""
        try:
            return self._get_openrouter().analyze_image(image_bytes, prompt)
        except Exception as e:
            print(f"OpenRouter vision call failed: {e}")
            return None

    def _fallback_face(self, image_bytes: bytes) -> dict:
        result = self._call_openrouter(image_bytes, """Analyze this face photo for looks optimization. Return ONLY valid JSON with:
{
  "proportions": {"score": 0-100, "ratios": {}, "symmetry": 0-100},
  "swelling": {"level": 0-100, "areas": []},
  "muscle_tension": {"level": 0-100, "areas": []},
  "skin_quality": {"score": 0-100, "issues": []},
  "overall_face_score": 0-100
}
Respond ONLY with valid JSON.""")
        return result or self._get_fallback().analyze_image_fallback(image_bytes, "face")

    def _fallback_body(self, image_bytes: bytes) -> dict:
        result = self._call_openrouter(image_bytes, """Analyze this body photo for aesthetics. Return ONLY valid JSON with:
{
  "proportions": {"v_taper": 0-100, "shoulder_waist_ratio": 0.0, "score": 0-100},
  "asymmetries": [{"part": "", "severity": 0-100}],
  "missing_muscles": [{"muscle": "", "priority": "high/medium/low"}],
  "overall_body_score": 0-100
}
Respond ONLY with valid JSON.""")
        return result or self._get_fallback().analyze_image_fallback(image_bytes, "body")

    def _fallback_skin(self, image_bytes: bytes) -> dict:
        result = self._call_openrouter(image_bytes, """Analyze this skin photo. Return ONLY valid JSON with:
{
  "skin_type": "dry/oily/combination/normal",
  "problems": [{"issue": "", "severity": 0-100}],
  "hydration": 0-100,
  "overall_skin_score": 0-100
}
Respond ONLY with valid JSON.""")
        return result or self._get_fallback().analyze_image_fallback(image_bytes, "skin")

    def _fallback_hair(self, image_bytes: bytes) -> dict:
        result = self._call_openrouter(image_bytes, """Analyze this hair photo. Return ONLY valid JSON with:
{
  "density": 0-100,
  "hairline": {"type": "", "recession": 0-100},
  "thickness": 0-100,
  "recommendations": [""],
  "overall_hair_score": 0-100
}
Respond ONLY with valid JSON.""")
        return result or self._get_fallback().analyze_image_fallback(image_bytes, "hair")
