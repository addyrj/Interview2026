---

# Q194. Build Data Fetcher with Caching
# Category: Real World Problems
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build an async `CachedFetcher(fetch, ttl)` whose `get(url)` returns cached data while fresh, and de-duplicates concurrent requests: if 5 callers ask for the same URL at once, only ONE network call is made.

```python
await asyncio.gather(*(f.get("/a") for _ in range(5)))   # network_calls == 1
```

---

## 💡 Quick Concept (2 lines only)
Two layers: a TTL cache for finished results, and an "in-flight" dict storing the running Task so concurrent callers await the same one.
हिंदी: दो layers: पूरा हुआ result TTL cache में, और चल रहा request in-flight dict में — सब callers एक ही task का इंतज़ार करते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # async
import time  # clock
from typing import Any, Awaitable, Callable  # type hints

class CachedFetcher:
    def __init__(self, fetch: Callable[[str], Awaitable[Any]], ttl: float = 60, clock=time.monotonic) -> None:
        self.fetch, self.ttl, self.clock = fetch, ttl, clock  # config
        self._cache: dict[str, tuple[Any, float]] = {}  # url -> (data, expires)
        self._inflight: dict[str, asyncio.Task] = {}  # url -> running task

    async def get(self, url: str) -> Any:
        hit = self._cache.get(url)  # check cache
        if hit and hit[1] > self.clock():
            return hit[0]  # fresh -> no network
        if url not in self._inflight:  # nobody fetching yet
            self._inflight[url] = asyncio.create_task(self._load(url))  # start one fetch
        return await self._inflight[url]  # everyone shares the same task

    async def _load(self, url: str) -> Any:
        try:
            data = await self.fetch(url)  # real fetch
            self._cache[url] = (data, self.clock() + self.ttl)  # store
            return data  # result
        finally:
            self._inflight.pop(url, None)  # clear in-flight marker

# ============================================
# TEST CASES
# ============================================
network_calls = 0  # count real fetches
async def fake_fetch(url: str) -> dict:
    global network_calls
    network_calls += 1  # count
    await asyncio.sleep(0.02)  # simulated latency
    return {"url": url, "n": network_calls}  # fake response

async def main() -> None:
    t = [0.0]  # fake time
    f = CachedFetcher(fake_fetch, ttl=10, clock=lambda: t[0])  # fetcher
    r = await asyncio.gather(*(f.get("/a") for _ in range(5)))  # 5 concurrent same-url calls
    print(network_calls, r[0] == r[4])  # Expected: 1 True
    print(await f.get("/a"), network_calls)  # Expected: {'url': '/a', 'n': 1} 1   (cache hit)
    t[0] = 11  # expire
    print(await f.get("/a"), network_calls)  # Expected: {'url': '/a', 'n': 2} 2   (refetch)
asyncio.run(main())
```

---

## 🔍 Why This Works (3 lines max)
There is no `await` between checking `_inflight` and inserting the task, so asyncio's single thread makes it race-free. All waiters await the same Task and get the same result; `finally` clears the marker so failures can be retried.
हिंदी: Check और insert के बीच `await` नहीं है, इसलिए race नहीं होता; सब callers एक ही Task से result लेते हैं।

---

## ⚡ Alternative Solution
```python
import asyncio  # async
from functools import lru_cache  # sync cache

calls = 0  # counter
@lru_cache(maxsize=128)  # simple memo for a SYNC fetch
def fetch_user(uid: int) -> dict:
    global calls
    calls += 1  # real call
    return {"id": uid}  # fake data

print(fetch_user(1), fetch_user(1), calls)  # Expected: {'id': 1} {'id': 1} 1
print(fetch_user.cache_info())  # Expected: CacheInfo(hits=1, misses=1, maxsize=128, currsize=1)
fetch_user.cache_clear()  # manual invalidation
# Async: cache the *task* so concurrent callers share one request
_tasks: dict[int, asyncio.Task] = {}
async def aget(uid: int) -> dict:
    async def _f():
        await asyncio.sleep(0.01)  # I/O
        return {"id": uid}
    if uid not in _tasks:
        _tasks[uid] = asyncio.ensure_future(_f())  # store task, not result
    return await _tasks[uid]
async def main():
    a, b = await asyncio.gather(aget(7), aget(7))  # one underlying task
    print(a is b)  # Expected: True
asyncio.run(main())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: @lru_cache on an async def caches the COROUTINE object; awaiting it twice raises (not run)
# @lru_cache
# async def fetch(url): ...
# await fetch("/a"); await fetch("/a")   # RuntimeError: cannot reuse already awaited coroutine

# ✅ Correct: cache the result (with TTL) and/or the Task, as in CachedFetcher
```

---

## 🎯 Interview Tip (1 line)
Say: "Cache plus request coalescing (single-flight) prevents cache stampedes; mention TTL, invalidation and not caching errors."

---

## 🔗 Related Questions
→ Q185 (cache with TTL) | Q215 (memoize async function) | Q218 (cache API responses) | Q278 (lru_cache)
