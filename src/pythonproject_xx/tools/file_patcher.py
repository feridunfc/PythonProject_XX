import difflib, pathlib
from typing import Any, Dict
from .base import BaseTool

class FilePatcherTool(BaseTool):
    name = "file.patch"

    def run(self, path: str, content_new: str) -> Dict[str, Any]:
        p = pathlib.Path(path)
        old = p.read_text(encoding="utf-8") if p.exists() else ""
        p.write_text(content_new, encoding="utf-8")
        diff = "".join(difflib.unified_diff(old.splitlines(True), content_new.splitlines(True), fromfile="old", tofile="new"))
        return {"ok": True, "diff": diff}