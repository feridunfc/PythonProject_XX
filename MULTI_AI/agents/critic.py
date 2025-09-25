from typing import Dict, Any
from agents.base import BaseAgent

class CriticAgent(BaseAgent):
    def __init__(self): super().__init__("critic")
    async def build_prompt(self, task: Dict[str, Any]) -> str:
        code = task.get("code","")
        return f"Şu kodu gözden geçir ve json formatta bulgular üret: issues:[{{severity,target,desc}}]\n---\n{code}"
