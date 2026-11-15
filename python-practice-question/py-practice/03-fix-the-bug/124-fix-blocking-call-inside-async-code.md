---

# Q124. Fix blocking call inside async code
# Category: FIX THE BUG
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Five "concurrent" handlers take 1 second in total instead of 0.2s, and other tasks freeze meanwhile. Find the bug and fix it (also handle a legacy sync library you cannot change).

```python
async def handler(n):
    time.sleep(0.2)      # BUG
    return n
```

---

## 💡 Quick Concept (2 lines only)
The event loop is single-threaded; a blocking call (`time.sleep`, `requests`, sync DB) freezes EVERY task. Use `await asyncio.sleep` or push sync code to a thread.
हिंदी: Blocking call पूरा event loop रोक देता है — `asyncio.sleep` या `asyncio.to_thread` इस्तेमाल करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio, time                                   # stdlib

async def handler_blocking(n: int) -> int:
    time.sleep(0.2)                                    # BUG: blocks the whole event loop
    return n

async def handler_fixed(n: int) -> int:
    await asyncio.sleep(0.2)                           # FIX 1: non-blocking, yields to the loop
    return n

def legacy_blocking_call(n: int) -> int:
    time.sleep(0.2)                                    # e.g. requests.get / sync DB driver
    return n

async def handler_thread(n: int) -> int:
    return await asyncio.to_thread(legacy_blocking_call, n)   # FIX 2: run sync code in a worker thread

async def timed(label, fn):
    start = time.perf_counter()                        # start clock
    res = await asyncio.gather(*(fn(i) for i in range(5)))    # 5 concurrent handlers
    print(f"{label}: {res} took {time.perf_counter() - start:.1f}s")

# ============================================
# TEST CASES
# ============================================
async def main():
    await timed("blocking  ", handler_blocking)        # Expected: blocking  : [0, 1, 2, 3, 4] took 1.0s
    await timed("asyncio   ", handler_fixed)           # Expected: asyncio   : [0, 1, 2, 3, 4] took 0.2s
    await timed("to_thread ", handler_thread)          # Expected: to_thread : [0, 1, 2, 3, 4] took 0.2s
asyncio.run(main())                                    # timings vary slightly per machine

# Heartbeat proof: a background task should tick every 0.1s
async def heartbeat(ticks: list, t0: float):
    for _ in range(4):
        ticks.append(round(time.perf_counter() - t0, 1))   # record time
        await asyncio.sleep(0.1)

async def run(block_fn):
    t0 = time.perf_counter(); ticks: list = []
    hb = asyncio.create_task(heartbeat(ticks, t0))     # start heartbeat
    await asyncio.sleep(0)                             # let it start
    await block_fn()                                   # the 0.5s job
    await hb
    return ticks

async def block_bad(): time.sleep(0.5)                 # freezes the loop
async def block_good(): await asyncio.to_thread(time.sleep, 0.5)   # loop stays free

async def m2():
    print("blocking ticks:", await run(block_bad))     # Expected: [0.0, 0.5, 0.6, 0.7]  <- gap!
    print("to_thread ticks:", await run(block_good))   # Expected: [0.0, 0.1, 0.2, 0.3]
asyncio.run(m2())
```

---

## 🔍 Why This Works (3 lines max)
`asyncio.sleep` hands control back to the loop so other tasks run meanwhile; `to_thread` moves blocking work to a thread so the loop stays responsive. With `time.sleep` the heartbeat could not tick for 0.5s.
हिंदी: `await` loop को खाली करता है; `time.sleep` पूरे loop को सुला देता है।

---

## ⚡ Alternative Solution
```python
# Detect it: asyncio debug mode logs slow callbacks (>100ms)
async def slow():
    time.sleep(0.2)                                    # blocking
asyncio.run(slow(), debug=True)
# stderr: Executing <Task ... coro=<slow() ...>> took 0.2xx seconds   (exact text/time varies)

# For CPU-bound work use a process pool instead of a thread:
# await asyncio.get_running_loop().run_in_executor(ProcessPoolExecutor(), cpu_func, arg)
# Or use async-native libraries (httpx.AsyncClient, asyncpg) instead of requests / psycopg2.
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: marking a function `async def` does NOT make its blocking body async
async def fetch():
    return requests.get(url)             # still blocks the loop (not run here)

# ✅ Correct: use httpx.AsyncClient, or await asyncio.to_thread(requests.get, url)
```

---

## 🎯 Interview Tip (1 line)
Say: "One blocking call stalls every coroutine — use async-native libs, `asyncio.to_thread` for blocking I/O, and a process pool for CPU work."

---

## 🔗 Related Questions
→ Q123 (missing await) | Q173 (asyncio event loop) | Q285 (threading for I/O-bound) | Q286 (asyncio for many connections)
