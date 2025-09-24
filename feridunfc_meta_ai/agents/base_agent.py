
from __future__ import annotations

import logging
from typing import Dict, Any, Optional

from ..utils.ai_client import AIClient
from ..memory.rag import try_retrieve_context

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Planla-Uygula (Plan & Execute) şablonunu temel alan agent iskeleti.
    Alt sınıflar sadece prompt üretimini özelleştirebilir.
    """
    role: str

    def __init__(self, role: str, model_hint: str, client: Optional[AIClient] = None):
        self.role = role
        self.model_hint = model_hint
        self.client = client or AIClient()
        logger.info("Agent %s -> model_hint=%s", self.role, self.model_hint)

    async def process_task(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Planla ve uygula."""
        # 0) RAG ile ilgili bağlamı al (opsiyonel)
        retrieved = await try_retrieve_context(task, context)
        # 1) Planlama
        planning_prompt = self._create_planning_prompt(task, context, retrieved)
        plan_ns = await self.client.call_model(self.role, prompt=planning_prompt, system=self._system_prompt("planner"))
        execution_plan = getattr(plan_ns, "content", "")
        # 2) Uygulama
        exec_prompt = self._create_execution_prompt(task, context, execution_plan, retrieved)
        exec_ns = await self.client.call_model(self.role, prompt=exec_prompt, system=self._system_prompt("executor"))
        final_output = getattr(exec_ns, "content", "")
        return {"execution_plan": execution_plan, "final_output": final_output, "retrieved_context": retrieved}

    # --- özelleştirilebilir kısımlar ---
    def _system_prompt(self, phase: str) -> str:
        if phase == "planner":
            return "You are a senior planner. Output clear JSON or markdown steps."
        return "You are an expert implementer. Output final artifacts only."

    def _create_planning_prompt(self, task: Dict[str, Any], context: Dict[str, Any], retrieved: Optional[str]) -> str:
        base = f"Görev: {task.get('title') or task.get('description') or task}\nHedef: net adımlar çıkar."
        if retrieved:
            base += f"\n\n[İlgili Kod/Kontext]\n{retrieved[:4000]}"
        return base

    def _create_execution_prompt(self, task: Dict[str, Any], context: Dict[str, Any], plan: str, retrieved: Optional[str]) -> str:
        base = f"Plan:\n{plan}\n\nPlanı adım adım uygula ve sonuç üret."
        if retrieved:
            base += f"\n\n[İlgili Kod/Kontext]\n{retrieved[:4000]}"
        return base
