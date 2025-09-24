
from collections import defaultdict, deque
from typing import Dict, List, Callable, Any
import asyncio

class DependencyCycleError(Exception):
    pass

def topological_order(tasks: List[Dict]) -> List[str]:
    graph = defaultdict(list)
    indeg = defaultdict(int)
    nodes = set()

    for t in tasks:
        tid = t["id"]
        nodes.add(tid)
        indeg.setdefault(tid, indeg.get(tid, 0))
        for d in t.get("dependencies", []):
            graph[d].append(tid)
            indeg[tid] += 1
            nodes.add(d)

    q = deque([n for n in nodes if indeg[n] == 0])
    out = []
    while q:
        n = q.popleft()
        out.append(n)
        for m in graph[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)

    if len(out) != len(nodes):
        raise DependencyCycleError("Cycle detected in task dependencies")
    return out

async def run_tasks_map(task_coros: Dict[str, Callable[[], Any]], tasks_meta: List[Dict], max_workers: int = 4) -> Dict[str, Any]:
    order = topological_order(tasks_meta)
    semaphore = asyncio.Semaphore(max_workers)
    results = {}

    # dependent failure policy (fail-fast): eğer bağımlılık fail ise skip
    deps = {t['id']: set(t.get('dependencies', [])) for t in tasks_meta}
    done_ok = set()
    failed = set()

    async def _run_one(tid):
        async with semaphore:
            # bağımlılık kontrolü
            if any(d in failed for d in deps[tid]):
                results[tid] = {"ok": False, "skipped": True, "reason": "dependency_failed"}
                return
            coro_func = task_coros.get(tid)
            if coro_func is None:
                results[tid] = {"error": "no_coroutine_registered"}
                failed.add(tid)
                return
            try:
                res = await coro_func()
                results[tid] = {"ok": True, "result": res}
                done_ok.add(tid)
            except Exception as e:
                results[tid] = {"ok": False, "error": str(e)}
                failed.add(tid)

    await asyncio.gather(*(_run_one(tid) for tid in order))
    return results
