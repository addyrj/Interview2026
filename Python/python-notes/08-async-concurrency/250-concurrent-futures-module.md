---

# 250. Concurrent.futures Module
# हिंदी में: concurrent.futures Module (Thread/Process Pool का आसान API)

---

## 🔵 Simple Definition (English)
`concurrent.futures` gives one simple interface to run functions in a pool of threads (`ThreadPoolExecutor`) or processes (`ProcessPoolExecutor`). You submit work and get back a `Future`, an object that holds the result when it is ready.

## 🔵 सरल परिभाषा (Hindi)
`concurrent.futures` threads (`ThreadPoolExecutor`) या processes (`ProcessPoolExecutor`) के pool में functions चलाने का एक सरल interface देता है। आप काम submit करते हैं और बदले में `Future` मिलता है, जो तैयार होने पर result रखता है।

---

## 🔴 Problem it Solves
Using `threading.Thread` or `multiprocessing.Process` directly means creating, starting, joining workers, passing results through queues and handling exceptions by hand. It is long and error-prone. `concurrent.futures` hides all that: a pool reuses workers, collects return values, and re-raises exceptions in your code.

## 🔴 यह क्यों बना? (Hindi)
सीधे `threading.Thread` या `multiprocessing.Process` इस्तेमाल करने पर workers बनाना, start करना, join करना, queues से results लेना और exceptions हाथ से संभालना पड़ता है। यह लंबा और गलती-प्रवण है। `concurrent.futures` यह सब छिपा देता है: pool workers दोबारा इस्तेमाल करता है, return values इकट्ठा करता है और exceptions आपके code में फिर से उठाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → with ThreadPoolExecutor(max_workers=N) as ex:  creates N workers
Step 2 → ex.submit(fn, *args) queues the job, returns a Future at once
Step 3 → A free worker takes the job and runs fn(*args)
Step 4 → future.result() waits and returns the value (or re-raises the exception)
Step 5 → ex.map(fn, items) = many submits, results come back IN INPUT ORDER
Step 6 → as_completed(futures) yields futures in the order they FINISH
Step 7 → Leaving the "with" block waits for all jobs and shuts the pool down
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → with ThreadPoolExecutor(max_workers=N) as ex:  N workers बनाता है
Step 2 → ex.submit(fn, *args) job queue में डालता है, तुरंत Future लौटाता है
Step 3 → कोई खाली worker job लेकर fn(*args) चलाता है
Step 4 → future.result() इंतजार करके value देता है (या exception फिर से उठाता है)
Step 5 → ex.map(fn, items) = कई submits, results INPUT के क्रम में आते हैं
Step 6 → as_completed(futures) futures को खत्म होने के क्रम में देता है
Step 7 → "with" block छोड़ने पर सारी jobs का इंतजार होता है और pool बंद होता है
```

---

## 🟡 Real World Example
A report service must download 200 invoices from S3 and email-check 50 addresses: I/O-bound, so `ThreadPoolExecutor(max_workers=20)` finishes in seconds instead of minutes. An image-processing API resizes 1000 photos: CPU-bound, so `ProcessPoolExecutor` uses every core. In a FastAPI app, `loop.run_in_executor(pool, blocking_fn)` runs old blocking libraries without freezing the event loop.

## 🟡 Real Example Hindi mein
Report service को S3 से 200 invoices download करने और 50 email addresses जांचने हैं: यह I/O-bound है, इसलिए `ThreadPoolExecutor(max_workers=20)` मिनटों की जगह सेकंडों में खत्म करता है। Image-processing API 1000 photos resize करती है: यह CPU-bound है, इसलिए `ProcessPoolExecutor` हर core इस्तेमाल करता है। FastAPI app में `loop.run_in_executor(pool, blocking_fn)` पुरानी blocking libraries को event loop रोके बिना चलाता है।

---

## 💻 Code Example — Basic
```python
# Basic concurrent.futures (verified on Python 3.13)
import time                                              # sleep + timer
from concurrent.futures import ThreadPoolExecutor        # thread pool


def slow(n: int) -> int:                                 # pretend I/O work
    time.sleep(0.2)                                      # wait 0.2 s
    return n * n                                         # return the square


if __name__ == "__main__":                               # needed for process pools; good habit
    with ThreadPoolExecutor(max_workers=5) as ex:        # pool of 5 threads
        f = ex.submit(slow, 3)                           # run slow(3) in background
        print(f.result())                                # wait for it -> 9
        print(list(ex.map(slow, [1, 2, 3])))             # run 3 jobs, results in order

    t: float = time.perf_counter()                       # start timer
    with ThreadPoolExecutor(max_workers=10) as ex:       # 10 threads
        out = list(ex.map(slow, range(10)))              # 10 jobs x 0.2 s each
    print(out, round(time.perf_counter() - t, 1))        # ~0.2 s total, not 2 s

# Output:
# 9
# [1, 4, 9]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81] 0.2
```

## 💻 Code Example — Advanced
```python
# Production style: as_completed, exception handling, process pool, timeout
import time                                              # sleep
from concurrent.futures import (                         # everything we need
    ThreadPoolExecutor, ProcessPoolExecutor, Future, as_completed,
)


def risky(n: int) -> int:                                # a job that can fail
    if n == 2:                                           # job 2 always fails
        raise ValueError("bad 2")                        # raise inside worker thread
    return n                                             # others succeed


def cpu(n: int) -> int:                                  # CPU-heavy job (top-level => picklable)
    return sum(i * i for i in range(n))                  # sum of squares


def slow(n: int) -> int:                                 # slow job
    time.sleep(0.2)                                      # sleep
    return n * n                                         # square


if __name__ == "__main__":                               # REQUIRED for ProcessPoolExecutor on macOS/Windows
    with ThreadPoolExecutor(max_workers=3) as ex:        # thread pool
        futs: dict[Future[int], int] = {ex.submit(risky, n): n for n in range(4)}   # future -> input
        for fu in as_completed(futs):                    # handle in FINISH order
            try:
                print("ok", futs[fu], fu.result())       # result() re-raises worker exception
            except ValueError as e:                      # catch it here, in the main thread
                print("err", futs[fu], e)                # report which input failed

    with ProcessPoolExecutor(max_workers=2) as ex:       # process pool: real parallelism for CPU work
        print(list(ex.map(cpu, [10, 100, 1000])))        # results in input order

    with ThreadPoolExecutor(max_workers=1) as ex:        # single worker
        f = ex.submit(slow, 1)                           # start job
        print(f.done(), f.result(timeout=2), f.done())   # not done -> wait -> done

# Output (the ok/err lines may appear in a different ORDER on each run):
# err 2 bad 2
# ok 1 1
# ok 0 0
# ok 3 3
# [285, 328350, 332833500]
# False 1 True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Future / result holder | `Future` | `Promise` |
| Run in background thread | `ThreadPoolExecutor.submit` | `new Worker()` / worker_threads |
| Many jobs, ordered results | `ex.map` | `Promise.all(arr.map(...))` |
| First to finish | `as_completed` | `Promise.race` / `allSettled` |
| Pool of workers | built in | libraries (piscina) |
| Exceptions | `future.result()` re-raises | `await promise` throws |

```python
# Python way
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor() as ex:                         # pool
    print(list(ex.map(lambda x: x * 2, [1, 2, 3])))      # [2, 4, 6]
```
```javascript
// JavaScript way — async I/O is already non-blocking, so Promise.all is enough
const out = await Promise.all([1, 2, 3].map(async x => x * 2));   // [2, 4, 6]
// For CPU work you need worker_threads or a pool library like piscina
```

Key difference: JS I/O is already async in one thread, so you rarely need a pool except for CPU work. In Python, blocking libraries (`requests`, `boto3`, PIL) block the thread, so pools are the standard way to get concurrency.

---

## 🟠 FastAPI Connection
FastAPI runs plain `def` endpoints in a thread pool for you. For blocking code inside `async def`, hand it to an executor so the event loop stays free. CPU-heavy work needs a `ProcessPoolExecutor`.

```python
# FastAPI example — blocking and CPU work off the event loop
import asyncio                                           # get_running_loop
import time                                              # blocking sleep
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor   # pools
from fastapi import FastAPI                              # FastAPI

app: FastAPI = FastAPI()                                 # app
io_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=8)       # for blocking I/O libs
cpu_pool: ProcessPoolExecutor = ProcessPoolExecutor(max_workers=2)    # for CPU work


def blocking_report() -> str:                            # old sync library call
    time.sleep(0.5)                                      # blocks only its own thread
    return "report ready"                                # result


def heavy(n: int) -> int:                                # CPU job, top-level so it can be pickled
    return sum(i * i for i in range(n))                  # compute


@app.get("/report")                                      # GET /report
async def report() -> dict[str, str]:
    loop = asyncio.get_running_loop()                    # current event loop
    msg: str = await loop.run_in_executor(io_pool, blocking_report)   # await a thread job
    return {"msg": msg}                                  # reply


@app.get("/heavy/{n}")                                   # GET /heavy/1000000
async def heavy_ep(n: int) -> dict[str, int]:
    loop = asyncio.get_running_loop()                    # loop
    return {"sum": await loop.run_in_executor(cpu_pool, heavy, n)}   # run in another process
```
(Pattern; `run_in_executor` itself was verified in the performance topic below, these endpoints were not served.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `ThreadPoolExecutor` for CPU-heavy work
✅ Correct: use `ProcessPoolExecutor` (the GIL stops threads from running Python code in parallel)

```python
# Wrong — 4 threads, still ~1 core of work
# ThreadPoolExecutor(4).map(cpu, [3_000_000] * 4)
# Right
# ProcessPoolExecutor(4).map(cpu, [3_000_000] * 4)
```

❌ Mistake 2: Missing `if __name__ == "__main__":` with process pools
✅ Correct: guard the entry point (macOS/Windows use "spawn", which re-imports your file)

```python
# Wrong: executor created at import time -> RuntimeError / endless spawning
# ex = ProcessPoolExecutor()
# Right
# if __name__ == "__main__":
#     with ProcessPoolExecutor() as ex: ...
```

❌ Mistake 3: Never calling `.result()` so errors vanish
✅ Correct: exceptions are stored inside the Future; call `result()` (or `exception()`)

```python
# Wrong — the ValueError is silently swallowed
# ex.submit(risky, 2)
# Right
# ex.submit(risky, 2).result()    # raises ValueError here
```

---

## 🧠 Tricky Interview Question

```python
# What is printed? (assume each call takes a different time)
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def work(n: int) -> int:
    time.sleep(3 - n)          # work(0) takes 3s, work(2) takes 1s
    return n

with ThreadPoolExecutor(3) as ex:
    print(list(ex.map(work, [0, 1, 2])))
    futs = [ex.submit(work, n) for n in [0, 1, 2]]
    print([f.result() for f in as_completed(futs)])
```
Answer: First line: `[0, 1, 2]`. `map` always returns results in INPUT order, even though work(2) finishes first. Second line: `[2, 1, 0]`. `as_completed` yields futures in the order they FINISH, so the fastest job (n=2, 1 second) comes first. If you need input order, use `map` or keep a list of futures; if you want to react to the quickest result, use `as_completed`.

---

## ⚫ Interview Questions + Answers

Q1: ThreadPoolExecutor vs ProcessPoolExecutor?
A1: Threads share memory and are cheap, good for I/O-bound tasks (the GIL is released while waiting). Processes have separate memory and GIL, so they give real CPU parallelism, but arguments and results must be picklable and start-up cost is higher.

Q2: What is a Future?
A2: A handle for a result that is not ready yet. Methods: `result(timeout)`, `exception()`, `done()`, `cancel()`, `add_done_callback(fn)`. A running job cannot be cancelled, only pending ones.

Q3: What is the default `max_workers`?
A3: For threads: `min(32, cpu_count + 4)` (since 3.8). For processes: `cpu_count`. From Python 3.13 the count comes from `os.process_cpu_count()` (CPUs this process may use) instead of `os.cpu_count()`. Set it explicitly in production.

Q4: `map` vs `submit`?
A4: `map` is simple, returns results in order, and raises the first exception when iterating. `submit` gives you a Future per job for finer control (as_completed, callbacks, per-job error handling).

Q5: What happens when the `with` block ends?
A5: `shutdown(wait=True)` is called: no new jobs, and it waits for all submitted jobs. Use `shutdown(wait=False, cancel_futures=True)` (3.9+) to drop queued jobs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Running blocking I/O functions concurrently (HTTP, files, SDK calls)
- CPU-bound batch work across cores (ProcessPool)
- Wrapping blocking code inside asyncio via `run_in_executor`

❌ Avoid when:
- You already have async libraries (use `asyncio` + aiohttp/asyncpg)
- Tasks need heavy shared mutable state (race conditions; use queues or processes)
- Tasks are tiny: pool overhead is bigger than the work

---

## 📊 Visual Diagram
```
 main thread
    │ submit(fn, a)     submit(fn, b)     submit(fn, c)
    ▼                       ▼                 ▼
  Future A              Future B           Future C
    │                       │                 │
 ┌──────────── pool: worker 1 | worker 2 | worker 3 ───────────┐
 │ takes jobs from an internal queue, runs fn, stores result   │
 └─────────────────────────────────────────────────────────────┘
    │
 f.result() <- blocks until done, or re-raises the worker's exception

 map(): results in input order      as_completed(): results in finish order
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Executor | Object that runs jobs in a pool | Pool में jobs चलाने वाला |
| Future | Placeholder for a future result | आने वाले result का placeholder |
| Worker | Thread/process that runs jobs | Job चलाने वाला thread/process |
| as_completed | Iterate futures as they finish | खत्म होते क्रम में futures |
| Picklable | Can be sent to another process | दूसरे process में भेजा जा सकने वाला |
| GIL | Lock letting one thread run Python at a time | एक समय में एक thread की lock |

---

## ⚡ 3-Line Summary
English: `concurrent.futures` offers thread and process pools with a clean `submit` / `map` / `Future` API. Use threads for I/O, processes for CPU work, and always call `result()` so exceptions are not lost.
Hindi: `concurrent.futures` thread और process pools को साफ `submit` / `map` / `Future` API के साथ देता है। I/O के लिए threads, CPU काम के लिए processes इस्तेमाल करें, और exceptions खोने से बचने के लिए हमेशा `result()` बुलाएं।

---

## ➡️ Next Topic
**251. asyncio vs Threading vs Multiprocessing** — a side-by-side comparison with numbers.
