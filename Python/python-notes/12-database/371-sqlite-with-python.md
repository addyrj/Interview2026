---

# 371. SQLite with Python
# हिंदी में: Python के साथ SQLite (Built-in Embedded Database)

---

## 🔵 Simple Definition (English)
SQLite is a small SQL database that lives in a single file (or in memory) and runs inside your program, with no server. Python ships with it as the `sqlite3` module, so you can use a real SQL database without installing anything.

## 🔵 सरल परिभाषा (Hindi)
SQLite एक छोटा SQL database है जो एक ही file (या memory) में रहता है और आपके program के अंदर चलता है, बिना किसी server के। Python इसे `sqlite3` module के रूप में साथ देता है, इसलिए बिना कुछ install किए असली SQL database इस्तेमाल हो जाता है।

---

## 🔴 Problem it Solves
Running PostgreSQL or MySQL for a small tool, a test suite, a mobile/desktop app or a prototype is heavy: install, configure users, ports, backups. Plain JSON or CSV files have no queries, no constraints and break with concurrent writes. SQLite gives you real SQL, transactions (ACID) and constraints with zero setup, stored in one portable file.

## 🔴 यह क्यों बना? (Hindi)
छोटे tool, test suite, mobile/desktop app या prototype के लिए PostgreSQL या MySQL चलाना भारी है: install, users, ports, backups सब करना पड़ता है। सादी JSON या CSV files में queries, constraints नहीं होते और एक साथ writes पर टूट जाती हैं। SQLite बिना setup के असली SQL, transactions (ACID) और constraints देता है, एक ही portable file में।

---

## 🟢 How it Works — Step by Step

```
Step 1 → sqlite3.connect("app.db") opens (or creates) the file; ":memory:" = RAM only
Step 2 → conn.execute(sql, params) runs SQL; "?" placeholders keep data separate from SQL
Step 3 → Writes open a transaction automatically (default legacy behaviour)
Step 4 → conn.commit() saves, conn.rollback() undoes
Step 5 → cursor / fetchone / fetchall / iteration read the rows
Step 6 → row_factory = sqlite3.Row gives dict-like access by column name
Step 7 → PRAGMA settings tune behaviour (foreign_keys, journal_mode=WAL, busy_timeout)
Step 8 → conn.close() when finished
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → sqlite3.connect("app.db") file खोलता (या बनाता) है; ":memory:" = सिर्फ RAM
Step 2 → conn.execute(sql, params) SQL चलाता है; "?" placeholders data को SQL से अलग रखते हैं
Step 3 → Writes पर transaction अपने आप शुरू होता है (default legacy behaviour)
Step 4 → conn.commit() save करता है, conn.rollback() वापस पलटता है
Step 5 → cursor / fetchone / fetchall / iteration से rows पढ़ते हैं
Step 6 → row_factory = sqlite3.Row से column name से dict जैसा access मिलता है
Step 7 → PRAGMA settings behaviour बदलती हैं (foreign_keys, journal_mode=WAL, busy_timeout)
Step 8 → काम खत्म होने पर conn.close()
```

---

## 🟡 Real World Example
Your browser (Chrome, Firefox), WhatsApp on Android and iOS apps all store data in SQLite files. In backend work, SQLite is used for fast pytest suites (database in memory), small internal tools, edge/IoT devices, and a local cache of an LLM app's chat history or embeddings metadata.

## 🟡 Real Example Hindi mein
आपका browser (Chrome, Firefox), Android पर WhatsApp और iOS apps सब data SQLite files में रखते हैं। Backend में SQLite तेज pytest suites (memory में database), छोटे internal tools, edge/IoT devices, और LLM app की chat history या embeddings metadata के local cache के लिए इस्तेमाल होता है।

---

## 💻 Code Example — Basic
```python
# Basic sqlite3: create, insert, query, rollback (in-memory, runs anywhere)
import sqlite3                                               # stdlib, no install

conn: sqlite3.Connection = sqlite3.connect(":memory:")       # temp db in RAM
conn.row_factory = sqlite3.Row                               # rows behave like dicts
conn.execute("PRAGMA foreign_keys = ON")                     # FK checks are OFF by default!
conn.execute("create table users (id integer primary key, name text not null, age integer)")   # DDL
conn.executemany("insert into users (name, age) values (?, ?)",   # ? placeholders, never f-strings
                 [("Asha", 30), ("Ravi", 25), ("Mehul", 41)])    # three rows
conn.commit()                                                # save the transaction
for row in conn.execute("select * from users where age > ? order by age", (26,)):   # parameterized
    print(row["id"], row["name"], row["age"])                # access by column name
try:
    conn.execute("insert into users (name) values (NULL)")   # violates NOT NULL
except sqlite3.IntegrityError as e:                          # specific error class
    print("IntegrityError:", e)
    conn.rollback()                                          # undo the failed transaction
print(conn.execute("select count(*) from users").fetchone()[0])   # still 3
print(sqlite3.sqlite_version_info >= (3, 35))                # RETURNING needs 3.35+
conn.close()                                                 # release the file/memory

# Output:
# 1 Asha 30
# 3 Mehul 41
# IntegrityError: NOT NULL constraint failed: users.name
# 3
# True
```
Verified: run on Python 3.13.3.

## 💻 Code Example — Advanced
```python
# Advanced: repository with context manager, WAL mode, transactions, constraints
from __future__ import annotations                           # forward refs
import sqlite3                                               # stdlib
import tempfile                                              # temp folder for the file db
import os                                                    # path join
from contextlib import contextmanager                        # transaction helper
from dataclasses import dataclass                            # row model
from typing import Iterator                                  # hint


@dataclass
class Account:
    id: int                                                  # primary key
    owner: str                                               # owner name
    balance: int                                             # paise/cents as int, never float for money


class Bank:
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(path, isolation_level=None)   # autocommit; we control BEGIN
        self.conn.row_factory = sqlite3.Row                  # dict-like rows
        self.conn.execute("PRAGMA journal_mode = WAL")       # readers do not block the writer
        self.conn.execute("PRAGMA busy_timeout = 3000")      # wait 3s on a lock instead of failing
        self.conn.execute("PRAGMA foreign_keys = ON")        # enforce FKs
        self.conn.execute("create table if not exists acc (id integer primary key, owner text, "
                          "balance integer not null check (balance >= 0))")   # no negative money

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        self.conn.execute("BEGIN IMMEDIATE")                 # take the write lock up front
        try:
            yield self.conn                                  # do work
            self.conn.execute("COMMIT")                      # all or nothing: commit
        except Exception:
            self.conn.execute("ROLLBACK")                    # any error: undo everything
            raise

    def open_account(self, owner: str, balance: int) -> Account:
        with self.tx() as c:                                 # one transaction
            row = c.execute("insert into acc (owner, balance) values (?, ?) returning id",
                            (owner, balance)).fetchone()     # RETURNING needs SQLite 3.35+
        return Account(row["id"], owner, balance)

    def transfer(self, src: int, dst: int, amount: int) -> None:
        with self.tx() as c:                                 # both updates in ONE transaction
            c.execute("update acc set balance = balance - ? where id = ?", (amount, src))
            c.execute("update acc set balance = balance + ? where id = ?", (amount, dst))

    def balance(self, acc_id: int) -> int:
        return self.conn.execute("select balance from acc where id = ?", (acc_id,)).fetchone()[0]


with tempfile.TemporaryDirectory() as d:                     # scratch folder, auto-deleted
    bank = Bank(os.path.join(d, "bank.db"))                  # file db so WAL is real
    a, b = bank.open_account("Asha", 1000), bank.open_account("Ravi", 500)
    bank.transfer(a.id, b.id, 300)                           # valid transfer
    print(bank.balance(a.id), bank.balance(b.id))            # 700 800
    try:
        bank.transfer(a.id, b.id, 5000)                      # would make Asha negative
    except sqlite3.IntegrityError as e:                      # CHECK constraint fires
        print("rejected:", e)
    print(bank.balance(a.id), bank.balance(b.id))            # unchanged: rolled back
    print(bank.conn.execute("PRAGMA journal_mode").fetchone()[0])   # wal
    bank.conn.close()                                        # close before temp dir removal

# Output:
# 700 800
# rejected: CHECK constraint failed: balance >= 0
# 700 800
# wal
```
Verified: run on Python 3.13.3 with SQLite from the stdlib build.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript (Node) |
|---------|--------|------------------|
| SQLite library | `sqlite3` (built in) | `better-sqlite3`, `sqlite3` (npm); `node:sqlite` in new Node |
| API style | sync (use thread/`aiosqlite` for async) | `better-sqlite3` sync, `sqlite3` callbacks |
| Placeholders | `?` or `:name` | `?` or `@name` |
| Transactions | `commit()` / `rollback()` | `db.transaction(fn)` in better-sqlite3 |
| Install | nothing | `npm install` (native build) |

```python
# Python way
import sqlite3                                           # built in
db = sqlite3.connect(":memory:")                         # connect
db.execute("create table t (x integer)")                 # create
db.execute("insert into t values (?)", (5,))             # insert with placeholder
print(db.execute("select x from t").fetchall())         # [(5,)]
```
```javascript
// JavaScript way (better-sqlite3)
const Database = require("better-sqlite3");              // npm install better-sqlite3
const db = new Database(":memory:");                     // connect
db.exec("create table t (x integer)");                   // create
db.prepare("insert into t values (?)").run(5);           // insert with placeholder
console.log(db.prepare("select x from t").all());        // [ { x: 5 } ]
```

Key difference: Python rows are tuples (use `row_factory = sqlite3.Row` for names), while better-sqlite3 returns objects. Python needs no install and no native compile.

---

## 🟠 FastAPI Connection
SQLite is the standard database for FastAPI tutorials, tests and small apps. Because FastAPI runs sync endpoints in a thread pool, a single connection shared by threads needs `check_same_thread=False` (or better: one connection per request). SQLAlchemy uses `sqlite3` under the hood, so you can start on SQLite and move to PostgreSQL later by changing the URL.

```python
# FastAPI example — sqlite3 dependency, 404 handling
import sqlite3                                               # stdlib db
from typing import Iterator                                  # hint
from fastapi import Depends, FastAPI, HTTPException          # FastAPI
from fastapi.testclient import TestClient                    # test client

app = FastAPI()                                              # app
shared = sqlite3.connect(":memory:", check_same_thread=False)   # demo only; prod uses a file/pool
shared.execute("create table todo (id integer primary key, title text)")   # schema
shared.execute("insert into todo (title) values ('learn sqlite')")         # seed row


def get_conn() -> Iterator[sqlite3.Connection]:
    yield shared                                             # in prod: open per request and close


@app.get("/todo/{tid}")                                      # sync def -> runs in a threadpool
def get_todo(tid: int, conn: sqlite3.Connection = Depends(get_conn)) -> dict[str, str]:
    row = conn.execute("select title from todo where id = ?", (tid,)).fetchone()
    if row is None:                                          # not found -> 404
        raise HTTPException(404, "todo not found")
    return {"title": row[0]}


c = TestClient(app)                                          # client
print(c.get("/todo/1").json(), c.get("/todo/9").status_code)
# Output:
# {'title': 'learn sqlite'} 404
```
Verified: run with TestClient.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building SQL with f-strings (SQL injection)
✅ Correct: always use `?` placeholders

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("create table u (name text)")
name = "x'; DROP TABLE u; --"
# Wrong
# db.executescript(f"select * from u where name = '{name}'")   # attacker controls your SQL
# Right
db.execute("select * from u where name = ?", (name,))          # name is only data
```

❌ Mistake 2: Forgetting `commit()` — data seems saved but other connections do not see it
✅ Correct: commit (or use a transaction helper)

```python
# Wrong
# a.execute("insert into t values (1)")   # another connection sees 0 rows
# Right
# a.execute("insert into t values (1)"); a.commit()
```

❌ Mistake 3: Assuming foreign keys are enforced
✅ Correct: run `PRAGMA foreign_keys = ON` on EVERY new connection (default is OFF)

```python
# Wrong: orphan rows insert silently
# Right
# conn.execute("PRAGMA foreign_keys = ON")
```

❌ Mistake 4: Sharing one connection across threads without care
✅ Correct: one connection per thread/request, or use WAL + `busy_timeout`

```python
# Wrong: ProgrammingError: SQLite objects created in a thread can only be used in that same thread
# Right: open a connection inside each request/thread, or a proper pool
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import sqlite3, tempfile, os
d = tempfile.mkdtemp(); p = os.path.join(d, "t.db")
a = sqlite3.connect(p); a.execute("create table t (x)"); a.commit()
a.execute("insert into t values (1)")
b = sqlite3.connect(p)
print(b.execute("select count(*) from t").fetchone()[0])
a.commit()
print(b.execute("select count(*) from t").fetchone()[0])
with a:
    a.execute("insert into t values (2)")
try:
    a.execute("select 1")
    print("still open")
except Exception as e:
    print(type(e).__name__)
```
Answer: `0`, `1`, `still open`. The insert on connection `a` is inside an uncommitted transaction, so connection `b` cannot see it (count 0). After `a.commit()` it is visible (count 1). Last: `with conn:` on an sqlite3 connection only commits (or rolls back on error); it does NOT close the connection, so `a` is still usable. Many people expect `with` to close it like a file. Use `contextlib.closing(conn)` to close. (Verified on Python 3.13.3; the default `autocommit` behaviour is the legacy one.)

---

## ⚫ Interview Questions + Answers

Q1: Why is SQLite called serverless?
A1: There is no separate database process. The library is linked into your program and reads/writes the database file directly. No network, no users, no daemon to run.

Q2: How does SQLite handle concurrency?
A2: Many readers can read at once, but only one writer at a time (file-level write lock). In the default rollback-journal mode, a writer blocks readers; in WAL mode (`PRAGMA journal_mode=WAL`) readers do not block the writer. Set `busy_timeout` so waiting writers retry instead of failing with "database is locked".

Q3: What is type affinity in SQLite?
A3: SQLite columns have a preferred type, not a strict one. You can store text in an INTEGER column and it will not complain (e.g. `'5' + 3` gives 8, and `1/2` gives 0 with integer division). Use `CREATE TABLE ... STRICT` (SQLite 3.37+) or CHECK constraints for strict typing.

Q4: When should you choose PostgreSQL over SQLite?
A4: When you need many concurrent writers, network access from multiple servers, advanced types and extensions, replication, or very large data. SQLite is great for single-node apps, tests, embedded and read-heavy workloads.

Q5: How do you avoid SQL injection in `sqlite3`?
A5: Pass values as parameters (`execute("... where id = ?", (x,))`). Placeholders only work for values, not for table or column names. If a name is dynamic, validate it against an allow-list before putting it into the SQL string.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Unit/integration tests (in-memory database)
- Prototypes, CLI tools, desktop/mobile apps, local caches
- Read-heavy small to medium websites on a single server
- Embedded/IoT devices

❌ Avoid when:
- Many servers must write to the same database over a network
- High write concurrency (hundreds of writers)
- You need user roles, row-level security, or advanced replication
- Data size is in the hundreds of GB with heavy analytics

---

## 📊 Visual Diagram
```
 Python process
 ┌──────────────────────────────────────┐
 │  your code ──► sqlite3 module        │
 │                   │ (library inside) │
 │                   ▼                  │
 │            app.db  (one file)        │
 │            app.db-wal (WAL mode)     │
 └──────────────────────────────────────┘
  no network, no server

 BEGIN ─► INSERT ─► UPDATE ─► COMMIT   (all saved)
                     └──────► ROLLBACK (all undone)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedded database | Runs inside the app | App के अंदर चलने वाला database |
| `:memory:` | Database only in RAM | सिर्फ RAM में database |
| Placeholder | `?` slot for a value | Value के लिए `?` जगह |
| Transaction | Group of changes, all or none | बदलावों का समूह, सब या कुछ नहीं |
| WAL | Write-ahead log mode | Write-ahead log mode |
| PRAGMA | SQLite setting command | SQLite की setting command |
| Row factory | Controls row shape | Row का रूप तय करने वाला |
| Type affinity | Preferred column type | Column का पसंदीदा type |

---

## ⚡ 3-Line Summary
English: `sqlite3` is a built-in, serverless SQL database stored in one file or in memory. Use `?` placeholders, commit or roll back transactions, and turn on `foreign_keys` and WAL for real work. It is perfect for tests, tools and small apps, but not for many concurrent writers across servers.
Hindi: `sqlite3` Python में built-in, बिना server वाला SQL database है जो एक file या memory में रहता है। `?` placeholders इस्तेमाल करें, transactions को commit या rollback करें, और असली काम के लिए `foreign_keys` और WAL चालू करें। यह tests, tools और छोटे apps के लिए बढ़िया है, पर कई servers से बहुत सारे concurrent writers के लिए नहीं।

---

## ➡️ Next Topic
**372. Database Best Practices** — the habits (parameterized queries, indexes, transactions, N+1 avoidance) that keep any database fast and safe in production.
