from __future__ import annotations

import os
import json
import logging
from types import SimpleNamespace

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception,
)

from ..config.agent_config import AGENT_MODEL_MAP

logger = logging.getLogger(__name__)

# --- Sabitler ---
ASCII_USER_AGENT = "feridunfc-meta-ai/0.1"  # sadece ASCII!

# 429'u varsayılan olarak retry etmiyoruz; doğrudan fallback yapacağız.
AI_RETRY_429 = os.getenv("AI_RETRY_429", "0").strip() == "1"

# Ağ/zaman aşımı ve 5xx'ler retry'lanır. 429 sadece AI_RETRY_429=1 ise retry'lanır.
RETRYABLE_STATUS = {408, 409, 500, 502, 503, 504} | ({429} if AI_RETRY_429 else set())

# Fallback'e yol açan kodlar: auth/bakiye + 429 + retryable olanlar
FALLBACK_STATUS = {401, 402, 403, 429} | RETRYABLE_STATUS


def _is_retryable_http(e: Exception) -> bool:
    """HTTP transport ve retryable status kodlarını yeniden dene."""
    if isinstance(e, httpx.HTTPStatusError):
        return e.response is not None and e.response.status_code in RETRYABLE_STATUS
    return isinstance(e, httpx.TransportError)


def _retry_after_hint(headers: httpx.Headers) -> str:
    """Header'lardan bekleme ipucunu (saniye) sadece log için çıkar."""
    ra = headers.get("Retry-After") or headers.get("retry-after")
    if ra:
        return f"Retry-After={ra}"
    for k in ("x-ratelimit-reset-requests", "x-ratelimit-reset-tokens"):
        v = headers.get(k)
        if v:
            return f"{k}={v}"
    return ""


class AIClient:
    def __init__(self, timeout: int = 30):
        # Client seviyesinde sadece ASCII User-Agent tut
        self.client = httpx.AsyncClient(timeout=timeout, headers={"User-Agent": ASCII_USER_AGENT})

    async def aclose(self):
        await self.client.aclose()

    # Sağlayıcı sırası (agent rolüne göre)
    def _providers_for_role(self, agent_role: str):
        providers = AGENT_MODEL_MAP.get(agent_role, [])
        # FORCE_PROVIDER başa al
        force = os.getenv("FORCE_PROVIDER", "").strip().lower()
        if force:
            if force == "mock":
                return [("mock", "mock")]
            forced = [pm for pm in providers if pm[0] == force]
            rest   = [pm for pm in providers if pm[0] != force]
            providers = forced + rest
        return providers or [("mock", "mock")]

    async def call_model(self, agent_role: str, prefer_costly: bool = False, prompt: str = "", system: str = ""):
        providers = self._providers_for_role(agent_role)
        last_err: Exception | None = None

        for prov, model in providers:
            try:
                if prov == "openai":
                    return await self.call_openai(model, prompt, system)
                elif prov == "deepseek":
                    return await self.call_deepseek(model, prompt, system)
                elif prov == "gemini":
                    return await self.call_gemini(model, prompt, system)
                elif prov == "mock":
                    return self._mock_response(agent_role, prompt)
                else:
                    logger.warning("Unknown provider %s, skipping", prov)
            except httpx.HTTPStatusError as e:
                sc = e.response.status_code if e.response is not None else None
                hint = _retry_after_hint(e.response.headers) if e.response is not None else ""
                logger.error("%s call failed (%s)%s", prov, sc, f" ({hint})" if hint else "")
                # Bu status kodlarında bir sonraki sağlayıcıya düş
                if sc in FALLBACK_STATUS:
                    last_err = e
                    continue
                raise
            except Exception as e:
                if prov == "openai" and str(e) == "OpenAI 429":
                    logger.warning("OpenAI rate limited; falling back to next provider")
                    last_err = e
                    continue
                logger.exception("%s provider error; trying next", prov)
                last_err = e
                continue

        if os.getenv("AI_ALLOW_MOCK", "1") == "1":
            logger.warning("All providers failed, returning MOCK output")
            return self._mock_response(agent_role, prompt)
        raise RuntimeError(f"All providers failed: {last_err}")

    # -------------------- OpenAI --------------------
    @retry(
        stop=stop_after_attempt(6),
        wait=wait_random_exponential(multiplier=1, max=60),
        retry=retry_if_exception(_is_retryable_http),
        reraise=True,
    )
    async def call_openai(self, model: str, prompt: str, system: str):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        messages = [
            {"role": "system", "content": system or "You output only JSON."},
            {"role": "user",   "content": prompt}
        ]

        try:
            r = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 800},
            )
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 429:
                hint = (e.response.headers.get("Retry-After")
                        or e.response.headers.get("x-ratelimit-reset-requests")
                        or e.response.headers.get("x-ratelimit-reset-tokens"))
                if hint:
                    logger.warning("OpenAI 429; sunucu ipucu: %s", hint)
                else:
                    logger.warning("OpenAI 429; sunucu ipucu: yok")
                # HTTPStatusError yerine RuntimeError -> tenacity bunu retry etmeyecek, call_model fallback'e geçecek
                raise RuntimeError("OpenAI 429")
            raise

        js = r.json()
        return SimpleNamespace(content=js["choices"][0]["message"]["content"], usage=js.get("usage", {}))

    # -------------------- DeepSeek --------------------
    @retry(
        stop=stop_after_attempt(6),
        wait=wait_random_exponential(multiplier=1, max=60),
        retry=retry_if_exception(_is_retryable_http),
        reraise=True,
    )
    async def call_deepseek(self, model: str, prompt: str, system: str):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set")

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        messages = [
            {"role": "system", "content": system or "You output only JSON."},
            {"role": "user", "content": prompt},
        ]

        r = await self.client.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json={"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 800},
        )
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 429:
                hint = _retry_after_hint(e.response.headers)
                logger.warning("DeepSeek 429; sunucu ipucu: %s", hint or "yok")
            raise

        js = r.json()
        return SimpleNamespace(content=js["choices"][0]["message"]["content"], usage=js.get("usage", {}))

    # -------------------- Gemini --------------------
    @retry(
        stop=stop_after_attempt(6),
        wait=wait_random_exponential(multiplier=1, max=60),
        retry=retry_if_exception(_is_retryable_http),
        reraise=True,
    )
    async def call_gemini(self, model: str, prompt: str, system: str):
        # Destek: GEMINI_API_KEY veya GOOGLE_API_KEY
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY (veya GOOGLE_API_KEY) is not set")

        # Gemini REST: ?key=API_KEY ile auth, content yapısı farklı
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        body = {
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": system or "You output only JSON."}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800,
                "response_mime_type": "application/json",
            },
        }

        r = await self.client.post(url, headers=headers, json=body)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response is not None and e.response.status_code == 429:
                hint = _retry_after_hint(e.response.headers)
                logger.warning("Gemini 429; sunucu ipucu: %s", hint or "yok")
            raise

        js = r.json()
        # Tipik yanıt: candidates[0].content.parts[0].text
        text = ""
        try:
            cands = js.get("candidates") or []
            if cands:
                parts = cands[0].get("content", {}).get("parts", []) or []
                text = "".join(p.get("text", "") for p in parts)
        except Exception:
            pass

        # Eğer text boşsa tüm JSON'u string olarak döndür (diagnostic)
        return SimpleNamespace(content=(text or json.dumps(js)), usage=js.get("usageMetadata", {}))

    # --- MOCK cevabı ---
    def _mock_response(self, agent_role: str, prompt: str):
        if agent_role == "architect":
            plan = {
                "sprint_title": "Sprint for: Basit TODO API",
                "sprint_goal": "Kullanıcı, görev ekle/listele uçlarıyla çalışan basit bir TODO API",
                "weeks": [
                    {
                        "week_number": 1,
                        "tasks": [
                            {
                                "task_id": "architect-initial-plan",
                                "title": "Mimari ve Modeller",
                                "description": "FastAPI yapısı ve Pydantic modelleri",
                                "agent_type": "architect",
                                "dependencies": [],
                                "estimated_hours": 4,
                            },
                            {
                                "task_id": "codegen-api",
                                "title": "API Uçları",
                                "description": "POST /users, POST /tasks, GET /tasks",
                                "agent_type": "codegen",
                                "dependencies": ["architect-initial-plan"],
                                "estimated_hours": 8,
                            },
                            {
                                "task_id": "tester-api",
                                "title": "Testler",
                                "description": "pytest ile unit/integration testleri",
                                "agent_type": "tester",
                                "dependencies": ["codegen-api"],
                                "estimated_hours": 6,
                            },
                            {
                                "task_id": "critic-review",
                                "title": "Kod İncelemesi",
                                "description": "CRUD doğrulama ve basit güvenlik kontrolleri",
                                "agent_type": "critic",
                                "dependencies": ["tester-api"],
                                "estimated_hours": 2,
                            },
                        ],
                    }
                ],
            }
            return SimpleNamespace(content=json.dumps(plan), usage={"mock": True})

        return SimpleNamespace(content="MOCK_OK", usage={"mock": True})


