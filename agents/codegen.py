from typing import Callable, Dict

class CodeGenAgent:
    def __init__(self, model: str, llm: Callable[[str,str,float], str] | None = None):
        self.model = model
        self.llm = llm

    def handle(self, context: Dict) -> Dict:
        algo = context.get("algorithm","")
        prompt = f"Generate Python code skeleton for the following algorithm:\n{algo}"
        code = self.llm(self.model, prompt) if self.llm else "# code"
        return {"code": code}