from __future__ import annotations
from collections import deque, defaultdict
from typing import Dict, List

class CycleError(Exception):
    pass

def topo_sort(graph: Dict[str, List[str]]) -> List[str]:
    indeg = defaultdict(int)
    for n, deps in graph.items():
        indeg.setdefault(n, 0)
        for d in deps:
            indeg[d] += 1
    q = deque([n for n, deg in indeg.items() if deg == 0])
    order = []
    while q:
        n = q.popleft()
        order.append(n)
        for m in graph.get(n, []):
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    if len(order) != len(indeg):
        raise CycleError("Cycle detected in DAG.")
    return order