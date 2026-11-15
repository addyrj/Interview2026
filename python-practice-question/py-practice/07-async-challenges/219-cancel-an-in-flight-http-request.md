---

# Q219. Cancel an in-flight HTTP request
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Start an `httpx.AsyncClient` request, then cancel it while it is still running (user clicked Cancel / deadline hit). Show that cleanup runs and that `CancelledError` is not swallowed.

```python
task = asyncio.create_task(client.get(url))
task.cancel()
```

---

## 💡 Quick Concept (2 lines only)
Wrap the request in a `Task` and call `task.cancel()` - `CancelledError` is raised inside the awaiting code, so `finally` blocks and `async with` cleanup run. `asyncio.timeout()` does it automatically.
हिंदी: Request को Task में चलाओ और task.cancel() करो — finally/cleanup चलता है; CancelledError को कभी दबाओ मत।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library
import httpx                                      # async HTTP client


async def slow_handler(request: httpx.Request) -> httpx.Response:
    try:
        await asyncio.sleep(5)                    # "server" takes 5 s
        return httpx.Response(200, text="late")   # never reached if cancelled
    finally:
        print("transport: request cleaned up")   # runs when cancellation arrives


async def main() -> None:
    transport = httpx.MockTransport(slow_handler) # fake network, no real server
    async with httpx.AsyncClient(transport=transport) as client:
        task = asyncio.create_task(client.get("http://example.test/slow"))  # start request
        await asyncio.sleep(0.05)                 # request is now in flight
        task.cancel()                             # cancel it
        try:
            await task                            # wait so we can observe the result
        except asyncio.CancelledError:
            print("request cancelled")            # the await raised CancelledError
        print("task.cancelled() =", task.cancelled())  # True


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# transport: request cleaned up
# request cancelled
# task.cancelled() = True
```

---

## 🔍 Why This Works (3 lines max)
`cancel()` only schedules cancellation; you must `await task` to see it finish (`task.cancelled()` is True). Tests use `httpx.MockTransport`, so no network is needed. `asyncio.timeout(0.1)` turns cancellation into a `TimeoutError`.
हिंदी: cancel() सिर्फ request करता है; await करके ही confirm होता है; timeout() इसे अपने आप कर देता है।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library
import httpx                                      # async HTTP client


async def slow_handler(request: httpx.Request) -> httpx.Response:
    await asyncio.sleep(5)                        # "server" takes 5 s
    return httpx.Response(200, text="late")       # never reached


async def main() -> None:
    async with httpx.AsyncClient(transport=httpx.MockTransport(slow_handler)) as client:
        try:
            async with asyncio.timeout(0.1):      # deadline for the whole block
                await client.get("http://example.test/slow")  # in-flight call
        except TimeoutError:
            print("deadline hit -> request cancelled")  # Cancelled is converted to TimeoutError

        async def fetch_or_none():
            return await client.get("http://example.test/slow")  # call to be raced

        t1 = asyncio.create_task(fetch_or_none())  # two competing requests
        t2 = asyncio.create_task(asyncio.sleep(0.05, "user clicked Cancel"))  # user action
        done, pending = await asyncio.wait({t1, t2}, return_when=asyncio.FIRST_COMPLETED)  # first wins
        for t in pending:                         # cancel what is still running
            t.cancel()                            # abort the HTTP call
        print(done.pop().result())                # the cancel signal won


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# deadline hit -> request cancelled
# user clicked Cancel
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: swallowing CancelledError - the task refuses to die
try:
    await client.get(url)
except Exception:                     # in 3.8+ CancelledError is BaseException, so this is OK...
    pass
except BaseException:                 # ...but THIS swallows cancellation (and Ctrl+C)
    pass

# ✅ Correct: let CancelledError propagate (re-raise after cleanup)
```

---

## 🎯 Interview Tip (1 line)
Say: "CancelledError is a BaseException; always re-raise it, use finally for cleanup, and prefer asyncio.timeout() for deadlines."

---

## 🔗 Related Questions
→ Q206 (cancel a task) | Q205 (timeout) | Q212 (race with fallback) | Q131 (bare except)
