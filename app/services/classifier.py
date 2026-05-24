"""LLM classification service (SRP — only calls the LLM)."""

from __future__ import annotations

import json

from openai import OpenAI

from app.core.config import Settings


class ClassificationService:
    """Dependency-inverted: prompt template is injected, not hardcoded."""

    def __init__(self, config: Settings, prompt_template: str) -> None:
        self._client = OpenAI(
            api_key=config.openai_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self._model = config.chat_model
        self._prompt_template = prompt_template

    def classify(self, text: str) -> dict:
        prompt = self._prompt_template.format(text=text)
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        # Safety net: Gemini sometimes wraps JSON in ```json ... ``` fences
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:-1]).strip()
        return json.loads(raw)