---

# Q205. Timeout a coroutine
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
A coroutine takes 1 second but you only want to wait 0.1s. Cancel it and handle the timeout using `asyncio.timeout` and `asyncio.wait_for`.

---

## 💡 Quick Concept (2 lines only)
`async with asyncio.timeout(sec):` (3.11+) cancels the block and raises `TimeoutError`; `wait_for` does the same for a single awaitable.
हिंदी: `asyncio.timeout` समय खत्म होने पर काम cancel करके `TimeoutError` देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # asyncio

async def slow() -> str:
    await asyncio.sleep(1)                           # takes 1 second
    return "finished"                                # never reached when timed out

async def main() -> None:
    try:
        async with asyncio.timeout(0.1):             # 3.11+: cancel the block after 0.1s
            await slow()                             # too slow
    except TimeoutError:                             # asyncio.timeout raises builtin TimeoutError
        print("timed out (context manager)")         # Expected
    try:
        print(await asyncio.wait_for(slow(), timeout=0.1))  # older API, same idea
    except TimeoutError:                             # 3.11+: wait_for also raises TimeoutError
        print("timed out (wait_for)")                # Expected
    print(await asyncio.wait_for(asyncio.sleep(0.01, "fast"), 1))  # Expected: fast

asyncio.run(main())

# --- Real output (Python 3.13) ---
# timed out (context manager)
# timed out (wait_for)
# fast
```

---

## 🔍 Why This Works (3 lines max)
On timeout the inner await receives `CancelledError`, which the timeout context converts into the builtin `TimeoutError` (since 3.11 it is the same as `asyncio.TimeoutError`). `asyncio.wait` with a timeout is different: it doesn't raise or cancel anything.
हिंदी: Timeout पर अंदर का काम cancel होता है और बाहर `TimeoutError` मिलता है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: asyncio.wait with timeout (task keeps running unless you cancel it)
# ============================================
import asyncio                                       # asyncio

async def slow() -> str:
    await asyncio.sleep(1)                           # 1s of work
    return "finished"

async def main() -> None:
    task = asyncio.create_task(slow())               # run as a task
    done, pending = await asyncio.wait({task}, timeout=0.1)  # no exception on timeout
    print(len(done), len(pending))                   # Expected: 0 1
    for t in pending:                                # we must clean up ourselves
        t.cancel()                                   # cancel the leftover task
    await asyncio.gather(*pending, return_exceptions=True)  # let cancellation finish
    print(task.cancelled())                          # Expected: True

asyncio.run(main())

# --- Real output (Python 3.13) ---
# 0 1
# True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: catching Exception around the timeout and 'moving on' hides the real problem,
# and time.sleep() can't be timed out at all because it blocks the loop
import time
async def bad():
    async with asyncio.timeout(0.1):
        time.sleep(1)      # blocks the whole loop; timeout fires only AFTER it returns

# ✅ Correct: await real async operations (asyncio.sleep, httpx, ...) inside the timeout
```

---

## 🎯 Interview Tip (1 line)
Say: "Timeouts are mandatory on every network call — and the task keeps running after `asyncio.wait` times out unless I cancel it."

---

## 🔗 Related Questions
→ Q206 (cancel a task) | Q212 (race with fallback) | Q092 (race) | Q219 (cancel in-flight request)
