---

# 354. mysql-connector-python
# हिंदी में: mysql-connector-python (Oracle का official MySQL driver)

---

## 🔵 Simple Definition (English)
`mysql-connector-python` is the official MySQL driver from Oracle. It is pure Python (with an optional C extension) and lets you connect to MySQL, run SQL with `%s` placeholders, manage transactions and use a built-in connection pool. Install: `pip install mysql-connector-python`, import: `mysql.connector`.

## 🔵 सरल परिभाषा (Hindi)
`mysql-connector-python` Oracle का official MySQL driver है। इससे MySQL से connect करके `%s` placeholders वाली SQL चला सकते हैं, transactions संभाल सकते हैं और built-in connection pool इस्तेमाल कर सकते हैं। Install: `pip install mysql-connector-python`, import: `mysql.connector`।

---

## 🔴 Problem it Solves
Python cannot talk to the MySQL wire protocol by itself. A driver converts Python calls (`cursor.execute`) into protocol packets and converts results (`DECIMAL`, `DATETIME`) back into Python types (`Decimal`, `datetime`). This connector needs no `libmysqlclient` system library, so installation is easy in Docker.

## 🔴 यह क्यों बना? (Hindi)
Python खुद MySQL protocol नहीं समझता। Driver Python calls (`cursor.execute`) को protocol packets में बदलता है और नतीजे (`DECIMAL`, `DATETIME`) को Python types (`Decimal`, `datetime`) में लौटाता है। इस connector को `libmysqlclient` system library नहीं चाहिए, इसलिए Docker में install आसान है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → mysql.connector.connect(host, user, password, database)  -> connection
Step 2 → conn.cursor()                                             -> cursor object
Step 3 → cursor.execute(sql, params)   (params are escaped/bound, safe from injection)
Step 4 → SELECT: fetchone() / fetchall() / iterate | write: conn.commit()
Step 5 → On error: catch mysql.connector.Error, call conn.rollback()
Step 6 → cursor.close(); conn.close()  (pooled conn.close() returns it to the pool)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → connect(host, user, password, database) से connection बनता है
Step 2 → conn.cursor() से cursor मिलता है
Step 3 → cursor.execute(sql, params): params सुरक्षित तरीके से जाते हैं
Step 4 → SELECT में fetchone()/fetchall(); लिखने के बाद conn.commit() ज़रूरी
Step 5 → Error आए तो mysql.connector.Error पकड़ो और conn.rollback() करो
Step 6 → cursor और connection बंद करो (pool में close() का मतलब pool को वापस देना)
```

---

## 🟡 Real World Example
An e-commerce backend (Flipkart style) stores orders in MySQL. Every checkout inserts into `orders` and decrements `inventory` inside one transaction; if stock is short, `rollback()` undoes everything. A `MySQLConnectionPool` of 10 connections serves many web workers.

## 🟡 Real Example Hindi mein
Flipkart जैसे e-commerce backend में orders MySQL में रहते हैं। हर checkout में `orders` में insert और `inventory` में घटाव एक transaction में होता है; stock कम हो तो `rollback()` सब वापस कर देता है। 10 connections का `MySQLConnectionPool` कई workers को serve करता है।

---

## 💻 Code Example — Basic
```python
# VERIFIED: run against a local MySQL 9.1 server (user app, db shop). Needs a running MySQL to execute.
# Install: pip install mysql-connector-python
from typing import Any, Dict, List, Tuple  # type hints

import mysql.connector  # the driver
from mysql.connector import Error  # base exception class

# connect() returns a connection object (use your real host/credentials, from env vars in production)
conn = mysql.connector.connect(
    host="127.0.0.1", port=3306, user="app", password="secret", database="shop"
)
print(conn.is_connected())  # Output: True

cur = conn.cursor()  # default cursor returns tuples
cur.execute("DROP TABLE IF EXISTS orders")  # reset the demo table
cur.execute(  # DDL (create table)
    "CREATE TABLE orders (id INT AUTO_INCREMENT PRIMARY KEY, "
    "customer VARCHAR(50) NOT NULL, amount DECIMAL(10,2) NOT NULL)"
)
cur.execute(  # %s placeholders (even for numbers), never use f-strings
    "INSERT INTO orders (customer, amount) VALUES (%s, %s)", ("Aarav", 499.50)
)
print(cur.lastrowid, cur.rowcount)  # Output: 1 1   (new auto id, rows affected)
cur.executemany(  # many rows in one call
    "INSERT INTO orders (customer, amount) VALUES (%s, %s)",
    [("Diya", 250), ("Kabir", 1200.75)],
)
print(cur.rowcount)  # Output: 2
conn.commit()  # IMPORTANT: autocommit is OFF by default, without this nothing is saved

cur.execute("SELECT id, customer, amount FROM orders WHERE amount > %s ORDER BY id", (300,))
rows: List[Tuple[Any, ...]] = cur.fetchall()  # all rows as a list of tuples
print(rows)  # Output: [(1, 'Aarav', Decimal('499.50')), (3, 'Kabir', Decimal('1200.75'))]
cur.close()  # close the cursor

cur = conn.cursor(dictionary=True)  # rows as dicts
cur.execute("SELECT * FROM orders WHERE customer = %(c)s", {"c": "Diya"})  # named placeholder
one: Dict[str, Any] | None = cur.fetchone()  # one row or None
print(one)  # Output: {'id': 2, 'customer': 'Diya', 'amount': Decimal('250.00')}

try:
    cur.execute("INSERT INTO orders (customer, amount) VALUES (NULL, 1)")  # breaks NOT NULL
except Error as exc:  # all driver errors inherit from Error
    print(type(exc).__name__, exc.errno, exc.msg)
    # Output: IntegrityError 1048 Column 'customer' cannot be null
    conn.rollback()  # undo the failed work
try:
    cur.execute("SELEKT 1")  # typo in SQL
except Error as exc:
    print(type(exc).__name__, exc.errno)  # Output: ProgrammingError 1064
conn.close()  # close the connection
print(conn.is_connected())  # Output: False
```

## 💻 Code Example — Advanced
```python
# VERIFIED: pool, transaction, rollback, streaming cursor and pool exhaustion ran on MySQL 9.1.
# Needs a running MySQL server. Production style: pool + context manager + transaction + typed helper.
from contextlib import contextmanager  # make our own with-block
from decimal import Decimal  # exact money
from typing import Any, Iterator  # type hints

from mysql.connector import Error, pooling  # errors and pool

pool = pooling.MySQLConnectionPool(  # create once at startup
    pool_name="shop_pool", pool_size=3, pool_reset_session=True,
    host="127.0.0.1", port=3306, user="app", password="secret", database="shop",
)


@contextmanager
def get_conn() -> Iterator[Any]:
    """Borrow a connection and always give it back."""
    conn = pool.get_connection()  # raises PoolError if all 3 are busy
    try:
        yield conn  # caller uses it
    finally:
        conn.close()  # for a pooled connection this RETURNS it to the pool


def transfer_wallet(src: int, dst: int, amount: Decimal) -> None:
    """Debit src and credit dst atomically."""
    with get_conn() as conn:  # borrow
        cur = conn.cursor()  # cursor created before try so finally can close it
        try:
            conn.start_transaction()  # explicit BEGIN (needs InnoDB tables)
            cur.execute(  # guard: balance >= amount prevents overdraft
                "UPDATE wallets SET balance = balance - %s WHERE id = %s AND balance >= %s",
                (amount, src, amount),
            )
            if cur.rowcount != 1:  # no row matched -> not enough money
                raise ValueError("insufficient funds")
            cur.execute("UPDATE wallets SET balance = balance + %s WHERE id = %s", (amount, dst))
            conn.commit()  # both updates become permanent together
        except (Error, ValueError):
            conn.rollback()  # undo the debit if anything failed
            raise  # let the caller handle it
        finally:
            cur.close()  # always release the cursor


with get_conn() as c:  # setup demo data
    cu = c.cursor()
    cu.execute("DROP TABLE IF EXISTS wallets")
    cu.execute("CREATE TABLE wallets (id INT PRIMARY KEY, balance DECIMAL(10,2) NOT NULL) ENGINE=InnoDB")
    cu.executemany("INSERT INTO wallets VALUES (%s, %s)", [(1, 1000), (2, 0)])
    c.commit()

transfer_wallet(1, 2, Decimal("300"))  # works
try:
    transfer_wallet(1, 2, Decimal("5000"))  # fails and rolls back
except ValueError as exc:
    print("failed:", exc)  # Output: failed: insufficient funds

with get_conn() as c:
    cu = c.cursor()
    cu.execute("SELECT id, balance FROM wallets ORDER BY id")
    print(cu.fetchall())  # Output: [(1, Decimal('700.00')), (2, Decimal('300.00'))]
    cu.close()

with get_conn() as c:  # unbuffered cursor streams rows (good for big result sets)
    cu = c.cursor(buffered=False)
    cu.execute("SELECT id FROM wallets")
    for (row_id,) in cu:  # must read ALL rows before another query on this connection
        print("row", row_id)  # Output: row 1 / row 2
    cu.close()

held = [pool.get_connection() for _ in range(3)]  # take every connection
try:
    pool.get_connection()  # 4th request
except Error as exc:
    print(type(exc).__name__, exc)  # Output: PoolError Failed getting connection; pool exhausted
for h in held:
    h.close()  # give them back
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: mysql-connector-python
import mysql.connector
conn = mysql.connector.connect(host="localhost", user="app", password="x", database="shop")
cur = conn.cursor(dictionary=True)
cur.execute("SELECT * FROM users WHERE id = %s", (1,))
user = cur.fetchone()
conn.close()
```
```javascript
// JavaScript: mysql2 (promise API)
const mysql = require("mysql2/promise");
const conn = await mysql.createConnection({ host: "localhost", user: "app", password: "x", database: "shop" });
const [rows] = await conn.execute("SELECT * FROM users WHERE id = ?", [1]);
await conn.end();
```

Key differences: `mysql2` uses `?` placeholders and is promise-based; `mysql-connector-python` uses `%s` and is blocking (synchronous) by default. Both default to manual transactions in the sense that Python needs `commit()`; in JS you call `conn.commit()` only after `beginTransaction()`.

---

## 🟠 FastAPI Connection
This connector is synchronous, so inside FastAPI use plain `def` endpoints (FastAPI runs them in a thread pool), not `async def`. Use a pool plus a dependency.

```python
# FastAPI + mysql-connector pool (needs a running MySQL; sync endpoints on purpose)
from typing import Any, Dict, Iterator  # type hints
from fastapi import Depends, FastAPI, HTTPException  # web framework
from mysql.connector import pooling  # connection pool

app: FastAPI = FastAPI()  # create the app
pool = pooling.MySQLConnectionPool(
    pool_name="api", pool_size=5, host="127.0.0.1", user="app", password="secret", database="shop"
)


def get_db() -> Iterator[Any]:
    conn = pool.get_connection()  # borrow one per request
    try:
        yield conn  # inject into the endpoint
    finally:
        conn.close()  # return to pool


@app.get("/orders/{order_id}")
def read_order(order_id: int, conn: Any = Depends(get_db)) -> Dict[str, Any]:  # def, not async def
    cur = conn.cursor(dictionary=True)  # dict rows become JSON easily
    cur.execute("SELECT id, customer, amount FROM orders WHERE id = %s", (order_id,))
    row = cur.fetchone()  # None if missing
    cur.close()
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    row["amount"] = float(row["amount"])  # Decimal is not JSON-friendly in all setups
    return row
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `commit()`
```python
# Wrong: INSERT is rolled back when the connection closes
cur.execute("INSERT INTO t VALUES (%s)", (1,))
conn.close()

# Right
cur.execute("INSERT INTO t VALUES (%s)", (1,))
conn.commit()   # or connect(..., autocommit=True) for simple scripts
```

❌ Mistake 2: String formatting in SQL
```python
# Wrong: injection risk
cur.execute(f"SELECT * FROM users WHERE name = '{name}'")

# Right
cur.execute("SELECT * FROM users WHERE name = %s", (name,))
```

❌ Mistake 3: Unread results ("Unread result found")
```python
# Wrong: unbuffered cursor, next query raises InternalError: Unread result found
cur = conn.cursor(buffered=False)
cur.execute("SELECT * FROM big"); cur.fetchone()
cur.execute("SELECT 1")

# Right: fetch everything (or use buffered=True / a second cursor)
cur.fetchall()
```

❌ Mistake 4: Never closing pooled connections
```python
# Wrong: pool exhausted after pool_size requests
conn = pool.get_connection()   # no close()

# Right: try/finally or the get_conn() context manager shown above
```

---

## 🧠 Tricky Interview Question

**Q**: After this code, is the row in the table?

```python
conn = mysql.connector.connect(**cfg)          # autocommit default
cur = conn.cursor()
cur.execute("INSERT INTO t (x) VALUES (%s)", (1,))
conn.close()                                   # (A)
```

And what changes if the table uses the MyISAM engine instead of InnoDB?

**Answer**: With InnoDB the row is NOT saved: the connector's autocommit defaults to `False`, so the open transaction is rolled back at close. With MyISAM there are no transactions, so every statement is applied immediately and the row stays even without `commit()` (and `rollback()` cannot undo it). Always use InnoDB for data you care about.

---

## ⚫ Interview Questions + Answers

Q1: How does `mysql-connector-python` differ from `PyMySQL` and `mysqlclient`?
A1: Connector is Oracle's official driver (pure Python + optional C ext). PyMySQL is pure Python and community-maintained. `mysqlclient` is a C extension needing `libmysqlclient`, fastest but harder to install.

Q2: Which placeholder is used?
A2: `%s` for positional (tuple) and `%(name)s` for named (dict), regardless of the data type.

Q3: Buffered vs unbuffered cursor?
A3: Buffered fetches the whole result to the client at once (safe, uses memory). Unbuffered streams rows (low memory) but you must read all rows before running the next query.

Q4: Does it support async?
A4: The standard API is blocking. Use `aiomysql`/`asyncmy` or SQLAlchemy async for non-blocking code, or run it in a thread pool (FastAPI `def` endpoints do this).

Q5: How to avoid "Too many connections"?
A5: Use `MySQLConnectionPool` with a fixed size, always `close()` connections to return them, and keep the pool size times worker count below MySQL's `max_connections`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You want the official, easy-to-install MySQL driver
- Small to medium services or scripts with raw SQL
- You need the built-in pooling without extra packages

❌ Avoid when:
- You need true async (use `asyncmy`/`aiomysql`)
- You want an ORM (use SQLAlchemy and this as the underlying driver)
- You need maximum throughput (try `mysqlclient`)

---

## 📊 Visual Diagram

```
Python code
   │  cursor.execute("... %s ...", params)
   ▼
mysql.connector  ──(escape/bind, protocol packets)──►  MySQL server
   ▲                                                      │
   └──── rows as tuple/dict (DECIMAL -> Decimal) ◄────────┘

Pool: [conn1][conn2][conn3]  get_connection() -> use -> close() -> back to pool
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cursor | Object that runs queries | query चलाने वाला object |
| Commit | Save the transaction | transaction सेव करना |
| Rollback | Undo the transaction | transaction वापस लेना |
| Pool | Reusable connection set | दोबारा काम आने वाले connections |
| Placeholder | `%s` slot for values | values की जगह |
| InnoDB | MySQL engine with transactions | transactions वाला engine |

---

## ⚡ 3-Line Summary
English: `mysql-connector-python` is Oracle's official driver. Use `%s` placeholders, call `commit()` because autocommit is off, and use `MySQLConnectionPool` in services. It is blocking, so use `def` endpoints in FastAPI.
Hindi: `mysql-connector-python` Oracle का official driver है। `%s` placeholders इस्तेमाल करें, autocommit बंद होने से `commit()` ज़रूर करें और services में `MySQLConnectionPool` लें। यह blocking है, इसलिए FastAPI में `def` endpoints रखें।

---

## ➡️ Next Topic
**355. PyMySQL** — a pure-Python MySQL driver (already in your notes), then SQLAlchemy.
