---

# 014. FastAPI + PostgreSQL (asyncpg)
# हिंदी में: FastAPI + PostgreSQL (asyncpg)

---

## 🔵 Simple Definition (English)
`asyncpg` is a fast async PostgreSQL driver for Python. With FastAPI you create one connection pool at startup, borrow a connection per request, run SQL with `await`, and give it back. AI apps use Postgres to store requests, results, token usage, users, and (with the pgvector extension) embeddings.

## 🔵 सरल परिभाषा (Hindi)
`asyncpg` Python के लिए तेज़ async PostgreSQL driver है। FastAPI के साथ startup पर एक connection pool बनाते हैं, हर request में एक connection उधार लेते हैं, `await` से SQL चलाते हैं और वापस दे देते हैं। AI apps Postgres में requests, results, token usage, users और (pgvector extension से) embeddings रखते हैं।

---

## 🔴 Problem it Solves
Sync DB drivers block the event loop while waiting for the database, so an async API loses its concurrency advantage. Opening a new connection per request is also slow (TCP + auth, 20-50 ms) and exhausts Postgres (each connection costs memory). An async driver plus a pool keeps the loop free and connections reused.

## 🔴 यह क्यों बना? (Hindi)
Sync DB drivers database का इंतज़ार करते समय event loop को block करते हैं, इसलिए async API अपना फ़ायदा खो देती है। हर request पर नया connection खोलना भी धीमा है (TCP + auth, 20-50 ms) और Postgres को थका देता है (हर connection memory लेता है)। Async driver और pool से loop खाली रहता है और connections दोबारा use होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → At startup (lifespan): pool = await asyncpg.create_pool(dsn, min_size=2, max_size=10)
Step 2 → Store the pool on app.state
Step 3 → In a route: `async with pool.acquire() as conn:` borrows a free connection (waits if none)
Step 4 → Run SQL: await conn.fetchrow("SELECT ... WHERE id = $1", id)   (parameters are $1, $2...)
Step 5 → Leaving the `async with` returns the connection to the pool (it is not closed)
Step 6 → For multi-step changes use `async with conn.transaction():` (commit on success, rollback on error)
Step 7 → At shutdown: await pool.close()
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Startup (lifespan) में: pool = await asyncpg.create_pool(dsn, min_size=2, max_size=10)
Step 2 → Pool को app.state पर रखो
Step 3 → Route में: `async with pool.acquire() as conn:` खाली connection उधार लेता है (न हो तो इंतज़ार)
Step 4 → SQL चलाओ: await conn.fetchrow("SELECT ... WHERE id = $1", id)   (parameters $1, $2...)
Step 5 → `async with` से निकलते ही connection pool में वापस जाता है (बंद नहीं होता)
Step 6 → कई steps के बदलाव के लिए `async with conn.transaction():` (सफल पर commit, error पर rollback)
Step 7 → Shutdown पर: await pool.close()
```

---

## 🟡 Real World Example
**Tariff Classification System**: Tables: `classifications(id, user_id, description, hs_code, confidence, prompt_tokens, completion_tokens, created_at)` and `hs_codes(code, name, duty)`. Each `/classify` request inserts a row (audit trail required by customs) and each lookup reads `hs_codes`. A daily report sums tokens per user. With pgvector, `hs_codes.embedding` enables similarity search for candidates.

**Amazon AI**: Stores generated product descriptions with the prompt version, so a bad prompt release can be traced and rolled back.

## 🟡 Real Example Hindi mein
**Tariff System**: Tables: `classifications(id, user_id, description, hs_code, confidence, prompt_tokens, completion_tokens, created_at)` और `hs_codes(code, name, duty)`। हर `/classify` request एक row insert करती है (customs को audit trail चाहिए) और हर lookup `hs_codes` पढ़ता है। Daily report प्रति user tokens जोड़ती है। pgvector से `hs_codes.embedding` पर similarity search होती है।

**Amazon AI**: Generated product descriptions prompt version के साथ store होते हैं ताकि खराब prompt release को trace और rollback किया जा सके।

---

## 💻 Code Example — Basic
```python
# Basic asyncpg usage (pip install asyncpg). Needs a running Postgres; set DATABASE_URL.
# Example: postgresql://postgres:postgres@localhost:5432/tariff
import asyncio  # run the async main
import os  # read environment variable

import asyncpg  # async Postgres driver


async def main() -> None:  # demo coroutine
    dsn = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")  # connection string
    conn = await asyncpg.connect(dsn)  # open ONE connection (fine for scripts, not for web apps)
    try:  # make sure we close it
        await conn.execute(  # run DDL
            "CREATE TABLE IF NOT EXISTS hs_codes (code TEXT PRIMARY KEY, name TEXT NOT NULL)"  # create table
        )  # no result
        await conn.execute(  # insert with parameters ($1, $2) - never use f-strings in SQL
            "INSERT INTO hs_codes (code, name) VALUES ($1, $2) ON CONFLICT (code) DO NOTHING",  # upsert-ish
            "8517", "Telephones",  # values
        )  # inserted
        row = await conn.fetchrow("SELECT code, name FROM hs_codes WHERE code = $1", "8517")  # one row or None
        print(dict(row) if row else "not found")  # {'code': '8517', 'name': 'Telephones'}
        rows = await conn.fetch("SELECT code, name FROM hs_codes ORDER BY code LIMIT 5")  # list of Records
        print([r["code"] for r in rows])  # access by column name
        count = await conn.fetchval("SELECT count(*) FROM hs_codes")  # single value
        print("rows:", count)  # number
    finally:  # always runs
        await conn.close()  # close connection


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run (requires Postgres to be running)
```

## 💻 Code Example — Advanced
```python
# Production: pool in lifespan, dependency, transaction, parameterised SQL, error mapping,
# usage summary query, health check. Needs Postgres (DATABASE_URL).
import os  # env
from contextlib import asynccontextmanager  # lifespan
from typing import Annotated, AsyncIterator  # typing

import asyncpg  # driver
from fastapi import Depends, FastAPI, HTTPException, Request  # FastAPI
from pydantic import BaseModel, Field  # models

DSN = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")  # config

SCHEMA = """
CREATE TABLE IF NOT EXISTS classifications (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    description TEXT NOT NULL,
    hs_code TEXT NOT NULL,
    confidence REAL NOT NULL,
    prompt_tokens INT NOT NULL,
    completion_tokens INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_class_user_time ON classifications (user_id, created_at DESC);
"""  # DDL with an index for per-user queries


@asynccontextmanager  # lifespan
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # startup/shutdown
    app.state.pool = await asyncpg.create_pool(  # create the pool ONCE
        DSN, min_size=2, max_size=10, command_timeout=10,  # sizes and per-query timeout
    )  # pool ready
    async with app.state.pool.acquire() as conn:  # run schema migration (use Alembic in real projects)
        await conn.execute(SCHEMA)  # create table and index
    yield  # app runs
    await app.state.pool.close()  # graceful shutdown


app = FastAPI(lifespan=lifespan)  # app


async def get_conn(request: Request) -> AsyncIterator[asyncpg.Connection]:  # per-request connection
    try:  # acquiring can time out if pool is exhausted
        async with request.app.state.pool.acquire(timeout=3) as conn:  # borrow connection, wait max 3 s
            yield conn  # give to route
    except asyncpg.exceptions.InterfaceError as exc:  # pool closed or broken
        raise HTTPException(status_code=503, detail="database unavailable") from exc  # map to 503
    except TimeoutError as exc:  # pool exhausted
        raise HTTPException(status_code=503, detail="database busy") from exc  # backpressure


Conn = Annotated[asyncpg.Connection, Depends(get_conn)]  # shortcut type


class SaveIn(BaseModel):  # body
    user_id: str  # who
    description: str = Field(min_length=3, max_length=2000)  # input
    hs_code: str  # result
    confidence: float = Field(ge=0, le=1)  # score
    prompt_tokens: int = Field(ge=0)  # input tokens
    completion_tokens: int = Field(ge=0)  # output tokens


@app.post("/classifications", status_code=201)  # save a result
async def save(body: SaveIn, conn: Conn) -> dict[str, int]:  # handler
    try:  # DB errors
        async with conn.transaction():  # atomic block
            new_id = await conn.fetchval(  # INSERT ... RETURNING id
                """INSERT INTO classifications
                   (user_id, description, hs_code, confidence, prompt_tokens, completion_tokens)
                   VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""",  # parameters prevent SQL injection
                body.user_id, body.description, body.hs_code, body.confidence,
                body.prompt_tokens, body.completion_tokens,  # values in order
            )  # id of new row
    except asyncpg.PostgresError as exc:  # any database error
        raise HTTPException(status_code=500, detail="could not save") from exc  # safe message
    return {"id": new_id}  # created id


@app.get("/usage/{user_id}")  # aggregate query
async def usage(user_id: str, conn: Conn) -> dict[str, int]:  # handler
    row = await conn.fetchrow(  # one aggregate row
        """SELECT COALESCE(SUM(prompt_tokens), 0) AS p, COALESCE(SUM(completion_tokens), 0) AS c, COUNT(*) AS n
           FROM classifications
           WHERE user_id = $1 AND created_at >= now() - interval '1 day'""",  # last 24 hours
        user_id,  # parameter
    )  # result
    return {"prompt_tokens": row["p"], "completion_tokens": row["c"], "requests": row["n"]}  # JSON


@app.get("/health/db")  # health check
async def health(conn: Conn) -> dict[str, bool]:  # handler
    return {"ok": await conn.fetchval("SELECT 1") == 1}  # simple ping
```

---

## 🟠 FastAPI Integration
Best practice: one pool per worker process created in `lifespan`; routes borrow connections through a dependency; keep transactions short; map DB errors to 503/409/500. For many teams SQLAlchemy 2.0 async (`create_async_engine("postgresql+asyncpg://...")`) is used for ORM features, with asyncpg still underneath.

```python
# SQLAlchemy 2.0 async engine on top of asyncpg (alternative)
from sqlalchemy import text  # raw SQL wrapper
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # async ORM pieces

engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost/postgres", pool_size=10)  # pool
Session = async_sessionmaker(engine, expire_on_commit=False)  # session factory


async def count_rows() -> int:  # example usage
    async with Session() as session:  # session context
        result = await session.execute(text("SELECT count(*) FROM classifications"))  # run SQL
        return result.scalar_one()  # single value
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph persists conversation state with checkpointers; `langgraph-checkpoint-postgres` provides `AsyncPostgresSaver` so threads survive restarts. For RAG, `langchain-postgres` offers `PGVector`, a vector store backed by pgvector. Use the same Postgres for app data and vectors when scale is moderate.

```python
# LangGraph Postgres checkpointer (pip install langgraph-checkpoint-postgres psycopg[pool])
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver  # async saver

DB_URI = "postgresql://postgres:postgres@localhost:5432/postgres"  # connection string


async def build_graph(builder):  # builder = a LangGraph StateGraph
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as saver:  # open saver
        await saver.setup()  # create checkpoint tables (first run)
        graph = builder.compile(checkpointer=saver)  # compile with persistence
        return await graph.ainvoke({"messages": []}, config={"configurable": {"thread_id": "user-1"}})  # run
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: SQL built with f-strings (SQL injection)
✅ Correct: parameters `$1, $2`.

```python
# Wrong: user_id = "x'; DROP TABLE classifications; --"
await conn.fetch(f"SELECT * FROM classifications WHERE user_id = '{user_id}'")
# Right
await conn.fetch("SELECT * FROM classifications WHERE user_id = $1", user_id)
```

❌ Mistake 2: Connecting per request or never releasing connections
✅ Correct: a pool and `async with pool.acquire()`.

```python
# Wrong: new TCP + auth each request; leaks if error occurs
conn = await asyncpg.connect(DSN)
rows = await conn.fetch("SELECT 1")
# Right
async with pool.acquire() as conn:
    rows = await conn.fetch("SELECT 1")
```

❌ Mistake 3: Holding a connection (or a transaction) while waiting for the LLM. The LLM call takes seconds; the connection would be idle but unavailable. Fetch data, release, call the LLM, then acquire again to save.

---

## 🧠 Tricky Interview Question

**Q**: "Under load your API starts failing with 'too many clients already' from Postgres, though each request is short. Pool max_size is 20 and you run 8 workers on 3 servers. Why?"

**Answer**: Pools are per process. 20 connections x 8 workers x 3 servers = 480 connections, above Postgres's default `max_connections` of 100. Fix: size the pool so the total fits (for example max_size 3 per worker), put PgBouncer (transaction pooling) in front, scale Postgres, and avoid holding connections during LLM calls. Note that with PgBouncer in transaction mode you must disable asyncpg's prepared statement cache (`statement_cache_size=0`).

---

## ⚫ Interview Questions + Answers

Q1: Why asyncpg instead of psycopg2 in FastAPI? (Easy)
A1: psycopg2 is blocking, so it would stall the event loop in `async def` routes. asyncpg is async-native and fast (binary protocol). (psycopg 3 also supports async.)

Q2: What are `fetch`, `fetchrow`, `fetchval`, `execute`? (Easy)
A2: `fetch` returns a list of Records, `fetchrow` returns one Record or None, `fetchval` returns a single value, `execute` runs a statement and returns a status string.

Q3: Why use a connection pool? (Medium)
A3: Opening connections is expensive and Postgres limits them. A pool keeps a small set of open connections and lends them out, which reduces latency and protects the database. `acquire()` waits when all are busy, giving natural backpressure.

Q4: How do transactions work in asyncpg? (Medium)
A4: `async with conn.transaction():` begins a transaction; leaving normally commits, an exception rolls back. Keep them short and never include LLM calls inside, because they hold locks and the connection.

Q5: How would you store and search embeddings for the tariff catalog in Postgres? (Hard)
A5: Install pgvector, add `embedding vector(1536)` to `hs_codes`, build an HNSW index (`CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)`), and query `ORDER BY embedding <=> $1 LIMIT 10` with the query vector. With asyncpg you must register a codec or pass the vector as text (`'[0.1,0.2]'::vector`) or use the `pgvector` Python package's `register_vector`. Combine with SQL filters (chapter, country) for hybrid retrieval. Trade-offs: simple stack and transactional consistency versus a dedicated vector DB at very large scale.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need durable, queryable records (audit logs, usage, users)
- You want SQL joins, transactions and constraints
- Moderate vector search needs (pgvector)

❌ Avoid when:
- You only need a cache or counters (Redis is better)
- Huge-scale vector search with strict latency (consider a dedicated vector DB)
- Storing large files (use object storage and keep the URL in Postgres)

---

## 📊 Visual Diagram
```
 startup ──► create_pool(min=2,max=10) ──► app.state.pool
                                   ┌───────────────────────────┐
 request A ─ acquire ─► [conn1] ───┤  PostgreSQL (max_conn=100) │
 request B ─ acquire ─► [conn2] ───┤                           │
 request C ─ acquire ─► (wait...) ─┘                           │
 release → conn goes back to pool (not closed)

 Rule: LLM call happens OUTSIDE acquire():
   read data → release → await llm → acquire → save → release
```

---

## 💰 Cost Impact
Database design affects token cost: storing LLM outputs keyed by a hash of the normalised input lets you reuse answers (cache) instead of paying again; storing `prompt_tokens` and `completion_tokens` per row enables per-user billing and anomaly detection; indexes keep these queries cheap. Holding connections during slow LLM calls forces a bigger pool and a bigger database instance, which costs real money. Example: a 30 percent cache hit rate on 100K daily queries at 800 tokens saves 24M tokens per day, about $3.6/day on gpt-4o-mini input pricing, for a few cents of storage.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| asyncpg | Async PostgreSQL driver | async PostgreSQL driver |
| Pool | Reusable set of connections | connections का reusable समूह |
| acquire | Borrow a connection | connection उधार लेना |
| Transaction | All-or-nothing group of SQL | सब या कुछ नहीं वाला SQL समूह |
| Parameterised query | Values passed separately ($1) | values अलग से देना |
| DSN | Connection string | connection string |
| pgvector | Postgres extension for vectors | vectors के लिए extension |
| Migration | Versioned schema change | schema बदलाव का version |

---

## ⚡ 3-Line Summary
English: Use asyncpg with a pool created once in `lifespan`, borrow connections per request, and always use `$1` parameters. Keep transactions short and never hold a connection during an LLM call. Store usage and results to audit, cache and bill.
Hindi: `lifespan` में एक बार pool बनाकर asyncpg use करो, हर request में connection उधार लो, और हमेशा `$1` parameters लगाओ। Transactions छोटे रखो और LLM call के दौरान connection मत पकड़ो। Audit, cache और billing के लिए usage और results store करो।

---

## ➡️ Next Topic
**015. FastAPI + Redis Integration** — Postgres is durable but slower; Redis gives fast caching, rate limits and counters in front of the LLM.
