from typing import Callable, Dict

class DebuggerAgent:
    def __init__(self, model: str, llm: Callable[[str,str,float], str] | None = None):
        self.model = model
        self.llm = llm

    def handle(self, context: Dict) -> Dict:
        status = context.get("test_results","fail")
        if status == "ok":
            return {"fix_plan": "none"}
        code = context.get("code","")
        prompt = f"Tests failed. Suggest a minimal patch plan for this code:\n{code[:200]}"
        plan = self.llm(self.model, prompt) if self.llm else "apply minimal patch"
        return {"fix_plan": plan}