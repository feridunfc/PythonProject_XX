# agents/architect.py
from __future__ import annotations
from typing import Dict, Any
from .base import BaseAgent

class ArchitectAgent(BaseAgent):
    def __init__(self, provider: str | None = None, model: str | None = None):
        super().__init__("architect", provider=provider, model=model)

    async def build_prompt(self, task: Dict[str, Any]) -> str:
        spec = task.get("spec") or task.get("description") or ""
        return (
            "Aşağıdaki gereksinim için üst seviye tasarım çıkar.\n"
            "- Ana modüller\n- Dosya/dizin yapısı\n- Veri modelleri (özet)\n"
            "- API uçları (özet)\n- Riskler & notlar (kısa)\n\n"
            f"GEREKSİNİM:\n{spec}"
        )
