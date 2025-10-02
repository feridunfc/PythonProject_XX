from datetime import datetime
import json, os
TRACE_FILE = os.environ.get("TRACE_JSONL_PATH", "trace_log.jsonl")

def trace(stage: str, payload):
    rec = {"ts": datetime.utcnow().isoformat()+"Z", "stage": stage, "payload": payload}
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
