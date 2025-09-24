
import json, html
from pathlib import Path
from string import Template

TRACE_FILE = Path("trace_log.jsonl")
HTML_FILE = Path("trace_report.html")

_HTML = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
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
  </style>
</head>
<body>
  <h1>Multi-AI Trace Report</h1>
  $content
</body>
</html>
""")

def _entry_html(entry: dict) -> str:
    esc = lambda v: html.escape(json.dumps(v, ensure_ascii=False, indent=2)) if not isinstance(v, str) else html.escape(v)
    status_class = "status-ok" if entry.get("status") == "ok" else "status-error"
    return f"""
    <div class="entry">
      <div class="agent">{html.escape(str(entry.get('agent')))} 
        <span class="{status_class}">[{html.escape(str(entry.get('status','')).upper())}]</span>
      </div>
      <div class="timestamp">{html.escape(str(entry.get('timestamp','')))}</div>
      <div><b>Task ID:</b> {html.escape(str(entry.get('task_id','')))}</div>
      <div><b>Input:</b><pre>{esc(entry.get('input'))}</pre></div>
      <div><b>Output:</b><pre>{esc(entry.get('output'))}</pre></div>
    </div>
    """

def generate_html_report(trace_file: Path = TRACE_FILE, html_file: Path = HTML_FILE):
    if not trace_file.exists():
        raise FileNotFoundError(f"Trace file {trace_file} not found.")
    entries_html = []
    with open(trace_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            entries_html.append(_entry_html(entry))
    html_content = _HTML.substitute(content="\n".join(entries_html))
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Trace raporu üretildi: {html_file}")
