---

# Q094. Implement Any (First Success)
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `any_success(*aws)` that returns the result of the **first awaitable that succeeds**, ignoring failures. If **all** fail, raise an `AggregateError` containing every error. Cancel the leftovers. Like `Promise.any`.

---

## 💡 Quick Concept (2 lines only)
Iterate with `asyncio.as_completed` (finish order): return the first success, collect failures, and raise an aggregate error only if the loop ends.
हिंदी: Any पहली सफल task का result देता है — सब fail हों तभी error raise होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # concurrency
from typing import Any, Awaitable  # type hints


class AggregateError(Exception):  # holds all the failures
    def __init__(self, errors: list[BaseException]) -> None:
        super().__init__(f"All {len(errors)} awaitables failed")  # message
        self.errors = errors  # keep the individual errors


async def any_success(*aws: Awaitable) -> Any:
    tasks = [asyncio.ensure_future(a) for a in aws]  # Step 1: start everything
    errors: list[BaseException] = []  # Step 2: failures so far
    try:
        for fut in asyncio.as_completed(tasks):  # Step 3: yields in finish order
            try:
                return await fut  # first success wins
            except Exception as e:
                errors.append(e)  # failure -> keep waiting
        raise AggregateError(errors)  # Step 4: everyone failed (or no input)
    finally:
        for t in tasks:
            t.cancel()  # Step 5: cancel leftovers
        await asyncio.gather(*tasks, return_exceptions=True)  # drain them


# ============================================
# TEST CASES
# ============================================
async def job(name: str, delay: float, fail: bool = False) -> str:  # simulated I/O
    await asyncio.sleep(delay)  # pretend work
    if fail:
        raise ValueError(f"{name} failed")  # simulated error
    return name  # result


async def main() -> None:
    print(await any_success(job("a", 0.05, True), job("b", 0.2), job("c", 0.3)))  # Expected: b
    try:
        await any_success(job("x", 0.05, True), job("y", 0.1, True))
    except AggregateError as e:
        print(e, [str(x) for x in e.errors])  # Expected: All 2 awaitables failed ['x failed', 'y failed']
    try:
        await any_success()  # no input at all
    except AggregateError as e:
        print(e)  # Expected: All 0 awaitables failed


asyncio.run(main())
```

---

## 🔍 Why This Works (3 lines max)
`as_completed` hands back futures as they finish, so a fast failure doesn't block a slower success. Only when the loop ends without a return do we know every task failed.
हिंदी: तेज़ failure धीमे success को नहीं रोकता — सब fail हों तभी aggregate error।

---

## ⚡ Alternative Solution
```python
async def any2(*aws):  # asyncio.wait loop + built-in ExceptionGroup (3.11+)
    pending = {asyncio.ensure_future(a) for a in aws}  # set of running tasks
    errors = []  # collected errors
    try:
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)  # next finisher(s)
            for d in done:
                if d.exception() is None:  # success?
                    return d.result()  # return it
                errors.append(d.exception())  # else remember the error
        raise ExceptionGroup("all failed", errors)  # all failed
    finally:
        for p in pending:
            p.cancel()  # cleanup


async def m2():
    print(await any2(job("a", 0.05, True), job("b", 0.1)))  # Expected: b
    try:
        await any2(job("x", 0.05, True), job("y", 0.1, True))
    except* ValueError as eg:
        print(len(eg.exceptions))  # Expected: 2


asyncio.run(m2())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using gather/race — the first FAILURE ends everything
# winner = await race(job("a", 0.05, True), job("b", 0.2))   # raises 'a failed'

# ❌ Also wrong: returning None when all fail (hides the problem)
# ✅ Correct: skip failures, raise an aggregate error only when all fail
```

---

## 🎯 Interview Tip (1 line)
Say: "race returns the first to *finish*, any returns the first to *succeed* — and when all fail I surface every error via an aggregate/ExceptionGroup."

---

## 🔗 Related Questions
→ Q092 (race) | Q091 (gather) | Q093 (all-settled) | Q212 (race with fallback) | Q260 (exception groups)
