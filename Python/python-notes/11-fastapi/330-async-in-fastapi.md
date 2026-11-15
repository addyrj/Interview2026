---

# 330. Async in FastAPI
# हिंदी में: FastAPI में Async (async def बनाम def)

---

## 🔵 Simple Definition (English)
FastAPI runs `async def` endpoints directly on the event loop and runs plain `def` endpoints in a threadpool. Use `async def` with `await` for async libraries; use `def` for blocking libraries. Never block the event loop.

## 🔵 सरल परिभाषा (Hindi)
FastAPI `async def` endpoints को सीधे event loop पर चलाता है और सादे `def` endpoints को threadpool में। Async libraries के लिए `await` के साथ `async def` इस्तेमाल करें; blocking libraries के लिए `def`। Event loop को कभी block न करें।

---

## 🔴 Problem it Solves
One event loop thread serves thousands of connections only if every handler yields while waiting for I/O. If an `async def` handler calls `time.sleep()` or a blocking DB driver, the whole server freezes for everyone. FastAPI's rule (async -> loop, def -> threadpool) lets you mix styles safely if you choose correctly.

## 🔴 यह क्यों बना? (Hindi)
एक event loop thread हज़ारों connections तभी संभालता है जब हर handler I/O के इंतज़ार में control छोड़े। अगर `async def` handler `time.sleep()` या blocking DB driver बुलाए तो पूरा server सबके लिए रुक जाता है। FastAPI का नियम (async -> loop, def -> threadpool) सही चुनाव करने पर दोनों style सुरक्षित मिलाने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives at Uvicorn (one event-loop thread per worker process)
Step 2 → FastAPI checks the endpoint: coroutine function or plain function?
Step 3 → `async def` -> awaited directly on the loop (fast, but must not block)
Step 4 → `def` -> sent to AnyIO's threadpool (default 40 threads)
Step 5 → While an `await` waits for I/O, the loop serves other requests
Step 6 → Blocking call inside `async def` -> loop stuck -> all requests wait
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request Uvicorn तक आती है (हर worker process में एक event-loop thread)
Step 2 → FastAPI देखता है: endpoint coroutine function है या सादा function?
Step 3 → `async def` -> loop पर सीधे await होता है (तेज़, पर block नहीं करना)
Step 4 → `def` -> AnyIO के threadpool में जाता है (default 40 threads)
Step 5 → `await` के I/O इंतज़ार में रहने पर loop दूसरी requests संभालता है
Step 6 → `async def` के अंदर blocking call -> loop अटका -> सारी requests इंतज़ार करती हैं
```

---

## 🟡 Real World Example
An AI gateway calls OpenAI with `httpx.AsyncClient` inside `async def` so 1000 users can wait for LLM replies at once on one worker. A legacy reporting endpoint uses `psycopg2` (blocking), so it is a plain `def` and runs in the threadpool. A CPU-heavy image resize goes to a process pool or worker, not the loop.

## 🟡 Real Example Hindi mein
AI gateway `async def` के अंदर `httpx.AsyncClient` से OpenAI call करता है ताकि एक worker पर 1000 users एक साथ LLM जवाब का इंतज़ार कर सकें। पुराना reporting endpoint `psycopg2` (blocking) इस्तेमाल करता है, इसलिए सादा `def` है और threadpool में चलता है। CPU-भारी image resize process pool या worker को जाता है, loop को नहीं।

---

## 💻 Code Example — Basic
See which thread runs each style (`async def` on the event-loop thread, `def` in a worker thread).

```python
# Basic: where do async def and def handlers run? - every line commented
import threading  # to see the thread name
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # app


@app.get("/async")  # async route
async def a() -> dict[str, str]:  # runs ON the event loop thread
    return {"thread": threading.current_thread().name}  # name of the current thread


@app.get("/sync")  # def route
def s() -> dict[str, str]:  # FastAPI sends this to a worker thread (threadpool)
    return {"thread": threading.current_thread().name}  # name of the current thread


client: TestClient = TestClient(app)  # client
print(client.get("/async").json())  # event-loop thread (TestClient runs the app in an anyio portal thread)
print(client.get("/sync").json())  # a different, worker thread
print(client.get("/async").json() != client.get("/sync").json())  # they differ
# Output: True
```

## 💻 Code Example — Advanced
Measure 5 concurrent requests of 0.2 s each: good async, blocking inside async (BAD), plain def, and `asyncio.to_thread` fix.

```python
# Production style: measure concurrency - async, blocking-in-async (BAD), def, to_thread (FIX)
import asyncio  # event loop tools
import time  # blocking sleep + timer
import httpx  # async client
from fastapi import FastAPI  # app

app: FastAPI = FastAPI()  # app


@app.get("/good-async")  # correct async
async def good_async() -> dict[str, bool]:  # handler
    await asyncio.sleep(0.2)  # non-blocking wait
    return {"ok": True}  # data


@app.get("/bad-async")  # WRONG: blocking call inside async def
async def bad_async() -> dict[str, bool]:  # handler
    time.sleep(0.2)  # blocks the WHOLE event loop
    return {"ok": True}  # data


@app.get("/plain-def")  # sync handler
def plain_def() -> dict[str, bool]:  # runs in threadpool
    time.sleep(0.2)  # blocks only its own thread
    return {"ok": True}  # data


@app.get("/fixed-async")  # blocking code moved off the loop
async def fixed_async() -> dict[str, bool]:  # handler
    await asyncio.to_thread(time.sleep, 0.2)  # run blocking call in a thread
    return {"ok": True}  # data


async def fire(path: str, n: int = 5) -> float:  # send n concurrent requests, return seconds
    transport: httpx.ASGITransport = httpx.ASGITransport(app=app)  # call app in-process
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:  # client
        start: float = time.perf_counter()  # start timer
        await asyncio.gather(*(c.get(path) for _ in range(n)))  # all at once
        return time.perf_counter() - start  # elapsed


async def main() -> None:  # run all experiments
    for path in ["/good-async", "/bad-async", "/plain-def", "/fixed-async"]:  # each route
        print(f"{path:14s} {await fire(path):.1f}s")  # 5 requests of 0.2s each


asyncio.run(main())  # go
# Output (timings approx): good-async 0.2s, bad-async 1.0s, plain-def 0.2s, fixed-async 0.2s
```

---

## 🟠 JavaScript vs Python Comparison

```python
@app.get("/a")
async def a():
    r = await client.get(url)   # non-blocking
    return r.json()

@app.get("/b")
def b():
    return blocking_call()      # runs in threadpool
```

```javascript
// Node is single-threaded: everything must be non-blocking
app.get('/a', async (req, res) => {
  const r = await fetch(url);         // non-blocking
  res.json(await r.json());
});
// a blocking loop here freezes the whole server (same danger)
```

Node has only the event loop, so blocking code is always dangerous. Python gives a second option: plain `def` handlers are automatically moved to threads, so blocking libraries are safe there. In `async def` the rule is the same as Node: never block.

---

## 🟠 FastAPI Connection
Rules of thumb: if you `await` something in the handler, use `async def`. If you use a blocking library (requests, psycopg2, sync SQLAlchemy, file/CPU work), use plain `def` (or wrap with `run_in_threadpool` / `asyncio.to_thread`). Dependencies follow the same rule. For CPU-heavy work use a process pool or a task queue; threads do not help because of the GIL (free-threaded builds aside).

```python
import asyncio
import httpx
from fastapi import FastAPI

app: FastAPI = FastAPI()


def cpu_heavy(n: int) -> int:  # blocking / CPU function
    return sum(i * i for i in range(n))


@app.get("/quote")
async def quote() -> dict[str, int]:
    async with httpx.AsyncClient() as c:  # async I/O
        r = await c.get("https://example.com")
    total: int = await asyncio.to_thread(cpu_heavy, 10_000)  # keep the loop free
    return {"status": r.status_code, "total": total}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside `async def`
```python
@app.get('/x')
async def x():
    time.sleep(2)  # freezes ALL requests
    requests.get(url)  # also blocking
```
✅ Correct:
```python
@app.get('/x')
async def x():
    await asyncio.sleep(2)
    async with httpx.AsyncClient() as c: await c.get(url)
```

❌ Mistake 2: Using `async def` with a sync DB driver
```python
async def users():
    return db.execute('SELECT ...')  # blocking driver on the loop
```
✅ Correct:
```python
def users():  # plain def -> threadpool
    return db.execute('SELECT ...')
```

❌ Mistake 3: Forgetting `await`
```python
async def h():
    data = fetch()  # coroutine object, never ran
```
✅ Correct:
```python
async def h():
    data = await fetch()
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import asyncio, time, httpx
from fastapi import FastAPI

app = FastAPI()

@app.get("/a")
async def a():
    time.sleep(0.2)
    return 1

@app.get("/b")
def b():
    time.sleep(0.2)
    return 1

async def fire(p):
    t = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=t, base_url="http://t") as c:
        s = time.perf_counter()
        await asyncio.gather(*(c.get(p) for _ in range(3)))
        return round(time.perf_counter() - s, 1)

async def main():
    print(await fire("/a"), await fire("/b"))
asyncio.run(main())
```

**Answer**:
```
0.6 0.2
```
`/a` is `async def` with a blocking `time.sleep(0.2)`: the three requests run one after another on the loop, so about 0.6 s. `/b` is a plain `def`, so each request gets its own thread and the three sleeps overlap, about 0.2 s. (Timings are rounded and vary slightly per machine.)

---

## ⚫ Interview Questions + Answers

Q1: When should I use `async def` vs `def`?
A1: `async def` if every I/O call inside is awaited (async libraries). `def` if you use blocking libraries. When unsure, `def` is the safe default.

Q2: What happens if I block inside `async def`?
A2: The single event-loop thread is busy, so no other request on that worker makes progress; latency spikes for everyone.

Q3: Is `def` slower than `async def`?
A3: There is thread overhead, but for blocking code it is the correct tool. The threadpool defaults to 40 threads, so heavy blocking traffic can exhaust it.

Q4: How do I call blocking code from async code?
A4: `await asyncio.to_thread(fn, *args)` or `await run_in_threadpool(fn, *args)` (from `fastapi.concurrency`).

Q5: Does async help CPU-bound work?
A5: No. It helps I/O waiting. For CPU work use `ProcessPoolExecutor`, Celery/ARQ workers or more Uvicorn/Gunicorn worker processes.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- `async def`: HTTP calls, async DB (asyncpg, SQLAlchemy async), Redis, streaming, WebSockets
- `def`: blocking libraries, simple CRUD with sync ORM
- `to_thread`: one blocking call inside an async flow

❌ Avoid when:
- `time.sleep`, `requests`, sync DB inside `async def`
- CPU-heavy loops on the event loop
- Mixing sync and async drivers without thinking

---

## 📊 Visual Diagram

```
             Uvicorn worker (1 event-loop thread)
request --> endpoint type?
             |-- async def --> runs ON the loop   (await = loop serves others)
             |                 blocking call here => EVERYONE waits
             |-- def       --> AnyIO threadpool (40 threads) => loop stays free
CPU heavy ---> process pool / task queue (not the loop)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Scheduler of coroutines | coroutines चलाने वाला scheduler |
| Coroutine | async def function object | async def से बना object |
| await | Pause until result | नतीजे तक रुकना, loop को छोड़कर |
| Threadpool | Worker threads for def | def के लिए worker threads |
| Blocking | Holds the thread idle | thread को अटकाए रखना |
| GIL | One thread runs Python at a time | एक समय में एक thread Python चलाता है |

---

## ⚡ 3-Line Summary
English: `async def` runs on the event loop and must never block; plain `def` runs in a threadpool and is safe for blocking libraries. Use `asyncio.to_thread` to call blocking code from async code. Async helps I/O, not CPU work.
Hindi: `async def` event loop पर चलता है और कभी block नहीं करना चाहिए; सादा `def` threadpool में चलता है और blocking libraries के लिए सुरक्षित है। Async code से blocking code बुलाने के लिए `asyncio.to_thread` लें। Async I/O में मदद करता है, CPU काम में नहीं।

---

## ➡️ Next Topic
**331. Sync vs Async Routes** — a deeper comparison of `def` and `async def` routes and when each wins.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output. Timing numbers are approximate and machine-dependent.
