---

# 246. Semaphore in asyncio
# हिंदी में: asyncio में Semaphore — एक साथ चलने वाले tasks की सीमा

---

## 🔵 Simple Definition (English)
`asyncio.Semaphore(n)` is a counter of "free slots". A task takes a slot with `async with sem:` (or `await sem.acquire()`) and gives it back when done. If all `n` slots are taken, the next task waits. It limits how many coroutines can be inside a section of code at the same time.

## 🔵 सरल परिभाषा (Hindi)
`asyncio.Semaphore(n)` "खाली जगहों" का एक counter है। Task `async with sem:` (या `await sem.acquire()`) से एक slot लेता है और काम खत्म होने पर लौटा देता है। सभी `n` slots भरे हों तो अगला task इंतज़ार करता है। यह सीमित करता है कि एक ही समय में कितनी coroutines code के किसी हिस्से के अंदर हो सकती हैं।

---

## 🔴 Problem it Solves
`gather` over 10,000 URLs opens 10,000 connections at once: the server blocks you, you hit rate limits, file descriptors run out, or the database pool is exhausted. You still want concurrency, but a controlled amount (say 20 at a time). A semaphore gives exactly that, without writing a worker pool.

## 🔴 यह क्यों बना? (Hindi)
10,000 URLs पर `gather` एक साथ 10,000 connections खोल देता है: server आपको block कर देता है, rate limit लग जाती है, file descriptors खत्म हो जाते हैं या database pool भर जाता है। आपको concurrency चाहिए, पर नियंत्रित मात्रा में (जैसे एक बार में 20)। Semaphore ठीक यही देता है, worker pool लिखे बिना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → sem = asyncio.Semaphore(3)   internal counter = 3 free slots
Step 2 → async with sem:  / await sem.acquire()
         counter > 0  -> counter -= 1, continue immediately
         counter == 0 -> the task is suspended in a FIFO waiting line
Step 3 → The task runs its protected section
Step 4 → Leaving the block (even on exception) calls release(): counter += 1
Step 5 → If somebody waits, the oldest waiter is woken and takes the slot
Step 6 → BoundedSemaphore raises ValueError if release() is called more
         times than acquire() (catches bugs); plain Semaphore silently grows
Step 7 → Create it inside a running loop (3.10+ binds the loop lazily)

Semaphore(1) behaves like a Lock. Semaphore(N) = "at most N at once".
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → sem = asyncio.Semaphore(3)   अंदरूनी counter = 3 खाली slots
Step 2 → async with sem:  / await sem.acquire()
         counter > 0  -> counter -= 1, तुरंत आगे बढ़ो
         counter == 0 -> task FIFO waiting line में रुक जाता है
Step 3 → Task अपना सुरक्षित हिस्सा चलाता है
Step 4 → Block छोड़ने पर (exception में भी) release() होता है: counter += 1
Step 5 → कोई इंतज़ार में हो तो सबसे पुराना waiter जागकर slot ले लेता है
Step 6 → BoundedSemaphore में release() की संख्या acquire() से ज़्यादा हो तो
         ValueError आता है (bugs पकड़ता है); सादा Semaphore चुपचाप बढ़ जाता है
Step 7 → इसे चलते loop के अंदर बनाएं (3.10+ में loop lazily जुड़ता है)
```

---

## 🟡 Real World Example
A scraper fetches 5,000 product pages but the shop allows only 10 parallel connections: `Semaphore(10)`. An AI batch job embeds 100,000 texts while the provider limits 50 concurrent requests. A Razorpay reconciliation job opens at most 5 database connections at once to avoid exhausting the pool. A file uploader sends at most 4 files in parallel to keep bandwidth fair.

## 🟡 Real Example Hindi mein
Scraper 5,000 product pages fetch करता है पर दुकान सिर्फ 10 parallel connections देती है: `Semaphore(10)`। AI batch job 100,000 texts की embedding बनाता है जबकि provider एक साथ 50 requests की सीमा रखता है। Razorpay जैसा reconciliation job pool खत्म होने से बचाने के लिए एक समय में सिर्फ 5 database connections खोलता है। File uploader bandwidth बराबर रखने के लिए एक साथ 4 files ही भेजता है।

---

## 💻 Code Example — Basic
```python
# Basic: asyncio.Semaphore
import asyncio                                              # asyncio


async def task(i: int, sem: asyncio.Semaphore, running: list[int]) -> None:
    async with sem:                                         # acquire; released automatically
        running.append(i)                                   # one more inside
        print("inside:", len(running))                      # never more than 2
        await asyncio.sleep(0.05)                           # work while holding the slot
        running.remove(i)                                   # leaving


async def main() -> None:
    sem = asyncio.Semaphore(2)                              # only 2 at a time
    running: list[int] = []                                 # who is inside
    await asyncio.gather(*(task(i, sem, running) for i in range(4)))   # 4 tasks, 2 slots
    print("locked?", sem.locked())                          # False, all released


asyncio.run(main())

# Output (verified on Python 3.13):
# inside: 1
# inside: 2
# inside: 1
# inside: 2
# locked? False
```

## 💻 Code Example — Advanced
```python
# Production style: rate-limited client with Semaphore + BoundedSemaphore + timeout
import asyncio                                              # asyncio
import time                                                 # timing


class LimitedClient:
    """HTTP-like client that allows at most `limit` requests in flight."""

    def __init__(self, limit: int) -> None:
        self._sem = asyncio.Semaphore(limit)                # created inside a running loop context
        self.max_seen = 0                                   # peak concurrency, for the demo
        self._now = 0                                       # current in-flight count

    async def get(self, url: str) -> str:
        async with self._sem:                               # wait for a free slot
            self._now += 1                                  # we are in flight
            self.max_seen = max(self.max_seen, self._now)   # track peak
            try:
                await asyncio.sleep(0.05)                   # network call
                return f"ok {url}"                          # response
            finally:
                self._now -= 1                              # always leave


async def main() -> None:
    client = LimitedClient(limit=3)                         # 3 concurrent max
    start = time.perf_counter()                             # timer
    res = await asyncio.gather(*(client.get(f"/p{i}") for i in range(9)))   # 9 requests
    took = time.perf_counter() - start                      # elapsed
    print(len(res), "peak:", client.max_seen)               # 9 peak: 3
    print("3 waves of 0.05s ~ 0.15s:", 0.14 < took < 0.3)   # 9/3 = 3 waves

    bs = asyncio.BoundedSemaphore(1)                        # raises if released too many times
    await bs.acquire()                                      # take the only slot
    bs.release()                                            # give it back (fine)
    try:                                                    # releasing again is a bug
        bs.release()                                        # too many releases
    except ValueError as exc:                               # BoundedSemaphore catches it
        print("BoundedSemaphore:", exc)                     # message

    sem = asyncio.Semaphore(1)                              # one slot
    await sem.acquire()                                     # take it, never release (simulating a hog)
    try:                                                    # try to get a slot with a deadline
        await asyncio.wait_for(sem.acquire(), timeout=0.05)   # waits, then times out
    except TimeoutError:                                    # asyncio.TimeoutError == TimeoutError (3.11+)
        print("could not get a slot in time")               # fail fast instead of hanging


if __name__ == "__main__":
    asyncio.run(main())

# Output (verified on 3.13; the timing check can be False on a heavily loaded machine):
# 9 peak: 3
# 3 waves of 0.05s ~ 0.15s: True
# BoundedSemaphore: BoundedSemaphore released too many times
# could not get a slot in time
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Limit concurrency | `asyncio.Semaphore(n)` | `p-limit`, `async-sema` (npm) |
| Built into language | yes (stdlib) | no |
| Acquire / release | `async with sem:` | `await sema.acquire()` / `release()` |
| Bug-catching variant | `BoundedSemaphore` | none |
| Typical use | wrap each call, then `gather` | `pLimit(10)(() => fetch(url))` |

```python
# Python way — wrap the call, then gather everything
import asyncio                                           # stdlib

async def fetch(i: int, sem: asyncio.Semaphore) -> int:  # one limited call
    async with sem:                                      # at most 5 inside
        await asyncio.sleep(0.01)                        # I/O
        return i                                         # value

async def main() -> None:
    sem = asyncio.Semaphore(5)                           # 5 slots
    print(len(await asyncio.gather(*(fetch(i, sem) for i in range(20)))))   # 20

asyncio.run(main())
```
```javascript
// JavaScript way — needs the p-limit package
import pLimit from 'p-limit';                            // npm i p-limit
const limit = pLimit(5);                                 // 5 at a time
const results = await Promise.all(
  Array.from({ length: 20 }, (_, i) => limit(async () => i))   // wrap each call
);
console.log(results.length);                             // 20
```

Key difference: Python's semaphore is a primitive with `async with` support in the standard library. In JS you install a package. `Promise.all` alone, like `gather` alone, has no limit.

---

## 🟠 FastAPI Connection
Use a semaphore to protect a scarce resource that all requests share: an upstream API with a rate limit, a GPU model that can run only 2 inferences at once, or a heavy report generator. Create it once at startup, then `async with` inside the endpoint. Run with `TestClient` on 3.13:

```python
# FastAPI example — at most 2 requests inside the guarded section
import asyncio                                            # semaphore
from contextlib import asynccontextmanager                # lifespan helper
from fastapi import FastAPI, Request                      # FastAPI


@asynccontextmanager                                      # startup + shutdown
async def lifespan(app: FastAPI):
    app.state.sem = asyncio.Semaphore(2)                  # created once, inside the running loop
    yield                                                 # app serves requests


app: FastAPI = FastAPI(lifespan=lifespan)                 # attach lifespan


@app.get("/limited")                                      # GET /limited
async def limited(request: Request) -> dict[str, str]:
    async with request.app.state.sem:                     # wait for one of the 2 slots
        await asyncio.sleep(0.01)                         # pretend: call rate-limited upstream
        return {"ok": "yes"}                              # reply
```
To return 429 or 503 instead of making users wait, check `sem.locked()` first, or use `asyncio.wait_for(sem.acquire(), timeout=...)` and map `TimeoutError` to `HTTPException(503)`. Note that the limit is per process: `uvicorn --workers 4` means 4 separate semaphores.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating the tasks but forgetting to wrap the work with the semaphore
✅ Correct: acquire inside each task, not outside the `gather`

```python
# Wrong — semaphore exists but is never used, all 1000 run together
# sem = asyncio.Semaphore(10)
# await asyncio.gather(*(fetch(u) for u in urls))
# Right
# async def limited(u):
#     async with sem: return await fetch(u)
# await asyncio.gather(*(limited(u) for u in urls))
```

❌ Mistake 2: Manual `acquire()` / `release()` without `try/finally`
✅ Correct: use `async with sem:`, which always releases, even on error or cancellation

```python
# Wrong — an exception leaks the slot; after N failures everything deadlocks
# await sem.acquire(); await call(); sem.release()
# Right
# async with sem: await call()
```

❌ Mistake 3: Sharing one asyncio semaphore across threads or processes
✅ Correct: it only works within one event loop. For threads use `threading.Semaphore`; across processes use `multiprocessing.Semaphore` or Redis

```python
# Wrong — asyncio.Semaphore used from worker threads is not thread-safe
# Right — one semaphore per loop, created inside the running loop
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import asyncio
async def main() -> None:
    s = asyncio.Semaphore(1)
    s.release()
    s.release()
    await s.acquire()
    await s.acquire()
    print("two acquires worked, locked:", s.locked())
    await s.acquire()
    print("third acquire worked, locked:", s.locked())
asyncio.run(main())
```
Answer: `two acquires worked, locked: False`, then `third acquire worked, locked: True` (verified on 3.13). A plain `Semaphore(1)` starts with value 1, and each unmatched `release()` increases the counter, so after two releases it has 3 slots. Two acquires leave 1 slot (`locked()` is False); the third takes the last one. With `BoundedSemaphore(1)` the first extra `release()` would raise `ValueError`. That is why `BoundedSemaphore` is the safer default when you manage release by hand.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Lock and Semaphore?
A1: A `Lock` allows exactly one holder at a time (mutual exclusion). A `Semaphore(n)` allows up to n holders. `Semaphore(1)` behaves like a lock but without ownership: any task can release it. Use Lock to protect shared data, Semaphore to limit concurrency or a pool of resources.

Q2: How does a semaphore differ from `gather` in controlling concurrency?
A2: `gather` has no limit: it starts everything it is given. A semaphore inside each coroutine makes the extra ones wait for a slot, so `gather` plus a semaphore gives "run all, but only N at a time". An alternative is a fixed number of worker tasks reading from an `asyncio.Queue`.

Q3: What does `BoundedSemaphore` add?
A3: It raises `ValueError("BoundedSemaphore released too many times")` if you release more than you acquired, which exposes logic bugs. A plain `Semaphore` just increases its counter, silently allowing more concurrency than you intended.

Q4: Is waiting for a semaphore fair?
A4: Waiters are woken in FIFO order, so the first to wait is the first to get the slot. Cancelling a waiting task removes it from the line without losing a slot, so timeouts such as `asyncio.wait_for(sem.acquire(), 1)` are safe.

Q5: Does a semaphore make CPU-bound work parallel?
A5: No. It only limits how many coroutines are inside a section; it does not add threads or processes. The event loop still runs one coroutine at a time. It is a tool for protecting I/O resources, not for CPU speed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must obey a rate or concurrency limit of an external service
- You protect a limited pool (DB connections, file handles, GPU slots)
- You use `gather` on a big list and want bounded concurrency
- You need a simple wait-for-a-slot with a timeout

❌ Avoid when:
- You need strict mutual exclusion; use `asyncio.Lock`
- You need requests-per-second limits (token bucket) rather than "in flight" limits
- Threads or processes are involved; use their own semaphores
- A fixed set of workers with a queue fits better (it also adds back-pressure)

---

## 📊 Visual Diagram
```
 Semaphore(2)      slots: [ A ][ B ]        waiting line: C -> D -> E

 time 0   A, B enter the block      C, D, E are suspended
 time 1   A leaves   -> release()   C is woken and takes the slot
 time 2   B leaves   -> release()   D takes the slot
 ...
 never more than 2 tasks inside `async with sem:`

 Lock = Semaphore(1) (but only the owner is supposed to release)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Semaphore | Counter of free slots | खाली slots का counter |
| `acquire` / `release` | Take / give back a slot | Slot लेना / लौटाना |
| `BoundedSemaphore` | Semaphore that errors on extra release | अतिरिक्त release पर error देने वाला semaphore |
| Rate limit | Maximum calls allowed | अनुमत calls की अधिकतम संख्या |
| In flight | Started but not finished | शुरू हुआ पर खत्म नहीं हुआ |
| FIFO | First waiting task gets the slot first | पहले इंतज़ार करने वाले को पहले slot |

---

## ⚡ 3-Line Summary
English: `asyncio.Semaphore(n)` lets at most n coroutines enter a block at once; the others wait in a FIFO line. Use `async with sem:` inside each task, then `gather` them, to get controlled concurrency. Prefer `BoundedSemaphore` to catch extra releases, and remember it works only inside one event loop.
Hindi: `asyncio.Semaphore(n)` एक समय में ज़्यादा से ज़्यादा n coroutines को block में आने देता है; बाकी FIFO line में इंतज़ार करती हैं। नियंत्रित concurrency के लिए हर task के अंदर `async with sem:` लगाएं और फिर उन्हें `gather` करें। अतिरिक्त release पकड़ने के लिए `BoundedSemaphore` लें, और याद रखें कि यह सिर्फ एक event loop के अंदर काम करता है।

---

## ➡️ Next Topic
**247. aiohttp — Async HTTP** — a real async HTTP client and server library, where semaphores and `gather` are used every day to fetch many URLs politely.
