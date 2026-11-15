---

# 331. Sync vs Async Routes
# हिंदी में: Sync बनाम Async Routes (def बनाम async def)

---

## 🔵 Simple Definition (English)
In FastAPI you can write a route as `def` (sync) or `async def` (async). A `def` route runs in a worker thread pool, so blocking code is safe there. An `async def` route runs directly on the event loop, so it must only `await` non-blocking calls.

## 🔵 सरल परिभाषा (Hindi)
FastAPI में route `def` (sync) या `async def` (async) दोनों तरह से लिख सकते हैं। `def` route worker thread pool में चलता है, इसलिए वहाँ blocking code सुरक्षित है। `async def` route सीधे event loop पर चलता है, इसलिए वहाँ सिर्फ non-blocking calls को `await` करना चाहिए।

---

## 🔴 Problem it Solves
A web server handles many users at once. If one request blocks (for example `time.sleep` or a slow sync DB driver) on the single event-loop thread, every other request waits. FastAPI solves this by giving you two modes: `def` goes to a thread pool (the loop stays free), and `async def` gives you cheap concurrency for I/O with `await`. Choosing the wrong mode is one of the most common FastAPI performance bugs.

## 🔴 यह क्यों बना? (Hindi)
Web server एक साथ कई users संभालता है। अगर एक request single event-loop thread पर block कर दे (जैसे `time.sleep` या धीमा sync DB driver), तो बाकी सभी requests इंतजार करती हैं। FastAPI दो mode देता है: `def` thread pool में जाता है (loop खाली रहता है), और `async def` में `await` से I/O पर सस्ती concurrency मिलती है। गलत mode चुनना FastAPI के सबसे आम performance bugs में से एक है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → uvicorn starts ONE event loop (one thread) per worker process
Step 2 → Request arrives, FastAPI finds the matching route function
Step 3 → If route is "async def": call it directly ON the event loop
Step 4 → If route is "def": send it to a thread pool (AnyIO, 40 threads by default)
Step 5 → async route hits "await": loop is free to serve other requests
Step 6 → async route hits a BLOCKING call (time.sleep, requests.get): loop is FROZEN
Step 7 → def route blocks only its own thread; the loop keeps serving others
Step 8 → The response is sent when the function returns
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → uvicorn हर worker process में एक event loop (एक thread) चलाता है
Step 2 → Request आती है, FastAPI सही route function ढूँढता है
Step 3 → अगर route "async def" है: उसे सीधे event loop पर call करता है
Step 4 → अगर route "def" है: उसे thread pool में भेजता है (AnyIO, default 40 threads)
Step 5 → async route "await" पर पहुँचे: loop बाकी requests serve करने को खाली
Step 6 → async route में BLOCKING call (time.sleep, requests.get): loop जम जाता है
Step 7 → def route सिर्फ अपना thread block करता है; loop बाकी को serve करता रहता है
Step 8 → Function return होने पर response भेजा जाता है
```

---

## 🟡 Real World Example
A Razorpay-style payment API has `POST /pay` that calls a bank over HTTP with `httpx.AsyncClient` (use `async def`), and `GET /report` that uses a legacy sync library (`psycopg2`, `boto3`, `reportlab`) to build a PDF (use plain `def`). Developers who put `requests.get()` inside `async def` see the whole API freeze under load, because one slow bank call blocks every other user.

## 🟡 Real Example Hindi mein
Razorpay जैसी payment API में `POST /pay` bank को `httpx.AsyncClient` से call करता है (`async def` उपयोग करें), और `GET /report` पुरानी sync library (`psycopg2`, `boto3`, `reportlab`) से PDF बनाता है (साधारण `def` उपयोग करें)। जो developers `async def` के अंदर `requests.get()` डालते हैं, उनकी पूरी API load में जम जाती है, क्योंकि एक धीमा bank call बाकी सभी users को रोक देता है।

---

## 💻 Code Example — Basic
```python
# Basic: see WHICH thread each kind of route runs on
import asyncio                                   # for asyncio.sleep (non-blocking sleep)
import threading                                 # to read the current thread name
import time                                      # for time.sleep (blocking sleep)
from fastapi import FastAPI                      # FastAPI class
from fastapi.testclient import TestClient        # run the app without starting a server

app: FastAPI = FastAPI()                         # create the app


@app.get("/sync")                                # a normal function route
def sync_route() -> dict[str, str]:              # def => runs in the thread pool
    name: str = threading.current_thread().name  # name of the thread running this code
    return {"thread": name, "kind": "sync"}      # return the thread name


@app.get("/async")                               # a coroutine route
async def async_route() -> dict[str, str]:       # async def => runs on the event loop
    await asyncio.sleep(0.01)                    # non-blocking wait, loop stays free
    name: str = threading.current_thread().name  # thread running the event loop
    return {"thread": name, "kind": "async"}     # return the thread name


@app.get("/bad-async")                           # a BAD example on purpose
async def bad_async() -> dict[str, str]:         # async def with blocking code inside
    time.sleep(0.2)                              # blocks the whole event loop for 0.2 s!
    return {"ok": "blocked loop"}                # works, but nobody else is served meanwhile


with TestClient(app) as client:                  # start the app in test mode
    print(client.get("/sync").json())            # call the sync route
    print(client.get("/async").json())           # call the async route
    print(client.get("/bad-async").json())       # call the bad route

# Output (verified on Python 3.13, FastAPI 0.162; the async thread name varies per run):
# {'thread': 'AnyIO worker thread', 'kind': 'sync'}
# {'thread': 'asyncio-portal-103602660', 'kind': 'async'}
# {'ok': 'blocked loop'}
```

## 💻 Code Example — Advanced
```python
# Production style: 3 ways to run blocking code, measured with 5 concurrent requests
import asyncio                                   # for gather
import time                                      # for the blocking call and timing
import httpx                                     # async HTTP client (also used as a test client)
from fastapi import FastAPI                      # FastAPI class
from starlette.concurrency import run_in_threadpool   # run a sync function in the thread pool

app: FastAPI = FastAPI()                         # create the app


def blocking_io() -> str:                        # pretend: legacy sync driver / PDF / boto3
    time.sleep(0.3)                              # blocking for 0.3 s
    return "done"                                # result


@app.get("/good")                                # async route, correct way
async def good() -> dict[str, str]:              # async def + offload
    return {"r": await run_in_threadpool(blocking_io)}   # blocking work goes to a thread


@app.get("/sync")                                # plain def route, also correct
def sync_ok() -> dict[str, str]:                 # FastAPI offloads it automatically
    return {"r": blocking_io()}                  # blocks only its own worker thread


@app.get("/bad")                                 # async route, WRONG way
async def bad() -> dict[str, str]:               # async def but blocking call inside
    return {"r": blocking_io()}                  # freezes the event loop


async def hit(client: httpx.AsyncClient, path: str) -> None:   # one request helper
    await client.get(path)                       # send the request and wait


async def main() -> None:                        # benchmark driver
    transport = httpx.ASGITransport(app=app)     # call the ASGI app in-process, no network
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
        for path in ("/good", "/sync", "/bad"):  # test each route
            t0: float = time.perf_counter()      # start timer
            await asyncio.gather(*(hit(client, path) for _ in range(5)))   # 5 at the same time
            elapsed: float = time.perf_counter() - t0   # total time
            print(path, "5 concurrent requests ->", round(elapsed, 1), "s")   # report


asyncio.run(main())                              # run the benchmark

# Output (verified; timings are approximate and vary by machine):
# /good 5 concurrent requests -> 0.3 s
# /sync 5 concurrent requests -> 0.3 s
# /bad 5 concurrent requests -> 1.5 s
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (FastAPI) | JavaScript (Express/Node) |
|---------|------------------|---------------------------|
| Async handler | `async def` + `await` | `async (req, res) =>` + `await` |
| Sync handler | `def` (auto thread pool) | plain function — runs on the ONE main thread |
| Blocking code in handler | safe in `def`, dangerous in `async def` | always dangerous (freezes everything) |
| Offload CPU/blocking work | `run_in_threadpool`, processes | `worker_threads`, child_process |
| Threads for sync handlers | yes, ~40 by default | no |

```python
# Python way — blocking work is safe inside a plain def
import time                                  # blocking sleep
from fastapi import FastAPI                  # framework

app = FastAPI()                              # create app

@app.get("/report")                          # route
def report() -> dict[str, str]:              # def => thread pool, loop stays free
    time.sleep(1)                            # blocks only this worker thread
    return {"ok": "yes"}                     # response
```
```javascript
// JavaScript way — there is no thread pool for handlers
app.get("/report", (req, res) => {           // runs on the single event-loop thread
  const end = Date.now() + 1000;             // busy-wait 1 second
  while (Date.now() < end) {}                // blocks EVERY other request in Node
  res.json({ ok: "yes" });                   // response
});
```

Key difference: in Node a blocking handler always freezes the server. In FastAPI a plain `def` handler is automatically protected by a thread pool, but an `async def` handler is exactly like Node: block it and everybody waits.

---

## 🟠 FastAPI Connection
Dependencies follow the same rule: `def` dependencies run in the thread pool, `async def` dependencies run on the loop. Background tasks, `Depends(get_db)`, and middleware all obey this. Rule of thumb for the interview: use `async def` only when every call inside is awaitable (httpx, asyncpg, async SQLAlchemy, aioredis); otherwise use `def`.

```python
# FastAPI example — mixing both correctly in one app
import httpx                                          # async HTTP client
from fastapi import FastAPI                           # FastAPI class

app: FastAPI = FastAPI()                              # create app


@app.get("/rate")                                     # I/O bound + async library
async def rate() -> dict[str, float]:                 # async def because we await httpx
    async with httpx.AsyncClient() as client:         # non-blocking HTTP client
        r = await client.get("https://example.com")   # loop is free while waiting
    return {"status": float(r.status_code)}           # return status


@app.get("/pdf")                                      # blocking legacy library
def pdf() -> dict[str, str]:                          # plain def => thread pool
    return {"file": "report.pdf"}                     # pretend we build a PDF here
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside `async def`
✅ Correct: use `def`, or `await run_in_threadpool(...)`, or an async library

```python
import time, requests                       # blocking libraries
# Wrong
async def a() -> None:
    time.sleep(5)                           # freezes the event loop
    requests.get("https://example.com")     # also blocks the loop
# Right
import asyncio, httpx
async def b() -> None:
    await asyncio.sleep(5)                  # non-blocking
    async with httpx.AsyncClient() as c:    # async HTTP
        await c.get("https://example.com")
```

❌ Mistake 2: Making every route `async def` "because it is faster"
✅ Correct: `async def` is not faster by itself. It only helps when you really `await` I/O.

```python
# Wrong — no await anywhere, sync DB driver inside: slower than def under load
async def users() -> list[int]:
    return [1, 2, 3]
# Right — plain def lets FastAPI use the thread pool for sync DB drivers
def users2() -> list[int]:
    return [1, 2, 3]
```

❌ Mistake 3: Heavy CPU work (image resize, ML inference, big loops) in either kind of route
✅ Correct: threads do not help CPU-bound code because of the GIL. Use a process pool or Celery.

```python
# Wrong — CPU loop inside async def blocks the loop
async def heavy() -> int:
    return sum(i * i for i in range(50_000_000))
# Right — send to another process (or a Celery worker)
```

---

## 🧠 Tricky Interview Question

```python
# What will happen when 2 users call /a at the same time?
import time
from fastapi import FastAPI
app = FastAPI()

@app.get("/a")
async def a() -> str:
    time.sleep(2)          # sync sleep inside async def
    return "A"

@app.get("/b")
def b() -> str:
    time.sleep(2)          # sync sleep inside def
    return "B"
```
Answer: Two simultaneous calls to `/a` take about 4 seconds in total, because `time.sleep` blocks the single event-loop thread and the second request cannot even start until the first finishes. Two simultaneous calls to `/b` take about 2 seconds, because each runs in its own thread from the pool. Worse, while `/a` sleeps, ALL other routes (even `/health`) are frozen. The fix for `/a` is `await asyncio.sleep(2)`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `def` and `async def` routes in FastAPI?
A1: `def` routes run in an external thread pool so blocking is safe. `async def` routes run on the event loop thread, so they must not block. Both can serve many users, but in different ways.

Q2: Is `async def` always faster?
A2: No. It only gives an advantage when the function awaits real non-blocking I/O. A CPU-bound or blocking function inside `async def` makes the app slower than a plain `def`.

Q3: How big is the thread pool and can I change it?
A3: AnyIO's default limiter is 40 threads. You can change it with `anyio.to_thread.current_default_thread_limiter().total_tokens = 100` at startup. More threads cost memory and do not help CPU-bound work.

Q4: How do I call a blocking function from an `async def` route?
A4: `await run_in_threadpool(func, *args)` (from `starlette.concurrency`) or `await asyncio.to_thread(func, *args)`. For CPU-heavy work use `ProcessPoolExecutor` or Celery.

Q5: Do dependencies and background tasks follow the same rule?
A5: Yes. A `def` dependency or `BackgroundTasks` function runs in the thread pool; an `async def` one runs on the loop. Mixing them in one request is fine.

---

## 🔷 When to Use + When Not to Use
✅ Use `async def` when:
- You call async libraries: httpx, asyncpg, async SQLAlchemy, redis.asyncio, motor/pymongo async
- You wait on many slow network calls (fan-out with `asyncio.gather`)
- You stream responses, use WebSockets or SSE

❌ Use plain `def` when:
- You use sync drivers (psycopg2, requests, boto3, pandas, Pillow)
- You are unsure whether a library is blocking
- The route is simple and has no I/O

❌ Avoid both for:
- Long CPU-bound jobs: use Celery, multiprocessing or a separate service

---

## 📊 Visual Diagram
```
                    uvicorn (1 event loop thread)
                              |
          +-------------------+--------------------+
          |                                        |
   async def route                             def route
   runs ON the loop                  sent to AnyIO thread pool (40)
          |                                        |
   await x  -> loop serves others      blocking call blocks only
   time.sleep -> LOOP FROZEN           that worker thread; loop is free
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Single thread that schedules coroutines | Coroutines को चलाने वाला single thread |
| Blocking call | Call that stops the thread until done | जो thread को रोक दे ऐसा call |
| Thread pool | A set of reusable worker threads | दोबारा उपयोग होने वाले worker threads का समूह |
| `await` | Pause here, let others run | यहाँ रुको, दूसरों को चलने दो |
| `run_in_threadpool` | Run sync code in a thread from async code | Async से sync code को thread में चलाना |
| GIL | Lock letting one thread run Python bytecode at a time | एक समय में एक thread का lock |

---

## ⚡ 3-Line Summary
English: `def` routes run in a thread pool, `async def` routes run on the event loop. Never put blocking calls inside `async def`; offload them with `run_in_threadpool` or use `def`. `async def` is only faster when you really `await` non-blocking I/O.
Hindi: `def` routes thread pool में चलते हैं, `async def` routes event loop पर। `async def` के अंदर कभी blocking call न रखें; उसे `run_in_threadpool` से offload करें या `def` उपयोग करें। `async def` तभी तेज है जब आप सच में non-blocking I/O को `await` करें।

---

## ➡️ Next Topic
**332. Database with FastAPI (SQLAlchemy)** — now that you know which route type to use, connect a real database with sessions, dependencies and Pydantic models.
