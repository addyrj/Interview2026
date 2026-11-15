---

# 355. PyMySQL
# हिंदी में: PyMySQL (Python से MySQL जोड़ने वाली pure-Python library)

---

## 🔵 Simple Definition (English)
PyMySQL is a pure-Python driver that lets your Python code talk to a MySQL or MariaDB server. You open a connection, send SQL through a cursor, and read the rows back. It needs no C compiler, so it installs easily everywhere.

## 🔵 सरल परिभाषा (Hindi)
PyMySQL एक pure-Python driver है जिससे आपका Python code MySQL या MariaDB server से बात करता है। आप connection खोलते हैं, cursor से SQL भेजते हैं और rows वापस पढ़ते हैं। इसे C compiler नहीं चाहिए, इसलिए यह हर जगह आसानी से install होता है।

---

## 🔴 Problem it Solves
Python cannot speak the MySQL network protocol by itself. Before drivers, you had to build raw sockets and parse binary packets. Older drivers like `mysqlclient` need C headers and `libmysqlclient`, which often fail to install on Alpine Docker images or Windows. PyMySQL solves this: `pip install pymysql` and it works. It also gives a standard DB-API 2.0 interface (`connect`, `cursor`, `execute`, `commit`), so the same pattern works in other drivers.

## 🔴 यह क्यों बना? (Hindi)
Python खुद MySQL का network protocol नहीं बोल सकता। Drivers से पहले raw sockets बनाकर binary packets parse करने पड़ते थे। `mysqlclient` जैसे पुराने drivers को C headers और `libmysqlclient` चाहिए, जो Alpine Docker image या Windows पर अक्सर install नहीं होते। PyMySQL यह हल करता है: `pip install pymysql` और काम शुरू। यह standard DB-API 2.0 interface (`connect`, `cursor`, `execute`, `commit`) भी देता है, इसलिए यही pattern दूसरे drivers में भी चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pymysql.connect(host, user, password, database) opens a TCP socket to MySQL (port 3306)
Step 2 → MySQL authenticates you (caching_sha2_password needs the `cryptography` package)
Step 3 → conn.cursor() gives an object that sends queries and holds results
Step 4 → cursor.execute(sql, params) sends the SQL; %s placeholders are escaped by the driver
Step 5 → fetchone() / fetchall() read rows (tuples, or dicts with DictCursor)
Step 6 → conn.commit() saves writes (autocommit is OFF by default); rollback() undoes
Step 7 → cursor and connection are closed (use `with` so it happens automatically)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pymysql.connect(host, user, password, database) MySQL (port 3306) से TCP socket खोलता है
Step 2 → MySQL आपको authenticate करता है (caching_sha2_password के लिए `cryptography` package चाहिए)
Step 3 → conn.cursor() ऐसा object देता है जो query भेजता है और result रखता है
Step 4 → cursor.execute(sql, params) SQL भेजता है; %s placeholders driver खुद escape करता है
Step 5 → fetchone() / fetchall() rows पढ़ते हैं (tuples, या DictCursor से dicts)
Step 6 → conn.commit() writes save करता है (autocommit डिफ़ॉल्ट में OFF है); rollback() वापस लेता है
Step 7 → cursor और connection बंद होते हैं (`with` इस्तेमाल करें तो अपने आप)
```

---

## 🟡 Real World Example
A Razorpay-style payments service stores orders in MySQL. A reconciliation script written with PyMySQL runs every night: it connects, selects all `pending` orders from the last day with a parameterized query, calls the bank API, then updates the status in a single transaction. If any update fails, `rollback()` keeps the data consistent. Swiggy-like analytics scripts also use `SSCursor` to stream millions of rows without loading them all in memory.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments service orders को MySQL में रखती है। PyMySQL से लिखी reconciliation script हर रात चलती है: connect करती है, पिछले दिन के सभी `pending` orders parameterized query से select करती है, bank API call करती है, फिर status एक ही transaction में update करती है। कोई update fail हो तो `rollback()` data को सही रखता है। Swiggy जैसी analytics scripts `SSCursor` से लाखों rows stream करती हैं, सब memory में load किए बिना।

---

## 💻 Code Example — Basic
```python
# Basic PyMySQL usage (needs a running MySQL server — NOT run in the notes environment)
# pip install pymysql cryptography
import pymysql                                    # the driver

conn = pymysql.connect(                           # open a connection
    host="127.0.0.1",                             # server address
    port=3306,                                    # default MySQL port
    user="app",                                   # database user
    password="secret",                            # password (use env vars in real code)
    database="shop",                              # database to use
    charset="utf8mb4",                            # full Unicode incl. emoji
)

with conn.cursor() as cur:                        # cursor closes automatically
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50))")  # DDL
    cur.execute("INSERT INTO users (name) VALUES (%s)", ("Asha",))   # %s is the placeholder, ALWAYS for MySQL
    cur.execute("SELECT id, name FROM users WHERE name = %s", ("Asha",))   # parameterized select
    print(cur.fetchone())                         # one row as a tuple
conn.commit()                                     # save the INSERT (autocommit is off)
conn.close()                                      # release the connection

# Output (MySQL server needed, so not verified here; id depends on table state):
# (1, 'Asha')
```

## 💻 Code Example — Advanced
```python
# Production style: connection helper, DictCursor, transactions, error handling
# NOT run here (needs MySQL). Syntax was checked with ast.parse.
import os                                         # read settings from environment
from collections.abc import Iterator              # type for the generator
from contextlib import contextmanager             # build a with-block helper
from typing import Any                            # row type

import pymysql                                    # driver
from pymysql.connections import Connection        # type for connection
from pymysql.cursors import DictCursor            # rows come back as dicts


def get_conn() -> Connection:
    """Create a new connection from environment variables."""
    return pymysql.connect(                       # open connection
        host=os.getenv("DB_HOST", "127.0.0.1"),   # host with default
        user=os.getenv("DB_USER", "app"),         # user with default
        password=os.getenv("DB_PASSWORD", ""),    # never hard-code passwords
        database=os.getenv("DB_NAME", "shop"),    # database name
        charset="utf8mb4",                        # emoji-safe
        cursorclass=DictCursor,                   # rows as dicts
        connect_timeout=5,                        # fail fast if server is down
        autocommit=False,                         # we control transactions
    )


@contextmanager
def transaction() -> Iterator[Connection]:
    """Commit if the block succeeds, roll back if it raises."""
    conn: Connection = get_conn()                 # new connection
    try:
        yield conn                                # run the caller's code
        conn.commit()                             # success -> save everything
    except Exception:                             # any failure
        conn.rollback()                           # undo partial work
        raise                                     # let the caller see the error
    finally:
        conn.close()                              # always release the connection


def transfer(from_id: int, to_id: int, amount: int) -> None:
    """Move money between two accounts atomically."""
    with transaction() as conn, conn.cursor() as cur:        # one transaction, one cursor
        cur.execute("SELECT balance FROM accounts WHERE id = %s FOR UPDATE", (from_id,))   # lock the row
        row: dict[str, Any] | None = cur.fetchone()          # get the balance
        if row is None or row["balance"] < amount:           # validate
            raise ValueError("insufficient funds")           # triggers rollback
        cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, from_id))   # debit
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, to_id))     # credit


def stream_orders() -> Iterator[dict[str, Any]]:
    """Read a huge table row by row without loading it all."""
    conn: Connection = pymysql.connect(           # separate connection
        host="127.0.0.1", user="app", password="secret", database="shop",
        cursorclass=pymysql.cursors.SSDictCursor, # server-side cursor: streams rows
    )
    try:
        with conn.cursor() as cur:                # open cursor
            cur.execute("SELECT * FROM orders")   # start the query
            yield from cur                        # yield one row at a time
    finally:
        conn.close()                              # close even if consumer stops early


if __name__ == "__main__":
    try:
        transfer(1, 2, 500)                       # try a transfer
        print("transfer ok")                      # printed on success
    except pymysql.err.OperationalError as e:     # server down / bad credentials
        print("DB unavailable:", e.args[0])       # e.g. 2003 = cannot connect
    except ValueError as e:                       # business rule failed
        print("Rejected:", e)                     # insufficient funds

# Output when no MySQL server is running (typical error code; not verified here):
# DB unavailable: 2003
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (PyMySQL) | JavaScript (mysql2) |
|---------|------------------|---------------------|
| Install | `pip install pymysql` | `npm i mysql2` |
| Placeholder | `%s` | `?` |
| Async | no (blocking) | promises built in |
| Transactions | `commit()` / `rollback()` | `connection.commit()` |
| Row type | tuple or dict (DictCursor) | objects by default |

```python
# Python way
import pymysql                                                  # driver
conn = pymysql.connect(host="localhost", user="app", password="x", database="shop")   # connect
with conn.cursor() as cur:                                      # cursor
    cur.execute("SELECT * FROM users WHERE id = %s", (1,))      # params as a tuple
    print(cur.fetchall())                                       # list of tuples
```
```javascript
// JavaScript way (mysql2/promise)
const mysql = require("mysql2/promise");                        // driver
const conn = await mysql.createConnection({host: "localhost", user: "app", database: "shop"});  // connect
const [rows] = await conn.execute("SELECT * FROM users WHERE id = ?", [1]);   // ? placeholder
console.log(rows);                                              // array of objects
```

Key difference: PyMySQL is blocking (a request waits for the DB), while mysql2 is promise-based. Placeholders differ (`%s` vs `?`), and `%s` is NOT Python string formatting: always pass params as the second argument.

---

## 🟠 FastAPI Connection
In FastAPI, a plain `def` endpoint runs in a thread pool, so blocking PyMySQL calls are OK there (never call them inside `async def`; use `asyncmy` / `aiomysql` for that). Use a dependency with `yield` to open and close a connection per request.

```python
# FastAPI with PyMySQL (not run here: needs a MySQL server)
from collections.abc import Iterator                  # generator type
import pymysql                                        # driver
from fastapi import Depends, FastAPI, HTTPException   # FastAPI parts

app: FastAPI = FastAPI()                              # create app


def db() -> Iterator[pymysql.connections.Connection]:
    conn = pymysql.connect(host="127.0.0.1", user="app", password="secret",
                           database="shop", cursorclass=pymysql.cursors.DictCursor)   # per request
    try:
        yield conn                                    # give it to the endpoint
    finally:
        conn.close()                                  # always close


@app.get("/users/{user_id}")                          # plain def -> runs in thread pool
def get_user(user_id: int, conn=Depends(db)) -> dict:
    with conn.cursor() as cur:                        # open cursor
        cur.execute("SELECT id, name FROM users WHERE id = %s", (user_id,))   # safe query
        row = cur.fetchone()                          # one row or None
    if row is None:                                   # not found
        raise HTTPException(status_code=404, detail="user not found")   # 404 reply
    return row                                        # dict -> JSON
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building SQL with f-strings (SQL injection)
✅ Correct: pass parameters as the second argument

```python
# Wrong — name = "x'; DROP TABLE users; --" destroys data
cur.execute(f"SELECT * FROM users WHERE name = '{name}'")
# Right — the driver escapes the value
cur.execute("SELECT * FROM users WHERE name = %s", (name,))
```

❌ Mistake 2: Forgetting `commit()`
✅ Correct: commit after writes (or set `autocommit=True` deliberately)

```python
# Wrong — the INSERT is rolled back when the connection closes
cur.execute("INSERT INTO users (name) VALUES (%s)", ("Asha",))
conn.close()
# Right
cur.execute("INSERT INTO users (name) VALUES (%s)", ("Asha",))
conn.commit()
conn.close()
```

❌ Mistake 3: Passing a single param without a tuple
✅ Correct: `(value,)` with the trailing comma

```python
# Wrong — ("Asha") is just a string; it is treated as 4 separate characters / raises an error
cur.execute("SELECT * FROM users WHERE name = %s", ("Asha"))
# Right
cur.execute("SELECT * FROM users WHERE name = %s", ("Asha",))
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (assume table t is empty, autocommit off, InnoDB)
import pymysql
c1 = pymysql.connect(host="127.0.0.1", user="app", password="x", database="d")
c2 = pymysql.connect(host="127.0.0.1", user="app", password="x", database="d")
with c1.cursor() as a:
    a.execute("INSERT INTO t (v) VALUES (1)")        # no commit on c1
with c2.cursor() as b:
    b.execute("SELECT COUNT(*) FROM t")
    print(b.fetchone())
```
Answer: `(0,)`. Connection `c1` has an open transaction, and its INSERT is not committed, so the other connection `c2` cannot see it (the InnoDB default isolation level is REPEATABLE READ, which never shows uncommitted data). Only after `c1.commit()` would a new query on `c2` return `(1,)`. Note: c2 also starts its own snapshot at its first read, so a long-lived c2 may keep seeing old data until it commits or rolls back too.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between PyMySQL and mysqlclient?
A1: PyMySQL is pure Python (slower, easy to install, no C dependencies). `mysqlclient` wraps the C library `libmysqlclient` (faster, but needs headers and a compiler). Both follow DB-API 2.0 and both work as the dialect driver under SQLAlchemy (`mysql+pymysql://`).

Q2: Why must you use `%s` placeholders instead of f-strings?
A2: Placeholders send values separately from the SQL text and the driver escapes them, which blocks SQL injection. f-strings put user input straight into SQL. Note `%s` is used for every type (int, str, date), not `%d`.

Q3: What does `commit()` do, and what is autocommit?
A3: With autocommit off (default in PyMySQL), statements run inside a transaction that becomes permanent only on `commit()`. With `autocommit=True` each statement is committed instantly, so multi-step operations are not atomic.

Q4: How do you read millions of rows without running out of memory?
A4: Use a server-side cursor: `pymysql.cursors.SSCursor` or `SSDictCursor`. It streams rows from the server instead of buffering the whole result. You must read all rows (or close the cursor) before running another query on the same connection.

Q5: Can you use PyMySQL in an `async def` FastAPI endpoint?
A5: Not directly: it blocks the event loop and freezes all other requests. Use a plain `def` endpoint (thread pool), or an async driver such as `aiomysql` / `asyncmy` (or SQLAlchemy async with `mysql+aiomysql`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want a simple, install-anywhere MySQL driver
- Scripts, cron jobs, small services, Docker images without compilers
- You need raw SQL control

❌ Avoid when:
- You need async I/O (use aiomysql/asyncmy)
- You need max performance (use mysqlclient or mysql-connector C extension)
- You want models and relationships (use SQLAlchemy or Django ORM on top)

---

## 📊 Visual Diagram
```
Python app
   |  pymysql.connect()
   v
+-----------+   SQL text + params    +-------------+
| Connection| ---------------------> | MySQL server|
|  cursor() |  <-------------------- |  (InnoDB)   |
+-----------+      rows / OK         +-------------+
   |
   |-- execute()  -> send query
   |-- fetchone() -> read rows
   |-- commit()   -> make permanent
   |-- rollback() -> undo
   '-- close()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Driver | Library speaking a DB protocol | DB से बात करने वाली library |
| Cursor | Object that runs queries and holds results | Query चलाने वाला object |
| DB-API 2.0 | Python's standard DB interface (PEP 249) | Python का standard DB interface |
| Placeholder | `%s` marker for safe parameters | सुरक्षित parameter का निशान |
| Transaction | Group of statements that succeed or fail together | साथ सफल या असफल होने वाले statements |
| SSCursor | Server-side streaming cursor | Rows stream करने वाला cursor |

---

## ⚡ 3-Line Summary
English: PyMySQL is a pure-Python MySQL driver following DB-API 2.0: connect, cursor, execute, commit. Always use `%s` parameters, commit your writes, and close connections. It is blocking, so use plain `def` endpoints in FastAPI or switch to an async driver.
Hindi: PyMySQL एक pure-Python MySQL driver है जो DB-API 2.0 follow करता है: connect, cursor, execute, commit। हमेशा `%s` parameters इस्तेमाल करें, writes commit करें और connection बंद करें। यह blocking है, इसलिए FastAPI में plain `def` endpoints रखें या async driver लें।

---

## ➡️ Next Topic
**357. SQLAlchemy ORM** — stop writing raw SQL strings: map Python classes to tables and query with Python objects.
