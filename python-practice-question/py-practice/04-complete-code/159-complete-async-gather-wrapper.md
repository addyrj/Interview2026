---

# Q159. Complete Async Gather Wrapper
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks (`____`) to finish `gather_limited`, which runs coroutines concurrently (max N at a time) and returns results in the SAME order as the input.

```python
import asyncio
from collections.abc import Awaitable

async def gather_limited(coros: list[Awaitable], limit: int) -> list:
    sem = asyncio.____(limit)                   # blank 1: limits concurrency

    async def run(coro: Awaitable):
        async ____ sem:                         # blank 2: acquire/release the semaphore
            return ____ coro                    # blank 3: wait for the result

    return await asyncio.____(*(run(c) for c in coros))   # blank 4: run all concurrently, keep order
```

---

## 💡 Quick Concept (2 lines only)
`asyncio.gather` runs awaitables concurrently and returns results in input order; a `Semaphore` caps how many run at once.
हिंदी: `gather` सब को एक साथ चलाता है और result उसी order में देता है; `Semaphore` एक समय में कितने चलें, यह सीमित करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                   # Step 1: event loop tools
from collections.abc import Awaitable            # Step 2: type hint

async def gather_limited(coros: list[Awaitable], limit: int) -> list:  # Step 3
    sem = asyncio.Semaphore(limit)               # Blank 1 -> Semaphore

    async def run(coro: Awaitable):              # Step 4: wrapper that respects the limit
        async with sem:                          # Blank 2 -> with (async context manager)
            return await coro                    # Blank 3 -> await

    return await asyncio.gather(*(run(c) for c in coros))   # Blank 4 -> gather (keeps order)

# ============================================
# TEST CASES
# ============================================
running = 0                                      # how many tasks run right now
peak = 0                                         # highest concurrency seen

async def job(i: int, delay: float) -> int:      # simulated I/O task
    global running, peak                         # share counters
    running += 1                                 # task started
    peak = max(peak, running)                    # track the maximum
    await asyncio.sleep(delay)                   # simulated I/O wait
    running -= 1                                 # task finished
    return i * 10                                # result depends on the input

async def main() -> None:                        # test driver
    delays = [0.03, 0.01, 0.02, 0.01, 0.01]      # different speeds: finish order != input order
    coros = [job(i, d) for i, d in enumerate(delays)]   # create coroutine objects
    results = await gather_limited(coros, limit=2)      # at most 2 at once
    print(results)                               # Expected: [0, 10, 20, 30, 40]  (input order)
    print(peak)                                  # Expected: 2  (never above the limit)

asyncio.run(main())                              # run the test
```

---

## 🔍 Why This Works (3 lines max)
Each wrapped coroutine must acquire the semaphore before running, so only `limit` of them execute at once. `gather` collects results by position, not by finish time, so order matches the input. Coroutines are lazy: nothing runs until `gather` schedules them.
हिंदी: Semaphore एक साथ चलने वाले tasks की संख्या रोकता है, और `gather` result को input की position से लौटाता है।

---

## ⚡ Alternative Solution
```python
# Python 3.11+: asyncio.TaskGroup (structured concurrency) keeps order via task objects
import asyncio                                    # event loop

async def gather_tg(coros: list, limit: int) -> list:   # TaskGroup version
    sem = asyncio.Semaphore(limit)                # cap concurrency

    async def run(c):                             # limited runner
        async with sem:                           # acquire a slot
            return await c                        # run the coroutine

    async with asyncio.TaskGroup() as tg:         # waits for all tasks; cancels siblings on error
        tasks = [tg.create_task(run(c)) for c in coros]   # start all tasks
    return [t.result() for t in tasks]            # read results in input order

async def work(x: int) -> int:                    # simulated I/O
    await asyncio.sleep(0.01)                     # pretend to wait
    return x * x                                  # compute

print(asyncio.run(gather_tg([work(i) for i in range(5)], 2)))   # Expected: [0, 1, 4, 9, 16]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: awaiting in a loop = sequential, not concurrent
async def bad(coros):
    return [await c for c in coros]           # one at a time: total time = sum of delays

# ✅ Correct: schedule them all, then gather
#     return await asyncio.gather(*coros)
```

---

## 🎯 Interview Tip (1 line)
Say: "gather preserves input order, `return_exceptions=True` stops one failure from hiding the others, and a Semaphore adds a concurrency cap."

---

## 🔗 Related Questions
→ Q091 (implement gather) | Q095 (worker pool) | Q202 (parallel coroutines) | Q203 (Semaphore) | Q208 (gather / TaskGroup errors)
