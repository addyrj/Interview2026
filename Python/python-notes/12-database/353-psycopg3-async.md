---

# 353. psycopg3 (async)
# हिंदी में: psycopg3 (async PostgreSQL driver)

---

## 🔵 Simple Definition (English)
`psycopg` (version 3) is the modern PostgreSQL driver for Python. It has a real async API (`AsyncConnection`, `AsyncCursor`) so your FastAPI endpoint does not block the event loop while waiting for the database. Package name: `psycopg`, import name: `psycopg`.

## 🔵 सरल परिभाषा (Hindi)
`psycopg` (version 3) Python का modern PostgreSQL driver है। इसमें असली async API (`AsyncConnection`, `AsyncCursor`) है, इसलिए database का इंतज़ार करते समय FastAPI का event loop block नहीं होता। Install: `pip install "psycopg[binary,pool]"`, import: `psycopg`।

---

## 🔴 Problem it Solves
`psycopg2` is synchronous. In an `async def` endpoint a slow query freezes the whole event loop, so other requests wait. Psycopg 3 adds native async, server-side parameter binding, `COPY` support, typed row factories and a connection pool package (`psycopg_pool`).

## 🔴 यह क्यों बना? (Hindi)
`psycopg2` synchronous है। `async def` endpoint में धीमी query पूरे event loop को रोक देती है, बाकी requests इंतज़ार करती हैं। Psycopg 3 में native async, server-side parameter binding, `COPY`, typed row factories और pool (`psycopg_pool`) मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → await psycopg.AsyncConnection.connect(conninfo)   (opens a socket, non-blocking)
Step 2 → async with conn.cursor() as cur                    (create a cursor)
Step 3 → await cur.execute("... %s ...", (value,))          (server binds the value, no SQL injection)
Step 4 → await cur.fetchall() / fetchone()                  (rows come back as tuples or dicts)
Step 5 → async with conn: commits on success, rolls back on error, then closes
Step 6 → In production use AsyncConnectionPool and borrow with `async with pool.connection()`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → await AsyncConnection.connect(...) से non-blocking connection खुलता है
Step 2 → cursor बनाओ: async with conn.cursor() as cur
Step 3 → await cur.execute(sql, params): values server bind करता है, इसलिए SQL injection नहीं
Step 4 → await cur.fetchall() / fetchone() से rows मिलती हैं
Step 5 → async with conn: सफल होने पर commit, error पर rollback
Step 6 → Production में AsyncConnectionPool से connection उधार लो
```

---

## 🟡 Real World Example
Swiggy-style order service: each `POST /orders` inserts the order and its items in one transaction. With `AsyncConnectionPool` of 10 connections, 500 concurrent requests share them without blocking the event loop. Razorpay-style ledgers use `async with conn.transaction()` so debit and credit commit together or not at all.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service में हर `POST /orders` order और items को एक transaction में insert करता है। 10 connections के `AsyncConnectionPool` से 500 concurrent requests बिना event loop block किए चलती हैं। Razorpay जैसे ledger में `async with conn.transaction()` से debit और credit साथ में commit होते हैं या बिल्कुल नहीं।

---

## 💻 Code Example — Basic
```python
# NOT RUN here: needs a live PostgreSQL server (no Postgres installed in the test environment).
# The syntax and the offline pieces (sql composition, error classes) WERE checked.
# Install: pip install "psycopg[binary]"
import asyncio  # to run the async main
from typing import Any, List, Tuple  # type hints

import psycopg  # the driver

DSN: str = "host=127.0.0.1 port=5432 dbname=shop user=app password=secret"  # connection string


async def main() -> None:
    # async with: opens the connection, commits at the end, closes always
    async with await psycopg.AsyncConnection.connect(DSN) as conn:
        # cursor is also an async context manager
        async with conn.cursor() as cur:
            await cur.execute(  # run DDL
                "CREATE TABLE IF NOT EXISTS orders ("
                "id SERIAL PRIMARY KEY, customer TEXT NOT NULL, amount NUMERIC(10,2) NOT NULL)"
            )
            # %s is a placeholder for ANY type (even for ints), never use f-strings
            await cur.execute(
                "INSERT INTO orders (customer, amount) VALUES (%s, %s) RETURNING id",
                ("Aarav", 499.50),
            )
            new_id: Tuple[Any, ...] | None = await cur.fetchone()  # RETURNING gives the id
            print("new id:", new_id)  # Output: new id: (1,)  (value depends on the table)

            await cur.executemany(  # many rows, one call
                "INSERT INTO orders (customer, amount) VALUES (%s, %s)",
                [("Diya", 250), ("Kabir", 1200.75)],
            )
            await cur.execute("SELECT id, customer, amount FROM orders WHERE amount > %s", (300,))
            rows: List[Tuple[Any, ...]] = await cur.fetchall()  # list of tuples
            print(rows)  # Output: [(1, 'Aarav', Decimal('499.50')), (3, 'Kabir', Decimal('1200.75'))]
    # leaving the outer `async with` committed the transaction


asyncio.run(main())  # start the event loop
```

## 💻 Code Example — Advanced
```python
# NOT RUN against a database (no Postgres here). Checked: ast.parse + sql.Composed output + OperationalError path.
# Install: pip install "psycopg[binary]" psycopg_pool
import asyncio  # event loop
from decimal import Decimal  # money type
from typing import Any, Dict, List

import psycopg  # driver
from psycopg import sql  # safe dynamic identifiers
from psycopg.rows import dict_row  # rows as dicts
from psycopg_pool import AsyncConnectionPool  # async pool

DSN: str = "host=127.0.0.1 port=5432 dbname=shop user=app password=secret"

# open=False + explicit open() avoids the deprecated "open in constructor" behaviour
pool: AsyncConnectionPool = AsyncConnectionPool(
    DSN, min_size=2, max_size=10, open=False, kwargs={"row_factory": dict_row}
)


async def transfer(src: int, dst: int, amount: Decimal) -> None:
    """Move money atomically between two wallets."""
    async with pool.connection() as conn:  # borrow a connection, returned automatically
        async with conn.transaction():  # BEGIN ... COMMIT, ROLLBACK on exception
            cur = await conn.execute(  # conn.execute is a shortcut that creates a cursor
                "UPDATE wallets SET balance = balance - %s WHERE id = %s AND balance >= %s",
                (amount, src, amount),
            )
            if cur.rowcount != 1:  # nothing updated -> not enough money
                raise ValueError("insufficient funds")  # triggers ROLLBACK
            await conn.execute(
                "UPDATE wallets SET balance = balance + %s WHERE id = %s", (amount, dst)
            )


async def list_rows(table: str, limit: int) -> List[Dict[str, Any]]:
    """Dynamic table name: values use %s, identifiers use sql.Identifier."""
    query: sql.Composed = sql.SQL("SELECT * FROM {} ORDER BY id LIMIT {}").format(
        sql.Identifier(table), sql.Placeholder()  # quotes the name safely
    )
    async with pool.connection() as conn:
        cur = await conn.execute(query, (limit,))
        return await cur.fetchall()  # list of dicts because of dict_row


async def main() -> None:
    await pool.open()  # create the min_size connections
    try:
        await transfer(1, 2, Decimal("300"))  # may raise ValueError / psycopg.Error
        print(await list_rows("wallets", 10))
    except psycopg.errors.UniqueViolation:  # specific SQLSTATE class
        print("duplicate")
    except psycopg.OperationalError as exc:  # connection / server down
        print("db down:", exc)
    finally:
        await pool.close()  # close all connections


# Verified offline:
print(sql.SQL("SELECT {} FROM {} WHERE id = {}").format(
    sql.Identifier("name"), sql.Identifier("users"), sql.Placeholder()).as_string(None))
# Output: SELECT "name" FROM "users" WHERE id = %s

if __name__ == "__main__":
    asyncio.run(main())  # needs a real database
```

---

## 🟠 JavaScript vs Python Comparison
`psycopg` plays the role of `pg` (node-postgres) in Node.js.

```python
# Python: psycopg 3 async
async with pool.connection() as conn:
    cur = await conn.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    row = await cur.fetchone()
```
```javascript
// JavaScript: node-postgres
const { Pool } = require("pg");
const pool = new Pool({ connectionString });
const { rows } = await pool.query("SELECT * FROM users WHERE id = $1", [userId]);
```

Key differences: node-postgres uses `$1, $2` placeholders; psycopg uses `%s` (or `%(name)s`) and the parameters are always a separate tuple/dict. In Python you use `async with` for pool/connection/transaction scoping, while in JS you call `client.release()` manually.

---

## 🟠 FastAPI Connection
Create one pool at startup with `lifespan`, close it at shutdown, and give each request a connection through a dependency.

```python
# FastAPI + psycopg pool (needs a running PostgreSQL; not run here)
from contextlib import asynccontextmanager  # lifespan helper
from typing import Any, AsyncIterator, Dict
from fastapi import Depends, FastAPI, HTTPException  # web
from psycopg import AsyncConnection  # connection type
from psycopg.rows import dict_row  # dict rows
from psycopg_pool import AsyncConnectionPool  # pool

pool = AsyncConnectionPool("dbname=shop user=app", open=False, kwargs={"row_factory": dict_row})


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    await pool.open()  # startup
    yield  # app runs
    await pool.close()  # shutdown


app = FastAPI(lifespan=lifespan)  # register lifespan


async def get_conn() -> AsyncIterator[AsyncConnection[Any]]:
    async with pool.connection() as conn:  # one connection per request
        yield conn  # given to the endpoint


@app.get("/orders/{order_id}")
async def get_order(order_id: int, conn: AsyncConnection[Any] = Depends(get_conn)) -> Dict[str, Any]:
    cur = await conn.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    row = await cur.fetchone()  # dict or None
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    return row
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building SQL with f-strings (SQL injection)
```python
# Wrong
await cur.execute(f"SELECT * FROM users WHERE name = '{name}'")

# Right: placeholders (identifiers: use psycopg.sql.Identifier)
await cur.execute("SELECT * FROM users WHERE name = %s", (name,))
```

❌ Mistake 2: Single value not passed as a tuple
```python
# Wrong: "abc" is treated as 3 parameters -> ProgrammingError
await cur.execute("SELECT * FROM t WHERE x = %s", ("abc"))

# Right: trailing comma makes a 1-tuple
await cur.execute("SELECT * FROM t WHERE x = %s", ("abc",))
```

❌ Mistake 3: Forgetting to await, or using a sync connection in async code
```python
# Wrong: coroutine never runs, no result
cur.execute("SELECT 1")

# Right
await cur.execute("SELECT 1")
```

❌ Mistake 4: Opening a new connection for every request
```python
# Wrong: slow (TCP + auth each time), can exhaust max_connections
async with await psycopg.AsyncConnection.connect(DSN) as conn: ...

# Right: one AsyncConnectionPool for the whole app
async with pool.connection() as conn: ...
```

---

## 🧠 Tricky Interview Question

**Q**: A literal `%` is needed in the SQL (`LIKE 'a%'`). What goes wrong, and what is the fix?

```python
await cur.execute("SELECT * FROM users WHERE name LIKE 'a%'")            # (1) no params
await cur.execute("SELECT * FROM users WHERE name LIKE 'a%' AND id = %s", (1,))  # (2)
await cur.execute("SELECT * FROM users WHERE name LIKE %s", ("a%",))     # (3)
```

**Answer**: (1) works because when no parameters are given psycopg does not parse `%`. (2) raises `ProgrammingError` because `%'` is read as a bad placeholder; write `'a%%'` when parameters are present. (3) is the best style: put the pattern in the parameter. Also remember `async with conn` commits when the block ends, but a plain `await conn.close()` without commit rolls back uncommitted work.

---

## ⚫ Interview Questions + Answers

Q1: psycopg2 vs psycopg3?
A1: psycopg3 (package `psycopg`) has native async, server-side binding, `COPY` via `cursor.copy()`, pipeline mode and `psycopg_pool`. psycopg2 is sync and in maintenance mode.

Q2: Is `%s` string formatting?
A2: No. It is a placeholder. By default psycopg 3 sends SQL and values separately (server-side binding), so values cannot change the SQL structure.

Q3: How do you make a transaction?
A3: `async with conn.transaction():` (savepoints if nested), or rely on `async with conn:` which commits at the end. By default psycopg opens a transaction on the first query (autocommit is off).

Q4: How to get dict rows?
A4: Pass `row_factory=dict_row` to `connect()` or the cursor. Other factories: `namedtuple_row`, `class_row(MyModel)` which fits Pydantic/dataclasses.

Q5: Why a pool?
A5: Opening a Postgres connection is expensive and the server has a connection limit. A pool reuses connections and queues extra requests.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You use PostgreSQL directly with raw SQL (high performance, full control)
- You need async in FastAPI without an ORM
- You need `COPY` for bulk loading or `LISTEN/NOTIFY`

❌ Avoid when:
- You want an ORM and migrations (use SQLAlchemy with the `postgresql+psycopg` async dialect)
- Your database is MySQL/SQLite (different drivers)

---

## 📊 Visual Diagram

```
FastAPI request ──► Depends(get_conn)
                        │
              AsyncConnectionPool (min 2, max 10)
              ┌─────┬─────┬─────┬─────┐
              │ c1  │ c2  │ ... │ c10 │  ── sockets ──► PostgreSQL
              └─────┴─────┴─────┴─────┘
 free connection? yes -> use it | no -> wait in queue (timeout 30s)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Driver | Library that talks to a DB | database से बात करने वाली library |
| Placeholder `%s` | Safe slot for a value | value के लिए सुरक्षित जगह |
| Transaction | All-or-nothing group of queries | सब या कुछ नहीं वाला group |
| Pool | Reusable connections | दोबारा इस्तेमाल होने वाले connections |
| row_factory | Controls the row type | row किस रूप में मिले |
| SQLSTATE | Standard error code | मानक error code |

---

## ⚡ 3-Line Summary
English: psycopg 3 is the modern async PostgreSQL driver. Use `%s` placeholders, `async with` for transactions and `AsyncConnectionPool` for production. Never build SQL with f-strings.
Hindi: psycopg 3 modern async PostgreSQL driver है। `%s` placeholders, transactions के लिए `async with` और production में `AsyncConnectionPool` इस्तेमाल करें। SQL को कभी f-string से न बनाएँ।

---

## ➡️ Next Topic
**354. mysql-connector-python** — the official Oracle driver for MySQL.
