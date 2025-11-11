from __future__ import annotations
import re
from typing import Tuple, Optional, List
from .settings import Settings

_SENSITIVE_RE = re.compile(r"\b(suicide|self[- ]?harm|sexual\s+minors|extremis[m]|terroris[m]|emergency|harass|hate\s+crime)\b", re.I)

def analyze_topic(question: str, answer: str, cfg: Settings) -> Tuple[bool, Optional[str]]:
    """Returns (should_reduce_humor, note)"""
    text = f"{question}\n{answer}"
    if cfg.enable_safety_filters and (_SENSITIVE_RE.search(text) or any(k.lower() in text.lower() for k in cfg.reduce_humor_keywords)):
        return True, "Sensitive or serious topic detected — humor softened."
    return False, None

def clamp_length(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + "…"

def strip_excess_emojis(text: str, max_emoji: int) -> str:
    # naive emoji stripper: count unicode category So and common emoji ranges
    # keep the first N visually; replace excess with nothing.
    chars = list(text)
    count = 0
    out: List[str] = []
    for ch in chars:
        if is_emoji(ch):
            if count < max_emoji:
                out.append(ch)
            count += 1
        else:
            out.append(ch)
    return "".join(out)

def is_emoji(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x1F300 <= cp <= 0x1FAFF or  # Misc Symbols and Pictographs
        0x1F600 <= cp <= 0x1F64F or  # Emoticons
        0x1F1E6 <= cp <= 0x1F1FF or  # Flags
        0x2600  <= cp <= 0x26FF  or  # Misc symbols
        0x2700  <= cp <= 0x27BF      # Dingbats
    )
