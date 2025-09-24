

# feridunfc_meta_ai/agents/architect_agent.py
import re
from .base_agent import AIAgent

class ArchitectAgent(AIAgent):
    def __init__(self, client):
        super().__init__("architect", client)

    async def process_task(self, task, context: dict) -> dict:
        req = context.get("requirements", task.description)
        agent_types = ",".join(context.get("agent_types", ["architect", "codegen", "tester", "critic"]))
        prompt = f"""Return ONLY a single valid JSON (no markdown, no prose).
Keys: title, goal, weeks:[{{week_number,start_date,end_date,tasks:[{{title,description,agent_type,estimated_hours,dependencies}}]}}]
Constraints: agent_type in [{agent_types}]. Use realistic estimates. Dependencies reference task titles.
Requirement:
{req}
"""
        resp = await self.client.call_model("architect", prompt=prompt, system="You output only JSON.")
        txt = resp.content.strip()
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", txt, flags=re.IGNORECASE)
        if m:
            txt = m.group(1).strip()
        else:
            # JSON parantez dengele fallback'i
            m2 = re.search(r"[\{\[]", txt)
            if m2:
                i = m2.start()
                stack, end = [], None
                for j, ch in enumerate(txt[i:], i):
                    if ch in "{[": stack.append(ch)
                    elif ch in "}]":
                        if not stack: continue
                        top = stack.pop()
                        if (top == "{" and ch != "}") or (top == "[" and ch != "]"): continue
                        if not stack:
                            end = j + 1
                            break
                if end:
                    txt = txt[i:end].strip()
        return {"sprint_plan_json": txt}



    @staticmethod
    def _extract_json_like(s: str) -> str:
        """
        LLM çıktısından geçerli JSON gövdesini çıkarır.
        - ```json ... ``` veya ``` ... ``` çitlerini soyar
        - Yoksa ilk { veya [ konumundan itibaren parantez dengeleme yapar
        """
        s = (s or "").strip()

        # 1) ```json ... ``` veya ``` ... ``` çitleri
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()

        # 2) Parantez dengeleme
        m2 = re.search(r"[\{\[]", s)
        if not m2:
            return s  # JSON benzeri bulamadık; olduğu gibi dön

        i = m2.start()
        stack = []
        for j, ch in enumerate(s[i:], i):
            if ch in "{[":
                stack.append(ch)
            elif ch in "}]":
                if not stack:
                    continue
                top = stack.pop()
                if (top == "{" and ch != "}") or (top == "[" and ch != "]"):
                    continue
                if not stack:
                    return s[i:j + 1].strip()

        return s  # dengeleme tutmazsa orijinali dön

    async def process_task(self, task, context: dict) -> dict:
        req = context.get("requirements", task.description)
        agent_types = ",".join(
            context.get(
                "agent_types",
                ["architect", "codegen", "tester", "critic", "debugger", "integrator"],
            )
        )

        prompt = f"""Return ONLY a single valid JSON (no markdown, no prose). Keys: title, goal, weeks:[{{number,start_date,end_date,tasks:[{{title,description,agent_type,estimated_hours,dependencies}}]}}]
Constraints: agent_type in [{agent_types}]. Use realistic estimates. Dependencies reference task titles.
Requirement:
{req}
"""

        resp = await self.client.call_model(
            "architect", prompt=prompt, system="You output only JSON."
        )
        txt = self._extract_json_like(resp.content)
        return {"sprint_plan_json": txt}
