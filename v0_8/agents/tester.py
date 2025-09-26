from typing import Dict, Any
from utils.sandbox import SandboxRunner
TEST="from todo import add_task, list_tasks\n\nprint('OK' if list_tasks(add_task([], 'a'))==['a'] else 'FAIL')\n"
class TesterAgent:
    def __init__(self): self.sb=SandboxRunner(allow_run=True)
    async def run(self, task:Dict[str,Any], context:Dict[str,Any])->Dict[str,Any]:
        files=context.get('files') or {}
        for n,c in files.items():
            code,_,err=self.sb.syntax_check(n,c)
            if code!=0: return {'status':'error','passed':False,'stderr':err,'agent':'tester'}
        code,out,err=self.sb.run_python('t.py', TEST)
        return {'status':'ok' if code==0 and 'OK' in out else 'error','passed': code==0 and 'OK' in out,'stdout':out,'stderr':err,'agent':'tester'}
