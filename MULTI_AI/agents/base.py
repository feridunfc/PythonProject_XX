# agents/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

from utils.ai_client import AIClient

load_dotenv()

log = logging.getLogger("agent.base")


def _pick_provider() -> str:
    """Öncelik: FORCE_PROVIDER -> OPENAI -> GEMINI -> DEEPSEEK -> mock"""
    forced = (os.getenv("FORCE_PROVIDER") or "").strip().lower()
    if forced:
        return forced
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    if os.getenv("DEEPSEEK_API_KEY"):
        return "deepseek"
    return "mock"


def _default_model(provider: str) -> str:
    if provider == "gemini":
        return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    if provider == "openai":
        # ucuz ve yeterli bir varsayılan
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if provider == "deepseek":
        return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    return "mock"


class BaseAgent(ABC):
    def __init__(self, role: str, provider: Optional[str] = None, model: Optional[str] = None):
        self.role = role
        self.provider = (provider or os.getenv("FORCE_PROVIDER") or _pick_provider()).lower()
        self.model = model or _default_model(self.provider)
        self.client = AIClient()
        self.log = logging.getLogger(f"agent.{role}")
        log.info("Agent init -> role=%s provider=%s model=%s", self.role, self.provider, self.model)

    @abstractmethod
    async def build_prompt(self, task: Dict[str, Any]) -> str:
        ...

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ortak çalışma: build_prompt -> LLM çağrısı.
        Çocuk sınıflar sadece build_prompt'u uygular.
        """
        system = task.get("system_prompt", "You are a helpful, concise assistant.")
        prompt = await self.build_prompt(task)
        try:
            text = await self.client.chat(self.provider, self.model, system, prompt)
            return {"status": "ok", "text": text}
        except Exception as e:
            self.log.exception("%s failed", self.role)
            return {"status": "error", "error": str(e)}
