---

# 019. PostgreSQL Async Queries
# हिंदी में: PostgreSQL Async Queries

---

## 🔵 Simple Definition (English)
Async queries are SQL statements run with `await`, so while Postgres works the event loop can serve other requests. With asyncpg you use `fetch`, `fetchrow`, `fetchval`, `execute`, `executemany`, `copy_records_to_table` and transactions. Writing good queries (parameters, indexes, batching, pagination) matters as much as the driver.

## 🔵 सरल परिभाषा (Hindi)
Async queries ऐसे SQL statements हैं जो `await` से चलते हैं, इसलिए Postgres के काम करते समय event loop दूसरी requests संभाल सकता है। asyncpg में `fetch`, `fetchrow`, `fetchval`, `execute`, `executemany`, `copy_records_to_table` और transactions use होते हैं। अच्छी queries लिखना (parameters, indexes, batching, pagination) driver जितना ही ज़रूरी है।

---

## 🔴 Problem it Solves
Slow or unsafe queries ruin AI services: a query that scans a 10-million-row usage table blocks a pooled connection for seconds and starves other requests; string-built SQL allows injection; inserting 10,000 embeddings one by one takes minutes. Knowing the async query toolbox keeps the API fast and the database safe.

## 🔴 यह क्यों बना? (Hindi)
धीमी या असुरक्षित queries AI services बिगाड़ देती हैं: 1 करोड़ rows की usage table scan करने वाली query pooled connection को seconds तक रोक देती है और दूसरी requests भूखी रह जाती हैं; string से बना SQL injection की जगह देता है; 10,000 embeddings एक-एक करके insert करने में minutes लगते हैं। Async query toolbox जानने से API तेज़ और database सुरक्षित रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Borrow a connection: async with pool.acquire() as conn
Step 2 → Write SQL with numbered parameters ($1, $2); values are sent separately (no injection)
Step 3 → Pick the method: fetch (many rows), fetchrow (one), fetchval (one value), execute (no rows)
Step 4 → Many writes: executemany or copy_records_to_table (bulk, much faster than a loop)
Step 5 → Several statements that must succeed together: async with conn.transaction()
Step 6 → Read big results lazily: cursor inside a transaction, or keyset pagination (WHERE id > $1 LIMIT n)
Step 7 → Check plans with EXPLAIN ANALYZE; add indexes; set command_timeout so slow queries cannot hang
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Connection उधार लो: async with pool.acquire() as conn
Step 2 → क्रमांकित parameters ($1, $2) वाला SQL लिखो; values अलग भेजी जाती हैं (injection नहीं)
Step 3 → Method चुनो: fetch (कई rows), fetchrow (एक), fetchval (एक value), execute (rows नहीं)
Step 4 → कई writes: executemany या copy_records_to_table (loop से बहुत तेज़)
Step 5 → जो statements साथ सफल होने चाहिए: async with conn.transaction()
Step 6 → बड़े results lazily पढ़ो: transaction में cursor, या keyset pagination (WHERE id > $1 LIMIT n)
Step 7 → EXPLAIN ANALYZE से plan देखो; indexes जोड़ो; command_timeout लगाओ ताकि धीमी query अटके नहीं
```

---

## 🟡 Real World Example
**Tariff Classification System**: (1) Usage report: tokens per user for the last 7 days using an index on `(user_id, created_at)`; (2) bulk-load 50,000 HS code rows with `copy_records_to_table`; (3) paginate the audit log with keyset pagination, so page 500 is as fast as page 1; (4) upsert classification cache rows with `INSERT ... ON CONFLICT DO UPDATE`.

**Amazon AI**: Insert generated descriptions in batches of 1,000 in one transaction, and mark the batch as processed so a crash can resume.

## 🟡 Real Example Hindi mein
**Tariff System**: (1) Usage report: पिछले 7 दिनों में प्रति user tokens, `(user_id, created_at)` index से; (2) 50,000 HS code rows `copy_records_to_table` से bulk-load; (3) audit log keyset pagination से, ताकि page 500 भी page 1 जितना तेज़ हो; (4) classification cache rows `INSERT ... ON CONFLICT DO UPDATE` से upsert।

**Amazon AI**: Generated descriptions 1,000 के batches में एक transaction में insert होते हैं और batch को processed mark किया जाता है ताकि crash के बाद resume हो सके।

---

## 💻 Code Example — Basic
```python
# Basic async queries with asyncpg. Needs Postgres: set DATABASE_URL (pip install asyncpg)
import asyncio  # run async main
import os  # env

import asyncpg  # driver


async def main() -> None:  # demo
    conn = await asyncpg.connect(os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"))  # connect
    try:  # always close
        await conn.execute("CREATE TEMP TABLE usage (id SERIAL PRIMARY KEY, user_id TEXT, tokens INT)")  # temp table
        await conn.executemany(  # many inserts in one call
            "INSERT INTO usage (user_id, tokens) VALUES ($1, $2)",  # parameterised
            [("alice", 500), ("alice", 300), ("bob", 700)],  # rows
        )  # inserted
        rows = await conn.fetch("SELECT user_id, SUM(tokens) AS total FROM usage GROUP BY user_id ORDER BY total DESC")  # aggregate
        for r in rows:  # loop over Records
            print(r["user_id"], r["total"])  # bob 700 / alice 800 order depends on totals
        one = await conn.fetchrow("SELECT * FROM usage WHERE user_id = $1 ORDER BY id LIMIT 1", "alice")  # one row
        print(dict(one))  # Record to dict
        total = await conn.fetchval("SELECT SUM(tokens) FROM usage")  # single value
        print("all tokens:", total)  # 1500
    finally:  # cleanup
        await conn.close()  # close connection


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run (needs Postgres)
```

## 💻 Code Example — Advanced
```python
# Production query patterns: pool, bulk COPY, upsert, keyset pagination, transaction with locking,
# concurrent queries with gather on separate connections, timeouts and error mapping.
import asyncio  # async
from dataclasses import dataclass  # result type
from typing import Any  # typing

import asyncpg  # driver
from asyncpg import Pool  # pool type


@dataclass
class Page:  # pagination result
    rows: list[dict[str, Any]]  # items
    next_cursor: int | None  # last id for the next page


class QueryError(Exception):  # our error type
    """Raised for database problems."""


async def bulk_load_codes(pool: Pool, codes: list[tuple[str, str]]) -> int:  # fast bulk insert
    async with pool.acquire() as conn:  # connection
        async with conn.transaction():  # atomic load
            await conn.execute("CREATE TEMP TABLE staging (code TEXT, name TEXT) ON COMMIT DROP")  # temp staging
            await conn.copy_records_to_table("staging", records=codes, columns=["code", "name"])  # COPY protocol: very fast
            result = await conn.execute(  # move into real table, ignoring duplicates (upsert)
                """INSERT INTO hs_codes (code, name) SELECT code, name FROM staging
                   ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name""",  # update existing names
            )  # status like "INSERT 0 50000"
    return int(result.split()[-1])  # number of rows affected


async def audit_page(pool: Pool, user_id: str, after_id: int | None = None, limit: int = 50) -> Page:  # keyset pagination
    limit = min(max(limit, 1), 200)  # clamp page size
    try:  # DB errors
        async with pool.acquire(timeout=3) as conn:  # wait max 3 s for a connection
            rows = await conn.fetch(  # no OFFSET: stays fast on deep pages
                """SELECT id, description, hs_code, created_at FROM classifications
                   WHERE user_id = $1 AND ($2::bigint IS NULL OR id < $2)
                   ORDER BY id DESC LIMIT $3""",  # needs index (user_id, id DESC)
                user_id, after_id, limit,  # parameters
                timeout=5,  # per-query timeout in seconds
            )  # list of Records
    except (asyncpg.PostgresError, TimeoutError, asyncio.TimeoutError) as exc:  # map errors
        raise QueryError(f"audit query failed: {type(exc).__name__}") from exc  # safe message
    items = [dict(r) for r in rows]  # to dicts
    return Page(items, items[-1]["id"] if len(items) == limit else None)  # cursor only if more may exist


async def reserve_budget(pool: Pool, user_id: str, tokens: int, daily_limit: int) -> bool:  # safe read-modify-write
    async with pool.acquire() as conn:  # connection
        async with conn.transaction():  # transaction
            row = await conn.fetchrow(  # lock the user's budget row so concurrent requests queue up
                "SELECT used FROM budgets WHERE user_id = $1 FOR UPDATE", user_id,  # row lock
            )  # None if no row
            used = row["used"] if row else 0  # current usage
            if used + tokens > daily_limit:  # would exceed
                return False  # reject, transaction rolls back nothing harmful
            await conn.execute(  # upsert new usage
                """INSERT INTO budgets (user_id, used) VALUES ($1, $2)
                   ON CONFLICT (user_id) DO UPDATE SET used = budgets.used + EXCLUDED.used""",
                user_id, tokens,  # parameters
            )  # saved
            return True  # reserved


async def dashboard(pool: Pool, user_id: str) -> dict[str, Any]:  # several independent queries at once
    async def one(sql: str, *args: Any) -> Any:  # helper: each query uses its own connection
        async with pool.acquire() as conn:  # separate connection (a single connection runs one query at a time)
            return await conn.fetchval(sql, *args)  # value

    total, today, requests = await asyncio.gather(  # parallel on different connections
        one("SELECT COALESCE(SUM(prompt_tokens + completion_tokens), 0) FROM classifications WHERE user_id = $1", user_id),
        one("SELECT COALESCE(SUM(prompt_tokens + completion_tokens), 0) FROM classifications "
            "WHERE user_id = $1 AND created_at >= date_trunc('day', now())", user_id),
        one("SELECT COUNT(*) FROM classifications WHERE user_id = $1", user_id),
    )  # three numbers
    return {"total_tokens": total, "today_tokens": today, "requests": requests}  # result


async def main() -> None:  # demo wiring (needs the tables from topic 014 plus hs_codes and budgets)
    pool = await asyncpg.create_pool("postgresql://postgres:postgres@localhost:5432/postgres", min_size=1, max_size=5)  # pool
    try:  # cleanup
        print(await dashboard(pool, "alice"))  # run dashboard
    finally:  # close
        await pool.close()  # close pool


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Expose paginated, bounded endpoints: always clamp `limit`, return a `next_cursor`, set per-query timeouts, and map `QueryError` to 503/500. Keep SQL in a repository module, so routes stay thin.

```python
# Paginated audit endpoint using the repository function above
from fastapi import APIRouter, HTTPException, Query, Request  # tools

router = APIRouter()  # router


@router.get("/audit/{user_id}")  # route
async def audit(request: Request, user_id: str, after_id: int | None = None,
                limit: int = Query(50, ge=1, le=200)) -> dict:  # bounded page size
    try:  # DB call
        page = await audit_page(request.app.state.pool, user_id, after_id, limit)  # repository function
    except QueryError:  # mapped error
        raise HTTPException(status_code=503, detail="database temporarily unavailable")  # safe message
    return {"items": page.rows, "next_cursor": page.next_cursor}  # JSON
```

---

## 🔗 LangChain / LangGraph Connection
For RAG on Postgres, `langchain-postgres` provides `PGVector` (similarity search with metadata filters); LangGraph's `AsyncPostgresSaver` stores checkpoints. For custom retrievers, write your own async SQL with pgvector (`ORDER BY embedding <=> $1`) in a `BaseRetriever._aget_relevant_documents`.

```python
# Custom async retriever using pgvector SQL (needs pgvector extension and an embedding function)
from langchain_core.callbacks import AsyncCallbackManagerForRetrieverRun  # run manager
from langchain_core.documents import Document  # document
from langchain_core.retrievers import BaseRetriever  # base class


class PgRetriever(BaseRetriever):  # custom retriever
    pool: object  # asyncpg pool (arbitrary type allowed below)
    k: int = 5  # number of results
    model_config = {"arbitrary_types_allowed": True}  # allow non-pydantic types

    def _get_relevant_documents(self, query: str, *, run_manager) -> list[Document]:  # sync version not supported
        raise NotImplementedError("use ainvoke")  # force async use

    async def _aget_relevant_documents(self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun) -> list[Document]:  # async
        vector = await embed(query)  # your async embedding function returning list[float]
        literal = "[" + ",".join(str(x) for x in vector) + "]"  # pgvector text format
        async with self.pool.acquire() as conn:  # connection
            rows = await conn.fetch(  # nearest neighbours by cosine distance
                "SELECT code, name FROM hs_codes ORDER BY embedding <=> $1::vector LIMIT $2", literal, self.k,
            )  # rows
        return [Document(page_content=r["name"], metadata={"code": r["code"]}) for r in rows]  # to Documents
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: `OFFSET` pagination on big tables
✅ Correct: keyset pagination.

```python
# Wrong: page 10,000 scans and discards 500,000 rows
await conn.fetch("SELECT * FROM classifications ORDER BY id DESC LIMIT 50 OFFSET 500000")
# Right: remember the last id seen
await conn.fetch("SELECT * FROM classifications WHERE id < $1 ORDER BY id DESC LIMIT 50", last_id)
```

❌ Mistake 2: Running queries in a loop (N+1) or inserting row by row
✅ Correct: one query with `ANY`, or `executemany`/`COPY`.

```python
# Wrong: 1,000 round trips
for code in codes:
    await conn.fetchrow("SELECT * FROM hs_codes WHERE code = $1", code)
# Right: one round trip
rows = await conn.fetch("SELECT * FROM hs_codes WHERE code = ANY($1::text[])", codes)
```

❌ Mistake 3: Using one connection for `asyncio.gather` of several queries. A single connection runs one operation at a time (asyncpg raises "another operation is in progress"). Acquire separate connections from the pool for parallel queries.

---

## 🧠 Tricky Interview Question

**Q**: "Two simultaneous requests from the same user both read `used=900` of a 1000-token budget, each reserves 80, and the user ends up spending 1,060. How do you fix it?"

**Answer**: It is a read-modify-write race. Fix with an atomic statement or a row lock: `SELECT ... FOR UPDATE` inside a transaction (as in `reserve_budget`), or a single `UPDATE budgets SET used = used + $2 WHERE user_id = $1 AND used + $2 <= $3 RETURNING used` and check whether a row came back. For very high rates use Redis `INCRBY` with a Lua script, then reconcile to Postgres. Always keep the transaction short and do not call the LLM inside it.

---

## ⚫ Interview Questions + Answers

Q1: Why must you use `$1` parameters instead of f-strings? (Easy)
A1: Parameters send values separately from SQL text, preventing SQL injection and letting Postgres cache plans.

Q2: Difference between `fetch` and `fetchrow`? (Easy)
A2: `fetch` returns a list of all rows; `fetchrow` returns the first row (or None); `fetchval` returns the first column of the first row.

Q3: Why is keyset pagination faster than OFFSET? (Medium)
A3: OFFSET makes Postgres read and discard all skipped rows, so deep pages get slower. Keyset uses an indexed `WHERE id < last_id` so each page is an index seek of constant cost. Trade-off: no random page jumps, needs a stable unique ordering.

Q4: How do you bulk-insert 100K rows quickly? (Medium)
A4: `copy_records_to_table` (COPY protocol) is fastest; `executemany` is good for thousands; avoid per-row `execute`. For upserts, COPY into a temp staging table, then `INSERT ... SELECT ... ON CONFLICT`.

Q5: How do you diagnose and fix a slow query affecting API latency? (Hard)
A5: Reproduce with `EXPLAIN (ANALYZE, BUFFERS)`; look for sequential scans on large tables, bad row estimates and sorts spilling to disk. Add the right composite index (equality columns first, then range/order column), avoid functions on indexed columns, run `ANALYZE`, consider partial indexes and partitioning by time for logs, and set `statement_timeout` or asyncpg `command_timeout` to protect the pool. Use `pg_stat_statements` to find top offenders in production, and check pool saturation (waiting acquires) to see if slow queries are starving other requests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Durable records and reports: usage, audit, billing
- Bulk loading datasets (tariff codes, embeddings)
- Transactions and constraints matter

❌ Avoid when:
- Simple counters or short-lived cache (use Redis)
- Huge analytical scans on the production primary (use a replica or warehouse)
- Long transactions that wait on LLM calls

---

## 📊 Visual Diagram
```
  OFFSET pagination                     Keyset pagination
  page 1:  read 50                      page 1:  WHERE id < ∞    → index seek, 50 rows
  page 2:  read 100, drop 50            page 2:  WHERE id < 951  → index seek, 50 rows
  page N:  read 50*N, drop 50*(N-1)     page N:  WHERE id < k    → index seek, 50 rows
  (slower each page)                    (constant cost)

  Parallel queries:   pool ─► conn1: Q1 ─┐
                             conn2: Q2 ─┼─ gather ─► results
                             conn3: Q3 ─┘      (one connection = one query at a time)
```

---

## 💰 Cost Impact
Queries do not consume LLM tokens, but they shape them: storing `prompt_tokens` and `completion_tokens` per request enables per-user and per-feature spend reports (`GROUP BY`), anomaly alerts, and cache lookups keyed by input hash that skip the LLM entirely. Efficient SQL keeps database size and pool size small, which cuts infrastructure cost. Example: a cache table with `ON CONFLICT` upserts that serves 30 percent of 100K daily 800-token queries saves about 24M tokens per day (about $3.6 on gpt-4o-mini input pricing), at the cost of one indexed lookup per request.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| fetch / fetchrow / fetchval | Read many / one row / one value | कई / एक row / एक value पढ़ना |
| executemany | Run one statement for many rows | कई rows के लिए एक statement |
| COPY | Fastest bulk load protocol | सबसे तेज़ bulk load |
| Upsert | Insert or update if exists | नहीं है तो insert, है तो update |
| Keyset pagination | Paginate by last seen key | आख़िरी key से pagination |
| Index | Structure to find rows fast | rows जल्दी ढूँढने की संरचना |
| FOR UPDATE | Lock selected rows | चुनी rows को lock करना |
| EXPLAIN ANALYZE | Show real query plan | असली query plan देखना |

---

## ⚡ 3-Line Summary
English: Use asyncpg with `$` parameters, the right fetch method, bulk COPY/executemany for writes, and keyset pagination for big tables. Use transactions and row locks for race-free budgets, and separate pooled connections for parallel queries. Never hold a connection during an LLM call.
Hindi: asyncpg में `$` parameters, सही fetch method, writes के लिए bulk COPY/executemany और बड़ी tables के लिए keyset pagination use करो। Race-free budgets के लिए transactions और row locks, और parallel queries के लिए अलग pooled connections लो। LLM call के दौरान connection कभी मत पकड़ो।

---

## ➡️ Next Topic
**020. Connection Pooling in FastAPI** — finally, how to size and manage pools (DB, Redis, HTTP clients) so the whole service stays stable under load.
