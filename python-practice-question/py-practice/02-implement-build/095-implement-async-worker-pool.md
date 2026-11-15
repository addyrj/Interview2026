---

# Q095. Implement Async Worker Pool
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement `worker_pool(jobs, size)` that runs a list of async job factories with at most `size` running at the same time, returning results in input order. A failing job must not stop the others (store the exception as its result).

```python
res = await worker_pool(jobs, size=2)   # 6 jobs of 0.1s -> ~0.3s total
```

---

## 💡 Quick Concept (2 lines only)
Put jobs in an `asyncio.Queue` and start N worker coroutines; each worker loops pulling the next job until the queue is empty. Concurrency is capped by the number of workers.
हिंदी: Queue में jobs डालो और N workers चलाओ — एक समय में सिर्फ N jobs चलेंगे।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # queue + tasks
from typing import Any, Awaitable, Callable  # type hints


async def worker_pool(jobs: list[Callable[[], Awaitable[Any]]], size: int) -> list[Any]:
    queue: asyncio.Queue[tuple[int, Callable[[], Awaitable[Any]]]] = asyncio.Queue()  # Step 1: job queue
    for i, job in enumerate(jobs):
        queue.put_nowait((i, job))  # remember the index to keep order
    results: list[Any] = [None] * len(jobs)  # Step 2: slots for ordered results

    async def worker(wid: int) -> None:  # Step 3: one worker loop
        while True:
            try:
                idx, job = queue.get_nowait()  # take the next job
            except asyncio.QueueEmpty:
                return  # nothing left -> worker exits
            try:
                results[idx] = await job()  # run it
            except Exception as e:
                results[idx] = e  # failure is stored, pool continues
            print(f"worker {wid} finished job {idx}")  # progress log

    await asyncio.gather(*(worker(w) for w in range(min(size, len(jobs)))))  # Step 4: start N workers
    return results  # Step 5: ordered results


# ============================================
# TEST CASES
# ============================================
def make_job(n: int, delay: float) -> Callable[[], Awaitable[int]]:  # job factory
    async def job() -> int:
        await asyncio.sleep(delay)  # simulated I/O
        if n == 3:
            raise ValueError("job 3 bad")  # one bad job
        return n * 10  # result
    return job


async def main() -> None:
    loop = asyncio.get_running_loop(); t = loop.time()  # timing
    res = await worker_pool([make_job(i, 0.1) for i in range(6)], size=2)
    # Expected log: worker 0 finished job 0 / worker 1 finished job 1 / ... (2 at a time)
    print(res)  # Expected: [0, 10, 20, ValueError('job 3 bad'), 40, 50]
    print(round(loop.time() - t, 1))  # Expected: 0.3  (6 jobs / 2 workers * 0.1s)
    print(await worker_pool([], 3))  # Expected: []


asyncio.run(main())
```

---

## 🔍 Why This Works (3 lines max)
Only `size` workers exist, each awaiting one job at a time, so concurrency never exceeds `size`. Storing each result by its index keeps order, and catching `Exception` stops one failure from killing the pool.
हिंदी: Workers की संख्या ही concurrency limit है; index से order बना रहता है।

---

## ⚡ Alternative Solution
```python
async def pool_sem(jobs, size):  # semaphore version — much shorter
    sem = asyncio.Semaphore(size)  # allows `size` holders at once

    async def run(j):
        async with sem:  # wait for a free slot
            return await j()  # run the job

    return await asyncio.gather(*(run(j) for j in jobs), return_exceptions=True)  # order kept, errors as values


async def m2():
    loop = asyncio.get_running_loop(); t = loop.time()
    print(await pool_sem([make_job(i, 0.1) for i in range(6)], 3))
    # Expected: [0, 10, 20, ValueError('job 3 bad'), 40, 50]
    print(round(loop.time() - t, 1))  # Expected: 0.2  (6 jobs / 3 slots * 0.1s)


asyncio.run(m2())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: launching every job at once (no limit) — can exhaust sockets / hit rate limits
await asyncio.gather(*(j() for j in jobs))

# ❌ Also wrong: shared results via list.append — order depends on finish time
# ✅ Correct: bounded workers (queue) or Semaphore, and write by index
```

---

## 🎯 Interview Tip (1 line)
Say: "Queue + N workers gives backpressure and a hard concurrency cap; for a quick version a Semaphore around gather does the same job."

---

## 🔗 Related Questions
→ Q203 (limit concurrency with Semaphore) | Q210 (async map with limit) | Q216 (producer-consumer) | Q184 (request queue)
