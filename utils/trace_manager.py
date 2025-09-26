import json
from datetime import datetime, timezone
from pathlib import Path

TRACE_FILE = Path("trace_log.jsonl")

def log_trace(agent_name, task_id, input_data, output_data, status="ok"):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "task_id": task_id,
        "input": input_data,
        "output": output_data,
        "status": status,
    }
    TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
