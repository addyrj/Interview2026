---

# 417. Connection Pooling
# हिंदी में: Connection Pooling (connections को दोबारा इस्तेमाल करना)

---

## 🔵 Simple Definition (English)
A connection pool keeps a set of already-open database connections and lends them to requests. A request borrows one, runs its queries, and returns it instead of closing it. This avoids the slow work of opening a new connection (TCP, TLS, login) for every request.

## 🔵 सरल परिभाषा (Hindi)
Connection pool पहले से खुले database connections का एक समूह रखता है और requests को उधार देता है। Request एक connection लेती है, queries चलाती है और उसे बंद करने की बजाय वापस लौटा देती है। इससे हर request के लिए नया connection खोलने (TCP, TLS, login) का धीमा काम बच जाता है।

---

## 🔴 Problem it Solves
Opening a PostgreSQL/MySQL connection costs 5-50 ms (more with TLS) and uses server memory (PostgreSQL forks a process per connection). Opening one per request makes the app slow, and a traffic spike can open thousands of connections and crash the database (`too many connections`). A pool reuses a small, fixed number.

## 🔴 यह क्यों बना? (Hindi)
PostgreSQL/MySQL का connection खोलने में 5-50 ms लगते हैं (TLS के साथ ज़्यादा) और server की memory खर्च होती है (PostgreSQL हर connection पर एक process बनाता है)। हर request पर connection खोलने से app धीमा होता है, और traffic बढ़ने पर हज़ारों connections खुलकर database को गिरा सकते हैं (`too many connections`)। Pool थोड़े, तय संख्या के connections दोबारा इस्तेमाल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → At first use the pool opens connections lazily (up to pool_size)
Step 2 → Request calls engine.connect() / a Session query: pool lends an idle connection
Step 3 → If none is idle and total < pool_size + max_overflow: open a temporary extra one
Step 4 → If the limit is reached: wait up to pool_timeout seconds, then raise TimeoutError
Step 5 → When the request ends, close()/context-exit RETURNS the connection (it stays open)
Step 6 → pool_pre_ping tests it before reuse; pool_recycle replaces old ones
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले उपयोग पर pool connections lazily खोलता है (pool_size तक)
Step 2 → Request engine.connect() / Session query करती है: pool कोई खाली connection देता है
Step 3 → खाली न हो और कुल < pool_size + max_overflow हो तो एक अस्थायी अतिरिक्त connection खुलता है
Step 4 → सीमा पूरी हो तो pool_timeout सेकंड तक इंतज़ार, फिर TimeoutError
Step 5 → Request खत्म होने पर close()/context-exit connection को वापस लौटाता है (वह खुला रहता है)
Step 6 → pool_pre_ping reuse से पहले जाँचता है; pool_recycle पुराने connections बदलता है
```

---

## 🟡 Real World Example
A Razorpay-style API runs 8 gunicorn workers, each with `pool_size=10, max_overflow=5`, so at most 120 connections hit PostgreSQL (below its `max_connections`, often 100-500). On sale days, when a spike arrives, requests queue briefly in the pool instead of overloading the database. A PgBouncer sits in front of Postgres for even more connection sharing.

## 🟡 Real Example Hindi mein
Razorpay जैसा API 8 gunicorn workers चलाता है, हर एक में `pool_size=10, max_overflow=5`, इसलिए PostgreSQL पर अधिकतम 120 connections पहुँचते हैं (उसके `max_connections` से कम, अक्सर 100-500)। Sale वाले दिन spike आने पर requests database पर टूटने की बजाय pool में थोड़ी देर कतार में रहती हैं। और अधिक sharing के लिए Postgres के आगे PgBouncer लगाया जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: a pool reuses connections. Counting how many REAL connections get opened (pip install sqlalchemy)
import os  # temp file handling
import tempfile  # throwaway database file

from sqlalchemy import create_engine, event, text, NullPool, QueuePool  # engine + pool classes

path: str = os.path.join(tempfile.mkdtemp(), "demo.db")  # SQLite file (a file DB gets a real pool)
opened: dict[str, int] = {"pooled": 0, "unpooled": 0}  # real connections created


def make_engine(poolclass, key: str):
    eng = create_engine(f"sqlite:///{path}", poolclass=poolclass)  # engine with the chosen pool

    @event.listens_for(eng, "connect")  # fires only when a REAL new DBAPI connection is made
    def on_connect(dbapi_conn, record) -> None:
        opened[key] += 1  # count it

    return eng  # ready engine


pooled = make_engine(QueuePool, "pooled")  # reuses connections
unpooled = make_engine(NullPool, "unpooled")  # opens and closes a connection every time

for _ in range(50):  # 50 "requests"
    with pooled.connect() as c:  # borrow a connection from the pool
        c.execute(text("SELECT 1"))  # run a query; leaving the block RETURNS it to the pool
    with unpooled.connect() as c:  # opens a brand-new connection
        c.execute(text("SELECT 1"))  # run a query; leaving the block CLOSES it

print("with pool   :", opened["pooled"], "real connection(s)")  # reused all 50 times
# Output: with pool   : 1 real connection(s)
print("without pool:", opened["unpooled"], "real connection(s)")  # one per request
# Output: without pool: 50 real connection(s)
print(type(pooled.pool).__name__)  # default pool class for file databases in SQLAlchemy 2.x
# Output: QueuePool
```

## 💻 Code Example — Advanced
```python
# Advanced: pool_size, max_overflow, timeout, pre_ping, recycle, and pool exhaustion
import os  # paths
import tempfile  # temp file
from typing import List

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import TimeoutError as PoolTimeout  # raised when the pool is exhausted

path: str = os.path.join(tempfile.mkdtemp(), "pool.db")  # database file

engine = create_engine(
    f"sqlite:///{path}",
    pool_size=2,  # keep 2 connections ready
    max_overflow=1,  # allow 1 extra temporary connection (total max 3)
    pool_timeout=0.3,  # wait up to 0.3s for a free connection, then raise
    pool_recycle=1800,  # replace connections older than 30 minutes (avoids stale ones)
    pool_pre_ping=True,  # test a connection before using it, reconnect if it died
)
print(engine.pool.size(), engine.pool._max_overflow)  # configured limits
# Output: 2 1

held: List[Connection] = []  # connections we keep checked out (simulating slow requests)
for _ in range(3):  # take all 3 allowed connections
    held.append(engine.connect())  # borrow, do not return
print(engine.pool.checkedout())  # 3 in use (2 pooled + 1 overflow)
# Output: 3

try:  # the 4th request must wait, then fail
    engine.connect()  # no connection available
except PoolTimeout as exc:  # pool exhausted after pool_timeout
    print("PoolTimeout:", "QueuePool limit of size 2 overflow 1 reached" in str(exc))  # message check
# Output: PoolTimeout: True

held.pop().close()  # return one connection to the pool
with engine.connect() as conn:  # now a request succeeds again
    print(conn.execute(text("SELECT 42")).scalar_one())  # query runs
# Output: 42

for c in held:  # clean up: ALWAYS return connections
    c.close()  # back to the pool
print(engine.pool.checkedout())  # nothing leaked
# Output: 0
engine.dispose()  # close all pooled connections at shutdown
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (SQLAlchemy): the engine owns the pool
engine = create_engine("postgresql+psycopg://user:pw@db/app", pool_size=10, max_overflow=5)
with engine.connect() as conn:       # borrow
    conn.execute(text("SELECT 1"))   # returned automatically on exit
```
```javascript
// JavaScript (node-postgres): Pool is the same idea
import pg from 'pg';
const pool = new pg.Pool({ connectionString: 'postgres://user:pw@db/app', max: 10 });
const res = await pool.query('SELECT 1');      // borrows and returns a client automatically
const client = await pool.connect();           // manual borrow
try { await client.query('SELECT 1'); } finally { client.release(); }   // MUST release
```

Key differences: the concept is identical. `pool.query()` in node-postgres and `with engine.connect()` in SQLAlchemy both return the connection automatically; the manual forms (`pool.connect()` / `engine.connect()` without `with`) need an explicit `release()` / `close()` or the pool leaks.

---

## 🟠 FastAPI Connection
Create the engine once for the whole app (module level or in `lifespan`), and create one short-lived session per request with a `Depends` generator that always calls `db.close()`. Remember pools are per process: total connections = workers x (pool_size + max_overflow), and this must stay below the database's `max_connections`. Do not use a pool with serverless platforms; use a pooler (PgBouncer, RDS Proxy) or `NullPool`.

```python
# FastAPI: one engine per app (created once), one short-lived session per request (pip install fastapi sqlalchemy httpx)
import os
import tempfile
from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterator

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

DB_PATH: str = os.path.join(tempfile.mkdtemp(), "app.db")  # demo database file
engine = create_engine(f"sqlite:///{DB_PATH}", pool_size=5, max_overflow=5, pool_pre_ping=True)  # created ONCE at import time
SessionLocal: sessionmaker[Session] = sessionmaker(engine, expire_on_commit=False)  # session factory


@asynccontextmanager  # app lifespan
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield  # serve requests
    engine.dispose()  # close the pool on shutdown


app: FastAPI = FastAPI(lifespan=lifespan)  # create app


def get_db() -> Iterator[Session]:  # dependency
    db: Session = SessionLocal()  # borrows a connection lazily on first query
    try:
        yield db  # endpoint uses it
    finally:
        db.close()  # ALWAYS returns the connection to the pool, even on errors


@app.get("/ping-db")  # GET /ping-db
def ping_db(db: Session = Depends(get_db)) -> dict[str, int]:  # sync def -> threadpool
    return {"value": db.execute(text("SELECT 1")).scalar_one(), "checked_out": engine.pool.checkedout()}  # 1 in use


with TestClient(app) as client:  # run lifespan
    print(client.get("/ping-db").json())  # the request holds one connection
    # Output: {'value': 1, 'checked_out': 1}
    print(engine.pool.checkedout())  # returned after the request ended
    # Output: 0
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating a new engine (and pool) per request
```python
# Wrong - every request builds a fresh pool and connection:
def handler():
    engine = create_engine(URL)
    with engine.connect() as c: ...

# Correct - one global engine, reused:
engine = create_engine(URL)
```

❌ Mistake 2: Not returning connections (leaks)
```python
# Wrong - the connection is never returned, the pool drains and requests time out:
conn = engine.connect()
conn.execute(text("SELECT 1"))

# Correct - context manager (or try/finally):
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
```

❌ Mistake 3: Pool size x workers exceeds the database limit
```python
# Wrong - 16 workers x (20 + 10) = 480 connections against max_connections=100:
create_engine(URL, pool_size=20, max_overflow=10)

# Correct - size for the total: 16 workers x (4 + 2) = 96, or put PgBouncer in front
create_engine(URL, pool_size=4, max_overflow=2)
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print?

```python
engine = create_engine(f"sqlite:///{path}", pool_size=1, max_overflow=0, pool_timeout=0.2)
c1 = engine.connect()
try:
    engine.connect()
except Exception as e:
    print(type(e).__name__)
c1.close()
with engine.connect() as c2:
    print(c2.execute(text("SELECT 7")).scalar())
print(engine.pool.checkedout())
```

**Answer**:
```
TimeoutError
7
0
```
With one connection allowed and no overflow, the second `connect()` waits 0.2 s and raises `sqlalchemy.exc.TimeoutError` (not the built-in `TimeoutError`). After `c1.close()` the connection returns to the pool, so the next `connect()` works, and after the `with` block nothing is checked out. `close()` on a pooled connection does not close the socket; it returns it to the pool.

---

## ⚫ Interview Questions + Answers

Q1: Why use a connection pool?
A1: Opening a connection is slow and expensive for the database. A pool reuses connections, cuts latency, limits the number of connections, and queues requests during spikes instead of crashing the database.

Q2: What do `pool_size`, `max_overflow`, `pool_timeout` mean?
A2: `pool_size` is the number of connections kept open. `max_overflow` is how many extra temporary connections are allowed beyond it. `pool_timeout` is how long a request waits for a free connection before raising an error.

Q3: What is `pool_pre_ping` and `pool_recycle`?
A3: `pool_pre_ping=True` issues a cheap test before handing out a connection and replaces it if the database closed it (after restarts or idle timeouts). `pool_recycle=N` closes connections older than N seconds to avoid server-side or firewall timeouts.

Q4: Is a pool shared across worker processes?
A4: No. Each process (gunicorn worker, Celery worker) has its own pool; after `fork`, create engines in the child or call `engine.dispose()`. Use PgBouncer for a pool shared by all processes.

Q5: What are symptoms of a connection leak?
A5: Requests hang and then raise `QueuePool limit ... reached, connection timed out`, while the database shows many idle connections. Fix by always using `with` blocks / `finally: close()` and by checking `engine.pool.status()`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A server handles many short database requests (almost every web API)
- Opening a connection is expensive (TLS, remote database)
- You must cap total connections to the database

❌ Avoid when:
- Short-lived scripts or serverless functions (use NullPool or an external pooler)
- You use SQLite `:memory:` in tests (a single connection is enough)
- A transaction pooler is already in front and you do not need a second large pool

---

## 📊 Visual Diagram

```
Requests            Pool (pool_size=2, max_overflow=1)        Database
 req A ──borrow──►  [conn1] ──────────────────────────────►
 req B ──borrow──►  [conn2] ──────────────────────────────►   few long-lived
 req C ──borrow──►  [conn3 overflow] ─────────────────────►   connections
 req D ──wait...──► (limit reached) → TimeoutError after pool_timeout
 req A ──return──►  [conn1] stays open, ready for the next request
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Connection pool | Reusable set of open connections | खुले connections का पुन: उपयोगी समूह |
| pool_size | Connections kept open | खुले रखे जाने वाले connections |
| max_overflow | Extra temporary connections | अतिरिक्त अस्थायी connections |
| pool_pre_ping | Test connection before use | उपयोग से पहले connection की जाँच |
| Leak | Connection borrowed but never returned | उधार लिया पर वापस नहीं किया |
| PgBouncer | External PostgreSQL connection pooler | बाहरी PostgreSQL pooler |

---

## ⚡ 3-Line Summary
English: A connection pool reuses open database connections so requests skip the slow connect step and the database sees a bounded number of connections. Create one engine per app, always return connections with `with`/`finally`, and size pools as workers x (pool_size + overflow). Use `pool_pre_ping` and a pooler like PgBouncer in production.
Hindi: Connection pool खुले database connections को दोबारा इस्तेमाल करता है, इसलिए requests को धीमा connect step नहीं करना पड़ता और database पर connections की संख्या सीमित रहती है। App में एक ही engine रखें, connections को हमेशा `with`/`finally` से लौटाएँ और pool का आकार workers x (pool_size + overflow) से तय करें। Production में `pool_pre_ping` और PgBouncer रखें।

---

## ➡️ Next Topic
**418. Lazy Evaluation** — compute values only when needed, which saves memory and time.
