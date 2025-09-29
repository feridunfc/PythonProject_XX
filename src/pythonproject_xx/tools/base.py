from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    name: str

    @abstractmethod
    def run(self, **kwargs: Any) -> Dict[str, Any]:
        ...