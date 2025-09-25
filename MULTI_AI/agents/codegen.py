from typing import Dict, Any
from agents.base import BaseAgent

class CodegenAgent(BaseAgent):
    def __init__(self): super().__init__("codegen")
    async def build_prompt(self, task: Dict[str, Any]) -> str:
        ctx = task.get("context","")
        desc = task.get("description","")
        return f"Aşağıdaki bağlamı dikkate alarak KOD üret:\n---- CONTEXT ----\n{ctx}\n---- TASK ----\n{desc}\nSadece kod bloğu döndür."
