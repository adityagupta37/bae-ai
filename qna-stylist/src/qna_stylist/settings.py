from pydantic import BaseSettings, Field
from typing import Optional, List

class Settings(BaseSettings):
    # LLM setup (CrewAI picks env-configured LLM; provide defaults here)
    llm_model: str = Field(default="gpt-4o-mini", description="Provider-specific model id")
    
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
