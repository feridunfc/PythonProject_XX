import asyncio, logging, json
from agents.planner import PlannerAgent
from agents.codegen import CodeGenAgent
from agents.critic import CriticAgent
from agents.tester import TesterAgent
from orchestrator.task_scheduler import TaskScheduler
from orchestrator.adaptive_executor import AdaptiveExecutor
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
log=logging.getLogger('orchestrator')
def demo_tasks(spec):
    return [
        {'id':'plan','name':'Plan','prompt':f'Plan for: {spec}'},
        {'id':'code','name':'Code','deps':['plan'],'prompt':f'Generate code for: {spec}'},
        {'id':'test','name':'Test','deps':['code'],'prompt':f'Test code for: {spec}'},
    ]
async def main_async(spec):
    log.info('Pipeline start spec=%s', spec)
    planner=PlannerAgent('planner'); codegen=CodeGenAgent('codegen'); critic=CriticAgent('critic'); tester=TesterAgent(); execu=AdaptiveExecutor(critic, tester)
    tasks=demo_tasks(spec); ctx={'spec':spec}
    for task in TaskScheduler(tasks).topological():
        if task['id']=='plan': ctx.update(await planner.run(task, ctx))
        elif task['id']=='code': ctx=await execu.run_once(codegen, task, ctx)
    log.info('Pipeline finished; summary:\n%s', json.dumps({k:v for k,v in ctx.items() if k in ['plan','files','passed']}, indent=2)); print('DONE')
if __name__=='__main__':
    import argparse; p=argparse.ArgumentParser(); p.add_argument('--spec', default='Basit TODO API: kullanÄ±cÄ±, gÃ¶rev ekle/listele'); a=p.parse_args(); asyncio.run(main_async(a.spec))
