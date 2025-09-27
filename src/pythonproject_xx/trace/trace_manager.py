from __future__ import annotations
import json, os
from datetime import datetime
from ..config.settings import get_settings

def log_event(kind: str, payload: dict) -> None:
    s = get_settings()
    os.makedirs(os.path.dirname(s.trace_path), exist_ok=True)
    rec = {"ts": datetime.utcnow().isoformat() + "Z", "kind": kind, **payload}
    with open(s.trace_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")