# feridunfc_meta_ai/agents/base_agent.py
from __future__ import annotations
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class AIAgent:
    """Tüm ajanların miras alacağı basit taban sınıf."""
    def __init__(self, agent_type: str, client: "AIClient"):
        self.agent_type = agent_type.lower()
        self.client = client

    async def process_task(self, task, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


# Geriye dönük uyumluluk (bazı dosyalarda BaseAIAgent kullanılmış olabilir)
class BaseAIAgent(AIAgent):
    pass
