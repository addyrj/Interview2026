---

# 351. Database in Python Overview
# हिंदी में: Python में Database का परिचय

---

## 🔵 Simple Definition (English)
Python talks to databases through a driver (a library for one database, e.g. `psycopg`, `mysql-connector-python`, built-in `sqlite3`). All SQL drivers follow the same standard called DB-API (PEP 249): `connect()`, `cursor()`, `execute()`, `fetch...()`, `commit()`. On top of drivers you can add a query builder, an ORM (SQLAlchemy) or an async layer.

## 🔵 सरल परिभाषा (Hindi)
Python database से driver के ज़रिए बात करता है (किसी एक database की library, जैसे `psycopg`, `mysql-connector-python`, built-in `sqlite3`)। सभी SQL drivers एक ही standard DB-API (PEP 249) मानते हैं: `connect()`, `cursor()`, `execute()`, `fetch...()`, `commit()`। Drivers के ऊपर query builder, ORM (SQLAlchemy) या async layer लगाई जा सकती है।

---

## 🔴 Problem it Solves
Every database speaks its own network protocol. Without a common pattern, each database would need a different way of coding. DB-API gives one shape, so learning one driver teaches you the others, and tools like SQLAlchemy can sit on top of any of them. Choosing the right layer (raw driver vs ORM, sync vs async) decides speed, safety and maintainability.

## 🔴 यह क्यों बना? (Hindi)
हर database का अपना network protocol होता है। साझा pattern न हो तो हर database के लिए अलग तरीके से code लिखना पड़ता। DB-API एक ही ढाँचा देता है, इसलिए एक driver सीखने से बाकी भी आ जाते हैं और SQLAlchemy जैसे tools किसी भी driver के ऊपर चल सकते हैं। सही layer चुनना (raw driver या ORM, sync या async) speed, safety और maintainability तय करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick the driver for your database (PostgreSQL: psycopg / asyncpg, MySQL: mysql-connector, SQLite: sqlite3)
Step 2 → connection = driver.connect(...)           # open network connection (expensive: pool it)
Step 3 → cursor = connection.cursor()               # object that runs statements
Step 4 → cursor.execute(SQL, params)                # params are sent SEPARATELY (prevents SQL injection)
Step 5 → rows = cursor.fetchall()                   # read results (SELECT)
Step 6 → connection.commit() or rollback()          # finish the transaction (INSERT/UPDATE/DELETE)
Step 7 → cursor.close(); connection.close()         # release resources (use `with` blocks)
Step 8 → Optional: add SQLAlchemy (Core/ORM) and Alembic (migrations) on top
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → अपने database का driver चुनें (PostgreSQL: psycopg / asyncpg, MySQL: mysql-connector, SQLite: sqlite3)
Step 2 → connection = driver.connect(...)           # network connection खुलता है (महँगा: pool करें)
Step 3 → cursor = connection.cursor()               # statements चलाने वाला object
Step 4 → cursor.execute(SQL, params)                # params अलग भेजे जाते हैं (SQL injection रुकता है)
Step 5 → rows = cursor.fetchall()                   # SELECT के results पढ़ें
Step 6 → connection.commit() या rollback()          # INSERT/UPDATE/DELETE का transaction पूरा करें
Step 7 → cursor.close(); connection.close()         # resources छोड़ें (`with` blocks इस्तेमाल करें)
Step 8 → चाहें तो ऊपर SQLAlchemy (Core/ORM) और Alembic (migrations) लगाएँ
```

---

## 🟡 Real World Example
A food-delivery backend stores orders in PostgreSQL (strong transactions), user sessions in Redis, product search in Elasticsearch, and uses SQLite for unit tests. The FastAPI app uses SQLAlchemy with the `psycopg` driver for most code, a raw `psycopg` call for one heavy reporting query, and Alembic to change tables safely.

## 🟡 Real Example Hindi mein
Food-delivery backend orders को PostgreSQL में (मज़बूत transactions), user sessions Redis में, product search Elasticsearch में रखता है और unit tests के लिए SQLite इस्तेमाल करता है। FastAPI app ज़्यादातर code में SQLAlchemy और `psycopg` driver लेता है, एक भारी reporting query के लिए सीधा `psycopg` और tables सुरक्षित बदलने के लिए Alembic।

---

## 💻 Code Example — Basic
```python
# Basic DB-API example with the built-in sqlite3 (no install needed)
import sqlite3  # standard library driver
from typing import List, Tuple  # type hints

conn: sqlite3.Connection = sqlite3.connect(":memory:")  # temporary in-memory database
print(sqlite3.paramstyle, sqlite3.apilevel, sqlite3.threadsafety)  # DB-API metadata
# Output: qmark 2.0 3   (threadsafety value depends on Python build/compile options)

conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INT)")  # create table
conn.executemany(  # insert many rows at once
    "INSERT INTO users (name, age) VALUES (?, ?)",  # ? = placeholder (sqlite style)
    [("Aman", 30), ("Bina", 25)],  # parameter tuples
)
conn.commit()  # save the transaction

rows: List[Tuple] = conn.execute("SELECT * FROM users WHERE age > ?", (26,)).fetchall()  # parameterised
print(rows)  # list of tuples
# Output: [(1, 'Aman', 30)]

conn.row_factory = sqlite3.Row  # rows behave like dicts too
row = conn.execute("SELECT * FROM users WHERE id=1").fetchone()  # one row
print(row["name"], dict(row))  # access by column name
# Output: Aman {'id': 1, 'name': 'Aman', 'age': 30}

try:  # constraint error
    with conn:  # transaction block: commit on success, rollback on error
        conn.execute("INSERT INTO users (id, name) VALUES (1, 'dup')")  # duplicate primary key
except sqlite3.IntegrityError as exc:  # standard DB-API exception
    print("IntegrityError", exc)  # error text
# Output: IntegrityError UNIQUE constraint failed: users.id
```

## 💻 Code Example — Advanced
```python
# Production style: same DB-API shape across drivers + safe parameters + transaction helper
import sqlite3  # runnable driver
from contextlib import contextmanager  # build a context manager
from typing import Any, Dict, Iterator, List, Sequence  # types


@contextmanager  # transaction helper usable with any DB-API connection
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Cursor]:
    cur: sqlite3.Cursor = conn.cursor()  # create cursor
    try:
        yield cur  # run caller's SQL
        conn.commit()  # success: save
    except Exception:  # any error
        conn.rollback()  # undo partial work
        raise  # re-raise so the caller knows
    finally:
        cur.close()  # always release cursor


def fetch_dicts(conn: sqlite3.Connection, sql: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
    cur = conn.execute(sql, params)  # params never concatenated into SQL
    cols: List[str] = [d[0] for d in cur.description]  # column names (DB-API standard)
    return [dict(zip(cols, r)) for r in cur.fetchall()]  # list of dicts


conn = sqlite3.connect(":memory:")  # database
conn.execute("CREATE TABLE accounts (id INTEGER PRIMARY KEY, balance INT CHECK (balance >= 0))")  # rule
conn.executemany("INSERT INTO accounts (balance) VALUES (?)", [(100,), (50,)])  # two accounts
conn.commit()  # save


def transfer(src: int, dst: int, amount: int) -> None:
    with transaction(conn) as cur:  # both updates succeed or none
        cur.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, src))  # debit
        cur.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, dst))  # credit


transfer(1, 2, 30)  # valid transfer
print(fetch_dicts(conn, "SELECT * FROM accounts ORDER BY id"))  # check balances
# Output: [{'id': 1, 'balance': 70}, {'id': 2, 'balance': 80}]

try:  # overdraw: debit fails CHECK constraint
    transfer(1, 2, 500)  # would make balance negative
except sqlite3.IntegrityError as exc:  # constraint error
    print("rolled back:", exc)  # message
# Output: rolled back: CHECK constraint failed: balance >= 0
print(fetch_dicts(conn, "SELECT balance FROM accounts ORDER BY id"))  # unchanged
# Output: [{'balance': 70}, {'balance': 80}]

# SQL injection demo: f-string vs parameters
bad: str = "x' OR '1'='1"  # attacker input
unsafe = conn.execute(f"SELECT count(*) FROM accounts WHERE id = '{bad}'").fetchone()  # string built into SQL!
safe = conn.execute("SELECT count(*) FROM accounts WHERE id = ?", (bad,)).fetchone()  # bound parameter
print("unsafe:", unsafe, "safe:", safe)  # compare
# Output: unsafe: (2,) safe: (0,)
```
Verified by running the sqlite3 parts. The same `transaction` shape works for `psycopg2`, `psycopg` 3 and `mysql.connector`, but the placeholder differs: sqlite3 uses `?`, while `psycopg2`, `psycopg` 3 and `mysql-connector` use `%s` (pyformat style). Always check `module.paramstyle`.

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: DB-API shape (works the same way across drivers)
conn = psycopg.connect(DSN)                                    # connect
with conn.cursor() as cur:                                     # cursor
    cur.execute("SELECT * FROM users WHERE id = %s", (1,))     # placeholder + params
    rows = cur.fetchall()                                      # results
conn.commit()                                                  # transaction end
```
```javascript
// JavaScript (node-postgres "pg"): same ideas, async by default
const pool = new Pool({ connectionString: DSN });              // pool
const { rows } = await pool.query("SELECT * FROM users WHERE id = $1", [1]);  // $1 placeholder
// ORMs: Prisma, Sequelize, TypeORM  <->  SQLAlchemy / Django ORM / SQLModel
```

Key differences: Node drivers are async-only and use `$1` (pg) or `?` (mysql2) placeholders. Python has sync drivers (DB-API) and separate async ones (`asyncpg`, `psycopg` async mode, `aiomysql`). Python's DB-API has an implicit transaction: nothing is saved until `commit()`.

---

## 🟠 FastAPI Connection
FastAPI does not include a database layer. You choose: raw driver + pool (fast, manual), SQLAlchemy sync session in plain `def` routes (simplest), or an async stack (async SQLAlchemy + `asyncpg`/`psycopg` async) in `async def` routes. Always give each request its own connection/session through a `yield` dependency.

```python
# Per-request SQLite connection dependency (demo; use a pool for PostgreSQL/MySQL)
import sqlite3  # driver
from typing import Annotated, Dict, Iterator  # types
from fastapi import Depends, FastAPI, HTTPException  # framework

app: FastAPI = FastAPI()  # app


def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect("app.db", check_same_thread=False)  # sqlite is picky about threads
    conn.row_factory = sqlite3.Row  # dict-like rows
    try:
        yield conn  # hand to the route
    finally:
        conn.close()  # always closed after the response


ConnDep = Annotated[sqlite3.Connection, Depends(get_conn)]  # alias


@app.get("/users/{uid}")  # plain def: blocking driver runs in a thread pool
def get_user(uid: int, conn: ConnDep) -> Dict[str, object]:
    row = conn.execute("SELECT id, name FROM users WHERE id = ?", (uid,)).fetchone()  # parameterised
    if row is None:  # not found
        raise HTTPException(status_code=404, detail="User not found")  # 404
    return dict(row)  # JSON
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building SQL with f-strings
```python
# Wrong: SQL injection, unsafe: (2,) in the demo above
conn.execute(f"SELECT * FROM users WHERE name = '{name}'")

# Right: bound parameters
conn.execute("SELECT * FROM users WHERE name = ?", (name,))   # %s for psycopg/mysql
```

❌ Mistake 2: Forgetting `commit()`
```python
# Wrong: the INSERT is lost when the connection closes
cur.execute("INSERT ..."); conn.close()

# Right: conn.commit() (or use `with conn:` / the driver's context manager)
```

❌ Mistake 3: Opening a new connection per query
```python
# Wrong: a TCP + auth handshake on every call
def get(): return psycopg.connect(DSN).execute("SELECT 1")

# Right: a pool (psycopg_pool, SQLAlchemy engine) created once at startup
```

❌ Mistake 4: Blocking driver inside `async def`
```python
# Wrong: async def route calling psycopg2/mysql-connector (freezes the event loop)
# Right: plain def route (thread pool), or a real async driver with await
```

❌ Mistake 5: Thinking `with sqlite3.connect() as conn` closes the connection
```python
# Wrong: assumes closed after the block
# Right: the block only commits/rolls back; close explicitly (contextlib.closing)
```

---

## 🧠 Tricky Interview Question

**Q**: What happens?

```python
import sqlite3
with sqlite3.connect(":memory:") as cn:
    pass
print(cn.execute("SELECT 1").fetchone())
```

**Answer**:
```
(1,)
```
In `sqlite3`, `with connection:` is a transaction manager (commit on success, rollback on exception); it does NOT close the connection. To close it, call `cn.close()` or wrap with `contextlib.closing(...)`; after closing, `execute` raises `sqlite3.ProgrammingError: Cannot operate on a closed database.` (Both verified by running.) Note: Python 3.12+ adds an `autocommit` attribute to sqlite3, but the context-manager behaviour above is unchanged.

---

## ⚫ Interview Questions + Answers

Q1: What is DB-API (PEP 249)?
A1: A standard interface for Python SQL drivers: `connect`, `cursor`, `execute`, `fetchone/fetchmany/fetchall`, `commit`, `rollback`, `close` and a hierarchy of exceptions (`IntegrityError`, `OperationalError`...).

Q2: Driver vs ORM?
A2: A driver sends SQL and returns rows. An ORM (SQLAlchemy) maps tables to classes and builds SQL for you, using a driver underneath.

Q3: Why do drivers use placeholders and a separate params argument?
A3: So the database treats values as data, never as SQL. This blocks SQL injection and lets the server reuse query plans.

Q4: Which driver for which database?
A4: PostgreSQL: `psycopg` 3 (sync/async) or `psycopg2` (legacy), `asyncpg` (async only). MySQL: `mysql-connector-python`, `PyMySQL`, `mysqlclient`, `aiomysql`. SQLite: built-in `sqlite3`, `aiosqlite` for async.

Q5: When do you need a connection pool?
A5: Almost always in a web app: opening connections is slow and databases have a connection limit. SQLAlchemy's engine pools for you; with raw drivers use `psycopg_pool` or `mysql.connector.pooling`.

---

## 🔷 When to Use + When Not to Use

✅ Use raw drivers when:
- You need full control or the best speed for a few heavy queries
- Small scripts, ETL jobs, one-off reports

✅ Use ORM (SQLAlchemy) when:
- Many tables and relationships, migrations, team projects

❌ Avoid when:
- Raw SQL strings spread across a huge app (hard to refactor)
- ORM for bulk data loads of millions of rows (use `COPY`/bulk inserts)

---

## 📊 Visual Diagram

```
  FastAPI route
      │
  SQLAlchemy ORM / Core    (optional layer: models, queries)
      │
  DB-API driver            (psycopg / mysql-connector / sqlite3 / asyncpg)
      │   connection pool
      ▼
  Network protocol  ──►  PostgreSQL / MySQL / SQLite file
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Driver | Library that talks to one DB | एक database से बात करने वाली library |
| DB-API | Python driver standard (PEP 249) | Python drivers का standard |
| Cursor | Object that runs SQL and holds results | SQL चलाने और results रखने वाला object |
| Transaction | Group of statements, all or none | statements का समूह, सब या कुछ नहीं |
| Placeholder | `%s` / `?` for values | values के लिए जगह |
| Connection pool | Reusable connections | दोबारा इस्तेमाल होने वाले connections |

---

## ⚡ 3-Line Summary
English: Python drivers follow DB-API: connect, cursor, execute with parameters, fetch, commit. Use pools, never f-string SQL, and add SQLAlchemy/Alembic when the project grows. Pick sync or async drivers to match your FastAPI routes.
Hindi: Python drivers DB-API मानते हैं: connect, cursor, parameters के साथ execute, fetch, commit। Pools इस्तेमाल करें, f-string SQL कभी नहीं, और project बढ़े तो SQLAlchemy/Alembic जोड़ें। अपने FastAPI routes के हिसाब से sync या async drivers चुनें।

---

## ➡️ Next Topic
**352. psycopg2 — PostgreSQL** — the classic sync PostgreSQL driver in detail.
