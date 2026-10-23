---

# 356. SQLAlchemy ORM — Complete Guide
# हिंदी में: SQLAlchemy ORM — पूरी Guide

---

## 🔵 Simple Definition (English)
SQLAlchemy is Python's most powerful database toolkit. It has two layers: **Core** (SQL expression language — build SQL programmatically) and **ORM** (map Python classes to database tables). The ORM lets you work with Python objects instead of raw SQL. SQLAlchemy 2.0 added full async support with `AsyncSession`.

## 🔵 सरल परिभाषा (Hindi)
SQLAlchemy Python का सबसे powerful database toolkit है। इसके दो layers हैं: **Core** (SQL programmatically build करो) और **ORM** (Python classes को database tables से map करो)। ORM से raw SQL की जगह Python objects से काम होता है। SQLAlchemy 2.0 में `AsyncSession` से async support आया।

---

## 🔴 Problem it Solves
Without ORM: write raw SQL strings (no type safety, SQL injection risk if not careful), manually map result rows to Python dicts/objects, manage DB connections manually, write boilerplate for every CRUD operation. SQLAlchemy abstracts this while giving you full control when needed.

## 🔴 यह क्यों बना? (Hindi)
ORM के बिना: raw SQL strings (type safety नहीं), result rows manually map करो, connections manually manage करो। SQLAlchemy सब abstract करता है पर full control भी देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define models: Python class inheriting DeclarativeBase + mapped_column()
Step 2 → Create engine: connection URL + connection pool config
Step 3 → Create tables: Base.metadata.create_all(engine) or Alembic migrations
Step 4 → Open a Session (unit of work — tracks all changes)
Step 5 → Add/query/update objects using the Session
Step 6 → session.commit() → Session generates SQL, executes, commits transaction
Step 7 → session.close() (or use 'with' / 'async with' for auto-close)
```

---

## 🟡 Real World Example
Flipkart product catalog: `Product` model with `Category` relationship. Fetch all electronics products with their category name — SQLAlchemy generates the JOIN automatically. Add a new product — SQLAlchemy generates the INSERT. Update price — SQLAlchemy detects the change (dirty tracking) and generates the UPDATE on commit.

---

## 💻 Code Example — Basic (SQLAlchemy 2.0 style)
```python
# SQLAlchemy 2.0 — modern declarative mapping
from sqlalchemy import create_engine, String, Integer, Float, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import Optional

# 1. Base class for all models:
class Base(DeclarativeBase):
    pass

# 2. Define models:
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    # Relationship — one Category has many Products:
    products: Mapped[list["Product"]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name!r})"

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Foreign key — links to categories.id:
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    # Relationship — many Products belong to one Category:
    category: Mapped["Category"] = relationship(back_populates="products")

# 3. Create engine:
engine = create_engine(
    "postgresql://user:password@localhost/mydb",
    echo=True,        # log all SQL statements (use only in dev!)
    pool_size=5,      # connection pool size
    max_overflow=10,  # extra connections beyond pool_size when needed
)

# 4. Create tables (or use Alembic for migrations):
Base.metadata.create_all(engine)

# 5. CRUD operations:
with Session(engine) as session:
    # CREATE:
    electronics = Category(name="Electronics")
    session.add(electronics)
    session.flush()        # sends INSERT to DB but doesn't commit (gets id)

    iphone = Product(name="iPhone 15", price=79999.0, stock=50, category=electronics)
    session.add(iphone)
    session.commit()       # commits transaction, iphone.id is now set

    # READ:
    stmt = select(Product).where(Product.price < 100000)
    products = session.execute(stmt).scalars().all()   # list of Product objects

    # With JOIN (SQLAlchemy generates it):
    stmt = (
        select(Product)
        .join(Product.category)
        .where(Category.name == "Electronics")
        .order_by(Product.price)
    )
    electronics_products = session.execute(stmt).scalars().all()

    # UPDATE — dirty tracking: just assign, commit handles the rest:
    iphone.price = 74999.0    # SQLAlchemy marks iphone as "dirty"
    session.commit()           # generates: UPDATE products SET price=74999 WHERE id=1

    # DELETE:
    old_product = session.get(Product, 1)  # get by primary key
    if old_product:
        session.delete(old_product)
        session.commit()
```

## 💻 Code Example — Advanced (Async + FastAPI)
```python
# SQLAlchemy async — required for FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, selectinload, joinedload
from sqlalchemy import select, update, delete, func
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Async engine — note: asyncpg driver!
async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/mydb",
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,    # test connection health before using from pool
)

# Session factory — creates new AsyncSession instances:
AsyncSessionFactory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,   # prevent lazy loading after commit (important for async!)
)

# FastAPI dependency — provides DB session per request:
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Repository pattern — encapsulates DB operations:
class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)

    async def get_all_with_category(self) -> list[Product]:
        """Eager load category to avoid N+1 query."""
        stmt = (
            select(Product)
            .options(selectinload(Product.category))  # JOIN in separate query (IN clause)
            # or: .options(joinedload(Product.category))  # JOIN in same query
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, name: str, price: float, category_id: int) -> Product:
        product = Product(name=name, price=price, category_id=category_id)
        self.session.add(product)
        await self.session.flush()   # get the generated id without committing
        await self.session.refresh(product)  # reload all columns from DB
        return product

    async def bulk_update_price(self, category_id: int, discount: float) -> int:
        """UPDATE with WHERE — more efficient than loading all objects."""
        stmt = (
            update(Product)
            .where(Product.category_id == category_id)
            .values(price=Product.price * (1 - discount))
        )
        result = await self.session.execute(stmt)
        return result.rowcount   # number of rows updated

    async def count_by_category(self) -> list[dict]:
        """Aggregation query."""
        stmt = (
            select(Category.name, func.count(Product.id).label("count"))
            .join(Product.category)
            .group_by(Category.name)
            .order_by(func.count(Product.id).desc())
        )
        rows = await self.session.execute(stmt)
        return [{"category": row.name, "count": row.count} for row in rows]

# FastAPI route using the repository:
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category_name: str

    model_config = {"from_attributes": True}

@app.get("/products", response_model=list[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db)):
    repo = ProductRepository(db)
    products = await repo.get_all_with_category()
    return [
        ProductResponse(
            id=p.id, name=p.name, price=p.price,
            category_name=p.category.name
        )
        for p in products
    ]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python + SQLAlchemy ORM:
from sqlalchemy import select
stmt = select(Product).where(Product.price < 1000).order_by(Product.name)
products = session.execute(stmt).scalars().all()
# Python objects — type-safe, IDE completion works
```

```javascript
// JavaScript with Prisma ORM (closest equivalent):
const products = await prisma.product.findMany({
    where: { price: { lt: 1000 } },
    orderBy: { name: "asc" },
    include: { category: true },    // like SQLAlchemy's selectinload
});
// TypeScript types auto-generated from schema — similar type safety
```

---

## 🟠 FastAPI Connection

```python
# Pattern: engine and session factory at module level, dependency per request

# database.py — setup
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(settings.db_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session          # FastAPI injects this into route functions

# Route using dependency:
@app.post("/products")
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()
    return ProductResponse.model_validate(product)
# db.commit() is called by get_db's __aexit__ if no exception

# Testing — override get_db with test DB:
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

@pytest.fixture
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(test_engine) as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db():
    # injected in tests via dependency_overrides
    ...
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `expire_on_commit=True` (default) causes lazy loading errors in async
```python
# Wrong — after commit, accessing attributes triggers a new query (sync in async!)
product = await session.get(Product, 1)
await session.commit()
print(product.name)    # LazyLoadingError — expired, needs a new query!

# Correct — set expire_on_commit=False on session factory:
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)
# OR: await session.refresh(product) before accessing attributes post-commit
```

❌ Mistake 2: N+1 query — accessing relationship in a loop
```python
# Wrong — N+1 queries:
products = (await session.execute(select(Product))).scalars().all()
for product in products:
    print(product.category.name)   # each access fires a separate SELECT!

# Correct — eager load with selectinload or joinedload:
stmt = select(Product).options(selectinload(Product.category))
products = (await session.execute(stmt)).scalars().all()
for product in products:
    print(product.category.name)   # data already loaded — no extra queries
```

---

## 🧠 Tricky Interview Question

```python
# What is the difference between selectinload and joinedload?
from sqlalchemy.orm import selectinload, joinedload

# joinedload:
stmt = select(Product).options(joinedload(Product.category))
# Generates: SELECT products.*, categories.* FROM products LEFT JOIN categories ...
# One query — categories loaded in same result set

# selectinload:
stmt = select(Product).options(selectinload(Product.category))
# Generates TWO queries:
# 1. SELECT * FROM products
# 2. SELECT * FROM categories WHERE id IN (1, 2, 3, ...)
# Separate query using IN clause
```
Answer: `joinedload` uses a SQL JOIN — one query, but may cause row duplication for one-to-many (100 products each with 3 tags = 300 rows). `selectinload` uses two queries with an `IN` clause — better for one-to-many collections (avoids cartesian explosion). Use `joinedload` for many-to-one (product → category), `selectinload` for one-to-many (category → products).

---

## ⚫ Interview Questions + Answers

Q1: What is the Unit of Work pattern in SQLAlchemy?
A1: The `Session` implements the Unit of Work pattern — it tracks all objects you've loaded or added, records all changes (dirty tracking), and on `commit()` generates the minimum SQL needed to sync the Python objects with the DB. You don't call UPDATE manually — you just modify Python attributes, and the Session figures out what changed.

Q2: What is the difference between `session.flush()` and `session.commit()`?
A2: `flush()` sends pending SQL to the DB within the current transaction (INSERT/UPDATE/DELETE) — useful for getting generated IDs before committing. But changes are not durable yet — a rollback still undoes them. `commit()` makes changes permanent, ends the transaction. In FastAPI patterns with `yield`, `commit()` is called at the end of the request if no exception.

Q3: What is lazy loading vs eager loading?
A3: Lazy loading: relationship attributes are loaded from DB on first access (generates a query per attribute access). This causes N+1 problem in loops. Eager loading: SQLAlchemy loads related objects upfront in the same or a second query. Use `selectinload(Model.relation)` or `joinedload(Model.relation)` in your `select()` statement. In async, lazy loading causes errors because you can't run sync queries.

Q4: What is Alembic?
A4: Alembic is SQLAlchemy's migration tool. It compares your Python model definitions to the current DB schema and generates migration scripts (`alembic revision --autogenerate -m "add price column"`). Migrations are versioned Python files. `alembic upgrade head` applies all pending migrations. Essential for production — never use `create_all()` in production.

Q5: What is `expire_on_commit=False` and why is it important for async?
A5: By default, SQLAlchemy expires all object attributes after `commit()` — next access to any attribute fires a lazy-load query to refresh. In async, lazy loading isn't supported (it would need to run a sync query). `expire_on_commit=False` keeps attributes set even after commit. In async FastAPI code, always set this on `async_sessionmaker`, or call `await session.refresh(obj)` after commit if you need fresh DB data.

---

## 🔷 When to Use + When Not to Use

✅ Use SQLAlchemy ORM when:
- Web apps with complex data models and relationships
- FastAPI with PostgreSQL (standard pattern)
- Need migrations (Alembic)
- Team needs readable Python instead of SQL
- Multiple DB support (SQLite for tests, PostgreSQL for prod)

✅ Use SQLAlchemy Core (not ORM) when:
- Need maximum SQL control and performance
- Bulk operations (`INSERT ... SELECT`, mass UPDATE)
- Complex analytical queries

❌ Use raw asyncpg/psycopg3 when:
- Maximum performance, minimal overhead
- Complex PostgreSQL-specific features (COPY, LISTEN/NOTIFY, custom types)
- The ORM abstraction is getting in the way

---

## 📊 Visual Diagram
```
Python Code                SQLAlchemy Session              Database
───────────                ──────────────────              ────────
product = Product(...)
session.add(product)  →    [identity map: tracks product]
                           [marked: new]

product.price = 999   →    [dirty tracking: price changed]

await session.flush() →    INSERT INTO products ...  →    [row inserted, id=5 returned]
                      ←    id=5                      ←

await session.commit()→    COMMIT                   →    [durable]

                           [all objects expired]

product.name          →    (expire_on_commit=False → uses cached value)
                           (expire_on_commit=True → SELECT * WHERE id=5)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ORM | Object-Relational Mapper | Python objects ↔ DB tables |
| Session | Unit of work — tracks and syncs changes | Changes track करने वाला unit |
| mapped_column | Type-safe column declaration | Type-safe column declare करना |
| relationship() | Declares a JOIN relationship | JOIN relationship declare करना |
| selectinload | Eager load via IN clause | IN clause से eager load |
| joinedload | Eager load via JOIN | JOIN से eager load |
| expire_on_commit | Whether to reload after commit | Commit के बाद reload करो? |
| Alembic | SQLAlchemy migration tool | Schema migration tool |

---

## ⚡ 3-Line Summary
English: SQLAlchemy ORM maps Python classes to DB tables — the `Session` tracks dirty objects and generates SQL on `commit()`. For FastAPI async, use `create_async_engine` + `async_sessionmaker` with `expire_on_commit=False`, and inject `AsyncSession` via `Depends(get_db)`. Always eager-load relationships with `selectinload` or `joinedload` — async doesn't support lazy loading.
Hindi: SQLAlchemy ORM Python classes को DB tables से map करता है। FastAPI async के लिए `create_async_engine` + `expire_on_commit=False`। Relationships के लिए `selectinload` — async में lazy loading काम नहीं करती।

---

## ➡️ Next Topic
**357. Alembic Migrations** — `alembic init`, `autogenerate`, migration scripts, rollback. Then **358. SQLAlchemy Core** — text(), select(), insert() without ORM.
