# agents/codegen.py
from __future__ import annotations
from typing import Dict, Any
from .base import BaseAgent

class CodegenAgent(BaseAgent):
    """
    Codegen ajanı: önce kısa bir yürütme planı çıkarır (planlama),
    ardından o plana sadık kalarak kodu üretir (uygulama).
    Çıktıda hem execution_plan hem de nihai code metni döner.
    """
    def __init__(self, provider: str | None = None, model: str | None = None):
        super().__init__("codegen", provider=provider, model=model)

    async def build_prompt(self, task: Dict[str, Any]) -> str:
        # BaseAgent.process_task kullanılırsa fallback prompt (tek-aşamalı)
        req = task.get("spec") or task.get("description") or task.get("plan") or task.get("text") or ""
        return (
            "Aşağıdaki gereksinime uygun, çalışır örnek kod üret. "
            "Yanıtı kısa tut; kod blokları ve kısa açıklama ver.\n\n"
            f"GEREKSİNİM:\n{req}"
        )

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        system = task.get(
            "system_prompt",
            "You are a senior Python engineer. Keep answers concise and practical."
        )
        req = task.get("spec") or task.get("description") or task.get("text") or ""

        # --- Aşama 1: Planlama ---
        planning_prompt = (
            "Görevi çözmek için kısa bir uygulama planı çıkar. "
            "Plan, 3-7 maddelik adımlardan oluşsun; dosya/dizin yapısı ve ana fonksiyonları belirt.\n\n"
            f"GÖREV:\n{req}"
        )
        try:
            execution_plan = await self.client.chat(self.provider, self.model, system, planning_prompt)
        except Exception as e:
            self.log.exception("codegen planning failed")
            return {"status": "error", "stage": "planning", "error": str(e)}

        # --- Aşama 2: Uygulama ---
        execution_prompt = (
            "Aşağıdaki plana sadık kalarak minimal ama çalışır bir örnek kod üret. "
            "Gerekiyorsa kısa bir README metni öner. Kodu Markdown kod bloğu içinde ver.\n\n"
            f"PLAN:\n{execution_plan}\n\n"
            f"GÖREV/BAĞLAM:\n{req}"
        )
        try:
            final_code = await self.client.chat(self.provider, self.model, system, execution_prompt)
        except Exception as e:
            self.log.exception("codegen execution failed")
            return {"status": "error", "stage": "execution", "error": str(e), "execution_plan": execution_plan}

        return {"status": "ok", "execution_plan": execution_plan, "text": final_code}
