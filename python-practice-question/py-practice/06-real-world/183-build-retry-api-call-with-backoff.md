---

# Q183. Build Retry API Call with Backoff
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build an async `retry(fn, retries, base)` helper that calls a flaky API. On failure it waits `base * 2**attempt` seconds (exponential backoff) and tries again. After the last retry fails, it must re-raise the original error.

```python
await retry(call_api, retries=3, base=0.1)  # waits 0.1s, 0.2s, 0.4s between attempts
```

---

## 💡 Quick Concept (2 lines only)
Backoff = wait longer after each failure so a struggling server can recover. Always cap the retries and re-raise the last error.
हिंदी: हर failure के बाद ज़्यादा इंतज़ार करो (0.1, 0.2, 0.4...) और आखिर में error वापस raise करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # async tools
from typing import Awaitable, Callable, TypeVar  # type hints

T = TypeVar("T")  # generic return type

# Step 1: sleep is injectable so tests don't really wait
async def retry(fn: Callable[[], Awaitable[T]], retries: int = 3, base: float = 0.1,
                sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> T:
    for attempt in range(retries + 1):  # first try + `retries` retries
        try:  # attempt the call
            return await fn()  # success -> return result
        except Exception:  # any failure
            if attempt == retries:  # no retries left
                raise  # surface the last error
            await sleep(base * 2 ** attempt)  # exponential backoff: 0.1, 0.2, 0.4

# ============================================
# TEST CASES
# ============================================
calls = {"n": 0}  # counts attempts
async def flaky() -> str:
    calls["n"] += 1  # count attempt
    if calls["n"] < 3:  # fail first two times
        raise ConnectionError("boom")  # simulated network error
    return "ok"  # third try works

async def always_fail() -> str:
    raise TimeoutError("down")  # never succeeds

async def main() -> None:
    delays: list[float] = []  # record backoff delays
    async def fake_sleep(d: float) -> None:
        delays.append(d)  # record instead of waiting
    print(await retry(flaky, 3, 0.1, fake_sleep), calls["n"], delays)  # Expected: ok 3 [0.1, 0.2]
    delays.clear()  # reset
    try:
        await retry(always_fail, 2, 0.1, fake_sleep)  # exhausts retries
    except TimeoutError as e:
        print("failed:", e, delays)  # Expected: failed: down [0.1, 0.2]
asyncio.run(main())  # run
```

---

## 🔍 Why This Works (3 lines max)
The loop runs `retries + 1` times; the `try` returns on success, otherwise sleeps `base * 2**attempt`. On the final attempt a bare `raise` re-throws the original exception with its traceback.
हिंदी: Loop retries+1 बार चलता है; आखिरी attempt पर bare `raise` original error फेंक देता है।

---

## ⚡ Alternative Solution
```python
import asyncio  # async tools
import random  # jitter
from functools import wraps  # keep metadata

def retry(retries: int = 3, base: float = 0.01, jitter: bool = True):  # decorator factory
    def deco(fn):
        @wraps(fn)  # keep name/doc
        async def wrapper(*a, **kw):
            for i in range(retries + 1):  # attempts
                try:
                    return await fn(*a, **kw)  # try call
                except Exception:
                    if i == retries:  # last attempt
                        raise  # give up
                    delay = base * 2 ** i  # exponential
                    if jitter:
                        delay = random.uniform(0, delay)  # full jitter avoids thundering herd
                    await asyncio.sleep(delay)  # wait
        return wrapper
    return deco

n = 0  # attempt counter
@retry(retries=3, base=0.01)
async def get() -> str:
    global n
    n += 1  # count
    if n < 3:
        raise OSError("flaky")  # fail twice
    return f"done after {n}"  # success

print(asyncio.run(get()), get.__name__)  # Expected: done after 3 get
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: bare except swallows Ctrl+C / CancelledError, no jitter, fixed delay, error lost (not run)
# async def retry(fn):
#     for _ in range(3):
#         try:
#             return await fn()
#         except:             # catches KeyboardInterrupt + asyncio.CancelledError too!
#             await asyncio.sleep(1)
#     return None             # caller never learns it failed

# ✅ Correct: catch Exception (not BaseException), exponential delay, re-raise on last attempt
# Also: only retry transient errors (timeouts, 5xx) — never 4xx like 400/404.
```

---

## 🎯 Interview Tip (1 line)
Say: "Exponential backoff + jitter, capped retries, only retry idempotent/transient failures, and re-raise the last error."

---

## 🔗 Related Questions
→ Q089 (retry decorator) | Q157 (complete retry logic) | Q204 (retry a failed coroutine) | Q205 (timeout a coroutine)
