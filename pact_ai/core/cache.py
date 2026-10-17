import hashlib
import json
import threading
import time
from typing import Any


def make_key(*parts: Any) -> str:
    digest = hashlib.sha256()
    for part in parts:
        if isinstance(part, bytes):
            digest.update(part)
        else:
            digest.update(json.dumps(part, sort_keys=True, default=str, ensure_ascii=False).encode())
        digest.update(b"\x00")
    return digest.hexdigest()


class TTLCache:
    def __init__(self, ttl_seconds: int, max_items: int = 256) -> None:
        self._ttl = ttl_seconds
        self._max_items = max_items
        self._items: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        if self._ttl <= 0:
            return None
        with self._lock:
            entry = self._items.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._items[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        if self._ttl <= 0:
            return
        with self._lock:
            if len(self._items) >= self._max_items:
                oldest = min(self._items, key=lambda k: self._items[k][0])
                del self._items[oldest]
            self._items[key] = (time.monotonic() + self._ttl, value)
