---

# 233. Process Pool (ProcessPoolExecutor)
# हिंदी में: Process Pool (ProcessPoolExecutor) — CPU वाले काम कई processes में बाँटना

---

## 🔵 Simple Definition (English)
`ProcessPoolExecutor` (from `concurrent.futures`) keeps a fixed group of worker processes alive. You hand it functions with `submit()` or `map()`, and it runs them in parallel on different CPU cores. Each process has its own GIL, so CPU-heavy Python code really runs in parallel.

## 🔵 सरल परिभाषा (Hindi)
`ProcessPoolExecutor` (`concurrent.futures` से) worker processes का एक fixed group चालू रखता है। आप `submit()` या `map()` से functions देते हैं, और यह उन्हें अलग-अलग CPU cores पर parallel चलाता है। हर process का अपना GIL होता है, इसलिए CPU-heavy Python code सच में parallel चलता है।

---

## 🔴 Problem it Solves
Threads cannot speed up CPU-bound Python code because of the GIL: only one thread runs Python bytecode at a time. Creating a `multiprocessing.Process` by hand for every task is also messy: you must start, join, collect results, and handle errors yourself. A pool reuses a few processes (starting a process is slow, 50-300 ms with spawn), gives you a `Future` per task, and re-raises worker exceptions in the parent.

## 🔴 यह क्यों बना? (Hindi)
GIL की वजह से threads CPU-bound Python code को तेज़ नहीं कर सकते: एक समय में सिर्फ एक thread Python bytecode चलाता है। हर task के लिए हाथ से `multiprocessing.Process` बनाना भी झंझट है: start, join, results इकट्ठा करना और errors संभालना सब खुद करना पड़ता है। Pool कुछ ही processes को बार-बार इस्तेमाल करता है (spawn में process शुरू करना धीमा है, 50-300 ms), हर task के लिए `Future` देता है, और worker की exception को parent में दोबारा raise करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → ProcessPoolExecutor(max_workers=N) prepares N worker processes
         (default N = os.process_cpu_count() on 3.13, os.cpu_count() before)
Step 2 → submit(fn, *args) pickles fn + args and puts them in a call queue
Step 3 → An idle worker unpickles it, runs fn in its own interpreter
Step 4 → The worker pickles the return value (or exception) and sends it back
Step 5 → The parent sets the Future result; .result() returns it or re-raises
Step 6 → Leaving the `with` block calls shutdown(wait=True) and joins workers

Parent process          Worker 1 (own GIL)     Worker 2 (own GIL)
   submit(f, 1) ------>  runs f(1)
   submit(f, 2) ------------------------------>  runs f(2)
   .result() <---------  pickled result
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ProcessPoolExecutor(max_workers=N) N worker processes तैयार करता है
         (default N = 3.13 में os.process_cpu_count(), पहले os.cpu_count())
Step 2 → submit(fn, *args) fn + args को pickle करके call queue में डालता है
Step 3 → खाली worker उसे unpickle करके अपने interpreter में fn चलाता है
Step 4 → Worker return value (या exception) को pickle करके वापस भेजता है
Step 5 → Parent Future में result set करता है; .result() उसे देता है या raise करता है
Step 6 → `with` block छोड़ने पर shutdown(wait=True) होता है और workers join हो जाते हैं
```

---

## 🟡 Real World Example
A Swiggy-style analytics job turns a 2 GB CSV of orders into daily revenue: the file is split into chunks and each chunk is aggregated in a separate process. A resume-parsing service in an AI product runs PDF text extraction plus OCR (CPU heavy) in a process pool so the FastAPI event loop stays free. Image thumbnails (Pillow), password hashing (bcrypt, argon2) and report generation are typical process-pool jobs.

## 🟡 Real Example Hindi mein
Swiggy जैसा analytics job 2 GB की orders CSV को daily revenue में बदलता है: file को chunks में बाँटा जाता है और हर chunk अलग process में aggregate होता है। AI product की resume-parsing service PDF text extraction और OCR (CPU heavy) को process pool में चलाती है ताकि FastAPI का event loop खाली रहे। Image thumbnails (Pillow), password hashing (bcrypt, argon2) और report generation सामान्य process-pool jobs हैं।

---

## 💻 Code Example — Basic
```python
# Basic ProcessPoolExecutor examples
from concurrent.futures import ProcessPoolExecutor        # the process pool


def square(n: int) -> int:                                  # must be a top-level function (picklable)
    return n * n                                            # runs in a worker process


if __name__ == "__main__":                                  # REQUIRED: spawn re-imports this file
    with ProcessPoolExecutor(max_workers=2) as pool:        # 2 worker processes, auto shutdown
        future = pool.submit(square, 7)                     # schedule one call, get a Future
        print(future.result())                              # wait for the answer -> 49
        print(list(pool.map(square, [1, 2, 3, 4])))         # map keeps input order
        print(type(future).__name__, future.done())         # the Future object after finishing

# Output:
# 49
# [1, 4, 9, 16]
# Future True
```

## 💻 Code Example — Advanced
```python
# Production style: CPU-heavy work, chunking, error handling, timeout
import math                                                 # for sqrt
from concurrent.futures import ProcessPoolExecutor, as_completed   # pool + completion iterator


def is_prime(n: int) -> bool:                               # CPU-bound check
    if n < 2:                                               # 0 and 1 are not prime
        return False                                        # early exit
    for i in range(2, math.isqrt(n) + 1):                   # trial division up to sqrt(n)
        if n % i == 0:                                      # found a divisor
            return False                                    # not prime
    return True                                             # prime


def count_primes(chunk: tuple[int, int]) -> int:            # one unit of work = a range
    lo, hi = chunk                                          # unpack the range
    return sum(1 for n in range(lo, hi) if is_prime(n))     # count primes in [lo, hi)


def risky(n: int) -> int:                                   # a task that may fail
    if n == 3:                                              # simulate a bad input
        raise ValueError(f"bad input {n}")                  # raised inside worker
    return n * 10                                           # normal result


def main() -> None:
    chunks: list[tuple[int, int]] = [(i, i + 25_000) for i in range(0, 100_000, 25_000)]   # 4 chunks
    with ProcessPoolExecutor(max_workers=4) as pool:        # 4 processes
        total: int = sum(pool.map(count_primes, chunks))    # fan-out, then add results
    print("primes below 100000:", total)                    # known answer: 9592

    with ProcessPoolExecutor(max_workers=2) as pool:        # new pool for error demo
        futures = {pool.submit(risky, n): n for n in range(1, 5)}   # future -> input map
        for fut in as_completed(futures):                   # results as they finish
            n: int = futures[fut]                           # which input is this?
            try:                                            # exceptions are re-raised here
                print(n, "->", fut.result(timeout=10))      # get result with a timeout
            except ValueError as exc:                       # worker exception arrives in parent
                print(n, "failed:", exc)                    # handle it


if __name__ == "__main__":                                  # guard needed on macOS/Windows (spawn)
    main()                                                  # run

# Output (the 4 lines for n=1..4 may appear in any order; run on Python 3.13):
# primes below 100000: 9592
# 1 -> 10
# 2 -> 20
# 4 -> 40
# 3 failed: bad input 3
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript / Node.js |
|---------|--------|---------------------|
| CPU parallelism | `ProcessPoolExecutor` | `worker_threads` pool (e.g. `piscina`) |
| Submit a job | `pool.submit(fn, arg)` | `pool.run(arg)` / `worker.postMessage(arg)` |
| Result object | `Future` | `Promise` |
| Data between workers | pickle (copied) | structured clone (copied) |
| Pass a function | top-level function only | worker file path |

```python
# Python way
from concurrent.futures import ProcessPoolExecutor      # stdlib pool

def cube(n: int) -> int:                                 # top-level function
    return n ** 3                                        # CPU work

if __name__ == "__main__":                               # guard for spawn
    with ProcessPoolExecutor() as pool:                  # default worker count
        print(list(pool.map(cube, [1, 2, 3])))           # [1, 8, 27]
```
```javascript
// JavaScript way — worker_threads with the piscina library
const Piscina = require('piscina');                      // npm i piscina
const pool = new Piscina({ filename: __dirname + '/cube.js' });   // worker file exports the function
Promise.all([1, 2, 3].map(n => pool.run(n)))             // run in parallel
  .then(console.log);                                    // [1, 8, 27]
```

Key difference: in Node you pass a worker *file*, in Python you pass a *function* that must be importable by name (picklable). Lambdas and nested functions do not work.

---

## 🟠 FastAPI Connection
A FastAPI `async def` endpoint must never run CPU work directly, because it blocks the event loop for every user. Create one pool at startup (lifespan) and call it with `loop.run_in_executor`. This code was run with `TestClient` on Python 3.13.

```python
# FastAPI example — CPU work in a process pool
import asyncio                                            # for the running loop
from concurrent.futures import ProcessPoolExecutor        # the pool
from contextlib import asynccontextmanager                # lifespan helper
from fastapi import FastAPI, Request                      # FastAPI


def heavy(n: int) -> int:                                 # top-level, picklable
    return sum(i * i for i in range(n))                   # CPU-bound


@asynccontextmanager                                      # startup/shutdown in one function
async def lifespan(app: FastAPI):
    app.state.pool = ProcessPoolExecutor(max_workers=2)   # created once at startup
    yield                                                 # app serves requests here
    app.state.pool.shutdown()                             # free the processes at shutdown


app: FastAPI = FastAPI(lifespan=lifespan)                 # attach lifespan


@app.get("/heavy/{n}")                                    # GET /heavy/1000
async def heavy_ep(n: int, request: Request) -> dict[str, int]:
    loop = asyncio.get_running_loop()                     # current event loop
    result: int = await loop.run_in_executor(request.app.state.pool, heavy, n)   # event loop stays free
    return {"result": result}                             # {"result": 332833500} for n=1000
```

Note: with `uvicorn --workers 4` every uvicorn worker creates its own pool, so 4 x 2 = 8 processes. Size the pool accordingly.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the `if __name__ == "__main__":` guard
✅ Correct: always guard the code that creates the pool (macOS and Windows use `spawn`; 3.14 also changes Linux's default to `forkserver`)

```python
from concurrent.futures import ProcessPoolExecutor
def f(x: int) -> int: return x
# Wrong — each child re-imports this file and tries to create a pool again
# -> RuntimeError: An attempt has been made to start a new process before the
#    current process has finished its bootstrapping phase.
# with ProcessPoolExecutor() as pool: print(list(pool.map(f, [1])))
# Right
if __name__ == "__main__":
    with ProcessPoolExecutor() as pool:
        print(list(pool.map(f, [1])))      # [1]
```

❌ Mistake 2: Submitting lambdas, nested functions or unpicklable objects
✅ Correct: use top-level functions and plain data (numbers, strings, lists, dicts)

```python
# Wrong — lambda cannot be pickled, the error appears when the result is requested
# pool.submit(lambda: 1).result()      # AttributeError / PicklingError (class varies by version)
# Right
def one() -> int: return 1
# pool.submit(one).result()            # 1
```

❌ Mistake 3: Sending huge objects to every task
✅ Correct: pass small arguments (file paths, ids, ranges); let each worker load its own data, or use shared memory

```python
# Wrong — a 500 MB list is pickled and copied for EVERY call
# pool.map(process_row, huge_list)
# Right — send ranges, let the worker read the file
# pool.map(process_chunk, [(0, 1_000_000), (1_000_000, 2_000_000)], )
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from concurrent.futures import ProcessPoolExecutor

def risky(n: int) -> int:
    if n == 2:
        raise ValueError("two")
    return n

if __name__ == "__main__":
    with ProcessPoolExecutor(1) as pool:
        it = pool.map(risky, [1, 2, 3])
        print(type(it).__name__)
        print(next(it))
        try:
            print(next(it))
        except ValueError as e:
            print("raised:", e)
        print(list(pool.map(risky, [1, 3])))
```
Answer: Output is `generator`, `1`, `raised: two`, `[1, 3]` (verified on 3.13). `pool.map` returns a generator, not a list. All tasks are submitted at once, but the exception from the second one is raised only when you *iterate to that item*, not when you call `map`. Results come in input order. Once an exception is raised by the generator, you cannot continue the same iterator, so start a new `map` call (the last line) for new work.

---

## ⚫ Interview Questions + Answers

Q1: When do you use `ProcessPoolExecutor` instead of `ThreadPoolExecutor`?
A1: Use processes for CPU-bound work (math, parsing, image processing, hashing) because each process has its own GIL. Use threads for I/O-bound work (HTTP, DB, files) because they are cheaper and share memory. Rule of thumb: waiting on something outside Python = threads; computing inside Python = processes.

Q2: Why must the function be at module top level?
A2: Arguments and the function are sent to the worker by pickle. Pickle stores functions by import path (`module.name`), so lambdas, closures and nested functions cannot be found by the worker. With `spawn`, the worker also re-imports your main module, which is why the `__main__` guard is required.

Q3: What is the default number of workers and how do you choose?
A3: `os.process_cpu_count()` on 3.13 (earlier: `os.cpu_count()`), capped to 61 on Windows. For pure CPU work use number of cores; more workers just add overhead. Pools in a web server multiply by the number of server workers.

Q4: How are exceptions handled?
A4: An exception in the worker is pickled and re-raised by `future.result()` (or while iterating `map`). If a worker process dies abruptly (killed, segfault) the pool becomes broken and raises `BrokenProcessPool`; you must create a new pool.

Q5: `map` vs `submit` + `as_completed`?
A5: `map` returns results in input order and is simplest. `submit` returns a `Future` per task; `as_completed` yields futures in finish order, which is better for progress bars, per-task error handling and timeouts. `map` also accepts `chunksize` to reduce pickling overhead for many tiny tasks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The work is CPU-bound and takes noticeably longer than the cost of pickling the data
- You want real multi-core speedup without managing `Process` objects
- You need to keep an async server responsive while heavy work runs
- Tasks are independent and take small inputs and return small outputs

❌ Avoid when:
- Work is I/O-bound, use threads or asyncio
- Tasks are tiny (microseconds): pickling and IPC cost more than the work
- Tasks need shared mutable state; use shared memory, a database or a queue
- You need to share unpicklable objects (open sockets, DB connections, locks)

---

## 📊 Visual Diagram
```
                      +-------------------------------+
 main process         |  ProcessPoolExecutor          |
 (your FastAPI app)   |  call queue  ---> result queue|
        |             +--------+-----------+----------+
        | submit(f, x)         |           |
        v                      v           v
   Future (pending)      worker 1     worker 2   ...  worker N
                         own GIL      own GIL         own GIL
                         own memory   own memory      own memory
        ^                      |           |
        +---- result pickled --+-----------+

 data goes in and out as pickle bytes, nothing is shared by default
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Process pool | Fixed set of reusable worker processes | दोबारा इस्तेमाल होने वाले worker processes का समूह |
| Future | Object for a result that is not ready yet | अभी तैयार न हुए result का object |
| Pickle | Python object to bytes conversion | Object को bytes में बदलना |
| `spawn` | Start a fresh interpreter, re-import main | नया interpreter शुरू करना |
| `BrokenProcessPool` | Worker died, pool unusable | Worker मर गया, pool बेकार |
| `chunksize` | Items sent to a worker per message | एक बार में worker को भेजे जाने वाले items |

---

## ⚡ 3-Line Summary
English: `ProcessPoolExecutor` runs functions in separate processes, each with its own GIL, so CPU-bound code uses all cores. Functions and data must be picklable and creation must sit under the `__main__` guard. In FastAPI, call it through `run_in_executor` so the event loop never blocks.
Hindi: `ProcessPoolExecutor` functions को अलग processes में चलाता है, हर एक का अपना GIL, इसलिए CPU-bound code सभी cores इस्तेमाल करता है। Functions और data picklable होने चाहिए और pool `__main__` guard के अंदर बनना चाहिए। FastAPI में इसे `run_in_executor` से बुलाएं ताकि event loop कभी block न हो।

---

## ➡️ Next Topic
**234. Queue + Pipe (IPC)** — how separate processes talk to each other: `multiprocessing.Queue` for many-to-many messages and `Pipe` for a fast two-way channel.
