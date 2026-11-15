---

# Q184. Build Request Queue
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `RequestQueue(concurrency)` that accepts async jobs and runs at most `concurrency` of them at the same time. Results must come back in the original order, and one failing job must not break the others.

```python
q = RequestQueue(concurrency=2)
results = await q.run([job1, job2, job3, ...])
```

---

## 💡 Quick Concept (2 lines only)
An `asyncio.Queue` plus N worker tasks: workers pull jobs and resolve a Future per job. Number of workers = max parallelism.
हिंदी: Queue में jobs डालो, N workers एक-एक job उठाकर चलाते हैं — एक साथ N से ज़्यादा नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import asyncio  # async tools
from typing import Any, Awaitable, Callable  # type hints

class RequestQueue:
    def __init__(self, concurrency: int = 2) -> None:
        self.concurrency = concurrency  # max parallel workers
        self._q: asyncio.Queue = asyncio.Queue()  # pending jobs

    def add(self, fn: Callable[[], Awaitable[Any]]) -> asyncio.Future:
        fut: asyncio.Future = asyncio.get_running_loop().create_future()  # result handle
        self._q.put_nowait((fn, fut))  # enqueue job
        return fut  # caller awaits this

    async def _worker(self) -> None:
        while True:  # loop forever
            fn, fut = await self._q.get()  # wait for a job
            try:
                fut.set_result(await fn())  # run and store result
            except Exception as e:
                fut.set_exception(e)  # store the error
            finally:
                self._q.task_done()  # mark processed

    async def run(self, jobs: list[Callable[[], Awaitable[Any]]]) -> list[Any]:
        futs = [self.add(j) for j in jobs]  # enqueue all
        workers = [asyncio.create_task(self._worker()) for _ in range(self.concurrency)]  # start workers
        try:
            return await asyncio.gather(*futs, return_exceptions=True)  # results in order
        finally:
            for w in workers:
                w.cancel()  # stop workers

# ============================================
# TEST CASES
# ============================================
active = 0  # currently running
peak = 0  # max running at once
def make(i: int, delay: float):
    async def job() -> str:
        global active, peak
        active += 1  # start
        peak = max(peak, active)  # track peak
        await asyncio.sleep(delay)  # simulated I/O
        active -= 1  # end
        if i == 3:
            raise ValueError("bad job 3")  # one failure
        return f"job{i}"  # result
    return job

async def main() -> None:
    q = RequestQueue(concurrency=2)  # 2 at a time
    res = await q.run([make(i, 0.02) for i in range(5)])  # 5 jobs
    print(res)  # Expected: ['job0', 'job1', 'job2', ValueError('bad job 3'), 'job4']
    print("peak concurrency:", peak)  # Expected: peak concurrency: 2
asyncio.run(main())
```

---

## 🔍 Why This Works (3 lines max)
Each job gets a Future, so `gather` returns results in submission order even though workers finish out of order. Only `concurrency` workers exist, so parallelism never exceeds the limit; errors are stored in the Future, not crashing the worker.
हिंदी: हर job का Future होता है, इसलिए results order में आते हैं और error से worker नहीं मरता।

---

## ⚡ Alternative Solution
```python
import asyncio  # async tools

async def run_limited(jobs, limit: int = 2):  # no queue, just a semaphore
    sem = asyncio.Semaphore(limit)  # at most `limit` at once
    async def guarded(j):
        async with sem:  # acquire slot
            return await j()  # run job
    return await asyncio.gather(*(guarded(j) for j in jobs), return_exceptions=True)  # ordered results

peak = active = 0  # counters
def make(i):
    async def job():
        global active, peak
        active += 1  # start
        peak = max(peak, active)  # peak
        await asyncio.sleep(0.02)  # I/O
        active -= 1  # end
        return i * 10  # result
    return job
print(asyncio.run(run_limited([make(i) for i in range(5)])), peak)  # Expected: [0, 10, 20, 30, 40] 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: gather everything at once — 1000 jobs = 1000 simultaneous requests (not run)
# results = await asyncio.gather(*(job() for job in jobs))

# ❌ Also wrong: forgetting to cancel workers -> "Task was destroyed but it is pending" warnings

# ✅ Correct: bound concurrency with Semaphore or N workers, and cancel workers in `finally`
```

---

## 🎯 Interview Tip (1 line)
Say: "Semaphore is the simplest limiter; a Queue + workers adds back-pressure and lets jobs arrive over time."

---

## 🔗 Related Questions
→ Q095 (async worker pool) | Q203 (Semaphore limit) | Q210 (async map with limit) | Q216 (producer-consumer)
