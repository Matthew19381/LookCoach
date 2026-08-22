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

# Qualitative analysis prompts — NO numeric attractiveness ratings of the person.
# Only observable state categories (NEURO_PLAN LC-9: risk of dysmorphia).
FACE_PROMPT = """Analyze this face photo. Describe observable state only — do NOT rate or score the person's attractiveness. Return ONLY valid JSON with:
{
  "observations": ["short text observations, e.g. mild puffiness in cheeks"],
  "swelling": {"level": "low|medium|high", "areas": ["cheeks"]},
  "muscle_tension": {"level": "low|medium|high", "areas": ["jaw"]},
  "skin_quality": {"status": "good|fair|needs_attention", "issues": ["dryness"]},
  "focus_areas": [{"area": "skincare|beauty_technique|posture|sleep|nutrition|stress", "priority": "high|medium|low", "reason": "why"}]
}
Respond ONLY with valid JSON."""

BODY_PROMPT = """Analyze this body photo. Describe observable state only — do NOT rate or score the person's attractiveness. Return ONLY valid JSON with:
{
  "observations": ["short text observations"],
  "asymmetries": [{"part": "shoulders", "severity": "mild|moderate|significant"}],
  "missing_muscles": [{"muscle": "delts", "priority": "high|medium|low"}],
  "posture_notes": ["e.g. forward head posture visible"],
  "focus_areas": [{"area": "training|posture|nutrition", "priority": "high|medium|low", "reason": "why"}]
}
Respond ONLY with valid JSON."""

SKIN_PROMPT = """Analyze this skin photo. Describe observable state only — do NOT rate or score the person. Return ONLY valid JSON with:
{
  "skin_type": "dry|oily|combination|normal|unknown",
  "problems": [{"issue": "acne", "severity": "mild|moderate|significant"}],
  "hydration_status": "low|adequate|good",
  "observations": ["short text observations"]
}
Respond ONLY with valid JSON."""

HAIR_PROMPT = """Analyze this hair photo. Describe observable state only — do NOT rate or score the person. Return ONLY valid JSON with:
{
  "hairline_status": "stable|mild_recession|moderate_recession|advanced_recession",
  "density_status": "thin|normal|full",
  "recommendations": ["styling or care suggestions"],
  "observations": ["short text observations"]
}
Respond ONLY with valid JSON."""


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

    def _analyze(self, image_bytes: bytes, prompt: str, fallback) -> dict:
        # Try selected AI service first
        if AI_SERVICE == "openrouter":
            result = self._call_openrouter(image_bytes, prompt)
            if result:
                return result
        elif AI_SERVICE == "gemini":
            result = self._call_gemini(image_bytes, prompt)
            if result:
                return result

        # Fallback chain: Gemini -> OpenRouter -> local heuristic
        result = self._call_gemini(image_bytes, prompt)
        if result:
            return result

        result = self._call_openrouter(image_bytes, prompt)
        if result:
            return result

        return fallback(image_bytes)

    def analyze_face(self, image_bytes: bytes) -> dict:
        return self._analyze(image_bytes, FACE_PROMPT, self._fallback_face)

    def analyze_body(self, image_bytes: bytes) -> dict:
        return self._analyze(image_bytes, BODY_PROMPT, self._fallback_body)

    def analyze_skin(self, image_bytes: bytes) -> dict:
        return self._analyze(image_bytes, SKIN_PROMPT, self._fallback_skin)

    def analyze_hair(self, image_bytes: bytes) -> dict:
        return self._analyze(image_bytes, HAIR_PROMPT, self._fallback_hair)

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
        result = self._call_openrouter(image_bytes, FACE_PROMPT)
        return result or self._get_fallback().analyze_image_fallback(image_bytes, "face")

    def _fallback_body(self, image_bytes: bytes) -> dict:
        result = self._call_openrouter(image_bytes, BODY_PROMPT)
        return result or self._get_fallback().analyze_image_fallback(image_bytes, "body")

    def _fallback_skin(self, image_bytes: bytes) -> dict:
        result = self._call_openrouter(image_bytes, SKIN_PROMPT)
        return result or self._get_fallback().analyze_image_fallback(image_bytes, "skin")

    def _fallback_hair(self, image_bytes: bytes) -> dict:
        result = self._call_openrouter(image_bytes, HAIR_PROMPT)
        return result or self._get_fallback().analyze_image_fallback(image_bytes, "hair")
