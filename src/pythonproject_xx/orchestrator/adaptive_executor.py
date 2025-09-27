class AdaptiveExecutor:
    def __init__(self, critic, tester): self.critic=critic; self.tester=tester
    async def run_once(self, agent, task, context):
        res=await agent.run(task, context); context.update(res)
        if 'files' in res:
            crit=await self.critic.run(task, context); context.update(crit)
            if not crit.get('passed', True): return context
            test=await self.tester.run(task, context); context.update(test)
        return context

from dataclasses import dataclass
from typing import List, Dict
from pythonproject_xx.agents.planner_agent import ExecutionPlan, PlanStep
from pythonproject_xx.tools.linter import LinterTool

TOOL_REGISTRY = {
    "linter.ruff": LinterTool(),
}

def run_plan(plan: ExecutionPlan) -> Dict:
    last = {}
    for step in plan.steps:
        if step.kind == "tool":
            tool = TOOL_REGISTRY.get(step.name)
            if not tool: 
                return {"ok": False, "error": f"unknown tool {step.name}"}
            last = tool.run(**(step.args or {}))
        elif step.kind == "finish":
            return {"ok": True, "result": last}
    return {"ok": True, "result": last}