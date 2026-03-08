from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

import requests


class GroqClient:
    def __init__(self, api_key: str, model: str, api_base: str) -> None:
        self.api_key = api_key
        self.model = model
        self.api_base = api_base.rstrip("/")

    @classmethod
    def from_env(cls) -> "GroqClient":
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY. Set it in your .env file.")

        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        api_base = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1").strip()
        return cls(api_key=api_key, model=model, api_base=api_base)

    def chat_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        url = f"{self.api_base}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = self._extract_json(content)
        if not isinstance(parsed, dict):
            raise ValueError("Expected a top-level JSON object from Groq response.")
        return parsed

    def _extract_json(self, raw: str) -> Any:
        """Parse JSON from plain text or fenced code blocks."""
        text = raw.strip()

        # Remove common fenced wrappers.
        fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
        if fence_match:
            text = fence_match.group(1).strip()

        # Try direct parse first.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Fallback: locate first JSON object.
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])

        raise ValueError("Could not parse JSON from Groq response.")


def chunk_text(text: str, chunk_size: int = 12000) -> List[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end
    return chunks