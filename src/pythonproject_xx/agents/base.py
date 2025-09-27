from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    role: str
    model_spec: str

    def __init__(self, role: str, model_spec: str) -> None:
        self.role = role
        self.model_spec = model_spec

    @abstractmethod
    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        ...