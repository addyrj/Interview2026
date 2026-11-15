---

# 332. Database with FastAPI (SQLAlchemy)
# हिंदी में: FastAPI के साथ Database (SQLAlchemy)

---

## 🔵 Simple Definition (English)
Connecting FastAPI to a database with SQLAlchemy means: one global `engine` (connection pool), a `sessionmaker`, and a `get_db` dependency that gives each request its own `Session` and closes it afterwards. Pydantic schemas are used for input and output, SQLAlchemy models for tables.

## 🔵 सरल परिभाषा (Hindi)
SQLAlchemy से FastAPI को database से जोड़ने का मतलब: एक global `engine` (connection pool), एक `sessionmaker`, और एक `get_db` dependency जो हर request को अपना `Session` देती है और बाद में उसे बंद करती है। Input/output के लिए Pydantic schemas और tables के लिए SQLAlchemy models उपयोग होते हैं।

---

## 🔴 Problem it Solves
Writing raw SQL strings in every route is repetitive and unsafe (SQL injection). Opening a new DB connection per request is slow, and forgetting to close it leaks connections until the database refuses new ones. The engine + session-per-request pattern gives pooled connections, automatic cleanup, transactions, and Python objects instead of tuples.

## 🔴 यह क्यों बना? (Hindi)
हर route में raw SQL strings लिखना दोहराव वाला और असुरक्षित (SQL injection) है। हर request पर नया DB connection खोलना धीमा है, और उसे बंद करना भूलने पर connections leak होते हैं जब तक database नए connections लेना बंद न कर दे। Engine + session-per-request pattern से pooled connections, automatic cleanup, transactions, और tuples की जगह Python objects मिलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → create_engine(url) once at startup (owns the connection pool)
Step 2 → sessionmaker(bind=engine) is a factory for Session objects
Step 3 → Request arrives; Depends(get_db) creates a new Session
Step 4 → Route uses the session: add / get / select / commit
Step 5 → Route returns an ORM object; response_model converts it to JSON
Step 6 → "finally" in get_db closes the session; connection returns to the pool
Step 7 → On an exception, uncommitted work is rolled back when the session closes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → create_engine(url) startup पर एक बार (connection pool का मालिक)
Step 2 → sessionmaker(bind=engine) Session objects बनाने की factory है
Step 3 → Request आती है; Depends(get_db) नया Session बनाता है
Step 4 → Route session उपयोग करता है: add / get / select / commit
Step 5 → Route ORM object return करता है; response_model उसे JSON बनाता है
Step 6 → get_db का "finally" session बंद करता है; connection pool में लौट जाता है
Step 7 → Exception पर uncommitted काम session बंद होते समय rollback हो जाता है
```

---

## 🟡 Real World Example
A Zomato-style restaurant service: `POST /restaurants` inserts a row, `GET /restaurants/{id}` reads it, and a unique constraint on the licence number returns a clean `409 Conflict`. Each request gets its own session, so two users ordering at the same time never share half-finished transactions.

## 🟡 Real Example Hindi mein
Zomato जैसी restaurant service: `POST /restaurants` एक row insert करता है, `GET /restaurants/{id}` उसे पढ़ता है, और licence number पर unique constraint साफ `409 Conflict` लौटाता है। हर request का अपना session होता है, इसलिए एक साथ order करने वाले दो users कभी अधूरे transactions share नहीं करते।

---

## 💻 Code Example — Basic
```python
# Basic: SQLAlchemy 2.0 ORM CRUD without FastAPI (in-memory SQLite)
from sqlalchemy import String, create_engine, select      # engine factory + select()
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column   # ORM tools

engine = create_engine("sqlite://")                       # in-memory SQLite database


class Base(DeclarativeBase):                              # base class of all models
    pass                                                  # nothing extra needed


class Product(Base):                                      # a table
    __tablename__ = "products"                            # real table name
    id: Mapped[int] = mapped_column(primary_key=True)     # integer primary key
    name: Mapped[str] = mapped_column(String(50))         # VARCHAR(50), NOT NULL
    price: Mapped[int]                                    # INTEGER, NOT NULL


Base.metadata.create_all(engine)                          # CREATE TABLE if missing
with Session(engine) as session:                          # session closes automatically
    session.add_all([Product(name="Pen", price=10), Product(name="Book", price=250)])   # stage inserts
    session.commit()                                      # write to the database
    rows = session.scalars(select(Product).where(Product.price > 100)).all()   # SELECT ... WHERE
    print([(p.id, p.name, p.price) for p in rows])        # plain tuples for display
    first = session.get(Product, 1)                       # fetch by primary key
    first.price = 12                                      # change attribute (tracked)
    session.commit()                                      # UPDATE is sent
    print(session.get(Product, 1).price)                  # read it back
    session.delete(first)                                 # stage a DELETE
    session.commit()                                      # DELETE is sent
    print(session.scalars(select(Product.name)).all())    # remaining names

# Output (verified, SQLAlchemy 2.x):
# [(2, 'Book', 250)]
# 12
# ['Book']
```

## 💻 Code Example — Advanced
```python
# Production style: engine + sessionmaker + get_db dependency + schemas + error handling
from collections.abc import Generator                     # type of a generator dependency
from typing import Annotated                              # reusable dependency alias
from fastapi import Depends, FastAPI, HTTPException       # FastAPI core
from fastapi.testclient import TestClient                 # in-process test client
from pydantic import BaseModel, ConfigDict                # request/response schemas
from sqlalchemy import String, create_engine, select      # engine + select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool                    # one shared connection (test only)

# production: create_engine("postgresql+psycopg://user:pw@host/db", pool_size=10, pool_pre_ping=True)
engine = create_engine(                                   # engine = connection pool
    "sqlite://",                                          # in-memory DB for this demo
    connect_args={"check_same_thread": False},            # SQLite: allow use from worker threads
    poolclass=StaticPool,                                 # keep ONE connection so memory DB survives
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)   # session factory


class Base(DeclarativeBase):                              # models base
    pass                                                  # empty


class User(Base):                                         # users table
    __tablename__ = "users"                               # table name
    id: Mapped[int] = mapped_column(primary_key=True)     # primary key
    email: Mapped[str] = mapped_column(String(120), unique=True)   # unique email
    name: Mapped[str] = mapped_column(String(80))         # display name


class UserIn(BaseModel):                                  # request body schema
    email: str                                            # required
    name: str                                             # required


class UserOut(BaseModel):                                 # response schema
    model_config = ConfigDict(from_attributes=True)       # allow reading from ORM objects
    id: int                                               # include id
    email: str                                            # include email
    name: str                                             # include name


def get_db() -> Generator[Session, None, None]:           # dependency: one session per request
    db: Session = SessionLocal()                          # create session
    try:                                                  # guarantee cleanup
        yield db                                          # hand it to the route
    finally:                                              # always runs
        db.close()                                        # return connection to the pool


DB = Annotated[Session, Depends(get_db)]                  # short alias for route signatures
app: FastAPI = FastAPI()                                  # create app
Base.metadata.create_all(engine)                          # demo only; use Alembic in production


@app.post("/users", response_model=UserOut, status_code=201)   # create user
def create_user(payload: UserIn, db: DB) -> User:         # def => thread pool (sync driver)
    if db.scalar(select(User).where(User.email == payload.email)):   # duplicate check
        raise HTTPException(409, "email already exists")  # clean 409 instead of a 500
    user: User = User(**payload.model_dump())             # schema -> ORM object
    db.add(user)                                          # stage insert
    db.commit()                                           # save (id is now filled)
    return user                                           # response_model converts to JSON


@app.get("/users/{user_id}", response_model=UserOut)      # read user
def get_user(user_id: int, db: DB) -> User:               # path param + session
    user: User | None = db.get(User, user_id)             # primary key lookup
    if user is None:                                      # not found
        raise HTTPException(404, "user not found")        # 404 response
    return user                                           # serialized by UserOut


client = TestClient(app)                                  # test client
print(client.post("/users", json={"email": "a@x.com", "name": "Asha"}).json())   # create
print(client.post("/users", json={"email": "a@x.com", "name": "Asha"}).status_code)   # duplicate
print(client.get("/users/1").json())                      # read
print(client.get("/users/99").json())                     # missing

# Output (verified):
# {'id': 1, 'email': 'a@x.com', 'name': 'Asha'}
# 409
# {'id': 1, 'email': 'a@x.com', 'name': 'Asha'}
# {'detail': 'user not found'}
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (SQLAlchemy) | JavaScript (Prisma / TypeORM) |
|---------|---------------------|-------------------------------|
| Pool | `create_engine(...)` | built into client |
| Per-request unit | `Session` | `prisma` client / `EntityManager` |
| Transaction | `session.commit()` | `prisma.$transaction` |
| Schema source | Python classes | `schema.prisma` / decorators |
| Migrations | Alembic | `prisma migrate` / TypeORM migrations |

```python
# Python way
with Session(engine) as s:                      # scoped session
    s.add(User(email="a@x.com", name="Asha"))   # stage insert
    s.commit()                                  # write it
```
```javascript
// JavaScript way (Prisma)
await prisma.user.create({                      // insert immediately
  data: { email: "a@x.com", name: "Asha" },     // data to insert
});                                             // each call is its own query
```

Key difference: SQLAlchemy keeps a unit-of-work in the Session, so nothing is written until `commit()` (or `flush()`). Prisma sends a query on every call.

---

## 🟠 FastAPI Connection
`Depends(get_db)` is THE standard FastAPI database pattern. A `yield` dependency runs the code before `yield` at request start and the code after `yield` (the `finally`) after the response is prepared. For tests you can swap it with `app.dependency_overrides[get_db] = override_get_db` to use a test database.

```python
# FastAPI example — override the DB dependency in tests
def override_get_db():                                   # test session provider
    db = SessionLocal()                                  # test session
    try:
        yield db                                         # give it to routes
    finally:
        db.close()                                       # cleanup

app.dependency_overrides[get_db] = override_get_db       # FastAPI uses this instead of get_db
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One global Session shared by all requests
✅ Correct: one Session per request via `Depends(get_db)`

```python
# Wrong — threads share state and see each other's half-done transactions
db = SessionLocal()                    # module-level session
# Right
def get_db():                          # per-request session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

❌ Mistake 2: Returning the ORM object without `from_attributes=True` / response_model
✅ Correct: set `ConfigDict(from_attributes=True)` on the response schema

```python
# Wrong — validation error: can't read attributes of an ORM object
class UserOut(BaseModel):
    id: int
# Right
class UserOut2(BaseModel):
    model_config = ConfigDict(from_attributes=True)    # Pydantic v2 (was orm_mode in v1)
    id: int
```

❌ Mistake 3: Forgetting `commit()` (or accessing attributes after the session closed)
✅ Correct: commit before returning, and use `expire_on_commit=False` when you return objects after commit

```python
# Wrong — data is never saved
db.add(User(email="x@x.com", name="X"))
# Right
db.add(User(email="x@x.com", name="X"))
db.commit()
```

---

## 🧠 Tricky Interview Question

```python
# What does this print?
with Session(engine) as s:
    p = Product(name="Pen", price=10)
    s.add(p)
    print(p.id)          # (1)
    s.flush()
    print(p.id)          # (2)
    s.rollback()
    print(s.scalars(select(Product)).all())   # (3)
```
Answer: (1) prints `None`: the object is only staged, no INSERT has run. (2) After `flush()` the INSERT is sent inside the transaction and the database fills `id`, so it prints `1`. (3) `rollback()` undoes the flushed INSERT, so the table is empty and it prints `[]`. `flush` writes SQL but does not commit; `commit` = flush + COMMIT.

---

## ⚫ Interview Questions + Answers

Q1: Why use a dependency with `yield` for the database session?
A1: It gives each request its own Session and guarantees `close()` in `finally`, even on exceptions. The code is reusable across routes and replaceable in tests via `dependency_overrides`.

Q2: Why must a SQLite database use `check_same_thread=False` with FastAPI?
A2: `def` routes run in thread-pool threads, and SQLite connections by default may only be used by the thread that created them. This flag allows sharing. It is not needed for PostgreSQL.

Q3: What does `pool_pre_ping=True` do?
A3: Before handing out a pooled connection, SQLAlchemy sends a light "ping". Dead connections (DB restart, network idle timeout) are replaced instead of crashing a request.

Q4: Should you use `Base.metadata.create_all` in production?
A4: No. It only creates missing tables and never alters existing ones. Use Alembic migrations so schema changes are versioned and reversible.

Q5: Why separate Pydantic schemas from ORM models?
A5: ORM models describe tables; schemas describe what the API accepts and returns. Separating them avoids leaking fields like `password_hash` and lets the API change independently from the database.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want relational data with transactions (orders, payments, users)
- Your team is fine with sync drivers (`def` routes) for moderate traffic
- You want a type-safe ORM and migrations

❌ Avoid when:
- You need very high concurrency on I/O: use async SQLAlchemy (topic 337)
- Your data is document-shaped: consider MongoDB/Beanie (topic 339)
- You only need a few raw queries: SQLAlchemy Core or raw `text()` is lighter

---

## 📊 Visual Diagram
```
 Request ──► Depends(get_db) ──► Session ──► Engine/Pool ──► PostgreSQL
    ▲              │                │
    │              │ yield          │ commit / rollback
    │              ▼                ▼
 Response ◄── response_model ◄── ORM object
                   │
                   └── finally: db.close()  (connection back to pool)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Engine | Holds the connection pool | Connection pool रखने वाला object |
| Session | Unit of work for one request | एक request का काम-इकाई |
| `sessionmaker` | Factory that makes sessions | Session बनाने की factory |
| Dependency | Function FastAPI calls for you | FastAPI द्वारा call होने वाला function |
| `flush` | Send SQL without committing | बिना commit SQL भेजना |
| `from_attributes` | Pydantic reads ORM attributes | ORM attributes से Pydantic भरना |

---

## ⚡ 3-Line Summary
English: Create one engine and a sessionmaker, then give every request its own Session through a `yield` dependency. Use Pydantic schemas for input/output and `from_attributes=True` to return ORM objects. Use Alembic, not `create_all`, in production.
Hindi: एक engine और sessionmaker बनाएं, फिर `yield` dependency से हर request को अपना Session दें। Input/output के लिए Pydantic schemas और ORM objects return करने के लिए `from_attributes=True` उपयोग करें। Production में `create_all` नहीं, Alembic उपयोग करें।

---

## ➡️ Next Topic
**333. Alembic Migrations** — versioned, reversible schema changes so your database evolves safely with your models.
