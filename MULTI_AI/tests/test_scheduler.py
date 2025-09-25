import pytest, anyio
from feridunfc_meta_ai.orchestrator.sprint_orchestrator import SprintOrchestrator

@pytest.mark.anyio
async def test_plan_and_execute_minimal():
    orch = SprintOrchestrator(concurrency=2)
    await orch.initialize(workdir="./work_t")
    s = await orch.plan_sprint_from_requirements("Mini API: add and list items")
    assert s.get_total_tasks() > 0
    res = await orch.execute_sprint(max_retries=1)
    rep = orch.get_sprint_report()
    assert rep["total_tasks"] >= rep["completed_tasks"]
    await orch.aclose()
