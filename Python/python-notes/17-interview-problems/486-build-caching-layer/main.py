"""Build Caching Layer: TTL + LRU cache with decorator and stats. Run: python main.py"""
from __future__ import annotations

import functools
import time
from collections import OrderedDict
from typing import Any, Callable, Hashable


class TTLCache:
    def __init__(self, max_size: int = 128, ttl: float = 60.0, clock: Callable[[], float] = time.monotonic) -> None:
        self.max_size, self.ttl, self.clock = max_size, ttl, clock
        self._data: OrderedDict[Hashable, tuple[float, Any]] = OrderedDict()  # key -> (expires_at, value)
        self.hits = 0
        self.misses = 0

    def get(self, key: Hashable, default: Any = None) -> Any:
        item = self._data.get(key)
        if item is None or item[0] <= self.clock():  # missing or expired
            self._data.pop(key, None)
            self.misses += 1
            return default
        self._data.move_to_end(key)  # mark as recently used
        self.hits += 1
        return item[1]

    def set(self, key: Hashable, value: Any, ttl: float | None = None) -> None:
        self._data[key] = (self.clock() + (self.ttl if ttl is None else ttl), value)
        self._data.move_to_end(key)
        while len(self._data) > self.max_size:
            self._data.popitem(last=False)  # evict least recently used

    def invalidate(self, key: Hashable) -> None:
        self._data.pop(key, None)


_MISSING = object()  # sentinel so None can be cached


def cached(cache: TTLCache) -> Callable:
    def deco(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (fn.__qualname__, args, tuple(sorted(kwargs.items())))
            val = cache.get(key, _MISSING)
            if val is _MISSING:
                val = fn(*args, **kwargs)  # cache miss: do the real work
                cache.set(key, val)
            return val
        wrapper.cache = cache  # type: ignore[attr-defined]
        return wrapper
    return deco


if __name__ == "__main__":
    now = [0.0]  # fake clock so the test is instant
    cache = TTLCache(max_size=2, ttl=10, clock=lambda: now[0])
    calls = {"n": 0}

    @cached(cache)
    def get_user(uid: int) -> dict[str, int]:
        calls["n"] += 1
        return {"id": uid}

    get_user(1); get_user(1)
    assert calls["n"] == 1 and (cache.hits, cache.misses) == (1, 1)
    now[0] = 11  # TTL passed
    get_user(1)
    assert calls["n"] == 2
    get_user(2); get_user(3)  # size 2 -> user 1 evicted (LRU)
    get_user(1)
    assert calls["n"] == 5
    cache.invalidate(("get_user", (1,), ()))
    print("hits", cache.hits, "misses", cache.misses, "size", len(cache._data))
    print("all ok")
