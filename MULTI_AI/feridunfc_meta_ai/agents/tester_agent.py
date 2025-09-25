# feridunfc_meta_ai/agents/tester_agent.py
from __future__ import annotations
from typing import Any, Dict
import logging

from .base_agent import AIAgent  # <-- EKLENDİ

logger = logging.getLogger(__name__)


class TesterAgent(AIAgent):  # <-- AIAgent tabanından türet
    def __init__(self, client):
        super().__init__("tester", client)

    async def process_task(self, task, context: Dict[str, Any]) -> Dict[str, Any]:
        # Plan-only veya test atlama durumunda no-op döner
        if context.get("skip_tests") or context.get("plan_only"):
            return {"ok": True, "skipped": True, "reason": "plan-only/skip_tests"}
        # Buraya gerçek pytest entegrasyonunuzu koyabilirsiniz; şimdilik stub:
        logger.debug("TesterAgent stub çalıştı (task=%s)", getattr(task, "title", ""))
        return {"ok": True, "message": "TesterAgent stub"}
