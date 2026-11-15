---

# Q215. Memoize an async function
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Write `@async_memoize` for coroutine functions so repeated calls with the same arguments reuse the result. Concurrent calls with the same key must trigger only ONE real call.

```python
@async_memoize
async def fetch_user(uid): ...
```

---

## 💡 Quick Concept (2 lines only)
Cache the `Task` (not the coroutine object, not just the result) - then concurrent callers await the same task and finished calls return instantly.
हिंदी: Result नहीं, Task को cache करो — तब एक साथ आने वाले callers भी एक ही call share करते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
import functools                                  # wraps
from collections.abc import Awaitable, Callable   # type hints
from typing import Any                            # generic


def async_memoize(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    cache: dict[tuple, asyncio.Task] = {}         # key -> Task (NOT the raw result)

    @functools.wraps(fn)                          # keep metadata
    async def wrapper(*args: Any) -> Any:
        if args not in cache:                     # first time we see these args
            cache[args] = asyncio.ensure_future(fn(*args))  # start once, store the task
        return await cache[args]                  # concurrent callers share the same task

    wrapper.cache = cache                         # expose for inspection/tests
    return wrapper


# ---------- TEST CASES ----------
hits = 0                                          # counts real calls


@async_memoize
async def fetch_user(uid: int) -> dict:
    global hits                                   # update counter
    hits += 1                                     # real call happened
    await asyncio.sleep(0.05)                     # simulated network
    return {"id": uid}                            # fake user


async def main() -> None:
    r = await asyncio.gather(fetch_user(1), fetch_user(1), fetch_user(1))  # concurrent, same key
    print(r, "hits =", hits)                      # only ONE real call
    await fetch_user(1)                           # later call -> cached
    await fetch_user(2)                           # new key -> real call
    print("hits =", hits)                         # 2


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# [{'id': 1}, {'id': 1}, {'id': 1}] hits = 1
# hits = 2
```

---

## 🔍 Why This Works (3 lines max)
`functools.lru_cache` on an `async def` caches the coroutine object, which can only be awaited once. Storing `asyncio.ensure_future(fn(...))` gives a reusable awaitable. The alternative also evicts failed tasks so errors are not cached forever.
हिंदी: lru_cache coroutine object cache करता है जो दोबारा await नहीं हो सकता — इसलिए Task cache करो।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library
import functools                                  # wraps


def async_memoize(fn):
    cache: dict[tuple, asyncio.Task] = {}         # key -> task

    @functools.wraps(fn)                          # keep metadata
    async def wrapper(*args):
        task = cache.get(args)                    # look up existing task
        if task is None:                          # miss
            task = cache[args] = asyncio.ensure_future(fn(*args))  # start + store
        try:
            return await task                     # wait for result
        except Exception:
            cache.pop(args, None)                 # do NOT cache failures
            raise                                 # re-raise to the caller

    return wrapper


attempts = 0                                      # call counter


@async_memoize
async def flaky(x: int) -> int:
    global attempts                               # update counter
    attempts += 1                                 # count real calls
    await asyncio.sleep(0.01)                     # simulated I/O
    if attempts == 1:                             # first call fails
        raise RuntimeError("boom")                # transient error
    return x * 2                                  # later calls succeed


async def main() -> None:
    try:
        await flaky(5)                            # fails
    except RuntimeError as e:
        print("first:", e)                        # boom
    print("second:", await flaky(5))              # retried (failure not cached)
    print("third:", await flaky(5), "attempts =", attempts)  # now cached


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# first: boom
# second: 10
# third: 10 attempts = 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: lru_cache on a coroutine function (real run, Python 3.13)
from functools import lru_cache

@lru_cache
async def get(x): return x

await get(1)    # 1
await get(1)    # RuntimeError: cannot reuse already awaited coroutine

# ✅ Correct: cache asyncio Tasks (see solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "Cache the in-flight Task so concurrent callers dedupe (request coalescing), and do not cache exceptions."

---

## 🔗 Related Questions
→ Q083 (memoize) | Q143 (complete memoize) | Q218 (cache API responses) | Q278 (lru_cache)
