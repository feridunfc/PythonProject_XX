from __future__ import annotations
import json, pathlib
from collections import Counter
from typing import Iterable, Dict, Any

def aggregate_trace(path: str | pathlib.Path) -> Dict[str, Any]:
    p = pathlib.Path(path)
    counts = Counter()
    first_ts = last_ts = None
    total = 0
    if not p.exists():
        return {"total": 0, "by_kind": {}, "first_ts": None, "last_ts": None}

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            total += 1
            k = obj.get("kind", "unknown")
            counts[k] += 1
            ts = obj.get("ts")
            first_ts = first_ts or ts
            last_ts = ts

    return {"total": total, "by_kind": dict(counts), "first_ts": first_ts, "last_ts": last_ts}

def make_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Run Report", ""]
    lines.append(f"Toplam kayıt: **{summary.get('total', 0)}**")
    lines.append(f"İlk kayıt: `{summary.get('first_ts')}`  |  Son kayıt: `{summary.get('last_ts')}`")
    lines.append("")
    lines.append("## Türlere göre")
    for k, v in sorted(summary.get("by_kind", {}).items()):
        lines.append(f"- **{k}**: {v}")
    return "\n".join(lines)

def build_report_md(trace_path: str | pathlib.Path) -> str:
    return make_markdown(aggregate_trace(trace_path))