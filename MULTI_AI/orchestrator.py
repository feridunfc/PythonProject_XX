from __future__ import annotations
import asyncio, os, logging, json
from typing import Dict, Any
from dotenv import load_dotenv

from agents.architect import ArchitectAgent
from agents.codegen import CodegenAgent
from agents.critic import CriticAgent
from agents.tester import TesterAgent

load_dotenv()
logging.basicConfig(
    level=os.getenv("LOG_LEVEL","INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

class Orchestrator:
    def __init__(self) -> None:
        self.architect = ArchitectAgent()
        self.codegen   = CodegenAgent()
        self.critic    = CriticAgent()
        self.tester    = TesterAgent()

    async def plan(self, requirements: str) -> Dict[str, Any]:
        resp = await self.architect.process_task({"requirements": requirements})
        if resp.get("status") != "ok":
            raise RuntimeError(f"Architect failed: {resp}")
        # Beklenen JSON plan
        try:
            plan = json.loads(resp["text"])
        except Exception:
            plan = {"title":"Plan","tasks":[{"agent":"codegen","description":"TODO API"}]}
        return plan

    async def run(self, plan: Dict[str, Any]) -> None:
        # Çok basit bir yürütücü örneği
        for t in plan.get("tasks", []):
            agent = t.get("agent","codegen")
            if agent == "codegen":
                r = await self.codegen.process_task({"description": t.get("description",""), "context": t.get("context","")})
            elif agent == "critic":
                r = await self.critic.process_task({"code": t.get("code","")})
            elif agent == "tester":
                r = await self.tester.process_task({"spec": t.get("spec","")})
            else:
                continue
            logging.info("Task %s -> %s", agent, r.get("status"))

async def main():
    orch = Orchestrator()
    req = os.getenv("DEMO_REQUIREMENTS", "Basit TODO API: kullanıcı, görev ekle/listele")
    plan = await orch.plan(req)
    logging.info("Plan title: %s", plan.get("title","(no title)"))
    await orch.run(plan)

if __name__ == "__main__":
    asyncio.run(main())
