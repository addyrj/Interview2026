---

# Q206. Cancel a task
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Start a long-running task, cancel it after a short time, run cleanup logic inside the task, and handle the `CancelledError` correctly.

---

## 💡 Quick Concept (2 lines only)
`task.cancel()` throws `CancelledError` into the task at its next `await`; clean up in `except/finally` and always re-raise.
हिंदी: `task.cancel()` task के अंदर `CancelledError` फेंकता है — cleanup करो और उसे दोबारा raise करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # asyncio

async def worker() -> None:
    try:
        print("worker: started")                     # begins running
        await asyncio.sleep(10)                      # long job
    except asyncio.CancelledError:                   # cancel() injects this at the await
        print("worker: cleaning up")                 # do cleanup here
        raise                                        # ALWAYS re-raise so the task ends as cancelled
    finally:
        print("worker: finally")                     # runs in all cases

async def main() -> None:
    task = asyncio.create_task(worker())             # start the task
    await asyncio.sleep(0.05)                        # let it start
    task.cancel()                                    # request cancellation
    try:
        await task                                   # awaiting a cancelled task raises
    except asyncio.CancelledError:
        print("main: task was cancelled")            # Expected
    print(task.cancelled(), task.done())             # Expected: True True

asyncio.run(main())

# --- Real output (Python 3.13) ---
# worker: started
# worker: cleaning up
# worker: finally
# main: task was cancelled
# True True
```

---

## 🔍 Why This Works (3 lines max)
Cancellation is cooperative: it only takes effect at an `await`. Swallowing `CancelledError` leaves the task looking 'done' normally and breaks `timeout()`/TaskGroup logic. Awaiting a cancelled task raises `CancelledError` in the awaiter.
हिंदी: Cancel सिर्फ `await` पर असर करता है; `CancelledError` को निगलना नहीं चाहिए।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: cancel many tasks + ignore the CancelledError with gather
# ============================================
import asyncio                                       # asyncio

async def job(i: int) -> int:
    await asyncio.sleep(10)                          # long job
    return i

async def main() -> None:
    tasks = [asyncio.create_task(job(i)) for i in range(3)]  # 3 tasks
    await asyncio.sleep(0)                           # let them start
    for t in tasks:
        t.cancel()                                   # cancel all
    results = await asyncio.gather(*tasks, return_exceptions=True)  # collect, don't raise
    print([type(r).__name__ for r in results])       # Expected: ['CancelledError', 'CancelledError', 'CancelledError']

asyncio.run(main())

# --- Real output (Python 3.13) ---
# ['CancelledError', 'CancelledError', 'CancelledError']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: swallowing CancelledError
async def worker():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("ignored")   # task now finishes 'normally' -> cancel() is defeated

# ✅ Correct: cleanup, then `raise` (see solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "Cancellation is cooperative — always re-raise CancelledError, and put cleanup in `finally`."

---

## 🔗 Related Questions
→ Q205 (timeout) | Q219 (cancel in-flight request) | Q173 (event loop) | Q172 (async/await internals)
