from typing import List, Dict, Any, Iterable
class TaskScheduler:
    def __init__(self, tasks: List[Dict[str, Any]]): self.tasks=tasks
    def topological(self)->Iterable[Dict[str,Any]]:
        pending={t['id']: set(t.get('deps',[])) for t in self.tasks}
        by_id={t['id']: t for t in self.tasks}; done=set()
        while pending:
            ready=[tid for tid,deps in pending.items() if deps.issubset(done)]
            if not ready:
                for tid in list(pending.keys()): yield by_id[tid]; return
            for tid in ready: yield by_id[tid]; done.add(tid); pending.pop(tid,None)
