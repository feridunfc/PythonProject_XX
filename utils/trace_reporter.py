import json
from pathlib import Path

TRACE_FILE = Path("trace_log.jsonl")
HTML_FILE = Path("trace_report.html")

HTML_HEAD = """<!DOCTYPE html>
<html lang="tr"><head><meta charset="utf-8">
<title>Multi-AI Trace Report</title>
<style>
body { font-family: Arial, sans-serif; background: #f4f4f9; color: #333; padding: 20px; }
h1 { text-align: center; }
.entry { border: 1px solid #ccc; border-radius: 8px; padding: 10px; margin: 10px 0; background: #fff; }
.agent { font-weight: bold; color: #2c3e50; }
.status-ok { color: green; }
.status-error { color: red; }
.timestamp { font-size: 0.9em; color: #888; }
pre { background: #f0f0f0; padding: 10px; border-radius: 4px; overflow-x: auto; }
</style></head><body><h1>Multi-AI Trace Report</h1>
"""

HTML_FOOT = """</body></html>"""

def generate_html_report(trace_file: Path = TRACE_FILE, html_file: Path = HTML_FILE):
    if not trace_file.exists():
        raise FileNotFoundError(f"Trace file {trace_file} not found.")
    entries = []
    with open(trace_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            status_cls = "status-ok" if entry.get("status") == "ok" else "status-error"
            entries.append(f"""
<div class="entry">
  <div class="agent">{entry.get('agent','?')} <span class="{status_cls}">[{entry.get('status','').upper()}]</span></div>
  <div class="timestamp">{entry.get('timestamp','')}</div>
  <div><b>Task ID:</b> {entry.get('task_id','')}</div>
  <div><b>Input:</b><pre>{json.dumps(entry.get('input'), ensure_ascii=False, indent=2)}</pre></div>
  <div><b>Output:</b><pre>{json.dumps(entry.get('output'), ensure_ascii=False, indent=2)}</pre></div>
</div>
""")
    html = HTML_HEAD + "\n".join(entries) + HTML_FOOT
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Trace raporu üretildi: {html_file}")
