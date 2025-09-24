from typing import Dict, Any
from agents.base import BaseAgent

class TesterAgent(BaseAgent):
    def __init__(self): super().__init__("tester")
    async def build_prompt(self, task: Dict[str, Any]) -> str:
        spec = task.get("spec","")
        return f"Şu spesifikasyon için pytest test iskeleti yaz ve sadece kod döndür:\n{spec}"
