---

# 144. pgvector Setup
# हिंदी में: pgvector Setup (Postgres में Vector Search)

---

## 🔵 Simple Definition (English)
pgvector is a PostgreSQL extension that adds a `vector` column type and similarity operators. You store embeddings next to your normal rows (id, HS code, description) and search them with plain SQL. No separate vector database is needed.

## 🔵 सरल परिभाषा (Hindi)
pgvector PostgreSQL का extension है जो `vector` column type और similarity operators जोड़ता है। Embeddings आपके normal rows (id, HS code, description) के साथ ही store होते हैं और SQL से search होते हैं। अलग vector database की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
Teams already run Postgres for users, orders and tariff tables. Adding a second database just for vectors means two systems to deploy, back up, secure and keep in sync. Metadata filters (country, year) need joins across systems. pgvector keeps vectors, metadata and transactions in one place.

## 🔴 यह क्यों बना? (Hindi)
ज़्यादातर teams के पास पहले से Postgres होता है। सिर्फ vectors के लिए दूसरा database मतलब दो systems का deploy, backup, security और sync। pgvector में vectors, metadata और transactions एक ही जगह रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run Postgres with pgvector installed (docker image pgvector/pgvector:pg16)
Step 2 → CREATE EXTENSION vector;   (once per database)
Step 3 → CREATE TABLE with a column vector(1536)   (dimension must match the embedding model)
Step 4 → Generate embeddings (text-embedding-3-small = 1536 dims) and INSERT them
Step 5 → CREATE INDEX (HNSW or IVFFlat) for fast approximate search
Step 6 → Query with ORDER BY embedding <=> query_vector LIMIT k
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → pgvector वाला Postgres चलाओ (docker image pgvector/pgvector:pg16)
Step 2 → CREATE EXTENSION vector;   (हर database में एक बार)
Step 3 → vector(1536) column वाली table बनाओ (dimension embedding model से match होनी चाहिए)
Step 4 → Embeddings बनाओ और INSERT करो
Step 5 → तेज़ approximate search के लिए HNSW या IVFFlat index बनाओ
Step 6 → ORDER BY embedding <=> query_vector LIMIT k से query करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: a table `tariff_codes(hs_code, description, country, embedding vector(1536))` holds 20,000 HS code descriptions. A user types "wireless bluetooth earbuds"; we embed it and fetch the 5 closest descriptions, filtered by `country = 'IN'`. Because it is just Postgres, the same DB also stores classification history and audit logs.

**Zomato AI**: restaurant dishes with embeddings live in the same Postgres as menus and prices, so "spicy paneer under 300 rupees" is one SQL query: vector similarity plus `price < 300`.

## 🟡 Real Example Hindi mein
**Tariff System**: `tariff_codes` table में 20,000 HS code descriptions और उनके embeddings हैं। User "wireless bluetooth earbuds" लिखता है, हम embed करके `country = 'IN'` filter के साथ 5 सबसे नज़दीकी descriptions निकालते हैं। Classification history भी उसी DB में रहती है।

**Zomato AI**: dishes के embeddings menus और prices वाले Postgres में ही हैं, इसलिए "300 रुपये से सस्ता spicy paneer" एक ही SQL query है।

---

## 💻 Code Example — Basic
```python
# pip install "psycopg[binary]"
# Start DB: docker run -e POSTGRES_PASSWORD=pw -p 5432:5432 pgvector/pgvector:pg16
import psycopg  # PostgreSQL driver (psycopg 3)

DSN = "postgresql://postgres:pw@localhost:5432/postgres"  # connection string


def to_literal(vec: list[float]) -> str:
    """Convert a python list into pgvector text format like '[0.1,0.2]'."""
    return "[" + ",".join(str(x) for x in vec) + "]"  # join numbers with commas


def setup() -> None:
    """Create extension and table (idempotent)."""
    with psycopg.connect(DSN) as conn:  # open connection, auto-commit on exit
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")  # enable pgvector
        conn.execute(  # create table with a 3-dim vector (tiny for demo)
            """CREATE TABLE IF NOT EXISTS tariff_demo (
                   id SERIAL PRIMARY KEY,
                   hs_code TEXT NOT NULL,
                   description TEXT NOT NULL,
                   embedding vector(3)
               )"""
        )
        conn.execute(  # insert a row; %s::vector casts the text to vector
            "INSERT INTO tariff_demo (hs_code, description, embedding) VALUES (%s, %s, %s::vector)",
            ("8518.30", "Headphones and earphones", to_literal([0.9, 0.1, 0.0])),
        )
        row = conn.execute(  # nearest neighbour by cosine distance
            "SELECT hs_code, description FROM tariff_demo ORDER BY embedding <=> %s::vector LIMIT 1",
            (to_literal([0.8, 0.2, 0.0]),),
        ).fetchone()  # get one row
        print(row)  # ('8518.30', 'Headphones and earphones')


if __name__ == "__main__":
    setup()  # needs a running pgvector database
```

## 💻 Code Example — Advanced
```python
# Production setup: real embeddings, connection pool, async, error handling
import asyncio
import logging
from typing import Sequence

from openai import AsyncOpenAI  # openai>=1
from psycopg_pool import AsyncConnectionPool  # pip install "psycopg[binary]" psycopg_pool

logger = logging.getLogger("pgvector_setup")  # module logger
EMBED_MODEL = "text-embedding-3-small"  # 1536 dimensions
DIM = 1536  # must match the model


def to_literal(vec: Sequence[float]) -> str:
    """pgvector text literal."""
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"  # fixed precision keeps SQL small


class TariffStore:
    """Owns schema creation, ingestion and search for tariff vectors."""

    def __init__(self, dsn: str) -> None:
        self.pool = AsyncConnectionPool(dsn, min_size=2, max_size=10, open=False)  # lazy pool
        self.client = AsyncOpenAI()  # reads OPENAI_API_KEY from env

    async def open(self) -> None:
        await self.pool.open()  # start the pool
        async with self.pool.connection() as conn:  # borrow a connection
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")  # enable extension
            await conn.execute(  # schema with metadata columns for filtering
                f"""CREATE TABLE IF NOT EXISTS tariff_codes (
                        id BIGSERIAL PRIMARY KEY,
                        hs_code TEXT NOT NULL,
                        description TEXT NOT NULL,
                        country TEXT NOT NULL DEFAULT 'IN',
                        embedding vector({DIM}) NOT NULL
                    )"""
            )
            await conn.execute(  # HNSW index with cosine ops (build AFTER bulk load for speed)
                "CREATE INDEX IF NOT EXISTS tariff_hnsw ON tariff_codes "
                "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
            )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Batch-embed texts (one API call for many inputs saves latency)."""
        resp = await self.client.embeddings.create(model=EMBED_MODEL, input=texts)
        return [d.embedding for d in resp.data]  # keep the original order

    async def add(self, rows: list[tuple[str, str, str]]) -> int:
        """rows = (hs_code, description, country). Returns inserted count."""
        try:
            vectors = await self.embed([r[1] for r in rows])  # embed descriptions
        except Exception:
            logger.exception("embedding failed")  # log full traceback
            raise
        async with self.pool.connection() as conn:  # one transaction for all rows
            async with conn.cursor() as cur:
                await cur.executemany(
                    "INSERT INTO tariff_codes (hs_code, description, country, embedding) "
                    "VALUES (%s, %s, %s, %s::vector)",
                    [(h, d, c, to_literal(v)) for (h, d, c), v in zip(rows, vectors)],
                )
        return len(rows)

    async def close(self) -> None:
        await self.pool.close()  # release connections


async def main() -> None:
    store = TariffStore("postgresql://postgres:pw@localhost:5432/postgres")
    await store.open()
    n = await store.add([("8518.30", "Headphones, earphones", "IN"), ("8517.13", "Smartphones", "IN")])
    print("inserted", n)
    await store.close()


if __name__ == "__main__":
    asyncio.run(main())  # needs DB + OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
Open the pool once in the app `lifespan` and share it through `app.state`. Never create a connection per request.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# TariffStore is the class from the Advanced example above
store = TariffStore("postgresql://postgres:pw@localhost:5432/postgres")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await store.open()  # startup: create pool + schema
    yield
    await store.close()  # shutdown: close pool


app = FastAPI(lifespan=lifespan)


class AddItem(BaseModel):
    hs_code: str
    description: str
    country: str = "IN"


@app.post("/tariff/items")
async def add_item(item: AddItem) -> dict[str, int]:
    try:
        n = await store.add([(item.hs_code, item.description, item.country)])
    except Exception as exc:  # DB or embedding error
        raise HTTPException(status_code=502, detail=f"ingest failed: {exc}")
    return {"inserted": n}
```

---

## 🔗 LangChain / LangGraph Connection
`langchain-postgres` provides `PGVector`, a ready vector store that creates tables itself and plugs into retrievers and LangGraph nodes.

```python
# pip install langchain-postgres langchain-openai
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

store = PGVector(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),  # embedding function
    collection_name="tariff",  # logical collection
    connection="postgresql+psycopg://postgres:pw@localhost:5432/postgres",  # SQLAlchemy URL
)
store.add_texts(["Headphones and earphones", "Smartphones"], metadatas=[{"hs": "8518.30"}, {"hs": "8517.13"}])
retriever = store.as_retriever(search_kwargs={"k": 3})  # use inside any LCEL chain or LangGraph node
docs = retriever.invoke("bluetooth earbuds")  # list[Document]
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Dimension mismatch between column and embedding model
```python
# Wrong: column is vector(1536) but model returns 3072 dims -> "expected 1536 dimensions, not 3072"
#   CREATE TABLE t (embedding vector(1536));  model = "text-embedding-3-large"
# Right: set the column to the model's dimension (or request dimensions=1536)
resp = client.embeddings.create(model="text-embedding-3-large", input="x", dimensions=1536)
```

❌ Mistake 2: Creating the HNSW index before loading millions of rows, or forgetting it entirely
```python
# Wrong: index exists during a bulk load -> very slow inserts; no index at all -> full scan on every query
# Right: bulk load first, then build the index once
#   COPY / executemany ...
#   CREATE INDEX CONCURRENTLY tariff_hnsw ON tariff_codes USING hnsw (embedding vector_cosine_ops);
```

---

## 🧠 Tricky Interview Question

**Q**: "You created an HNSW index with `vector_l2_ops`, but your query uses `<=>` (cosine). Queries work but are slow. Why?"

**Answer**: The planner only uses an index when the query operator matches the index operator class. `vector_l2_ops` serves `<->`, `vector_cosine_ops` serves `<=>`, `vector_ip_ops` serves `<#>`. A mismatch silently falls back to a sequential scan, so results are correct but slow. Check with `EXPLAIN` and rebuild the index with the right ops class.

---

## ⚫ Interview Questions + Answers

Q1: What is pgvector?
A1: A Postgres extension adding the `vector` type, distance operators and ANN indexes (HNSW, IVFFlat), so embeddings can be stored and searched with SQL.

Q2: Which command enables it?
A2: `CREATE EXTENSION IF NOT EXISTS vector;` once per database. Managed services (RDS, Supabase, Neon, Cloud SQL) support it.

Q3: Why must the column dimension match the model?
A3: The `vector(n)` type has a fixed length. Inserting a different length raises an error. Changing models means a new column or table and re-embedding everything.

Q4: What are the three distance operators?
A4: `<->` L2 (Euclidean), `<=>` cosine distance, `<#>` negative inner product. Choose the one your embedding model is trained for (OpenAI embeddings are normalised, so cosine and inner product give the same ranking).

Q5: How would you set up pgvector for 10 million vectors?
A5: Use HNSW, load data first and build the index after (raise `maintenance_work_mem` so the graph fits in memory), use a pool, consider `halfvec` to halve storage, partition by tenant/country, monitor recall with `hnsw.ef_search`, and put read replicas behind the search path.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You already run Postgres and have under roughly 10-50M vectors
- You need joins, transactions and metadata filters with vectors
- You want fewer moving parts

❌ Avoid when:
- You need billions of vectors or very high QPS with tiny latency
- The Postgres team cannot afford extra memory pressure on the primary

---

## 📊 Visual Diagram
```
 query text ──► embedding model ──► [0.12, -0.4, ... 1536 floats]
                                         │
                                         ▼
 ┌──────────────── PostgreSQL + pgvector ────────────────┐
 │ tariff_codes                                           │
 │  id | hs_code | description | country | embedding      │
 │                       HNSW index (vector_cosine_ops)   │
 └───────────────┬────────────────────────────────────────┘
                 ▼
   ORDER BY embedding <=> $1 LIMIT 5  ──► top-5 HS codes
```

---

## 💰 Cost Impact
- Embedding cost (one time per document): tokens x embedding price. `text-embedding-3-small` is very cheap (about a couple of cents per 1M tokens, check current pricing). Query embedding is a few tokens per request.
- Storage: 1536 floats x 4 bytes = about 6 KB per vector, so 1M vectors is about 6 GB plus index. `halfvec` halves it.
- Optimisation: batch embeddings, cache query embeddings, use `dimensions=512` or 768 on `text-embedding-3-*` to cut storage and RAM, reuse your existing Postgres instead of paying for a new service.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pgvector | Postgres extension for vectors | Postgres का vector extension |
| vector(n) | Fixed length column type | n लंबाई वाला column type |
| HNSW | Graph-based ANN index | Graph वाला approximate index |
| IVFFlat | Cluster-based ANN index | Cluster वाला index |
| Operator class | Distance type bound to an index | Index का distance प्रकार |
| Connection pool | Reused DB connections | Connections का पुन: उपयोग |

---

## ⚡ 3-Line Summary
English: pgvector turns Postgres into a vector store with a `vector(n)` column and SQL distance operators. Match the dimension to the embedding model and the operator class to the query operator. Load data first, then build the HNSW index.
Hindi: pgvector Postgres को vector store बना देता है, `vector(n)` column और SQL operators के साथ। Dimension model से और operator class query से match करो। पहले data load करो, फिर HNSW index बनाओ।

---

## ➡️ Next Topic
**145. pgvector Queries** — cosine/L2/inner product queries, metadata filters, `ef_search`, and reading `EXPLAIN` plans.
