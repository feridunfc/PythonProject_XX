from pythonproject_xx.agents.planner_agent import PlannerAgent
from pythonproject_xx.orchestrator.adaptive_executor import run_plan

def test_planner_lint_flow():
    plan = PlannerAgent().plan_for_lint("x=1+1\n")
    out = run_plan(plan)
    assert out["ok"] is True
    assert "result" in out