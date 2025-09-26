# agents/codegen.py
from __future__ import annotations
from typing import Dict, Any
from .base import BaseAgent

class CodegenAgent(BaseAgent):
    def __init__(self, provider: str | None = None, model: str | None = None):
        super().__init__("codegen", provider=provider, model=model)

    async def build_prompt(self, task: Dict[str, Any]) -> str:
        plan = task.get("plan") or task.get("text") or task.get("description") or task.get("spec") or ""
        return (
            "Aşağıdaki plana/speke uygun üretim kalitesinde kod yaz. "
            "Gerekiyorsa minimal dosya/dizin yapısı öner. "
            "Yanıtını KISA tut, kod blokları ve kısa açıklama ver.\n\n"
            f"PLAN/SPEC:\n{plan}"
        )