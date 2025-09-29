from typing import Callable, Dict

class ArchitectAgent:
    def __init__(self, model: str, llm: Callable[[str,str,float], str] | None = None):
        self.model = model
        self.llm = llm

    def handle(self, context: Dict) -> Dict:
        spec = context.get("spec","")
        prompt = f"Design a high-level architecture for: {spec}"
        design = self.llm(self.model, prompt) if self.llm else f"Design for {spec}"
        return {"design": design}