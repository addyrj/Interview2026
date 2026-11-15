---

# 352. psycopg2 — PostgreSQL
# हिंदी में: psycopg2 — PostgreSQL का classic Python driver

---

## 🔵 Simple Definition (English)
`psycopg2` is the most widely used synchronous PostgreSQL driver for Python. It follows DB-API: you `connect()`, make a `cursor()`, run `execute()` with `%s` placeholders, `fetch` rows and `commit()`. It is a C library wrapper, fast and stable, and it is what many older Django and Flask projects still use.

## 🔵 सरल परिभाषा (Hindi)
`psycopg2` Python के लिए सबसे ज़्यादा इस्तेमाल होने वाला synchronous PostgreSQL driver है। यह DB-API मानता है: `connect()`, `cursor()`, `%s` placeholders के साथ `execute()`, `fetch` और `commit()`। यह C library का wrapper है, तेज़ और स्थिर, और कई पुराने Django व Flask projects आज भी इसी पर चलते हैं।

---

## 🔴 Problem it Solves
Python cannot talk to PostgreSQL's binary protocol on its own. psycopg2 handles the connection, type conversion (Python `datetime`, `Decimal`, `list`, `dict` to Postgres types and back), safe parameter passing, transactions and errors with the right exception class (e.g. `UniqueViolation`).

## 🔴 यह क्यों बना? (Hindi)
Python खुद PostgreSQL के binary protocol से बात नहीं कर सकता। psycopg2 connection, type conversion (Python `datetime`, `Decimal`, `list`, `dict` से Postgres types और वापस), सुरक्षित parameter passing, transactions और सही exception class (जैसे `UniqueViolation`) संभालता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install psycopg2-binary          (dev; production often builds psycopg2 from source)
Step 2 → conn = psycopg2.connect(host=..., dbname=..., user=..., password=...)
Step 3 → A transaction starts automatically at your first execute()
Step 4 → with conn.cursor() as cur: cur.execute("... %s ...", (value,))
Step 5 → cur.fetchone() / fetchall() / iterate over cur
Step 6 → conn.commit() to save, conn.rollback() to undo
Step 7 → If a statement fails, the transaction is "aborted": you MUST rollback() before the next query
Step 8 → conn.close() when done (or return it to a pool)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install psycopg2-binary          (dev के लिए; production में अक्सर source से build)
Step 2 → conn = psycopg2.connect(host=..., dbname=..., user=..., password=...)
Step 3 → पहले execute() पर transaction अपने-आप शुरू हो जाता है
Step 4 → with conn.cursor() as cur: cur.execute("... %s ...", (value,))
Step 5 → cur.fetchone() / fetchall() / cur पर loop
Step 6 → सेव करने के लिए conn.commit(), वापस करने के लिए conn.rollback()
Step 7 → कोई statement fail हो तो transaction "aborted" हो जाता है: अगली query से पहले rollback() ज़रूरी
Step 8 → काम खत्म होने पर conn.close() (या pool को लौटाएँ)
```

---

## 🟡 Real World Example
A nightly reporting job for a Zerodha-like platform reads 5 million trades with a server-side (named) cursor, so memory stays flat, and bulk-inserts the summary rows with `execute_values`. A Flask admin tool keeps a `ThreadedConnectionPool` and checks out one connection per request.

## 🟡 Real Example Hindi mein
Zerodha जैसे platform का रात का reporting job 50 लाख trades को server-side (named) cursor से पढ़ता है ताकि memory स्थिर रहे, और summary rows को `execute_values` से bulk insert करता है। एक Flask admin tool `ThreadedConnectionPool` रखता है और हर request पर एक connection लेता है।

---

## 💻 Code Example — Basic
```python
# Basic psycopg2 example. pip install psycopg2-binary
# Verified against a real local PostgreSQL 16 (unix-socket host). Adjust DSN for your server.
import psycopg2  # the driver
import psycopg2.errors  # specific exception classes
import psycopg2.extras  # helpers: RealDictCursor, execute_values
from typing import Any, Dict, List, Tuple  # type hints

conn = psycopg2.connect(host="localhost", dbname="postgres", user="postgres", password="postgres")  # open connection

with conn.cursor() as cur:  # cursor closes automatically
    cur.execute("DROP TABLE IF EXISTS users")  # clean start
    cur.execute(  # create table
        "CREATE TABLE users (id SERIAL PRIMARY KEY, email TEXT UNIQUE NOT NULL, name TEXT, age INT)"
    )
    cur.execute(  # %s placeholders: values are sent separately, never concatenated
        "INSERT INTO users (email, name, age) VALUES (%s, %s, %s) RETURNING id",  # RETURNING gives new id
        ("a@x.com", "Aman", 30),  # parameters as a tuple
    )
    print(cur.fetchone(), cur.rowcount)  # new id and rows affected
    # Output: (1,) 1
    psycopg2.extras.execute_values(  # fastest way to insert many rows
        cur,
        "INSERT INTO users (email, name, age) VALUES %s",  # one %s for the whole list
        [("b@x.com", "Bina", 25), ("c@x.com", "Chirag", 41)],  # list of tuples
    )
    print(cur.rowcount)  # rows inserted
    # Output: 2
conn.commit()  # without this, nothing is saved

with conn.cursor() as cur:  # new cursor
    cur.execute("SELECT id, email FROM users WHERE age > %s ORDER BY id", (26,))  # parameterised query
    rows: List[Tuple[Any, ...]] = cur.fetchall()  # list of tuples
    print(rows)  # show them
    # Output: [(1, 'a@x.com'), (3, 'c@x.com')]

with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:  # rows as dicts
    cur.execute("SELECT * FROM users WHERE id = %s", (1,))  # one user
    row: Dict[str, Any] = dict(cur.fetchone())  # convert to plain dict
    print(row)  # show it
    # Output: {'id': 1, 'email': 'a@x.com', 'name': 'Aman', 'age': 30}
conn.close()  # release connection
```

## 💻 Code Example — Advanced
```python
# Production style: error handling, transactions, pool, safe identifiers, server-side cursor
# pip install psycopg2-binary   (every output below was produced by a real run on PostgreSQL 16)
from contextlib import contextmanager  # for our own helper
from typing import Any, Iterator, List, Optional, Sequence, Tuple  # types

import psycopg2  # driver
import psycopg2.errors  # exceptions such as UniqueViolation
from psycopg2 import pool, sql  # connection pool + safe SQL composition

DSN: str = "host=localhost dbname=postgres user=postgres password=postgres"  # use env vars in real code
db_pool: pool.ThreadedConnectionPool = pool.ThreadedConnectionPool(1, 5, DSN)  # min 1, max 5 connections


@contextmanager  # get connection, commit/rollback, always give it back
def get_conn() -> Iterator[psycopg2.extensions.connection]:
    conn = db_pool.getconn()  # borrow a connection
    try:
        yield conn  # caller works here
        conn.commit()  # success: save
    except Exception:  # any failure
        conn.rollback()  # clean the aborted transaction
        raise  # let the caller see the error
    finally:
        db_pool.putconn(conn)  # return to pool (never close pooled conns yourself)


def add_user(email: str, name: Optional[str], age: int) -> Optional[int]:
    try:
        with get_conn() as conn, conn.cursor() as cur:  # connection + cursor
            cur.execute(
                "INSERT INTO users (email, name, age) VALUES (%s, %s, %s) RETURNING id",
                (email, name, age),  # None becomes SQL NULL automatically
            )
            return cur.fetchone()[0]  # new id
    except psycopg2.errors.UniqueViolation as exc:  # duplicate email
        print("UniqueViolation", exc.pgcode)  # 23505 is the Postgres error code
        return None  # tell the caller


print(add_user("d@x.com", "Dev", 22))  # works
print(add_user("a@x.com", "Dup", 20))  # already exists
# Output (ids depend on the sequence): 4
# Output: UniqueViolation 23505
# Output: None

# --- Aborted transaction trap -------------------------------------------------
conn = psycopg2.connect(DSN)  # plain connection to demonstrate
try:
    with conn.cursor() as cur:
        cur.execute("SELECT 1/0")  # runtime error inside the transaction
except psycopg2.Error as exc:
    print(type(exc).__name__)  # error class
    # Output: DivisionByZero
try:
    with conn.cursor() as cur:
        cur.execute("SELECT 1")  # even a valid query now fails
except psycopg2.Error as exc:
    print(type(exc).__name__, str(exc).strip()[:60])
    # Output: InFailedSqlTransaction current transaction is aborted, commands ignored until end o
conn.rollback()  # the fix: rollback, then continue

# --- `with conn:` is a transaction block, not a close ------------------------
try:
    with conn:  # commit on success, rollback on exception
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users")  # delete everything...
        raise RuntimeError("oops")  # ...then fail
except RuntimeError:
    pass
with conn.cursor() as cur:
    cur.execute("SELECT count(*) FROM users")  # delete was rolled back
    print(cur.fetchone(), conn.closed)  # connection is still open (closed == 0)
    # Output: (4,) 0   (count depends on rows you inserted)

# --- Dynamic table/column names: use sql.Identifier, NEVER f-strings ---------
with conn.cursor() as cur:
    query = sql.SQL("SELECT {col} FROM {tbl} LIMIT 1").format(
        col=sql.Identifier("email"), tbl=sql.Identifier("users")  # safely quoted names
    )
    cur.execute(query)  # run it
    print(cur.fetchone())  # one row
    # Output: ('a@x.com',)
    print(cur.mogrify("SELECT %s, %s", ("o'neil", None)))  # see the final SQL (debug only)
    # Output: b"SELECT 'o''neil', NULL"

# --- Server-side cursor: stream big results without loading all in memory ----
with conn.cursor(name="big_scan") as cur:  # a NAME makes it server-side
    cur.itersize = 2  # rows fetched per network round trip (use thousands in real life)
    cur.execute("SELECT generate_series(1, 5)")  # pretend big result
    print([r[0] for r in cur])  # iterate lazily
    # Output: [1, 2, 3, 4, 5]
conn.rollback()  # server-side cursors need a transaction; end it
conn.close()  # close
db_pool.closeall()  # close all pooled connections at shutdown
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (psycopg2)
with conn.cursor() as cur:
    cur.execute("SELECT * FROM users WHERE id = %s", (1,))   # %s placeholder, tuple
    row = cur.fetchone()                                      # blocking call
conn.commit()                                                 # explicit commit
```
```javascript
// JavaScript (node-postgres)
const { rows } = await pool.query("SELECT * FROM users WHERE id = $1", [1]);  // $1 placeholder
// every call is async; autocommit unless you BEGIN manually via client.query("BEGIN")
```

Key differences: psycopg2 blocks the thread (sync) while `pg` is non-blocking; placeholders are `%s` vs `$1`; psycopg2 opens a transaction automatically and needs `commit()`, node-postgres runs each `query()` in autocommit mode unless you use `BEGIN`.

---

## 🟠 FastAPI Connection
psycopg2 is synchronous, so use it in plain `def` routes (FastAPI runs them in a thread pool). Use a `ThreadedConnectionPool` and a `yield` dependency to borrow and return connections.

```python
# FastAPI + psycopg2 pool (verified with TestClient: returned {'id': 1, 'email': 'a@x.com'} and 404)
from typing import Annotated, Dict, Iterator  # types
import psycopg2  # driver
from psycopg2 import pool  # pool
from psycopg2.extras import RealDictCursor  # dict rows
from fastapi import Depends, FastAPI, HTTPException  # framework

pg_pool = pool.ThreadedConnectionPool(1, 5, "host=localhost dbname=postgres user=postgres password=postgres")
app: FastAPI = FastAPI()  # app


def get_conn() -> Iterator[psycopg2.extensions.connection]:
    conn = pg_pool.getconn()  # borrow
    try:
        yield conn  # use
        conn.commit()  # save on success
    except Exception:
        conn.rollback()  # undo on error
        raise
    finally:
        pg_pool.putconn(conn)  # return


ConnDep = Annotated[psycopg2.extensions.connection, Depends(get_conn)]  # alias


@app.get("/users/{uid}")  # plain def = thread pool, so blocking driver is OK
def get_user(uid: int, conn: ConnDep) -> Dict:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:  # dict rows
        cur.execute("SELECT id, email FROM users WHERE id = %s", (uid,))  # safe query
        row = cur.fetchone()  # None if missing
    if row is None:  # not found
        raise HTTPException(404, "not found")  # 404
    return dict(row)  # JSON
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not rolling back after an error
```python
# Wrong: after one failure every query raises InFailedSqlTransaction
try: cur.execute("SELECT 1/0")
except Exception: pass
cur.execute("SELECT 1")   # InFailedSqlTransaction

# Right:
except Exception: conn.rollback()
```

❌ Mistake 2: Formatting values into SQL
```python
# Wrong: injection risk
cur.execute("SELECT * FROM users WHERE email = '%s'" % email)
cur.execute(f"... '{email}'")

# Right: pass a tuple (even for one value, note the comma)
cur.execute("SELECT * FROM users WHERE email = %s", (email,))
```

❌ Mistake 3: `(value)` instead of `(value,)`
```python
# Wrong: (5) is just the int 5, not a tuple
cur.execute("SELECT * FROM users WHERE id = %s", (5))

# Right:
cur.execute("SELECT * FROM users WHERE id = %s", (5,))
```

❌ Mistake 4: Forgetting `commit()` or assuming `with conn:` closes
```python
# Right: conn.commit() (or `with conn:`); close/return the connection yourself
```

❌ Mistake 5: Calling `conn.close()` on a pooled connection / using psycopg2 in `async def`
```python
# Right: pool.putconn(conn); and keep psycopg2 in plain def routes, or use psycopg 3 async (topic 353)
```

---

## 🧠 Tricky Interview Question

**Q**: What happens on the last line?

```python
try:
    with conn.cursor() as cur:
        cur.execute("SELECT 1/0")
except psycopg2.Error as e:
    print(type(e).__name__)
with conn.cursor() as cur:
    cur.execute("SELECT 1")
```

**Answer**:
```
DivisionByZero
psycopg2.errors.InFailedSqlTransaction: current transaction is aborted, commands ignored until end of transaction block
```
After an error inside a transaction, PostgreSQL refuses every command until you call `conn.rollback()`. The `with conn.cursor()` block only closes the cursor; it does not clean the transaction. (The two exception names were verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: `psycopg2` vs `psycopg2-binary`?
A1: Same code. `-binary` ships a precompiled wheel (easy for dev). The plain package compiles against your system libpq (recommended for production, because the binary wheel bundles its own libraries).

Q2: What does `with conn:` do?
A2: Starts a transaction block: commit on success, rollback on exception. It does not close the connection.

Q3: How do you insert many rows fast?
A3: `psycopg2.extras.execute_values` (single multi-row INSERT) or `COPY` through `cur.copy_expert` for very large loads. `executemany` is slower because it runs one statement per row.

Q4: Why a named cursor?
A4: It creates a server-side cursor so rows are streamed in batches (`itersize`). Without a name, psycopg2 downloads the entire result set to client memory.

Q5: Is psycopg2 still recommended?
A5: It is maintained but in maintenance mode; new projects should consider `psycopg` 3 (async support, server-side binding, `COPY` API). Existing apps and SQLAlchemy with `postgresql+psycopg2://` work fine.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Existing sync apps (Django, Flask, scripts) already use it
- You want a mature, battle-tested driver
- Raw SQL / bulk loading with `execute_values`

❌ Avoid when:
- You need native async (use `psycopg` 3 or `asyncpg`)
- Starting a new project and want the newest features (prefer `psycopg` 3)

---

## 📊 Visual Diagram

```
 connect() ─► [ connection ] ─► cursor() ─► execute(sql, params) ─► fetch...()
                  │                                  │
                  │ transaction starts automatically │ error?
                  ▼                                  ▼
              commit()  ◄── success       rollback() ◄── failure (mandatory!)
                  │
              putconn() / close()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cursor | Runs SQL, holds results | SQL चलाने वाला object |
| RealDictCursor | Rows as dicts | dict जैसे rows |
| Named cursor | Server-side streaming cursor | server-side streaming cursor |
| SQLSTATE / pgcode | Error code like 23505 | error code |
| execute_values | Fast multi-row insert | तेज़ multi-row insert |
| Aborted transaction | Needs rollback before reuse | rollback के बिना दोबारा नहीं चलता |

---

## ⚡ 3-Line Summary
English: psycopg2 is the classic sync PostgreSQL driver: use `%s` parameters, commit explicitly, rollback after errors, pool connections, and stream large results with named cursors.
Hindi: psycopg2 classic sync PostgreSQL driver है: `%s` parameters इस्तेमाल करें, commit खुद करें, error के बाद rollback करें, connections pool करें और बड़े results के लिए named cursors लें।

---

## ➡️ Next Topic
**353. psycopg3 (async)** — the modern PostgreSQL driver with async connections and pools.
