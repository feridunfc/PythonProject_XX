Patch: Trace Reporting Fix
--------------------------
Files:
  - feridunfc_meta_ai/utils/trace_reporter.py  (fixed: no KeyError from CSS braces; HTML-escaped content)
  - feridunfc_meta_ai/utils/trace_manager.py   (UTC timestamps; simple JSONL logger)

Install:
  1) Unzip to your repo root, allowing overwrite.
  2) Ensure a trace_log.jsonl exists (created automatically by log_trace or generate a demo as below).

Quick demo (PowerShell):
  python -c "from feridunfc_meta_ai.utils.trace_manager import log_trace;     log_trace('ArchitectAgent','demo',{'req':'Basit TODO API'},{'design':'service+repo'});     log_trace('CodegenAgent','demo',{'design':'service+repo'},{'code':'print(42)'});     log_trace('TesterAgent','demo',{'code':'print(42)'},{'result':'pass'})"

  python -c "from feridunfc_meta_ai.utils.trace_reporter import generate_html_report as g; g()"
  start .\trace_report.html

Custom paths:
  python -c "from feridunfc_meta_ai.utils.trace_reporter import generate_html_report as g;     from pathlib import Path; g(Path(r'.\MULTI_AI\trace_log.jsonl'), Path('trace_report.html'))"