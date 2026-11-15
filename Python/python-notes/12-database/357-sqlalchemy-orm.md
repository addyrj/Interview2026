---

# 357. SQLAlchemy ORM
# हिंदी में: SQLAlchemy ORM (Python classes से database tables)

---

## 🔵 Simple Definition (English)
The SQLAlchemy ORM maps a Python class to a database table and each object to a row. You write `select(User).where(User.age > 18)` in Python and SQLAlchemy builds the SQL. This guide uses the modern 2.0 style (`DeclarativeBase`, `Mapped`, `mapped_column`).

## 🔵 सरल परिभाषा (Hindi)
SQLAlchemy ORM एक Python class को database table से और हर object को एक row से जोड़ता है। आप Python में `select(User).where(User.age > 18)` लिखते हैं और SQLAlchemy SQL बना देता है। यह guide आधुनिक 2.0 style (`DeclarativeBase`, `Mapped`, `mapped_column`) इस्तेमाल करती है।

---

## 🔴 Problem it Solves
Raw SQL strings are easy to get wrong, are not checked by the editor, and every result row is an anonymous tuple. You also write the same INSERT/SELECT code again and again, and switching from SQLite to PostgreSQL means rewriting queries. An ORM gives typed classes, autocomplete, safe parameter binding, and one query language for many databases.

## 🔴 यह क्यों बना? (Hindi)
Raw SQL strings में गलती आसान है, editor उन्हें check नहीं करता और हर result row एक anonymous tuple होती है। एक जैसे INSERT/SELECT code बार-बार लिखना पड़ता है, और SQLite से PostgreSQL जाने पर queries फिर से लिखनी पड़ती हैं। ORM typed classes, autocomplete, सुरक्षित parameter binding और कई databases के लिए एक ही query language देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → create_engine("sqlite:///app.db") builds the connection pool + dialect
Step 2 → class Base(DeclarativeBase) is the parent of all models
Step 3 → class User(Base) with Mapped[...] columns describes a table
Step 4 → Base.metadata.create_all(engine) creates the tables (dev/test only; use Alembic in prod)
Step 5 → A Session collects objects: session.add(obj)
Step 6 → session.commit() flushes the INSERT/UPDATE SQL in one transaction
Step 7 → session.scalars(select(User)...) runs a query and returns User objects
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → create_engine("sqlite:///app.db") connection pool + dialect बनाता है
Step 2 → class Base(DeclarativeBase) सभी models की parent class है
Step 3 → Mapped[...] columns वाली class User(Base) table बताती है
Step 4 → Base.metadata.create_all(engine) tables बनाता है (सिर्फ dev/test; production में Alembic)
Step 5 → Session objects इकट्ठा करता है: session.add(obj)
Step 6 → session.commit() INSERT/UPDATE SQL एक transaction में भेजता है
Step 7 → session.scalars(select(User)...) query चलाकर User objects लौटाता है
```

---

## 🟡 Real World Example
A Zomato-style restaurant service has `Restaurant` and `MenuItem` models. A search endpoint filters by city and rating, orders by rating, and paginates, all in Python. When the team moves from SQLite in tests to PostgreSQL in production, only the connection URL changes.

## 🟡 Real Example Hindi mein
Zomato जैसी restaurant service में `Restaurant` और `MenuItem` models हैं। Search endpoint city और rating से filter, rating से order और pagination सब Python में करता है। Tests में SQLite से production में PostgreSQL जाने पर सिर्फ connection URL बदलता है।

---

## 💻 Code Example — Basic
```python
# Basic SQLAlchemy 2.0 ORM (in-memory SQLite, runs as is)
from sqlalchemy import create_engine, select              # engine + select()
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column   # ORM parts


class Base(DeclarativeBase):                              # parent of all models
    pass


class User(Base):                                         # one class = one table
    __tablename__ = "users"                               # table name
    id: Mapped[int] = mapped_column(primary_key=True)     # integer primary key
    name: Mapped[str]                                     # NOT NULL VARCHAR (non-Optional)
    age: Mapped[int | None]                               # nullable column (Optional)

    def __repr__(self) -> str:                            # nice printing
        return f"User(id={self.id}, name={self.name!r}, age={self.age})"


engine = create_engine("sqlite:///:memory:")              # throw-away database
Base.metadata.create_all(engine)                          # CREATE TABLE users

with Session(engine) as session:                          # unit of work
    session.add_all([User(name="Asha", age=25), User(name="Ravi", age=17), User(name="Meena")])   # stage 3 rows
    session.commit()                                      # INSERT them in one transaction

    adults = session.scalars(select(User).where(User.age >= 18)).all()   # WHERE age >= 18
    print(adults)                                         # list of User objects
    first = session.get(User, 2)                          # lookup by primary key
    print(first)                                          # Ravi
    first.age = 18                                        # change an attribute
    session.commit()                                      # UPDATE is generated automatically
    print(session.scalar(select(User.age).where(User.id == 2)))   # 18
    session.delete(first)                                 # mark for deletion
    session.commit()                                      # DELETE
    print(session.scalars(select(User.name).order_by(User.name)).all())   # remaining names

# Output:
# [User(id=1, name='Asha', age=25)]
# User(id=2, name='Ravi', age=17)
# 18
# ['Asha', 'Meena']
```

## 💻 Code Example — Advanced
```python
# Production style: typed models, constraints, repository class, bulk ops, error handling
from datetime import datetime, timezone                   # timestamps
from sqlalchemy import DateTime, String, UniqueConstraint, create_engine, func, select, update
from sqlalchemy.exc import IntegrityError                 # duplicate / constraint errors
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):                              # shared base
    pass


class Product(Base):                                      # products table
    __tablename__ = "products"                            # table name
    __table_args__ = (UniqueConstraint("sku", name="uq_products_sku"),)   # unique SKU
    id: Mapped[int] = mapped_column(primary_key=True)     # pk
    sku: Mapped[str] = mapped_column(String(20))          # business key
    name: Mapped[str] = mapped_column(String(100))        # title
    price_paise: Mapped[int]                              # store money as integer paise
    stock: Mapped[int] = mapped_column(default=0)         # python-side default
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))   # set on insert


class ProductRepo:
    """All DB access for products lives here, not in the endpoints."""

    def __init__(self, session: Session) -> None:
        self.s: Session = session                         # injected session

    def add(self, sku: str, name: str, price_paise: int, stock: int = 0) -> Product:
        p = Product(sku=sku, name=name, price_paise=price_paise, stock=stock)   # build object
        try:
            with self.s.begin_nested():                   # SAVEPOINT: only this insert is undone on failure
                self.s.add(p)                             # stage it
                self.s.flush()                            # send INSERT now to catch errors early
        except IntegrityError as e:                       # SKU already exists
            raise ValueError(f"duplicate sku {sku}") from e   # domain-friendly error
        return p                                          # has an id after flush

    def by_sku(self, sku: str) -> Product | None:
        return self.s.scalar(select(Product).where(Product.sku == sku))   # one or None

    def cheaper_than(self, paise: int, limit: int = 10) -> list[Product]:
        stmt = select(Product).where(Product.price_paise < paise).order_by(Product.price_paise).limit(limit)
        return list(self.s.scalars(stmt))                 # list of Product

    def restock_all(self, qty: int) -> int:
        res = self.s.execute(update(Product).values(stock=Product.stock + qty))   # one UPDATE for all rows
        return res.rowcount                               # rows changed

    def inventory_value(self) -> int:
        return self.s.scalar(select(func.coalesce(func.sum(Product.price_paise * Product.stock), 0))) or 0


engine = create_engine("sqlite:///:memory:")              # test database
Base.metadata.create_all(engine)                          # tables
SessionLocal = sessionmaker(engine, expire_on_commit=False)   # session factory

with SessionLocal.begin() as session:                     # commit on success, rollback on error
    repo = ProductRepo(session)                           # repository
    repo.add("A1", "Pen", 1000, 5)                        # Rs 10.00
    repo.add("B2", "Book", 25000, 2)                      # Rs 250.00
    repo.add("C3", "Bag", 90000)                          # Rs 900.00
    try:
        repo.add("A1", "Pen again", 1000)                 # duplicate SKU
    except ValueError as e:
        print("Error:", e)                                # Error: duplicate sku A1

with SessionLocal() as session:                           # new read session
    repo = ProductRepo(session)                           # repository
    print([p.name for p in repo.cheaper_than(50000)])     # names under Rs 500
    print(repo.by_sku("ZZ"))                              # None
    print(repo.inventory_value())                         # sum(price*stock)

# Output:
# Error: duplicate sku A1
# ['Pen', 'Book']
# None
# 55000
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | SQLAlchemy | Prisma / TypeORM (JS) |
|---------|-----------|------------------------|
| Model | class with `Mapped[]` | `schema.prisma` / decorators |
| Query | `select(User).where(...)` | `prisma.user.findMany({where})` |
| Unit of work | `Session` | Prisma client is stateless; TypeORM has `EntityManager` |
| Migrations | Alembic | `prisma migrate` |
| Raw SQL | `text("...")` | `$queryRaw` |

```python
# Python way
from sqlalchemy import select                              # query builder
rows = session.scalars(select(User).where(User.age > 18).order_by(User.name)).all()   # list[User]
```
```javascript
// JavaScript way (Prisma)
const rows = await prisma.user.findMany({     // query object
  where: { age: { gt: 18 } },                 // filter
  orderBy: { name: "asc" },                   // order
});
```

Key difference: SQLAlchemy has a real "unit of work": objects you load are tracked, and changing an attribute then calling `commit()` produces an UPDATE with no explicit save call. Prisma needs an explicit `update()`.

---

## 🟠 FastAPI Connection
FastAPI's official database pattern: one `engine`, a `sessionmaker`, and a `get_db` dependency that yields a session per request. Pydantic response models (`from_attributes=True`) turn ORM objects into JSON.

```python
# FastAPI + SQLAlchemy ORM (runs with TestClient)
from collections.abc import Iterator                      # generator type
from fastapi import Depends, FastAPI, HTTPException       # FastAPI
from fastapi.testclient import TestClient                 # test without a server
from pydantic import BaseModel, ConfigDict                # schemas
from sqlalchemy import create_engine, select              # engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool                    # share one in-memory DB across threads


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]


class ItemIn(BaseModel):                                  # request body
    title: str


class ItemOut(BaseModel):                                 # response body
    model_config = ConfigDict(from_attributes=True)       # read from ORM objects
    id: int
    title: str


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(engine)
app = FastAPI()


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:                            # one session per request
        yield db                                          # closed automatically after


@app.post("/items", response_model=ItemOut, status_code=201)
def create(body: ItemIn, db: Session = Depends(get_db)) -> Item:
    item = Item(title=body.title)                         # model from request
    db.add(item)
    db.commit()                                           # save
    db.refresh(item)                                      # load the generated id
    return item


@app.get("/items/{item_id}", response_model=ItemOut)
def read(item_id: int, db: Session = Depends(get_db)) -> Item:
    item = db.get(Item, item_id)                          # by primary key
    if item is None:
        raise HTTPException(404, "not found")
    return item


c = TestClient(app)
print(c.post("/items", json={"title": "tea"}).json())     # {'id': 1, 'title': 'tea'}
print(c.get("/items/1").json(), c.get("/items/9").status_code)   # ... 404
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the old 1.x style `session.query(User)` and `declarative_base()` in new code
✅ Correct: use `select()` and `DeclarativeBase` (2.0 style)

```python
# Wrong (legacy)
users = session.query(User).filter(User.age > 18).all()
# Right
users = session.scalars(select(User).where(User.age > 18)).all()
```

❌ Mistake 2: Using Python `and` / `or` in filters
✅ Correct: use `&`, `|` (with brackets) or `and_()`, `or_()`

```python
# Wrong — Python evaluates `and` first; only one condition survives
select(User).where(User.age > 18 and User.name == "Asha")
# Right
select(User).where((User.age > 18) & (User.name == "Asha"))
select(User).where(User.age > 18, User.name == "Asha")     # multiple args = AND
```

❌ Mistake 3: Comparing to None with `==` in your head (`is None` in Python is wrong here)
✅ Correct: `.is_(None)`

```python
# Wrong — `is None` is evaluated by Python immediately, gives False
select(User).where(User.age is None)
# Right
select(User).where(User.age.is_(None))
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

class Base(DeclarativeBase): pass
class U(Base):
    __tablename__ = "u"
    id: Mapped[int] = mapped_column(primary_key=True)
    n: Mapped[str]

e = create_engine("sqlite://")
Base.metadata.create_all(e)
with Session(e) as s:
    u = U(n="a")
    s.add(u)
    print(u.id)
    s.flush()
    print(u.id)
    s.rollback()
    print(s.get(U, 1))
```
Answer: `None`, then `1`, then `None`. Before `flush()` the object is only "pending" and has no id. `flush()` sends the INSERT inside the open transaction and fills the primary key. `rollback()` cancels that transaction, so the row is gone and `get` returns `None`. flush is not commit: it does not make data permanent.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Engine, Connection and Session?
A1: The Engine holds the connection pool and dialect (one per app). A Connection is one checked-out DB connection. A Session is the ORM "unit of work": it tracks objects and uses a connection while a transaction is active. Create one Session per request or task.

Q2: What does `flush()` do compared to `commit()`?
A2: `flush()` sends pending SQL to the database inside the current transaction (ids are assigned, constraints are checked) but the data can still be rolled back. `commit()` flushes and then permanently commits the transaction.

Q3: What is `expire_on_commit` and why do APIs often set it to False?
A3: By default after `commit()` all loaded attributes are expired and reloaded with a new query on next access. After the session is closed, that access raises `DetachedInstanceError`. Setting `expire_on_commit=False` keeps the data, which helps when returning objects from an endpoint or using async.

Q4: What is the N+1 query problem?
A4: Loading N parent rows and then lazily loading a relationship for each makes 1 + N queries. Fix with `selectinload()` or `joinedload()`. (See topic 359.)

Q5: Why store money as an integer?
A5: Floats cannot represent most decimals exactly (0.1 + 0.2 != 0.3). Store integer paise or use `Numeric`/`Decimal`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- CRUD-heavy apps with relationships
- You want database portability and type-checked models
- You need migrations (with Alembic) and testing with SQLite

❌ Avoid when:
- Huge bulk loads of millions of rows (use Core `insert()`, `COPY`, or raw SQL)
- Very complex analytical SQL (write it with `text()`)
- Tiny scripts where a raw driver is enough

---

## 📊 Visual Diagram
```
 Python object            Session (unit of work)             Database
 -------------            ----------------------             --------
 u = User(name="A")  -->  add(u)    [pending]
                          flush()   [INSERT sent]   ------>  row (uncommitted)
                          commit()  [persistent]    ------>  COMMIT
 u.age = 20          -->  (dirty)
                          commit()  [UPDATE sent]   ------>  UPDATE ... COMMIT

 Engine (pool) <----- Session borrows a connection while a transaction runs
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ORM | Maps classes to tables | Class को table से जोड़ना |
| Engine | Pool + dialect, one per app | Connection pool वाला object |
| Session | Tracks objects, runs transactions | Objects track करने वाला unit of work |
| Mapped[] | Typed column declaration | Typed column की घोषणा |
| flush | Send SQL, not final | SQL भेजना, final नहीं |
| commit | Make changes permanent | Changes को पक्का करना |

---

## ⚡ 3-Line Summary
English: SQLAlchemy ORM maps classes to tables using `DeclarativeBase` and `Mapped` columns. Use `select()` with a `Session`, and remember that `flush` sends SQL while `commit` makes it permanent. In FastAPI give each request its own session through a `yield` dependency.
Hindi: SQLAlchemy ORM `DeclarativeBase` और `Mapped` columns से classes को tables से जोड़ता है। `Session` के साथ `select()` इस्तेमाल करें, और याद रखें कि `flush` SQL भेजता है जबकि `commit` उसे पक्का करता है। FastAPI में हर request को `yield` dependency से अपना session दें।

---

## ➡️ Next Topic
**358. SQLAlchemy Sessions** — deeper look at the session lifecycle: states, identity map, autoflush and transactions.
