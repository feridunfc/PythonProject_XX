# agents/base.py
from __future__ import annotations
import asyncio
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

from utils.ai_client import AIClient

load_dotenv()
log = logging.getLogger("agent.base")


def _pick_provider() -> str:
    """Öncelik: FORCE_PROVIDER -> mevcut anahtar -> mock."""
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


def _default_model(provider: str, role: str) -> str:
    """Sağlayıcıya göre makul varsayılan model."""
    if provider == "openai":
        return os.getenv(f"{role.upper()}_MODEL", "gpt-4o-mini")
    if provider == "gemini":
        return os.getenv(f"{role.upper()}_MODEL", "gemini-1.5-flash")
    if provider == "deepseek":
        return os.getenv(f"{role.upper()}_MODEL", "deepseek-chat")
    return "mock"


class Agent:
    """
    Senkron orchestrator çağrıları için:
      - handle(task) -> dict   (sync)
      - process_task(task) -> dict (async)
    Alt sınıflar genelde _build_prompt ve/veya process_task override eder.
    """
    def __init__(self, role: str, model: str | None = None, provider: str | None = None):
        self.role = role
        self.provider = provider or _pick_provider()
        self.model = model or _default_model(self.provider, role)
        self.client = AIClient()
        self.log = logging.getLogger(f"agent.{role}")
        log.info("Agent init -> role=%s provider=%s model=%s", role, self.provider, self.model)

    async def _build_prompt(self, task: Dict[str, Any]) -> tuple[str, str]:
        """(system, user_prompt) döndürür. Alt sınıflar gerekirse override eder."""
        system = task.get("system_prompt", "You are a helpful, concise assistant.")
        spec = task.get("spec") or task.get("description") or ""
        user = f"Task: {spec}"
        return system, user

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Async çalışma: prompt hazırla -> model çağır -> sonuç döndür."""
        system, prompt = await self._build_prompt(task)
        try:
            text = await self.client.chat(self.provider, self.model, system, prompt)
            return {"status": "ok", "text": text}
        except Exception as e:
            self.log.exception("%s failed", self.role)
            return {"status": "error", "error": str(e)}

    # Orchestrator sync çalışıyorsa bu wrapper'ı kullanır
    def handle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self.process_task(task))


# Eski importları kırmamak için (bazı yerlerde BaseAgent import edilmiş olabilir)
BaseAgent = Agent
