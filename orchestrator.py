import os
import uuid
import importlib
from typing import Dict, List, Optional, Callable

from dotenv import load_dotenv
from obs import event as obs_event

# OpenAI 1.x client
try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

load_dotenv()

def _mock_enabled() -> bool:
    v = os.getenv("MOCK_AI", "true").strip().lower()
    return v in ("1","true","yes","on")

class Orchestrator:
    """
    Basit sıralı orkestratör.
    - agents/<role>.py içindeki sınıf adları ROLE_CLASS_MAP ile çözülür.
    - LLM çağrısı execute_with_model üzerinden yapılır; MOCK_AI varsa deterministik döner.
    - Obs: pipeline/agent/llm eventleri JSONL'e yazılabilir.
    """
    ROLE_CLASS_MAP: Dict[str, str] = {
        "architect":     "ArchitectAgent",
        "algo_designer": "AlgoDesignerAgent",
        "codegen":       "CodeGenAgent",
        "tester":        "TesterAgent",
        "debugger":      "DebuggerAgent",
        "critic":        "CriticAgent",
        "integrator":    "IntegratorAgent",
        "knowledge":     "KnowledgeAgent",
    }

    def __init__(self,
                 mapping: Optional[Dict[str, str]] = None,
                 sequence: Optional[List[str]] = None) -> None:
        self.mapping = mapping or {
            "architect":      "gpt-4o-mini",
            "algo_designer":  "gpt-4o-mini",
            "codegen":        "gpt-4o-mini",
            "tester":         "gpt-4o-mini",
            "debugger":       "gpt-4o-mini",
            "critic":         "gpt-4o-mini",
            "integrator":     "gpt-4o-mini",
            "knowledge":      "gpt-4o-mini",
        }
        self.sequence = sequence or list(self.ROLE_CLASS_MAP.keys())
        self.history: List[Dict] = []

        # OpenAI 1.x client (MOCK ise None, gerçek çağrı yapılmaz)
        self._client = None
        if not _mock_enabled() and OpenAI is not None:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                # OpenAI() zaten ortamdan anahtarı alır; eksplisit de geçebiliriz
                self._client = OpenAI()

    # LLM çağrısı: ajanlara callable olarak verilir
    def execute_with_model(self, model: str, prompt: str, temperature: float = 0.2) -> str:
        if _mock_enabled() or self._client is None:
            text = f"[MOCK:{model}] {prompt[:64]}"
            obs_event("llm.chat", {"model": model, "mock": True})
            return text

        # OpenAI 1.x
        resp = self._client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        out = resp.choices[0].message.content or ""
        obs_event("llm.chat", {"model": model, "mock": False})
        return out

    def run(self, spec: str) -> Dict:
        run_id = str(uuid.uuid4())[:8]
        ctx: Dict = {"spec": spec, "run_id": run_id}
        obs_event("pipeline.start", {"run_id": run_id, "spec": spec})

        for role in self.sequence:
            model = self.mapping.get(role, "gpt-4o-mini")
            try:
                mod = importlib.import_module(f"agents.{role}")
                cls_name = self.ROLE_CLASS_MAP[role]
                AgentCls = getattr(mod, cls_name)
                agent = AgentCls(model=model, llm=self.execute_with_model)
                obs_event("agent.start", {"role": role, "model": model})

                output = agent.handle(ctx) or {}
                self.history.append({"role": role, "output": output})
                ctx.update(output)

                obs_event("agent.done", {"role": role, "keys": list(output.keys())})
            except Exception as e:  # pragma: no cover (negatif akış)
                obs_event("agent.error", {"role": role, "error": str(e)})
                break

        obs_event("pipeline.done", {"run_id": run_id, "ctx_keys": list(ctx.keys())})
        return ctx


if __name__ == "__main__":
    orch = Orchestrator()
    result = orch.run("Implement quicksort")
    print(result)