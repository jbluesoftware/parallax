import json
from typing import Any

import requests

from app.config import OLLAMA_API_URL


class OllamaClient:
    def __init__(self, base_url: str = OLLAMA_API_URL, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def send_chat(self, model: str, prompt: str) -> str:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return self._extract_response(response.json())

    def _extract_response(self, payload: Any) -> str:
        if isinstance(payload, dict):
            choices = payload.get("choices")
            if isinstance(choices, list) and choices:
                first_choice = choices[0]
                if isinstance(first_choice, dict):
                    message = first_choice.get("message")
                    if isinstance(message, dict):
                        return message.get("content", "")
                    if "text" in first_choice:
                        return first_choice.get("text", "")
            if "result" in payload:
                return payload.get("result", "")
        return json.dumps(payload, indent=2)
