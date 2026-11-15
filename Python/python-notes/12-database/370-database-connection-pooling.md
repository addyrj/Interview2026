---

# 370. Database Connection Pooling
# हिंदी में: Database Connection Pooling (Connections को दोबारा इस्तेमाल करना)

---

## 🔵 Simple Definition (English)
A connection pool keeps a small set of already-open database connections. Each request borrows one, uses it, and gives it back instead of opening and closing a new connection every time. This saves time and protects the database from too many connections.

## 🔵 सरल परिभाषा (Hindi)
Connection pool पहले से खुले हुए database connections का एक छोटा समूह रखता है। हर request उनमें से एक उधार लेती है, इस्तेमाल करती है और वापस दे देती है, हर बार नया connection खोलने-बंद करने की जगह। इससे समय बचता है और database पर बहुत ज्यादा connections नहीं बनते।

---

## 🔴 Problem it Solves
Opening a database connection is expensive: TCP handshake, TLS, authentication, and (in PostgreSQL) a whole new server process using several MB of RAM. If every API request opens its own connection, latency grows and the database hits `max_connections` (PostgreSQL default is 100) and starts refusing users. A pool pays the open cost once, reuses connections, and caps the total number.

## 🔴 यह क्यों बना? (Hindi)
Database connection खोलना महंगा है: TCP handshake, TLS, authentication, और PostgreSQL में एक नया server process जो कई MB RAM लेता है। अगर हर API request अपना connection खोले तो latency बढ़ती है और database `max_connections` (PostgreSQL में default 100) तक पहुंचकर users को मना करने लगता है। Pool खोलने की कीमत एक बार चुकाता है, connections दोबारा इस्तेमाल करता है, और कुल संख्या सीमित रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → App start: create ONE engine (it owns the pool). Connections open lazily
Step 2 → Request arrives: engine.connect() / Session asks the pool for a connection
Step 3 → Idle connection exists → hand it out (pool_pre_ping tests it first)
Step 4 → No idle one, but total < pool_size + max_overflow → open a new connection
Step 5 → Limit reached → wait up to pool_timeout seconds, then raise TimeoutError
Step 6 → Request ends: close() does NOT close the socket, it returns it to the pool
Step 7 → pool_recycle replaces connections older than N seconds (firewalls kill idle ones)
Step 8 → App shutdown: engine.dispose() closes all pooled connections
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App शुरू होने पर: एक ही engine बनाओ (pool उसी के पास है)। Connections lazily खुलते हैं
Step 2 → Request आती है: engine.connect() / Session pool से connection मांगता है
Step 3 → Idle connection मिला → दे दो (pool_pre_ping पहले उसे test करता है)
Step 4 → Idle नहीं है पर कुल < pool_size + max_overflow → नया connection खोलो
Step 5 → Limit पूरी → pool_timeout सेकंड तक इंतजार, फिर TimeoutError
Step 6 → Request खत्म: close() socket बंद नहीं करता, pool में लौटा देता है
Step 7 → pool_recycle N सेकंड से पुराने connections बदल देता है (firewalls idle को मार देते हैं)
Step 8 → App बंद होने पर: engine.dispose() सारे pooled connections बंद करता है
```

---

## 🟡 Real World Example
During a Zomato lunch rush, 5,000 requests per second hit the backend. With 20 app servers each holding a pool of 10 connections, PostgreSQL sees only 200 connections, not 5,000. A Razorpay-style payments service also puts PgBouncer in front of PostgreSQL so thousands of app workers share a few hundred real connections.

## 🟡 Real Example Hindi mein
Zomato के lunch rush में backend पर 5,000 requests प्रति सेकंड आती हैं। 20 app servers और हर एक में 10 connections का pool हो तो PostgreSQL को सिर्फ 200 connections दिखते हैं, 5,000 नहीं। Razorpay जैसी payments service PostgreSQL के आगे PgBouncer भी लगाती है ताकि हजारों app workers कुछ सौ असली connections बांट लें।

---

## 💻 Code Example — Basic
```python
# Basic: SQLAlchemy QueuePool settings and live pool statistics (SQLite file, so pool is real)
from sqlalchemy import create_engine, text                   # engine + raw SQL
from sqlalchemy.pool import QueuePool                        # pool class

engine = create_engine(                                      # one engine = one pool, make it once
    "sqlite:///pool_demo.db",                                # file db (in-memory uses a different pool)
    poolclass=QueuePool,                                     # explicit queue pool
    pool_size=2,                                             # keep 2 connections ready
    max_overflow=1,                                          # allow 1 extra under load
    pool_timeout=1,                                          # wait max 1 sec for a connection
    pool_pre_ping=True,                                      # test connection before use
)
print(engine.pool.status())                                  # nothing checked out yet
c1 = engine.connect()                                        # borrow connection 1
c2 = engine.connect()                                        # borrow connection 2
c3 = engine.connect()                                        # borrow overflow connection
print(engine.pool.checkedout(), engine.pool.size())          # 3 in use, base size 2
try:
    engine.connect()                                         # 4th: pool is exhausted
except Exception as e:                                       # TimeoutError after pool_timeout
    print(type(e).__name__)
for c in (c1, c2, c3):                                       # ALWAYS give them back
    c.close()                                                # returns to pool, not really closed
print(engine.pool.checkedout())                              # 0 in use again
with engine.connect() as c:                                  # preferred: context manager
    print(c.execute(text("select 1")).scalar())             # run a query
engine.dispose()                                             # close all pooled connections

# Output:
# Pool size: 2  Connections in pool: 0 Current Overflow: -2 Current Checked out connections: 0
# 3 2
# TimeoutError
# 0
# 1
```
Verified: run with SQLAlchemy 2.1.8 and Python 3.13 (the 4th `connect()` takes about 1 second to time out). It creates a `pool_demo.db` file in the current directory.

## 💻 Code Example — Advanced
```python
# Advanced: a tiny thread-safe connection pool from scratch (shows what pools really do)
import queue                                                 # thread-safe FIFO
import sqlite3                                               # stdlib db
import threading                                             # threads for the load test
import time                                                  # timing
from contextlib import contextmanager                        # for "with pool.connection()"
from typing import Iterator                                  # generator hint


class SimplePool:
    def __init__(self, path: str, size: int = 3, timeout: float = 2.0) -> None:
        self._q: "queue.Queue[sqlite3.Connection]" = queue.Queue(maxsize=size)   # idle connections
        self._timeout = timeout                              # max wait for a free connection
        self.created = 0                                     # how many real connects happened
        for _ in range(size):                                # pre-create (open cost paid once)
            self._q.put(sqlite3.connect(path, check_same_thread=False))
            self.created += 1                                # count real connects

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        try:
            conn = self._q.get(timeout=self._timeout)        # borrow, blocks if none idle
        except queue.Empty:                                  # waited too long
            raise TimeoutError("pool exhausted") from None
        try:
            yield conn                                       # caller uses the connection
        finally:
            self._q.put(conn)                                # ALWAYS return, even on error

    def close(self) -> None:
        while not self._q.empty():                           # close every idle connection
            self._q.get().close()


pool = SimplePool(":memory:", size=3)                        # 3 connections for 12 workers
results: list[int] = []                                      # collected answers
lock = threading.Lock()                                      # protect the list


def worker(i: int) -> None:
    with pool.connection() as conn:                          # borrow
        time.sleep(0.05)                                     # pretend the query takes 50ms
        val = conn.execute("select ?", (i,)).fetchone()[0]   # run a query
    with lock:
        results.append(val)                                  # store result


threads = [threading.Thread(target=worker, args=(i,)) for i in range(12)]   # 12 concurrent users
for t in threads: t.start()                                  # go
for t in threads: t.join()                                   # wait
print(sorted(results))                                       # all 12 served
print("real connects:", pool.created)                        # only 3, reused 12 times
pool.close()                                                 # shutdown

# Output:
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
# real connects: 3
```
Verified: run as shown. Note each `:memory:` connection is a separate database, which is fine here because we only run `select ?`.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript (Node) |
|---------|--------|------------------|
| Pool library | SQLAlchemy `QueuePool`, `psycopg_pool`, `asyncpg.create_pool` | `pg.Pool`, `mysql2.createPool` |
| Size setting | `pool_size`, `max_overflow` | `max` |
| Wait limit | `pool_timeout` | `connectionTimeoutMillis` |
| Idle cleanup | `pool_recycle` | `idleTimeoutMillis` |
| Give back | `conn.close()` / `with` | `client.release()` |

```python
# Python way (asyncpg)
import asyncpg                                           # async PostgreSQL driver
async def main() -> None:
    pool = await asyncpg.create_pool(dsn="postgresql://u:p@localhost/db", min_size=2, max_size=10)
    async with pool.acquire() as conn:                   # borrow, auto-release on exit
        print(await conn.fetchval("select 1"))           # run a query
    await pool.close()                                   # shutdown
```
```javascript
// JavaScript way (node-postgres)
const { Pool } = require("pg");                          // import
const pool = new Pool({ max: 10, connectionTimeoutMillis: 2000 });   // pool config
const client = await pool.connect();                     // borrow
try { console.log((await client.query("select 1")).rows); }   // use
finally { client.release(); }                            // MUST release or the pool leaks
await pool.end();                                        // shutdown
```

Key difference: in Node, forgetting `client.release()` leaks a connection. In Python, `with` / `async with` releases automatically, even on exceptions. Also Python web servers use multiple processes, so each worker process has its own pool: total = workers x pool size.

---

## 🟠 FastAPI Connection
Create the engine once at module level (or in `lifespan`), give each request a Session through `Depends` and dispose the engine at shutdown. With multiple Uvicorn/Gunicorn workers, size the pool as `(pool_size + max_overflow) x workers`, and keep it below the database's `max_connections`.

```python
# FastAPI example — one engine, session per request, dispose on shutdown
from contextlib import asynccontextmanager                   # lifespan helper
from typing import AsyncIterator, Iterator                   # hints
from fastapi import Depends, FastAPI                         # FastAPI
from fastapi.testclient import TestClient                    # test
from sqlalchemy import create_engine, text                   # engine
from sqlalchemy.engine import Engine                         # type
from sqlalchemy.orm import Session, sessionmaker             # session factory
from sqlalchemy.pool import StaticPool                       # one shared conn for in-memory sqlite

engine: Engine = create_engine("sqlite://", poolclass=StaticPool,
                               connect_args={"check_same_thread": False})   # demo; prod: Postgres + QueuePool
SessionLocal = sessionmaker(engine)                          # session factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield                                                    # app runs here
    engine.dispose()                                         # close pool on shutdown


app = FastAPI(lifespan=lifespan)                             # app with lifecycle


def get_db() -> Iterator[Session]:
    with SessionLocal() as s:                                # borrow connection lazily
        yield s                                              # returned to pool after request


@app.get("/ping")
def ping(db: Session = Depends(get_db)) -> dict[str, int]:
    return {"db": db.execute(text("select 1")).scalar_one()}   # simple health query


with TestClient(app) as c:                                   # runs lifespan too
    print(c.get("/ping").json())
# Output:
# {'db': 1}
```
Verified: run with TestClient. The demo uses `StaticPool` because in-memory SQLite is per-connection; for PostgreSQL use the default `QueuePool`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating a new engine for every request
✅ Correct: create one engine for the whole app; it owns the pool

```python
# Wrong — a brand new pool (and new connections) per request
def handler_bad() -> None:
    engine = create_engine("postgresql+psycopg://u:p@db/app")   # new pool each call
    engine.connect()
# Right — module level, created once
engine = create_engine("postgresql+psycopg://u:p@db/app", pool_size=10, max_overflow=5)
```

❌ Mistake 2: Not returning connections (leak) so the app freezes with TimeoutError
✅ Correct: always use `with` or `try/finally`

```python
# Wrong
conn = engine.connect()
conn.execute(text("select 1"))            # exception here -> connection never returned
# Right
with engine.connect() as conn:            # returned automatically
    conn.execute(text("select 1"))
```

❌ Mistake 3: Pool bigger than the database can accept
✅ Correct: total = workers x (pool_size + max_overflow) must stay below `max_connections`

```python
# Wrong: 8 workers x (50 + 50) = 800 connections vs PostgreSQL max_connections = 100
# Right: 8 workers x (5 + 5) = 80; use PgBouncer if you need more
```

❌ Mistake 4: Holding a connection during slow external calls
✅ Correct: release the DB session before calling third-party APIs

```python
# Wrong: the connection is busy while we wait 3 seconds for a payment gateway
# with SessionLocal() as db: row = db.get(...); requests.post(gateway_url, timeout=3)
# Right: read what you need, leave the `with`, then call the gateway
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from sqlalchemy import create_engine
e = create_engine("sqlite:///tk.db", pool_size=1, max_overflow=0, pool_timeout=0.2)
c = e.connect()
try:
    e.connect()
except Exception as ex:
    print(type(ex).__name__)
c.close()
c2 = e.connect()
print(c2.closed, e.pool.checkedout())
c2.close()
print(e.pool.checkedout())
```
Answer: it prints `TimeoutError`, then `False 1`, then `0`. The pool allows only one connection and the first one is still checked out, so the second `connect()` waits 0.2 seconds and raises SQLAlchemy's `TimeoutError`. After `c.close()` the connection goes back to the pool (the socket stays open), so `c2` can borrow it again. `c2.closed` is `False` (we only closed `c`), and one connection is checked out. After `c2.close()` zero are checked out. (Output verified; creates `tk.db`.)

---

## ⚫ Interview Questions + Answers

Q1: Why is opening a database connection expensive?
A1: It needs a TCP handshake, usually TLS, authentication and server-side session setup. PostgreSQL forks a new backend process per connection (several MB RAM). Doing this per request adds milliseconds of latency and limits scale.

Q2: What do `pool_size`, `max_overflow`, `pool_timeout` and `pool_recycle` mean?
A2: `pool_size` is how many connections are kept open. `max_overflow` is how many extra temporary connections are allowed on top. `pool_timeout` is how long a caller waits when everything is busy before an error. `pool_recycle` closes and replaces connections older than N seconds, useful because MySQL (`wait_timeout`) and cloud firewalls drop idle connections.

Q3: What does `pool_pre_ping=True` do?
A3: Before handing out a connection, the pool sends a lightweight test query. If the connection died (database restart, network cut), it is replaced silently instead of your request failing with "connection closed". It costs one small round trip.

Q4: Why do you need PgBouncer if the app already has a pool?
A4: App pools are per process. With many workers or many pods, the total can exceed the database limit. PgBouncer sits in front of PostgreSQL and multiplexes thousands of client connections onto a small number of server connections (often in transaction pooling mode). Caution: in transaction mode, session features such as prepared statements and `SET` need care.

Q5: Is `async` code pooled differently?
A5: The idea is the same, but you need an async driver and pool (`asyncpg` pool, SQLAlchemy `create_async_engine`). The key rule: never run blocking sync DB calls inside `async def` because they block the event loop. Use sync endpoints (FastAPI runs them in a threadpool) or async drivers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any web service with many short requests to PostgreSQL/MySQL
- You want predictable latency and a hard limit on DB connections
- Running many workers or pods (add PgBouncer/RDS Proxy)

❌ Avoid when:
- A one-off script or cron job that runs one query (a pool is overkill; `NullPool` is fine)
- Serverless functions with thousands of cold starts (use an external pooler or HTTP-based DB access)
- SQLite in-memory tests (use `StaticPool` or `SingletonThreadPool` deliberately)

---

## 📊 Visual Diagram
```
 requests ─┐
 requests ─┼──►  ┌────────────── Pool (size 2 + overflow 1) ──────────────┐
 requests ─┤     │  [conn A] idle   [conn B] in use   [conn C] overflow   │
 requests ─┘     └───────┬────────────────────┬───────────────────┬───────┘
   (4th waits             ▼                    ▼                   ▼
    pool_timeout)    PostgreSQL (max_connections = 100)

 borrow → use → close() → back to pool (socket stays open)
 no free + limit hit → wait → TimeoutError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Connection pool | Reusable set of open connections | दोबारा इस्तेमाल होने वाले खुले connections |
| pool_size | Connections kept open | खुले रखे गए connections |
| max_overflow | Extra temporary connections | अतिरिक्त अस्थायी connections |
| pool_timeout | Max wait for a free connection | Free connection के लिए अधिकतम इंतजार |
| pool_recycle | Replace old connections | पुराने connections बदलना |
| pre-ping | Test before use | इस्तेमाल से पहले जांच |
| PgBouncer | External PostgreSQL pooler | PostgreSQL के आगे लगने वाला pooler |
| Connection leak | Borrowed but never returned | उधार लिया पर लौटाया नहीं |

---

## ⚡ 3-Line Summary
English: A connection pool reuses open database connections so requests skip the costly connect step. Create one engine, tune `pool_size` and `max_overflow` so workers x pool stays below the DB limit, and always return connections with `with`. Use `pool_pre_ping` and `pool_recycle` for long-running services and PgBouncer for large fleets.
Hindi: Connection pool खुले database connections को दोबारा इस्तेमाल करता है ताकि requests महंगा connect step छोड़ दें। एक ही engine बनाएं, `pool_size` और `max_overflow` ऐसे रखें कि workers x pool, DB की limit से कम रहे, और connections हमेशा `with` से लौटाएं। लंबे चलने वाले services के लिए `pool_pre_ping` और `pool_recycle`, और बड़े fleet के लिए PgBouncer इस्तेमाल करें।

---

## ➡️ Next Topic
**371. SQLite with Python** — the simplest database, built into Python; perfect to practice transactions, constraints and SQL before moving to server databases.
