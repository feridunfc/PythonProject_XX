from __future__ import annotations
import os, json, logging
from typing import Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

class AIError(RuntimeError):
    pass

def _headers_for(provider: str) -> Dict[str, str]:
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key: raise AIError("OPENAI_API_KEY missing")
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key: raise AIError("ANTHROPIC_API_KEY missing")
        return {"x-api-key": key, "content-type": "application/json"}
    if provider == "deepseek":
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key: raise AIError("DEEPSEEK_API_KEY missing")
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    raise AIError(f"Unknown provider: {provider}")

class AIClient:
    def __init__(self, timeout: int = None):
        self.timeout = timeout or int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.http = httpx.AsyncClient(timeout=self.timeout)

    async def aclose(self): await self.http.aclose()

    @retry(
        stop=stop_after_attempt(int(os.getenv("MAX_RETRIES", "3"))),
        wait=wait_random_exponential(multiplier=1, max=10),
        retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def chat(self, provider: str, model: str, system: str, user: str, temperature: float=0.2, max_tokens: int=1000) -> str:
        if provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": model,
                "messages": [{"role":"system","content":system},{"role":"user","content":user}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        elif provider == "anthropic":
            url = "https://api.anthropic.com/v1/messages"
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system,
                "messages": [{"role":"user","content":user}],
            }
            # Anthropic requires version header
        elif provider == "deepseek":
            url = "https://api.deepseek.com/v1/chat/completions"
            payload = {
                "model": model,
                "messages": [{"role":"system","content":system},{"role":"user","content":user}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        else:
            raise AIError(f"Unknown provider: {provider}")

        headers = _headers_for(provider)
        if provider == "anthropic":
            headers["anthropic-version"] = "2023-06-01"

        r = await self.http.post(url, headers=headers, json=payload)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            log.error("AI %s error %s: %s", provider, e.response.status_code if e.response else "?", e)
            raise

        js = r.json()
        # Normalize text
        if provider in ("openai","deepseek"):
            return js["choices"][0]["message"]["content"]
        if provider == "anthropic":
            return "".join(part.get("text","") for part in js["content"])
        return json.dumps(js)

def model_for_role(role: str) -> str:
    env_map = {
        "architect": os.getenv("MODEL_ARCHITECT", "gpt-4o-mini"),
        "codegen":   os.getenv("MODEL_CODEGEN",   "gpt-4o-mini"),
        "critic":    os.getenv("MODEL_CRITIC",    "gpt-4o-mini"),
        "tester":    os.getenv("MODEL_TESTER",    "gpt-4o-mini"),
    }
    return env_map.get(role, os.getenv("MODEL_CODEGEN","gpt-4o-mini"))
