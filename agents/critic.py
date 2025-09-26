# agents/critic.py
from __future__ import annotations
from typing import Dict, Any
from .base import BaseAgent

class CriticAgent(BaseAgent):
    def __init__(self, provider: str | None = None, model: str | None = None):
        super().__init__("critic", provider=provider, model=model)

    async def build_prompt(self, task: Dict[str, Any]) -> str:
        code = task.get("text") or task.get("code") or ""
        context = task.get("context") or ""
        return (
            "Aşağıdaki kod/çıktıyı kısa ve net biçimde eleştir. "
            "Hatalar, eksikler, güvenlik ve test önerilerini maddeler halinde yaz. "
            "Gerekiyorsa küçük bir patch planı öner.\n\n"
            f"BAĞLAM:\n{context}\n\n"
            f"KOD/ÇIKTI:\n{code}"
        )
