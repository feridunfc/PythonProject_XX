from pythonproject_xx.agents.planner_agent import ExecutionPlan, PlanStep
from pythonproject_xx.orchestrator.react_executor import ReactRunner

def test_rbac_forbids_file_patch_for_tester_role(tmp_path):
    # file.patch çağrısı tester rolü için yasak — alete ulaşmadan engellenir
    plan = ExecutionPlan(steps=[
        PlanStep(kind="tool", name="file.patch", args={"path": str(tmp_path/"x.py"), "content_new": "print(42)\n"})
    ])
    rr = ReactRunner(role="tester")
    out = rr.run(plan)
    assert out["ok"] is False and "forbidden_tool" in out["error"]

def test_sanity_check_stops_quickly(monkeypatch):
    # hızlı tetiklemek için N=1
    import os
    os.environ["SELF_CHECK_EVERY"] = "1"
    plan = ExecutionPlan(steps=[
        PlanStep(kind="tool", name="linter.ruff", args={"code": "x=1\n"}),
        PlanStep(kind="tool", name="linter.ruff", args={"code": "x=2\n"}),
    ])
    rr = ReactRunner(role="codegen")
    out = rr.run(plan)
    assert out["ok"] is True and out.get("stopped_by") == "sanity_check"