---

# 236. multiprocessing vs threading
# हिंदी में: multiprocessing बनाम threading — कब कौन सा?

---

## 🔵 Simple Definition (English)
Threads are several workers inside ONE process that share memory but take turns running Python code (the GIL). Processes are separate programs with their own memory and their own GIL, so they run Python code truly in parallel. Threads suit waiting (I/O); processes suit computing (CPU).

## 🔵 सरल परिभाषा (Hindi)
Threads एक ही process के अंदर कई workers हैं जो memory share करते हैं लेकिन Python code बारी-बारी चलाते हैं (GIL)। Processes अलग programs हैं जिनकी अपनी memory और अपना GIL होता है, इसलिए वे Python code सच में parallel चलाते हैं। Threads इंतज़ार वाले काम (I/O) के लिए और processes गणना वाले काम (CPU) के लिए सही हैं।

---

## 🔴 Problem it Solves
Beginners pick the wrong tool: they add threads to a CPU loop and see no speedup, or they start 100 processes for HTTP calls and run out of RAM. Knowing the difference (GIL, memory, startup cost, communication) tells you which one to use for each job.

## 🔴 यह क्यों बना? (Hindi)
नए लोग गलत tool चुन लेते हैं: CPU loop में threads लगाते हैं और speedup नहीं मिलता, या HTTP calls के लिए 100 processes चालू कर देते हैं और RAM खत्म हो जाती है। फर्क जानना (GIL, memory, startup cost, communication) बताता है कि किस काम के लिए कौन सा इस्तेमाल करें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Threading: one process, N threads, ONE GIL, shared memory
Step 2 → Only the thread holding the GIL runs Python bytecode
Step 3 → A thread waiting on I/O (socket, disk, sleep) RELEASES the GIL,
         so other threads run -> good for I/O
Step 4 → Multiprocessing: N processes, N GILs, separate memory
Step 5 → All N can run Python code at the same moment on N cores -> good for CPU
Step 6 → Processes talk through pickled messages or shared memory;
         threads simply read/write the same variables (and need locks)

            threads                          processes
   +--------------------+        +---------+  +---------+  +---------+
   | one process, 1 GIL |        | proc 1  |  | proc 2  |  | proc 3  |
   | T1  T2  T3  (take  |        | GIL 1   |  | GIL 2   |  | GIL 3   |
   |  turns on Python)  |        +---------+  +---------+  +---------+
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Threading: एक process, N threads, एक GIL, shared memory
Step 2 → जिस thread के पास GIL है सिर्फ वही Python bytecode चलाता है
Step 3 → I/O (socket, disk, sleep) पर इंतज़ार करने वाला thread GIL छोड़ देता है,
         तब दूसरे threads चलते हैं -> I/O के लिए अच्छा
Step 4 → Multiprocessing: N processes, N GILs, अलग memory
Step 5 → सभी N एक ही समय N cores पर Python code चला सकते हैं -> CPU के लिए अच्छा
Step 6 → Processes pickled messages या shared memory से बात करते हैं;
         threads बस वही variables पढ़-लिख लेते हैं (और locks चाहिए)
```

---

## 🟡 Real World Example
A Razorpay-style reconciliation job downloads 500 settlement files from banks (waiting on network: use threads, 32 of them) and then computes checksums and parses each file (CPU: use a process pool). A Flask/Gunicorn app often uses several worker processes (to use all cores) and several threads per worker (to overlap DB waits). An image-resize endpoint uses processes; a webhook fan-out to 50 URLs uses threads or asyncio.

## 🟡 Real Example Hindi mein
Razorpay जैसा reconciliation job banks से 500 settlement files download करता है (network का इंतज़ार: threads, 32 की संख्या में) और फिर हर file का checksum और parsing करता है (CPU: process pool)। Flask/Gunicorn app में अक्सर कई worker processes (सभी cores इस्तेमाल के लिए) और हर worker में कई threads (DB waits को overlap करने के लिए) होते हैं। Image-resize endpoint processes इस्तेमाल करता है; 50 URLs को webhook भेजना threads या asyncio से होता है।

---

## 💻 Code Example — Basic
```python
# Basic: CPU-bound task, threads vs processes
import time                                                 # timing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor   # both pools


def burn(n: int) -> int:                                    # pure CPU work
    return sum(i * i for i in range(n))                     # holds the GIL


if __name__ == "__main__":
    jobs = [3_000_000] * 4                                  # four equal jobs
    t = time.perf_counter()                                 # start timer
    with ThreadPoolExecutor(4) as ex:                       # threads: GIL blocks parallelism
        list(ex.map(burn, jobs))                            # run
    t_threads = time.perf_counter() - t                     # elapsed
    t = time.perf_counter()                                 # restart timer
    with ProcessPoolExecutor(4) as ex:                      # processes: each has own GIL
        list(ex.map(burn, jobs))                            # run
    t_procs = time.perf_counter() - t                       # elapsed
    print("threads slower than processes:", t_threads > t_procs)   # True on multi-core machines

# Output (timings vary; the boolean was True on this multi-core machine, Python 3.13):
# threads slower than processes: True
```
Note: on the free-threaded build of Python 3.13+ (`python3.13t`, experimental), threads can also run CPU code in parallel. The default build still has the GIL.

## 💻 Code Example — Advanced
```python
# Production style: pick the right executor, show memory isolation and pickling limits
import os                                                   # process ids
import time                                                 # sleeping / timing
from concurrent.futures import Executor, ThreadPoolExecutor, ProcessPoolExecutor   # pools
from typing import Literal                                  # types

state: dict[str, int] = {"hits": 0}                         # module-level data


def touch(_: int) -> int:                                   # mutates global state
    state["hits"] += 1                                      # in a thread: shared; in a process: a copy
    return os.getpid()                                      # which process ran this


def fake_io(_: int) -> None:                                # simulates a network call
    time.sleep(0.2)                                         # releases the GIL while waiting


def make_executor(kind: Literal["io", "cpu"], workers: int = 4) -> Executor:
    """Return the right pool for the job type."""
    if kind == "cpu":                                       # CPU-bound -> processes
        return ProcessPoolExecutor(max_workers=workers)     # one GIL per process
    return ThreadPoolExecutor(max_workers=workers)          # I/O-bound -> threads (cheap)


def main() -> None:
    with make_executor("io") as ex:                         # threads
        pids = set(ex.map(touch, range(4)))                 # all ran in this same process
    print("threads: same pid:", pids == {os.getpid()}, "| hits in parent:", state["hits"])

    state["hits"] = 0                                       # reset
    with make_executor("cpu") as ex:                        # processes
        pids = set(ex.map(touch, range(4)))                 # ran in child processes
    print("procs: different pid:", os.getpid() not in pids, "| hits in parent:", state["hits"])

    start = time.perf_counter()                             # time 8 sleeps
    with make_executor("io", workers=8) as ex:              # 8 threads
        list(ex.map(fake_io, range(8)))                     # all sleep together
    print("8 x 0.2s sleeps in threads took < 0.6s:", time.perf_counter() - start < 0.6)

    try:                                                    # processes need picklable callables
        with ProcessPoolExecutor(1) as ex:                  # one worker
            ex.submit(lambda: 1).result()                   # lambdas cannot be pickled
    except Exception as exc:                                # catch pickling failure
        print("process pool error:", type(exc).__name__)    # shows the error class


if __name__ == "__main__":
    main()

# Output (verified on 3.13):
# threads: same pid: True | hits in parent: 4
# procs: different pid: True | hits in parent: 0
# 8 x 0.2s sleeps in threads took < 0.6s: True
# process pool error: AttributeError    (the class name varies by Python version, e.g. PicklingError)
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python threads | Python processes | Node.js |
|---------|----------------|------------------|---------|
| Parallel CPU code | no (GIL) | yes | `worker_threads` yes |
| Parallel I/O | yes | yes (heavy) | yes, event loop |
| Memory | shared | separate | workers separate (SharedArrayBuffer optional) |
| Startup cost | ~ 0.1 ms | 50-300 ms (spawn) | worker ~ 30 ms |
| Default idea | `ThreadPoolExecutor` | `ProcessPoolExecutor` | `cluster` / `worker_threads` |

```python
# Python way — choose by workload
from concurrent.futures import ThreadPoolExecutor        # for I/O
import urllib.request                                    # stdlib HTTP

def fetch(url: str) -> int:                              # I/O-bound function
    with urllib.request.urlopen(url) as r:               # waits on network, GIL released
        return r.status                                  # status code

with ThreadPoolExecutor(8) as pool:                      # 8 threads is plenty for I/O
    print(list(pool.map(fetch, ["https://example.com"])))   # [200]
```
```javascript
// JavaScript way — I/O needs no threads at all, the event loop handles it
const urls = ['https://example.com'];                    // list of URLs
Promise.all(urls.map(u => fetch(u).then(r => r.status))) // concurrent I/O in ONE thread
  .then(console.log);                                    // [ 200 ]
// CPU work -> worker_threads or child_process.fork (like Python multiprocessing)
```

Key difference: Node's single thread handles I/O concurrency natively, so JS devs rarely need threads for I/O. In Python you choose: threads or asyncio for I/O, processes for CPU. Node `cluster` ~ Python `multiprocessing` / Gunicorn workers.

---

## 🟠 FastAPI Connection
FastAPI runs `def` (sync) endpoints in a thread pool (AnyIO, 40 threads by default), so blocking I/O in a plain `def` endpoint does not freeze the server. CPU work still hurts, because those threads share the GIL. Heavy CPU belongs in a `ProcessPoolExecutor`, and production scaling uses multiple uvicorn/gunicorn worker *processes*.

```python
# FastAPI example — which tool for which endpoint
import asyncio                                            # loop access
import time                                               # blocking sleep
from concurrent.futures import ProcessPoolExecutor        # CPU pool
from fastapi import FastAPI                               # FastAPI

app: FastAPI = FastAPI()                                  # create app
cpu_pool: ProcessPoolExecutor = ProcessPoolExecutor(2)    # processes for CPU work


def crunch(n: int) -> int:                                # top-level => picklable
    return sum(i * i for i in range(n))                   # CPU-bound


@app.get("/io")                                           # sync def => runs in a thread
def io_endpoint() -> dict[str, str]:
    time.sleep(0.1)                                       # blocking wait is fine here (thread pool)
    return {"mode": "thread"}


@app.get("/async-io")                                     # async def => runs on the event loop
async def async_io() -> dict[str, str]:
    await asyncio.sleep(0.1)                              # must use await, never time.sleep
    return {"mode": "event loop"}


@app.get("/cpu/{n}")                                      # CPU work => process pool
async def cpu_endpoint(n: int) -> dict[str, int]:
    loop = asyncio.get_running_loop()                     # current loop
    return {"result": await loop.run_in_executor(cpu_pool, crunch, n)}   # off the event loop
# run: uvicorn module:app --workers 4   -> 4 processes, each with its own event loop and GIL
```
(Pattern: the process-pool `run_in_executor` call was run with `TestClient` on 3.13 in topic 233; the sync-vs-async endpoint behaviour is standard FastAPI and was not run separately here.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using threads to speed up CPU-bound code
✅ Correct: use `ProcessPoolExecutor` (or the free-threaded build) for CPU

```python
# Wrong — four threads, same speed as one (GIL)
# ThreadPoolExecutor(4).map(burn, jobs)
# Right
# ProcessPoolExecutor(4).map(burn, jobs)
```

❌ Mistake 2: Starting one process per small task
✅ Correct: use a pool and batch small tasks (process start costs 50-300 ms with `spawn`)

```python
# Wrong — 10,000 processes
# for x in items: Process(target=f, args=(x,)).start()
# Right
# with ProcessPoolExecutor() as pool: pool.map(f, items, chunksize=100)
```

❌ Mistake 3: Expecting global variables to be shared between processes
✅ Correct: threads share globals; processes need `Queue`, `Value`, shared memory or a database

```python
# Wrong — child process changes its OWN copy
# counter = 0; Process(target=lambda: ...)   # parent still sees 0
# Right — shared types
# from multiprocessing import Value; counter = Value("i", 0)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import threading, multiprocessing as mp
items: list[int] = []
def add() -> None:
    items.append(1)
if __name__ == "__main__":
    t = threading.Thread(target=add); t.start(); t.join()
    p = mp.Process(target=add); p.start(); p.join()
    print(items)
    print(mp.get_start_method())
```
Answer: `[1]` and then `spawn` (verified on macOS, Python 3.13). The thread appended to the shared list, so the list has one item. The process appended to its own copy of `items`, so the parent never sees it. The default start method is `spawn` on macOS and Windows, `fork` on Linux up to 3.13, and `forkserver` on Linux from 3.14. That is a version-dependent detail interviewers like: with `fork` the child starts with a copy of the parent's memory, with `spawn` it starts fresh.

---

## ⚫ Interview Questions + Answers

Q1: Does threading give any speedup in Python?
A1: Yes for I/O-bound work: a waiting thread releases the GIL, so many requests wait together. No for pure-Python CPU work: the GIL lets one thread run bytecode at a time, and thread switching adds small overhead. C extensions such as numpy, hashlib and zlib may release the GIL during heavy work, so threads can help there.

Q2: Why are processes heavier than threads?
A2: Each process has its own interpreter and memory (copy-on-write with `fork`, a fresh import with `spawn`). Start-up takes tens to hundreds of milliseconds and uses tens of MB. Data must be pickled between processes. A thread starts in under a millisecond and shares everything.

Q3: What are the three start methods?
A3: `fork` (copy the parent; fast but unsafe with threads), `spawn` (fresh interpreter; safe, slower, requires the `__main__` guard; default on macOS and Windows), `forkserver` (a clean server process forks children; default on Linux from 3.14). Set it with `mp.set_start_method()` or `mp.get_context("spawn")`.

Q4: Why is thread safety an issue and process safety is not?
A4: Threads share memory, so two threads can change the same variable at once (race conditions), needing `Lock`. Processes do not share memory by default, so there is nothing to race on, until you add shared memory.

Q5: What replaces the GIL problem in newer Python?
A5: PEP 703: an experimental free-threaded build (`python3.13t`, officially supported in 3.14) disables the GIL so threads can use all cores. Many C extensions need updates, and single-thread speed is somewhat lower, so most production code still uses processes for CPU.

---

## 🔷 When to Use + When Not to Use
✅ Use threads when:
- Work is I/O-bound (HTTP, DB, files) and libraries are blocking
- Tasks must share data in memory
- You need cheap, quick-to-start concurrency

✅ Use processes when:
- Work is CPU-bound (parsing, image/video, crypto, ML pre-processing)
- You want real multi-core speedup and fault isolation (a crashing worker does not kill the app)

❌ Avoid both when:
- The library offers `async` I/O, use asyncio for thousands of connections
- The work is too tiny to pay for a thread or process hop
- Your app needs to scale across machines; use a task queue (Celery, RQ) instead

---

## 📊 Visual Diagram
```
                       THREADS                     PROCESSES
 memory               shared                      separate (copy / pickle)
 GIL                  one for all                 one per process
 CPU parallel         no                          yes
 I/O parallel         yes                         yes
 start cost           ~0.1 ms                     50-300 ms
 crash effect         can kill whole process      only that worker dies
 communication        variables + Lock            Queue / Pipe / shared memory
 best for             waiting (network, DB)       computing (math, images)

 Decision:  waiting on something?  -> threads / asyncio
            computing in Python?   -> processes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GIL | Lock letting one thread run Python code at a time | एक समय में एक thread की अनुमति देने वाला lock |
| I/O-bound | Mostly waiting for network/disk | ज़्यादातर इंतज़ार वाला काम |
| CPU-bound | Mostly computing | ज़्यादातर गणना वाला काम |
| `fork` / `spawn` | Ways to start a child process | Child process शुरू करने के तरीके |
| Race condition | Bug from unsynchronised shared access | बिना तालमेल shared access से bug |
| Free-threaded | Python build without the GIL | बिना GIL वाला Python build |

---

## ⚡ 3-Line Summary
English: Threads share memory but take turns because of the GIL, so they speed up I/O only. Processes have their own memory and GIL, so they speed up CPU work at the cost of startup time and pickling. Choose by workload: waiting means threads or asyncio, computing means processes.
Hindi: Threads memory share करते हैं पर GIL की वजह से बारी-बारी चलते हैं, इसलिए सिर्फ I/O को तेज़ करते हैं। Processes की अपनी memory और GIL होती है, इसलिए CPU काम तेज़ होता है, लेकिन startup समय और pickling की कीमत पर। Workload से चुनें: इंतज़ार हो तो threads या asyncio, गणना हो तो processes।

---

## ➡️ Next Topic
**238. Event Loop in Python** — the heart of asyncio: how one thread runs thousands of tasks by switching at every `await`.
