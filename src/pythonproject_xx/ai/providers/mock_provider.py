from __future__ import annotations
from typing import Any, Dict

from .base import Provider

class MockProvider(Provider):
    name = "mock"

    def chat(self, model: str, messages: list[dict], temperature: float = 0.3) -> Dict[str, Any]:
        user = next((m["content"] for m in messages if m.get("role") == "user"), "")
        return {
            "provider": self.name,
            "model": model,
            "output": f"[MOCK] {user[:120]}",
            "usage": {"prompt_tokens": len(user.split()), "completion_tokens": 8, "total_tokens": len(user.split()) + 8},
            "temperature": temperature,
        }