from pathlib import Path
from typing import Dict, Any
import difflib

class FilePatcherTool:
    """Basit dosya yazma/patch aracı; her zaman 'diff' döndürür."""
    def run(self, path: str, content_new: str | None = None, patch: str | None = None) -> Dict[str, Any]:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        old = p.read_text(encoding="utf-8") if p.exists() else ""

        if content_new is not None:
            diff = "\n".join(difflib.unified_diff(
                old.splitlines(), content_new.splitlines(),
                fromfile=str(p), tofile=str(p), lineterm=""
            ))
            p.write_text(content_new, encoding="utf-8")
            return {"ok": True, "path": str(p), "mode": "write", "diff": diff}

        if patch is not None:
            with p.open("a", encoding="utf-8") as f:
                f.write(patch)
            return {"ok": True, "path": str(p), "mode": "append-patch", "diff": patch}

        return {"ok": False, "error": "no_input", "diff": ""}