
import json
from pathlib import Path
from typing import Any, Dict

class StateManager:
    def __init__(self, path: str = ".meta_state.json"):
        self.path = Path(path)

    def save(self, data: Dict[str, Any]):
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
