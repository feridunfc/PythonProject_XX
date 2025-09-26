class AdaptiveExecutor:
    def __init__(self, critic, tester): self.critic=critic; self.tester=tester
    async def run_once(self, agent, task, context):
        res=await agent.run(task, context); context.update(res)
        if 'files' in res:
            crit=await self.critic.run(task, context); context.update(crit)
            if not crit.get('passed', True): return context
            test=await self.tester.run(task, context); context.update(test)
        return context
