import os
from .base_agent import AIAgent
from ..config.agent_config import AGENT_MODEL_MAP
from ..utils.ai_client import AIClient
from ..utils.file_utils import write_text, ensure_dir
# feridunfc_meta_ai/agents/codegen_agent.py
from ..utils.file_utils import write_text, ensure_dir  # bu kalsın
# Ör: feridunfc_meta_ai/agents/codegen_agent.py
from .base_agent import AIAgent



def ensure_dir(path: str): os.makedirs(path, exist_ok=True)

class CodeGenAgent(AIAgent):
    def __init__(self, client):
        super().__init__("codegen", client)
    async def process_task(self, task, context: dict) -> dict:
        workdir = context.get("workdir")
        prompt = f"""Write a clean, PEP8-compliant Python module implementing:
{task.description}

Return only code (no fences). The module will be saved as generated_module.py and imported by tests.
"""
        resp = await self.client.call_model("codegen", prompt=prompt)
        code = resp.content
        result = {"generated_code": code, "files_created": []}
        if workdir:
            path = os.path.join(workdir, "generated_module.py")
            write_text(path, code)
            result["files_created"].append(path)
        return result
