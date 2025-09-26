import logging
from typing import Dict, Any
from utils.ai_client import AIClient, pick_provider, DEFAULT_MODEL
log=logging.getLogger('agent.base')
class BaseAgent:
    def __init__(self, role, model=None, provider=None):
        self.role=role; self.provider=provider or pick_provider(); self.model=model or DEFAULT_MODEL; self.client=AIClient()
        log.info('Agent init -> role=%s provider=%s model=%s', role, self.provider, self.model)
    async def run(self, task:Dict[str,Any], context:Dict[str,Any])->Dict[str,Any]:
        return {'status':'ok','agent':self.role}
