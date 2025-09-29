from typing import Callable, Dict

class AlgoDesignerAgent:
    def __init__(self, model: str, llm: Callable[[str,str,float], str] | None = None):
        self.model = model
        self.llm = llm

    def handle(self, context: Dict) -> Dict:
        base = context.get("design") or context.get("spec","")
        prompt = f"Propose an algorithmic approach based on this design:\n{base}"
        algorithm = self.llm(self.model, prompt) if self.llm else "Algorithm plan"
        return {"algorithm": algorithm}