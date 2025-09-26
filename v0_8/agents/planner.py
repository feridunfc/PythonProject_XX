from typing import Dict, Any
from .base import BaseAgent
class PlannerAgent(BaseAgent):
    async def run(self, task:Dict[str,Any], context:Dict[str,Any])->Dict[str,Any]:
        return {'status':'ok','plan':['1) model','2) api','3) test'],'agent':self.role}
