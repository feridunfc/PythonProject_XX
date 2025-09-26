# MULTI_AI/utils/ai_client.py
import os
import asyncio
import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

log = logging.getLogger("utils.ai_client")


class AIError(Exception):
    pass


def _map_model_for(provider: str, model: str | None) -> str:
    """Hedef sağlayıcıya uygun makul varsayılan model adı."""
    if not model:
        model = ""
    p = (provider or "").lower()
    if p == "openai":
        return model if model.startswith("gpt-") else "gpt-4o-mini"
    if p == "gemini":
        return model if model.startswith("gemini-") else "gemini-1.5-flash"
    if p == "deepseek":
        return model if model.startswith("deepseek") else "deepseek-chat"
    return "mock"


class AIClient:
    def __init__(self, timeout: float = 30.0):
        self._client = httpx.AsyncClient(timeout=timeout)

    async def _maybe_wait_retry_after(self, r: httpx.Response) -> None:
        """429 durumunda Retry-After başlığına saygı göster."""
        if r.status_code == 429:
            retry_after = r.headers.get("Retry-After") or r.headers.get("retry-after")
            if retry_after:
                try:
                    wait_s = int(retry_after)
                except ValueError:
                    wait_s = 2
                log.warning("429 received, waiting %s seconds per Retry-After", wait_s)
                await asyncio.sleep(wait_s)

    # DÜŞÜK SEVİYE SAĞLAYICI ÇAĞRISI (retry burada)
    @retry(
        stop=stop_after_attempt(6),
        wait=wait_random_exponential(multiplier=1, max=60),
        retry=retry_if_exception_type(httpx.HTTPError),
        reraise=True,
    )
    async def _call(self, provider: str, model: str, system: str, prompt: str,
                    max_tokens: int = 800, temperature: float = 0.2) -> str:
        provider = (provider or "").lower()

        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise AIError("GEMINI_API_KEY missing")
            model = _map_model_for("gemini", model)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            body = {
                "systemInstruction": {
                    "role": "system",
                    "parts": [{"text": system or "You are a helpful AI."}],
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
            await self._maybe_wait_retry_after(r)
            r.raise_for_status()
            js = r.json()
            # Gemini text extract
            try:
                cands = js.get("candidates") or []
                if cands:
                    parts = (cands[0].get("content") or {}).get("parts") or []
                    return "".join(p.get("text", "") for p in parts)
            except Exception:
                pass
            return str(js)

        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise AIError("OPENAI_API_KEY missing")
            model = _map_model_for("openai", model)
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system or "You are a helpful AI."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            r = await self._client.post(url, headers=headers, json=body)
            await self._maybe_wait_retry_after(r)
            r.raise_for_status()
            js = r.json()
            ch = (js.get("choices") or [{}])[0]
            msg = ch.get("message") or {}
            return msg.get("content", "") or ch.get("text", "") or str(js)

        elif provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise AIError("DEEPSEEK_API_KEY missing")
            model = _map_model_for("deepseek", model)
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system or "You are a helpful AI."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            r = await self._client.post(url, headers=headers, json=body)
            await self._maybe_wait_retry_after(r)
            r.raise_for_status()
            js = r.json()
            ch = (js.get("choices") or [{}])[0]
            msg = ch.get("message") or {}
            return msg.get("content", "") or ch.get("text", "") or str(js)

        elif provider == "mock":
            return "MOCK_OK"

        else:
            raise AIError(f"Unknown provider: {provider}")

    # YÜKSEK SEVİYE CHAT (opsiyonel fallback ile)
    async def chat(self, provider: str, model: str, system: str, prompt: str,
                   max_tokens: int = 800, temperature: float = 0.2) -> str:
        try:
            return await self._call(provider, model, system, prompt, max_tokens, temperature)
        except httpx.HTTPStatusError as e:
            # 429 ise ve fallback açıksa (AI_FALLBACK=1), Gemini'ye düş
            if e.response is not None and e.response.status_code == 429:
                allow_fallback = (os.getenv("AI_FALLBACK", "1") == "1")
                have_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
                if allow_fallback and provider.lower() != "gemini" and have_gemini:
                    log.warning("Rate limited on %s -> falling back to Gemini", provider)
                    return await self._call("gemini", None, system, prompt, max_tokens, temperature)
            raise

    async def close(self):
        try:
            await self._client.aclose()
        except Exception:
            log.exception("error closing httpx client")
