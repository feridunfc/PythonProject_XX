from orchestrator.task_scheduler import TaskScheduler
def test_topological_order_linear():
    tasks=[{'id':'a'},{'id':'b','deps':['a']},{'id':'c','deps':['b']}]
    out=[t['id'] for t in TaskScheduler(tasks).topological()]
    assert out==['a','b','c']
