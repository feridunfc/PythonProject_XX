# utils/ai_client.py
import os
import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

log = logging.getLogger("utils.ai_client")

class AIError(Exception):
    pass

class AIClient:
    def __init__(self, timeout: float = 30.0):
        # One async client per process is fine for our CLI/orchestrator usage
        self._client = httpx.AsyncClient(timeout=timeout)

    @retry(
        stop=stop_after_attempt(6),
        wait=wait_random_exponential(multiplier=1, max=60),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )
    async def chat(
        self,
        provider: str,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int = 800,
        temperature: float = 0.2,
    ) -> str:
        """
        Minimal, provider-agnostic chat wrapper with retries.
        Providers: gemini | openai | deepseek | mock
        """
        provider = (provider or "mock").lower()
        system = system or "You are a helpful AI."
        prompt = prompt or ""

        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise AIError("GEMINI_API_KEY missing")
            # If a generic model leaked in, coerce to a valid Gemini default
            if not model or model == "gpt-4o-mini":
                model = "gemini-1.5-flash"

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            body = {
                "systemInstruction": {
                    "role": "system",
                    "parts": [{"text": system}],
                },
                "contents": [
                    {"role": "user", "parts": [{"text": prompt}]}
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            }
            r = await self._client.post(url, headers=headers, json=body)
            r.raise_for_status()
            js = r.json()

            # Extract text safely
            for c in js.get("candidates", []):
                content = c.get("content") or {}
                parts = content.get("parts") or []
                text = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                if text:
                    return text.strip()
            # Fallback: return raw JSON text
            return str(js)

        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise AIError("OPENAI_API_KEY missing")
            if not model or model == "gemini-1.5-flash":
                model = "gpt-4o-mini"

            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            r = await self._client.post(url, headers=headers, json=body)
            r.raise_for_status()
            js = r.json()
            choice = (js.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            return (msg.get("content") or choice.get("text") or "").strip() or str(js)

        elif provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise AIError("DEEPSEEK_API_KEY missing")
            if not model:
                model = "deepseek-chat"

            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            r = await self._client.post(url, headers=headers, json=body)
            r.raise_for_status()
            js = r.json()
            choice = (js.get("choices") or [{}])[0]
            msg = choice.get("message") or {}
            return (msg.get("content") or choice.get("text") or "").strip() or str(js)

        elif provider == "mock":
            return "MOCK_OK"

        else:
            raise AIError(f"Unknown provider: {provider}")
