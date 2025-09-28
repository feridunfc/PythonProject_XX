from typing import Callable, Dict

class CriticAgent:
    def __init__(self, model: str, llm: Callable[[str,str,float], str] | None = None):
        self.model = model
        self.llm = llm

    def handle(self, context: Dict) -> Dict:
        prompt = "Provide a brief review summary for the solution."
        review = self.llm(self.model, prompt) if self.llm else "looks reasonable"
        return {"review": review}