from __future__ import annotations
import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Provider seçimi: "mock:tiny" veya "openai:gpt-4o-mini" gibi
    default_model: str = Field("mock:tiny", env="DEFAULT_MODEL")
    force_provider: str | None = Field(default=os.getenv("FORCE_PROVIDER"))
    openai_api_key: str | None = Field(default=os.getenv("OPENAI_API_KEY"))

    # Orchestrator & Scheduler
    max_workers: int = Field(2, env="MAX_WORKERS")

    # Limits (sandbox için okunur)
    sandbox_mem_limit: str | None = Field(default=os.getenv("SANDBOX_MEM_LIMIT"))
    sandbox_cpu_shares: int | None = Field(default=None)

    # Observability
    trace_path: str = Field("logs/trace.jsonl", env="TRACE_PATH")

def get_settings() -> Settings:
    return Settings()