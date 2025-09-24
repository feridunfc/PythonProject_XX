# feridunfc_meta_ai/orchestrator/registry.py
from __future__ import annotations
import uuid
from typing import Dict, Any

class SprintRegistry:
    def __init__(self) -> None:
        self._sprints: Dict[str, Any] = {}

    def add(self, sprint: Any) -> str:
        sid = str(getattr(sprint, "id", "") or uuid.uuid4())
        setattr(sprint, "id", sid)
        self._sprints[sid] = sprint
        return sid

    def get(self, sid: str) -> Any | None:
        return self._sprints.get(sid)

    def all_ids(self):
        return list(self._sprints.keys())
