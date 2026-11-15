---

# Q201. Run coroutines sequentially
# Category: ASYNC CHALLENGES
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `run_sequential(*coros)` that runs coroutines one after another and returns results in order. Show that total time is the sum of the delays.

---

## 💡 Quick Concept (2 lines only)
`await` inside a loop runs one coroutine at a time — needed when step N depends on step N-1 or order of side effects matters.
हिंदी: Loop में `await` करने से coroutines एक के बाद एक चलते हैं — total time = सबका जोड़।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # event loop + sleep
import time                                          # to measure elapsed time

async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)                       # simulated I/O
    return f"{name} done"                            # result

async def run_sequential(*coros) -> list[str]:
    results: list[str] = []                          # collect in order
    for coro in coros:                               # one at a time
        results.append(await coro)                   # wait for it before starting next
    return results                                   # ordered results

async def main() -> None:
    start = time.perf_counter()                      # start timer
    res = await run_sequential(fetch("A", 0.2), fetch("B", 0.1), fetch("C", 0.1))
    print(res)                                       # Expected: ['A done', 'B done', 'C done']
    print(f"{time.perf_counter() - start:.1f}s")     # Expected: ~0.4s (0.2+0.1+0.1; varies slightly)

asyncio.run(main())                                  # run the program

# --- Real output (Python 3.13) ---
# ['A done', 'B done', 'C done']
# 0.4s
```

---

## 🔍 Why This Works (3 lines max)
Each `await coro` suspends the caller until that coroutine finishes, so the next one doesn't start until then. 0.2 + 0.1 + 0.1 = ~0.4s. Note: coroutine objects created up-front don't start running until awaited.
हिंदी: हर `await` पूरा होने तक रुकता है, इसलिए time जुड़ता जाता है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: pass factories (lambdas) so no coroutine starts early / is left un-awaited
# ============================================
import asyncio                                       # asyncio
from collections.abc import Awaitable, Callable      # types

async def fetch(name: str, delay: float) -> str:
    await asyncio.sleep(delay)                       # simulated I/O
    return f"{name} done"                            # result

async def run_sequential(factories: list[Callable[[], Awaitable[str]]]) -> list[str]:
    return [await f() for f in factories]            # create + await each coroutine lazily

async def main() -> None:
    print(await run_sequential([lambda: fetch("A", 0.1), lambda: fetch("B", 0.05)]))
    # Expected: ['A done', 'B done']

asyncio.run(main())

# --- Real output (Python 3.13) ---
# ['A done', 'B done']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to await — coroutine never runs
async def main():
    fetch("A", 0.1)   # RuntimeWarning: coroutine 'fetch' was never awaited; no work done

# ✅ Correct
async def main():
    await fetch("A", 0.1)   # actually runs and returns the value
```

---

## 🎯 Interview Tip (1 line)
Say: "Sequential when there's a dependency; otherwise `gather` — I always ask whether the steps are independent."

---

## 🔗 Related Questions
→ Q202 (parallel) | Q207 (chain) | Q211 (waterfall) | Q123 (missing await)
