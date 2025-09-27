from __future__ import annotations
import json, os
from typing import Any

class JSONState:
    def __init__(self, path: str = "state.json") -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        if not os.path.exists(self.path):
            return {}
        return json.load(open(self.path, "r", encoding="utf-8"))

    def save(self, data: dict[str, Any]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)