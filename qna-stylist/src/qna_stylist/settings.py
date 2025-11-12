import os
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional, List, Literal

class Settings(BaseSettings):
    # LLM setup
    provider: Literal["openai", "ollama"] = Field(
        default="openai",
        description="Primary LLM provider to use."
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model used for styling."
    )
    ollama_model: str = Field(
        default="phi3:medium",
        description="Fallback Ollama model tag."
    )
    temperature: float = Field(
        default=0.6,
        description="Sampling temperature applied to all LLM calls."
    )
    max_tokens: int = Field(
        default=512,
        description="Maximum generation length."
    )
    cache_ttl_s: int = Field(
        default=600,
        description="Seconds to keep cached responses."
    )
    cache_max_items: int = Field(
        default=1024,
        description="Maximum number of cache entries to retain."
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="Optional override for OPENAI_API_KEY environment variable."
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434/v1",
        description="Base URL for the local Ollama HTTP endpoint."
    )
    
    # Behavior
    max_emojis: int = 3
    max_length_chars: int = 1200
    enable_safety_filters: bool = True
    safe_topics_blocklist: List[str] = [
        "suicide", "self-harm", "sexual minors", "terrorism", "extremism",
        "medical emergency", "harassment", "hate crime"
    ]
    reduce_humor_keywords: List[str] = [
        "legal compliance", "privacy policy", "terms of service", "security incident",
        "outage", "breach", "death", "bereavement", "disaster", "earthquake", "flood"
    ]

    # Retries
    retry_attempts: int = 3
    retry_min_wait_s: float = 0.6
    retry_max_wait_s: float = 2.4

    class Config:
        env_prefix = "STYLIST_"
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_openai_api_key(self) -> Optional[str]:
        return self.openai_api_key or os.getenv("STYLIST_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

    def active_model(self, provider_override: Optional[str] = None) -> str:
        provider = provider_override or self.provider
        return self.openai_model if provider == "openai" else self.ollama_model
