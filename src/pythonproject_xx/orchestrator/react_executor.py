import os
from typing import Dict, List, Optional, Set, Any

from pythonproject_xx.agents.planner_agent import ExecutionPlan, PlanStep
from pythonproject_xx.tools.linter import LinterTool
from pythonproject_xx.tools.file_patcher import FilePatcherTool
from pythonproject_xx.utils.ai_client import AIClient
from pythonproject_xx.observability.obs import obs

TOOL_REGISTRY: Dict[str, Any] = {
    "linter.ruff": LinterTool(),
    "file.patch": FilePatcherTool(),
}

ROLE_ALLOWED_TOOLS: Dict[str, Set[str]] = {
    "codegen": {"linter.ruff", "file.patch"},
    "tester": {"linter.ruff"},
    "*": {"linter.ruff"},
}

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1","true","yes","on")

class ReactRunner:
    """Minimal ReAct yürütücüsü: RBAC, bütçe, periyodik sanity-check."""
    def __init__(self, role: str = "codegen", ai: Optional[AIClient] = None) -> None:
        self.role = role
        self.tool_calls = 0
        self.cost_usd = 0.0
        self.history: List[Dict[str, Any]] = []
        self.ai = ai or AIClient()

    def _allowed(self, tool_name: str) -> bool:
        allow = ROLE_ALLOWED_TOOLS.get(self.role, ROLE_ALLOWED_TOOLS.get("*", set()))
        return tool_name in allow

    def _sanity_check(self) -> Dict[str, Any]:
        """SELF_CHECK_EVERY adımda dur/ devam kararı; MOCK_AI ise deterministik durdur."""
        step = len(self.history)
        every = _env_int("SELF_CHECK_EVERY", 3)
        if step == 0 or every <= 0 or (step % every) != 0:
            return {"ok": True, "decision": "continue"}

        if _env_bool("MOCK_AI", True):
            decision = "stop"
        else:
            prompt = (
                "You are a sanity checker. Given the Think/Act/Observe history, "
                "decide whether to CONTINUE or STOP to avoid loops.\n\n"
                f"History: {self.history}\n\n"
                "Answer strictly with CONTINUE or STOP."
            )
            out = self.ai.chat(model="cheap", messages=[{"role":"user","content": prompt}]) or ""
            decision = "stop" if "stop" in out.lower() else "continue"
            self.cost_usd += 0.0001
        return {"ok": True, "decision": decision}

    def _check_budget(self) -> Optional[Dict[str, Any]]:
        max_calls = _env_int("MAX_TOOL_CALLS", 20)
        max_cost  = _env_float("MAX_COST_USD", 1.0)
        if self.tool_calls >= max_calls:
            return {"ok": False, "error": "budget_exceeded:tool_calls", "tool_calls": self.tool_calls, "cost_usd": self.cost_usd}
        if self.cost_usd >= max_cost:
            return {"ok": False, "error": "budget_exceeded:cost_usd", "tool_calls": self.tool_calls, "cost_usd": self.cost_usd}
        return None

    def run(self, plan: ExecutionPlan) -> Dict[str, Any]:
        last: Dict[str, Any] = {}
        for step in plan.steps:
            lim = self._check_budget()
            if lim:
                lim["history"] = self.history
                return lim

            if step.kind == "tool":
                if not self._allowed(step.name):
                    return {"ok": False, "error": f"forbidden_tool:{step.name}", "role": self.role, "history": self.history}
                tool = TOOL_REGISTRY.get(step.name)
                if not tool:
                    return {"ok": False, "error": f"unknown_tool:{step.name}", "history": self.history}
                last = tool.run(**(step.args or {}))
                self.tool_calls += 1
                self.history.append({"kind":"tool","name":step.name,"args":step.args or {}, "result": last})
                obs.event("tool.run", {"name": step.name, "role": self.role, "args": step.args or {}})

            elif step.kind == "llm":
                prompt = (step.args or {}).get("prompt", "")
                out = self.ai.chat(model="cheap", messages=[{"role":"user","content": prompt}])
                last = {"llm": out}
                self.cost_usd += 0.0001
                self.history.append({"kind":"llm","prompt": prompt, "result": out})
                obs.event("llm.chat", {"role": self.role})

            elif step.kind == "finish":
                return {"ok": True, "result": last, "history": self.history}

            # Self-correction periyodu
            sc = self._sanity_check()
            obs.event("react.sanity_check", {"decision": sc.get("decision"), "steps": len(self.history)})
            if sc.get("decision") == "stop":
                return {"ok": True, "stopped_by": "sanity_check", "result": last, "history": self.history}

        return {"ok": True, "result": last, "history": self.history}