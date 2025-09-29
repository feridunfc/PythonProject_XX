from dataclasses import dataclass
from typing import List, Literal, Optional, Dict, Any

@dataclass
class PlanStep:
    kind: Literal["tool", "llm", "finish"]
    name: str = ""
    args: Optional[Dict[str, Any]] = None

@dataclass
class ExecutionPlan:
    steps: List[PlanStep]

class PlannerAgent:
    """Basit planlayıcı: lint -> finish zinciri üretebilir."""
    def __init__(self, role: str = "codegen"):
        self.role = role

    def plan(self, **kwargs) -> ExecutionPlan:
        code = kwargs.get("code", "print('ok')\n")
        return ExecutionPlan(steps=[
            PlanStep(kind="tool", name="linter.ruff", args={"code": code}),
            PlanStep(kind="finish"),
        ])

    # Testlerin çağırdığı isimler:
    def plan_for_lint(self, code: str) -> ExecutionPlan:
        return ExecutionPlan(steps=[
            PlanStep(kind="tool", name="linter.ruff", args={"code": code}),
            PlanStep(kind="finish"),
        ])

    def build_plan(self, *args, **kwargs) -> ExecutionPlan:
        return self.plan(**kwargs)

    def react_plan(self, *args, **kwargs) -> ExecutionPlan:
        return self.plan(**kwargs)

    def from_spec(self, spec: str) -> ExecutionPlan:
        return self.plan(code=spec)