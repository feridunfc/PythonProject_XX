from __future__ import annotations
from typing import Any, Dict
import os

from .base import Provider

class OpenAIProvider(Provider):
    name = "openai"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def chat(self, model: str, messages: list[dict], temperature: float = 0.3) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        # Lazy import (SDK 1.x)
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        resp = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
        return {
            "provider": self.name,
            "model": model,
            "output": resp.choices[0].message.content,
            "usage": {"prompt_tokens": resp.usage.prompt_tokens, "completion_tokens": resp.usage.completion_tokens, "total_tokens": resp.usage.total_tokens},
            "temperature": temperature,
        }