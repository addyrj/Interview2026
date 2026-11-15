---

# Q218. Cache API responses
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Write an `AsyncTTLCache` with `get(key, loader)`. Fresh entries are returned from memory, expired ones reload, and simultaneous misses for the same key must share ONE API call.

```python
cache = AsyncTTLCache(ttl=60)
await cache.get('user:1', fetch_user)
```

---

## 💡 Quick Concept (2 lines only)
Store `(expires_at, value)` using `time.monotonic()`; also track in-flight tasks so concurrent misses are coalesced (no cache stampede).
हिंदी: (expiry, value) store करो; in-flight task भी रखो ताकि एक साथ miss पर सिर्फ एक API call हो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
import time                                       # monotonic clock
from collections.abc import Awaitable, Callable   # type hints
from typing import Any                            # generic


class AsyncTTLCache:
    def __init__(self, ttl: float) -> None:
        self.ttl = ttl                            # seconds an entry stays fresh
        self._data: dict[str, tuple[float, Any]] = {}  # key -> (expires_at, value)
        self._inflight: dict[str, asyncio.Task] = {}   # key -> running request

    async def get(self, key: str, loader: Callable[[], Awaitable[Any]]) -> Any:
        hit = self._data.get(key)                 # look in cache
        if hit and hit[0] > time.monotonic():     # present and not expired
            return hit[1]                         # cache hit
        if key not in self._inflight:             # nobody is loading this key yet
            self._inflight[key] = asyncio.create_task(self._load(key, loader))  # start one load
        return await self._inflight[key]          # everyone shares the same request

    async def _load(self, key: str, loader: Callable[[], Awaitable[Any]]) -> Any:
        try:
            value = await loader()                # real API call
            self._data[key] = (time.monotonic() + self.ttl, value)  # store with expiry
            return value                          # hand value back
        finally:
            self._inflight.pop(key, None)         # request finished (success or error)


# ---------- TEST CASES ----------
calls = 0                                         # real API call counter


async def api() -> str:
    global calls                                  # update counter
    calls += 1                                    # real call
    await asyncio.sleep(0.02)                     # simulated latency
    return f"data#{calls}"                        # unique per real call


async def main() -> None:
    cache = AsyncTTLCache(ttl=0.1)                # 100 ms TTL
    print(await asyncio.gather(*(cache.get("u", api) for _ in range(3))))  # 3 callers, 1 request
    print(await cache.get("u", api), "calls =", calls)  # fresh -> cache hit
    await asyncio.sleep(0.15)                     # let TTL expire
    print(await cache.get("u", api), "calls =", calls)  # expired -> reload


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# ['data#1', 'data#1', 'data#1']
# data#1 calls = 1
# data#2 calls = 2
```

---

## 🔍 Why This Works (3 lines max)
`monotonic()` is immune to wall-clock changes. The `_inflight` dict makes 3 simultaneous callers await the same task (1 real call). The `finally` removes the in-flight entry even on error, so failures are not cached.
हिंदी: monotonic clock TTL के लिए safe है; _inflight dict से stampede रुकता है।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library
import httpx                                      # async HTTP client


def handler(request: httpx.Request) -> httpx.Response:
    handler.count += 1                            # count requests that reach the "server"
    return httpx.Response(200, json={"path": request.url.path, "n": handler.count})


handler.count = 0                                 # function attribute as counter


async def main() -> None:
    cache: dict[str, dict] = {}                   # simplest possible cache (no TTL)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://api.test") as c:
        async def get(path: str) -> dict:
            if path not in cache:                 # miss
                cache[path] = (await c.get(path)).json()  # fetch + store parsed JSON
            return cache[path]                    # hit or just stored

        print(await get("/a"))                    # network
        print(await get("/a"))                    # cache (same n)
        print(await get("/b"))                    # network
    print("server hits:", handler.count)          # 2


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# {'path': '/a', 'n': 1}
# {'path': '/a', 'n': 1}
# {'path': '/b', 'n': 2}
# server hits: 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: time.time() for TTL (clock can jump) and no in-flight tracking
if key in cache and cache[key][0] > time.time():   # clock change breaks this
    return cache[key][1]
value = await loader()                              # 100 concurrent misses = 100 API calls
cache[key] = (time.time() + ttl, value)

# ✅ Correct: monotonic() + share in-flight task (see solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "TTL cache + request coalescing prevents the thundering herd; use Redis for multi-process, and mention stale-while-revalidate."

---

## 🔗 Related Questions
→ Q185 (cache with TTL) | Q194 (data fetcher with caching) | Q215 (memoize async) | Q278 (lru_cache)
