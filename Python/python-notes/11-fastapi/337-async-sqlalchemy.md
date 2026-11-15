---

# 337. Async SQLAlchemy
# हिंदी में: Async SQLAlchemy (AsyncSession, create_async_engine)

---

## 🔵 Simple Definition (English)
Async SQLAlchemy lets you talk to the database with `await`, so the event loop stays free while the database works. You use `create_async_engine`, `AsyncSession`, and an async driver (`asyncpg`, `aiosqlite`, `aiomysql`). The ORM models and `select()` queries stay the same.

## 🔵 सरल परिभाषा (Hindi)
Async SQLAlchemy में आप `await` से database से बात करते हैं, इसलिए database के काम करते समय event loop खाली रहता है। इसमें `create_async_engine`, `AsyncSession` और async driver (`asyncpg`, `aiosqlite`, `aiomysql`) उपयोग होते हैं। ORM models और `select()` queries वही रहते हैं।

---

## 🔴 Problem it Solves
In an `async def` FastAPI route, a sync database call blocks the event loop (see topic 331). Running sync routes in threads works, but threads are heavy and limited (40 by default). Async SQLAlchemy lets thousands of requests wait for the database at the same time on one loop, using far less memory, and it fits naturally with other async I/O such as httpx and Redis.

## 🔴 यह क्यों बना? (Hindi)
`async def` FastAPI route में sync database call event loop को block करता है (topic 331 देखें)। Sync routes को threads में चलाना काम करता है, लेकिन threads भारी और सीमित (default 40) हैं। Async SQLAlchemy से हजारों requests एक ही loop पर एक साथ database का इंतजार कर सकती हैं, बहुत कम memory में, और यह httpx और Redis जैसे दूसरे async I/O के साथ स्वाभाविक रूप से जुड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install "sqlalchemy[asyncio]" asyncpg   (greenlet is required)
Step 2 → engine = create_async_engine("postgresql+asyncpg://...")
Step 3 → SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Step 4 → Dependency: async with SessionLocal() as session: yield session
Step 5 → Query: result = await session.execute(select(User)) / await session.scalars(...)
Step 6 → Write: session.add(obj); await session.commit()
Step 7 → Relationships must be eager loaded (selectinload) or use awaitable_attrs
Step 8 → Shutdown: await engine.dispose()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install "sqlalchemy[asyncio]" asyncpg   (greenlet जरूरी है)
Step 2 → engine = create_async_engine("postgresql+asyncpg://...")
Step 3 → SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Step 4 → Dependency: async with SessionLocal() as session: yield session
Step 5 → Query: result = await session.execute(select(User)) / await session.scalars(...)
Step 6 → Write: session.add(obj); await session.commit()
Step 7 → Relationships eager load (selectinload) करनी होंगी या awaitable_attrs उपयोग करें
Step 8 → Shutdown: await engine.dispose()
```

---

## 🟡 Real World Example
A chat or notification service with many concurrent users: each request fetches a team and its members, then calls an external push API with httpx. With async SQLAlchemy + async httpx, a single uvicorn worker handles thousands of in-flight requests because every wait (DB, HTTP) frees the loop. This is typical in Indian fintech and ride-hailing backends that fan out to several services per request.

## 🟡 Real Example Hindi mein
Chat या notification service जहाँ कई users एक साथ हैं: हर request एक team और उसके members लाती है, फिर httpx से external push API call करती है। Async SQLAlchemy + async httpx के साथ एक uvicorn worker हजारों in-flight requests संभालता है क्योंकि हर इंतजार (DB, HTTP) loop को खाली कर देता है। यह भारतीय fintech और ride-hailing backends में आम है जो हर request पर कई services को call करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: AsyncSession, lazy-loading error, awaitable_attrs, streaming (verified)
import asyncio                                                # run the coroutine
from sqlalchemy import ForeignKey, select                     # core imports
from sqlalchemy.exc import StatementError                     # MissingGreenlet is wrapped in this
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):                      # AsyncAttrs adds awaitable_attrs
    pass                                                      # empty


class Team(Base):                                             # parent table
    __tablename__ = "teams"                                   # table name
    id: Mapped[int] = mapped_column(primary_key=True)         # PK
    members: Mapped[list["Member"]] = relationship(back_populates="team")   # one-to-many


class Member(Base):                                           # child table
    __tablename__ = "members"                                 # table name
    id: Mapped[int] = mapped_column(primary_key=True)         # PK
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))   # FK
    team: Mapped[Team] = relationship(back_populates="members")    # back reference


async def main() -> None:                                     # everything async lives here
    engine = create_async_engine("sqlite+aiosqlite://")       # async engine (aiosqlite driver)
    async with engine.begin() as conn:                        # async connection + transaction
        await conn.run_sync(Base.metadata.create_all)         # DDL is sync: run via run_sync
    Session = async_sessionmaker(engine, expire_on_commit=False)   # session factory
    async with Session() as s:                                # async context manager
        s.add(Team(members=[Member(), Member()]))             # add team with 2 members
        await s.commit()                                      # commit must be awaited
    async with Session() as s:                                # fresh session
        team = (await s.execute(select(Team))).scalar_one()   # load the team
        try:                                                  # touching a lazy relationship
            print(len(team.members))                          # tries implicit IO => error
        except StatementError as e:                           # wrapper around the real error
            print(type(e.orig).__name__)                      # MissingGreenlet
        members = await team.awaitable_attrs.members          # explicit awaited lazy load
        print(len(members))                                   # 2
        rows = await s.stream_scalars(select(Member))         # server-side streaming result
        print([m.id async for m in rows])                     # async iteration
    await engine.dispose()                                    # close pool


asyncio.run(main())                                           # run it

# Output (verified; also prints a harmless "coroutine ... never awaited" RuntimeWarning on the failed lazy load):
# MissingGreenlet
# 2
# [1, 2]
```

## 💻 Code Example — Advanced
```python
# Production style: async engine, async_sessionmaker, session dependency, eager loading, 404 handling
import asyncio                                                # run the demo
from collections.abc import AsyncGenerator                    # type of async generator dependency
from typing import Annotated                                  # dependency alias
from fastapi import Depends, FastAPI, HTTPException           # FastAPI core
from httpx import ASGITransport, AsyncClient                  # async test client
from sqlalchemy import ForeignKey, String, select             # core imports
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy.pool import StaticPool                        # keep a single in-memory connection

# production: create_async_engine("postgresql+asyncpg://user:pw@host/db", pool_size=10, pool_pre_ping=True)
engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool,
                             connect_args={"check_same_thread": False})   # demo engine
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)   # MUST disable expire in async


class Base(DeclarativeBase):                                  # base class
    pass                                                      # empty


class Team(Base):                                             # teams table
    __tablename__ = "teams"                                   # name
    id: Mapped[int] = mapped_column(primary_key=True)         # PK
    name: Mapped[str] = mapped_column(String(40))             # team name
    members: Mapped[list["Member"]] = relationship(back_populates="team")   # members list


class Member(Base):                                           # members table
    __tablename__ = "members"                                 # name
    id: Mapped[int] = mapped_column(primary_key=True)         # PK
    name: Mapped[str] = mapped_column(String(40))             # member name
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))   # FK
    team: Mapped[Team] = relationship(back_populates="members")    # back reference


async def get_session() -> AsyncGenerator[AsyncSession, None]:   # per-request async session
    async with SessionLocal() as session:                     # open and auto close
        yield session                                         # give it to the route


Sess = Annotated[AsyncSession, Depends(get_session)]          # short alias
app: FastAPI = FastAPI()                                      # create app


@app.post("/teams/{name}")                                    # create a team with 2 members
async def create_team(name: str, session: Sess) -> dict[str, int]:
    team = Team(name=name, members=[Member(name="m1"), Member(name="m2")])   # build objects
    session.add(team)                                         # stage
    await session.commit()                                    # awaited commit
    return {"id": team.id}                                    # id available (no expire)


@app.get("/teams/{team_id}")                                  # read with members
async def read_team(team_id: int, session: Sess) -> dict[str, object]:
    stmt = select(Team).where(Team.id == team_id).options(selectinload(Team.members))   # EAGER load
    team: Team | None = await session.scalar(stmt)            # await the query
    if team is None:                                          # not found
        raise HTTPException(404, "not found")                 # 404
    return {"name": team.name, "members": [m.name for m in team.members]}   # safe: already loaded


@app.get("/lazy/{team_id}")                                   # the classic async bug
async def lazy(team_id: int, session: Sess) -> dict[str, str]:
    team = await session.get(Team, team_id)                   # no eager load
    return {"members": str(len(team.members))}                # lazy load => MissingGreenlet => 500


async def main() -> None:                                     # demo driver
    async with engine.begin() as conn:                        # create tables
        await conn.run_sync(Base.metadata.create_all)         # sync DDL via run_sync
    transport = ASGITransport(app=app, raise_app_exceptions=False)   # return 500 instead of raising
    async with AsyncClient(transport=transport, base_url="http://t") as c:   # async client
        print((await c.post("/teams/dev")).json())            # create
        print((await c.get("/teams/1")).json())               # read with members
        print((await c.get("/teams/9")).status_code)          # missing
        print((await c.get("/lazy/1")).status_code)           # lazy bug
    await engine.dispose()                                    # cleanup


asyncio.run(main())                                           # run

# Output (verified):
# {'id': 1}
# {'name': 'dev', 'members': ['m1', 'm2']}
# 404
# 500
```
Requires `pip install "sqlalchemy[asyncio]" aiosqlite` (without `greenlet` you get `ImportError: The SQLAlchemy asyncio module requires that the Python 'greenlet' library is installed`).

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (async SQLAlchemy) | JavaScript (Node) |
|---------|---------------------------|-------------------|
| Default style | sync is default; async is opt-in | all DB drivers are async/promise based |
| Query call | `await session.execute(...)` | `await prisma.user.findMany()` |
| Lazy relationship access | NOT allowed (error) | not applicable (explicit `include`) |
| Driver | asyncpg / aiosqlite | pg, mysql2 |

```python
# Python way
team = (await session.execute(select(Team).options(selectinload(Team.members)))).scalar_one()   # eager
print([m.id for m in team.members])      # safe
```
```javascript
// JavaScript way (Prisma) — relations are always explicit
const team = await prisma.team.findFirst({ include: { members: true } });   // explicit include
console.log(team.members.map((m) => m.id));                                 // safe
```

Key difference: in JS you must always ask for relations explicitly, so there is no hidden query. In Python's ORM an attribute access can secretly run SQL; in async code that is forbidden and raises `MissingGreenlet`.

---

## 🟠 FastAPI Connection
Async SQLAlchemy is the recommended stack for `async def` routes. Pair it with `asyncpg` for PostgreSQL. Create the engine once (module level or in `lifespan`), a session per request via a `yield` dependency, and always use eager loading in queries that touch relationships. For tests, override `get_session` with a session bound to a test database.

```python
# FastAPI example — engine lifecycle in lifespan
from contextlib import asynccontextmanager                   # lifespan helper
from fastapi import FastAPI                                  # app

@asynccontextmanager                                         # startup/shutdown in one function
async def lifespan(app: FastAPI):
    yield                                                    # app runs here
    await engine.dispose()                                   # close all DB connections on shutdown

app = FastAPI(lifespan=lifespan)                             # attach lifespan
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Lazy loading relationships in async code
✅ Correct: `selectinload` / `joinedload` in the query, or `await obj.awaitable_attrs.rel`

```python
# Wrong — MissingGreenlet error
team = await session.get(Team, 1)
print(team.members)
# Right
team = await session.scalar(select(Team).options(selectinload(Team.members)).where(Team.id == 1))
print(team.members)
```

❌ Mistake 2: Keeping default `expire_on_commit=True`
✅ Correct: `async_sessionmaker(engine, expire_on_commit=False)`; otherwise attributes expire after commit and reading them triggers an implicit (forbidden) refresh

```python
# Wrong
SessionLocal = async_sessionmaker(engine)          # after commit, team.id access can raise MissingGreenlet
# Right
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

❌ Mistake 3: Using a sync driver URL (`postgresql://`, `psycopg2`) with `create_async_engine`
✅ Correct: async driver in the URL: `postgresql+asyncpg://`, `sqlite+aiosqlite://`, `mysql+aiomysql://`

```python
# Wrong
create_async_engine("postgresql://u:p@h/db")       # raises (needs an async driver)
# Right
create_async_engine("postgresql+asyncpg://u:p@h/db")
```

---

## 🧠 Tricky Interview Question

```python
# Why does this code raise in async SQLAlchemy?
async def handler(session: AsyncSession) -> int:
    team = await session.get(Team, 1)
    return len(team.members)
```
Answer: `team.members` is a lazy-loaded relationship. Accessing it makes SQLAlchemy run SQL implicitly, which needs `await`, but a normal attribute access cannot be awaited. SQLAlchemy raises `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_() here`. Fix: load it in the query with `selectinload(Team.members)`, use `await team.awaitable_attrs.members`, or set `lazy="selectin"` on the relationship.

---

## ⚫ Interview Questions + Answers

Q1: Why is `greenlet` needed?
A1: SQLAlchemy reuses its sync code internally by running it inside a greenlet that can "suspend" when the async driver awaits. This is how `await session.execute()` works without rewriting the whole library.

Q2: Why `expire_on_commit=False`?
A2: By default, commit marks all attributes expired so the next access reloads from the database. In async, that reload is an implicit lazy IO call and fails. Disabling expiry keeps loaded values readable after commit.

Q3: Can one AsyncSession be shared by concurrent tasks (`asyncio.gather`)?
A3: No. A session represents one transaction on one connection; concurrent use causes errors. Give each task its own session, or run queries sequentially.

Q4: How do you run sync-only things like `create_all` on an async engine?
A4: `async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)`. `run_sync` executes a sync function with a sync-style connection.

Q5: When is async SQLAlchemy NOT worth it?
A5: Low-traffic internal tools, CPU-heavy code, or teams that rely on sync-only libraries. Sync `def` routes with a thread pool are simpler, and with a 40-thread pool they handle quite a lot.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- High concurrency and mostly waiting on I/O (APIs, DB, cache)
- The rest of your stack is async (httpx, redis.asyncio, websockets)
- You use PostgreSQL with `asyncpg`

❌ Avoid when:
- Simple CRUD app with moderate traffic: sync is easier to debug
- You need many lazy-loaded relationships everywhere (you must be explicit)
- Heavy CPU work (async does not help)

---

## 📊 Visual Diagram
```
 async def route ──► await session.execute(select(...))
                              │  (loop is FREE here, serves other requests)
                              ▼
                      AsyncSession ──► async engine ──► asyncpg ──► PostgreSQL
                              │
         team.members (lazy) ─┴─► ✗ MissingGreenlet
         selectinload / awaitable_attrs ─► ✓
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `AsyncSession` | Session with awaitable methods | Awaitable methods वाला Session |
| `create_async_engine` | Async engine factory | Async engine बनाने वाला |
| `greenlet` | Library letting sync code pause | Sync code को रोकने वाली library |
| `awaitable_attrs` | Await a lazy attribute | Lazy attribute को await करना |
| `run_sync` | Run sync function inside async connection | Async में sync function चलाना |
| `asyncpg` | Fast async PostgreSQL driver | तेज़ async PostgreSQL driver |

---

## ⚡ 3-Line Summary
English: Async SQLAlchemy uses `create_async_engine`, `async_sessionmaker` and `await` for every database call, so the event loop is never blocked. Disable `expire_on_commit` and eager load relationships, because implicit lazy loading raises `MissingGreenlet`. Install `greenlet` and an async driver such as `asyncpg`.
Hindi: Async SQLAlchemy में `create_async_engine`, `async_sessionmaker` और हर database call पर `await` उपयोग होता है, इसलिए event loop कभी block नहीं होता। `expire_on_commit` बंद करें और relationships eager load करें, क्योंकि implicit lazy loading `MissingGreenlet` देती है। `greenlet` और `asyncpg` जैसा async driver install करें।

---

## ➡️ Next Topic
**338. Tortoise ORM** — an async-first, Django-style ORM that avoids lazy-loading surprises by design.
