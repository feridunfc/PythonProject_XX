# agents/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import os
from dotenv import load_dotenv

from utils.ai_client import AIClient, model_for_role

load_dotenv()  # .env dosyasını yükle


class BaseAgent(ABC):
    def __init__(self, role: str, provider: str | None = None):
        self.role = role
        # .env -> AI_PROVIDER (openai | anthropic | deepseek)
        self.provider = provider or os.getenv("AI_PROVIDER", "openai")
        self.model = model_for_role(role)
        self.client = AIClient()
        self.log = logging.getLogger(f"agent.{role}")

    @abstractmethod
    async def build_prompt(self, task: Dict[str, Any]) -> str:
        ...

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = await self.build_prompt(task)
        system = task.get("system_prompt", "You are a helpful, concise assistant.")
        try:
            text = await self.client.chat(self.provider, self.model, system, prompt)
            return {"status": "ok", "text": text}
        except Exception as e:
            self.log.exception("%s failed", self.role)
            return {"status": "error", "error": str(e)}
