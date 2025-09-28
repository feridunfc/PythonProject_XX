import os
import importlib
import inspect
import types

ROLES = [
    "architect","algo_designer","codegen","tester",
    "debugger","critic","integrator","knowledge"
]

CLASSMAP = {
    "architect": "ArchitectAgent",
    "algo_designer": "AlgoDesignerAgent",
    "codegen": "CodeGenAgent",
    "tester": "TesterAgent",
    "debugger": "DebuggerAgent",
    "critic": "CriticAgent",
    "integrator": "IntegratorAgent",
    "knowledge": "KnowledgeAgent",
}

def setup_module(_m):
    os.environ.setdefault("MOCK_AI", "true")

def test_agent_contracts():
    for role in ROLES:
        mod = importlib.import_module(f"agents.{role}")
        cls_name = CLASSMAP[role]
        assert hasattr(mod, cls_name), f"{role}: class {cls_name} not found"
        AgentCls = getattr(mod, cls_name)
        ag = AgentCls(model="gpt-4o-mini", llm=lambda m,p,t=0.2: f"[MOCK:{m}] {p[:20]}")
        out = ag.handle({"spec":"X"})
        assert isinstance(out, dict), f"{role}: handle must return dict"
        assert len(out) >= 1, f"{role}: expected at least 1 key in output"