---

# Q213. Polling with async/await
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `poll(check, done, interval, max_attempts)` that repeatedly calls an async `check()` until `done(result)` is True. Raise `TimeoutError` if it never finishes.

```python
await poll(job_status, lambda r: r['status'] == 'done', interval=1)
```

---

## 💡 Quick Concept (2 lines only)
Loop: call, test, `await asyncio.sleep(interval)`, repeat - with a hard attempt limit so it can never spin forever.
हिंदी: Check करो, done नहीं तो asyncio.sleep, फिर दोबारा — और max_attempts ज़रूर रखो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
from collections.abc import Awaitable, Callable   # type hints
from typing import Any                            # generic value


async def poll(
    check: Callable[[], Awaitable[Any]],          # async function to call repeatedly
    done: Callable[[Any], bool],                  # predicate: is the result final?
    interval: float = 0.1,                        # seconds between attempts
    max_attempts: int = 10,                       # safety limit
) -> Any:
    for attempt in range(1, max_attempts + 1):    # bounded loop (never infinite)
        result = await check()                    # call the API
        if done(result):                          # finished?
            return result                         # return final result
        await asyncio.sleep(interval)             # non-blocking wait before retry
    raise TimeoutError(f"not done after {max_attempts} attempts")  # give up


# ---------- TEST CASES ----------
state = {"calls": 0}                              # fake server state


async def job_status() -> dict:
    state["calls"] += 1                           # count calls
    await asyncio.sleep(0)                        # yield to loop (simulated I/O)
    status = "done" if state["calls"] >= 3 else "pending"  # finishes on 3rd call
    return {"status": status, "calls": state["calls"]}


async def main() -> None:
    print(await poll(job_status, lambda r: r["status"] == "done", interval=0.01))  # succeeds
    try:
        await poll(job_status, lambda r: False, interval=0.01, max_attempts=3)  # never done
    except TimeoutError as e:
        print("TimeoutError:", e)                 # gave up


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# {'status': 'done', 'calls': 3}
# TimeoutError: not done after 3 attempts
```

---

## 🔍 Why This Works (3 lines max)
`asyncio.sleep` yields to the event loop, so other tasks keep running while you wait (never use `time.sleep`). The bounded `for` loop guarantees termination; the async-generator version lets the caller decide when to stop.
हिंदी: asyncio.sleep loop को free छोड़ता है; time.sleep पूरा event loop block कर देगा।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library
from collections.abc import AsyncIterator         # type hint


async def poll_stream(check, interval: float) -> AsyncIterator[dict]:
    while True:                                   # infinite generator; caller decides when to stop
        yield await check()                       # emit every status update
        await asyncio.sleep(interval)             # wait between polls


calls = 0                                         # fake server counter


async def check() -> dict:
    global calls                                  # modify module counter
    calls += 1                                    # count call
    return {"progress": calls * 25}               # 25, 50, 75, 100


async def main() -> None:
    try:
        async with asyncio.timeout(1):            # overall deadline for the whole polling
            async for status in poll_stream(check, 0.01):  # consume updates
                print(status)                     # show progress
                if status["progress"] >= 100:     # done condition
                    break                         # stop polling (generator is closed)
    except TimeoutError:
        print("timed out")                        # deadline exceeded


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# {'progress': 25}
# {'progress': 50}
# {'progress': 75}
# {'progress': 100}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: time.sleep blocks the WHOLE event loop + infinite loop
while True:
    r = await check()
    if done(r):
        break
    time.sleep(1)                     # freezes every other task!

# ✅ Correct: await asyncio.sleep + attempt limit (see solution)
```

---

## 🎯 Interview Tip (1 line)
Say: "Polling = bounded loop + asyncio.sleep; mention exponential backoff or webhooks/SSE as better alternatives."

---

## 🔗 Related Questions
→ Q205 (timeout) | Q204 (retry) | Q089 (retry with backoff) | Q220 (async generators)
