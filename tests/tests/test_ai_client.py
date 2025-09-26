import os, pytest
from utils.ai_client import AIClient
@pytest.mark.asyncio
async def test_mock_chat():
    os.environ['FORCE_PROVIDER']='mock'; c=AIClient(); out=await c.chat('mock','gpt-4o-mini','sys','hi')
    assert out.startswith('[MOCK:')
