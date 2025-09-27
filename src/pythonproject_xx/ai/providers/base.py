from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Provider(ABC):
    name: str

    @abstractmethod
    def chat(self, model: str, messages: list[dict], temperature: float = 0.3) -> Dict[str, Any]:
        ...
