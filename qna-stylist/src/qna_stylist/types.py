from enum import Enum
from typing import Optional, TypedDict

class StylistTone(str, Enum):
    FRIENDLY = "friendly"
    FUNNY = "funny"
    WITTY = "witty"
    GENZ = "genz"
    HIGH_ENERGY = "high_energy"
    PROFESSIONAL = "professional"  # low-humor, crisp

class StylistResult(TypedDict):
    styled_text: str
    used_tone: StylistTone
    safety_notes: Optional[str]
    elapsed_ms: int
    cache_hit: bool
