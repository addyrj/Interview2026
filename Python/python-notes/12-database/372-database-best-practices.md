---

# 372. Database Best Practices
# हिंदी में: Database Best Practices (Database इस्तेमाल करने के सही तरीके)

---

## 🔵 Simple Definition (English)
Database best practices are proven habits that keep your data correct, your app fast and your system safe: parameterized queries, indexes, transactions, avoiding N+1 queries, pagination, migrations and sensible connection handling.

## 🔵 सरल परिभाषा (Hindi)
Database best practices वे आजमाई हुई आदतें हैं जो आपके data को सही, app को तेज और system को सुरक्षित रखती हैं: parameterized queries, indexes, transactions, N+1 queries से बचना, pagination, migrations और सही connection handling।

---

## 🔴 Problem it Solves
Most production outages and breaches come from the same few mistakes: SQL injection from string-built queries, full table scans because an index is missing, one request firing 1,000 queries (N+1), half-finished money transfers without transactions, and floating point rounding in prices. These problems do not show up with 10 rows in development, but explode at 10 million rows in production.

## 🔴 यह क्यों बना? (Hindi)
Production के ज्यादातर outages और breaches कुछ ही गलतियों से आते हैं: string से बनी queries से SQL injection, index न होने से full table scan, एक request का 1,000 queries चलाना (N+1), transactions के बिना अधूरे पैसे के transfers, और कीमतों में floating point की गलतियां। ये समस्याएं development में 10 rows पर नहीं दिखतीं, पर production में 1 करोड़ rows पर फट पड़ती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Security: pass values as parameters (?, :name), never format them into SQL
Step 2 → Correctness: wrap related writes in ONE transaction; add constraints (NOT NULL, UNIQUE, CHECK, FK)
Step 3 → Money: store integers (paise) or DECIMAL, never float
Step 4 → Speed: index columns used in WHERE / JOIN / ORDER BY; check with EXPLAIN
Step 5 → Avoid N+1: use JOIN or eager loading (selectinload) instead of a query per row
Step 6 → Paginate: LIMIT with keyset (WHERE id > last_id) instead of big OFFSET
Step 7 → Make writes idempotent: UNIQUE key + upsert (ON CONFLICT) so retries are safe
Step 8 → Operate: schema changes through migrations (Alembic), pooled connections, backups, least-privilege DB user
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Security: values को parameters (?, :name) से दो, SQL में कभी format मत करो
Step 2 → Correctness: जुड़े हुए writes को एक ही transaction में रखो; constraints लगाओ (NOT NULL, UNIQUE, CHECK, FK)
Step 3 → पैसा: integers (paise) या DECIMAL रखो, float कभी नहीं
Step 4 → Speed: WHERE / JOIN / ORDER BY में आने वाले columns पर index लगाओ; EXPLAIN से जांचो
Step 5 → N+1 से बचो: हर row पर query की जगह JOIN या eager loading (selectinload) इस्तेमाल करो
Step 6 → Pagination: बड़े OFFSET की जगह keyset (WHERE id > last_id) के साथ LIMIT
Step 7 → Writes को idempotent बनाओ: UNIQUE key + upsert (ON CONFLICT) ताकि retry सुरक्षित हो
Step 8 → Operations: schema changes migrations (Alembic) से, pooled connections, backups, कम अधिकार वाला DB user
```

---

## 🟡 Real World Example
Razorpay-style payments: a refund must debit the merchant and credit the customer in one transaction; the payment id has a UNIQUE constraint so a retried webhook does not double-refund; amounts are stored in paise as integers. On Swiggy's order list, loading 50 orders with their items must be 2 queries (selectin), not 51.

## 🟡 Real Example Hindi mein
Razorpay जैसे payments में: refund merchant को debit और customer को credit एक ही transaction में करना होता है; payment id पर UNIQUE constraint होता है ताकि webhook retry होने पर दोबारा refund न हो; amounts paise में integers के रूप में रखे जाते हैं। Swiggy की order list में 50 orders और उनके items 2 queries में आने चाहिए (selectin), 51 में नहीं।

---

## 💻 Code Example — Basic
```python
# Basic best practices: parameterized queries vs SQL injection, and an index
import sqlite3                                               # stdlib

db = sqlite3.connect(":memory:")                             # temp db
db.execute("create table users (id integer primary key, email text, is_admin integer)")   # schema
db.executemany("insert into users (email, is_admin) values (?, ?)",
               [("a@x.com", 0), ("boss@x.com", 1)])          # two users

evil: str = "nobody' OR '1'='1"                              # attacker input

bad_sql: str = f"select email from users where email = '{evil}'"   # WRONG: string building
print("unsafe:", db.execute(bad_sql).fetchall())             # leaks every row!

good = db.execute("select email from users where email = ?", (evil,)).fetchall()   # RIGHT
print("safe  :", good)                                       # no match, input stayed data

print(db.execute("explain query plan select * from users where email = 'a@x.com'").fetchall()[0][3])
db.execute("create index idx_users_email on users(email)")   # index the lookup column
print(db.execute("explain query plan select * from users where email = 'a@x.com'").fetchall()[0][3])

# Output:
# unsafe: [('a@x.com',), ('boss@x.com',)]
# safe  : []
# SCAN users
# SEARCH users USING INDEX idx_users_email (email=?)
```
Verified: run on Python 3.13.3 (EXPLAIN text can differ slightly between SQLite versions).

## 💻 Code Example — Advanced
```python
# Advanced: N+1 detection, eager loading, keyset pagination, idempotent upsert (SQLAlchemy 2.0 style + SQLite)
from __future__ import annotations                           # forward refs
from sqlalchemy import ForeignKey, create_engine, event, select, func   # core pieces
from sqlalchemy.dialects.sqlite import insert as sqlite_insert   # upsert for SQLite (pg has its own)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload


class Base(DeclarativeBase): pass                            # declarative base


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)        # pk
    name: Mapped[str] = mapped_column(unique=True)           # unique -> upsert target
    books: Mapped[list["Book"]] = relationship(back_populates="author")   # lazy by default


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)        # pk
    title: Mapped[str]                                       # title
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), index=True)   # index FKs!
    author: Mapped[Author] = relationship(back_populates="books")


engine = create_engine("sqlite://")                          # in-memory
Base.metadata.create_all(engine)                             # create tables
count = {"n": 0}                                             # statement counter


@event.listens_for(engine, "before_cursor_execute")          # runs before every SQL statement
def _count(*args: object) -> None:
    count["n"] += 1                                          # tally


with Session(engine) as s:
    s.add_all([Author(name=f"A{i}", books=[Book(title=f"B{i}{j}") for j in range(2)]) for i in range(5)])
    s.commit()                                               # 5 authors x 2 books

    count["n"] = 0                                           # reset
    for a in s.scalars(select(Author)):                      # 1 query for authors...
        _ = [b.title for b in a.books]                       # ...+1 per author = N+1
    print("lazy      :", count["n"], "queries")

    s.expunge_all(); count["n"] = 0                          # fresh identity map
    for a in s.scalars(select(Author).options(selectinload(Author.books))):   # eager load
        _ = [b.title for b in a.books]                       # already loaded
    print("selectin  :", count["n"], "queries")

    last_id = 0                                              # keyset pagination: remember last id
    page = s.scalars(select(Book).where(Book.id > last_id).order_by(Book.id).limit(4)).all()
    print("page1 ids :", [b.id for b in page])               # no OFFSET scan cost
    page = s.scalars(select(Book).where(Book.id > page[-1].id).order_by(Book.id).limit(4)).all()
    print("page2 ids :", [b.id for b in page])

    for _ in range(2):                                       # run the same upsert twice: idempotent
        stmt = sqlite_insert(Author).values(name="A0").on_conflict_do_nothing(index_elements=["name"])
        s.execute(stmt)                                      # second run is a no-op
    s.commit()
    print("authors   :", s.scalar(select(func.count()).select_from(Author)))   # still 5

# Output:
# lazy      : 6 queries
# selectin  : 2 queries
# page1 ids : [1, 2, 3, 4]
# page2 ids : [5, 6, 7, 8]
# authors   : 5
```
Verified: run with SQLAlchemy 2.1.8. The `lazy` count was 6 (1 + 5). For PostgreSQL the upsert import is `sqlalchemy.dialects.postgresql.insert`.

---

## 🟠 JavaScript vs Python Comparison

| Practice | Python | JavaScript |
|----------|--------|-----------|
| Parameters | `execute(sql, (x,))` / `text(":x")` | `client.query(sql, [x])` ($1 in pg) |
| Eager loading | `selectinload`, `joinedload` | Prisma `include`, Sequelize `include` |
| Migrations | Alembic | Prisma Migrate, Knex, Sequelize CLI |
| Money type | `Decimal` or int | `BigInt` or integer minor units (no Decimal built in) |
| Transaction | `with session.begin():` | `await client.query("BEGIN")` / ORM `transaction()` |

```python
# Python way — safe query + transaction
from sqlalchemy import text                              # raw SQL helper
def pay(session, order_id: int, amount_paise: int) -> None:   # session is a SQLAlchemy Session
    with session.begin():                                # commit on success, rollback on error
        session.execute(text("update orders set paid = :a where id = :i"),
                        {"a": amount_paise, "i": order_id})   # bound parameters
```
```javascript
// JavaScript way — safe query + transaction (node-postgres)
async function pay(client, orderId, amountPaise) {       // client from pool.connect()
  try {
    await client.query("BEGIN");                         // start
    await client.query("update orders set paid = $1 where id = $2", [amountPaise, orderId]);   // params
    await client.query("COMMIT");                        // save
  } catch (e) { await client.query("ROLLBACK"); throw e; }   // undo on error
}
```

Key difference: JavaScript numbers are floats (`0.1 + 0.2 = 0.30000000000000004`), and Python floats behave the same. Both need integers (paise) or Decimal for money. Python has `decimal.Decimal` in the standard library, JS does not.

---

## 🟠 FastAPI Connection
In FastAPI, apply these habits at the edges: validate input with Pydantic, use a session dependency per request, commit only on success, translate database errors into correct HTTP codes (409 for duplicates, 404 for missing, never leak raw SQL errors) and paginate list endpoints.

```python
# FastAPI example — validation, bound parameters, unique violation -> 409
from typing import Iterator                                  # hint
from fastapi import Depends, FastAPI, HTTPException          # FastAPI
from fastapi.testclient import TestClient                    # test
from pydantic import BaseModel, Field                        # validation
from sqlalchemy import create_engine, text                   # engine
from sqlalchemy.exc import IntegrityError                    # constraint errors
from sqlalchemy.orm import Session, sessionmaker             # session
from sqlalchemy.pool import StaticPool                       # in-memory demo pool

engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
with engine.begin() as c:                                    # one transaction for setup
    c.execute(text("create table users (id integer primary key, email text unique not null)"))
Local = sessionmaker(engine)                                 # session factory
app = FastAPI()                                              # app


class UserIn(BaseModel):
    email: str = Field(min_length=5, max_length=100)         # validate at the edge


def get_db() -> Iterator[Session]:
    with Local() as s:                                       # session per request
        yield s


@app.post("/users", status_code=201)
def create(u: UserIn, db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("insert into users (email) values (:e)"), {"e": u.email})   # bound param
        db.commit()                                          # commit only on success
    except IntegrityError:                                   # unique violation
        db.rollback()                                        # clean the session
        raise HTTPException(409, "email already exists")     # clear client error
    return {"email": u.email}


c = TestClient(app)
print(c.post("/users", json={"email": "a@x.com"}).status_code,
      c.post("/users", json={"email": "a@x.com"}).status_code,
      c.post("/users", json={"email": "x"}).status_code)
# Output:
# 201 409 422
```
Verified: run with TestClient (first call 201, duplicate 409, too-short email 422).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Building SQL with f-strings
✅ Correct: bound parameters (shown in Basic example above)

```python
# Wrong
# sql = f"select * from users where email = '{email}'"
# Right
# conn.execute(text("select * from users where email = :e"), {"e": email})
```

❌ Mistake 2: Storing money as float
✅ Correct: integer minor units (paise) or `Decimal` / `NUMERIC`

```python
print(0.1 + 0.2)          # Wrong: 0.30000000000000004
print(10 + 20)            # Right: 30 paise (integer math is exact)
```

❌ Mistake 3: `SELECT *` and no `LIMIT` on big tables
✅ Correct: select only needed columns and always paginate

```python
# Wrong: select * from events                       -> 50 million rows into memory
# Right: select id, type from events where id > :last order by id limit 100
```

❌ Mistake 4: Large `OFFSET` pagination
✅ Correct: keyset pagination (`WHERE id > last_id ORDER BY id LIMIT n`)

```python
# Wrong: ... limit 20 offset 1000000   -- DB reads and throws away 1,000,000 rows
# Right: ... where id > 1000000 order by id limit 20   -- jumps straight in using the index
```

❌ Mistake 5: Index on every column
✅ Correct: index columns used in filters/joins/sorts; every index slows writes and uses disk

```python
# Wrong: create index on all 12 columns "just in case"
# Right: composite index matching the query:  create index on orders (user_id, created_at)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output? (SQLite)
import sqlite3
c = sqlite3.connect(":memory:")
print(c.execute("select 1/2, 1.0/2, '5'+3, 5='5'").fetchone())
print(0.1 + 0.2, 10 + 20)
```
Answer: `(0, 0.5, 8, 0)` and then `0.30000000000000004 30`. SQLite does integer division for `1/2` (result 0) and float division when one side is a float. `'5'+3` converts the string to a number (8) because of SQLite's loose typing, but `5='5'` is `0` (integer vs text comparison is false unless column affinity converts it). Python's float `0.1 + 0.2` is not exactly 0.3, which is why money is stored as integers. (Verified on Python 3.13.3.)

---

## ⚫ Interview Questions + Answers

Q1: What is the N+1 query problem and how do you fix it?
A1: You run 1 query to fetch N parent rows, then 1 query per parent for its children, so N+1 queries in total. Fix with a JOIN or eager loading: `selectinload` (2 queries, good for collections) or `joinedload` (1 query with JOIN, good for many-to-one). Detect it by logging query counts, as in the Advanced example (6 queries became 2).

Q2: How do indexes work and what is their cost?
A2: A B-tree index keeps a sorted copy of a column so lookups are O(log n) instead of a full scan. The cost: extra disk space and slower INSERT/UPDATE/DELETE because every index must be updated. Put indexes on columns in WHERE, JOIN and ORDER BY, and on foreign keys. Composite index order matters: `(user_id, created_at)` helps `WHERE user_id=? ORDER BY created_at` but not a filter on `created_at` alone.

Q3: What are ACID properties?
A3: Atomicity (all or nothing), Consistency (constraints always hold), Isolation (concurrent transactions do not see each other's half-done work), Durability (committed data survives a crash). Transactions provide these.

Q4: Why is keyset pagination better than OFFSET?
A4: `OFFSET n` makes the database walk past n rows every time, so deep pages become slow (O(n)). Keyset uses `WHERE id > last_seen ORDER BY id LIMIT k`, which uses the index to jump directly. Trade-off: you cannot jump to "page 57" directly, only next/previous, which suits infinite scroll and APIs.

Q5: How do you make an API write idempotent so retries are safe?
A5: Put a UNIQUE constraint on a natural key (payment id, idempotency key) and use `INSERT ... ON CONFLICT DO NOTHING/UPDATE` (PostgreSQL, SQLite) or `ON DUPLICATE KEY UPDATE` (MySQL). Retried requests then do not create duplicates. Combine with a transaction so side effects commit together.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production database work (these are defaults, not options)
- Money, orders, bookings: transactions plus constraints
- Large lists: keyset pagination and proper indexes
- ORM code: always check the generated SQL and query counts

❌ Avoid when (over-applying):
- Adding indexes before measuring; check `EXPLAIN` first
- Premature denormalization or caching before fixing queries
- Raw SQL everywhere when a simple ORM call is safe and clear
- Long transactions that hold locks while calling slow external APIs

---

## 📊 Visual Diagram
```
 Request ─► validate (Pydantic) ─► Session (pooled)
                                    │
        ┌───────────────────────────┴──────────────────────────┐
        │ BEGIN                                                │
        │   parameterized INSERT/UPDATE   (no string SQL)      │
        │   constraints: UNIQUE / CHECK / FK                   │
        │ COMMIT  (or ROLLBACK on error)                       │
        └───────────────────────────┬──────────────────────────┘
                                    ▼
 reads: index on WHERE/JOIN/ORDER ─► keyset page ─► 2 queries (selectin), not N+1
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SQL injection | Attacker input runs as SQL | Attacker का input SQL की तरह चलना |
| Index | Sorted lookup structure | Sorted lookup structure |
| N+1 | One query per row | हर row के लिए एक query |
| Eager loading | Load related rows in advance | जुड़े rows पहले से लोड करना |
| Keyset pagination | Page by last seen id | आखिरी देखे id से page करना |
| Idempotent | Repeat gives same result | दोहराने पर वही नतीजा |
| Upsert | Insert or update | Insert या update |
| Migration | Versioned schema change | Version वाला schema बदलाव |

---

## ⚡ 3-Line Summary
English: Use parameterized queries, transactions and constraints so data stays safe and correct. Make reads fast with indexes, eager loading and keyset pagination, and store money as integers or Decimal. Make writes idempotent with unique keys and upserts, and change schemas only through migrations.
Hindi: Data को सुरक्षित और सही रखने के लिए parameterized queries, transactions और constraints इस्तेमाल करें। Reads को तेज करने के लिए indexes, eager loading और keyset pagination लगाएं, और पैसा integers या Decimal में रखें। Writes को unique keys और upserts से idempotent बनाएं, और schema सिर्फ migrations से बदलें।

---

## ➡️ Next Topic
**374. NumPy Arrays** — leaving databases for the AI/ML section: NumPy's `ndarray` is the fast array that Pandas, scikit-learn and PyTorch are all built on.
