---

# 252. When to Use Each Approach
# हिंदी में: कौन सा तरीका कब इस्तेमाल करें (threads vs processes vs asyncio)

---

## 🔵 Simple Definition (English)
Python gives you three ways to do many things at once: `asyncio` (one thread, many coroutines), `threading` (many threads, shared memory), and `multiprocessing` / `ProcessPoolExecutor` (many processes, separate memory). Which one is right depends on one question: is your work waiting (I/O-bound) or calculating (CPU-bound)?

## 🔵 सरल परिभाषा (Hindi)
Python में एक साथ कई काम करने के तीन तरीके हैं: `asyncio` (एक thread, कई coroutines), `threading` (कई threads, shared memory) और `multiprocessing` / `ProcessPoolExecutor` (कई processes, अलग memory)। सही तरीका एक सवाल से तय होता है: आपका काम इंतज़ार कर रहा है (I/O-bound) या गणना कर रहा है (CPU-bound)?

---

## 🔴 Problem it Solves
Beginners pick the wrong tool: they add threads to a number-crunching loop (no speedup because of the GIL), or spawn processes to call 100 APIs (huge memory, slow startup), or call a blocking `requests.get()` inside an `async def` (freezes the whole server). Choosing correctly is the difference between a 10x faster service and a slower, buggier one.

## 🔴 यह क्यों बना? (Hindi)
नए developers गलत tool चुन लेते हैं: number-crunching loop में threads लगा देते हैं (GIL की वजह से speedup नहीं मिलता), या 100 APIs call करने के लिए processes बना देते हैं (बहुत memory, slow startup), या `async def` के अंदर blocking `requests.get()` चला देते हैं (पूरा server अटक जाता है)। सही चुनाव का मतलब है 10 गुना तेज़ service बनाम धीमी और buggy service।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Ask: is the task mostly WAITING (network, DB, disk) or CALCULATING (math, parsing, ML)?
Step 2 → WAITING + many connections (100s-1000s)  -> asyncio (cheapest, one thread)
Step 3 → WAITING + library is blocking (requests, old SDK) -> threads (or asyncio.to_thread)
Step 4 → CALCULATING (CPU-bound) -> processes (each has its own GIL), or numpy / C extensions
Step 5 → MIXED -> asyncio for I/O + run_in_executor(ProcessPool) for the heavy math
Step 6 → Python 3.13 free-threaded build (PEP 703, experimental) may let threads use many cores later

Cost per unit:  coroutine ~ KBs   <   thread ~ 8 MB stack   <   process ~ tens of MBs
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पूछो: काम ज़्यादातर INTERVAL (network, DB, disk) है या CALCULATION (math, parsing, ML)?
Step 2 → WAITING + बहुत सारे connections (100s-1000s)  -> asyncio (सबसे सस्ता, एक thread)
Step 3 → WAITING + library blocking है (requests, पुराना SDK) -> threads (या asyncio.to_thread)
Step 4 → CALCULATING (CPU-bound) -> processes (हर एक का अपना GIL), या numpy / C extensions
Step 5 → MIXED -> I/O के लिए asyncio + भारी math के लिए run_in_executor(ProcessPool)
Step 6 → Python 3.13 free-threaded build (PEP 703, experimental) भविष्य में threads को कई cores दे सकता है

हर unit की cost:  coroutine ~ KBs   <   thread ~ 8 MB stack   <   process ~ दसियों MB
```

---

## 🟡 Real World Example
A Swiggy-style order service: calling the restaurant API, payment gateway and SMS provider is pure waiting, so `asyncio.gather` handles it. Generating the monthly GST invoice PDF for 10,000 merchants is CPU work, so it goes to a `ProcessPoolExecutor`. A legacy SDK for a bank that only has blocking calls is wrapped with `asyncio.to_thread`.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service: restaurant API, payment gateway और SMS provider call करना सिर्फ इंतज़ार है, इसलिए `asyncio.gather` इसे संभालता है। 10,000 merchants के लिए monthly GST invoice PDF बनाना CPU का काम है, इसलिए `ProcessPoolExecutor` में जाता है। किसी bank का legacy SDK जिसमें सिर्फ blocking calls हैं उसे `asyncio.to_thread` में लपेटा जाता है।

---

## 💻 Code Example — Basic
```python
# Same I/O-bound job done 3 ways: sequential, threads, asyncio
import asyncio                                     # event loop and coroutines
import time                                        # blocking sleep and timer
from concurrent.futures import ThreadPoolExecutor  # thread pool


def fetch_blocking(i: int) -> int:                 # pretend blocking HTTP call
    time.sleep(0.2)                                # waiting for the network
    return i * 10                                  # fake response


async def fetch_async(i: int) -> int:              # pretend non-blocking HTTP call
    await asyncio.sleep(0.2)                       # waiting, but loop stays free
    return i * 10                                  # fake response


def sequential() -> tuple[list[int], float]:       # approach 0: one after another
    start: float = time.perf_counter()             # start timer
    result: list[int] = [fetch_blocking(i) for i in range(3)]   # 3 x 0.2s
    return result, time.perf_counter() - start     # data and elapsed


def threaded() -> tuple[list[int], float]:         # approach 1: threads
    start: float = time.perf_counter()             # start timer
    with ThreadPoolExecutor(max_workers=3) as pool:   # 3 worker threads
        result: list[int] = list(pool.map(fetch_blocking, range(3)))   # run in parallel
    return result, time.perf_counter() - start     # data and elapsed


async def with_asyncio() -> tuple[list[int], float]:   # approach 2: asyncio
    start: float = time.perf_counter()             # start timer
    result: list[int] = await asyncio.gather(*(fetch_async(i) for i in range(3)))   # concurrent
    return result, time.perf_counter() - start     # data and elapsed


r1, t1 = sequential()                              # run sequential
r2, t2 = threaded()                                # run threads
r3, t3 = asyncio.run(with_asyncio())               # run asyncio
print("sequential", r1, round(t1, 1))              # about 0.6 seconds
print("threads   ", r2, round(t2, 1))              # about 0.2 seconds
print("asyncio   ", r3, round(t3, 1))              # about 0.2 seconds

# Output:
# sequential [0, 10, 20] 0.6
# threads    [0, 10, 20] 0.2
# asyncio    [0, 10, 20] 0.2
```

## 💻 Code Example — Advanced
```python
# Production style: one async function that mixes I/O, blocking libs and CPU work
import asyncio                                     # event loop
import hashlib                                     # CPU-heavy hashing for demo
import time                                        # blocking sleep
from concurrent.futures import ProcessPoolExecutor   # separate processes, separate GILs


def cpu_heavy(n: int) -> str:                      # pure CPU work (must be top-level to pickle)
    data: bytes = b"x" * 1000                      # starting bytes
    for _ in range(n):                             # many rounds of hashing
        data = hashlib.sha256(data).digest()       # CPU-bound loop
    return data.hex()[:8]                          # short fingerprint


def legacy_blocking_sdk(order_id: int) -> str:     # a blocking third-party SDK we cannot change
    time.sleep(0.1)                                # blocks its thread, not the loop
    return f"bank-ok-{order_id}"                   # fake response


async def call_api(order_id: int) -> str:          # a native async call
    await asyncio.sleep(0.1)                       # non-blocking wait
    return f"api-ok-{order_id}"                    # fake response


async def process_order(order_id: int, pool: ProcessPoolExecutor) -> dict[str, str]:
    loop = asyncio.get_running_loop()              # needed for run_in_executor
    api, bank, digest = await asyncio.gather(      # run all three at the same time
        call_api(order_id),                        # I/O -> coroutine
        asyncio.to_thread(legacy_blocking_sdk, order_id),   # blocking I/O -> thread
        loop.run_in_executor(pool, cpu_heavy, 50_000),      # CPU -> process
    )
    return {"api": api, "bank": bank, "digest": digest}     # combined result


async def main() -> None:
    with ProcessPoolExecutor(max_workers=2) as pool:        # create the process pool once
        try:                                       # error handling around the batch
            results = await asyncio.wait_for(      # never wait forever
                asyncio.gather(*(process_order(i, pool) for i in range(3))),
                timeout=30,                        # overall budget in seconds
            )
        except asyncio.TimeoutError:               # budget exceeded
            print("timed out")                     # report and stop
            return
    for r in results:                              # show every order result
        print(r)


if __name__ == "__main__":                         # required guard for multiprocessing on macOS/Windows
    asyncio.run(main())                            # start the loop

# Output:
# {'api': 'api-ok-0', 'bank': 'bank-ok-0', 'digest': '79d0d925'}
# {'api': 'api-ok-1', 'bank': 'bank-ok-1', 'digest': '79d0d925'}
# {'api': 'api-ok-2', 'bank': 'bank-ok-2', 'digest': '79d0d925'}
```

---

## 🟠 JavaScript vs Python Comparison

| Need | Python | JavaScript (Node.js) |
|------|--------|----------------------|
| Many network calls | `asyncio` | default event loop (`Promise.all`) |
| Blocking library | `asyncio.to_thread` / threads | `worker_threads` or just async API |
| CPU-bound work | `multiprocessing` / `ProcessPoolExecutor` | `worker_threads` |
| Threads share memory | yes, but GIL (3.13 default build) | `SharedArrayBuffer` only |
| Async is default? | No, you must opt in with `async def` | Yes, almost all I/O is async |

```python
# Python way: mix I/O and CPU explicitly
import asyncio                                       # event loop
async def main() -> None:
    a, b = await asyncio.gather(asyncio.sleep(0.1, "io"), asyncio.to_thread(sum, range(10)))   # I/O + thread
    print(a, b)                                      # io 45
asyncio.run(main())                                  # run it
```
```javascript
// JavaScript way: I/O is already async, CPU needs a worker
const { Worker } = require('worker_threads');        // for CPU work
const [a, b] = await Promise.all([                   // I/O in parallel
  new Promise(r => setTimeout(() => r('io'), 100)),
  new Promise(r => new Worker('./sum.js').on('message', r)),   // CPU in a worker
]);
```

Key difference: In Node.js, the single event loop is the only model and heavy CPU blocks everything. Python gives you three models, so you must choose consciously. A `for` loop with heavy math inside `async def` blocks the loop in both languages.

---

## 🟠 FastAPI Connection
FastAPI runs `async def` endpoints on the event loop and plain `def` endpoints in a thread pool (about 40 threads by default via AnyIO). So: use `async def` with async libraries (httpx, asyncpg), use plain `def` when you call blocking code, and push CPU work to a process pool.

```python
# FastAPI example — all three models in one app (tested with TestClient)
import asyncio                                       # async sleep and thread helper
import time                                          # blocking sleep
from fastapi import FastAPI                          # framework
from fastapi.testclient import TestClient            # in-process HTTP client

app: FastAPI = FastAPI()                             # create app


@app.get("/async-io")                                # async endpoint
async def async_io() -> dict[str, str]:
    await asyncio.sleep(0.05)                        # non-blocking wait on event loop
    return {"model": "asyncio"}                      # reply


@app.get("/blocking-io")                             # plain def -> FastAPI uses a thread
def blocking_io() -> dict[str, str]:
    time.sleep(0.05)                                 # blocking is OK here, thread absorbs it
    return {"model": "thread-pool"}                  # reply


@app.get("/wrapped")                                 # async endpoint calling blocking code
async def wrapped() -> dict[str, str]:
    await asyncio.to_thread(time.sleep, 0.05)        # push blocking call off the loop
    return {"model": "to_thread"}                    # reply


with TestClient(app) as client:                      # run app in-process
    for path in ("/async-io", "/blocking-io", "/wrapped"):   # hit each route
        print(path, client.get(path).json())         # show result

# Output:
# /async-io {'model': 'asyncio'}
# /blocking-io {'model': 'thread-pool'}
# /wrapped {'model': 'to_thread'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside `async def`
✅ Correct: use an async library or `asyncio.to_thread`

```python
import asyncio, time
# Wrong — freezes the whole event loop for 1 second, every other request waits
async def bad() -> None:
    time.sleep(1)
# Right
async def good() -> None:
    await asyncio.sleep(1)                 # or: await asyncio.to_thread(time.sleep, 1)
```

❌ Mistake 2: Using threads to speed up CPU-bound code
✅ Correct: use processes (or numpy / C extensions that release the GIL)

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
# Wrong — threads share one GIL, CPU loops run one at a time (no speedup)
# with ThreadPoolExecutor() as p: p.map(cpu_heavy, jobs)
# Right
# with ProcessPoolExecutor() as p: p.map(cpu_heavy, jobs)
```

❌ Mistake 3: Creating a new process for every tiny task
✅ Correct: create one pool and reuse it; send big enough chunks of work

---

## 🧠 Tricky Interview Question

```python
# How long will this take, and why?
import asyncio, time

async def work(n: int) -> int:
    time.sleep(0.1)                  # NOTE: time.sleep, not asyncio.sleep
    return n

async def main() -> None:
    start = time.perf_counter()
    await asyncio.gather(work(1), work(2), work(3))
    print(round(time.perf_counter() - start, 1))

asyncio.run(main())

# Output:
# 0.3
```
Answer: About `0.3` seconds, not `0.1`. `gather` schedules three coroutines, but each one calls the blocking `time.sleep` without ever hitting an `await` that yields control, so the event loop can only run them one after another. Concurrency in asyncio only happens at `await` points. Replace it with `await asyncio.sleep(0.1)` to get `0.1`.

---

## ⚫ Interview Questions + Answers

Q1: Which approach for 1,000 concurrent HTTP calls?
A1: `asyncio` with `httpx.AsyncClient` (and a `Semaphore` to limit concurrency). 1,000 threads would cost GBs of stack memory; coroutines cost KBs.

Q2: Which approach for resizing 10,000 images?
A2: `ProcessPoolExecutor`. It is CPU-bound, so each process gets its own GIL and uses a separate core. Pillow/numpy may release the GIL, but processes are the safe default.

Q3: Why does the GIL not hurt I/O-bound threads?
A3: A thread releases the GIL while waiting for I/O (socket read, `sleep`, file read), so other threads can run during that time. The GIL only hurts when threads compete for CPU.

Q4: How do you call blocking code from async code?
A4: `await asyncio.to_thread(func, *args)` (3.9+) or `loop.run_in_executor(None, func, *args)`. For CPU work pass a `ProcessPoolExecutor` as the first argument of `run_in_executor`.

Q5: What changes in Python 3.13?
A5: An experimental free-threaded build (`python3.13t`, PEP 703) can disable the GIL, so threads may run Python code on many cores. It is not the default and many C extensions are not yet ready, so the three-way choice still applies in production.

---

## 🔷 When to Use + When Not to Use
✅ Use asyncio when:
- Thousands of connections, mostly waiting (APIs, WebSockets, DB)
- All libraries have async versions

✅ Use threads when:
- The library is blocking and has no async version
- Small number of concurrent tasks, simple code

✅ Use processes when:
- CPU-bound work: image/video, ML inference, big parsing, encryption

❌ Avoid:
- asyncio with CPU-heavy loops (blocks everyone)
- threads for CPU-bound work (GIL)
- processes for tiny, fast tasks (startup and pickling cost more than the work)

---

## 📊 Visual Diagram
```
                    What is the work?
                          |
            +-------------+--------------+
            |                            |
      waiting (I/O)                calculating (CPU)
            |                            |
   library async?                 ProcessPoolExecutor
     /         \                   (one GIL per process)
   yes          no
    |            |
 asyncio    threads / asyncio.to_thread

Mixed workload:  asyncio loop  --run_in_executor-->  process pool
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| I/O-bound | Time spent waiting for network/disk | इंतज़ार में लगने वाला समय |
| CPU-bound | Time spent calculating | गणना में लगने वाला समय |
| GIL | Lock letting one thread run Python bytecode | एक समय में एक thread की lock |
| Coroutine | Function that can pause at `await` | रुक सकने वाला function |
| Executor | Pool that runs functions off the loop | loop के बाहर काम चलाने वाला pool |
| `to_thread` | Run a blocking function in a thread | blocking function को thread में चलाना |

---

## ⚡ 3-Line Summary
English: Waiting work goes to `asyncio` (or threads for blocking libraries); calculating work goes to processes. Mixed apps keep the event loop for I/O and offload CPU with `run_in_executor`. Never block the loop.
Hindi: इंतज़ार वाला काम `asyncio` (या blocking libraries के लिए threads) में जाता है; गणना वाला काम processes में। Mixed apps I/O के लिए event loop रखते हैं और CPU काम `run_in_executor` से बाहर भेजते हैं। Loop को कभी block मत करो।

---

## ➡️ Next Topic
**253. uvloop — Fast Event Loop** — a drop-in replacement for the default asyncio loop, written in Cython on top of libuv, that makes servers like Uvicorn noticeably faster.
