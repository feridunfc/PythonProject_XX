from pydantic import BaseModel
import json

class Brief(BaseModel):
    goal: str
    use_cases: list[str]
    constraints: list[str]
    acceptance_criteria: list[str]
    risks: list[str]
    open_questions: list[str]

RESEARCHER_SYSTEM = "Kıdemli keşif analistisiniz. Yalnızca geçerli JSON verin."

RESEARCHER_PROMPT = '''Proje hedefi: {goal}
Gereksinimler, kısıtlar, kabul kriterleri, riskler ve açık soruları çıkar.
FORMAT:
{{
  "goal": "...",
  "use_cases": ["..."],
  "constraints": ["..."],
  "acceptance_criteria": ["..."],
  "risks": ["..."],
  "open_questions": ["..."]
}}'''

def run_researcher(backend, goal: str) -> Brief:
    out = backend.generate("architect", RESEARCHER_SYSTEM, RESEARCHER_PROMPT.format(goal=goal))
    data = json.loads(out)
    return Brief(**data)
