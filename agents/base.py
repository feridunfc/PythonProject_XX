from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging, os

from utils.ai_client import AIClient, model_for_role

class BaseAgent(ABC):
    def __init__(self, role: str, provider: str | None = None):
        self.role = role
        self.provider = provider or os.getenv("AI_PROVIDER","openai")  # ENV ile override edilebilir
        self.model = model_for_role(role)
        self.client = AIClient()
        self.log = logging.getLogger(f"agent.{role}")

    @abstractmethod
    async def build_prompt(self, task: Dict[str, Any]) -> str: ...

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Common execution flow with logging + error handling."""
        prompt = await self.build_prompt(task)
        system = task.get("system_prompt","You are a helpful, concise assistant.")
        try:
            text = await self.client.chat(self.provider, self.model, system, prompt)
            return {"status":"ok","text":text}
        except Exception as e:
            self.log.exception("%s failed", self.role)
            return {"status":"error","error":str(e)}
