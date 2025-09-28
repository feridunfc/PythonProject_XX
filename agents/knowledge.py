from typing import Callable, Dict, List

class KnowledgeAgent:
    def __init__(self, model: str, llm: Callable[[str,str,float], str] | None = None):
        self.model = model
        self.llm = llm

    def handle(self, context: Dict) -> Dict:
        # Gelecekte KB/RAG eklenebilir
        return {"kb_refs": []}