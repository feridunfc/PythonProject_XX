import os, subprocess
from .base_agent import AIAgent
from ..config.agent_config import AGENT_MODEL_MAP
from ..utils.ai_client import AIClient

def run(args, cwd):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, "", str(e)

class IntegratorAgent(AIAgent):
    def __init__(self, client: AIClient):
        super().__init__("Integrator", AGENT_MODEL_MAP["integrator"][0]); self.client = client
    async def process_task(self, task, context: dict) -> dict:
        repo = context.get("workdir", ".")
        rc, _, _ = run(["git", "rev-parse", "--is-inside-work-tree"], repo)
        if rc != 0: return {"ci": "not a git repo"}
        run(["git", "checkout", "-b", "feature/meta-ai"], repo)
        run(["git", "add", "-A"], repo)
        rc, out, err = run(["git", "commit", "-m", "meta-ai automated update"], repo)
        return {"ci": "commit", "returncode": rc, "stdout": out[-1000:], "stderr": err[-1000:]}
