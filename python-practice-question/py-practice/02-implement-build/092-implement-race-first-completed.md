---

# Q092. Implement Race (First Completed)
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `race(*aws)` that returns the result (or raises the error) of whichever awaitable finishes **first**, and **cancels the losers**. Like `Promise.race`.

```python
await race(job("slow", 0.3), job("fast", 0.1), job("mid", 0.2))  # 'fast'
```

---

## 💡 Quick Concept (2 lines only)
`asyncio.wait(..., return_when=FIRST_COMPLETED)` returns as soon as one task finishes. Always cancel the pending ones, or they keep running in the background.
हिंदी: Race सबसे पहले खत्म होने वाले का result देता है — बाकी tasks cancel करने ज़रूरी हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # event loop utilities
from typing import Any, Awaitable  # type hints


async def race(*aws: Awaitable) -> Any:
    tasks = [asyncio.ensure_future(a) for a in aws]  # Step 1: start all concurrently
    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)  # Step 2: wait for first
        winner = next(iter(done))  # Step 3: pick the finished task
        return winner.result()  # Step 4: value, or raises its exception
    finally:  # Step 5: always clean up
        for t in tasks:
            if not t.done():
                t.cancel()  # cancel losers
        await asyncio.gather(*tasks, return_exceptions=True)  # let cancellation finish


# ============================================
# TEST CASES
# ============================================
async def job(name: str, delay: float, fail: bool = False) -> str:  # simulated I/O
    try:
        await asyncio.sleep(delay)  # pretend work
    except asyncio.CancelledError:
        print(f"{name} cancelled")  # show cleanup happens
        raise  # always re-raise CancelledError
    if fail:
        raise RuntimeError(f"{name} failed")  # simulated failure
    return name  # result


async def main() -> None:
    print(await race(job("slow", 0.3), job("fast", 0.1), job("mid", 0.2)))
    # Expected: slow cancelled / mid cancelled (order may vary), then: fast
    try:
        await race(job("slow", 0.3), job("bad", 0.05, True))  # first to finish is a failure
    except RuntimeError as e:
        print("race error:", e)  # Expected: slow cancelled  then  race error: bad failed
    try:
        await race()  # nothing to race
    except Exception as e:
        print(type(e).__name__, e)  # Expected: ValueError Set of Tasks/Futures is empty.


asyncio.run(main())
```

---

## 🔍 Why This Works (3 lines max)
`asyncio.wait` returns on the first completion, success or failure, just like `Promise.race`. The `finally` cancels the still-running tasks and awaits them so no "Task was destroyed" warnings appear.
हिंदी: पहला खत्म होते ही वापस आता है; finally में बाकी को cancel किया जाता है।

---

## ⚡ Alternative Solution
```python
async def race2(*aws):  # as_completed version
    for fut in asyncio.as_completed([asyncio.ensure_future(a) for a in aws]):  # yields in finish order
        return await fut  # take the first and stop (losers NOT cancelled here!)


async def m2():
    print(await race2(job("slow", 0.3), job("fast", 0.1)))  # Expected: fast
    await asyncio.sleep(0.4)  # losers keep running in the background


asyncio.run(m2())
# Shorter, but leaks the pending task — prefer the cancelling version above.
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: return the winner but never cancel the losers
done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
return next(iter(done)).result()   # ❌ pending tasks keep running (wasted work, leaked connections)

# ✅ Correct: cancel pending in a finally block and await them (see solution)
# Also: for a timeout-style race, prefer asyncio.timeout() / wait_for().
```

---

## 🎯 Interview Tip (1 line)
Say: "wait(FIRST_COMPLETED), then cancel and drain the pending tasks in finally — a race that leaks losers is a resource leak."

---

## 🔗 Related Questions
→ Q091 (gather) | Q094 (any) | Q212 (race with fallback) | Q205 (timeout a coroutine) | Q206 (cancel a task)
