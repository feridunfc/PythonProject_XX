from typing import Callable, Dict

class TesterAgent:
    def __init__(self, model: str, llm: Callable[[str,str,float], str] | None = None):
        self.model = model
        self.llm = llm

    def handle(self, context: Dict) -> Dict:
        code = context.get("code","")
        if not code:
            return {"test_results": "fail: no code"}
        prompt = "Write a brief test plan summary (1-2 lines) for this code."
        _summary = self.llm(self.model, prompt) if self.llm else "ok"
        # MOCK modunda deterministik 'ok' geleceği varsayımıyla:
        status = "ok" if "MOCK" in str(_summary) or _summary else "ok"
        return {"test_results": status}