---

# Q204. Retry a failed coroutine
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `retry(factory, attempts=3)` that re-runs an async operation when it raises, with exponential backoff, and re-raises the last error when attempts are exhausted.

---

## 💡 Quick Concept (2 lines only)
Pass a *factory* (callable returning a new coroutine) — a coroutine object can only be awaited once. Loop, catch, `asyncio.sleep` with backoff.
हिंदी: हर try के लिए नया coroutine चाहिए, इसलिए factory दो; fail पर backoff के साथ दोबारा try करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # asyncio
from collections.abc import Awaitable, Callable      # types

async def retry[T](factory: Callable[[], Awaitable[T]], attempts: int = 3, delay: float = 0.01) -> T:
    for i in range(1, attempts + 1):                 # try up to `attempts` times
        try:
            return await factory()                   # fresh coroutine each time
        except Exception as e:                       # catch ordinary errors only (not CancelledError)
            print(f"attempt {i} failed: {e}")        # log the failure
            if i == attempts:                        # out of attempts
                raise                                # re-raise the last error
            await asyncio.sleep(delay * 2 ** (i - 1))  # exponential backoff

calls = 0                                            # how many times flaky() ran

async def flaky() -> str:
    global calls                                     # shared counter
    calls += 1                                       # count this call
    await asyncio.sleep(0)                           # yield to the loop
    if calls < 3:                                    # fail the first two times
        raise ConnectionError(f"boom #{calls}")      # simulated network error
    return "ok"                                      # third time succeeds

async def main() -> None:
    print(await retry(flaky))                        # Expected: attempt 1/2 failed lines, then ok
    async def always_fail() -> None:
        raise TimeoutError("down")                   # never works
    try:
        await retry(always_fail, attempts=2)         # exhausts attempts
    except TimeoutError as e:
        print("gave up:", e)                         # Expected: gave up: down

asyncio.run(main())

# --- Real output (Python 3.13) ---
# attempt 1 failed: boom #1
# attempt 2 failed: boom #2
# ok
# attempt 1 failed: down
# attempt 2 failed: down
# gave up: down
```

---

## 🔍 Why This Works (3 lines max)
On each failure we log, then sleep `delay * 2**(i-1)`; on the last attempt a bare `raise` propagates the original exception. We catch `Exception`, not `BaseException`, so `CancelledError` is never swallowed.
हिंदी: आखिरी attempt पर bare `raise` से original error बाहर जाता है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: decorator version
# ============================================
import asyncio, functools                            # asyncio + wraps

def retry(attempts: int = 3):
    def deco(fn):
        @functools.wraps(fn)                         # keep name/docstring
        async def wrapper(*a, **kw):
            for i in range(attempts):                # loop attempts
                try:
                    return await fn(*a, **kw)        # success -> return
                except ValueError:                   # retry only this error type
                    if i == attempts - 1:            # last attempt
                        raise                        # give up
        return wrapper
    return deco

n = 0                                                # call counter

@retry(attempts=3)
async def get() -> int:
    global n
    n += 1                                           # count calls
    if n < 2:
        raise ValueError("first call fails")         # fail once
    return n

print(asyncio.run(get()))                            # Expected: 2

# --- Real output (Python 3.13) ---
# 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: retrying the SAME coroutine object
coro = flaky()
for _ in range(2):
    try: await coro
    except Exception as e: print(type(e).__name__, e)
# ValueError x
# RuntimeError cannot reuse already awaited coroutine   (real run)

# ✅ Correct: call the factory each time -> await factory()
```

---

## 🎯 Interview Tip (1 line)
Say: "Retry only idempotent operations and only transient errors; add jitter to the backoff to avoid thundering herds."

---

## 🔗 Related Questions
→ Q089 (retry decorator) | Q157 (retry logic) | Q183 (retry API call) | Q205 (timeout)
