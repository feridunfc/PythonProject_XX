from typing import Dict, Any
from agents.base import BaseAgent

class ArchitectAgent(BaseAgent):
    def __init__(self): super().__init__("architect")
    async def build_prompt(self, task: Dict[str, Any]) -> str:
        req = task.get("requirements","")
        return f"Verilen gereksinimlerden JSON sprint planı üret:\n{req}\nYalnızca JSON döndür."
