import json, subprocess, tempfile, pathlib
from typing import Any, Dict
from .base import BaseTool

class LinterTool(BaseTool):
    name = "linter.ruff"

    def run(self, code: str) -> Dict[str, Any]:
        with tempfile.TemporaryDirectory() as td:
            p = pathlib.Path(td, "snippet.py"); p.write_text(code, encoding="utf-8")
            cp = subprocess.run(["python","-m","ruff","check",str(p),"-f","json"], capture_output=True, text=True)
            issues = json.loads(cp.stdout or "[]")
            return {"ok": cp.returncode == 0, "issues": issues}