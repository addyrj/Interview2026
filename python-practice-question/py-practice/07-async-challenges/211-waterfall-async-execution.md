---

# Q211. Waterfall async execution
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `waterfall(steps, initial)` that runs async (or sync) steps one after another, passing each result into the next step, and returns the last result.

```python
await waterfall([get_user, get_orders, total])   # get_orders(user), total(orders)
```

---

## 💡 Quick Concept (2 lines only)
Waterfall = sequential chain where step N needs the output of step N-1, so you must `await` each step before calling the next.
हिंदी: Waterfall में हर step पिछले step का result लेता है — इसलिए हर step को await करके ही आगे बढ़ो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
import inspect                                    # to detect awaitable results
from collections.abc import Awaitable, Callable   # type hints for callables
from typing import Any                            # generic value type

Step = Callable[[Any], Any]                       # a step takes previous result, returns value/awaitable


async def waterfall(steps: list[Step], initial: Any = None) -> Any:
    result = initial                              # start with the seed value
    for step in steps:                            # run steps strictly one after another
        result = step(result)                     # call step with previous result
        if inspect.isawaitable(result):           # step may be sync OR async
            result = await result                 # wait for it before moving on
    return result                                 # final output of the last step


# ---------- TEST CASES ----------
async def get_user(_: Any) -> dict:               # step 1: fetch user
    await asyncio.sleep(0.01)                     # simulated network I/O
    return {"id": 1, "name": "Aditya"}            # return user dict


async def get_orders(user: dict) -> list[int]:    # step 2: needs user from step 1
    await asyncio.sleep(0.01)                     # simulated network I/O
    return [user["id"] * 10, user["id"] * 20]     # fake order ids


def total(orders: list[int]) -> int:              # step 3: plain sync function
    return sum(orders)                            # sum order ids


async def main() -> None:
    print(await waterfall([get_user, get_orders, total]))  # chain of 3 steps
    print(await waterfall([lambda x: x + 1, lambda x: x * 2], 5))  # sync-only steps
    print(await waterfall([], "seed"))            # no steps -> seed returned


asyncio.run(main())                               # run the demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# 30
# 12
# seed
```

---

## 🔍 Why This Works (3 lines max)
A plain `for` loop with `await` inside keeps order strict. `inspect.isawaitable` lets sync and async steps mix. Do NOT use `gather` here — it would start everything at once and the data dependency breaks.
हिंदी: for loop + await = एक के बाद एक; gather यहाँ गलत है क्योंकि अगला step पिछले result पर depend करता है।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library
from functools import reduce                      # fold helper


async def waterfall(steps, initial=None):
    async def apply(acc_coro, step):              # fold one step onto the accumulator
        acc = await acc_coro                      # wait for previous result
        out = step(acc)                           # call next step
        return await out if asyncio.iscoroutine(out) else out  # await only if coroutine

    async def seed():                             # wrap initial value as a coroutine
        return initial                            # just return the seed

    return await reduce(apply, steps, seed())     # reduce chains coroutines left to right


async def add_one(x):                             # async step
    await asyncio.sleep(0.01)                     # simulated I/O
    return x + 1                                  # +1


async def main() -> None:
    print(await waterfall([add_one, add_one, lambda x: x * 10], 0))  # (0+1+1)*10


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# 20
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: gather runs all steps at the same time with the same input
results = await asyncio.gather(get_user(None), get_orders(None))  # get_orders never sees the user!

# ✅ Correct: sequential loop, each result feeds the next step
result = initial                      # seed
for step in steps:                    # one by one
    result = await step(result)       # wait, then pass forward
```

---

## 🎯 Interview Tip (1 line)
Say: "Dependent steps run sequentially (await in a loop); independent steps run concurrently (gather) — waterfall is the sequential case."

---

## 🔗 Related Questions
→ Q201 (sequential coroutines) | Q202 (parallel) | Q207 (chain async ops) | Q209 (async reduce)
