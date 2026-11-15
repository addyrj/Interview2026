---

# 228. Thread Pool (ThreadPoolExecutor)
# हिंदी में: Thread Pool (ThreadPoolExecutor - threads का पूल)

---

## 🔵 Simple Definition (English)
`ThreadPoolExecutor` (in `concurrent.futures`) keeps a fixed set of worker threads and feeds them tasks. You call `submit()` or `map()`, and get back `Future` objects that hold the result or the exception. It handles starting, reusing and stopping threads for you.

## 🔵 सरल परिभाषा (Hindi)
`ThreadPoolExecutor` (`concurrent.futures` में) worker threads का एक तय समूह रखता है और उन्हें tasks देता है। आप `submit()` या `map()` call करते हैं और `Future` objects मिलते हैं जिनमें result या exception होता है। Threads को शुरू करना, दोबारा इस्तेमाल करना और बंद करना यह खुद संभालता है।

---

## 🔴 Problem it Solves
Creating one `Thread` per task is wasteful (startup cost, memory) and dangerous (10,000 tasks = 10,000 threads). Manually collecting results and errors from threads is awkward. A pool caps the number of threads, reuses them, and gives a clean result/exception API.

## 🔴 यह क्यों बना? (Hindi)
हर task के लिए एक `Thread` बनाना महँगा (startup cost, memory) और खतरनाक है (10,000 tasks = 10,000 threads)। Threads से result और errors हाथ से इकट्ठा करना असुविधाजनक है। Pool threads की संख्या सीमित रखता है, उन्हें दोबारा इस्तेमाल करता है और result/exception का साफ API देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pool = ThreadPoolExecutor(max_workers=N)
Step 2 → future = pool.submit(fn, *args)       task goes into an internal queue
Step 3 → an idle worker thread takes it and runs fn
Step 4 → future.result() returns the value (or re-raises the exception)
Step 5 → pool.shutdown(wait=True) / "with" block waits and stops the workers
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pool = ThreadPoolExecutor(max_workers=N)
Step 2 → future = pool.submit(fn, *args)       task अंदरूनी queue में जाता है
Step 3 → खाली worker thread उसे लेकर fn चलाता है
Step 4 → future.result() value देता है (या exception दोबारा उठाता है)
Step 5 → pool.shutdown(wait=True) / "with" block इंतज़ार करके workers बंद करता है
```

---

## 🟡 Real World Example
A travel-aggregator API (MakeMyTrip style) must query 6 airline SDKs, all blocking libraries. A pool of 6 threads calls them in parallel, so the page loads in the time of the slowest vendor instead of the sum of all. A data pipeline downloads 500 files from S3 with `max_workers=16`. An AI app calls an embedding API for 100 chunks in parallel.

## 🟡 Real Example Hindi mein
Travel-aggregator API (MakeMyTrip जैसी) को 6 airline SDKs से पूछना है, सब blocking libraries हैं। 6 threads का pool उन्हें parallel call करता है, इसलिए page सबसे धीमे vendor के समय में लोड होता है, सबके जोड़ में नहीं। Data pipeline `max_workers=16` से S3 की 500 files download करती है। AI app 100 chunks के लिए embedding API parallel call करता है।

---

## 💻 Code Example — Basic
```python
# Basic ThreadPoolExecutor - every line commented
import time  # sleep
from concurrent.futures import ThreadPoolExecutor, as_completed, Future  # pool and helpers
from typing import Tuple  # type hints


def fetch(i: int) -> Tuple[int, str]:  # simulated blocking call
    time.sleep(0.05 * (3 - i % 3))  # different durations
    if i == 4:  # one task fails
        raise ValueError(f"bad {i}")  # error inside the worker
    return i, f"page-{i}"  # result


with ThreadPoolExecutor(max_workers=3, thread_name_prefix="fx") as ex:  # pool; "with" shuts it down
    print(list(ex.map(lambda i: i * 2, range(5))))  # map: results in INPUT order
    # Output: [0, 2, 4, 6, 8]

    f: Future = ex.submit(fetch, 1)  # submit: returns a Future immediately
    print(f.result(), f.done(), type(f).__name__)  # result() waits for the value
    # Output: (1, 'page-1') True Future

    futs = {ex.submit(fetch, i): i for i in range(6)}  # submit several, remember the id
    ok, bad = [], []  # successes and failures
    for fut in as_completed(futs):  # yields futures as they FINISH (fastest first)
        try:  # result() re-raises worker exceptions
            ok.append(fut.result())  # store the success
        except ValueError as e:  # handle the failing task
            bad.append(str(e))  # store the error text
    print(sorted(ok), bad)  # sorted for stable display
    # Output: [(0, 'page-0'), (1, 'page-1'), (2, 'page-2'), (3, 'page-3'), (5, 'page-5')] ['bad 4']
```

## 💻 Code Example — Advanced
```python
# Production style: timeouts, wait(), callbacks, thread reuse, shutdown behaviour, map errors
import os  # cpu count
import threading  # thread names
import time  # sleep
from concurrent.futures import (  # everything we need
    FIRST_COMPLETED, Future, ThreadPoolExecutor, wait,
    TimeoutError as FutureTimeout,
)

with ThreadPoolExecutor(3) as ex:  # pool of three
    slow: Future = ex.submit(time.sleep, 0.3)  # a slow task
    try:  # wait only 50 ms for it
        slow.result(timeout=0.05)  # raises if not ready
    except FutureTimeout:  # the TASK keeps running, only our wait gave up
        print("timeout")
    # Output: timeout

    done, pending = wait(  # wait for the first one to finish
        [ex.submit(time.sleep, 0.01), ex.submit(time.sleep, 0.3)],  # a fast and a slow task
        return_when=FIRST_COMPLETED,  # do not wait for all
    )
    print(len(done), len(pending))  # one done, one still running
    # Output: 1 1


def on_done(f: Future) -> None:  # callback runs when the future completes
    print("callback:", f.result())  # use the result


with ThreadPoolExecutor(1) as ex:  # single worker
    ex.submit(lambda: 42).add_done_callback(on_done)  # attach callback
# Output: callback: 42

with ThreadPoolExecutor(2, thread_name_prefix="w") as ex:  # two workers
    names = set(ex.map(lambda _: threading.current_thread().name, range(10)))  # 10 tasks
print(sorted(names) <= ["w_0", "w_1"], len(names))  # only two threads did all the work (reuse)
# Output: True 2

pool = ThreadPoolExecutor(1)  # a pool we shut down manually
pool.shutdown()  # no new work accepted
try:  # submit after shutdown
    pool.submit(print)  # not allowed
except RuntimeError as e:  # explicit error
    print("RuntimeError:", e)
# Output: RuntimeError: cannot schedule new futures after shutdown

with ThreadPoolExecutor(2) as ex:  # map and exceptions
    it = ex.map(lambda i: 1 / i, [1, 0, 2])  # the second item will fail
    print(next(it))  # first result is fine
    # Output: 1.0
    try:  # error appears only when you iterate to that item
        next(it)  # raises ZeroDivisionError here
    except ZeroDivisionError as e:  # caught
        print("ZeroDivisionError:", e)
    # Output: ZeroDivisionError: division by zero

print(min(32, (os.cpu_count() or 1) + 4))  # default max_workers since Python 3.8
# Output: 12   (on an 8-core machine; the cap is 32)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
with ThreadPoolExecutor(5) as ex:
    results = list(ex.map(fetch, urls))        # parallel, ordered results
```

```javascript
// JavaScript: promises, with an optional limit (p-limit)
const results = await Promise.all(urls.map(u => fetch(u)));        // all at once
// Promise.allSettled(...) to keep going when some fail
// CPU work: Piscina / worker_threads is the thread-pool equivalent
```

Key differences: JS `Promise.all` plays the role of `map` for I/O without any threads. Python needs a thread pool only for blocking libraries. A `Future` is the Python version of a Promise: `result()` blocks (JS uses `await`).

---

## 🟠 FastAPI Connection
Inside a sync endpoint, fan out to several blocking vendor calls with a shared pool. For `async def` endpoints use `await loop.run_in_executor(pool, fn)` or `asyncio.to_thread`.

```python
import time  # sleep
from concurrent.futures import ThreadPoolExecutor  # pool
from typing import Dict, List  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # create app
pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=4)  # shared pool

def call_vendor(vendor: str) -> Dict[str, str]:  # blocking vendor SDK call
    time.sleep(0.1)  # pretend network
    return {"vendor": vendor, "price": "100"}  # fake response

@app.get("/prices")  # fan-out to many vendors
def prices() -> List[Dict[str, str]]:  # sync endpoint
    return list(pool.map(call_vendor, ["a", "b", "c", "d"]))  # parallel calls

client = TestClient(app)
t = time.perf_counter()
print(client.get("/prices").json()[:2])
# Output: [{'vendor': 'a', 'price': '100'}, {'vendor': 'b', 'price': '100'}]
print("fast (parallel):", time.perf_counter() - t < 0.3)
# Output: fast (parallel): True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling `.result()` inside the submit loop
```python
# Wrong - waits for each task before submitting the next: no parallelism
for u in urls:
    results.append(ex.submit(fetch, u).result())

# Correct - submit all, then collect
futs = [ex.submit(fetch, u) for u in urls]
results = [f.result() for f in futs]
```

❌ Mistake 2: Ignoring exceptions (they hide inside the Future)
```python
# Wrong - the error is silently lost
ex.submit(risky)

# Correct
f = ex.submit(risky)
f.result()                     # re-raises, or add_done_callback to log
```

❌ Mistake 3: Using a pool for CPU-bound work
```python
# Wrong - GIL: threads give no speedup
ThreadPoolExecutor(8).map(cpu_heavy, data)

# Correct
ProcessPoolExecutor(8).map(cpu_heavy, data)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output order?

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def f(n):
    time.sleep(n)
    return n

with ThreadPoolExecutor(3) as ex:
    print(list(ex.map(f, [0.3, 0.1, 0.2])))
    futs = [ex.submit(f, n) for n in (0.3, 0.1, 0.2)]
    print([x.result() for x in as_completed(futs)])
```

**Answer**:
```
[0.3, 0.1, 0.2]
[0.1, 0.2, 0.3]
```
`map` returns results in input order (it waits for the first even if later ones finish sooner). `as_completed` yields futures in completion order.

---

## ⚫ Interview Questions + Answers

Q1: `map` vs `submit`?
A1: `map` applies one function to many inputs and yields results in input order. `submit` schedules a single call and returns a Future, giving finer control (callbacks, per-task error handling, `as_completed`).

Q2: What is the default `max_workers`?
A2: Since Python 3.8: `min(32, os.cpu_count() + 4)`. Tune it based on how many concurrent calls the downstream service can take.

Q3: What happens if a task raises?
A3: The exception is stored in the Future and re-raised by `result()`. With `map` it is raised when you reach that item in iteration.

Q4: Can you cancel a running task?
A4: `future.cancel()` works only for tasks that have not started. A running thread cannot be stopped; use an `Event` the task checks.

Q5: ThreadPoolExecutor vs asyncio?
A5: A pool fits blocking libraries and moderate parallelism (tens of threads). asyncio scales to thousands of connections but needs async libraries.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Many blocking I/O calls (HTTP with `requests`, SDKs, file downloads)
- You want results/exceptions as Futures

❌ Avoid when:
- CPU-bound work (use ProcessPoolExecutor)
- Thousands of connections (use asyncio)
- Tasks depend on each other in complex ways (design a pipeline or use queues)

---

## 📊 Visual Diagram

```
 submit(task) ─► [ internal queue ] ─► worker-1 ─┐
 submit(task) ─►  task task task  ─► worker-2 ─┼─► Future.result()
 submit(task) ─►                  ─► worker-3 ─┘
                 (threads are reused, never more than max_workers)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Executor | Runs callables in workers | workers में callables चलाने वाला |
| Future | Placeholder for a result | result का placeholder |
| submit | Schedule one call | एक call schedule करना |
| map | Apply fn to many inputs | कई inputs पर fn चलाना |
| as_completed | Futures in finish order | खत्म होने के क्रम में futures |
| max_workers | Thread limit | threads की सीमा |

---

## ⚡ 3-Line Summary
English: `ThreadPoolExecutor` reuses a capped set of threads and returns Futures for results and errors. Submit everything first, then collect; use `as_completed` for fastest-first. Use it for blocking I/O, not CPU work.
Hindi: `ThreadPoolExecutor` सीमित threads को दोबारा इस्तेमाल करता है और result व errors के लिए Futures देता है। पहले सब submit करें, फिर collect करें; सबसे पहले खत्म होने वाले के लिए `as_completed`। इसे blocking I/O के लिए इस्तेमाल करें, CPU काम के लिए नहीं।

---

## ➡️ Next Topic
**229. GIL** is covered already; continue with **230. GIL — Impact on Threading**.
