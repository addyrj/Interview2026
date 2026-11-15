---

# 298. FastAPI Performance
# हिंदी में: FastAPI की Performance (तेज़ क्यों और कैसे)

---

## 🔵 Simple Definition (English)
FastAPI is fast because it runs on an async server (uvicorn), uses Starlette for routing and Pydantic v2 (written in Rust) for validation. But speed depends on you: a blocking call inside an `async def` handler freezes the whole server.

## 🔵 सरल परिभाषा (Hindi)
FastAPI तेज़ इसलिए है कि वह async server (uvicorn) पर चलता है, routing के लिए Starlette और validation के लिए Pydantic v2 (Rust में लिखा) इस्तेमाल करता है। लेकिन गति आप पर भी निर्भर है: `async def` handler के अंदर blocking call पूरे server को जमा देती है।

---

## 🔴 Problem it Solves
Classic sync servers use one thread per request. When 1,000 requests wait for a database or an external API, you need 1,000 threads and a lot of memory. Async I/O lets one event loop handle many waiting requests. Understanding it prevents the most common performance bug: using blocking code in async handlers.

## 🔴 यह क्यों बना? (Hindi)
पुराने sync servers हर request के लिए एक thread लगाते हैं। जब 1,000 requests database या external API का इंतज़ार करें तो 1,000 threads और बहुत memory चाहिए। Async I/O में एक event loop इंतज़ार करती कई requests सँभालता है। इसे समझने से सबसे आम performance bug (async handler में blocking code) से बचा जा सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → uvicorn receives a request and hands it to the ASGI app (Starlette/FastAPI)
Step 2 → async def handler  -> runs ON the event loop; "await" lets others run while waiting
Step 3 → plain def handler  -> FastAPI runs it in a threadpool (default 40 threads)
Step 4 → Blocking call inside async def -> event loop is stuck, all requests wait
Step 5 → Pydantic v2 validates data in Rust; response is serialized once
Step 6 → Scale across CPU cores with multiple worker processes (gunicorn/uvicorn --workers)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → uvicorn request लेता है और ASGI app (Starlette/FastAPI) को देता है
Step 2 → async def handler  -> event loop पर ही चलता है; "await" से इंतज़ार में दूसरे चलते हैं
Step 3 → सादा def handler  -> FastAPI उसे threadpool में चलाता है (default 40 threads)
Step 4 → async def में blocking call -> event loop अटक जाती है, सारी requests रुक जाती हैं
Step 5 → Pydantic v2 Rust में validate करता है; response एक बार serialize होता है
Step 6 → CPU cores पर scale करने के लिए कई worker processes (gunicorn/uvicorn --workers)
```

---

## 🟡 Real World Example
A Zomato-style "restaurant details" endpoint calls three services: menu, ratings, offers. With `async def` and `asyncio.gather` the three calls run together in ~200 ms instead of 600 ms. A developer once used `requests.get` inside that `async def`: during peak, p99 latency jumped from 300 ms to 9 seconds because each call blocked the loop. Changing to `httpx.AsyncClient` fixed it.

## 🟡 Real Example Hindi mein
Zomato जैसे "restaurant details" endpoint में तीन services बुलाई जाती हैं: menu, ratings, offers। `async def` और `asyncio.gather` से तीनों साथ चलती हैं और 600 ms की जगह ~200 ms लगते हैं। एक developer ने उस `async def` में `requests.get` लगा दिया: peak में p99 latency 300 ms से 9 सेकंड हो गई क्योंकि हर call loop को रोकती थी। `httpx.AsyncClient` लगाने से ठीक हुआ।

---

## 💻 Code Example — Basic
```python
# Basic: measure async-good vs async-bad vs sync handlers (verified, Python 3.13)
# pip install fastapi httpx
import asyncio  # event loop tools
import time  # blocking sleep + timer
import httpx  # async client, can call the ASGI app directly
from fastapi import FastAPI  # framework

app: FastAPI = FastAPI()  # the app being measured


@app.get("/async-good")  # async handler with a NON-blocking wait
async def async_good() -> dict[str, str]:
    await asyncio.sleep(0.2)  # other requests can run during this wait
    return {"kind": "async-good"}  # response


@app.get("/async-bad")  # async handler with a BLOCKING call
async def async_bad() -> dict[str, str]:
    time.sleep(0.2)  # BLOCKS the event loop: nobody else runs for 0.2 s
    return {"kind": "async-bad"}  # response


@app.get("/sync-ok")  # plain def handler
def sync_ok() -> dict[str, str]:
    time.sleep(0.2)  # blocks only one worker thread from the threadpool
    return {"kind": "sync-ok"}  # response


async def hit(client: httpx.AsyncClient, path: str, n: int = 10) -> float:
    start: float = time.perf_counter()  # start timer
    await asyncio.gather(*(client.get(path) for _ in range(n)))  # n concurrent calls
    return time.perf_counter() - start  # elapsed seconds


async def main() -> None:
    transport = httpx.ASGITransport(app=app)  # call the app in-process, no network
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        for p in ("/async-good", "/async-bad", "/sync-ok"):  # try each route
            print(p, f"{await hit(c, p):.2f}s for 10 concurrent calls")  # show time

asyncio.run(main())  # run the experiment
# Real output (times vary a little per machine):
# /async-good 0.20s for 10 concurrent calls
# /async-bad 2.05s for 10 concurrent calls
# /sync-ok 0.23s for 10 concurrent calls
```

## 💻 Code Example — Advanced
```python
# Production style: parallel I/O, offload CPU work, reuse client, fast JSON response
import asyncio  # concurrency
from concurrent.futures import ProcessPoolExecutor  # separate processes for CPU work
from contextlib import asynccontextmanager  # lifespan helper
from typing import AsyncIterator  # type for the lifespan
import httpx  # async HTTP client
from fastapi import FastAPI  # framework
from fastapi.concurrency import run_in_threadpool  # run blocking code safely


def heavy_cpu(n: int) -> int:  # CPU-bound: must NOT run on the event loop
    return sum(i * i for i in range(n))  # pure computation


def blocking_legacy_call(x: int) -> int:  # an old blocking library function
    return x * 2  # pretend it does blocking I/O


@asynccontextmanager  # startup/shutdown in one function
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http = httpx.AsyncClient(timeout=5.0)  # ONE shared client (connection pooling)
    app.state.pool = ProcessPoolExecutor(max_workers=2)  # process pool for CPU tasks
    yield  # app serves requests here
    await app.state.http.aclose()  # close connections on shutdown
    app.state.pool.shutdown()  # stop the worker processes


app: FastAPI = FastAPI(lifespan=lifespan)  # attach lifespan


@app.get("/cpu/{n}")  # CPU heavy endpoint
async def cpu(n: int) -> dict[str, int]:
    loop = asyncio.get_running_loop()  # current event loop
    result: int = await loop.run_in_executor(app.state.pool, heavy_cpu, n)  # other process
    return {"result": result}  # event loop stayed free meanwhile


@app.get("/legacy/{x}")  # must call blocking code from async handler
async def legacy(x: int) -> dict[str, int]:
    value: int = await run_in_threadpool(blocking_legacy_call, x)  # thread, not the loop
    return {"value": value}  # safe


@app.get("/fanout")  # many upstream calls at once
async def fanout() -> dict[str, int]:
    async def one(i: int) -> int:  # pretend upstream call
        await asyncio.sleep(0.1)  # async I/O wait
        return i  # fake data

    results: list[int] = await asyncio.gather(*(one(i) for i in range(5)))  # ~0.1 s total
    return {"sum": sum(results)}  # 0+1+2+3+4 = 10

# Run with several processes for multiple CPU cores:
#   uvicorn main:app --workers 4        (or: gunicorn -k uvicorn.workers.UvicornWorker -w 4 main:app)
# Optional speedups: pip install uvloop httptools (uvicorn[standard] installs them)
```

---

## 🟠 JavaScript vs Python Comparison
Node.js also has a single-threaded event loop, so the same rule applies: never block it. In Node a heavy loop or `fs.readFileSync` blocks everything. In Python it is `time.sleep`, `requests`, or a heavy `for` loop inside `async def`.

```python
# Python: blocking vs non-blocking
await asyncio.sleep(1)      # good: yields to the loop
time.sleep(1)               # bad inside async def: blocks everyone
```
```javascript
// JavaScript (Node): blocking vs non-blocking
await new Promise(r => setTimeout(r, 1000));   // good
while (Date.now() < end) {}                    // bad: blocks the event loop
```

Key differences: Node's built-in libraries are mostly async already. Python has many old blocking libraries (`requests`, `psycopg2`, classic SQLAlchemy), so you must choose async versions (`httpx`, `asyncpg`, SQLAlchemy async) or use plain `def` handlers.

---

## 🟠 FastAPI Connection
The rule of thumb for FastAPI handlers:

| Your code inside the handler | Use |
|---|---|
| Uses `await` with async libraries (httpx, asyncpg) | `async def` |
| Uses blocking libraries (requests, psycopg2, sync SQLAlchemy) | plain `def` |
| Heavy CPU (image, ML inference, hashing) | `def` + process pool, or a task queue (Celery) |

```python
# FastAPI: response_model keeps the payload small and faster to serialize
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # schemas

app: FastAPI = FastAPI()  # app


class UserOut(BaseModel):  # only public fields leave the server
    id: int
    name: str


@app.get("/users/{uid}", response_model=UserOut)  # extra fields are dropped
def user(uid: int) -> dict[str, int | str]:
    return {"id": uid, "name": "Asha", "password_hash": "secret"}  # hash is filtered out
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside `async def`
✅ Correct: Use an async library, `run_in_threadpool`, or declare the handler with plain `def`.

```python
# Wrong: 10 concurrent calls take 2.05 s (measured above)
@app.get("/a")
async def a(): time.sleep(0.2)
# Right: 0.20 s (async) or 0.23 s (plain def in a thread)
@app.get("/a")
async def a(): await asyncio.sleep(0.2)
```

❌ Mistake 2: Creating a new HTTP client or DB connection per request
✅ Correct: Create once in `lifespan` and reuse it (connection pooling).

```python
# Wrong
async with httpx.AsyncClient() as c: ...     # new TCP/TLS handshake every request
# Right
request.app.state.http.get(url)              # shared pooled client
```

❌ Mistake 3: Running CPU-heavy code or a single worker and expecting scale
✅ Correct: Python threads share one GIL for CPU work. Use `--workers N` (processes), a process pool, or a queue. Note: Python 3.13 free-threaded builds are experimental, not the default.

---

## 🧠 Tricky Interview Question

**Q**: Which two of these handlers can serve 10 simultaneous 0.2 s requests in about 0.2 s?

```python
@app.get("/a")
async def a(): await asyncio.sleep(0.2)
@app.get("/b")
async def b(): time.sleep(0.2)
@app.get("/c")
def c(): time.sleep(0.2)
```

**Answer**:
```
/a -> ~0.20 s   (event loop is free during await)
/b -> ~2.05 s   (blocks the loop: requests run one after another)
/c -> ~0.23 s   (plain def goes to the threadpool, 40 threads by default)
```
So `/a` and `/c`. Surprising point: a plain `def` with blocking code is better than `async def` with blocking code. But with more than ~40 concurrent blocking requests, `/c` would also start queueing. (Timings measured on this machine.)

---

## ⚫ Interview Questions + Answers

Q1: What makes FastAPI fast?
A1: ASGI + uvicorn (uvloop, httptools), Starlette's lean core, Pydantic v2's Rust validation, and async I/O. The big wins come from not blocking the loop and from caching and DB tuning.

Q2: How does FastAPI run a plain `def` endpoint?
A2: In a threadpool (AnyIO, 40 threads by default), so blocking code does not stop the event loop.

Q3: How do you use multiple CPU cores?
A3: Run several worker processes: `uvicorn --workers 4` or gunicorn with `UvicornWorker`. Each process has its own event loop and memory; shared state needs Redis or a database.

Q4: Is `orjson` still needed?
A4: FastAPI's `ORJSONResponse` was a common speed-up but is deprecated in newer versions because with a response model FastAPI serializes via Pydantic's Rust serializer directly. Prefer a return type or `response_model`.

Q5: What are quick wins for latency?
A5: Async DB driver, connection pooling, caching (Redis), pagination, `response_model` to trim data, gzip middleware for big JSON, and moving slow work to background tasks or queues.

---

## 🔷 When to Use + When Not to Use

✅ Use async handlers when:
- The work is I/O bound and you have async libraries (HTTP calls, async DB, Redis)
- You have many concurrent, slow-waiting clients (chat, streaming, webhooks)

❌ Avoid async handlers when:
- You only have blocking libraries (use `def`)
- The task is CPU heavy (use process pool or worker queue)
- The endpoint is trivial and fast either way

---

## 📊 Visual Diagram

```
 async def (good)        async def + time.sleep (bad)      def (threadpool)
 ──────────────          ───────────────────────────       ────────────────
 loop: r1 r2 r3 ...      loop: [r1 blocks]                 loop: free
 (all waiting at await)        [r2 blocks]                 thread1: r1
 total ≈ 0.2 s                 [r3 blocks] ...             thread2: r2 ...
                          total ≈ N × 0.2 s                total ≈ 0.2 s (up to 40)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Scheduler that runs async tasks | async tasks चलाने वाला scheduler |
| Blocking call | Call that stops the thread while waiting | इंतज़ार में thread को रोकने वाली call |
| Threadpool | Pool of threads for sync handlers | sync handlers के लिए threads का समूह |
| Worker | One server process | एक server process |
| GIL | Lock allowing one thread to run Python at a time | एक समय में एक thread को Python चलाने देने वाला lock |
| p99 latency | Time under which 99% requests finish | 99% requests जितने में पूरी होती हैं |

---

## ⚡ 3-Line Summary
English: FastAPI is fast because of ASGI, Starlette and Pydantic v2, but only if you keep the event loop free. Use `async def` with async libraries, plain `def` with blocking ones, and processes for CPU work. Reuse clients and run multiple workers.
Hindi: FastAPI ASGI, Starlette और Pydantic v2 की वजह से तेज़ है, पर तभी जब आप event loop को खाली रखें। Async libraries के साथ `async def`, blocking वालों के साथ सादा `def`, और CPU काम के लिए processes इस्तेमाल करें। Clients दोबारा इस्तेमाल करें और कई workers चलाएँ।

---

## ➡️ Next Topic
**299. Installing + First App** — install FastAPI, write your first endpoint and open the auto docs.
