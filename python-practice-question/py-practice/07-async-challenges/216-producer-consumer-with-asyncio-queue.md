---

# Q216. Producer-consumer with asyncio.Queue
# Category: ASYNC CHALLENGES
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Build a producer that puts 6 jobs on an `asyncio.Queue(maxsize=2)` and 2 consumer workers that process them. Shut the workers down cleanly when all work is done.

```python
q = asyncio.Queue(maxsize=2)
```

---

## 💡 Quick Concept (2 lines only)
`Queue` decouples producers and consumers; `maxsize` gives back-pressure, `task_done()`/`join()` track work, a sentinel (or `shutdown()` in 3.13) stops workers.
हिंदी: Queue producer और consumer को अलग करता है; maxsize से back-pressure मिलता है; sentinel से workers रुकते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio                                    # asyncio library

SENTINEL = None                                   # "no more work" marker


async def producer(q: asyncio.Queue, n: int) -> None:
    for i in range(n):                            # make n jobs
        await q.put(i)                            # blocks if queue is full (back-pressure)
        await asyncio.sleep(0.001)                # simulated production time


async def consumer(name: str, q: asyncio.Queue, out: list) -> None:
    while True:                                   # keep working until told to stop
        item = await q.get()                      # wait for a job
        if item is SENTINEL:                      # stop signal
            q.task_done()                         # mark sentinel as handled
            break                                 # leave the loop
        await asyncio.sleep(0.01)                 # simulated processing
        out.append((name, item * item))           # store result
        q.task_done()                             # mark job as handled


async def main() -> None:
    q: asyncio.Queue = asyncio.Queue(maxsize=2)   # bounded queue
    out: list = []                                # collected results
    consumers = [asyncio.create_task(consumer(f"c{i}", q, out)) for i in range(2)]  # 2 workers
    await producer(q, 6)                          # produce 6 jobs
    for _ in consumers:                           # one sentinel per consumer
        await q.put(SENTINEL)                     # tell each worker to stop
    await asyncio.gather(*consumers)              # wait for workers to exit
    print(sorted(r for _, r in out))              # squares of 0..5
    print("workers used:", sorted({n for n, _ in out}))  # both workers did work


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13, which and how work is split between workers can vary; results are sorted):
# ============================================

# [0, 1, 4, 9, 16, 25]
# workers used: ['c0', 'c1']
```

---

## 🔍 Why This Works (3 lines max)
`put()` waits when the queue is full, so a fast producer cannot flood memory. Each consumer loops on `get()` until it sees the sentinel `None`. Python 3.13 adds `Queue.shutdown()`, which removes the need for sentinels (see alternative).
हिंदी: भरी queue पर put() रुक जाता है; हर consumer को एक sentinel भेजो; 3.13 में shutdown() भी है।

---

## ⚡ Alternative Solution
```python
import asyncio                                    # asyncio library (Queue.shutdown needs 3.13+)


async def consumer(q: asyncio.Queue, out: list) -> None:
    try:
        while True:                               # loop until queue is shut down
            item = await q.get()                  # raises QueueShutDown when empty + shut down
            out.append(item * 2)                  # "process" the item
            q.task_done()                         # mark done
    except asyncio.QueueShutDown:                 # new in Python 3.13
        pass                                      # clean exit, no sentinel needed


async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue()       # unbounded queue
    out: list[int] = []                           # results
    workers = [asyncio.create_task(consumer(q, out)) for _ in range(3)]  # 3 workers
    for i in range(5):                            # enqueue jobs
        q.put_nowait(i)                           # no await needed (unbounded)
    q.shutdown()                                  # no more puts; getters drain then stop
    await asyncio.gather(*workers)                # workers exit by themselves
    print(sorted(out))                            # doubled values


asyncio.run(main())                               # run demo

# ============================================
# OUTPUT (real run, Python 3.13, which and how work is split between workers can vary; results are sorted):
# ============================================

# [0, 2, 4, 6, 8]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: queue.Queue (thread queue) in async code - get() BLOCKS the event loop
import queue
q = queue.Queue()
item = q.get()                        # freezes everything

# ❌ Wrong: only ONE sentinel for two consumers -> the second consumer waits forever
# ✅ Correct: asyncio.Queue + one sentinel per consumer (or q.shutdown() on 3.13)
```

---

## 🎯 Interview Tip (1 line)
Say: "asyncio.Queue for async producers/consumers, bounded for back-pressure; one stop signal per worker; 3.13 added Queue.shutdown()."

---

## 🔗 Related Questions
→ Q095 (async worker pool) | Q184 (request queue) | Q203 (Semaphore limit) | Q101 (queue)
