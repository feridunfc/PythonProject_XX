from ..config.agent_config import AGENT_MODEL_MAP
from ..utils.ai_client import AIClient
from .base_agent import AIAgent  # mevcut taban sınıfın ne ise onu import et

class IntegratorAgent(AIAgent):
    def __init__(self, client: AIClient):
        # Güvenli: yoksa mock'a düş
        prov_model_pair = (AGENT_MODEL_MAP.get("integrator") or [("mock", "mock")])[0]
        super().__init__("Integrator", prov_model_pair)
        self.client = client
