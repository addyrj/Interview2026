---

# 413. Multiprocessing for CPU Tasks
# हिंदी में: CPU वाले कामों के लिए Multiprocessing

---

## 🔵 Simple Definition (English)
`multiprocessing` starts separate Python processes, each with its own interpreter, memory and GIL. CPU-bound work is split across them, so it runs on several cores at the same time. Use `Pool` or `ProcessPoolExecutor` to hand out jobs.

## 🔵 सरल परिभाषा (Hindi)
`multiprocessing` अलग-अलग Python processes शुरू करता है, हर एक का अपना interpreter, memory और GIL होता है। CPU वाला काम उनमें बँट जाता है और कई cores पर एक साथ चलता है। जॉब बाँटने के लिए `Pool` या `ProcessPoolExecutor` इस्तेमाल करें।

---

## 🔴 Problem it Solves
The GIL lets only one thread run Python bytecode at a time, so threads do not speed up CPU-bound loops (image resizing, hashing, number crunching). Multiple processes bypass the GIL because each has its own, giving real parallelism on multi-core machines.

## 🔴 यह क्यों बना? (Hindi)
GIL की वजह से एक समय में सिर्फ एक thread Python bytecode चला सकता है, इसलिए threads CPU वाले loops (image resize, hashing, number crunching) को तेज़ नहीं करते। हर process का अपना GIL होता है, इसलिए multi-core machine पर असली parallelism मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent creates a pool of N worker processes (spawn on macOS/Windows, fork on Linux up to 3.13)
Step 2 → You submit a function + arguments; they are pickled and sent to a worker
Step 3 → Each worker runs the function on its own core with its own GIL
Step 4 → Return values are pickled and sent back to the parent
Step 5 → The parent collects results (map keeps input order)
Note   → Memory is NOT shared; a global changed in a worker stays in that worker
Note   → Python 3.14 changes the Linux default start method from fork to forkserver
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent N worker processes का pool बनाता है (macOS/Windows पर spawn, Linux पर 3.13 तक fork)
Step 2 → Function और arguments pickle होकर worker को जाते हैं
Step 3 → हर worker अपने core और अपने GIL पर function चलाता है
Step 4 → Return values pickle होकर parent को लौटती हैं
Step 5 → Parent results इकट्ठा करता है (map input का क्रम रखता है)
नोट   → Memory साझा नहीं होती; worker में बदला global वहीं रह जाता है
नोट   → Python 3.14 में Linux का default start method fork से forkserver हो गया
```

---

## 🟡 Real World Example
A Razorpay-style nightly reconciliation job splits 5 million transactions into chunks and verifies signatures in 8 worker processes. An AI app resizes and hashes 100,000 uploaded images in parallel. A FastAPI endpoint sends a heavy PDF-generation task to a process pool instead of blocking the server.

## 🟡 Real Example Hindi mein
Razorpay जैसा nightly reconciliation job 50 लाख transactions को chunks में बाँटकर 8 worker processes में signatures verify करता है। AI app 1 लाख uploaded images को parallel में resize और hash करता है। FastAPI endpoint भारी PDF-generation task को server block करने की बजाय process pool को भेजता है।

---

## 💻 Code Example — Basic
```python
# Basic: multiprocessing.Pool - one Python process per CPU core (no GIL sharing)
import multiprocessing as mp  # process pool
import os  # core count
import time  # timer
from typing import List  # type hints


def cpu_heavy(n: int) -> int:
    total: int = 0  # accumulator
    for i in range(n):  # pure-Python CPU loop (GIL-bound in threads)
        total += i * i  # arithmetic work
    return total  # result


def main() -> None:
    jobs: List[int] = [2_000_000] * 4  # four equal heavy tasks
    cores: int = min(4, os.cpu_count() or 1)  # do not use more than we have

    start: float = time.perf_counter()  # serial run
    serial: List[int] = [cpu_heavy(n) for n in jobs]  # one after another
    t_serial: float = time.perf_counter() - start  # seconds

    start = time.perf_counter()  # parallel run
    with mp.Pool(processes=cores) as pool:  # start worker processes
        parallel: List[int] = pool.map(cpu_heavy, jobs)  # split jobs across workers
    t_parallel: float = time.perf_counter() - start  # seconds

    print(serial == parallel)  # same results, same order
    # Output: True
    print(serial[0])  # sum of i*i for i < 2,000,000
    # Output: 2666664666667000000
    print("parallel faster:", t_parallel < t_serial)  # true when cores >= 2
    # Output: parallel faster: True   (needs 2+ CPU cores; speedup depends on your machine)


if __name__ == "__main__":  # REQUIRED: spawn start method (macOS/Windows) re-imports this file
    main()  # run
```

## 💻 Code Example — Advanced
```python
# Advanced: ProcessPoolExecutor, chunking, error handling, timeouts, shared-nothing design
import os  # process ids
from concurrent.futures import ProcessPoolExecutor, as_completed  # futures API
from typing import Dict, List, Tuple  # type hints


def count_primes(bounds: Tuple[int, int]) -> int:
    lo, hi = bounds  # unpack the range handled by this worker
    count: int = 0  # primes found in [lo, hi)
    for n in range(max(lo, 2), hi):  # test each number
        d: int = 2  # first divisor
        while d * d <= n:  # up to sqrt(n)
            if n % d == 0:  # divisible
                break  # not prime
            d += 1  # next divisor
        else:  # loop ended without break
            count += 1  # prime
    return count  # per-chunk answer


def risky(x: int) -> int:
    if x == 3:  # simulate a bad record
        raise ValueError("bad record 3")  # worker raises
    return x * 10  # normal result


def split(limit: int, parts: int) -> List[Tuple[int, int]]:
    step: int = -(-limit // parts)  # ceiling division
    return [(i, min(i + step, limit)) for i in range(0, limit, step)]  # contiguous chunks


def main() -> None:
    chunks: List[Tuple[int, int]] = split(100_000, 8)  # 8 chunks of work
    with ProcessPoolExecutor(max_workers=4) as pool:  # 4 worker processes
        total: int = sum(pool.map(count_primes, chunks))  # map keeps order, then reduce
    print(total)  # primes below 100000
    # Output: 9592

    results: Dict[int, str] = {}  # per-input outcome
    with ProcessPoolExecutor(max_workers=2) as pool:  # a second pool
        futures = {pool.submit(risky, x): x for x in range(5)}  # submit single jobs
        for fut in as_completed(futures):  # in completion order
            x: int = futures[fut]  # which input
            try:  # exceptions travel back to the parent
                results[x] = str(fut.result(timeout=30))  # value, with a timeout
            except ValueError as exc:  # worker error re-raised here
                results[x] = f"error: {exc}"  # keep going, record failure
    print(dict(sorted(results.items())))  # sorted for stable output
    # Output: {0: '0', 1: '10', 2: '20', 3: 'error: bad record 3', 4: '40'}

    with ProcessPoolExecutor(max_workers=2) as pool:  # check workers differ from parent
        worker_pid: int = pool.submit(os.getpid).result()  # pid inside a worker
    print("different process:", worker_pid != os.getpid())  # separate memory space
    # Output: different process: True


if __name__ == "__main__":  # guard needed for spawn
    main()  # run
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: processes for CPU parallelism
from multiprocessing import Pool
with Pool(4) as pool:
    print(pool.map(abs, [-1, -2, -3]))   # [1, 2, 3]
```
```javascript
// JavaScript: worker_threads (Node) - separate V8 isolates, messages are copied/transferred
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
if (isMainThread) {
  const w = new Worker(__filename, { workerData: [-1, -2, -3] });
  w.on('message', (r) => console.log(r));            // [1, 2, 3]
} else {
  parentPort.postMessage(workerData.map(Math.abs));
}
```

Key differences: Node's `worker_threads` are threads with isolated heaps; Python's `multiprocessing` uses full OS processes (heavier to start, stronger isolation). In both, data is copied by message passing, not shared by default. Node's `cluster` module is closer to forking multiple server processes.

---

## 🟠 FastAPI Connection
`async def` endpoints must never run CPU loops, because that blocks the event loop for every user. Create a `ProcessPoolExecutor` in the `lifespan`, and `await loop.run_in_executor(pool, func, arg)` from the endpoint. In production you also run several uvicorn/gunicorn worker processes; a CPU pool is for the occasional heavy job, while a task queue (Celery, RQ, ARQ) is better for long jobs.

```python
# FastAPI: offload CPU work to a process pool so the event loop stays free (pip install fastapi httpx)
import asyncio  # event loop access
from concurrent.futures import ProcessPoolExecutor  # process pool
from contextlib import asynccontextmanager  # lifespan
from typing import AsyncIterator  # type hints

from fastapi import FastAPI, Query  # app
from fastapi.testclient import TestClient  # test client

pool: ProcessPoolExecutor | None = None  # created at startup, one per app process


def heavy(n: int) -> int:  # must be a top-level function so it can be pickled
    return sum(i * i for i in range(n))  # CPU work


@asynccontextmanager  # app lifespan
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    global pool  # module-level handle
    pool = ProcessPoolExecutor(max_workers=2)  # start workers once
    yield  # serve requests
    pool.shutdown(wait=True)  # clean shutdown


app: FastAPI = FastAPI(lifespan=lifespan)  # create app


@app.get("/compute")  # GET /compute?n=1000
async def compute(n: int = Query(1000, ge=1, le=5_000_000)) -> dict[str, int]:
    loop = asyncio.get_running_loop()  # current loop
    result: int = await loop.run_in_executor(pool, heavy, n)  # await without blocking the loop
    return {"n": n, "result": result}  # JSON response


if __name__ == "__main__":  # guard needed for spawn
    with TestClient(app) as client:  # runs lifespan
        print(client.get("/compute", params={"n": 10}).json())  # sum of squares 0..9
        # Output: {'n': 10, 'result': 285}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Missing the `if __name__ == "__main__"` guard
```python
# Wrong - with spawn (macOS/Windows) every worker re-imports the file and starts more pools:
pool = Pool(4)
print(pool.map(f, data))

# Correct:
if __name__ == "__main__":
    with Pool(4) as pool:
        print(pool.map(f, data))
```

❌ Mistake 2: Sending lambdas, local functions or huge objects
```python
# Wrong - cannot be pickled:
pool.map(lambda x: x * 2, data)

# Correct - top-level named function, and pass small arguments (chunks, ids), not giant objects:
def double(x: int) -> int:
    return x * 2
pool.map(double, data)
```

❌ Mistake 3: Using processes for tiny tasks or I/O
```python
# Wrong - process start + pickling costs more than the work (or the work is I/O waiting):
pool.map(str.upper, ["a", "b", "c"])

# Correct - batch work with chunksize, or use asyncio/threads for I/O
pool.map(heavy, jobs, chunksize=50)
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print (macOS, Python 3.13)?

```python
import multiprocessing as mp

counter = 0

def inc(_):
    global counter
    counter += 1
    return counter

if __name__ == "__main__":
    with mp.Pool(2) as pool:
        pool.map(inc, range(4))
    print(counter)
    try:
        with mp.Pool(2) as pool:
            pool.map(lambda x: x, range(2))
    except Exception as e:
        print(type(e).__name__)
    print(mp.get_start_method())
```

**Answer**:
```
0
PicklingError
spawn
```
Each worker has its own copy of `counter`, so the parent's value stays 0. A lambda cannot be pickled by reference, so sending it fails with `PicklingError`. On macOS (and Windows) the default start method is `spawn`; on Linux with Python 3.13 it is `fork` (3.14 switches it to `forkserver`).

---

## ⚫ Interview Questions + Answers

Q1: Threads vs processes for CPU-bound Python?
A1: Threads share one GIL, so there is no CPU speed-up. Processes each have their own GIL and run in parallel. Free-threaded Python (3.13t, experimental) is changing this, but processes are still the standard answer.

Q2: `fork` vs `spawn`?
A2: `fork` copies the parent process quickly (Linux default up to 3.13) but is unsafe with threads and some libraries. `spawn` starts a fresh interpreter and re-imports your module (macOS/Windows default), so it is slower and requires the `__main__` guard and picklable arguments. `forkserver` is a safer middle path.

Q3: How do processes share data?
A3: Message passing (`Queue`, `Pipe`, return values), `shared_memory.SharedMemory` for big arrays, or `Manager` objects. All have costs: pickling or synchronization.

Q4: How many workers should I use?
A4: About `os.cpu_count()` for CPU-bound work (sometimes one fewer). More workers than cores adds overhead, not speed. Use `chunksize` to cut communication costs.

Q5: `Pool` vs `ProcessPoolExecutor`?
A5: `Pool` has `map`, `imap`, `apply_async` and more options. `ProcessPoolExecutor` has the cleaner `concurrent.futures` API (`submit`, `as_completed`, exceptions via `future.result()`) and works well with `asyncio` through `run_in_executor`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- The work is CPU-bound and splits into independent chunks
- You have several cores and tasks that take at least tens of milliseconds
- You need isolation (a crash in one worker does not kill the parent)

❌ Avoid when:
- The work is I/O-bound (use asyncio or threads)
- Tasks are tiny or need heavy shared state
- NumPy/Numba already uses multiple cores internally
- The data to pass is huge (pickling cost dominates)

---

## 📊 Visual Diagram

```
                 ┌── worker 1 (own GIL, core 1) ──┐
parent process ──┼── worker 2 (own GIL, core 2) ──┼──► results collected (pickled)
 splits jobs     ├── worker 3 (own GIL, core 3) ──┤
                 └── worker 4 (own GIL, core 4) ──┘

Threads:   [thread A][thread B] share ONE GIL → only one runs Python at a time
Processes: each process has its own GIL → truly parallel
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Process | Separate program instance with its own memory | अपनी memory वाला अलग program |
| GIL | Global lock: one thread runs bytecode at a time | एक समय में एक thread की global lock |
| Pickle | Serialize objects to send between processes | processes के बीच भेजने के लिए serialize |
| spawn / fork | Ways to start worker processes | worker processes शुरू करने के तरीके |
| chunksize | Jobs sent to a worker per message | एक बार में worker को भेजे जाने वाले jobs |
| Pool | Fixed group of worker processes | worker processes का तय समूह |

---

## ⚡ 3-Line Summary
English: Multiprocessing runs CPU-bound Python on several cores using separate processes with separate GILs. Always use the `__main__` guard, picklable top-level functions and reasonable chunk sizes. Use asyncio for I/O work and a task queue for long jobs.
Hindi: Multiprocessing अलग GIL वाले अलग processes से CPU वाले Python code को कई cores पर चलाता है। हमेशा `__main__` guard, picklable top-level functions और सही chunk size रखें। I/O के लिए asyncio और लंबे jobs के लिए task queue लें।

---

## ➡️ Next Topic
**414. asyncio for IO Tasks** — the right tool when the program mostly waits on the network or database.
