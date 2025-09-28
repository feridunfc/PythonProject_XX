import json, os, time

def event(name: str, payload: dict | None = None) -> None:
    """Minimal obs: OBS_BACKENDS='jsonl' ise TRACE_JSONL_PATH'e yaz."""
    backends = (os.getenv("OBS_BACKENDS") or "").lower()
    if "jsonl" not in backends:
        return
    path = os.getenv("TRACE_JSONL_PATH") or "trace_log.jsonl"
    rec = {
        "ts": time.time(),
        "service": os.getenv("TRACE_SERVICE_NAME") or "pythonproject_xx",
        "event": name,
        "payload": payload or {}
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")