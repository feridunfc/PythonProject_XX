import sys
import json, re
from pydantic import BaseModel, Field, ValidationError
from typing import List

class Api(BaseModel):
    route: str
    method: str
    handler: str
    inputs: List[str]
    outputs: List[str]

class Task(BaseModel):
    id: str
    title: str
    owner: str
    deps: List[str] = []

class Plan(BaseModel):
    goal: str
    modules: List[dict]
    apis: List[Api]
    tasks: List[Task]
    observability: dict
    risks: List[str]
    acceptance: List[str]
    next_actions: List[str]

def _extract_json(text: str) -> str:
    # â€œyanlÄ±ÅŸlÄ±klaâ€ kod bloÄŸu/ek aÃ§Ä±klama gelirse JSONâ€™u Ã§ek
    m = re.search(r'\{(?:[^{}]|(?R))*\}', text, re.DOTALL)
    return m.group(0) if m else "{}"

# ... run_sprint iÃ§inde architect aÅŸamasÄ±nÄ± bul ve ÅŸu kalÄ±ba getir:
raw = self.ollama.call_model("architect", prompt, self.context)
content = raw.get("data") if isinstance(raw, dict) else raw
json_str = content if isinstance(content, str) else str(content)
json_str = _extract_json(json_str)

valid = False
for attempt in range(2):  # 1 retry
    try:
        plan_obj = Plan.model_validate_json(json_str)
        valid = True
        break
    except ValidationError:
        # yeniden yÃ¶nlendir: "YANLIÅ! SADECE ÅEMA'ya uygun JSON Ã¼ret."
        reprompt = (
            "Ã–NCEKÄ° Ã‡IKTI GEÃ‡ERSÄ°Z.\n"
            "Kurallar: SADECE ÅEMA'ya birebir uyan GEÃ‡ERLÄ° JSON dÃ¶ndÃ¼r; markdown/kod yok.\n"
            "ÅEMA: (yukarÄ±daki ile aynÄ±)"
        )
        raw = self.ollama.call_model("architect", reprompt, self.context)
        json_str = _extract_json(raw.get("data") if isinstance(raw, dict) else str(raw))

# trace
self.trace.log_execution({"stage":"architect","input":prompt[:500],"output":json_str,"success":valid})

print("\n>>> ARCHITECT AÅAMASI - Ã‡IKTI (JSON) <<<")
print(json_str if len(json_str) < 4000 else json_str[:4000]+" ...")

# hÄ±zlÄ± Ã¶zet
if valid:
    print("\n[Ã–ZET]")
    print("Hedef:", plan_obj.goal)
    print("API sayÄ±sÄ±:", len(plan_obj.apis), "â†’", ", ".join([a.route for a in plan_obj.apis[:5]]))
    print("GÃ¶rev sayÄ±sÄ±:", len(plan_obj.tasks))

ans = input("\nArchitect Ã§Ä±ktÄ±sÄ±nÄ± onaylÄ±yor musun? [y/N] ").strip().lower()
if ans != "y":
    print("âŒ Reddedildi."); return
self.context["architect"] = json_str  # sonraki aÅŸamalar iÃ§in

