import os
import httpx
import json

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")


class OpenRouterService:
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = model or OPENROUTER_MODEL
        self.base_url = base_url or OPENROUTER_BASE_URL
        self.api_url = f"{self.base_url}/chat/completions"

    def generate_text(self, prompt: str, model: str = None, temperature: float = 0.7) -> str:
        if not self.api_key:
            print("OpenRouter: No API key provided")
            return ""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "LookCoach",
            }
            payload = {
                "model": model or self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": False,
            }
            response = httpx.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"OpenRouter call failed: {e}")
            return ""

    def generate_json(self, prompt: str, model: str = None) -> dict:
        """Generate JSON response. Appends 'Respond ONLY with valid JSON' to prompt."""
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON. No markdown fences."
        try:
            result = self.generate_text(json_prompt, model)
            # Strip markdown fences if present
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[-1].rsplit("```", 1)[0]
            return json.loads(result)
        except Exception as e:
            print(f"OpenRouter JSON generation failed: {e}")
            return {}

    def analyze_image(self, image_bytes: bytes, prompt: str, model: str = None) -> dict:
        """Analyze image using vision-capable models via OpenRouter."""
        if not self.api_key:
            print("OpenRouter: No API key provided")
            return {}

        try:
            import base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "LookCoach",
            }

            vision_model = model or "google/gemini-2.0-flash-001"

            payload = {
                "model": vision_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.7,
                "stream": False,
            }

            response = httpx.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"]

            # Strip markdown fences if present
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[-1].rsplit("```", 1)[0]

            return json.loads(text)
        except Exception as e:
            print(f"OpenRouter vision call failed: {e}")
            return {}
