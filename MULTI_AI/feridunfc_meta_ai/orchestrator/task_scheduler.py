import asyncio
from collections import defaultdict, deque
from typing import Dict, List, Set, Any

class TaskDAG:
    def __init__(self):
        self.graph = defaultdict(list)
        self.indeg = defaultdict(int)
        self.tasks: Dict[str, Any] = {}

    def add_task(self, task):
        tid = task.id
        if tid in self.tasks: return
        self.tasks[tid] = task
        self.indeg.setdefault(tid, 0)
        for dep in task.dependencies:
            self.graph[dep].append(tid)
            self.indeg[tid] += 1

    def order(self) -> List[str]:
        q = deque([t for t in self.tasks if self.indeg[t]==0])
        out = []
        indeg = dict(self.indeg)
        while q:
            n = q.popleft(); out.append(n)
            for m in self.graph[n]:
                indeg[m] -= 1
                if indeg[m] == 0: q.append(m)
        if len(out) != len(self.tasks):
            raise ValueError("Cycle detected in task dependencies")
        return out

class Scheduler:
    def __init__(self, agents: Dict[str, Any], concurrency: int = 2):
        self.agents = agents
        self.dag = TaskDAG()
        self.completed: Set[str] = set()
        self.failed: Set[str] = set()
        self.concurrency = concurrency

    def register_weeks(self, weeks):
        for w in weeks:
            for t in w.tasks:
                self.dag.add_task(t)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        order = self.dag.order()
        sem = asyncio.Semaphore(self.concurrency)
        results: Dict[str, Any] = {}

        async def run_one(tid: str):
            t = self.dag.tasks[tid]
            # wait deps
            while not all(d in self.completed for d in t.dependencies):
                await asyncio.sleep(0.05)
            agent = self.agents.get(t.agent_type)
            if not agent:
                t.status="failed"; self.failed.add(tid); results[tid]={"error":"no agent"}; return
            async with sem:
                try:
                    t.status = "in_progress"
                    r = await agent.process_task(t, context)
                    t.status = "completed"; t.result = r; self.completed.add(tid); results[tid]=r; context.update(r)
                except Exception as e:
                    t.status = "failed"; self.failed.add(tid); results[tid]={"error":str(e)}

        await asyncio.gather(*(run_one(tid) for tid in order))
        return results
