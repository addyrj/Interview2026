---

# Q286. asyncio for Many Connections
# Category: PERFORMANCE
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Handle 1,000 simulated network calls (each waits 0.2s). Use asyncio so total time is about 0.2s, not 200s. Also limit concurrency to protect a server.

---

## 💡 Quick Concept (2 lines only)
asyncio runs many coroutines on ONE thread; `await` hands control back while waiting, so thousands of waits overlap cheaply. Use a `Semaphore` to cap how many run at once.
हिंदी: एक thread पर हज़ारों coroutines; await पर control छोड़ते हैं, इसलिए wait overlap होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                  # Step 1: event loop library
import time                                     # timing

async def fake_call(i: int) -> int:             # Step 2: simulated async I/O
    await asyncio.sleep(0.2)                    # yields to the event loop while "waiting"
    return i * 2                                # pretend response

async def main() -> None:                       # Step 3: orchestrate all calls
    start = time.perf_counter()                 # start clock
    results = await asyncio.gather(*(fake_call(i) for i in range(1000)))  # run 1000 at once
    elapsed = time.perf_counter() - start       # total time

    # ============================================
    # TEST CASES
    # ============================================
    print(len(results))                         # Expected: 1000
    print(results[:5])                          # Expected: [0, 2, 4, 6, 8]
    print(elapsed < 1.0)                        # Expected: True  (about 0.2s; varies)

asyncio.run(main())                             # Step 4: start the event loop
```

---

## 🔍 Why This Works (3 lines max)
Each coroutine is a tiny object (not an OS thread), so 1,000 of them are cheap, and `asyncio.sleep` suspends without blocking the loop. A single blocking call like `time.sleep` would freeze ALL of them.
हिंदी: Coroutine हल्का होता है; blocking call (time.sleep) पूरा loop रोक देता है।

---

## ⚡ Alternative Solution
```python
# Bounded concurrency with Semaphore + TaskGroup (Python 3.11+)
import asyncio                                  # asyncio import
import time                                     # timing

async def fake_call(i: int, sem: asyncio.Semaphore) -> int:  # call guarded by semaphore
    async with sem:                             # at most 100 inside at once
        await asyncio.sleep(0.1)                # simulated I/O
        return i                                # response

async def main() -> None:                       # orchestrator
    sem = asyncio.Semaphore(100)                # concurrency limit
    start = time.perf_counter()                 # start clock
    async with asyncio.TaskGroup() as tg:       # structured concurrency
        tasks = [tg.create_task(fake_call(i, sem)) for i in range(500)]  # 500 tasks
    elapsed = time.perf_counter() - start       # 5 waves of 100 -> ~0.5s
    print(sum(t.result() for t in tasks))       # Expected: 124750
    print(0.4 < elapsed < 1.5)                  # Expected: True  (about 0.5s; varies)

asyncio.run(main())                             # run it
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: blocking call inside a coroutine freezes the whole loop
import asyncio                                  # asyncio import
import time                                     # timing

async def bad() -> None:                        # blocks the loop
    time.sleep(0.1)                             # NOT awaitable-friendly: nothing else runs

async def good() -> None:                       # ✅ correct: cooperative wait
    await asyncio.sleep(0.1)                    # yields control

async def main() -> None:                       # compare 5 concurrent calls each
    s = time.perf_counter()                     # start
    await asyncio.gather(*(bad() for _ in range(5)))   # runs one after another: ~0.5s
    t_bad = time.perf_counter() - s             # measure
    s = time.perf_counter()                     # start
    await asyncio.gather(*(good() for _ in range(5)))  # overlaps: ~0.1s
    t_good = time.perf_counter() - s            # measure
    print(t_bad > 0.4, t_good < 0.3)            # Expected: True True

asyncio.run(main())                             # run
```

---

## 🎯 Interview Tip (1 line)
Say: "asyncio for many concurrent I/O waits on one thread; never block the loop (use `asyncio.to_thread` for blocking code) and bound concurrency with a Semaphore."

---

## 🔗 Related Questions
→ Q285 (threading for I/O) | Q124 (blocking call in async) | Q091 (implement gather) | Q299 (threading vs multiprocessing vs asyncio)
