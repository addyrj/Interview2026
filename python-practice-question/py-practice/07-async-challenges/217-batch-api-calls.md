---

# Q217. Batch API calls
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
You have 7 ids to fetch from an API that tolerates only 3 parallel requests. Write `batch_calls(items, fetch, batch_size)` that runs each batch in parallel, batches one after another, and keeps the result order.

```python
await batch_calls(list(range(1, 8)), fetch, batch_size=3)
```

---

## 💡 Quick Concept (2 lines only)
Slice the list into chunks; `asyncio.gather` each chunk (parallel inside), loop over chunks (sequential between).
हिंदी: List को chunks में बाँटो; chunk के अंदर gather (parallel), chunks के बीच await (sequential)।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
from collections.abc import Awaitable, Callable   # type hints
from typing import Any                            # generic


async def batch_calls(
    items: list[int],                             # all ids to fetch
    fetch: Callable[[int], Awaitable[Any]],       # async call for one id
    batch_size: int = 3,                          # max parallel calls at a time
) -> list[Any]:
    results: list[Any] = []                       # keeps original order
    for i in range(0, len(items), batch_size):    # walk in slices of batch_size
        chunk = items[i : i + batch_size]         # current batch
        results += await asyncio.gather(*(fetch(x) for x in chunk))  # batch runs in parallel
    return results                                # batches ran one after another


# ---------- TEST CASES ----------
active = 0                                        # currently running calls
peak = 0                                          # max concurrency seen


async def fetch(x: int) -> int:
    global active, peak                           # shared counters
    active += 1                                   # call started
    peak = max(peak, active)                      # record peak
    await asyncio.sleep(0.05)                     # simulated API latency
    active -= 1                                   # call finished
    return x * 10                                 # fake response


async def main() -> None:
    res = await batch_calls(list(range(1, 8)), fetch, batch_size=3)  # 7 ids -> 3 batches
    print(res)                                    # order preserved
    print("peak concurrency:", peak)              # never above 3


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# [10, 20, 30, 40, 50, 60, 70]
# peak concurrency: 3
```

---

## 🔍 Why This Works (3 lines max)
Slicing with `range(0, n, size)` gives fixed batches. `gather` returns results in input order, so order is preserved. The measured peak concurrency is 3, never more. A `Semaphore` gives a sliding window with no idle gaps.
हिंदी: gather result का order input जैसा ही रखता है; peak concurrency हमेशा batch_size तक रहती है।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library
from itertools import batched                     # Python 3.12+ helper


async def fetch(x: int) -> int:
    await asyncio.sleep(0.01)                     # simulated latency
    return x + 100                                # fake response


async def main() -> None:
    out: list[int] = []                           # results in order
    for chunk in batched(range(1, 8), 3):         # tuples of up to 3 items
        async with asyncio.TaskGroup() as tg:     # structured concurrency (3.11+)
            tasks = [tg.create_task(fetch(x)) for x in chunk]  # run the chunk in parallel
        out += [t.result() for t in tasks]        # all done when the block exits
    print(out)                                    # [101 ... 107]

    sem = asyncio.Semaphore(3)                    # alternative: sliding window, not fixed batches

    async def limited(x: int) -> int:
        async with sem:                           # at most 3 inside at once
            return await fetch(x)                 # do the call

    print(await asyncio.gather(*(limited(x) for x in range(1, 8))))  # same output, no idle gaps


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# [101, 102, 103, 104, 105, 106, 107]
# [101, 102, 103, 104, 105, 106, 107]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: gather everything at once - 1000 ids = 1000 parallel requests (rate-limit / 429)
results = await asyncio.gather(*(fetch(x) for x in all_ids))

# ❌ Wrong: awaiting one by one - safe but slow (N x latency)
# ✅ Correct: bounded batches (or Semaphore)
```

---

## 🎯 Interview Tip (1 line)
Say: "Batching/Semaphore bounds concurrency; Semaphore is a sliding window, fixed batches wait for the slowest item."

---

## 🔗 Related Questions
→ Q202 (parallel) | Q203 (Semaphore) | Q210 (async map with limit) | Q060 (chunk list)
