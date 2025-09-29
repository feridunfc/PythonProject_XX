import os
import importlib

def setup_module(_m):
    os.environ.setdefault("MOCK_AI", "true")
    os.environ.setdefault("OBS_BACKENDS", "jsonl")
    os.environ.setdefault("TRACE_JSONL_PATH", "trace_log.jsonl")

def test_pipeline_smoke():
    from orchestrator import Orchestrator
    orch = Orchestrator()
    ctx = orch.run("Implement quicksort")
    # temel anahtarlar akışta üretildi mi?
    for k in ["design","algorithm","code","test_results","review","integration_notes","kb_refs"]:
        assert k in ctx, f"missing key: {k}"
    assert ctx["test_results"] in ("ok","fail"), "unexpected test result"

def test_execute_with_model_mock():
    from orchestrator import Orchestrator
    orch = Orchestrator()
    out = orch.execute_with_model("gpt-4o-mini", "hello")
    assert "[MOCK:gpt-4o-mini]" in out