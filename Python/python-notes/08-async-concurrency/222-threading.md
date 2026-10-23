---

# 222. Threading — Complete Guide
# हिंदी में: Threading — पूरी Guide

---

## 🔵 Simple Definition (English)
Python's `threading` module creates OS threads that run concurrently within the same process and share memory. Due to the GIL, only one thread executes Python bytecode at a time — but threads ARE useful for I/O-bound tasks (network calls, file I/O, DB queries) because the GIL is released during I/O. `ThreadPoolExecutor` (from `concurrent.futures`) is the modern, cleaner API.

## 🔵 सरल परिभाषा (Hindi)
Python का `threading` module OS threads create करता है जो same process में share memory के साथ concurrently run होते हैं। GIL की वजह से एक time पर एक ही thread Python bytecode execute करती है — लेकिन I/O-bound tasks (network calls, file I/O, DB queries) के लिए threads useful हैं क्योंकि I/O के दौरान GIL release होती है। `ThreadPoolExecutor` modern, cleaner API है।

---

## 🔴 Problem it Solves
Waiting for 10 HTTP API calls one by one takes 10s if each takes 1s. With threading, all 10 calls run "simultaneously" — total time ~1s. Same for DB queries, file reads. Threading gives concurrency for I/O-bound work without the complexity of asyncio (which requires async/await throughout the codebase).

## 🔴 यह क्यों बना? (Hindi)
10 HTTP API calls एक-एक करके 10s लेती हैं। Threading से सब एक साथ ~1s में। DB queries, file reads — same। Threading I/O-bound work के लिए concurrency देता है asyncio की complexity के बिना (asyncio को पूरे codebase में async/await चाहिए)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create Thread(target=func, args=(arg1,)) objects
Step 2 → Call thread.start() → OS creates the thread, starts running func
Step 3 → GIL allows only one thread to run Python at a time
Step 4 → Thread doing I/O → releases GIL → other threads can run Python
Step 5 → thread.join() → main thread waits for this thread to finish
Step 6 → All threads finish → program continues
```

---

## 🟡 Real World Example
Zomato order tracking: fetch restaurant status, rider location, and estimated time in parallel — three independent API calls. Sequentially: 300ms + 200ms + 400ms = 900ms. With threads: max(300, 200, 400) = ~400ms. Nearly 2.5x faster for the user.

## 🟡 Real Example Hindi mein
Zomato order tracking: restaurant status, rider location, estimated time — तीनों independent API calls। Sequential: 900ms। Threads से: ~400ms। User को nearly 2.5x faster response।

---

## 💻 Code Example — Basic
```python
# Basic Thread — I/O-bound tasks (right use case for threads)
import threading
import time
import requests
from typing import Any

results: dict[str, Any] = {}
lock = threading.Lock()     # protects shared 'results' dict from concurrent writes

def fetch_data(url: str, key: str) -> None:
    """Download URL — GIL released during network I/O."""
    response = requests.get(url, timeout=5)
    with lock:                          # acquire lock before writing shared state
        results[key] = response.json()

# Sequential (baseline):
start = time.time()
for url, key in [("https://api1.com/data", "a"), ("https://api2.com/data", "b")]:
    fetch_data(url, key)
print(f"Sequential: {time.time()-start:.2f}s")   # ~2s if each takes 1s

# Threaded:
start = time.time()
threads = [
    threading.Thread(target=fetch_data, args=(url, key))
    for url, key in [("https://api1.com/data", "a"), ("https://api2.com/data", "b")]
]
for t in threads:
    t.start()           # start all threads
for t in threads:
    t.join()            # wait for all to finish
print(f"Threaded: {time.time()-start:.2f}s")      # ~1s (parallel I/O)

# Thread with daemon=True — thread dies when main program exits:
def background_monitor():
    while True:
        print("Monitoring...")
        time.sleep(5)

monitor = threading.Thread(target=background_monitor, daemon=True)
monitor.start()         # starts in background
# When main program exits, daemon thread is killed automatically
```

## 💻 Code Example — Advanced
```python
# ThreadPoolExecutor — modern, recommended API
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from typing import Callable

# Basic ThreadPoolExecutor:
def process_order(order_id: int) -> dict:
    """Simulate API call — takes ~1s."""
    time.sleep(1)
    return {"order_id": order_id, "status": "processed"}

order_ids = list(range(1, 11))   # 10 orders

# Without threads: ~10s
with ThreadPoolExecutor(max_workers=5) as executor:
    # map: submits all tasks, returns results in ORDER (not completion order)
    results = list(executor.map(process_order, order_ids))
# ~2s (10 tasks / 5 workers each taking 1s)

# submit: more control, results in COMPLETION order:
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(process_order, oid): oid for oid in order_ids}

    for future in as_completed(futures):          # yields as each completes
        order_id = futures[future]
        try:
            result = future.result()              # raises if the task raised
            print(f"Order {order_id}: {result['status']}")
        except Exception as e:
            print(f"Order {order_id} failed: {e}")

# Thread safety — Lock, RLock, Semaphore:
class ThreadSafeCounter:
    """Counter safe for concurrent increment from multiple threads."""
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:            # acquire → do work → release (even on exception)
            self._value += 1
            return self._value      # read consistent value while lock held

    @property
    def value(self) -> int:
        with self._lock:            # lock for reads too (prevents torn reads)
            return self._value

# Thread-local storage — each thread gets its own copy:
_thread_local = threading.local()

def set_request_context(user_id: str):
    _thread_local.user_id = user_id

def get_request_context() -> str:
    return getattr(_thread_local, "user_id", None)

# Useful in web servers: each request runs in its own thread,
# set context at start → available throughout that request's call stack

# Event — coordinate between threads:
download_complete = threading.Event()

def downloader():
    time.sleep(2)          # simulate download
    print("Download done")
    download_complete.set()   # signal the event

def processor():
    download_complete.wait()  # blocks until event is set
    print("Processing downloaded data")

t1 = threading.Thread(target=downloader)
t2 = threading.Thread(target=processor)
t1.start(); t2.start()
t1.join(); t2.join()
# "Download done" then "Processing downloaded data" — in order
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: explicit threading with GIL constraint
from concurrent.futures import ThreadPoolExecutor
import time

def fetch(url):
    time.sleep(1)    # I/O wait — GIL released
    return f"data from {url}"

urls = ["url1", "url2", "url3"]
with ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(fetch, urls))
# ~1s (I/O-bound — threads are effective)
```

```javascript
// JavaScript: single-threaded event loop (no GIL problem!)
// Concurrent I/O via Promise.all — no threads needed:
async function fetch(url) {
    await new Promise(resolve => setTimeout(resolve, 1000)); // simulate I/O
    return `data from ${url}`;
}

const urls = ["url1", "url2", "url3"];
const results = await Promise.all(urls.map(fetch));  // ~1s

// Worker threads (Node.js): for CPU-bound work (like Python multiprocessing)
const { Worker } = require('worker_threads');
// JS equivalent of Python's threading is more like asyncio (event loop)
// Python threading ≈ Node.js worker_threads
```

---

## 🟠 FastAPI Connection

```python
# FastAPI runs sync route handlers in a ThreadPoolExecutor automatically!
# Regular 'def' routes → FastAPI runs them in thread pool to avoid blocking event loop

from fastapi import FastAPI
import time, httpx

app = FastAPI()

# FastAPI runs this in ThreadPoolExecutor (default 40 workers):
@app.get("/sync-endpoint")
def sync_handler():
    # Blocking call is OK here — FastAPI moved it to a thread
    time.sleep(1)
    return {"result": "done"}

# Async endpoint — runs in event loop (don't block!):
@app.get("/async-endpoint")
async def async_handler():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()

# Calling synchronous I/O from async route with threads:
from fastapi.concurrency import run_in_threadpool

@app.get("/mixed")
async def mixed_handler():
    # Run blocking code in thread pool without blocking event loop:
    result = await run_in_threadpool(some_blocking_function, arg1, arg2)
    return result

# Real use case: PIL image processing (CPU+I/O, no async support)
from PIL import Image
import io

@app.post("/resize-image")
async def resize_image(file: bytes):
    # PIL is synchronous — must run in thread pool:
    def process():
        img = Image.open(io.BytesIO(file))
        img = img.resize((800, 600))
        output = io.BytesIO()
        img.save(output, format="JPEG")
        return output.getvalue()

    result = await run_in_threadpool(process)
    return {"size": len(result)}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using threads for CPU-bound work (GIL makes it slower!)
```python
# Wrong — GIL makes this slower than single thread:
import threading

def cpu_work(n: int) -> int:
    return sum(i * i for i in range(n))

# 2 threads on CPU-bound: ~2x SLOWER than 1 thread (GIL contention overhead)
threads = [threading.Thread(target=cpu_work, args=(10_000_000,)) for _ in range(2)]
for t in threads: t.start()
for t in threads: t.join()

# Correct — use multiprocessing for CPU-bound:
from multiprocessing import Pool
with Pool(2) as p:
    results = p.map(cpu_work, [10_000_000, 10_000_000])   # actually parallel
```

❌ Mistake 2: Race condition — modifying shared state without a lock
```python
# Wrong — race condition! counter may not reach 10000:
counter = 0

def increment():
    global counter
    for _ in range(1000):
        counter += 1    # NOT atomic: read → add → write (3 operations)

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)    # might be 9872 or any number < 10000!

# Correct — use a Lock:
lock = threading.Lock()
counter = 0

def safe_increment():
    global counter
    for _ in range(1000):
        with lock:
            counter += 1   # atomic now
```

---

## 🧠 Tricky Interview Question

```python
import threading

results = []

def worker(i):
    results.append(i * 2)

threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(sorted(results))
```
Question: Is this code thread-safe? What will `sorted(results)` print?
Answer: It might be thread-safe *in CPython* because Python's `list.append()` is atomic at the GIL level (it's a single bytecode). But this is an **implementation detail of CPython** — not guaranteed. In PyPy or future Python without GIL, it's a race condition. The **sorted result is always `[0, 2, 4, 6, 8]`** — values are correct even if order of insertion varies. Proper code should use a `Lock` around `append`.

---

## ⚫ Interview Questions + Answers

Q1: When should you use threads vs asyncio vs multiprocessing?
A1: **Threads**: I/O-bound work in a codebase that can't use async/await (legacy code, sync libraries like `requests`, PIL). **asyncio**: I/O-bound work in async-capable code — better performance, less overhead than threads (no OS context switching). **multiprocessing**: CPU-bound work (data processing, image manipulation, ML inference) — bypasses GIL with separate processes. Rule of thumb: async for greenfield async-capable code, threads for sync I/O, multiprocessing for CPU.

Q2: What is a race condition and how do you prevent it?
A2: A race condition occurs when two threads read and write shared state simultaneously — the final value depends on which thread runs first. Example: `x += 1` is not atomic (read, add, write — three steps). Prevention: `threading.Lock()` makes a critical section atomic. Use `with lock:` (context manager) so the lock is always released even if an exception occurs.

Q3: What is `threading.local()` and when is it useful?
A3: `threading.local()` creates an object where each thread has its own independent copy of attributes. Setting `local.x = 1` in thread A doesn't affect thread B's `local.x`. Useful for: per-request context in multi-threaded web servers (user ID, request ID), per-thread DB connections in connection pools. Flask uses thread-local for `request` and `g` objects.

Q4: What is the difference between `thread.join()` and `daemon=True`?
A4: `thread.join()` blocks the calling thread until the joined thread finishes — use it when you need the thread's work to complete before continuing. `daemon=True` makes a thread a background daemon — when all non-daemon threads finish, Python exits and kills daemon threads immediately (no waiting). Use daemon threads for background monitoring tasks that shouldn't prevent program exit.

Q5: What is `ThreadPoolExecutor` and why prefer it over `Thread`?
A5: `ThreadPoolExecutor(max_workers=N)` manages a pool of N reusable threads — avoids the overhead of creating/destroying threads per task. `submit(fn, *args)` returns a `Future` you can inspect. `map(fn, iterable)` applies a function to all items concurrently and returns results in order. Used as a context manager (`with`): automatically waits for all tasks on exit. Cleaner, safer, and more performant than manually managing `Thread` objects.

---

## 🔷 When to Use + When Not to Use

✅ Use threading when:
- I/O-bound concurrent tasks in synchronous code
- Calling synchronous blocking libraries (requests, psycopg2, boto3 sync)
- Running sync code from an async FastAPI route (`run_in_threadpool`)
- Background tasks that shouldn't block the main thread (with daemon=True)

❌ Avoid threading when:
- CPU-bound work — use `multiprocessing`
- New async-capable code — use `asyncio`
- Need zero-overhead concurrency for many connections — use asyncio

---

## 📊 Visual Diagram
```
I/O-bound (threads ARE effective):

Thread 1: ──[Python]──[wait for I/O]──────────────────[Python]──
Thread 2: ──────────────[Python]──[wait for I/O]──────────[Python]──
GIL:       ████████     (released)  █████████       (released) ██

CPU-bound (GIL blocks):

Thread 1: ──[Python]──[GIL wait]──[Python]──[GIL wait]──
Thread 2: ──[GIL wait]──[Python]──[GIL wait]──[Python]──
↑ Threads take turns — effectively sequential!
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Thread | Lightweight execution unit | Lightweight execution unit |
| GIL | Global Interpreter Lock | Python का global lock |
| Race condition | Shared state corruption from concurrent access | Concurrent access से data corruption |
| Lock | Mutual exclusion primitive | Mutual exclusion के लिए primitive |
| ThreadPoolExecutor | Pool of reusable threads | Reusable threads का pool |
| daemon thread | Thread killed on program exit | Program exit पर kill हो जाती thread |
| thread-local | Per-thread storage | हर thread की अपनी storage |

---

## ⚡ 3-Line Summary
English: Threads are effective for I/O-bound work (network, files, DB) where the GIL is released during waiting — for CPU-bound work, threads contend on the GIL and are slower than a single thread. `ThreadPoolExecutor` is the modern API: submit tasks, get `Future` objects, and all cleanup happens automatically with the context manager. Protect shared mutable state with `threading.Lock()` — `counter += 1` is not atomic!
Hindi: Threads I/O-bound work के लिए effective हैं — GIL I/O के दौरान release होती है। CPU-bound के लिए multiprocessing। `ThreadPoolExecutor` modern API है। Shared state के लिए `Lock` जरूरी है।

---

## ➡️ Next Topic
**223. Thread Synchronization** — `Lock`, `RLock`, `Semaphore`, `Event`, `Condition`, `Barrier`. Then **224. Thread Communication** — `Queue.Queue` for producer-consumer patterns between threads.
