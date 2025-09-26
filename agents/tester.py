# agents/tester.py
from __future__ import annotations
from typing import Dict, Any
from .base import BaseAgent

class TesterAgent(BaseAgent):
    def __init__(self, provider: str | None = None, model: str | None = None):
        super().__init__("tester", provider=provider, model=model)

    async def build_prompt(self, task: Dict[str, Any]) -> str:
        code = task.get("text") or task.get("code") or ""
        return (
            "Aşağıdaki kod için minimal test planı üret. "
            "3-6 arası test vakası ve beklenen sonuçları yaz. "
            "Uygunsa pytest iskeleti ver (kısa tut).\n\n"
            f"KOD:\n{code}"
        )
