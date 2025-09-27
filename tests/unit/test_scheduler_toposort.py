from pythonproject_xx.orchestrator.scheduler import topo_sort, CycleError

def test_toposort_simple():
    g = {"A": ["B", "C"], "B": [], "C": []}
    order = topo_sort(g)
    assert set(order) == {"A","B","C"}
    assert order.index("B") < order.index("A")
    assert order.index("C") < order.index("A")

def test_toposort_cycle():
    g = {"A": ["B"], "B": ["A"]}
    try:
        topo_sort(g)
        assert False, "CycleError expected"
    except CycleError:
        pass