---

# 348. FastAPI Performance Tips
# हिंदी में: FastAPI Performance Tips (API को तेज़ कैसे करें)

---

## 🔵 Simple Definition (English)
FastAPI is fast by design, but your code decides real speed. The big wins are: never block the event loop, reuse connections (pools and one shared HTTP client), run several workers, cache repeated work, return less data (pagination, compression), and fix N+1 database queries. Measure first, then optimize.

## 🔵 सरल परिभाषा (Hindi)
FastAPI design से तेज़ है, पर असली speed आपका code तय करता है। बड़े फ़ायदे: event loop को block न करें, connections दोबारा इस्तेमाल करें (pools और एक साझा HTTP client), कई workers चलाएँ, बार-बार होने वाला काम cache करें, कम data लौटाएँ (pagination, compression) और N+1 database queries ठीक करें। पहले measure करें, फिर optimize करें।

---

## 🔴 Problem it Solves
Slow APIs lose users and cost money: a single `time.sleep` or blocking DB call inside `async def` stalls every request; opening a new DB connection per request wastes 20-50 ms; returning 10,000 rows per call floods the network. Knowing the usual causes lets you fix 90% of slowness without rewriting the app.

## 🔴 यह क्यों बना? (Hindi)
धीमी API users खोती है और पैसा खर्च कराती है: `async def` में एक `time.sleep` या blocking DB call हर request को रोक देता है; हर request पर नया DB connection खोलना 20-50 ms बर्बाद करता है; एक call में 10,000 rows लौटाना network भर देता है। आम कारण जान लें तो बिना app दोबारा लिखे 90% धीमापन ठीक हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure: log request time, use a profiler or load test (locust, k6, wrk)
Step 2 → Fix event-loop blocking: def for blocking code, await for async libs
Step 3 → Reuse connections: DB pool, one httpx.AsyncClient created in lifespan
Step 4 → Scale out: several worker processes (uvicorn --workers / gunicorn) per CPU
Step 5 → Cache: lru_cache for pure functions, Redis for shared cache with TTL
Step 6 → Send less: pagination (limit/offset or keyset), select only needed columns, GZip
Step 7 → Fix N+1 queries with joinedload/selectinload; add DB indexes
Step 8 → Move slow work to BackgroundTasks / Celery and return 202 quickly
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Measure करें: request time log करें, profiler या load test (locust, k6, wrk) चलाएँ
Step 2 → Event-loop blocking ठीक करें: blocking code के लिए def, async libs के लिए await
Step 3 → Connections दोबारा इस्तेमाल: DB pool, lifespan में बना एक httpx.AsyncClient
Step 4 → Scale: हर CPU के हिसाब से कई worker processes (uvicorn --workers / gunicorn)
Step 5 → Cache: pure functions के लिए lru_cache, साझा cache के लिए TTL वाला Redis
Step 6 → कम भेजें: pagination, सिर्फ़ ज़रूरी columns, GZip
Step 7 → N+1 queries को joinedload/selectinload से ठीक करें; DB indexes जोड़ें
Step 8 → धीमा काम BackgroundTasks / Celery को दें और जल्दी 202 लौटाएँ
```

---

## 🟡 Real World Example
A Flipkart-like product listing endpoint took 1.8 s. Profiling showed 101 SQL queries (N+1: one for products, one per product for its seller). Switching to `selectinload` cut it to 2 queries; adding `limit=50` pagination and GZip reduced the payload from 2 MB to 40 KB; caching the category list in Redis for 60 s removed another query. Result: about 120 ms.

## 🟡 Real Example Hindi mein
Flipkart जैसे product listing endpoint को 1.8 s लग रहे थे। Profiling में 101 SQL queries मिलीं (N+1: products की एक और हर product के seller की एक-एक)। `selectinload` लगाने से 2 queries रह गईं; `limit=50` pagination और GZip से payload 2 MB से 40 KB हुआ; category list को 60 s के लिए Redis में cache करने से एक और query हटी। नतीजा: करीब 120 ms।

---

## 💻 Code Example — Basic
```python
# Basic: why blocking the event loop is the #1 performance bug
# pip install fastapi httpx   (verified run; timings vary per machine)
import asyncio  # event loop tools
import time  # blocking sleep (the villain)
from fastapi import FastAPI  # framework
import httpx  # async client used as in-memory tester

app: FastAPI = FastAPI()  # app


@app.get("/blocking")  # async + blocking call = BAD
async def blocking() -> int:
    time.sleep(0.2)  # freezes the whole event loop
    return 1


@app.get("/sync")  # plain def = runs in thread pool = fine
def sync() -> int:
    time.sleep(0.2)  # only this thread waits
    return 1


@app.get("/nb")  # async + await = fine
async def nb() -> int:
    await asyncio.sleep(0.2)  # loop is free to serve others
    return 1


async def run(path: str) -> float:
    transport = httpx.ASGITransport(app=app)  # direct to app
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as c:
        start: float = time.perf_counter()  # start timer
        await asyncio.gather(*[c.get(path) for _ in range(5)])  # 5 simultaneous requests
        return time.perf_counter() - start  # elapsed seconds


for p in ["/blocking", "/sync", "/nb"]:  # try all three
    print(p, round(asyncio.run(run(p)), 1))  # print time
# Output (approx, measured):
# /blocking 1.0
# /sync 0.2
# /nb 0.2
```

## 💻 Code Example — Advanced
```python
# Production style: shared HTTP client, caching, GZip, pagination, background work
# pip install fastapi httpx   (verified: gzip used, cached call fast)
from contextlib import asynccontextmanager  # lifespan helper
from functools import lru_cache  # in-process cache
from typing import AsyncIterator, Dict, List  # types

import httpx  # async HTTP client
from fastapi import BackgroundTasks, FastAPI, Query, Request  # FastAPI pieces
from fastapi.middleware.gzip import GZipMiddleware  # compress big responses
from fastapi.testclient import TestClient  # demo runner
from pydantic import BaseModel  # response schema


class Row(BaseModel):  # one row of output
    id: int  # id
    name: str  # name


@asynccontextmanager  # create heavy objects ONCE
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http = httpx.AsyncClient(timeout=5.0)  # shared client = connection reuse
    yield  # serve
    await app.state.http.aclose()  # close sockets


app: FastAPI = FastAPI(lifespan=lifespan)  # app
app.add_middleware(GZipMiddleware, minimum_size=500)  # compress bodies >= 500 bytes

ALL: List[Row] = [Row(id=i, name=f"item-{i}") for i in range(5000)]  # fake table


@app.get("/rows", response_model=List[Row])  # paginated list
def rows(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)) -> List[Row]:
    return ALL[offset: offset + limit]  # never return the whole table


@lru_cache(maxsize=1)  # cache a pure, expensive function
def categories() -> int:
    return 42  # imagine a slow computation or DB query


def write_audit(msg: str) -> None:  # slow side effect
    print("audit:", msg)  # e.g. write to a log store


@app.post("/orders", status_code=202)  # 202 = accepted, work continues
def order(bg: BackgroundTasks) -> Dict[str, str]:
    bg.add_task(write_audit, "order placed")  # runs AFTER the response is sent
    return {"status": "accepted"}  # fast reply


@app.get("/ext")  # call external API using the shared client
async def ext(request: Request) -> Dict[str, int]:
    _ = request.app.state.http  # reuse: await _.get("https://api.example.com/x")
    return {"cats": categories()}  # cached value


with TestClient(app) as c:  # `with` runs lifespan
    r = c.get("/rows", params={"limit": 100}, headers={"accept-encoding": "gzip"})  # ask for gzip
    print(r.status_code, r.headers.get("content-encoding"), len(r.json()))  # gzip is used
    # Output: 200 gzip 100
    print(c.post("/orders").status_code)  # background task runs after response
    # Output: audit: order placed   (printed by the task)
    # Output: 202
    print(c.get("/ext").json())  # cached categories
    # Output: {'cats': 42}
```
Verified by running (a variant with 500 rows): the response carried `content-encoding: gzip` and the compressed body was smaller than the plain one (about 14 KB uncompressed for 500 small rows; compression ratio improves for bigger payloads); the second call to an `lru_cache`-d 0.2 s function took far less than 0.05 s. Version note: `ORJSONResponse` and `UJSONResponse` are deprecated in recent FastAPI (0.162 prints `FastAPIDeprecationWarning: ORJSONResponse is deprecated`), because FastAPI now serializes with Pydantic's Rust core directly; do not add orjson just for speed.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: CPU work blocks, use more processes; I/O waits use async
# uvicorn app.main:app --workers 4        # 4 processes = real parallelism for CPU
await asyncio.gather(fetch(a), fetch(b))  # parallel I/O inside one process
```
```javascript
// Node.js: same single-thread event-loop model
// pm2 start app.js -i max                // cluster = one process per core
await Promise.all([fetch(a), fetch(b)]);  // parallel I/O inside one process
// Blocking the loop (JSON.parse of 500MB, crypto sync) freezes Node exactly like time.sleep in Python
```

Key differences: both have a single-threaded event loop, so both suffer when you block it. Python also has the GIL, so CPU-heavy work needs multiple processes (workers, `ProcessPoolExecutor`, Celery), while Node uses `cluster`/`worker_threads`. FastAPI also gives you a free thread pool for plain `def` routes.

---

## 🟠 FastAPI Connection
Production setups run many worker processes behind a proxy. Each worker has its own memory, so in-process caches and counters are per worker (see 350 tricky question). Use Redis for shared caches.

```python
# Dependency that reuses one pooled client (do not create a client per request)
from typing import Annotated  # typing helper
from fastapi import Depends, FastAPI, Request  # FastAPI pieces
import httpx  # client type


def get_http(request: Request) -> httpx.AsyncClient:  # fetch the shared client
    return request.app.state.http  # created once in lifespan


HttpDep = Annotated[httpx.AsyncClient, Depends(get_http)]  # alias


app: FastAPI = FastAPI()  # app


@app.get("/rate")  # example route
async def rate(http: HttpDep) -> dict:
    r = await http.get("https://api.example.com/rate")  # reuses TCP/TLS connection
    return r.json()  # forward data
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside `async def`
```python
# Wrong: requests.get() or time.sleep() in async def stalls all users
async def handler(): return requests.get(url).json()

# Right: httpx.AsyncClient + await, or make the route a plain def
async def handler(): return (await client.get(url)).json()
```

❌ Mistake 2: New HTTP client or DB connection per request
```python
# Wrong: TLS handshake every call
async with httpx.AsyncClient() as c: await c.get(url)  # inside the route

# Right: create once in lifespan, reuse via Depends; use a DB pool
```

❌ Mistake 3: N+1 queries
```python
# Wrong: loop touches lazy relationship -> 1 + N queries
for p in db.scalars(select(Product)): print(p.seller.name)

# Right: eager load
db.scalars(select(Product).options(selectinload(Product.seller)))
```

❌ Mistake 4: Returning unbounded lists
```python
# Wrong: return db.query(Order).all()   # millions of rows
# Right: limit/offset or keyset pagination with le=100 cap
```

❌ Mistake 5: Optimizing without measuring
```python
# Right: add timing middleware / use py-spy / load-test, then fix the real bottleneck
```

---

## 🧠 Tricky Interview Question

**Q**: 5 clients call each route simultaneously; each does 0.2 s of "waiting". Predict the total time.

```python
@app.get("/blocking")
async def a(): time.sleep(0.2); return 1

@app.get("/sync")
def b(): time.sleep(0.2); return 1

@app.get("/nb")
async def c(): await asyncio.sleep(0.2); return 1
```

**Answer**:
```
/blocking  ~1.0 s   (requests run one after another)
/sync      ~0.2 s   (thread pool, default 40 threads)
/nb        ~0.2 s   (cooperative switching)
```
The `async def` route with `time.sleep` is the slowest, even though it looks "more async". (Measured: 1.0, 0.2, 0.2.)

---

## ⚫ Interview Questions + Answers

Q1: Why is my `async def` endpoint slow?
A1: Most often something inside is blocking (sync DB driver, `requests`, `time.sleep`, CPU loop). Use awaitable libraries, or use plain `def`, or `run_in_threadpool`.

Q2: How many workers should I run?
A2: Start with about one per CPU core (gunicorn rule of thumb: 2 x cores + 1 for sync workers, fewer for async). In containers, set workers by the CPU limit and scale replicas horizontally.

Q3: What is the N+1 problem?
A3: One query for the list plus one query per item for a related row. Fix with `joinedload`/`selectinload` or a JOIN.

Q4: When do you use BackgroundTasks vs Celery?
A4: `BackgroundTasks` for small, quick follow-up work in the same process (send an email). Celery/RQ/ARQ for long, retryable or heavy jobs that must survive a restart.

Q5: Does GZip always help?
A5: It helps for large text/JSON (over ~1 KB). It wastes CPU on tiny or already-compressed bodies (images). Often the reverse proxy (nginx) does compression instead.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- p95 latency or CPU is high, or you plan for traffic growth
- You see many DB queries per request in logs
- Payloads are large

❌ Avoid when:
- You have no measurements: premature optimization adds bugs
- The endpoint serves 10 requests a day

---

## 📊 Visual Diagram

```
 Client ──► nginx (TLS, gzip, rate limit)
              │
              ├─► Worker 1 (event loop + thread pool) ─┐
              ├─► Worker 2 (event loop + thread pool) ─┼─► DB pool ─► PostgreSQL
              └─► Worker 3 (event loop + thread pool) ─┘
                          │
                          └─► Redis (shared cache)    └─► Celery queue (slow jobs)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Scheduler for async code | async काम का scheduler |
| Blocking call | Call that stops the loop | loop को रोकने वाली call |
| Connection pool | Reused DB connections | दोबारा इस्तेमाल होने वाले connections |
| N+1 | One query plus N extra | एक query के साथ N और queries |
| Pagination | Return data in pages | data को pages में देना |
| Worker | One server process | server की एक process |

---

## ⚡ 3-Line Summary
English: Do not block the event loop, reuse connections, add workers, cache, paginate, compress and fix N+1 queries. Measure first and move slow jobs to background workers.
Hindi: Event loop को block न करें, connections दोबारा इस्तेमाल करें, workers बढ़ाएँ, cache करें, pagination और compression लगाएँ और N+1 queries ठीक करें। पहले measure करें और धीमे jobs को background workers को दें।

---

## ➡️ Next Topic
**349. FastAPI Security Checklist** — the protections every FastAPI service needs before going live.
