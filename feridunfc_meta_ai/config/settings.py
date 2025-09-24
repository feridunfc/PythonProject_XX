from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    deepseek_api_key: Optional[str] = Field(None, alias="DEEPSEEK_API_KEY")
    force_provider: Optional[str] = Field(None, alias="FORCE_PROVIDER")  # "deepseek" veya "openai"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # ← 'extra_forbidden' hatasını engeller
    )

settings = Settings()
