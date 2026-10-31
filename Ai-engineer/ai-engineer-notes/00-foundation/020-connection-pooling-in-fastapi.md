---

# 020. Connection Pooling in FastAPI
# हिंदी में: FastAPI में Connection Pooling

---

## 🔵 Simple Definition (English)
A connection pool keeps a limited set of open connections (to Postgres, Redis or an HTTP API like OpenAI) that requests borrow and return, instead of opening a new one each time. It saves setup time, caps load on the other side, and gives natural backpressure when everything is busy.

## 🔵 सरल परिभाषा (Hindi)
Connection pool खुले connections (Postgres, Redis या OpenAI जैसे HTTP API के) का सीमित set रखता है जिसे requests उधार लेकर लौटाती हैं, हर बार नया connection खोलने की जगह। इससे setup समय बचता है, दूसरी तरफ़ का load सीमित रहता है, और सब कुछ busy होने पर स्वाभाविक backpressure मिलता है।

---

## 🔴 Problem it Solves
Opening a connection costs a TCP handshake, TLS and authentication (20-100 ms), and databases cap connections (Postgres defaults to 100, each using several MB). Without a pool, 500 concurrent requests would try 500 connections and crash the database, or each request would pay the setup latency. HTTP clients without pooling also re-do TLS for every LLM call.

## 🔴 यह क्यों बना? (Hindi)
Connection खोलने में TCP handshake, TLS और authentication लगते हैं (20-100 ms), और databases connections सीमित रखते हैं (Postgres में default 100, हर एक कई MB लेता है)। Pool के बिना 500 concurrent requests 500 connections खोलने की कोशिश करेंगी और database गिर सकता है, या हर request को setup latency भरनी पड़ेगी। Pooling के बिना HTTP clients भी हर LLM call पर TLS दोबारा करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Startup (lifespan): create pools ONCE per process: DB pool, Redis client, one shared HTTP client
Step 2 → Pool opens min_size connections and keeps them idle, ready to use
Step 3 → A request calls pool.acquire(): gets an idle connection immediately (no handshake)
Step 4 → If all are in use and size < max_size, the pool opens a new one; if at max, the request WAITS
Step 5 → Request finishes: connection is released back (reset state, not closed)
Step 6 → Waiting too long → acquire timeout → return 503 (backpressure, protects the DB)
Step 7 → Shutdown: close pools gracefully. Total connections = pool_max x workers x replicas
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Startup (lifespan) में pools प्रति process एक बार बनाओ: DB pool, Redis client, एक shared HTTP client
Step 2 → Pool min_size connections खोलकर idle तैयार रखता है
Step 3 → Request pool.acquire() करती है: तुरंत idle connection मिलता है (handshake नहीं)
Step 4 → सब busy हैं और size < max_size तो pool नया खोलता है; max पर हो तो request इंतज़ार करती है
Step 5 → Request खत्म: connection वापस जाता है (state reset, बंद नहीं)
Step 6 → बहुत देर इंतज़ार → acquire timeout → 503 लौटाओ (backpressure, DB की रक्षा)
Step 7 → Shutdown: pools शालीनता से बंद करो। कुल connections = pool_max x workers x replicas
```

---

## 🟡 Real World Example
**Tariff Classification System**: One Uvicorn worker holds: an asyncpg pool (min 2, max 5), one Redis client (its own pool, max 20), and one `httpx.AsyncClient`/`AsyncOpenAI` (max 100 keep-alive connections). With 4 workers on 3 pods, the database sees up to 5 x 4 x 3 = 60 connections, safely under `max_connections=100`. The route releases the DB connection before the 3-second LLM call, so 5 connections serve hundreds of concurrent requests.

**Zomato AI**: At dinner peak, a pool with a 2-second acquire timeout returns a fast 503 plus fallback results instead of letting requests queue for 30 seconds.

## 🟡 Real Example Hindi mein
**Tariff System**: एक Uvicorn worker के पास: asyncpg pool (min 2, max 5), एक Redis client (अपना pool, max 20), और एक `httpx.AsyncClient`/`AsyncOpenAI` (max 100 keep-alive connections)। 3 pods पर 4 workers के साथ database को अधिकतम 5 x 4 x 3 = 60 connections दिखते हैं, `max_connections=100` से सुरक्षित। Route 3 second की LLM call से पहले DB connection छोड़ देता है, इसलिए 5 connections सैकड़ों concurrent requests संभालते हैं।

**Zomato AI**: Dinner peak में 2 second acquire timeout वाला pool 30 second queue करने की जगह तुरंत 503 और fallback results देता है।

---

## 💻 Code Example — Basic
```python
# Basic pool idea without any server: a tiny async pool built with asyncio.Queue, pure Python.
# It shows borrow/return, max size and waiting - the same logic real pools use.
import asyncio  # async tools
import time  # timing


class FakeConn:  # stands in for a real DB connection
    created = 0  # how many were created in total

    def __init__(self) -> None:  # constructor
        FakeConn.created += 1  # count creations (each would cost a handshake)
        self.id = FakeConn.created  # connection id

    async def query(self, sql: str) -> str:  # pretend query
        await asyncio.sleep(0.1)  # 100 ms of work
        return f"conn{self.id}: {sql}"  # result


class Pool:  # minimal pool
    def __init__(self, size: int) -> None:  # fixed size
        self._q: asyncio.Queue[FakeConn] = asyncio.Queue()  # idle connections
        for _ in range(size):  # pre-create
            self._q.put_nowait(FakeConn())  # add

    async def acquire(self, timeout: float = 1.0) -> FakeConn:  # borrow
        return await asyncio.wait_for(self._q.get(), timeout)  # waits if none are free

    def release(self, conn: FakeConn) -> None:  # return
        self._q.put_nowait(conn)  # back to idle


async def handle(pool: Pool, n: int) -> str:  # one "request"
    conn = await pool.acquire()  # borrow
    try:  # always return it
        return await conn.query(f"SELECT {n}")  # use it
    finally:  # runs even on error
        pool.release(conn)  # return it


async def main() -> None:  # demo
    pool = Pool(size=3)  # only 3 connections
    start = time.perf_counter()  # timer
    results = await asyncio.gather(*(handle(pool, i) for i in range(9)))  # 9 concurrent requests share 3 connections
    print(len(results), "requests done in", round(time.perf_counter() - start, 1), "s")  # about 0.3 s (3 rounds)
    print("connections ever created:", FakeConn.created)  # 3, reused


asyncio.run(main())  # run it
```

## 💻 Code Example — Advanced
```python
# Production pool management: lifespan creates DB + Redis + HTTP pools once, acquire timeouts mapped to 503,
# pool stats endpoint, release-before-LLM pattern, and sizing helper. Needs asyncpg, redis, httpx, fastapi.
import os  # env
from contextlib import asynccontextmanager  # lifespan
from typing import Annotated, AsyncIterator  # typing

import asyncpg  # Postgres driver
import httpx  # HTTP client
import redis.asyncio as redis  # Redis client
from fastapi import Depends, FastAPI, HTTPException, Request  # FastAPI


def pool_size_per_worker(db_max_connections: int, replicas: int, workers: int, reserve: int = 10) -> int:  # sizing helper
    usable = db_max_connections - reserve  # keep spare for admin, migrations, monitoring
    return max(1, usable // (replicas * workers))  # equal share per worker process


@asynccontextmanager  # lifespan
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # startup/shutdown
    per_worker = pool_size_per_worker(db_max_connections=100, replicas=3, workers=4)  # 90 // 12 = 7
    app.state.db = await asyncpg.create_pool(  # DB pool
        os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"),  # DSN
        min_size=1, max_size=per_worker,  # bounded
        max_inactive_connection_lifetime=300,  # close idle ones after 5 min
        command_timeout=10,  # per-query timeout
    )  # ready
    app.state.redis = redis.from_url(  # Redis client (has its own internal pool)
        os.environ.get("REDIS_URL", "redis://localhost:6379"), max_connections=20, decode_responses=True,  # cap
        socket_timeout=1, socket_connect_timeout=1,  # fast failure
    )  # ready
    app.state.http = httpx.AsyncClient(  # ONE shared HTTP client for LLM/other APIs
        timeout=httpx.Timeout(30, connect=5),  # total and connect timeouts
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),  # pool limits
    )  # ready
    yield  # serve
    await app.state.http.aclose()  # close HTTP pool
    await app.state.redis.aclose()  # close Redis pool
    await app.state.db.close()  # close DB pool (waits for connections to be released)


app = FastAPI(lifespan=lifespan)  # app


async def db_conn(request: Request) -> AsyncIterator[asyncpg.Connection]:  # dependency with acquire timeout
    try:  # waiting for a connection can time out
        async with request.app.state.db.acquire(timeout=2) as conn:  # wait at most 2 s
            yield conn  # lend it
    except TimeoutError as exc:  # pool exhausted
        raise HTTPException(status_code=503, detail="server busy, retry shortly", headers={"Retry-After": "2"}) from exc  # shed load


Conn = Annotated[asyncpg.Connection, Depends(db_conn)]  # type shortcut


@app.get("/pool-stats")  # operational endpoint
async def pool_stats(request: Request) -> dict[str, int]:  # handler
    pool: asyncpg.Pool = request.app.state.db  # DB pool
    return {"size": pool.get_size(), "idle": pool.get_idle_size(), "max": pool.get_max_size(),
            "min": pool.get_min_size()}  # watch these in dashboards


@app.post("/classify")  # route showing the release-before-LLM pattern
async def classify(request: Request, description: str) -> dict[str, str]:  # handler
    # 1) short DB use, connection returned immediately after the block
    async with request.app.state.db.acquire(timeout=2) as conn:  # borrow
        known = await conn.fetchval("SELECT hs_code FROM classifications WHERE description = $1 LIMIT 1", description)  # lookup
    if known:  # found in DB
        return {"hs_code": known, "source": "db"}  # no LLM call
    # 2) slow LLM call happens with NO DB connection held
    r = await request.app.state.http.post(  # shared pooled HTTP client
        "https://api.openai.com/v1/chat/completions",  # endpoint
        headers={"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}"},  # key from env
        json={"model": "gpt-4o-mini", "max_tokens": 30,
              "messages": [{"role": "user", "content": f"HS code for: {description}"}]},  # tiny request
    )  # response
    if r.status_code != 200:  # provider error
        raise HTTPException(status_code=502, detail="LLM provider error")  # map
    code = r.json()["choices"][0]["message"]["content"].strip()  # answer
    # 3) borrow again briefly to save
    async with request.app.state.db.acquire(timeout=2) as conn:  # borrow again
        await conn.execute("INSERT INTO classifications (description, hs_code) VALUES ($1, $2)", description, code)  # save
    return {"hs_code": code, "source": "llm"}  # response
```

---

## 🟠 FastAPI Integration
Create pools in `lifespan`, store them on `app.state`, hand them out through dependencies, and expose pool stats for monitoring. Remember pools are per process: with `uvicorn --workers 4` you get 4 pools. For SQLAlchemy async use `create_async_engine(url, pool_size=5, max_overflow=0, pool_timeout=2, pool_pre_ping=True)`. If you use PgBouncer in transaction mode, set asyncpg `statement_cache_size=0`.

```python
# SQLAlchemy async pool settings (alternative to raw asyncpg)
from sqlalchemy.ext.asyncio import create_async_engine  # async engine

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost/postgres",  # URL
    pool_size=5,  # steady connections
    max_overflow=0,  # no extra bursts beyond pool_size (predictable total)
    pool_timeout=2,  # wait at most 2 s for a free connection
    pool_pre_ping=True,  # test connection before use (handles dropped connections)
    pool_recycle=1800,  # replace connections older than 30 min
)  # engine
```

---

## 🔗 LangChain / LangGraph Connection
LangChain chat models wrap an `httpx` client (OpenAI SDK) with its own pool: create the model once and reuse it, not per request. You can pass a shared client: `ChatOpenAI(http_async_client=shared_httpx_client)`. LangGraph checkpointers (`AsyncPostgresSaver`) can take a `psycopg_pool.AsyncConnectionPool`, so graph state saves share pooled connections.

```python
# Reuse one httpx client for LangChain's OpenAI calls (needs OPENAI_API_KEY)
import httpx  # client
from langchain_openai import ChatOpenAI  # model

shared = httpx.AsyncClient(limits=httpx.Limits(max_connections=100, max_keepalive_connections=20), timeout=30)  # pool
llm = ChatOpenAI(model="gpt-4o-mini", http_async_client=shared, max_retries=2)  # reuse the pool for every request
# result = await llm.ainvoke("HS code for a laptop")  # no new TLS handshake per call
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating a client or pool inside the route
✅ Correct: create once in lifespan.

```python
# Wrong: new pool (and many new connections) per request
@app.get("/x")
async def x():
    pool = await asyncpg.create_pool(DSN)
    ...
# Right: use app.state.db created in lifespan
```

❌ Mistake 2: Holding a connection while calling the LLM
✅ Correct: release first, call the LLM, acquire again.

```python
# Wrong: connection is idle for 3 seconds; 5 users exhaust a 5-connection pool
async with pool.acquire() as conn:
    row = await conn.fetchrow(...)
    answer = await llm.ainvoke(...)   # slow!
    await conn.execute(...)
# Right: three separate short uses (see classify above)
```

❌ Mistake 3: Pool size = "as large as possible". Postgres performs worse with hundreds of connections. Size from total capacity: `max_connections / (replicas x workers)`, and use PgBouncer for many clients.

---

## 🧠 Tricky Interview Question

**Q**: "You increased pool max_size from 10 to 100 to fix timeouts, and the database got slower and started rejecting connections. Why?"

**Answer**: More connections do not mean more throughput. Postgres has a limited number of CPU cores and each connection is a process using memory; too many active connections cause context switching and lock contention, so latency rises. And since pools are per worker process, 100 x workers x replicas can exceed `max_connections`. The real fixes: find why connections are held too long (LLM calls inside the block, slow queries, missing indexes), shorten transactions, add indexes, use PgBouncer in transaction mode, cache reads in Redis, and set a modest pool (roughly `cores x 2` per database in total, tuned by measurement) with an acquire timeout to shed load.

---

## ⚫ Interview Questions + Answers

Q1: What is a connection pool? (Easy)
A1: A set of reusable open connections. Requests borrow one and return it, avoiding the cost of opening a new connection each time and limiting the load on the server.

Q2: Where should pools be created in FastAPI? (Easy)
A2: In the `lifespan` startup handler, stored on `app.state` (or module-level singleton), and closed on shutdown. Never per request.

Q3: What happens when the pool is exhausted? (Medium)
A3: `acquire()` waits until a connection is released. Without a timeout it can wait forever and requests pile up. Set an acquire timeout and return 503 with `Retry-After`; this is backpressure and protects the database.

Q4: How do you compute the pool size? (Medium)
A4: Start from the database's capacity: `(max_connections - reserved) / (replicas x workers_per_replica)`. Then check that concurrency needs are met given short holding times: in-flight DB requests ≈ requests per second x average connection hold time (Little's law). Measure pool wait times and tune.

Q5: Why do LLM-heavy APIs need fewer DB connections than they have concurrent users, and how do you ensure it? (Hard)
A5: Most of a request's life is waiting on the LLM (seconds), while DB work takes milliseconds. If the DB connection is held only during the actual queries, 5 connections can serve hundreds of concurrent users: with 100 requests per second and 10 ms of DB time per request, only about 1 connection is busy on average (Little's law: 100 x 0.01). Ensure this by never acquiring a connection (or opening a transaction) before the LLM call, using short `async with` blocks, avoiding connection-scoped dependencies on routes that call the LLM (a yield-dependency holds the connection until the response is sent, even during the LLM call!), and verifying with pool stats and `pg_stat_activity` (idle in transaction should be near zero).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any service talking to Postgres, Redis or HTTP APIs repeatedly
- Many concurrent requests share limited backend capacity
- You want predictable latency and resource use

❌ Avoid when:
- A one-off script (a single connection is fine)
- Serverless functions with short lifetimes (use an external pooler like PgBouncer/RDS Proxy)
- Using pool size to hide slow queries or long-held connections

---

## 📊 Visual Diagram
```
   300 concurrent requests (each waits ~3 s for the LLM)
        │
        ▼
 ┌────────────── FastAPI worker ───────────────┐
 │  DB pool (max 5)    Redis pool (max 20)      │
 │  [c1][c2][c3][c4][c5]   [r1]..[r20]          │
 │   ▲ borrowed only for ~10 ms                 │
 │  HTTP pool (max 100)  ──► LLM provider       │
 │   (keep-alive, TLS reused)                   │
 └──────────────────────────────────────────────┘
 Total DB connections = 5 per worker x 4 workers x 3 pods = 60  (< max_connections 100)

 Anti-pattern: acquire ─► await LLM (3 s) ─► release   → 5 users exhaust the pool
```

---

## 💰 Cost Impact
Pooling does not change tokens, but it lowers infrastructure cost and prevents waste. A shared HTTP client keeps TLS connections alive, cutting latency by about 50-150 ms per call and reducing timeouts that trigger paid retries. Right-sized DB pools let a small database instance serve high traffic instead of paying for a bigger one. Failing fast (503 on acquire timeout) stops requests from queueing, timing out and being retried by clients, where each retry could repeat a 700-token LLM call. Example: 2 percent of 100K daily requests timing out and retried twice at 700 tokens wastes 2.8M tokens, about $0.4 per day on gpt-4o-mini input pricing, plus user frustration.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Connection pool | Reusable set of connections | connections का reusable set |
| min_size / max_size | Lowest / highest pool size | pool का न्यूनतम / अधिकतम आकार |
| acquire / release | Borrow / return a connection | उधार लेना / लौटाना |
| Acquire timeout | Max wait for a free connection | connection के लिए अधिकतम इंतज़ार |
| Backpressure | Slow or reject when overloaded | overload पर धीमा/reject |
| Keep-alive | Reuse an open HTTP connection | खुला HTTP connection दोबारा use |
| PgBouncer | External Postgres connection pooler | Postgres का बाहरी pooler |
| Little's law | In-flight = rate x time | in-flight = दर x समय |

---

## ⚡ 3-Line Summary
English: Create DB, Redis and HTTP pools once per process in `lifespan`, with size limits, acquire timeouts and shared clients. Hold a connection only for the milliseconds you need it, never during an LLM call. Size pools from total database capacity divided by workers and replicas.
Hindi: DB, Redis और HTTP pools `lifespan` में प्रति process एक बार बनाओ, size limits, acquire timeouts और shared clients के साथ। Connection सिर्फ़ उन milliseconds के लिए पकड़ो जितने चाहिए, LLM call के दौरान कभी नहीं। Pool size database की कुल क्षमता को workers और replicas से भाग देकर तय करो।

---

## ➡️ Next Topic
**021. What is an LLM — How it Works** — with the Python and FastAPI foundation complete, we start Phase 1 (LLM APIs) by understanding what an LLM is and how it works.
