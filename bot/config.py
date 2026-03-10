"""Prompt Strategist Bot — Configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram
    bot_token: str = Field(..., description="Telegram Bot API token")

    # Groq API
    groq_api_key: str = Field(..., description="Groq API key")
    groq_model: str = Field("groq/compound", description="Groq model")

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        10, description="Max requests per minute per user"
    )

    # Logging
    log_level: str = Field("INFO", description="Logging level")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
