from typing import Dict, Any
from .base import BaseAgent
SAMPLE='def add_task(xs,item):\n    xs.append(item)\n    return xs\n\n' \
      'def list_tasks(xs):\n    return xs\n'
class CodeGenAgent(BaseAgent):
    async def run(self, task:Dict[str,Any], context:Dict[str,Any])->Dict[str,Any]:
        return {'status':'ok','files':{'todo.py':SAMPLE},'agent':self.role}
