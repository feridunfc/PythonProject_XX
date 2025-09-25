# feridunfc_meta_ai/orchestrator/sprint_orchestrator.py
from __future__ import annotations

from typing import Optional, Dict, Any
import json
import logging
import re
import ast
from pydantic import ValidationError
import uuid

from ..utils.ai_client import AIClient
from ..models.sprint import Sprint, Task
from ..agents.architect_agent import ArchitectAgent
from ..agents.codegen_agent import CodeGenAgent
from ..agents.tester_agent import TesterAgent
from ..agents.critic_agent import CriticAgent
from ..agents.debugger_agent import DebuggerAgent
from ..agents.integrator_agent import IntegratorAgent

logger = logging.getLogger(__name__)

# ----------------------- JSON Yardımcıları -----------------------
# --- sprint_orchestrator.py içinde, yardımcıların yanına ekle/değiştir ---

# --- ÜST KISIMDA: import'ların hemen altı ---

import re, json, logging, ast
logger = logging.getLogger(__name__)

_SINGLE_QUOTED_STR = re.compile(r"(?<!\\)'([^'\\]*(?:\\.[^'\\]*)*)'")

# dosyanın üstlerine (helperların yanına) ekleyin
_INCOMPLETE_TAIL_PATTERNS = [
    r',\s*"(?:[^"\\]|\\.)*$',                         #  , "key
    r',\s*"(?:[^"\\]|\\.)*"\s*:\s*$',                 #  , "key":
    r',\s*"(?:[^"\\]|\\.)*"\s*:\s*"(?:[^"\\]|\\.)*$', #  , "key":"value
    r',\s*$',                                         #  sonda tek başına virgül
]

def _strip_incomplete_trailing_bits(s: str) -> str:
    if not s:
        return s
    changed = True
    while changed:
        changed = False
        for pat in _INCOMPLETE_TAIL_PATTERNS:
            new = re.sub(pat, '', s)
            if new != s:
                s = new
                changed = True
    return s


def _remove_lonely_quotes(s: str) -> str:
    # Sadece çift tırnakdan oluşan satırları temizle
    return re.sub(r'^\s*"\s*$', '', s, flags=re.MULTILINE)

def _escape_newlines_in_json_strings(s: str) -> str:
    if not s:
        return s
    out = []
    in_str = False
    escape = False
    i = 0
    while i < len(s):
        ch = s[i]
        if in_str:
            if escape:
                out.append(ch); escape = False
            else:
                if ch == '\\':
                    out.append(ch); escape = True
                elif ch == '"':
                    out.append(ch); in_str = False
                elif ch in ('\r', '\n'):
                    # string içi ham satırsonlarını kaçır
                    if ch == '\r' and i + 1 < len(s) and s[i+1] == '\n':
                        i += 1
                    out.append('\\n')
                else:
                    out.append(ch)
        else:
            if ch == '"':
                in_str = True
            out.append(ch)
        i += 1
    return ''.join(out)

def _balance_and_close_json(s: str) -> str:
    if not s:
        return s

    s = s.replace("\u00A0", " ").replace("\u200B", "")
    s = _remove_lonely_quotes(s)

    res = []
    stack = []  # beklenen kapanışlar
    in_str = False
    escape = False

    for ch in s:
        if in_str:
            res.append(ch)
            if escape:
                escape = False
            else:
                if ch == '\\':
                    escape = True
                elif ch == '"':
                    in_str = False
            continue

        if ch == '"':
            in_str = True
            res.append(ch)
        elif ch == '{':
            stack.append('}')
            res.append(ch)
        elif ch == '[':
            stack.append(']')
            res.append(ch)
        elif ch in '}]':
            # eşleşiyorsa tepeyi indir
            if stack and stack[-1] == ch:
                stack.pop()
            res.append(ch)
        else:
            res.append(ch)

    if in_str:
        res.append('"')

    out = ''.join(res)
    out = _strip_incomplete_trailing_bits(out)              # <<< yeni: sondaki yarım property'yi kes
    out = re.sub(r',(\s*[}\]])', r'\1', out)                # kapanıştan önceki virgül

    # eksik kapanışları LIFO ile ekle (DOĞRU SIRA)
    while stack:
        out = re.sub(r',\s*$', '', out)                     # eklemeden hemen önce trailing virgül varsa temizle
        out += stack.pop()

    out = re.sub(r',(\s*[}\]])', r'\1', out)                # bir tur daha süpür
    return out


def _extract_json_like(s: str) -> str:
    s = (s or "").strip()
    s = s.replace("\u00A0", " ").replace("\u200B", "")
    s = re.sub(r"^\s*```(?:json)?\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*```$", "", s)

    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s, re.IGNORECASE)
    if m:
        s = m.group(1).strip()

    m2 = re.search(r"[\{\[]", s)
    if m2:
        s = s[m2.start():]

    s = _remove_lonely_quotes(s)
    s = _escape_newlines_in_json_strings(s)
    s = _strip_incomplete_trailing_bits(s)   # <<< yeni
    s = _balance_and_close_json(s)
    s = _strip_incomplete_trailing_bits(s)   # <<< yeni (son temizlik)
    return s



def _repair_json(s: str) -> str:
    if not s:
        return s
    s = (s.replace("“", "\"").replace("”", "\"").replace("„", "\"")
           .replace("’", "'"))
    s = re.sub(r"//.*?$", "", s, flags=re.MULTILINE)
    s = re.sub(r"/\*[\s\S]*?\*/", "", s)
    s = re.sub(r",(\s*[}\]])", r"\1", s)

    def _sq_to_dq(m):
        inner = m.group(1).replace('"', '\\"')
        return f"\"{inner}\""
    s = _SINGLE_QUOTED_STR.sub(_sq_to_dq, s)

    s = re.sub(r'([{\[,]\s*)([A-Za-z_][A-Za-z0-9_\-]*)(\s*):', r'\1"\2"\3:', s)

    s = _remove_lonely_quotes(s)
    s = _escape_newlines_in_json_strings(s)
    s = _strip_incomplete_trailing_bits(s)   # <<< yeni
    s = _balance_and_close_json(s)
    s = _strip_incomplete_trailing_bits(s)   # <<< yeni
    return s.strip()


def _loads_lenient(s: str):
    s = re.sub(r"```(?:json)?\s*", "", (s or ""), flags=re.IGNORECASE).replace("```", "").strip()
    s = _remove_lonely_quotes(s)
    s = _escape_newlines_in_json_strings(s)
    s = _strip_incomplete_trailing_bits(s)   # <<< yeni
    s = _balance_and_close_json(s)
    s = _strip_incomplete_trailing_bits(s)   # <<< yeni

    try:
        return json.loads(s)
    except Exception:
        pass

    fixed = _repair_json(s)
    try:
        return json.loads(fixed)
    except Exception:
        pass

    py_like = (fixed
               .replace(": true", ": True")
               .replace(": false", ": False")
               .replace(": null", ": None"))
    try:
        obj = ast.literal_eval(py_like)
        return json.loads(json.dumps(obj))
    except Exception:
        last_try = fixed.replace("```json", "").replace("```", "").strip()
        last_try = _remove_lonely_quotes(last_try)
        last_try = _escape_newlines_in_json_strings(last_try)
        last_try = _strip_incomplete_trailing_bits(last_try)  # <<< yeni
        last_try = _balance_and_close_json(last_try)
        last_try = _strip_incomplete_trailing_bits(last_try)  # <<< yeni
        return json.loads(last_try)



# def _loads_lenient(s: str):
#     # 1) Direkt JSON
#     try:
#         return json.loads(s)
#     except Exception:
#         pass
#
#     # 2) Onarıp tekrar dene
#     fixed = _repair_json(s)
#     try:
#         return json.loads(fixed)
#     except Exception:
#         pass
#
#     # 3) Python literal'a çevirip geri JSON'la
#     py_like = (fixed
#                .replace(": true", ": True")
#                .replace(": false", ": False")
#                .replace(": null", ": None"))
#     try:
#         obj = ast.literal_eval(py_like)
#         return json.loads(json.dumps(obj))
#     except Exception:
#         # 4) Son bir süpürme: olası kalan çitleri kaldır
#         last_try = fixed.replace("```json", "").replace("```", "").strip()
#         return json.loads(last_try)


def _normalize_sprint_schema(data: dict) -> dict:
    """
    LLM çıktısını Sprint Pydantic şemasına uydurur:
    - weeks[].number => weeks[].week_number
    - eşanlamlılar: start/startDate, end/endDate, name/title, desc/description, estimate/hours/estimated_hours
    - üst seviye: sprint_title/sprint_goal => title/goal
    """
    if not isinstance(data, dict):
        return data

    out = {
        "title": data.get("title") or data.get("sprint_title") or "Sprint",
        "goal": data.get("goal") or data.get("sprint_goal") or "",
    }

    weeks = data.get("weeks") or data.get("week_plan") or []
    norm_weeks = []

    for w in weeks if isinstance(weeks, list) else []:
        if not isinstance(w, dict):
            continue

        wn = (w.get("week_number") or
              w.get("number") or
              w.get("week") or
              w.get("index"))

        start_date = w.get("start_date") or w.get("start") or w.get("startDate") or ""
        end_date   = w.get("end_date")   or w.get("end")   or w.get("endDate")   or ""

        tasks = w.get("tasks") or []
        norm_tasks = []
        for t in tasks if isinstance(tasks, list) else []:
            if not isinstance(t, dict):
                continue
            title = t.get("title") or t.get("name") or "Task"
            description = t.get("description") or t.get("desc") or ""
            agent_type = t.get("agent_type") or t.get("agent") or "codegen"
            est = (t.get("estimated_hours", None) if "estimated_hours" in t
                   else t.get("estimate", None) if "estimate" in t
                   else t.get("hours", None))
            try:
                estimated_hours = float(est) if est is not None else 0.0
            except Exception:
                estimated_hours = 0.0
            deps = t.get("dependencies") or t.get("deps") or []
            if isinstance(deps, str):
                sep = ";" if ";" in deps else "," if "," in deps else None
                deps = [d.strip() for d in deps.split(sep)] if sep else ([deps.strip()] if deps.strip() else [])
            elif not isinstance(deps, list):
                deps = []

            # benzersiz ve string ID üret
            tid = (t.get("task_id") or t.get("id")
                   or f"w{len(norm_weeks) + 1}-t{len(norm_tasks) + 1}-{uuid.uuid4().hex[:8]}")

            norm_tasks.append({
                "task_id": str(tid),
                "title": title,
                "description": description,
                "agent_type": agent_type,
                "estimated_hours": estimated_hours,
                "dependencies": deps,
            })

        try:
            week_number = int(wn) if wn is not None else len(norm_weeks) + 1
        except Exception:
            week_number = len(norm_weeks) + 1

        norm_weeks.append({
            "week_number": week_number,
            "start_date": start_date,
            "end_date": end_date,
            "tasks": norm_tasks,
        })

    out["weeks"] = norm_weeks
    return out

# ----------------------- Orchestrator -----------------------
class SprintOrchestrator:
    def __init__(self, concurrency: int = 2):
        self.client = AIClient()
        self.agents: Dict[str, Any] = {}
        self.active_sprint: Optional[Sprint] = None
        self.context_base: Dict[str, Any] = {}
        self.concurrency = concurrency

    async def initialize(
        self,
        workdir: Optional[str] = None,
        *,
        no_sandbox: bool = False,
        skip_tests: bool = False,
    ):
        """Ajanları hazırla ve çalışma bağlamını (context) ayarla."""
        self.agents = {
            "architect":   ArchitectAgent(self.client),
            "codegen":     CodeGenAgent(self.client),
            "tester":      TesterAgent(self.client),
            "critic":      CriticAgent(self.client),
            "debugger":    DebuggerAgent(self.client),
            "integrator":  IntegratorAgent(self.client),
        }
        if workdir:
            self.context_base["workdir"] = workdir
        self.context_base["no_sandbox"] = no_sandbox
        self.context_base["skip_tests"] = skip_tests

        logger.debug(
            "Orchestrator initialized (workdir=%s, no_sandbox=%s, skip_tests=%s)",
            workdir, no_sandbox, skip_tests
        )

    async def aclose(self):
        await self.client.aclose()

    async def plan_sprint_from_requirements(self, requirements: str) -> Sprint:
        """Architect ile JSON plan üret, normalize et, Pydantic ile doğrula ve aktif sprinte ata."""
        arch: ArchitectAgent = self.agents["architect"]
        context = {
            **self.context_base,
            "requirements": requirements,
            "agent_types": list(self.agents.keys()),
        }

        resp = await arch.process_task(
            Task(title="Plan", description="JSON plan"), context
        )

        raw = (resp or {}).get("sprint_plan_json", "") or ""
        if not raw:
            raise RuntimeError("ArchitectAgent boş plan döndürdü.")

        san = _extract_json_like(raw)
        try:
            data = _loads_lenient(san)
        except Exception:
            logger.exception("Plan JSON onarımı başarısız. Ham metin (ilk 400):\n%s", san[:400])
            raise

        data = _normalize_sprint_schema(data)
        sprint = Sprint.model_validate(data)
        self.active_sprint = sprint
        return sprint

    async def execute_sprint(self, max_retries: int = 1) -> Dict[str, Any]:
        """(Plan-only senaryosunda yürütme atlanabilir) — burada sadece iskelet."""
        if not self.active_sprint:
            raise RuntimeError("Aktif sprint yok.")
        ctx = dict(self.context_base)
        # Burada gerçek yürütme yer alacak; şimdilik stub:
        return {"ok": True, "executed": False, "context": ctx}

    def get_sprint_report(self) -> Dict[str, Any]:
        if not self.active_sprint:
            raise RuntimeError("Aktif sprint yok.")
        s = self.active_sprint
        return {
            "sprint_id": s.id,
            "title": s.title,
            "total_tasks": s.get_total_tasks(),
            "completed_tasks": s.get_completed_tasks(),
        }
