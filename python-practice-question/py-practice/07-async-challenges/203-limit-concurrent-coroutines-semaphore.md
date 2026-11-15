---

# Q203. Limit concurrent coroutines (Semaphore)
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
You have 10 jobs but may only run 3 at the same time (e.g. API rate limit). Use `asyncio.Semaphore` and prove the peak concurrency is 3.

---

## 💡 Quick Concept (2 lines only)
A Semaphore holds N permits; `async with sem:` takes one and releases it on exit — extra tasks wait their turn.
हिंदी: Semaphore(3) एक समय में सिर्फ 3 tasks को अंदर आने देता है, बाकी इंतज़ार करते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio                                       # asyncio

active = 0                                           # currently running workers
peak = 0                                             # highest concurrency seen

async def worker(i: int, sem: asyncio.Semaphore) -> int:
    global active, peak                              # shared counters
    async with sem:                                  # wait for a free slot, release on exit
        active += 1                                  # we are now running
        peak = max(peak, active)                     # track the maximum
        await asyncio.sleep(0.05)                    # simulated I/O
        active -= 1                                  # finished
    return i * 10                                    # result

async def main() -> None:
    sem = asyncio.Semaphore(3)                       # at most 3 at once (create inside the loop)
    results = await asyncio.gather(*(worker(i, sem) for i in range(10)))
    print(results)                                   # Expected: [0, 10, 20, ..., 90]
    print("peak concurrency:", peak)                 # Expected: 3

asyncio.run(main())

# --- Real output (Python 3.13) ---
# [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
# peak concurrency: 3
```

---

## 🔍 Why This Works (3 lines max)
All 10 tasks are created at once, but only 3 can pass `async with sem`. When one finishes it frees a permit and the next waiter proceeds. The `peak` counter proves the limit. Create the Semaphore inside the running loop (inside `main`).
हिंदी: 10 tasks बनते हैं पर permit सिर्फ 3 हैं; एक खत्म होते ही अगला चलता है।

---

## ⚡ Alternative Solution
```python
# ============================================
# ALTERNATIVE: fixed pool of workers pulling from a Queue
# ============================================
import asyncio                                       # asyncio

async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue()          # job queue
    for i in range(6):                               # enqueue 6 jobs
        q.put_nowait(i)                              # no await needed (unbounded queue)
    out: list[int] = []                              # results

    async def worker() -> None:
        while not q.empty():                         # until queue is drained
            i = q.get_nowait()                       # take a job
            await asyncio.sleep(0.01)                # simulated I/O
            out.append(i * 2)                        # store result

    await asyncio.gather(*(worker() for _ in range(2)))  # only 2 workers -> max 2 at once
    print(sorted(out))                               # Expected: [0, 2, 4, 6, 8, 10]

asyncio.run(main())

# --- Real output (Python 3.13) ---
# [0, 2, 4, 6, 8, 10]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: acquire without release on error paths
await sem.acquire()
await do_work()      # if this raises, the permit is never released -> deadlock later
sem.release()

# ✅ Correct: async with sem: ...  (releases even on exceptions/cancellation)
```

---

## 🎯 Interview Tip (1 line)
Say: "Semaphore limits concurrency, not rate — for requests-per-second I'd combine it with a token bucket (Q186)."

---

## 🔗 Related Questions
→ Q095 (worker pool) | Q186 (rate limiter) | Q210 (async map with limit) | Q217 (batch API calls)
