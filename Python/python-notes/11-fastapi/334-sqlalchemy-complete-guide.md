---

# 334. SQLAlchemy — Complete Guide
# हिंदी में: SQLAlchemy — पूरी गाइड (Models, Relationships, Queries, Transactions)

---

## 🔵 Simple Definition (English)
SQLAlchemy is Python's main database toolkit. It has two layers: Core (SQL expressions, tables, connections) and ORM (Python classes mapped to tables, with a Session that tracks changes). You describe tables as classes, and SQLAlchemy writes the SQL for any database: PostgreSQL, MySQL, SQLite, and more.

## 🔵 सरल परिभाषा (Hindi)
SQLAlchemy Python का मुख्य database toolkit है। इसकी दो परतें हैं: Core (SQL expressions, tables, connections) और ORM (Python classes जो tables से map होती हैं, और Session जो बदलाव track करता है)। आप tables को classes की तरह लिखते हैं और SQLAlchemy किसी भी database (PostgreSQL, MySQL, SQLite आदि) के लिए SQL बनाता है।

---

## 🔴 Problem it Solves
Raw SQL strings scatter across code, differ per database, are prone to injection, and return untyped tuples. Relationships (author -> posts) need manual joins and manual object assembly. SQLAlchemy gives typed models, portable queries, parameter binding by default, relationships that load as lists, and a unit-of-work that groups changes into a transaction.

## 🔴 यह क्यों बना? (Hindi)
Raw SQL strings code में बिखरी रहती हैं, हर database में अलग होती हैं, injection का खतरा रहता है, और untyped tuples देती हैं। Relationships (author -> posts) के लिए हाथ से joins और objects जोड़ने पड़ते हैं। SQLAlchemy typed models, portable queries, default parameter binding, list की तरह load होने वाली relationships, और बदलावों को एक transaction में जोड़ने वाला unit-of-work देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare models: class X(Base) with Mapped[...] = mapped_column(...)
Step 2 → relationship() links classes; ForeignKey() links tables
Step 3 → Query with select(Model).where(...).order_by(...) (a SQL expression)
Step 4 → session.execute / scalars sends SQL via the Engine connection
Step 5 → Rows become ORM objects stored in the session's identity map
Step 6 → Changing attributes marks objects "dirty"
Step 7 → commit() flushes INSERT/UPDATE/DELETE in the right order, then COMMITs
Step 8 → On error: rollback() undoes the whole transaction
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Models लिखें: class X(Base) में Mapped[...] = mapped_column(...)
Step 2 → relationship() classes जोड़ता है; ForeignKey() tables जोड़ता है
Step 3 → select(Model).where(...).order_by(...) से query (SQL expression) बनाएं
Step 4 → session.execute / scalars Engine connection से SQL भेजता है
Step 5 → Rows ORM objects बनते हैं जो session के identity map में रहते हैं
Step 6 → Attributes बदलने पर objects "dirty" mark होते हैं
Step 7 → commit() सही क्रम में INSERT/UPDATE/DELETE flush करता है, फिर COMMIT
Step 8 → Error पर: rollback() पूरा transaction undo कर देता है
```

---

## 🟡 Real World Example
A blogging or e-commerce backend: `Customer` has many `Order`s, each order has a unique reference per customer, every row has `created_at`. Placing an order creates the customer if needed and inserts the order in one transaction; a duplicate reference triggers `IntegrityError` and everything rolls back, so no half-created customer is left behind.

## 🟡 Real Example Hindi mein
Blog या e-commerce backend: `Customer` के कई `Order` हैं, हर customer के लिए order reference unique है, हर row में `created_at` है। Order देने पर customer (अगर नहीं है) और order एक ही transaction में बनते हैं; duplicate reference पर `IntegrityError` आता है और सब कुछ rollback हो जाता है, इसलिए आधा बना customer नहीं बचता।

---

## 💻 Code Example — Basic
```python
# Basic: one-to-many relationship, eager loading, aggregate, cascade delete
from sqlalchemy import ForeignKey, String, create_engine, func, select   # core pieces
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            relationship, selectinload)       # ORM pieces


class Base(DeclarativeBase):                                  # models base class
    pass                                                      # nothing needed


class Author(Base):                                           # "one" side
    __tablename__ = "authors"                                 # table name
    id: Mapped[int] = mapped_column(primary_key=True)         # PK
    name: Mapped[str] = mapped_column(String(50))             # NOT NULL string
    posts: Mapped[list["Post"]] = relationship(               # Author.posts -> list of Post
        back_populates="author", cascade="all, delete-orphan")   # deleting author deletes posts


class Post(Base):                                             # "many" side
    __tablename__ = "posts"                                   # table name
    id: Mapped[int] = mapped_column(primary_key=True)         # PK
    title: Mapped[str] = mapped_column(String(100))           # title
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))   # FK column
    author: Mapped[Author] = relationship(back_populates="posts")      # Post.author -> Author


engine = create_engine("sqlite://")                           # in-memory DB
Base.metadata.create_all(engine)                              # create tables
with Session(engine) as s:                                    # open a session
    a = Author(name="Ravi", posts=[Post(title="Intro"), Post(title="Async")])   # build objects
    b = Author(name="Neha", posts=[Post(title="SQL")])        # another author
    s.add_all([a, b])                                         # stage both (posts cascade)
    s.commit()                                                # INSERT everything
    authors = s.scalars(                                      # scalars() = ORM objects
        select(Author).options(selectinload(Author.posts)).order_by(Author.name)   # 2 queries, no N+1
    ).all()                                                   # fetch list
    for au in authors:                                        # iterate authors
        print(au.name, [p.title for p in au.posts])           # posts already loaded
    counts = s.execute(                                       # execute() = rows
        select(Author.name, func.count(Post.id)).join(Post).group_by(Author.id).order_by(Author.name)
    ).all()                                                   # name + number of posts
    print(counts)                                             # list of Row tuples
    s.delete(a)                                               # delete Ravi
    s.commit()                                                # cascade removes his posts
    print(s.scalar(select(func.count()).select_from(Post)))   # posts left

# Output (verified):
# Neha ['SQL']
# Ravi ['Intro', 'Async']
# [('Neha', 1), ('Ravi', 2)]
# 1
```

## 💻 Code Example — Advanced
```python
# Production style: mixin, constraints, FK enforcement, transaction helper, rollback on error
from datetime import datetime, timezone                       # timezone-aware timestamps
from sqlalchemy import ForeignKey, String, UniqueConstraint, create_engine, event, func, select
from sqlalchemy.exc import IntegrityError                     # constraint violation error
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):                                  # base class
    pass                                                      # empty


class TimestampMixin:                                         # reusable column(s)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))   # set on insert


class Customer(TimestampMixin, Base):                         # customers table
    __tablename__ = "customers"                               # name
    id: Mapped[int] = mapped_column(primary_key=True)         # PK
    email: Mapped[str] = mapped_column(String(120), unique=True)   # unique email
    orders: Mapped[list["Order"]] = relationship(back_populates="customer", cascade="all, delete-orphan")


class Order(TimestampMixin, Base):                            # orders table
    __tablename__ = "orders"                                  # name
    __table_args__ = (UniqueConstraint("customer_id", "ref"),)   # a ref is unique per customer
    id: Mapped[int] = mapped_column(primary_key=True)         # PK
    ref: Mapped[str] = mapped_column(String(20))              # order reference
    total: Mapped[int]                                        # amount in paise/rupees
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))   # FK
    customer: Mapped[Customer] = relationship(back_populates="orders")     # back reference


engine = create_engine("sqlite://")                           # demo database


@event.listens_for(engine, "connect")                         # run on every new DBAPI connection
def fk_on(dbapi_conn, _):                                     # SQLite ignores FKs unless enabled
    dbapi_conn.execute("PRAGMA foreign_keys=ON")              # turn FK enforcement on


Base.metadata.create_all(engine)                              # create tables
SessionLocal = sessionmaker(engine, expire_on_commit=False)   # session factory


def place_order(email: str, ref: str, total: int) -> Order:   # business function
    with SessionLocal.begin() as s:                           # begin(): commit on success, rollback on error
        cust: Customer | None = s.scalar(select(Customer).where(Customer.email == email))   # lookup
        if cust is None:                                      # first order of this customer
            cust = Customer(email=email)                      # create customer
            s.add(cust)                                       # stage it
        order = Order(ref=ref, total=total, customer=cust)    # build order
        s.add(order)                                          # stage it
    return order                                              # committed here (block ended)


o = place_order("a@x.com", "R1", 500)                         # first order works
print(o.id, o.ref, o.created_at.tzinfo)                       # id, ref, tz of created_at
try:                                                          # same (customer, ref) again
    place_order("a@x.com", "R1", 999)                         # violates UniqueConstraint
except IntegrityError as e:                                   # database rejected it
    print("rolled back:", type(e).__name__)                   # whole transaction undone
with SessionLocal() as s:                                     # new session to verify
    print(s.scalar(select(func.sum(Order.total))))            # only the first order exists

# Output (verified):
# 1 R1 UTC
# rolled back: IntegrityError
# 500
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (SQLAlchemy) | JavaScript (TypeORM / Prisma) |
|---------|---------------------|-------------------------------|
| Model | class + `Mapped[]` | class + decorators / schema file |
| Relationship | `relationship()` | `@OneToMany` / `include:` |
| Query | `select(User).where(...)` | `repo.find({ where })` / `prisma.user.findMany` |
| Eager load | `selectinload` | `relations: [...]` / `include` |
| Transaction | `with Session.begin():` | `$transaction([...])` |
| Raw SQL | `text("...")` + params | `$queryRaw` |

```python
# Python way — query + eager load
stmt = select(Author).options(selectinload(Author.posts)).where(Author.name == "Ravi")   # expression
author = session.scalars(stmt).first()               # run it
```
```javascript
// JavaScript way — Prisma
const author = await prisma.author.findFirst({       // run query
  where: { name: "Ravi" },                           // filter
  include: { posts: true },                          // eager load posts
});
```

Key difference: SQLAlchemy builds a SQL expression object first; nothing hits the database until you execute it. The Session also tracks changes automatically (unit of work).

---

## 🟠 FastAPI Connection
In FastAPI, SQLAlchemy models live in `models.py`, Pydantic schemas in `schemas.py`, and queries in a repository/service layer that receives the `Session` from `Depends(get_db)`. Keep transaction boundaries in the service or route (commit once per request) rather than scattered in helpers.

```python
# FastAPI example — service function receives the session (testable, no globals)
from fastapi import APIRouter, Depends                   # routing + DI
from sqlalchemy.orm import Session                       # type hint

router = APIRouter(prefix="/orders")                     # group routes


@router.post("/")                                        # create order endpoint
def create(email: str, ref: str, total: int, db: Session = Depends(get_db)) -> dict[str, int]:
    cust = db.scalar(select(Customer).where(Customer.email == email))   # find customer
    if cust is None:                                     # new customer
        cust = Customer(email=email)                     # create
    order = Order(ref=ref, total=total, customer=cust)   # build order
    db.add(order)                                        # stage (cascades customer)
    db.commit()                                          # one transaction per request
    return {"id": order.id}                              # response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: The N+1 query problem (lazy loading in a loop)
✅ Correct: `selectinload` (collections) or `joinedload` (single objects)

```python
# Wrong — 1 query for authors + 1 query PER author for posts
for a in session.scalars(select(Author)):
    print(len(a.posts))
# Right — 2 queries total
for a in session.scalars(select(Author).options(selectinload(Author.posts))):
    print(len(a.posts))
```

❌ Mistake 2: Using the object after the session closed (DetachedInstanceError)
✅ Correct: load what you need before closing, or `expire_on_commit=False`, or return Pydantic data

```python
# Wrong
with Session(engine) as s:
    a = s.get(Author, 1)
print(a.posts)          # lazy load on a closed session -> DetachedInstanceError
# Right
with Session(engine) as s:
    a = s.scalars(select(Author).options(selectinload(Author.posts))).first()
print(len(a.posts))     # already loaded
```

❌ Mistake 3: Building SQL with f-strings
✅ Correct: bound parameters

```python
# Wrong — SQL injection
session.execute(text(f"SELECT * FROM users WHERE email = '{email}'"))
# Right
session.execute(text("SELECT * FROM users WHERE email = :e"), {"e": email})
```

---

## 🧠 Tricky Interview Question

```python
# How many SQL queries run here?  (Author has 100 rows, each with posts)
with Session(engine) as s:
    for a in s.scalars(select(Author)):
        print(len(a.posts))
```
Answer: 101 queries: one `SELECT` for authors, then one lazy-load `SELECT` per author when `a.posts` is first accessed (the N+1 problem). With `.options(selectinload(Author.posts))` it becomes 2 queries; with `joinedload` it is 1 query with a JOIN (but rows multiply, so prefer `selectinload` for collections). Turn on `create_engine(..., echo=True)` to count them.

---

## ⚫ Interview Questions + Answers

Q1: What is the Session's identity map?
A1: A per-session cache keyed by (class, primary key). Loading the same row twice in one session returns the same Python object. It enables change tracking and avoids duplicate objects.

Q2: Difference between `flush()` and `commit()`?
A2: `flush()` sends pending SQL to the database inside the current transaction (ids get filled) but can still be rolled back. `commit()` flushes and then commits the transaction, making it permanent.

Q3: Lazy vs eager loading?
A3: Lazy (default) loads related rows on first attribute access, one query each. Eager strategies (`selectinload`, `joinedload`, `subqueryload`) load them up front. Choose eager to avoid N+1.

Q4: `session.get()` vs `select(...).where(id==...)`?
A4: `session.get(Model, pk)` checks the identity map first and may skip the query entirely; a `select` always hits the database.

Q5: How do you prevent lost updates when two requests edit the same row?
A5: Use pessimistic locking with `select(...).with_for_update()`, or optimistic locking with a version column (`__mapper_args__ = {"version_id_col": version}`), which raises `StaleDataError` on conflict.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have relational data, transactions and relationships
- You want portability between databases and typed models
- You want migrations (with Alembic)

❌ Avoid when:
- Bulk loading millions of rows: use Core `insert()` or `COPY` (topic 335)
- Pure analytics: use SQL directly or pandas/DuckDB
- Schema-less documents: use MongoDB (topic 339)

---

## 📊 Visual Diagram
```
 Python objects         Session (unit of work)         Database
 ───────────────        ──────────────────────        ──────────
 Author ──► posts   ──► identity map + dirty list ──► authors
 Post   ◄── author       add / delete / modify         posts
                                │
             flush() ───────────┤ INSERT/UPDATE/DELETE (in order)
             commit() ──────────┘ COMMIT  (rollback() = undo)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ORM | Maps classes to tables | Classes को tables से जोड़ना |
| Session | Tracks objects and transactions | Objects और transactions का tracker |
| Identity map | Same row = same object per session | एक session में एक row = एक object |
| N+1 | One query plus one per row | एक query और हर row पर एक और |
| Cascade | Apply action to related objects | संबंधित objects पर भी action |
| `IntegrityError` | Constraint violated | Constraint टूटने की error |

---

## ⚡ 3-Line Summary
English: SQLAlchemy maps classes to tables and a Session tracks your changes as one transaction. Use relationships with `selectinload` to avoid N+1 queries, and `Session.begin()` so errors roll back. Never build SQL with f-strings.
Hindi: SQLAlchemy classes को tables से map करता है और Session आपके बदलावों को एक transaction की तरह track करता है। N+1 queries से बचने के लिए relationships के साथ `selectinload` उपयोग करें, और `Session.begin()` से error पर rollback पाएं। SQL में कभी f-strings न लगाएं।

---

## ➡️ Next Topic
**335. SQLAlchemy ORM vs Core** — when the lightweight SQL expression layer beats the ORM (bulk inserts are about 18x faster in our test).
