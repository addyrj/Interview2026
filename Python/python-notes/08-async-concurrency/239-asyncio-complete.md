---

# 239. asyncio — Complete Guide
# हिंदी में: asyncio — पूरी Guide

---

## 🔵 Simple Definition (English)
`asyncio` is Python's built-in async I/O library — the foundation of FastAPI, aiohttp, asyncpg, and all modern async Python code. Key concept: an **event loop** runs coroutines (async functions). While one coroutine waits for I/O (DB query, HTTP call), the event loop runs other coroutines. Result: one thread handles thousands of concurrent connections. No GIL issue — asyncio is single-threaded.

## 🔵 सरल परिभाषा (Hindi)
`asyncio` Python का built-in async I/O library है — FastAPI, aiohttp, asyncpg का foundation। Key: **event loop** coroutines (async functions) run करता है। एक coroutine I/O wait करते समय loop दूसरे coroutines run करता है। Single thread में thousands of concurrent connections। GIL issue नहीं — asyncio single-threaded है।

---

## 💻 Code Example — Basic
```python
import asyncio

# ─── Basic coroutine ──────────────────────────────────────────────
async def greet(name: str) -> str:
    await asyncio.sleep(1)   # simulates I/O wait (DB, HTTP, etc.)
    return f"Hello, {name}!"

# Run a coroutine:
result = asyncio.run(greet("Priya"))   # Python 3.7+
print(result)   # "Hello, Priya!"

# ─── await — pause until result is ready ─────────────────────────
async def fetch_data(user_id: int) -> dict:
    # These all run sequentially (each waits for previous):
    user = await db.get_user(user_id)        # wait for DB
    orders = await db.get_orders(user_id)   # wait for DB
    return {"user": user, "orders": orders}

# ─── Concurrent execution with asyncio.gather ─────────────────────
async def fetch_all_data(user_id: int) -> dict:
    # These run CONCURRENTLY — not sequentially!
    user, orders, preferences = await asyncio.gather(
        db.get_user(user_id),
        db.get_orders(user_id),
        db.get_preferences(user_id),
    )
    # All three DB queries run at the same time!
    # Total time = slowest query, not sum of all
    return {"user": user, "orders": orders, "prefs": preferences}

# ─── async/await with context managers ────────────────────────────
async def get_from_redis(key: str) -> str | None:
    async with redis.client() as conn:   # async context manager
        return await conn.get(key)

# ─── async generators ────────────────────────────────────────────
async def stream_events():
    for i in range(10):
        await asyncio.sleep(0.1)   # simulate delay
        yield f"event_{i}"

async def consume_events():
    async for event in stream_events():   # async for
        print(event)
```

## 💻 Code Example — Advanced
```python
import asyncio
from typing import Any

# ─── asyncio.gather vs asyncio.create_task ────────────────────────
# gather: waits for all to complete, returns all results:
results = await asyncio.gather(task1(), task2(), task3())
# [(result1), (result2), (result3)]

# gather with return_exceptions=True — don't cancel all on first error:
results = await asyncio.gather(
    task1(),
    task2(),
    failing_task(),
    return_exceptions=True,    # errors returned as values, not raised
)
# [result1, result2, Exception("failed")]

# create_task: start immediately, get result later:
task = asyncio.create_task(background_work())
# ... do other stuff ...
result = await task   # wait for it here

# ─── asyncio.wait_for — timeout ───────────────────────────────────
async def fetch_with_timeout(url: str, timeout: float = 5.0):
    try:
        async with aiohttp.ClientSession() as session:
            return await asyncio.wait_for(
                session.get(url),
                timeout=timeout
            )
    except asyncio.TimeoutError:
        raise HTTPException(504, "Upstream timeout")

# ─── Semaphore — limit concurrency ───────────────────────────────
async def process_items(items: list, max_concurrent: int = 10):
    """Process many items but limit to max_concurrent at a time."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_one(item):
        async with semaphore:   # blocks if max_concurrent already running
            return await do_work(item)
    
    return await asyncio.gather(*[process_one(item) for item in items])

# Real use: embed 1000 documents, max 10 OpenAI calls at once:
async def embed_all(texts: list[str]) -> list[list[float]]:
    semaphore = asyncio.Semaphore(10)
    
    async def embed_one(text: str) -> list[float]:
        async with semaphore:
            response = await openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
    
    return await asyncio.gather(*[embed_one(t) for t in texts])

# ─── asyncio.Queue — async producer-consumer ─────────────────────
async def producer(queue: asyncio.Queue, items: list):
    for item in items:
        await queue.put(item)
    await queue.put(None)   # sentinel: signal done

async def consumer(queue: asyncio.Queue, results: list):
    while True:
        item = await queue.get()
        if item is None:
            break
        result = await process(item)
        results.append(result)
        queue.task_done()

async def pipeline(items: list) -> list:
    queue = asyncio.Queue(maxsize=50)   # bounded queue
    results = []
    
    # Run producer and consumer concurrently:
    await asyncio.gather(
        producer(queue, items),
        consumer(queue, results),
    )
    return results

# ─── Running sync code in thread pool ─────────────────────────────
import concurrent.futures

def cpu_intensive_work(data: bytes) -> bytes:
    """CPU-bound: don't run directly in async context — blocks event loop!"""
    # image processing, encryption, compression, etc.
    return process(data)

async def handle_upload(data: bytes) -> bytes:
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, cpu_intensive_work, data)
    return result

# FastAPI equivalent:
from fastapi.concurrency import run_in_threadpool

@app.post("/upload")
async def upload(file: UploadFile):
    content = await file.read()
    # Run blocking/CPU-intensive work in thread pool:
    processed = await run_in_threadpool(cpu_intensive_work, content)
    return {"size": len(processed)}

# ─── Async patterns in FastAPI ────────────────────────────────────
@app.get("/dashboard")
async def get_dashboard(user_id: int, db=Depends(get_db)):
    # Fetch multiple data sources concurrently:
    tariffs, stats, recent_searches = await asyncio.gather(
        db.get_user_tariffs(user_id),
        db.get_user_stats(user_id),
        redis.get_recent_searches(user_id),
    )
    return {
        "tariffs": tariffs,
        "stats": stats,
        "recent_searches": recent_searches,
    }
    # Without gather: 3 sequential queries (3x slower)
    # With gather: 3 concurrent queries (1x — limited by slowest)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python async/await:
async def fetch_users():
    # Concurrent:
    users, orders = await asyncio.gather(
        db.get_users(),
        db.get_orders()
    )
    return users, orders

# Event loop:
asyncio.run(main())
```

```javascript
// JavaScript async/await (very similar!):
async function fetchUsers() {
    // Concurrent:
    const [users, orders] = await Promise.all([
        db.getUsers(),
        db.getOrders()
    ]);
    return { users, orders };
}

// Node.js event loop runs automatically
```

Key similarities: both use `async/await`. `asyncio.gather()` = `Promise.all()`. `asyncio.create_task()` ≈ `Promise` (fire-and-forget).

Key difference: Python needs `asyncio.run()` to start the event loop. Node.js event loop always running. Python has `asyncio.Semaphore` for rate limiting — JS needs manual implementation.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling sync code in async function without thread pool
```python
# Wrong — blocks event loop during requests.get():
@app.get("/proxy")
async def proxy(url: str):
    response = requests.get(url)   # BLOCKING! Freezes all requests!
    return response.json()

# Correct — use aiohttp (async HTTP):
import aiohttp

@app.get("/proxy")
async def proxy(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

❌ Mistake 2: Not using gather for independent operations
```python
# Wrong — sequential (3x slower):
user = await db.get_user(id)
orders = await db.get_orders(id)
prefs = await db.get_prefs(id)

# Correct — concurrent:
user, orders, prefs = await asyncio.gather(
    db.get_user(id),
    db.get_orders(id),
    db.get_prefs(id),
)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the difference between `await asyncio.gather()` and sequential `await` calls?

**Answer**: Sequential awaits run one after another — total time = sum of all. `asyncio.gather()` starts all coroutines **concurrently** — total time = max (slowest one). For 3 DB queries each taking 100ms: sequential = 300ms, gather = ~100ms. However, they share the **same thread** (cooperative multitasking) — `gather` only helps for I/O-bound operations where coroutines spend time waiting. For CPU-bound work, use `run_in_executor()` with `ProcessPoolExecutor` instead.

---

## ⚫ Interview Questions + Answers

Q1: What is the event loop and how does it work?
A1: The event loop is a single thread that manages and schedules coroutines. It maintains a queue of coroutines and runs them one at a time. When a coroutine hits `await`, it registers an I/O callback and yields control back to the loop. The loop runs other coroutines. When the I/O completes, the loop resumes the waiting coroutine. This is cooperative multitasking — coroutines must explicitly yield (via `await`) to let others run. A blocking operation (no `await`) holds the loop and freezes all other coroutines.

Q2: When should you use asyncio vs threading vs multiprocessing?
A2: **asyncio**: I/O-bound, many concurrent connections, shared memory needed. Best for: web servers, DB queries, API calls, file I/O. **Threading**: I/O-bound but can't convert to async, or mixing sync/async code. The GIL is released during I/O — threads work well for downloads, file operations. FastAPI auto-runs sync routes in thread pool. **Multiprocessing**: CPU-bound work needing true parallelism (image processing, ML training, heavy computation). Each process has own GIL, own memory space — no sharing. Rule: asyncio first, threading for legacy sync code, multiprocessing for CPU work.

Q3: What does `asyncio.create_task()` do differently from `await`?
A3: `await coroutine()` pauses current coroutine until the awaited one finishes — sequential. `task = asyncio.create_task(coroutine())` **starts the coroutine immediately** as a background task without waiting. Later: `result = await task` waits for it. Use `create_task` when: you want to start a task and do other work before getting the result; you want fire-and-forget (never await); you want to cancel tasks (`task.cancel()`). `gather` uses `create_task` internally — it's the building block for concurrent execution.

Q4: How do you handle errors in asyncio.gather()?
A4: Default: if any coroutine raises, `gather` cancels remaining and raises the first exception. `return_exceptions=True`: exceptions are returned as values in the results list instead of raised — you check each result. Pattern: `results = await gather(*tasks, return_exceptions=True); errors = [r for r in results if isinstance(r, Exception)]`. For critical operations: let default behavior cancel all on failure. For independent operations (embed 1000 documents): use `return_exceptions=True` — one failure shouldn't cancel all 999 others.

Q5: What is an async context manager (`async with`) and when do you need it?
A5: `async with` calls `__aenter__` and `__aexit__` which are coroutines (can `await`). Needed when: opening/closing async resources (DB session, HTTP session, Redis connection). `async with aiohttp.ClientSession() as session:` creates and properly closes the HTTP connection pool. `async with asyncpg.connect() as conn:` manages DB connection lifecycle. Use `@asynccontextmanager` decorator to create from a generator: `async def managed_resource(): r = await open_resource(); yield r; await r.close()`. FastAPI's `lifespan` is built on `@asynccontextmanager`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Async coroutine scheduler | Async coroutines का scheduler |
| Coroutine | async def function | async def function |
| gather | Run coroutines concurrently | Concurrently run करो |
| create_task | Start task in background | Background में task start |
| Semaphore | Limit concurrent coroutines | Concurrent coroutines limit |
| await | Wait for I/O to complete | I/O complete होने का wait |
| run_in_executor | Run blocking code in thread | Blocking code thread में चलाओ |

---

## ⚡ 3-Line Summary
English: `asyncio` lets one thread handle thousands of concurrent I/O operations — while one coroutine awaits a DB response, others run. Use `asyncio.gather()` to run independent operations concurrently (not sequentially) — this is the #1 FastAPI performance optimization. Never block the event loop with `time.sleep()`, `requests.get()`, or CPU-intensive code — use `await`, `aiohttp`, and `run_in_threadpool` instead.
Hindi: `asyncio` = single thread में thousands concurrent I/O। `asyncio.gather()` से independent operations concurrently चलाओ — FastAPI का #1 optimization। Event loop block मत करो — `await`, `aiohttp`, `run_in_threadpool` use करो।

---

## ➡️ Next Topic
**231. Multiprocessing** — CPU parallelism, ProcessPool, shared memory. **248. asyncpg** — async PostgreSQL driver. **237. asyncio deep dive** — queues, events, locks.
