---

# 248. asyncpg — Async PostgreSQL
# हिंदी में: asyncpg — Async PostgreSQL Driver

---

## 🔵 Simple Definition (English)
`asyncpg` is a fast, async-only driver that talks to PostgreSQL directly using its binary protocol. You `await` every query, so the event loop stays free while the database works. It has built-in connection pools and transactions.

## 🔵 सरल परिभाषा (Hindi)
`asyncpg` एक तेज़, सिर्फ async driver है जो PostgreSQL से सीधे उसके binary protocol में बात करता है। हर query पर `await` लगता है, इसलिए database के काम करते समय event loop खाली रहता है। इसमें connection pool और transactions पहले से मौजूद हैं।

---

## 🔴 Problem it Solves
`psycopg2` is blocking. In an async web app, one slow SQL query would freeze every other request. Opening a new database connection per request is also expensive (TCP + auth). `asyncpg` makes queries awaitable and gives a pool, so many requests share a few open connections.

## 🔴 यह क्यों बना? (Hindi)
`psycopg2` blocking है। Async web app में एक धीमी SQL query बाकी सारी requests को रोक देती है। हर request पर नया database connection खोलना भी महंगा है (TCP + auth)। `asyncpg` queries को awaitable बनाता है और pool देता है, जिससे कई requests कुछ ही खुले connections share करती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → create_pool(dsn) opens min_size connections at startup
Step 2 → pool.acquire() borrows one free connection (or waits)
Step 3 → await conn.fetch(sql, *args) sends the query with $1, $2 placeholders
Step 4 → Postgres runs it; the event loop serves other tasks meanwhile
Step 5 → Rows come back as asyncpg.Record objects (dict-like)
Step 6 → async with conn.transaction(): -> COMMIT on success, ROLLBACK on error
Step 7 → Leaving "async with pool.acquire()" returns the connection to the pool
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → create_pool(dsn) startup पर min_size connections खोलता है
Step 2 → pool.acquire() एक खाली connection उधार लेता है (या इंतजार करता है)
Step 3 → await conn.fetch(sql, *args) query भेजता है, placeholders $1, $2 वाले
Step 4 → Postgres चलाता है; इस बीच event loop दूसरे tasks चलाता है
Step 5 → Rows asyncpg.Record objects (dict जैसे) में आती हैं
Step 6 → async with conn.transaction(): -> सफल हो तो COMMIT, error पर ROLLBACK
Step 7 → "async with pool.acquire()" खत्म होने पर connection pool में लौट जाता है
```

---

## 🟡 Real World Example
A food-delivery backend (Swiggy-style) stores orders in PostgreSQL. Each API call reads the restaurant, inserts the order and decrements stock. With `asyncpg` and a pool of 10-20 connections, a single FastAPI process handles thousands of requests per second because no request blocks while waiting for the database. Money movement (wallet debit + order insert) runs inside one transaction so both succeed or both roll back.

## 🟡 Real Example Hindi mein
Food-delivery backend (Swiggy जैसा) orders PostgreSQL में रखता है। हर API call restaurant पढ़ती है, order insert करती है और stock घटाती है। `asyncpg` और 10-20 connections के pool से एक FastAPI process हजारों requests प्रति सेकंड संभालता है, क्योंकि database का इंतजार करते समय कोई request अटकती नहीं। पैसे का लेन-देन (wallet debit + order insert) एक transaction में होता है ताकि दोनों साथ सफल हों या दोनों वापस हों।

---

## 💻 Code Example — Basic
```python
# Basic asyncpg usage
# NOT RUN in this repo's verification: needs a real PostgreSQL server.
# (Only verified: the code parses, and a refused connection raises ConnectionRefusedError.)
# pip install asyncpg
import asyncio                                           # event loop
import asyncpg                                           # async Postgres driver


async def main() -> None:
    conn: asyncpg.Connection = await asyncpg.connect(    # open ONE connection
        "postgresql://user:pass@localhost:5432/shop"     # dsn: user, password, host, db
    )
    try:
        await conn.execute(                              # run a statement, no rows back
            "CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, name text, age int)"
        )
        await conn.execute(                              # $1, $2 = safe parameters
            "INSERT INTO users (name, age) VALUES ($1, $2)", "Asha", 25
        )
        rows: list[asyncpg.Record] = await conn.fetch(   # many rows
            "SELECT id, name FROM users WHERE age > $1", 20
        )
        for r in rows:                                   # Record works like a dict
            print(r["id"], r["name"])                    # e.g. 1 Asha
        one = await conn.fetchrow("SELECT * FROM users WHERE id = $1", 1)   # one row or None
        count: int = await conn.fetchval("SELECT count(*) FROM users")      # one value
        print(dict(one) if one else None, count)         # dict(Record) -> plain dict
    finally:
        await conn.close()                               # always close


asyncio.run(main())                                      # run

# Expected output (not executed here; ids depend on the table):
# 1 Asha
# {'id': 1, 'name': 'Asha', 'age': 25} 1
```

## 💻 Code Example — Advanced
```python
# Production style: pool, transaction, error handling, executemany
# NOT RUN: requires PostgreSQL. Parsed with ast only.
import asyncio                                           # event loop
from typing import Any                                   # type hints
import asyncpg                                           # driver


async def transfer(pool: asyncpg.Pool, src: int, dst: int, amount: int) -> None:
    async with pool.acquire() as conn:                   # borrow a connection
        async with conn.transaction():                   # BEGIN ... COMMIT / ROLLBACK
            bal: int | None = await conn.fetchval(       # lock the row so nobody else edits it
                "SELECT balance FROM wallets WHERE id = $1 FOR UPDATE", src
            )
            if bal is None or bal < amount:              # validate inside the transaction
                raise ValueError("insufficient balance") # raising triggers ROLLBACK
            await conn.execute("UPDATE wallets SET balance = balance - $1 WHERE id = $2", amount, src)
            await conn.execute("UPDATE wallets SET balance = balance + $1 WHERE id = $2", amount, dst)


async def add_users(pool: asyncpg.Pool, users: list[tuple[str, int]]) -> int:
    async with pool.acquire() as conn:                   # borrow connection
        try:
            await conn.executemany(                      # one prepared statement, many rows
                "INSERT INTO users (name, age) VALUES ($1, $2)", users
            )
            return len(users)                            # how many we tried to insert
        except asyncpg.UniqueViolationError:             # specific Postgres error class
            return 0                                     # duplicate -> nothing saved (all-or-nothing)


async def main() -> None:
    pool: asyncpg.Pool = await asyncpg.create_pool(      # create the pool ONCE
        dsn="postgresql://user:pass@localhost:5432/shop",
        min_size=2, max_size=10,                         # keep 2..10 connections
        command_timeout=10,                              # any query > 10 s raises
    )
    try:
        print(await add_users(pool, [("Ravi", 30), ("Meena", 28)]))   # 2
        try:
            await transfer(pool, 1, 2, 500)              # money transfer
        except ValueError as e:                          # business-rule error
            print("transfer failed:", e)                 # rolled back automatically
    finally:
        await pool.close()                               # graceful shutdown


asyncio.run(main())                                      # run
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (asyncpg) | JavaScript (node-postgres `pg`) |
|---------|------------------|--------------------------------|
| Pool | `asyncpg.create_pool()` | `new Pool()` |
| Placeholders | `$1, $2` | `$1, $2` (same!) |
| Query many rows | `await conn.fetch()` | `await pool.query()` -> `.rows` |
| One row | `fetchrow()` | `rows[0]` |
| One value | `fetchval()` | `rows[0].count` |
| Transaction | `async with conn.transaction()` | manual `BEGIN`/`COMMIT` |

```python
# Python way
rows = await conn.fetch("SELECT * FROM users WHERE age > $1", 20)   # rows list
```
```javascript
// JavaScript way (pg)
const { rows } = await pool.query("SELECT * FROM users WHERE age > $1", [20]);   // rows array
```

Key difference: parameters are passed as separate arguments in asyncpg (`..., 20`) while `pg` takes an array. Also asyncpg has a built-in transaction context manager, and Postgres types convert automatically (jsonb, arrays, uuid, timestamp -> Python types).

---

## 🟠 FastAPI Connection
Create the pool in `lifespan`, store it on `app.state`, and fetch it in endpoints via a dependency.

```python
# FastAPI example — pool in lifespan + dependency
# NOT RUN: needs PostgreSQL
from contextlib import asynccontextmanager               # lifespan helper
from collections.abc import AsyncIterator                # type
import asyncpg                                           # driver
from fastapi import Depends, FastAPI, HTTPException, Request   # FastAPI parts


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.pool = await asyncpg.create_pool(dsn="postgresql://user:pass@localhost/shop")   # startup
    yield                                                # serve requests
    await app.state.pool.close()                         # shutdown


app: FastAPI = FastAPI(lifespan=lifespan)                # attach


async def get_conn(request: Request) -> AsyncIterator[asyncpg.Connection]:
    async with request.app.state.pool.acquire() as conn: # borrow per request
        yield conn                                       # released after the response


@app.get("/users/{user_id}")                             # GET /users/1
async def read_user(user_id: int, conn: asyncpg.Connection = Depends(get_conn)) -> dict:
    row = await conn.fetchrow("SELECT id, name FROM users WHERE id = $1", user_id)   # query
    if row is None:                                      # not found
        raise HTTPException(404, "user not found")       # 404 reply
    return dict(row)                                     # Record -> dict -> JSON
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building SQL with f-strings (SQL injection)
✅ Correct: use `$1` placeholders

```python
# Wrong — attacker sends  name = "x'; DROP TABLE users; --"
await conn.fetch(f"SELECT * FROM users WHERE name = '{name}'")
# Right
await conn.fetch("SELECT * FROM users WHERE name = $1", name)
```

❌ Mistake 2: One shared `Connection` used by many tasks at once
✅ Correct: a connection runs one operation at a time. Use a pool and `acquire()` per task (otherwise `InterfaceError: another operation is in progress`)

```python
# Wrong
await asyncio.gather(conn.fetch("SELECT 1"), conn.fetch("SELECT 2"))
# Right
async def q(sql: str):
    async with pool.acquire() as c:
        return await c.fetch(sql)
await asyncio.gather(q("SELECT 1"), q("SELECT 2"))
```

❌ Mistake 3: Using `%s` or `?` placeholders
✅ Correct: asyncpg only understands `$1, $2, ...`

```python
# Wrong (psycopg2 style)
await conn.fetch("SELECT * FROM users WHERE id = %s", 1)
# Right
await conn.fetch("SELECT * FROM users WHERE id = $1", 1)
```

---

## 🧠 Tricky Interview Question

```python
# Does the INSERT survive? What is printed?
async def f(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        try:
            async with conn.transaction():
                await conn.execute("INSERT INTO t VALUES (1)")
                raise RuntimeError("oops")
        except RuntimeError:
            print("caught")
        print(await conn.fetchval("SELECT count(*) FROM t WHERE id = 1"))
```
Answer: It prints `caught`, then `0`. The exception leaves the `async with conn.transaction()` block, so asyncpg issues ROLLBACK before the exception reaches your `except`. The row was never committed. (Without the transaction block, asyncpg runs each `execute` in autocommit mode and the row WOULD stay.)

---

## ⚫ Interview Questions + Answers

Q1: Why is asyncpg faster than psycopg2/SQLAlchemy+psycopg2?
A1: It implements the PostgreSQL binary protocol directly in Cython, avoids libpq, and decodes values straight into Python types. It is typically several times faster in benchmarks. It is also natively async.

Q2: What does `fetch`, `fetchrow`, `fetchval`, `execute` return?
A2: `fetch` -> list of Records; `fetchrow` -> one Record or `None`; `fetchval` -> first column of first row; `execute` -> status string like `'INSERT 0 1'`.

Q3: How big should the pool be?
A3: Start small (10-20 per process). Postgres has a hard `max_connections` (default 100), and total = pool size x number of app processes. Use PgBouncer when you have many workers.

Q4: What is the difference between asyncpg and SQLAlchemy async?
A4: asyncpg is a raw driver (you write SQL). SQLAlchemy async (`create_async_engine("postgresql+asyncpg://...")`) adds ORM and query building and can use asyncpg underneath.

Q5: How do you handle `jsonb` columns?
A5: By default asyncpg returns `jsonb` as a string. Register a codec with `conn.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")` (or use the `init=` callback of the pool).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Async app (FastAPI, aiohttp) with PostgreSQL
- High throughput, performance-sensitive services
- You are comfortable writing SQL directly

❌ Avoid when:
- Your database is MySQL/SQLite (use aiomysql / aiosqlite)
- You need an ORM with migrations (use SQLAlchemy / SQLModel on top)
- A sync script or Django app (use psycopg)

---

## 📊 Visual Diagram
```
 FastAPI requests (many)
   │  │  │  │
   ▼  ▼  ▼  ▼
 ┌─────────────────┐
 │  asyncpg Pool   │  min_size=2 ... max_size=10
 │ [c1][c2][c3]... │
 └────────┬────────┘
          │ binary protocol
          ▼
     PostgreSQL

 async with pool.acquire() as conn:      # borrow
     async with conn.transaction():      # BEGIN
         await conn.execute(...)         # work
                                         # COMMIT (or ROLLBACK on error)
                                         # connection returned
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Pool | Reusable set of open connections | खुले connections का समूह |
| Record | Row object, dict-like | Row का object, dict जैसा |
| Transaction | All-or-nothing group of queries | सब या कुछ नहीं वाला query समूह |
| Prepared statement | Query parsed once, run many times | एक बार parse, कई बार चलने वाली query |
| DSN | Connection URL string | Connection का URL |
| Placeholder `$1` | Safe slot for a value | Value के लिए सुरक्षित जगह |

---

## ⚡ 3-Line Summary
English: `asyncpg` is the fastest async PostgreSQL driver. Create one pool at startup, borrow a connection per request, use `$1` placeholders and `conn.transaction()` for safety.
Hindi: `asyncpg` सबसे तेज़ async PostgreSQL driver है। Startup पर एक pool बनाएं, हर request पर एक connection उधार लें, सुरक्षा के लिए `$1` placeholders और `conn.transaction()` इस्तेमाल करें।

---

## ➡️ Next Topic
**249. motor — Async MongoDB** — the async MongoDB driver: collections, queries and cursors with `await`.
