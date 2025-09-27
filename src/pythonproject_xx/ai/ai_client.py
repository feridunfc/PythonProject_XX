from __future__ import annotations
from typing import Dict, Tuple

from .config.settings import get_settings
from .ai.providers.mock_provider import MockProvider
try:
    from .ai.providers.openai_provider import OpenAIProvider
except Exception:
    OpenAIProvider = None  # type: ignore

class AIClient:
    """Provider seçimi + basit usage logging döndüren hafif istemci."""
    def __init__(self, model_spec: str | None = None) -> None:
        self.settings = get_settings()
        self.model_spec = model_spec or self.settings.default_model
        self.provider_name, self.model = self._parse_spec(self.model_spec)
        self.provider = self._build_provider(self.provider_name)

    def _parse_spec(self, spec: str) -> Tuple[str, str]:
        if ":" in spec:
            p, m = spec.split(":", 1)
        else:
            p, m = spec, "tiny"
        # FORCE_PROVIDER override
        force = self.settings.force_provider
        if force:
            p = force
        return p, m

    def _build_provider(self, name: str):
        if name == "mock":
            return MockProvider()
        if name == "openai":
            if OpenAIProvider is None:
                raise RuntimeError("OpenAI provider unavailable (package missing?).")
            return OpenAIProvider(api_key=self.settings.openai_api_key)
        raise ValueError(f"Unknown provider: {name}")

    def run(self, user_prompt: str, system_prompt: str | None = None, temperature: float = 0.3) -> Dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        out = self.provider.chat(self.model, messages, temperature=temperature)
        return out