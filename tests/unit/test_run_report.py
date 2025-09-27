import json
from pythonproject_xx.reporting.run_report import aggregate_trace, make_markdown, build_report_md

def test_aggregate_and_md(tmp_path):
    p = tmp_path / "trace.jsonl"
    lines = [
        {"ts":"2025-01-01T00:00:00Z","kind":"test","x":1},
        {"ts":"2025-01-01T00:01:00Z","kind":"ai_call","m":"ok"},
        {"ts":"2025-01-01T00:02:00Z","kind":"ai_call","m":"ok"},
    ]
    p.write_text("\n".join(json.dumps(x) for x in lines), encoding="utf-8")
    summary = aggregate_trace(p)
    assert summary["total"] == 3
    assert summary["by_kind"]["ai_call"] == 2
    md = make_markdown(summary)
    assert "Toplam kayıt: **3**" in md
    md2 = build_report_md(p)
    assert "# Run Report" in md2