---

# 416. Database Query Optimization
# हिंदी में: Database Query Optimization (query को तेज़ बनाना)

---

## 🔵 Simple Definition (English)
Query optimization means making the database do less work for the same answer: add the right indexes, read only the rows and columns you need, avoid the N+1 query pattern, and paginate. Most slow APIs are slow because of the database, not Python.

## 🔵 सरल परिभाषा (Hindi)
Query optimization का मतलब है उसी जवाब के लिए database से कम काम करवाना: सही indexes लगाना, सिर्फ ज़रूरी rows और columns पढ़ना, N+1 query pattern से बचना और pagination करना। ज़्यादातर धीमे APIs की वजह Python नहीं, database होता है।

---

## 🔴 Problem it Solves
Without an index the database scans every row (a full table scan), so a lookup on 10 million rows takes seconds. ORMs make it easy to accidentally run one query per item (N+1) or to load whole tables into memory. These problems appear only when data grows, so a fast development database hides them.

## 🔴 यह क्यों बना? (Hindi)
Index के बिना database हर row स्कैन करता है (full table scan), इसलिए 1 करोड़ rows में lookup सेकंडों लेता है। ORM में गलती से हर item के लिए एक query (N+1) चल जाती है या पूरी table memory में आ जाती है। ये समस्याएँ data बढ़ने पर ही दिखती हैं, इसलिए छोटा development database इन्हें छिपा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Find the slow query (slow query log, APM, pg_stat_statements, logging)
Step 2 → Run EXPLAIN (ANALYZE) to see the plan: SCAN (bad) or SEARCH/Index (good)
Step 3 → Add an index on the columns used in WHERE / JOIN / ORDER BY
Step 4 → Select only needed columns; add LIMIT; paginate with keyset instead of big OFFSET
Step 5 → Remove N+1: JOIN, selectinload/joinedload, or one aggregate query
Step 6 → Re-run EXPLAIN and measure; remember each index slows down writes a little
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → धीमी query ढूँढें (slow query log, APM, pg_stat_statements, logging)
Step 2 → EXPLAIN (ANALYZE) से plan देखें: SCAN (बुरा) या SEARCH/Index (अच्छा)
Step 3 → WHERE / JOIN / ORDER BY वाले columns पर index लगाएँ
Step 4 → सिर्फ ज़रूरी columns लें; LIMIT लगाएँ; बड़े OFFSET की जगह keyset pagination
Step 5 → N+1 हटाएँ: JOIN, selectinload/joinedload या एक aggregate query
Step 6 → दोबारा EXPLAIN चलाकर मापें; याद रखें हर index writes को थोड़ा धीमा करता है
```

---

## 🟡 Real World Example
A Swiggy "my orders" API loads 20 orders and their items. The first version issues 1 query for orders plus 20 for items (21 queries, 400 ms). With `selectinload` it becomes 2 queries (15 ms). Adding an index on `orders(user_id, created_at)` removes a full scan of 50 million rows. Switching deep `OFFSET 100000` pages to keyset pagination keeps page 5000 as fast as page 1.

## 🟡 Real Example Hindi mein
Swiggy का "my orders" API 20 orders और उनके items लोड करता है। पहले version में orders के लिए 1 और items के लिए 20 queries (कुल 21, 400 ms) चलती हैं। `selectinload` से 2 queries (15 ms) हो जाती हैं। `orders(user_id, created_at)` पर index लगाने से 5 करोड़ rows का full scan हट जाता है। गहरे `OFFSET 100000` pages को keyset pagination में बदलने से page 5000 भी page 1 जितना तेज़ रहता है।

---

## 💻 Code Example — Basic
```python
# Basic: indexes and EXPLAIN QUERY PLAN with SQLite (standard library only)
import sqlite3  # built-in database
import timeit  # timer
from typing import List, Tuple  # type hints

conn: sqlite3.Connection = sqlite3.connect(":memory:")  # throwaway in-memory database
conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount INTEGER, status TEXT)")  # table
conn.executemany(  # insert 100,000 rows in one batch
    "INSERT INTO orders (user_id, amount, status) VALUES (?, ?, ?)",
    [(i % 5000, i % 997, "paid" if i % 3 else "pending") for i in range(100_000)],
)
conn.commit()  # save


def plan(sql: str, params: Tuple[int, ...]) -> str:
    rows: List[Tuple] = conn.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()  # ask the planner
    return rows[0][3]  # the human-readable plan text


QUERY: str = "SELECT COUNT(*) FROM orders WHERE user_id = ?"  # a very common lookup
print(plan(QUERY, (42,)))  # no index yet
# Output: SCAN orders

t_before: float = min(timeit.repeat(lambda: conn.execute(QUERY, (42,)).fetchone(), number=50, repeat=3))  # slow

conn.execute("CREATE INDEX idx_orders_user ON orders (user_id)")  # add an index on the filter column
print(plan(QUERY, (42,)))  # planner now uses it
# Output: SEARCH orders USING COVERING INDEX idx_orders_user (user_id=?)

t_after: float = min(timeit.repeat(lambda: conn.execute(QUERY, (42,)).fetchone(), number=50, repeat=3))  # fast
print("index made it at least 10x faster:", t_before / t_after > 10)  # full scan vs B-tree lookup
# Output: index made it at least 10x faster: True

print(conn.execute(QUERY, (42,)).fetchone()[0])  # same answer, 20 rows per user
# Output: 20

# SELECT only what you need, and always LIMIT lists
cols: List[Tuple[int, int]] = conn.execute(  # two columns, 3 rows
    "SELECT id, amount FROM orders WHERE user_id = ? ORDER BY id LIMIT 3", (42,)
).fetchall()
print(cols)  # first three orders of user 42 (amounts vary per row)
# Output: [(43, 42), (5043, 57), (10043, 72)]
```

## 💻 Code Example — Advanced
```python
# Advanced: N+1 queries vs eager loading, keyset pagination, query counting (pip install sqlalchemy)
from typing import List, Optional

from sqlalchemy import ForeignKey, create_engine, event, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload


class Base(DeclarativeBase):  # declarative base for models
    pass


class Author(Base):
    __tablename__ = "authors"  # table name
    id: Mapped[int] = mapped_column(primary_key=True)  # primary key
    name: Mapped[str]  # author name
    books: Mapped[List["Book"]] = relationship(back_populates="author")  # one-to-many


class Book(Base):
    __tablename__ = "books"  # table name
    id: Mapped[int] = mapped_column(primary_key=True)  # primary key
    title: Mapped[str]  # book title
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), index=True)  # FK with an index
    author: Mapped[Author] = relationship(back_populates="books")  # many-to-one


engine = create_engine("sqlite://")  # in-memory SQLite
Base.metadata.create_all(engine)  # create tables
counter: dict[str, int] = {"n": 0}  # number of SQL statements executed


@event.listens_for(engine, "before_cursor_execute")  # called for every SQL statement
def count_queries(conn, cursor, statement, parameters, context, executemany) -> None:
    counter["n"] += 1  # count it


with Session(engine) as s:  # seed 20 authors x 3 books
    s.add_all([Author(name=f"A{i}", books=[Book(title=f"B{i}-{j}") for j in range(3)]) for i in range(20)])
    s.commit()  # save

counter["n"] = 0  # reset the counter
with Session(engine) as s:  # BAD: N+1
    names: List[int] = [len(a.books) for a in s.scalars(select(Author))]  # 1 query + 1 per author
print("N+1 queries:", counter["n"])  # 1 + 20
# Output: N+1 queries: 21

counter["n"] = 0  # reset
with Session(engine) as s:  # GOOD: eager load
    names = [len(a.books) for a in s.scalars(select(Author).options(selectinload(Author.books)))]  # 2 queries
print("selectinload queries:", counter["n"])  # authors + one IN (...) query for all books
# Output: selectinload queries: 2

counter["n"] = 0  # reset
with Session(engine) as s:  # BEST for counts: let the database aggregate
    rows = s.execute(select(Author.name, func.count(Book.id)).join(Book).group_by(Author.id).limit(2)).all()
print(rows, "queries:", counter["n"])  # one query, no objects loaded
# Output: [('A0', 3), ('A1', 3)] queries: 1


def page_after(session: Session, last_id: Optional[int], size: int) -> List[int]:
    stmt = select(Book.id).order_by(Book.id).limit(size)  # stable order is required
    if last_id is not None:  # keyset: continue AFTER the last id (no OFFSET scan)
        stmt = stmt.where(Book.id > last_id)  # uses the primary-key index
    return list(session.scalars(stmt))  # ids of this page


with Session(engine) as s:  # keyset pagination demo
    first: List[int] = page_after(s, None, 5)  # first page
    second: List[int] = page_after(s, first[-1], 5)  # next page starts after the last id
print(first, second)  # consecutive pages
# Output: [1, 2, 3, 4, 5] [6, 7, 8, 9, 10]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (SQLAlchemy): eager load to avoid N+1
stmt = select(Author).options(selectinload(Author.books))
authors = session.scalars(stmt).all()
```
```javascript
// JavaScript (Prisma): include = eager load; without it you may loop and query per item
const authors = await prisma.author.findMany({ include: { books: true } });
// N+1 trap: for (const a of authors) await prisma.book.findMany({ where: { authorId: a.id } });
```

Key differences: the problem and the fix are identical in every ORM (Prisma `include`, Sequelize `include`, TypeORM `relations`, SQLAlchemy `selectinload`/`joinedload`). SQLAlchemy lazily loads relationships on attribute access by default, which is the usual source of N+1 in Python code.

---

## 🟠 FastAPI Connection
Give every endpoint a bounded `limit` (`Query(le=100)`), use keyset pagination for big tables, return Pydantic schemas with only the needed fields, and eager-load relationships. Use a per-request session through `Depends`. Log SQL in development (`create_engine(..., echo=True)`) to count queries per request.

```python
# FastAPI + SQLAlchemy: eager loading + pagination bounds (pip install fastapi sqlalchemy httpx)
from typing import Iterator, List

from fastapi import Depends, FastAPI, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):  # models base
    pass


class Author(Base):
    __tablename__ = "authors"  # table
    id: Mapped[int] = mapped_column(primary_key=True)  # pk
    name: Mapped[str]  # name
    books: Mapped[List["Book"]] = relationship()  # one-to-many


class Book(Base):
    __tablename__ = "books"  # table
    id: Mapped[int] = mapped_column(primary_key=True)  # pk
    title: Mapped[str]  # title
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), index=True)  # indexed FK


class AuthorOut(BaseModel):  # response schema: only the fields we need
    id: int
    name: str
    book_count: int


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)  # shared memory db
Base.metadata.create_all(engine)  # create tables
with Session(engine) as s:  # seed data
    s.add_all([Author(name=f"A{i}", books=[Book(title=f"t{i}{j}") for j in range(i % 3)]) for i in range(10)])
    s.commit()

app: FastAPI = FastAPI()  # create app


def get_db() -> Iterator[Session]:  # one session per request
    with Session(engine) as session:  # open
        yield session  # use in endpoint; closed afterwards


@app.get("/authors", response_model=List[AuthorOut])  # GET /authors?limit=3
def authors(limit: int = Query(5, ge=1, le=100), after_id: int = Query(0, ge=0), db: Session = Depends(get_db)) -> List[AuthorOut]:
    stmt = select(Author).where(Author.id > after_id).order_by(Author.id).limit(limit).options(selectinload(Author.books))  # keyset + eager load
    return [AuthorOut(id=a.id, name=a.name, book_count=len(a.books)) for a in db.scalars(stmt)]  # 2 queries total


client: TestClient = TestClient(app)  # test client
print(client.get("/authors", params={"limit": 3}).json())  # first page
# Output: [{'id': 1, 'name': 'A0', 'book_count': 0}, {'id': 2, 'name': 'A1', 'book_count': 1}, {'id': 3, 'name': 'A2', 'book_count': 2}]
print(client.get("/authors", params={"limit": 3, "after_id": 3}).json()[0]["id"])  # next page starts at 4
# Output: 4
print(client.get("/authors", params={"limit": 5000}).status_code)  # blocked by validation
# Output: 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Lazy loading inside a loop (N+1)
```python
# Wrong - one extra query per author:
for a in session.scalars(select(Author)):
    print(len(a.books))

# Correct:
for a in session.scalars(select(Author).options(selectinload(Author.books))):
    print(len(a.books))
```

❌ Mistake 2: Wrapping the indexed column in a function
```python
# Wrong - the index on user_id cannot be used (full scan):
"SELECT * FROM orders WHERE user_id + 0 = 42"
"SELECT * FROM orders WHERE abs(user_id) = 42"

# Correct - compare the raw column (or create an expression index):
"SELECT * FROM orders WHERE user_id = 42"
```

❌ Mistake 3: `SELECT *`, no LIMIT, deep OFFSET
```python
# Wrong - loads every column of every row, then skips 100000 rows:
"SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000"

# Correct - needed columns + keyset pagination:
"SELECT id, amount FROM orders WHERE id > :last_id ORDER BY id LIMIT 20"
```

---

## 🧠 Tricky Interview Question

**Q**: Table `t(id INTEGER PRIMARY KEY, user_id INTEGER, note TEXT)` has an index on `user_id`. What does SQLite's `EXPLAIN QUERY PLAN` show for each WHERE clause?

```python
for where in ["user_id = 42", "user_id + 0 = 42", "abs(user_id) = 42", "user_id IN (1, 2)"]:
    ...
```

**Answer**:
```
user_id = 42        -> SEARCH t USING INDEX i (user_id=?)
user_id + 0 = 42    -> SCAN t
abs(user_id) = 42   -> SCAN t
user_id IN (1, 2)   -> SEARCH t USING INDEX i (user_id=?)
```
An index can only be used when the indexed column appears "bare" in the condition. Applying arithmetic or a function to the column forces a full scan. `IN` with a list can still use the index. (The same rule applies in PostgreSQL and MySQL; there you can create an expression index such as `ON t (abs(user_id))`.)

---

## ⚫ Interview Questions + Answers

Q1: What is the N+1 problem and how do you fix it?
A1: One query loads N parents and then one more query per parent loads its children: N+1 round trips. Fix it with a JOIN, eager loading (`selectinload`/`joinedload`), or a single aggregate query.

Q2: How does an index speed up a query and what does it cost?
A2: A B-tree index finds rows in O(log n) instead of scanning O(n). It costs disk space and slows `INSERT/UPDATE/DELETE` because the index must be updated too. Index columns used in filters, joins and sorts, not everything.

Q3: What is a composite index and does column order matter?
A3: An index on several columns, e.g. `(user_id, created_at)`. Order matters: it serves queries that filter on the leftmost column(s) (`user_id`, or `user_id` + `created_at`) but not `created_at` alone.

Q4: Why is `OFFSET` slow for deep pages?
A4: The database must read and discard all skipped rows. Keyset pagination (`WHERE id > last_id ORDER BY id LIMIT n`) jumps directly using the index, so cost is constant. Its limitation is that you cannot jump to an arbitrary page number.

Q5: How do you find what to optimize?
A5: Measure: slow query log, `EXPLAIN ANALYZE`, `pg_stat_statements`, APM tracing, and counting queries per request. Optimize the slowest or most frequent query first, then re-measure.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- An endpoint is slow and EXPLAIN shows a table scan
- You see many near-identical queries per request (N+1)
- Tables grow past tens of thousands of rows

❌ Avoid when:
- The table is tiny (an index will not help)
- The table is write-heavy and you are tempted to index every column
- You have not measured: do not guess, and cache only after fixing the query

---

## 📊 Visual Diagram

```
No index:   WHERE user_id = 42      Index on user_id:  WHERE user_id = 42
 row1 row2 row3 ... row100000                 [B-tree]
 └── check every row (SCAN) ──┘                 /  |  \
        O(n)                                   ...  42 → row ids → rows
                                               O(log n)

N+1:   1 query (authors) + 20 queries (books per author) = 21 round trips
Fixed: 1 query (authors) + 1 query (books WHERE author_id IN (...)) = 2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | Structure for fast lookups | तेज़ खोज के लिए structure |
| Full table scan | Reading every row | हर row पढ़ना |
| EXPLAIN | Shows the query plan | query plan दिखाता है |
| N+1 | One query plus one per item | एक query और हर item पर एक और |
| Eager loading | Load related rows up front | related rows पहले ही लोड करना |
| Keyset pagination | Paging with WHERE id > last_id | WHERE id > last_id से pagination |

---

## ⚡ 3-Line Summary
English: Use EXPLAIN to find scans, add indexes on filter and join columns, and never wrap indexed columns in functions. Remove N+1 with eager loading or aggregates, select only what you need, and paginate with keyset. Measure before and after.
Hindi: EXPLAIN से scans ढूँढें, filter और join columns पर index लगाएँ और indexed column को function में न लपेटें। Eager loading या aggregate से N+1 हटाएँ, सिर्फ ज़रूरी data लें और keyset से pagination करें। पहले और बाद में मापें।

---

## ➡️ Next Topic
**417. Connection Pooling** — reuse database connections instead of opening a new one for every request.
