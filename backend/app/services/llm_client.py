from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from google import genai

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    text: str
    model: str = "gemini-3.5-flash"


FALLBACK_TEXT = {
    "rw": "Mbabarira, ntibishoboka kubona igisubizo muri iki gihe. Gerageza nanone.",
    "en": "Sorry, I couldn't generate a response right now. Please try again.",
}


class LLMClient:
    def __init__(self, model_name: str = "gemini-3.5-flash") -> None:
        self.model_name = model_name
        api_key = os.getenv("GEMINI_API_KEY")
        self._client = genai.Client(api_key=api_key) if api_key else None

    def generate_reply(self, prompt: str, system_prompt: str | None = None) -> LLMResponse:
        if self._client is None:
            logger.error("GEMINI_API_KEY not set; cannot call Gemini")
            return LLMResponse(text=FALLBACK_TEXT["en"], model="unavailable")

        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"[{system_prompt}]\n\n{prompt}"

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )
            text = (response.text or "").strip()
            if not text:
                return LLMResponse(text=FALLBACK_TEXT["en"], model=self.model_name)
            return LLMResponse(text=text, model=self.model_name)
        except Exception as exc:
            logger.error(f"Gemini call failed: {exc}")
            return LLMResponse(text=FALLBACK_TEXT["en"], model="error")
