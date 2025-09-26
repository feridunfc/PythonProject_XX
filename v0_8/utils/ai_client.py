import os, httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
DEFAULT_MODEL='gpt-4o-mini'
class AIError(Exception):
    pass
def pick_provider():
    forced=(os.getenv('FORCE_PROVIDER') or '').strip().lower()
    if forced: return forced
    if os.getenv('OPENAI_API_KEY'): return 'openai'
    if os.getenv('GEMINI_API_KEY'): return 'gemini'
    if os.getenv('DEEPSEEK_API_KEY'): return 'deepseek'
    return 'mock'
class AIClient:
    def __init__(self, timeout=30.0):
        self._client=httpx.AsyncClient(timeout=timeout)
    @retry(stop=stop_after_attempt(int(os.getenv('MAX_RETRIES','3'))), wait=wait_random_exponential(multiplier=1,max=10), retry=retry_if_exception_type(httpx.HTTPError), reraise=True)
    async def chat(self, provider, model, system, prompt, max_tokens=800, temperature=0.2):
        provider=(provider or pick_provider()).lower()
        if provider=='mock':
            return f"[MOCK:{model}] {prompt[:64]}..."
        raise AIError('Only mock is bundled in the minimal zip')

# NOTE(#9): If OPENAI_API_KEY is missing, prefer mock (FORCE_PROVIDER=mock).
