---

# 221. Concurrency vs Parallelism
# हिंदी में: Concurrency बनाम Parallelism (एक साथ संभालना बनाम एक साथ चलाना)

---

## 🔵 Simple Definition (English)
Concurrency means handling many tasks by switching between them, so they overlap in time (one cook, many dishes). Parallelism means actually running many tasks at the exact same moment on different CPU cores (many cooks). Concurrency is about structure; parallelism is about execution.

## 🔵 सरल परिभाषा (Hindi)
Concurrency का मतलब है कई tasks को बारी-बारी switch करके संभालना ताकि वे समय में overlap करें (एक cook, कई dishes)। Parallelism का मतलब है कई tasks का सच में एक ही पल में अलग-अलग CPU cores पर चलना (कई cooks)। Concurrency structure की बात है; parallelism execution की।

---

## 🔴 Problem it Solves
A program that waits (for a database, an API, a file) wastes time if it does nothing meanwhile. A program that crunches numbers is limited by one core. Knowing which problem you have (waiting = I/O-bound, computing = CPU-bound) tells you the right tool: threads or asyncio for waiting, processes for computing.

## 🔴 यह क्यों बना? (Hindi)
जो program इंतज़ार करता है (database, API, file) वह बीच में कुछ न करे तो समय बर्बाद होता है। जो program गणना करता है वह एक core तक सीमित है। यह पहचानना कि आपकी समस्या कौन सी है (इंतज़ार = I/O-bound, गणना = CPU-bound) सही tool बताता है: इंतज़ार के लिए threads या asyncio, गणना के लिए processes।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Classify the work: I/O-bound (waiting) or CPU-bound (computing)?
Step 2 → I/O-bound  → concurrency: asyncio (many sockets) or threads (blocking libraries)
Step 3 → CPU-bound  → parallelism: multiprocessing / ProcessPoolExecutor (one GIL per process)
Step 4 → Measure: time sequential vs concurrent vs parallel
Step 5 → Mixed workload → asyncio for I/O + a process pool for heavy CPU parts
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → काम पहचानें: I/O-bound (इंतज़ार) या CPU-bound (गणना)?
Step 2 → I/O-bound  → concurrency: asyncio (कई sockets) या threads (blocking libraries)
Step 3 → CPU-bound  → parallelism: multiprocessing / ProcessPoolExecutor (हर process का अपना GIL)
Step 4 → नापें: sequential बनाम concurrent बनाम parallel का समय
Step 5 → मिला-जुला काम → I/O के लिए asyncio + भारी CPU हिस्से के लिए process pool
```

---

## 🟡 Real World Example
Zomato's order page calls restaurant, payment, and delivery services: all waiting on the network, so one asyncio worker serves thousands of users concurrently. Their nightly "restaurant ranking" job crunches millions of rows: split into chunks and run on 8 cores in parallel with a process pool. An AI app waits for the OpenAI API (concurrency) but tokenizes huge documents (parallelism).

## 🟡 Real Example Hindi mein
Zomato का order page restaurant, payment और delivery services को call करता है: सब network का इंतज़ार, इसलिए एक asyncio worker हज़ारों users को concurrently संभालता है। उनका रात का "restaurant ranking" job लाखों rows की गणना करता है: chunks में बाँटकर process pool से 8 cores पर parallel चलाते हैं। AI app OpenAI API का इंतज़ार करता है (concurrency) पर बड़े documents को tokenize करता है (parallelism)।

---

## 💻 Code Example — Basic
```python
# Basic: sequential vs threads vs asyncio for waiting tasks
import asyncio  # concurrency without threads
import time  # sleeping and timing
from concurrent.futures import ThreadPoolExecutor  # thread pool


def io_task(n: int) -> int:  # simulates a slow network call
    time.sleep(0.2)  # waiting, not computing
    return n  # return the id


async def aio_task(n: int) -> int:  # async version of the same call
    await asyncio.sleep(0.2)  # non-blocking wait
    return n  # return the id


def sequential() -> None:  # one after another
    [io_task(i) for i in range(5)]  # 5 x 0.2s = about 1.0s


def threaded() -> None:  # overlapping waits with threads
    with ThreadPoolExecutor(5) as ex:  # 5 worker threads
        list(ex.map(io_task, range(5)))  # about 0.2s total


def with_asyncio() -> None:  # overlapping waits on one thread
    async def main() -> list:  # coroutine that runs 5 tasks
        return await asyncio.gather(*(aio_task(i) for i in range(5)))  # about 0.2s total
    asyncio.run(main())  # start the event loop


def timed(label: str, fn) -> None:  # tiny timing helper
    start: float = time.perf_counter()  # start clock
    fn()  # run the function
    took: float = time.perf_counter() - start  # elapsed seconds
    print(label, "fast" if took < 0.6 else "slow")  # fast = overlapped


if __name__ == "__main__":  # entry point
    timed("sequential", sequential)  # slow
    timed("threads", threaded)  # fast
    timed("asyncio", with_asyncio)  # fast
# Output:
# sequential slow
# threads fast
# asyncio fast
```

## 💻 Code Example — Advanced
```python
# CPU-bound work: threads do NOT help, processes do (needs several cores)
import os  # cpu count
import time  # timing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor  # both pools
from typing import Callable, List  # type hints


def cpu_task(n: int) -> int:  # pure computation, holds the GIL
    return sum(i * i for i in range(n))  # sum of squares


def run(label: str, runner: Callable[[], None]) -> float:  # time one strategy
    start: float = time.perf_counter()  # start clock
    runner()  # execute
    return time.perf_counter() - start  # seconds taken


if __name__ == "__main__":  # REQUIRED for processes on macOS/Windows (spawn)
    N: int = 3_000_000  # work per task
    jobs: List[int] = [N] * 4  # four identical jobs

    def seq() -> None:  # one by one
        [cpu_task(n) for n in jobs]

    def thr() -> None:  # four threads, still one GIL
        with ThreadPoolExecutor(4) as ex:
            list(ex.map(cpu_task, jobs))

    def proc() -> None:  # four processes, four GILs
        with ProcessPoolExecutor(4) as ex:
            list(ex.map(cpu_task, jobs))

    t_seq: float = run("seq", seq)  # baseline
    t_thr: float = run("thr", thr)  # threads
    t_proc: float = run("proc", proc)  # processes
    print("cores:", os.cpu_count())  # how many cores this machine has
    print("threads about same as sequential:", t_thr > 0.7 * t_seq)  # no speedup
    print("processes faster:", t_proc < t_seq)  # real parallelism
# Output (8-core Mac, 3.13): cores: 8 / True / True
# Example timings: seq 0.57s, threads 0.54s, processes 0.25s (vary by machine)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: pick the tool by workload
import asyncio
async def main():
    await asyncio.gather(fetch(1), fetch(2))   # concurrency (I/O)
# CPU work: multiprocessing / ProcessPoolExecutor (parallelism)
```

```javascript
// JavaScript: single-threaded event loop = concurrency by default
await Promise.all([fetch(url1), fetch(url2)]);   // concurrency (I/O)
// CPU work: worker_threads for parallelism
const { Worker } = require("worker_threads");
new Worker("./heavy.js");
```

Key differences: Node's event loop and Python's asyncio are the same idea (concurrency on one thread). JS `worker_threads` can run truly in parallel; Python threads cannot run Python code in parallel (GIL), so Python uses separate processes for parallelism.

---

## 🟠 FastAPI Connection
`async def` endpoints run on the event loop (concurrency); plain `def` endpoints run in a threadpool; CPU-heavy work should be pushed to a process pool, otherwise it blocks the loop for everyone.

```python
import asyncio, time  # asyncio and timing
from concurrent.futures import ProcessPoolExecutor  # for CPU work
from typing import Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # create app

def heavy(n: int) -> int:  # CPU-bound: module level so it can be pickled
    return sum(i * i for i in range(n))  # pure computation

@app.get("/io")  # I/O-bound -> concurrency (async)
async def io() -> Dict[str, str]:
    await asyncio.sleep(0.1)  # simulated DB call; the event loop stays free
    return {"kind": "io"}  # response

@app.get("/cpu")  # CPU-bound -> parallelism (processes)
async def cpu() -> Dict[str, int]:
    loop = asyncio.get_running_loop()  # current event loop
    with ProcessPoolExecutor(1) as pool:  # another process = another GIL
        result: int = await loop.run_in_executor(pool, heavy, 100_000)  # offload
    return {"sum": result}  # response

if __name__ == "__main__":  # required: spawn re-imports this file
    client = TestClient(app)
    print(client.get("/io").json(), client.get("/cpu").json())
# Output: {'kind': 'io'} {'sum': 333328333350000}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using threads to speed up CPU-bound code
```python
# Wrong - same speed as sequential because of the GIL
with ThreadPoolExecutor(8) as ex:
    list(ex.map(cpu_task, jobs))

# Correct
with ProcessPoolExecutor(8) as ex:
    list(ex.map(cpu_task, jobs))
```

❌ Mistake 2: Calling blocking code inside `async def`
```python
# Wrong - freezes the event loop for every user
async def handler():
    time.sleep(2)

# Correct
async def handler():
    await asyncio.sleep(2)            # or await asyncio.to_thread(blocking_fn)
```

❌ Mistake 3: Starting processes without the `__main__` guard
```python
# Wrong - on macOS/Windows each child re-imports the file and starts more children (RuntimeError)
pool = ProcessPoolExecutor(4)

# Correct
if __name__ == "__main__":
    pool = ProcessPoolExecutor(4)
```

---

## 🧠 Tricky Interview Question

**Q**: Is `asyncio` parallel? Can 100 threads run Python bytecode at the same time on a 16-core machine in CPython 3.13?

**Answer**:
```
asyncio: concurrent, NOT parallel (one thread, one task running at a time).
100 threads in standard CPython 3.13: concurrent, NOT parallel for Python code
(the GIL lets one thread run bytecode at a time), but their blocking I/O waits and
C extensions that release the GIL (hashlib, numpy) can overlap.
```
Free-threaded builds (`python3.13t`, experimental in 3.13) can run threads in parallel; the standard build cannot.

---

## ⚫ Interview Questions + Answers

Q1: Concurrency vs parallelism in one line?
A1: Concurrency is dealing with many things at once (interleaving); parallelism is doing many things at once (simultaneous execution).

Q2: Which tool for 1000 HTTP calls?
A2: asyncio with `httpx.AsyncClient` (or a thread pool for blocking `requests`). It is I/O-bound.

Q3: Which tool for resizing 10,000 images?
A3: `ProcessPoolExecutor` or `multiprocessing.Pool`, because it is CPU-bound.

Q4: Can concurrency exist without parallelism?
A4: Yes. Single core with a scheduler, or asyncio on one thread. Parallelism requires multiple execution units.

Q5: What is the downside of multiple processes?
A5: Higher memory, slow startup, and data must be pickled to move between processes (no shared objects).

---

## 🔷 When to Use + When Not to Use

✅ Use concurrency (asyncio/threads) when:
- Work is dominated by waiting (network, disk, DB)

✅ Use parallelism (processes) when:
- Work is dominated by computation (parsing, ML preprocessing, compression)

❌ Avoid when:
- The task is tiny (overhead of pools exceeds the gain)
- You have not measured a bottleneck first

---

## 📊 Visual Diagram

```
Concurrency (1 core):    A--B--A--B--A--B      tasks interleave
Parallelism (2 cores):   core1: A A A A A
                         core2: B B B B B      tasks truly simultaneous

 I/O-bound  ──► asyncio / threads
 CPU-bound  ──► processes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Concurrency | Tasks overlap in time | tasks का समय में overlap |
| Parallelism | Tasks run at the same instant | एक ही पल में चलना |
| I/O-bound | Mostly waiting | ज़्यादातर इंतज़ार |
| CPU-bound | Mostly computing | ज़्यादातर गणना |
| Event loop | Scheduler for async tasks | async tasks का scheduler |
| Core | One CPU execution unit | CPU की एक execution इकाई |

---

## ⚡ 3-Line Summary
English: Concurrency overlaps waiting; parallelism overlaps computing. In Python use asyncio/threads for I/O-bound work and processes for CPU-bound work. Always measure first.
Hindi: Concurrency इंतज़ार को overlap करती है; parallelism गणना को। Python में I/O-bound के लिए asyncio/threads और CPU-bound के लिए processes इस्तेमाल करें। पहले हमेशा नापें।

---

## ➡️ Next Topic
**222. threading** is done; continue with **223. Thread Class** — creating, starting, joining and naming threads.
