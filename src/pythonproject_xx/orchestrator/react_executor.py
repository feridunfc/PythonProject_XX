import os
from typing import Dict, List, Set, Any

from pythonproject_xx.agents.planner_agent import ExecutionPlan, PlanStep
from pythonproject_xx.tools.linter import LinterTool
from pythonproject_xx.tools.file_patcher import FilePatcherTool
from pythonproject_xx.utils.ai_client import AIClient
from pythonproject_xx.observability.obs import obs

# --- tool registry
TOOL_REGISTRY: Dict[str, Any] = {
    "linter.ruff": LinterTool(),
    "file.patch": FilePatcherTool(),
}

# --- RBAC: role -> allowed tools
ROLE_ALLOWED_TOOLS: Dict[str, Set[str]] = {
    "codegen": {"linter.ruff", "file.patch"},
    "tester": {"linter.ruff"},
    "*": {"linter.ruff"},
}

class ReactRunner:
    """
    Minimal ReAct yürütücüsü:
    - RBAC & bütçe kontrolü
    - SELF_CHECK_EVERY adımında sanity-check (self-reflection)
    """
    def __init__(self, role: str = "codegen"):
        self.role = role
        self.tool_calls = 0
        self.cost_usd = 0.0
        self.history: List[Dict[str, Any]] = []
        self.ai = AIClient()

        # Env'leri örnek oluşumunda oku (test içinde os.environ set edildikten sonra!)
        self.self_check_every = int(os.getenv("SELF_CHECK_EVERY", "3"))
        self.max_tool_calls   = int(os.getenv("MAX_TOOL_CALLS", "20"))
        self.max_cost_usd     = float(os.getenv("MAX_COST_USD", "1.0"))
        self.mock_ai          = os.getenv("MOCK_AI", "true").lower() in ("1","true","yes")

    # --- izin kontrolü
    def _allowed(self, tool_name: str) -> bool:
        allow = ROLE_ALLOWED_TOOLS.get(self.role, ROLE_ALLOWED_TOOLS.get("*", set()))
        return tool_name in allow

    # --- basit self-correction adımı
    def _sanity_check(self) -> Dict[str, Any]:
        step = len(self.history)
        if step == 0 or step % self.self_check_every != 0:
            return {"ok": True, "decision": "continue"}

        if self.mock_ai:
            decision = "stop" if step >= self.self_check_every else "continue"
            return {"ok": True, "decision": decision}

        # Gerçek çağrı (ucuz rota)
        prompt = (
            "You are a sanity checker. Given the Think/Act/Observe history, "
            "decide whether to CONTINUE or STOP to avoid loops.\n\n"
            f"History (JSON-like): {self.history}\n\n"
            "Answer strictly with CONTINUE or STOP."
        )
        out = self.ai.chat(model="cheap", messages=[{"role":"user","content":prompt}])
.event("llm.chat", {"role": self.role})
        text = (out or "").strip().lower()
        decision = "stop" if "stop" in text else "continue"
        self.cost_usd += 0.0001
        return {"ok": True, "decision": decision}

    # --- bütçe kontrolü
    def _check_budget(self):
        if self.tool_calls >= self.max_tool_calls:
            return {"ok": False, "error": "budget_exceeded:tool_calls",
                    "tool_calls": self.tool_calls, "cost_usd": self.cost_usd}
        if self.cost_usd >= self.max_cost_usd:
            return {"ok": False, "error": "budget_exceeded:cost_usd",
                    "tool_calls": self.tool_calls, "cost_usd": self.cost_usd}
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
                    return {"ok": False, "error": f"forbidden_tool:{step.name}",
                            "role": self.role, "history": self.history}
                tool = TOOL_REGISTRY.get(step.name)
                if not tool:
                    return {"ok": False, "error": f"unknown_tool:{step.name}",
                            "history": self.history}
                last = tool.run(**(step.args or {}))
.event("tool.run", {"name": step.name, "role": self.role, "args": step.args or {}})
                self.tool_calls += 1
                self.history.append({"kind": "tool", "name": step.name,
                                     "args": step.args or {}, "result": last})

            elif step.kind == "llm":
                out = self.ai.chat(messages=[{"role":"user","content": step.args.get("prompt","")}])
.event("llm.chat", {"role": self.role})
                last = {"llm": out}
                self.cost_usd += 0.0001
                self.history.append({"kind": "llm",
                                     "prompt": step.args.get("prompt",""),
                                     "result": out})

            elif step.kind == "finish":
                return {"ok": True, "result": last, "history": self.history}

            # her adım sonrası sanity check
            sc = self._sanity_check()
.event("react.sanity_check", {"decision": sc.get("decision"), "steps": len(self.history)})
            if sc.get("decision") == "stop":
                return {"ok": True, "stopped_by": "sanity_check",
                        "result": last, "history": self.history}

        return {"ok": True, "result": last, "history": self.history}