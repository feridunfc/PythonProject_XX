from pathlib import Path
from typing import Dict, Any

class FilePatcherTool:
    """Basit dosya yazma/patch ekleme aracı (güvenli stub)."""
    def run(self, path: str, content_new: str | None = None, patch: str | None = None) -> Dict[str, Any]:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if content_new is not None:
            p.write_text(content_new, encoding="utf-8")
            return {"ok": True, "path": str(p), "mode": "write"}
        if patch is not None:
            with p.open("a", encoding="utf-8") as f:
                f.write(patch)
            return {"ok": True, "path": str(p), "mode": "append-patch"}
        return {"ok": False, "error": "no_input"}