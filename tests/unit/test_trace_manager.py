import os, json, tempfile
from pythonproject_xx.trace.trace_manager import log_event
from pythonproject_xx.config.settings import Settings

def test_trace_jsonl(tmp_path, monkeypatch):
    path = tmp_path / "trace.jsonl"
    # settings override
    monkeypatch.setenv("TRACE_PATH", str(path))
    log_event("test", {"x": 1})
    s = path.read_text(encoding="utf-8").strip()
    assert s
    obj = json.loads(s)
    assert obj["kind"] == "test"
    assert obj["x"] == 1