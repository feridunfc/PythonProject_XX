import pytest
from feridunfc_meta_ai.orchestrator.task_scheduler import topological_order, run_tasks_map

def test_topological_order():
    tasks = [
        {"id":"a","dependencies":[]},
        {"id":"b","dependencies":["a"]},
        {"id":"c","dependencies":["b"]},
    ]
    assert topological_order(tasks) == ["a","b","c"]

@pytest.mark.asyncio
async def test_run_tasks_map_success():
    called = []
    async def a(): called.append("a"); return "A"
    async def b(): called.append("b"); return "B"

    task_coros = {"a": a, "b": b}
    meta = [{"id":"a","dependencies":[]},{"id":"b","dependencies":["a"]}]
    res = await run_tasks_map(task_coros, meta, max_workers=2)
    assert res["a"]["ok"] and res["b"]["ok"]
    assert "a" in called and "b" in called

@pytest.mark.asyncio
async def test_run_tasks_map_fail_fast():
    async def a(): raise RuntimeError("boom")
    async def b(): return "B"

    task_coros = {"a": a, "b": b}
    meta = [{"id":"a","dependencies":[]},{"id":"b","dependencies":["a"]}]
    res = await run_tasks_map(task_coros, meta, max_workers=2)
    assert not res["a"]["ok"]
    assert res["b"].get("skipped") is True
