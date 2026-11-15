---

# Q212. Race with fallback
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
A primary API is sometimes slow or down. Write `with_fallback(primary, fallback, timeout)` that returns the primary result if it answers in time, otherwise uses the fallback.

```python
await with_fallback(primary_api, cache_lookup, timeout=0.5)
```

---

## 💡 Quick Concept (2 lines only)
`asyncio.wait_for` cancels the primary after the timeout; catch `TimeoutError` (and real errors) and call the fallback. A hedged request instead races both.
हिंदी: Primary को timeout दो; slow या fail हो तो fallback चलाओ — दोनों को race भी करा सकते हो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
from collections.abc import Awaitable, Callable   # type hints

Fetcher = Callable[[], Awaitable[str]]            # zero-arg async function


async def with_fallback(primary: Fetcher, fallback: Fetcher, timeout: float) -> str:
    try:
        return await asyncio.wait_for(primary(), timeout)  # give primary `timeout` seconds
    except (asyncio.TimeoutError, ConnectionError):         # slow OR failed primary
        return await fallback()                             # use the fallback instead


# ---------- TEST CASES ----------
async def slow_primary() -> str:
    await asyncio.sleep(1)                        # too slow
    return "primary"                              # never reached in time


async def fast_primary() -> str:
    await asyncio.sleep(0.01)                     # quick
    return "primary"


async def broken_primary() -> str:
    raise ConnectionError("down")                 # primary is down


async def fallback() -> str:
    await asyncio.sleep(0.01)                     # cache/replica is quick
    return "fallback"


async def main() -> None:
    print(await with_fallback(fast_primary, fallback, 0.1))    # primary wins
    print(await with_fallback(slow_primary, fallback, 0.1))    # timeout -> fallback
    print(await with_fallback(broken_primary, fallback, 0.1))  # error -> fallback


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# primary
# fallback
# fallback
```

---

## 🔍 Why This Works (3 lines max)
`wait_for` raises `TimeoutError` and cancels the slow coroutine, so no work is leaked. The alternative "hedging" starts the fallback only after a short delay and cancels whichever task loses.
हिंदी: wait_for timeout पर slow call cancel कर देता है, फिर except में fallback call होता है।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library


async def hedged(primary, fallback, hedge_after: float) -> str:
    p = asyncio.create_task(primary())            # start primary immediately
    done, _ = await asyncio.wait({p}, timeout=hedge_after)  # wait a short while
    if done:                                      # primary finished in time
        return p.result()                         # use its result
    f = asyncio.create_task(fallback())           # otherwise start fallback too
    done, pending = await asyncio.wait({p, f}, return_when=asyncio.FIRST_COMPLETED)  # race both
    for t in pending:                             # cancel the loser
        t.cancel()                                # stop wasting work
    return done.pop().result()                    # first finisher wins


async def slow() -> str:
    await asyncio.sleep(0.3)                      # slow one
    return "slow"


async def quick() -> str:
    await asyncio.sleep(0.05)                     # quick one
    return "quick"


async def main() -> None:
    print(await hedged(slow, quick, 0.1))         # fallback starts at 0.1s, finishes at 0.15s
    print(await hedged(quick, slow, 0.1))         # primary finishes before hedge


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# quick
# quick
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no timeout - a hanging primary blocks the user forever
result = await primary()

# ❌ Wrong: bare except hides real bugs (and can swallow CancelledError in old code)
try:
    result = await asyncio.wait_for(primary(), 0.1)
except:                               # catches EVERYTHING
    result = await fallback()

# ✅ Correct: catch only what you expect
except (TimeoutError, ConnectionError):
    result = await fallback()
```

---

## 🎯 Interview Tip (1 line)
Say: "Timeout + fallback for graceful degradation; hedged requests trade extra load for lower tail latency."

---

## 🔗 Related Questions
→ Q205 (timeout a coroutine) | Q092 (race / first completed) | Q094 (any - first success) | Q204 (retry)
