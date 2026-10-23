---

# 237. asyncio — Complete Guide
# हिंदी में: asyncio — पूरी Guide

---

## 🔵 Simple Definition (English)
`asyncio` is Python's built-in library for writing concurrent I/O-bound code using `async/await` syntax. It uses a single-threaded event loop that can handle thousands of concurrent operations by switching between them whenever one is waiting for I/O — no threads or processes needed.

## 🔵 सरल परिभाषा (Hindi)
`asyncio` Python की built-in library है जो single thread में हजारों concurrent I/O operations handle करती है। Event loop एक coordinator है जो `async/await` coroutines के बीच switch करता है जब भी कोई I/O wait कर रहा हो — threads या processes की जरूरत नहीं।

---

## 🔴 Problem it Solves
Traditional synchronous code: `request1` takes 1s, `request2` takes 1s → total 2s. With threads: thread overhead, GIL issues. With asyncio: while waiting for `request1`'s response, start `request2` — both complete in ~1s total. Handle 10,000 concurrent connections on a single thread.

## 🔴 यह क्यों बना? (Hindi)
Sync code: request1 (1s) + request2 (1s) = 2s। Threads: overhead, GIL problems। asyncio: request1 wait कर रहा है → request2 start करो → दोनों ~1s में done। Single thread पर 10,000 connections handle करो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Event loop starts (asyncio.run())
Step 2 → Coroutine added to event loop as a Task
Step 3 → Event loop runs coroutine until it hits await
Step 4 → await = "I'm waiting for I/O, please run someone else"
Step 5 → Event loop picks another ready coroutine and runs it
Step 6 → When I/O completes (OS notifies), event loop wakes the waiting coroutine
Step 7 → Waiting coroutine resumes from where it left off (after await)
Step 8 → Repeat — cooperative multitasking, never truly parallel
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Event loop start (asyncio.run())
Step 2 → Coroutine, event loop में Task के रूप में add होती है
Step 3 → Event loop coroutine को await तक run करता है
Step 4 → await = "मैं I/O wait कर रहा हूं, दूसरा चलाओ"
Step 5 → Event loop दूसरी ready coroutine run करता है
Step 6 → I/O complete (OS notify) → event loop sleeping coroutine को wake करता है
Step 7 → Coroutine await के बाद से resume
Step 8 → Cooperative multitasking, कभी truly parallel नहीं
```

---

## 🟡 Real World Example
Zomato API: user searches for restaurants → simultaneously fetch from 5 microservices (menu, ratings, delivery time, offers, availability). Without asyncio: 5 × 200ms = 1000ms. With `asyncio.gather()`: all 5 run concurrently → ~200ms total (the slowest one).

## 🟡 Real Example Hindi mein
Zomato: restaurant search → एक साथ 5 microservices से fetch (menu, ratings, delivery, offers, availability)। asyncio के बिना: 5 × 200ms = 1000ms। `asyncio.gather()` से: सब साथ में → ~200ms (सबसे slow का time)।

---

## 💻 Code Example — Basic
```python
# Basic asyncio: coroutines, await, gather
import asyncio
import time

async def fetch_data(name: str, delay: float) -> str:
    """Simulates async I/O (network call, DB query)."""
    print(f"  {name}: starting (will wait {delay}s)")
    await asyncio.sleep(delay)           # RELEASE control to event loop during wait
    # time.sleep(delay) would BLOCK the whole event loop — never use in async code!
    print(f"  {name}: done!")
    return f"{name}_result"

async def main():
    # Sequential (wrong way — slow):
    print("--- Sequential ---")
    start = time.time()
    r1 = await fetch_data("user_service", 1.0)
    r2 = await fetch_data("order_service", 1.0)
    print(f"Sequential time: {time.time()-start:.2f}s")  # ~2.0s

    # Concurrent with gather (right way!):
    print("\n--- Concurrent ---")
    start = time.time()
    results = await asyncio.gather(
        fetch_data("user_service", 1.0),
        fetch_data("order_service", 1.0),
        fetch_data("payment_service", 1.0),
    )
    print(f"Concurrent time: {time.time()-start:.2f}s")  # ~1.0s ← 3× faster!
    print(f"Results: {results}")

asyncio.run(main())   # ALWAYS use asyncio.run() as the entry point
```

## 💻 Code Example — Advanced
```python
# Production asyncio patterns
import asyncio
import aiohttp
import asyncpg
from typing import Any

# Pattern 1: gather vs create_task (key difference)
async def gather_example():
    """gather: runs coroutines concurrently, waits for ALL to complete."""
    # If one fails, ALL fail (by default — use return_exceptions=True to catch)
    results = await asyncio.gather(
        fetch_user(1),
        fetch_user(2),
        return_exceptions=True          # ← don't raise, return exceptions as values
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"Failed: {r}")
        else:
            print(f"Got user: {r}")

async def create_task_example():
    """create_task: fire-and-forget, doesn't block, can cancel."""
    task = asyncio.create_task(slow_operation())   # starts immediately!
    # Do other work while slow_operation runs:
    await asyncio.sleep(0.1)
    print("Did other work while waiting")
    result = await task                             # wait for it when needed
    return result

# Pattern 2: asyncio.Queue for producer-consumer
async def producer(queue: asyncio.Queue, n: int) -> None:
    for i in range(n):
        await queue.put(f"item_{i}")    # add to queue
        print(f"Produced item_{i}")
        await asyncio.sleep(0.1)        # simulate production time
    await queue.put(None)               # sentinel to signal end

async def consumer(queue: asyncio.Queue) -> None:
    while True:
        item = await queue.get()        # wait for item
        if item is None:
            break
        print(f"Consumed {item}")
        queue.task_done()               # signal task complete
        await asyncio.sleep(0.2)        # simulate processing time

async def producer_consumer():
    queue: asyncio.Queue = asyncio.Queue(maxsize=5)  # bounded queue
    await asyncio.gather(
        producer(queue, 10),
        consumer(queue)
    )

# Pattern 3: Semaphore — limit concurrent requests
async def fetch_with_limit(urls: list[str], limit: int = 5) -> list[str]:
    """Fetch URLs with max 'limit' concurrent requests."""
    semaphore = asyncio.Semaphore(limit)  # max 5 concurrent
    
    async def fetch_one(session: aiohttp.ClientSession, url: str) -> str:
        async with semaphore:             # only 'limit' coroutines here at once
            async with session.get(url) as resp:
                return await resp.text()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Pattern 4: asyncio with PostgreSQL (asyncpg — fastest async PG driver)
async def get_users_async() -> list[dict]:
    conn = await asyncpg.connect(
        host='localhost', database='mydb', user='postgres'
    )
    try:
        rows = await conn.fetch("SELECT id, name, email FROM users LIMIT 100")
        return [dict(row) for row in rows]
    finally:
        await conn.close()

# Pattern 5: timeout with asyncio.wait_for
async def fetch_with_timeout(url: str) -> str:
    try:
        async with asyncio.timeout(5.0):    # Python 3.11+ (or asyncio.wait_for)
            async with aiohttp.ClientSession() as s:
                async with s.get(url) as r:
                    return await r.text()
    except asyncio.TimeoutError:
        return "Request timed out"

async def fetch_user(user_id: int) -> dict:
    """Mock fetch."""
    await asyncio.sleep(0.1)
    return {"id": user_id}

async def slow_operation() -> str:
    await asyncio.sleep(0.5)
    return "done"
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python asyncio
import asyncio
import aiohttp

async def fetch_all(urls: list[str]) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.text() for r in responses]

asyncio.run(fetch_all(["http://api1.com", "http://api2.com"]))

# Key: asyncio.run() starts event loop
# asyncio.gather() = Promise.all()
# await asyncio.sleep() = await setTimeout (but non-blocking)
# aiohttp = node-fetch / axios equivalent
```

```javascript
// JavaScript (Node.js) — async/await is native!
const fetch = require('node-fetch');

async function fetchAll(urls) {
    const responses = await Promise.all(urls.map(url => fetch(url)));
    return Promise.all(responses.map(r => r.text()));
}

fetchAll(['http://api1.com', 'http://api2.com'])
    .then(console.log);

// JavaScript differences:
// No asyncio.run() needed — event loop is always running in Node.js
// Promise.all() = asyncio.gather()
// Async/await is built-in, not a separate library
// No GIL to worry about
// No need to choose between threads/asyncio/multiprocessing
```

---

## 🟠 FastAPI Connection

```python
# FastAPI IS asyncio — uvicorn runs the event loop
from fastapi import FastAPI, HTTPException
import asyncio
import aiohttp
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Lifespan: startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # STARTUP: create DB connection pool
    app.state.db = await asyncpg.create_pool(
        "postgresql://user:pass@localhost/mydb",
        min_size=5,
        max_size=20
    )
    print("DB pool ready")
    yield                              # app runs here
    # SHUTDOWN: close pool
    await app.state.db.close()
    print("DB pool closed")

app = FastAPI(lifespan=lifespan)

@app.get("/dashboard/{user_id}")
async def get_dashboard(user_id: int, request: Request):
    """Fetch user + orders + recommendations concurrently."""
    # All 3 DB queries run concurrently!
    user, orders, recs = await asyncio.gather(
        request.app.state.db.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        ),
        request.app.state.db.fetch(
            "SELECT * FROM orders WHERE user_id = $1 LIMIT 10", user_id
        ),
        get_recommendations(user_id)   # external API call
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"user": dict(user), "orders": [dict(o) for o in orders], "recs": recs}

async def get_recommendations(user_id: int) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://rec-service/recs/{user_id}") as r:
            return await r.json()

# IMPORTANT FastAPI rule:
# async def route: runs in event loop → non-blocking, handles many concurrent requests
# def route (sync): FastAPI runs it in a thread pool → blocking is OK
# Never: async def with time.sleep() or requests.get() → blocks entire event loop!
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using blocking code inside async function
```python
# WRONG: blocks the entire event loop!
async def get_data():
    import time
    import requests
    time.sleep(2)           # ← blocks! No other request can run!
    r = requests.get(url)   # ← blocks! Sync HTTP in async context!
    return r.json()

# CORRECT:
async def get_data():
    await asyncio.sleep(2)        # ← non-blocking
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            return await r.json()  # ← non-blocking
```

❌ Mistake 2: Forgetting `await` on coroutines
```python
# Wrong — creates coroutine but never runs it!
async def main():
    result = fetch_user(1)    # ← NO await! Returns coroutine object, not result
    print(result)             # <coroutine object at 0x...>

# Correct:
async def main():
    result = await fetch_user(1)   # ← await!
    print(result)                  # {'id': 1, 'name': 'Alice'}
```

❌ Mistake 3: Creating tasks but not awaiting them
```python
# Wrong — task may not complete before function returns!
async def bad_example():
    asyncio.create_task(some_work())  # started but not awaited
    return "done"                     # function exits, task may be cancelled!

# Correct:
async def good_example():
    task = asyncio.create_task(some_work())
    result = await task    # wait for it to complete
    return result
```

---

## 🧠 Tricky Interview Question

```python
import asyncio

async def task(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    print(f"{name} done")
    return name

async def main():
    results = await asyncio.gather(
        task("A", 3),
        task("B", 1),
        task("C", 2),
    )
    print(results)

asyncio.run(main())
```
What is the print order?
Answer: **B done → C done → A done → ['A', 'B', 'C']**

- B finishes first (1s delay), then C (2s), then A (3s) — **print order follows completion**
- But `gather` preserves the **input order** in results: `['A', 'B', 'C']` not `['B', 'C', 'A']`
- All three start at the same time — total time is ~3s (the slowest one), not 1+2+3=6s

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `asyncio.gather()` and `asyncio.create_task()`?
A1: `gather()` runs coroutines concurrently and waits for ALL to complete — returns a list of results in input order. `create_task()` schedules a coroutine and returns a Task immediately without waiting — fire-and-forget. You can `await` the task later. `gather()` is for "run these N things and get all results". `create_task()` is for "start this in the background, I'll check later or not at all".

Q2: What is the difference between `async def` and regular `def` in FastAPI?
A2: `async def` runs in the event loop — if it does async I/O (await db, await redis), requests are handled concurrently (one thread). `def` (sync) runs in a thread pool — FastAPI creates a thread for each call — handles blocking I/O but with thread overhead. Key rule: use `async def` with async libraries (asyncpg, aiohttp, aioredis). Use `def` if you must use sync libraries (requests, psycopg2). Never use `time.sleep` or `requests.get` inside `async def`.

Q3: What happens if you use `time.sleep()` inside an async function?
A3: It blocks the entire event loop — all other coroutines freeze until sleep completes. If you have 1000 concurrent requests and one does `time.sleep(1)`, ALL 1000 requests freeze for 1 second. Use `await asyncio.sleep()` instead — it releases control to the event loop so other coroutines can run.

Q4: What is `asyncio.Semaphore` and when do you use it?
A4: A Semaphore limits the number of coroutines executing a section concurrently. `sem = asyncio.Semaphore(10)` → max 10 coroutines inside `async with sem` at once. Use for: rate limiting external API calls (don't hammer the API with 1000 concurrent requests), limiting DB connections, controlling memory usage for parallel downloads.

Q5: How do you run blocking/sync code from async code without blocking the event loop?
A5: Use `loop.run_in_executor()`: `result = await loop.run_in_executor(None, sync_function, arg)`. `None` uses the default ThreadPoolExecutor. For CPU-bound: use `ProcessPoolExecutor`. This runs the sync function in a thread/process and the event loop remains responsive. FastAPI's `def` routes do this automatically.

---

## 🔷 When to Use + When Not to Use

✅ Use asyncio when:
- I/O-bound concurrency: HTTP requests, DB queries, file I/O, Redis
- Web servers (FastAPI, aiohttp — built on asyncio)
- High concurrency needed (hundreds/thousands of simultaneous connections)
- Building microservice clients that call multiple services in parallel

❌ Avoid asyncio when:
- CPU-bound computation (use multiprocessing)
- Simple scripts that don't need concurrency (overkill)
- Using sync-only libraries that can't be easily replaced with async equivalents
- Team is not familiar with async patterns (steep learning curve)

---

## 📊 Visual Diagram
```
SYNC (Sequential):         ASYNC (asyncio):
                           
t=0 ─→ Request A starts    t=0 ─→ Request A starts
t=1 ─→ A waiting for DB         ─→ Request B starts  ← event loop switches!
t=2 ─→ A waiting for DB         ─→ A DB response arrives
t=3 ─→ A done              t=1 ─→ A done, B DB response arrives
t=3 ─→ Request B starts         ─→ B done
t=6 ─→ B done              
                           
Total: 6 seconds           Total: ~1 second!

Event Loop:
         ┌──────────────────────────────────┐
         │         Event Loop               │
await ──→│ "I'm waiting, who's ready?" ─→  │
         │    Task B ready → run B          │
         │    Task C ready → run C          │
         │    Task A ready → resume A       │
         └──────────────────────────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Single thread that schedules coroutines | Coroutines को schedule करने वाला single thread |
| Coroutine | Function defined with `async def` | `async def` से बनी function |
| await | Yield control, wait for result | Control दो, result का wait करो |
| Task | Coroutine scheduled in event loop | Event loop में scheduled coroutine |
| asyncio.gather | Run multiple coroutines concurrently | कई coroutines साथ में run करो |
| Semaphore | Limit concurrent access to a resource | Concurrent access limit करो |
| aiohttp | Async HTTP client library | Async HTTP library |

---

## ⚡ 3-Line Summary
English: asyncio is a single-threaded event loop that switches between coroutines at `await` points — providing I/O concurrency without threads. `asyncio.gather()` runs multiple coroutines concurrently. Never use blocking calls (time.sleep, requests.get) inside async functions — they freeze the entire event loop.
Hindi: asyncio single-thread event loop है जो `await` पर coroutines switch करता है। `asyncio.gather()` = कई coroutines साथ में। Async function में blocking calls मत करो — पूरा event loop freeze हो जाता है।

---

## ➡️ Next Topic
**238. Event Loop in Python** — how uvloop makes asyncio 2× faster, event loop internals, `asyncio.get_event_loop()` vs `asyncio.run()`, and debugging async code.
