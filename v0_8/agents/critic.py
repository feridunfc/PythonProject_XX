from typing import Dict, Any
from .base import BaseAgent
class CriticAgent(BaseAgent):
    async def run(self, task:Dict[str,Any], context:Dict[str,Any])->Dict[str,Any]:
        files=context.get('files') or {}
        ok=any('add_task' in v for v in files.values())
        return {'status':'ok','passed':ok,'agent':self.role}
