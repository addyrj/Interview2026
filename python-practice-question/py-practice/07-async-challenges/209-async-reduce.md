---

# Q209. Async reduce
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `async_reduce(fn, items, initial)` where the reducer `fn(acc, item)` is an async function. Items must be processed in order.

---

## 💡 Quick Concept (2 lines only)
Same as `functools.reduce`, but `await` the reducer in a loop — the accumulator makes it inherently sequential.
हिंदी: `reduce` जैसा ही, बस हर step में reducer को `await` करो — accumulator की वजह से order में चलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # asyncio
from collections.abc import Awaitable, Callable, Iterable  # types

async def async_reduce[T, A](
    fn: Callable[[A, T], Awaitable[A]], items: Iterable[T], initial: A
) -> A:
    acc = initial                                    # running accumulator
    for item in items:                               # strictly in order
        acc = await fn(acc, item)                    # next step needs previous result
    return acc                                       # final value

async def add_slowly(acc: int, x: int) -> int:
    await asyncio.sleep(0.01)                        # simulated I/O
    return acc + x                                   # new accumulator

async def main() -> None:
    print(await async_reduce(add_slowly, [1, 2, 3, 4], 0))   # Expected: 10
    async def join(acc: str, x: str) -> str:
        await asyncio.sleep(0)                       # yield to loop
        return acc + x                               # concatenate
    print(await async_reduce(join, "abc", ""))       # Expected: abc

asyncio.run(main())

# --- Real output (Python 3.13) ---
# 10
# abc
```

---

## 🔍 Why This Works (3 lines max)
Each step needs the previous accumulator, so the work can't be parallelised. If the per-item async work is independent, fetch everything with `gather` first and then reduce synchronously (alternative).
हिंदी: Accumulator पिछले step पर निर्भर है, इसलिए parallel नहीं हो सकता।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: fetch in parallel first, then reduce synchronously (when the fn itself is pure)
# ============================================
import asyncio                                       # asyncio
from functools import reduce                         # sync reduce

async def load(n: int) -> int:
    await asyncio.sleep(0.01)                        # simulated I/O per item
    return n * n                                     # square

async def main() -> None:
    values = await asyncio.gather(*(load(n) for n in [1, 2, 3, 4]))  # parallel I/O
    print(reduce(lambda a, b: a + b, values, 0))     # Expected: 30  (1+4+9+16)

asyncio.run(main())

# --- Real output (Python 3.13) ---
# 30
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: functools.reduce with an async function — acc becomes a coroutine object
from functools import reduce
async def add(a, b): return a + b
r = reduce(lambda a, b: add(a, b), [1, 2, 3])   # acc is a coroutine at the next step!
# not run: next iteration computes add(<coroutine>, 3) -> TypeError when finally awaited

# ✅ Correct: loop with `acc = await fn(acc, item)`
```

---

## 🎯 Interview Tip (1 line)
Say: "Reduce is sequential by nature; if only the I/O part is slow I parallelise the loading and reduce afterwards."

---

## 🔗 Related Questions
→ Q109 (implement reduce) | Q207 (chain) | Q211 (waterfall) | Q210 (async map)
