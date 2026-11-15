---

# Q237. Async DB session (SQLAlchemy)
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐⭐

---

## ❓ Question
Wire SQLAlchemy 2.x async (`AsyncSession`) into FastAPI: one engine, a session-per-request dependency, create tables at startup, and create/read/list endpoints returning Pydantic models. Use in-memory SQLite (aiosqlite) so it runs anywhere.

---

## 💡 Quick Concept (2 lines only)
Create ONE async engine and a `async_sessionmaker`; give each request its own `AsyncSession` through a `yield` dependency so it is always closed. Every DB call must be `await`ed.
हिंदी: Engine एक, session हर request का अपना (`yield` dependency) — और हर DB call पर `await` ज़रूरी है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections.abc import AsyncIterator  # dependency type
from contextlib import asynccontextmanager  # lifespan helper
from fastapi import FastAPI, Depends, HTTPException  # web
from fastapi.testclient import TestClient  # client
from pydantic import BaseModel, ConfigDict  # schemas
from sqlalchemy import select  # query builder
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # async ORM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # ORM models
from sqlalchemy.pool import StaticPool  # keep ONE in-memory sqlite connection for the demo

engine = create_async_engine(  # Step 1: one engine per process
    "sqlite+aiosqlite:///:memory:", poolclass=StaticPool,  # in-memory db (use postgresql+asyncpg in prod)
    connect_args={"check_same_thread": False},  # allow cross-thread use
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)  # Step 2: session factory (no expiry after commit)

class Base(DeclarativeBase):  # ORM base
    pass  # nothing needed

class User(Base):  # table
    __tablename__ = "users"  # table name
    id: Mapped[int] = mapped_column(primary_key=True)  # pk
    name: Mapped[str]  # name column

class UserOut(BaseModel):  # response schema
    model_config = ConfigDict(from_attributes=True)  # read from ORM objects
    id: int  # id
    name: str  # name

async def get_session() -> AsyncIterator[AsyncSession]:  # Step 3: one session PER REQUEST
    async with SessionLocal() as session:  # open session
        yield session  # give to route
    # leaving the block closes the session (returns connection to pool)

@asynccontextmanager  # startup/shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # lifespan
    async with engine.begin() as conn:  # startup: create tables
        await conn.run_sync(Base.metadata.create_all)  # DDL is sync -> run_sync
    yield  # app runs
    await engine.dispose()  # shutdown: close pool

app = FastAPI(lifespan=lifespan)  # app

@app.post("/users", response_model=UserOut, status_code=201)  # create
async def create(name: str, db: AsyncSession = Depends(get_session)) -> User:  # session injected
    user = User(name=name)  # new row
    db.add(user)  # stage
    await db.commit()  # write (await!)
    return user  # id filled in after commit

@app.get("/users/{uid}", response_model=UserOut)  # read
async def read(uid: int, db: AsyncSession = Depends(get_session)) -> User:  # session injected
    user = await db.get(User, uid)  # primary-key lookup
    if user is None:  # missing
        raise HTTPException(404, "not found")  # 404
    return user  # ORM -> schema

@app.get("/users", response_model=list[UserOut])  # list
async def list_users(db: AsyncSession = Depends(get_session)) -> list[User]:  # session injected
    result = await db.execute(select(User).order_by(User.id))  # SELECT
    return list(result.scalars().all())  # rows -> objects

# ============================================
# TEST CASES
# ============================================
with TestClient(app) as client:  # context manager runs lifespan
    print(client.post("/users", params={"name": "ann"}).json())  # Expected: {'id': 1, 'name': 'ann'}
    client.post("/users", params={"name": "bob"})  # second row
    print(client.get("/users").json())  # Expected: [{'id': 1, 'name': 'ann'}, {'id': 2, 'name': 'bob'}]
    print(client.get("/users/1").json())  # Expected: {'id': 1, 'name': 'ann'}
    print(client.get("/users/9").status_code)  # Expected: 404
```

---

## 🔍 Why This Works (3 lines max)
`get_session` opens a session, yields it to the route and closes it afterwards, even on errors. `expire_on_commit=False` keeps attributes readable after `commit()` (async can't lazily reload). Table creation uses `run_sync` because DDL is sync API. Install `sqlalchemy[asyncio]`, `aiosqlite`.
हिंदी: `expire_on_commit=False` ज़रूरी है, वरना commit के बाद attributes पढ़ने पर async में error आता है।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: session.begin() = auto commit / rollback ----
async def add_user(name: str) -> None:  # standalone helper
    async with SessionLocal() as s, s.begin():  # commit on success, rollback on error
        s.add(User(name=name))  # stage insert

import asyncio  # to run the helper
async def demo() -> None:  # demo
    async with engine.begin() as c:  # recreate tables (engine was disposed)
        await c.run_sync(Base.metadata.create_all)  # DDL
    await add_user("zed")  # insert
    try:  # failing transaction
        async with SessionLocal() as s, s.begin():  # transaction
            s.add(User(name="temp"))  # stage
            raise ValueError("fail")  # forces rollback
    except ValueError:  # expected
        pass  # ignore
    async with SessionLocal() as s:  # read back
        print([u.name for u in (await s.scalars(select(User))).all()])  # Expected: ['zed'] (temp rolled back)
asyncio.run(demo())  # run
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: one global session shared by all requests -> concurrent requests corrupt each other's transactions
session = SessionLocal()

# ❌ Wrong: forgetting await -> you get a coroutine object, nothing is committed
db.commit()

# ❌ Wrong: lazy-loading a relationship after the session closed (MissingGreenlet error)
# ✅ Correct: session per request via Depends, await every call, eager-load with selectinload()
```

---

## 🎯 Interview Tip (1 line)
Say: "One engine per process, one session per request via a yield dependency, always await, and eager-load relationships because async has no implicit lazy loading."

---

## 🔗 Related Questions
→ Q221 (CRUD) | Q222 (dependencies) | Q240 (lifespan) | Q236 (testing)
