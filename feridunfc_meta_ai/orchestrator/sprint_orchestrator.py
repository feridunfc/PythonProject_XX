
from __future__ import annotations
import logging
from typing import Dict, Any

from .task_scheduler import run_tasks_map
from ..agents.base_agent import BaseAgent
from ..utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class SprintOrchestrator:
    def __init__(self, concurrency: int = 2):
        self.concurrency = concurrency
        self.active_sprint = None
        self.agents: Dict[str, BaseAgent] = {}
        self.client = AIClient()
        self.context_base: Dict[str, Any] = {}

    async def initialize(self, workdir: str = ".", no_sandbox: bool = False, skip_tests: bool = False):
        self.context_base["workdir"] = workdir
        # Agent örnekleri (örnek)
        from ..agents.base_agent import BaseAgent
        self.agents = {
            "architect": BaseAgent("architect", "gemini-1.5-flash", self.client),
            "codegen":   BaseAgent("codegen", "gemini-1.5-flash", self.client),
            "critic":    BaseAgent("critic", "gemini-1.5-flash", self.client),
            "tester":    BaseAgent("tester", "gemini-1.5-flash", self.client),
            "debugger":  BaseAgent("debugger", "gemini-1.5-flash", self.client),
        }

    async def plan_sprint_from_requirements(self, req: str):
        # Basit mock plan
        self.active_sprint = type("Sprint", (), {"id": "S1", "title": "Basit TODO API", "weeks": [
            type("Week", (), {"tasks": [
                type("Task", (), {"id": "architect-1", "title": "Mimari", "description": req, "dependencies": [], "agent_type": "architect", "status": "pending", "result": None})(),
                type("Task", (), {"id": "codegen-1", "title": "Kod", "description": req, "dependencies": ["architect-1"], "agent_type": "codegen", "status": "pending", "result": None})(),
                type("Task", (), {"id": "critic-1", "title": "Review", "description": req, "dependencies": ["codegen-1"], "agent_type": "critic", "status": "pending", "result": None})(),
                type("Task", (), {"id": "tester-1", "title": "Test", "description": req, "dependencies": ["critic-1"], "agent_type": "tester", "status": "pending", "result": None})(),
            ]})()
        ]})()
        return self.active_sprint

    async def execute_sprint(self, max_workers: int = 4):
        if not self.active_sprint:
            raise ValueError("No active sprint")

        task_coros = {}
        tasks_meta = []
        for week in self.active_sprint.weeks:
            for task in week.tasks:
                tid = task.id
                tasks_meta.append({"id": tid, "dependencies": task.dependencies})
                agent = self.agents.get(task.agent_type)
                async def _make_coro(a=agent, t=task):
                    t.status = "in_progress"
                    try:
                        res = await a.process_task({"id": t.id, "title": t.title, "description": t.description}, {**self.context_base})
                        t.result = res
                        t.status = "completed"
                        return res
                    except Exception as e:
                        t.status = "failed"
                        logger.exception("Task failed %s: %s", t.id, str(e))
                        raise
                task_coros[tid] = _make_coro

        results = await run_tasks_map(task_coros, tasks_meta, max_workers=max_workers)
        return results

    async def aclose(self):
        await self.client.aclose()
