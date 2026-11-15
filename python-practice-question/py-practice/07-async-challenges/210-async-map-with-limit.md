---

# Q210. Async map with limit
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `async_map(fn, items, limit)` that applies an async function to every item with at most `limit` running at once, and returns results in the original order.

---

## 💡 Quick Concept (2 lines only)
Wrap each call in `async with sem:` (Semaphore) and `gather` them — gather keeps input order regardless of finish order.
हिंदी: Semaphore से concurrency सीमित करो और `gather` से result का order input जैसा रखो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # asyncio
from collections.abc import Awaitable, Callable, Iterable  # types

async def async_map[T, R](fn: Callable[[T], Awaitable[R]], items: Iterable[T], limit: int = 3) -> list[R]:
    sem = asyncio.Semaphore(limit)                   # cap concurrency

    async def run(item: T) -> R:
        async with sem:                              # wait for a free slot
            return await fn(item)                    # run the real work

    return await asyncio.gather(*(run(i) for i in items))  # gather keeps input order

active = peak = 0                                    # concurrency tracking

async def slow_square(n: int) -> int:
    global active, peak                              # shared counters
    active += 1; peak = max(peak, active)            # entering
    await asyncio.sleep(0.05 - n * 0.002)            # later items finish sooner
    active -= 1                                      # leaving
    return n * n

async def main() -> None:
    print(await async_map(slow_square, range(8), limit=3))  # Expected: [0, 1, 4, 9, 16, 25, 36, 49]
    print("peak:", peak)                             # Expected: peak: 3

asyncio.run(main())

# --- Real output (Python 3.13) ---
# [0, 1, 4, 9, 16, 25, 36, 49]
# peak: 3
```

---

## 🔍 Why This Works (3 lines max)
All items become tasks immediately but only `limit` can enter the semaphore. Items later in the list finish faster in the demo, yet results are still in input order. `peak` proves the cap (3).
हिंदी: कई tasks बनते हैं पर अंदर सिर्फ `limit` चलते हैं; order फिर भी सही रहता है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: TaskGroup + Semaphore (cancels everything if one item fails)
# ============================================
import asyncio                                       # asyncio

async def double(n: int) -> int:
    await asyncio.sleep(0.01)                        # simulated I/O
    return n * 2

async def main() -> None:
    sem = asyncio.Semaphore(2)                       # 2 at a time
    async def run(n: int) -> int:
        async with sem:                              # limit
            return await double(n)

    async with asyncio.TaskGroup() as tg:            # structured concurrency
        tasks = [tg.create_task(run(n)) for n in range(5)]
    print([t.result() for t in tasks])               # Expected: [0, 2, 4, 6, 8]

asyncio.run(main())

# --- Real output (Python 3.13) ---
# [0, 2, 4, 6, 8]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: awaiting inside the comprehension — everything runs one by one, limit is pointless
out = [await run(n) for n in range(6)]   # measured ~0.31s (real run) vs ~0.15s with gather

# ✅ Correct: build all awaitables first, then await them together
out = await asyncio.gather(*(run(n) for n in range(6)))
```

---

## 🎯 Interview Tip (1 line)
Say: "For huge inputs, creating a task per item is wasteful — I'd use a fixed worker pool with a Queue instead."

---

## 🔗 Related Questions
→ Q203 (semaphore) | Q095 (worker pool) | Q202 (parallel) | Q217 (batch API calls)
