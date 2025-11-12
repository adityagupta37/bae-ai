from __future__ import annotations
import hashlib
import time
from collections import OrderedDict
from threading import RLock
from typing import Optional

_STORE: "OrderedDict[str, tuple[float, str]]" = OrderedDict()
_LOCK = RLock()

def make_cache_key(*parts: str) -> str:
    payload = "||".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def cache_get(key: str) -> Optional[str]:
    with _LOCK:
        entry = _STORE.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if expires_at <= time.time():
            _STORE.pop(key, None)
            return None
        _STORE.move_to_end(key)
        return value

def cache_set(key: str, value: str, ttl_s: int, max_items: int) -> None:
    if ttl_s <= 0 or max_items <= 0:
        return
    expires_at = time.time() + ttl_s
    with _LOCK:
        _STORE[key] = (expires_at, value)
        _STORE.move_to_end(key)
        _prune_locked(max_items)

def _prune_locked(max_items: int) -> None:
    now = time.time()
    expired = [cache_key for cache_key, (expires, _) in _STORE.items() if expires <= now]
    for cache_key in expired:
        _STORE.pop(cache_key, None)
    while len(_STORE) > max_items:
        _STORE.popitem(last=False)

def cache_clear() -> None:
    with _LOCK:
        _STORE.clear()
