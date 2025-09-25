from ..config.agent_config import AGENT_MODEL_MAP
from .base_agent import AIAgent  # senin base sınıfın her neyse
from ..utils.ai_client import AIClient

class DebuggerAgent(AIAgent):
    def __init__(self, client: AIClient):
        # Güvenli erişim: haritada yoksa DeepSeek’e düş
        models = AGENT_MODEL_MAP.get("debugger", [("deepseek", "deepseek-chat")])
        super().__init__("Debugger", models[0])
        self.client = client

    async def process_task(self, task, context: dict) -> dict:
        return {"debug": "placeholder"}
