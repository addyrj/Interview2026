---

# 251. asyncio vs Threading vs Multiprocessing
# हिंदी में: asyncio बनाम Threading बनाम Multiprocessing

---

## 🔵 Simple Definition (English)
These are three ways to do many things at once in Python. `asyncio` runs many tasks on ONE thread by switching when a task waits. `threading` runs many threads in ONE process (the GIL lets only one run Python code at a time). `multiprocessing` runs many processes, each with its own GIL, so it gives real parallel CPU work.

## 🔵 सरल परिभाषा (Hindi)
ये Python में एक साथ कई काम करने के तीन तरीके हैं। `asyncio` एक ही thread पर कई tasks चलाता है और जब कोई task इंतजार करे तब बदलता है। `threading` एक process में कई threads चलाता है (GIL के कारण एक समय में सिर्फ एक thread Python code चलाता है)। `multiprocessing` कई processes चलाता है, हर एक की अपनी GIL होती है, इसलिए CPU का काम सच में parallel होता है।

---

## 🔴 Problem it Solves
Programs wait a lot (network, disk, database) and sometimes compute a lot (images, ML, maths). One tool does not fit both. Choosing wrong makes code slower or more complex: threads for CPU work give no speedup, processes for 10,000 network calls waste memory, and blocking calls inside `asyncio` freeze everything. You need to know which tool matches which bottleneck.

## 🔴 यह क्यों बना? (Hindi)
Programs बहुत इंतजार करते हैं (network, disk, database) और कभी-कभी बहुत compute करते हैं (images, ML, गणित)। एक ही tool दोनों के लिए ठीक नहीं बैठता। गलत चुनाव से code धीमा या जटिल हो जाता है: CPU काम के लिए threads से कोई speedup नहीं, 10,000 network calls के लिए processes memory बर्बाद करते हैं, और `asyncio` के अंदर blocking call सब कुछ रोक देती है। आपको पता होना चाहिए कि कौन सा tool किस bottleneck के लिए है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ask: is my program waiting (I/O-bound) or computing (CPU-bound)?
Step 2 → I/O-bound + thousands of connections + async libraries  -> asyncio
Step 3 → I/O-bound + blocking libraries (requests, boto3, JDBC)  -> threading
Step 4 → CPU-bound (maths, image, parsing, ML preprocessing)    -> multiprocessing
Step 5 → asyncio: one thread, event loop, tasks give control back at every await
Step 6 → threading: OS switches threads; GIL is released during I/O waits
Step 7 → multiprocessing: separate memory; data is pickled between processes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पूछो: मेरा program इंतजार कर रहा है (I/O-bound) या गणना कर रहा है (CPU-bound)?
Step 2 → I/O-bound + हजारों connections + async libraries  -> asyncio
Step 3 → I/O-bound + blocking libraries (requests, boto3)    -> threading
Step 4 → CPU-bound (गणित, image, parsing, ML preprocessing) -> multiprocessing
Step 5 → asyncio: एक thread, event loop, हर await पर task control लौटाता है
Step 6 → threading: OS threads बदलता है; I/O के इंतजार में GIL छूट जाती है
Step 7 → multiprocessing: अलग memory; processes के बीच data pickle होता है
```

---

## 🟡 Real World Example
A Zomato-like backend: the API gateway calling 5 microservices per request uses `asyncio` (thousands of waiting sockets, tiny memory). A legacy invoice generator using the blocking `boto3` S3 client uses a thread pool. The nightly job that resizes 100,000 restaurant photos uses `multiprocessing` to use all CPU cores. One system, three tools, each for its own bottleneck.

## 🟡 Real Example Hindi mein
Zomato जैसा backend: हर request पर 5 microservices बुलाने वाला API gateway `asyncio` इस्तेमाल करता है (हजारों इंतजार करते sockets, कम memory)। Blocking `boto3` S3 client वाला पुराना invoice generator thread pool इस्तेमाल करता है। रोज़ रात को 100,000 restaurant photos resize करने वाला job सभी CPU cores के लिए `multiprocessing` इस्तेमाल करता है। एक system, तीन tools, हर एक अपने bottleneck के लिए।

---

## 💻 Code Example — Basic
```python
# Basic: the same 10 "I/O" jobs with three styles (verified on Python 3.13, 8-core Mac)
import asyncio                                           # async style
import time                                              # sleep + timer
from concurrent.futures import ThreadPoolExecutor        # thread style


def io_task(i: int) -> int:                              # blocking "I/O" job
    time.sleep(0.2)                                      # blocks the thread
    return i                                             # return its number


async def aio_task(i: int) -> int:                       # async "I/O" job
    await asyncio.sleep(0.2)                             # does NOT block the loop
    return i                                             # return its number


async def run_async() -> list[int]:                      # run 10 coroutines together
    return await asyncio.gather(*(aio_task(i) for i in range(10)))   # gather them


def timed(label: str, fn) -> None:                       # tiny timing helper
    t: float = time.perf_counter()                       # start
    fn()                                                 # run it
    print(f"{label}: {time.perf_counter() - t:.1f}s")    # print seconds


def threads() -> None:                                   # 10 jobs on 10 threads
    with ThreadPoolExecutor(10) as ex:                   # pool
        list(ex.map(io_task, range(10)))                 # run all


timed("sequential io x10", lambda: [io_task(i) for i in range(10)])   # one by one
timed("threads    io x10", threads)                      # in threads
timed("asyncio    io x10", lambda: asyncio.run(run_async()))          # in asyncio

# Output (timings vary by machine):
# sequential io x10: 2.0s
# threads    io x10: 0.2s
# asyncio    io x10: 0.2s
```

## 💻 Code Example — Advanced
```python
# Advanced: CPU-bound work with sequential vs threads vs processes
import time                                              # timer
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor   # pools


def cpu_task(n: int) -> int:                             # pure Python computation
    return sum(i * i for i in range(n))                  # holds the GIL the whole time


def timed(label: str, fn) -> None:                       # timing helper
    t: float = time.perf_counter()                       # start
    fn()                                                 # run
    print(f"{label}: {time.perf_counter() - t:.1f}s")    # seconds


def threads(n: int, jobs: int) -> None:                  # thread pool version
    with ThreadPoolExecutor(jobs) as ex:                 # pool
        list(ex.map(cpu_task, [n] * jobs))               # same work in threads


def procs(n: int, jobs: int) -> None:                    # process pool version
    with ProcessPoolExecutor(jobs) as ex:                # pool of processes
        list(ex.map(cpu_task, [n] * jobs))               # same work in processes


if __name__ == "__main__":                               # required for process pools
    N, JOBS = 3_000_000, 4                               # size of work, number of jobs
    timed("cpu sequential x4", lambda: [cpu_task(N) for _ in range(JOBS)])   # baseline
    timed("cpu threads    x4", lambda: threads(N, JOBS))                     # GIL: no gain
    timed("cpu processes  x4", lambda: procs(N, JOBS))                       # real parallel

# Output (timings vary; the shape is what matters):
# cpu sequential x4: 0.6s
# cpu threads    x4: 0.6s     <- no speedup (GIL)
# cpu processes  x4: 0.3s     <- ~2x faster here (process start-up cost matters for small jobs)
# Python 3.13: free-threaded (no-GIL) builds are experimental; the default build still has the GIL.
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript (Node.js) |
|---------|--------|---------------------|
| Single-thread async | `asyncio` | the default event loop |
| Threads | `threading` (GIL) | `worker_threads` |
| Processes | `multiprocessing` | `child_process` / `cluster` |
| Async I/O is default? | No, you opt in | Yes |
| CPU work blocks loop? | Yes | Yes |
| Shared memory | threads only | `SharedArrayBuffer` |

```python
# Python way — you must choose
await asyncio.gather(fetch(a), fetch(b))                 # I/O: asyncio
# ThreadPoolExecutor(...).map(blocking_fn, items)        # blocking libs
# ProcessPoolExecutor(...).map(cpu_fn, items)            # CPU
```
```javascript
// JavaScript way — async I/O is automatic
await Promise.all([fetch(a), fetch(b)]);                 // I/O: nothing to choose
// CPU work: new Worker("./heavy.js") or child_process.fork()
```

Key difference: Node's whole runtime is an event loop, so async I/O needs no choice. Python offers three models and you must pick. The JS rule "do not block the event loop" is exactly the Python `asyncio` rule.

---

## 🟠 FastAPI Connection
FastAPI uses all three ideas at once. `async def` endpoints run on the event loop (asyncio). Plain `def` endpoints run in a thread pool automatically. For CPU-heavy work you send a job to a process pool (or a worker like Celery/RQ).

```python
# FastAPI example — three kinds of endpoints
import asyncio                                           # sleep, loop
import time                                              # blocking sleep
from concurrent.futures import ProcessPoolExecutor       # processes
from fastapi import FastAPI                              # FastAPI

app: FastAPI = FastAPI()                                 # app
pool: ProcessPoolExecutor = ProcessPoolExecutor(2)       # for CPU work


def crunch(n: int) -> int:                               # CPU job (top-level, picklable)
    return sum(i * i for i in range(n))                  # compute


@app.get("/io-async")                                    # asyncio: thousands of these are fine
async def io_async() -> dict[str, str]:
    await asyncio.sleep(0.1)                             # awaiting an async resource
    return {"mode": "asyncio"}                           # reply


@app.get("/io-blocking")                                 # plain def -> runs in FastAPI's thread pool
def io_blocking() -> dict[str, str]:
    time.sleep(0.1)                                      # blocking is OK, only this thread waits
    return {"mode": "threads"}                           # reply


@app.get("/cpu/{n}")                                     # CPU job -> separate process
async def cpu(n: int) -> dict[str, int]:
    loop = asyncio.get_running_loop()                    # current loop
    return {"sum": await loop.run_in_executor(pool, crunch, n)}   # keep loop free
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling a blocking function inside `async def`
✅ Correct: use an async library, or `asyncio.to_thread()` (3.9+)

```python
# Wrong — freezes the event loop for everyone
async def handler():
    time.sleep(2)
# Right
async def handler():
    await asyncio.sleep(2)               # or: await asyncio.to_thread(blocking_fn)
```

❌ Mistake 2: Using threads to speed up CPU-bound Python code
✅ Correct: use processes (or NumPy / C-extensions that release the GIL)

```python
# Wrong — no speedup, sometimes slower (see benchmark above)
ThreadPoolExecutor(8).map(cpu_task, data)
# Right
ProcessPoolExecutor(8).map(cpu_task, data)
```

❌ Mistake 3: Starting thousands of processes/threads for I/O
✅ Correct: asyncio handles 10,000 sockets on one thread; threads cost ~8 MB stack each (virtual), processes far more

```python
# Wrong: 10_000 threads -> memory blow-up, context switching
# Right: asyncio.Semaphore(200) + gather over 10_000 coroutines
```

---

## 🧠 Tricky Interview Question

```python
# Is this concurrent? How long does it take?
import asyncio, time

async def main() -> None:
    t = time.perf_counter()
    await asyncio.gather(
        asyncio.sleep(1),
        asyncio.to_thread(time.sleep, 1),
        asyncio.sleep(1),
    )
    print(round(time.perf_counter() - t))

asyncio.run(main())
```
Answer: It prints `1`. All three run concurrently: two coroutines yield to the loop while sleeping, and the blocking `time.sleep(1)` runs in a worker thread via `asyncio.to_thread`, so the loop is not blocked. If you wrote `time.sleep(1)` directly inside a coroutine, the total would be about 2 seconds (the other sleeps would start late, and the loop would freeze for one second).

---

## ⚫ Interview Questions + Answers

Q1: What is the GIL and why does it matter here?
A1: The Global Interpreter Lock lets only one thread execute Python bytecode at a time in a process. Threads therefore cannot speed up CPU-bound pure Python. It is released during I/O and by many C extensions (NumPy), so threads do help I/O. Processes each have their own GIL.

Q2: When would you pick threads over asyncio for I/O?
A2: When the library is blocking and has no async version (boto3, older DB drivers, requests), or when you want a quick change without rewriting code in `async/await`.

Q3: What are the costs of multiprocessing?
A3: Process start-up time, higher memory, and data must be pickled between processes (large objects are slow to send). Shared state needs `multiprocessing.Manager`, `shared_memory` or queues.

Q4: Can asyncio use multiple cores?
A4: Not by itself: one loop = one thread = one core. Run several worker processes (`uvicorn --workers 4`, gunicorn) or offload CPU to a process pool.

Q5: Is Python 3.13 free-threading a replacement for multiprocessing?
A5: Python 3.13 adds an experimental free-threaded build (PEP 703) where threads can run in parallel. It is optional and not the default; many C extensions are still being adapted, so multiprocessing remains the safe choice for CPU parallelism today.

---

## 🔷 When to Use + When Not to Use
✅ Use asyncio when: many concurrent network/DB calls with async libraries (APIs, scrapers, chat servers)
✅ Use threading when: blocking I/O libraries, small concurrency, existing sync code
✅ Use multiprocessing when: CPU-heavy work (image/video, data crunching, ML features)

❌ Avoid when:
- asyncio for CPU work (it will block the loop)
- threads for CPU work (GIL) or for shared mutable state without locks
- multiprocessing for tiny tasks (start-up and pickling cost exceed the work)

---

## 📊 Visual Diagram
```
asyncio            1 process, 1 thread, 1 event loop
                   [task A][task B][task C][A][B]...   (switch at every await)

threading          1 process, N threads, 1 GIL
                   T1 ▓░▓░    only one runs Python at a time;
                   T2 ░▓░▓    others wait for I/O

multiprocessing    N processes, N GILs
                   P1 ▓▓▓▓▓
                   P2 ▓▓▓▓▓   true parallel on N cores
                   P3 ▓▓▓▓▓

Decision:  waiting?  -> asyncio (async libs) / threads (blocking libs)
           computing? -> multiprocessing
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| I/O-bound | Time spent waiting | इंतजार में लगने वाला समय |
| CPU-bound | Time spent computing | गणना में लगने वाला समय |
| GIL | One-thread-at-a-time lock | एक समय में एक thread की lock |
| Event loop | Scheduler for coroutines | Coroutines का scheduler |
| Pickle | Serialize objects between processes | Processes के बीच object भेजने का serialization |
| Context switch | CPU changes to another task | CPU का दूसरे काम पर जाना |

---

## ⚡ 3-Line Summary
English: Use `asyncio` for lots of waiting with async libraries, threads for blocking I/O libraries, and processes for CPU-heavy work. The GIL is why threads do not speed up CPU code. Measure before choosing.
Hindi: बहुत इंतजार वाले काम और async libraries के लिए `asyncio`, blocking I/O libraries के लिए threads, और CPU-भारी काम के लिए processes इस्तेमाल करें। GIL की वजह से threads CPU code तेज़ नहीं करते। चुनने से पहले मापें।

---

## ➡️ Next Topic
**252. When to Use Each Approach** (already written) — then **254. Async Context Managers**: safe setup and cleanup with `async with`.
