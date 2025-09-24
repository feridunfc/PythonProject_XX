from .base_agent import AIAgent
from ..config.agent_config import AGENT_MODEL_MAP
from ..utils.ai_client import AIClient

# Ör: feridunfc_meta_ai/agents/critic_agent.py
from .base_agent import AIAgent



class CriticAgent(AIAgent):
    def __init__(self, client):
        super().__init__("critic", client)
    async def process_task(self, task, context: dict) -> dict:
        prompt = f"""
Provide a concise code review in bullet points. Mark CRITICAL items with 'CRITICAL:' prefix.
Code:
{context.get('generated_code','')[:5000]}

Test results:
{context.get('test_results','')}
"""
        resp = await self.client.call_model("critic", prompt=prompt)
        lines = [l.strip() for l in resp.content.splitlines() if l.strip()]
        return {"review_report": resp.content, "suggestions": lines}
