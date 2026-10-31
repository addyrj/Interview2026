---

# 143. pgvector — PostgreSQL Extension
# हिंदी में: pgvector — PostgreSQL का Extension (SQL में vector search)

---

## 🔵 Simple Definition (English)
pgvector is an open-source PostgreSQL extension that adds a `vector(n)` column type, distance operators (`<->` L2, `<=>` cosine, `<#>` negative inner product) and ANN indexes (HNSW and IVFFlat). You store embeddings next to your normal rows and search with plain SQL (`ORDER BY embedding <=> query LIMIT 5`), including WHERE filters, JOINs and transactions.

## 🔵 सरल परिभाषा (Hindi)
pgvector एक open-source PostgreSQL extension है जो `vector(n)` column type, distance operators (`<->` L2, `<=>` cosine, `<#>` negative inner product) और ANN indexes (HNSW और IVFFlat) जोड़ता है। आप embeddings को अपनी normal rows के साथ रखते हैं और plain SQL (`ORDER BY embedding <=> query LIMIT 5`) से search करते हैं, WHERE filters, JOINs और transactions के साथ।

---

## 🔴 Problem it Solves
A separate vector database means a second system to run, secure, back up and keep in sync with your main data (user permissions, deletes, updates). Data can drift: a row is deleted in Postgres but its vector remains in the vector DB. With pgvector the vector lives in the same row, same transaction and same backup, and metadata filtering is just SQL.

## 🔴 यह क्यों बना? (Hindi)
अलग vector database का मतलब दूसरा system चलाना, secure करना, backup लेना और main data (permissions, deletes, updates) के साथ sync रखना। Data drift हो सकता है: Postgres में row delete हुई पर vector DB में vector रह गया। pgvector में vector उसी row, उसी transaction और उसी backup में रहता है, और metadata filtering बस SQL है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Install: use an image with pgvector (e.g. pgvector/pgvector:pg16) or a managed Postgres that offers it
Step 2 → CREATE EXTENSION IF NOT EXISTS vector;
Step 3 → CREATE TABLE headings (id bigserial PRIMARY KEY, hs_code text, country text, body text, embedding vector(1536));
Step 4 → INSERT rows with the embedding as a vector literal: '[0.1,0.2,...]'
Step 5 → CREATE INDEX ON headings USING hnsw (embedding vector_cosine_ops);   (or ivfflat ... WITH (lists = 100))
Step 6 → Search: SELECT hs_code, 1 - (embedding <=> $1) AS score FROM headings WHERE country = 'IN'
                 ORDER BY embedding <=> $1 LIMIT 5;
Step 7 → Tune: SET hnsw.ef_search = 100;  (or SET ivfflat.probes = 10;)
Step 8 → Maintain: VACUUM/ANALYZE, REINDEX after heavy churn, monitor with EXPLAIN ANALYZE
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Install: pgvector वाली image (जैसे pgvector/pgvector:pg16) या ऐसा managed Postgres जो इसे दे
Step 2 → CREATE EXTENSION IF NOT EXISTS vector;
Step 3 → CREATE TABLE headings (id bigserial PRIMARY KEY, hs_code text, country text, body text, embedding vector(1536));
Step 4 → Embedding को vector literal '[0.1,0.2,...]' के रूप में rows में INSERT करो
Step 5 → CREATE INDEX ON headings USING hnsw (embedding vector_cosine_ops);  (या ivfflat ... WITH (lists = 100))
Step 6 → Search: SELECT hs_code, 1 - (embedding <=> $1) AS score FROM headings WHERE country = 'IN'
                 ORDER BY embedding <=> $1 LIMIT 5;
Step 7 → Tune: SET hnsw.ef_search = 100;  (या SET ivfflat.probes = 10;)
Step 8 → Maintenance: VACUUM/ANALYZE, भारी churn के बाद REINDEX, EXPLAIN ANALYZE से monitor
```

---

## 🟡 Real World Example
**Tariff Classification System**: the company already stores customers, shipments and HS headings in Postgres. Adding `embedding vector(1536)` to the `headings` table gives semantic search without new infrastructure. A single SQL query joins `headings` with `duty_rates` and filters `country = 'IN' AND active`, then orders by cosine distance. Deleting a heading also deletes its vector in the same transaction.

**Zomato AI**: restaurant tables already have city/price columns; adding a vector column makes "similar dishes under Rs 300 in Pune" one SQL query.

## 🟡 Real Example Hindi mein
**Tariff System**: Company पहले से customers, shipments और HS headings Postgres में रखती है। `headings` table में `embedding vector(1536)` जोड़ने से नई infrastructure के बिना semantic search मिलता है। एक SQL query `headings` को `duty_rates` से join करती है, `country = 'IN' AND active` filter लगाती है और cosine distance से order करती है। Heading delete होने पर उसका vector भी उसी transaction में delete होता है। **Zomato**: Restaurant tables में city/price columns पहले से हैं; vector column जोड़ने पर "पुणे में 300 रुपये से कम similar dishes" एक SQL query बन जाती है।

---

## 💻 Code Example — Basic
```python
# Basic: pgvector SQL + a pure-Python helper for vector literals and score conversion (runs offline).
# With a real database you would run these statements through psycopg (see the advanced example).
from typing import List, Sequence                          # type hints

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS headings (
    id        bigserial PRIMARY KEY,
    hs_code   text NOT NULL,
    country   text NOT NULL,
    body      text NOT NULL,
    embedding vector(4)            -- use 1536 for text-embedding-3-small
);
CREATE INDEX IF NOT EXISTS headings_emb_hnsw
    ON headings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
"""                                                         # schema: table + HNSW index

SEARCH_SQL = """
SELECT hs_code, body, 1 - (embedding <=> %(q)s::vector) AS similarity   -- cosine similarity = 1 - cosine distance
FROM headings
WHERE country = %(country)s
ORDER BY embedding <=> %(q)s::vector                                     -- ORDER BY the distance to use the index
LIMIT %(k)s;
"""                                                         # search query with a filter

def to_vector_literal(vec: Sequence[float]) -> str:
    """Format a Python list as pgvector's text input: '[0.1,0.2,0.3]'."""
    if not vec:                                             # empty vectors are invalid
        raise ValueError("vector must not be empty")
    return "[" + ",".join(f"{float(x):.6f}" for x in vec) + "]"   # fixed precision keeps SQL short

def distance_to_similarity(distance: float) -> float:
    return 1.0 - distance                                   # cosine similarity from cosine distance

print(to_vector_literal([0.9, 0.1, 0.0, 0.1]))              # [0.900000,0.100000,0.000000,0.100000]
print(distance_to_similarity(0.17))                         # 0.83
params = {"q": to_vector_literal([1.0, 0.0, 0.1, 0.0]), "country": "IN", "k": 5}   # query parameters
# psycopg usage:  cur.execute(SEARCH_SQL, params); rows = cur.fetchall()
```

## 💻 Code Example — Advanced
```python
# Advanced: async psycopg 3 repository with a connection pool, batch insert, filtered search,
# per-query ef_search tuning and error handling.  pip install "psycopg[binary,pool]"
import asyncio                                             # async runtime
import logging                                             # logs
from typing import Any, Dict, List, Optional, Sequence

import psycopg                                             # psycopg 3
from psycopg.rows import dict_row                          # rows as dicts
from psycopg_pool import AsyncConnectionPool               # async pool

log = logging.getLogger("pgvector-repo")                   # logger

def vec(v: Sequence[float]) -> str:
    return "[" + ",".join(f"{float(x):.7f}" for x in v) + "]"      # pgvector text format

class HeadingRepo:
    def __init__(self, dsn: str, dim: int = 1536) -> None:
        self.dim = dim                                     # must match the column definition
        self.pool = AsyncConnectionPool(dsn, min_size=1, max_size=10, open=False,
                                        kwargs={"row_factory": dict_row})   # open later (async)

    async def start(self) -> None:
        await self.pool.open()                             # open connections
        async with self.pool.connection() as conn:         # create schema once
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute(f"""CREATE TABLE IF NOT EXISTS headings (
                id bigserial PRIMARY KEY, hs_code text NOT NULL, country text NOT NULL,
                body text NOT NULL, embedding vector({self.dim}))""")
            await conn.execute("""CREATE INDEX IF NOT EXISTS headings_emb_hnsw
                ON headings USING hnsw (embedding vector_cosine_ops)""")

    async def insert_many(self, rows: List[Dict[str, Any]]) -> int:
        for r in rows:                                     # validate before touching the DB
            if len(r["embedding"]) != self.dim:
                raise ValueError(f"{r['hs_code']}: expected {self.dim} dims, got {len(r['embedding'])}")
        try:
            async with self.pool.connection() as conn:     # one transaction for the whole batch
                async with conn.cursor() as cur:
                    await cur.executemany(
                        "INSERT INTO headings (hs_code, country, body, embedding) VALUES (%s, %s, %s, %s::vector)",
                        [(r["hs_code"], r["country"], r["body"], vec(r["embedding"])) for r in rows])
            return len(rows)
        except psycopg.Error as exc:                       # DB errors: log and re-raise
            log.error("insert failed: %s", exc)
            raise

    async def search(self, q: Sequence[float], country: str, k: int = 5,
                     ef_search: Optional[int] = None, min_sim: float = 0.3) -> List[Dict[str, Any]]:
        async with self.pool.connection() as conn:
            async with conn.transaction():                 # SET LOCAL lives only inside this transaction
                if ef_search:
                    await conn.execute(f"SET LOCAL hnsw.ef_search = {int(ef_search)}")   # int() prevents injection
                cur = await conn.execute(
                    """SELECT hs_code, body, 1 - (embedding <=> %s::vector) AS similarity
                       FROM headings WHERE country = %s
                       ORDER BY embedding <=> %s::vector LIMIT %s""",
                    (vec(q), country, vec(q), k))
                rows = await cur.fetchall()
        return [r for r in rows if r["similarity"] >= min_sim]   # drop weak matches

    async def close(self) -> None:
        await self.pool.close()                            # release connections

# Token usage: pgvector itself uses 0 LLM tokens. The query embedding (~20 tokens) is the only AI cost.
```

---

## 🟠 FastAPI Integration
```python
import os                                                  # env
from contextlib import asynccontextmanager                 # lifespan
from fastapi import FastAPI, HTTPException                  # FastAPI
from openai import AsyncOpenAI                              # embeddings

oai = AsyncOpenAI()                                         # client
repo = HeadingRepo(os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tariff"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    await repo.start()                                      # open the pool + ensure schema
    yield
    await repo.close()                                      # close on shutdown

app = FastAPI(lifespan=lifespan)                            # app

@app.get("/headings/search")                                # semantic search route
async def search(q: str, country: str = "IN", k: int = 5) -> dict:
    emb = await oai.embeddings.create(model="text-embedding-3-small", input=q)
    try:
        hits = await repo.search(emb.data[0].embedding, country, k, ef_search=80)
    except Exception as exc:                                # connection/SQL failure
        raise HTTPException(503, f"database error: {exc}")
    return {"hits": hits}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-postgres "psycopg[binary]"
from langchain_openai import OpenAIEmbeddings                # embeddings
from langchain_postgres import PGVector                       # official Postgres integration

vs = PGVector(
    embeddings=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="tariff_headings",
    connection="postgresql+psycopg://postgres:postgres@localhost:5432/tariff",   # SQLAlchemy URL (psycopg3)
    use_jsonb=True,                                           # store metadata as JSONB (filterable)
)
vs.add_texts(["Headphones and earphones"], metadatas=[{"country": "IN"}], ids=["8518.30"])
docs = vs.similarity_search("wireless earbuds", k=4, filter={"country": "IN"})   # metadata filter
retriever = vs.as_retriever(search_kwargs={"k": 4})           # plug into LCEL / LangGraph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `ORDER BY 1 - (embedding <=> q) DESC` (index is not used)
✅ Correct: `ORDER BY embedding <=> q` ascending.

```sql
-- Wrong: expression on the left side prevents index use -> sequential scan
SELECT * FROM headings ORDER BY 1 - (embedding <=> '[...]') DESC LIMIT 5;
-- Right
SELECT * FROM headings ORDER BY embedding <=> '[...]' LIMIT 5;
```

❌ Mistake 2: Index operator class does not match the query operator
✅ Correct: `vector_cosine_ops` with `<=>`, `vector_l2_ops` with `<->`, `vector_ip_ops` with `<#>`.

```sql
-- Wrong: index built with vector_l2_ops but queries use <=> -> index ignored
CREATE INDEX ON headings USING hnsw (embedding vector_l2_ops);
-- Right
CREATE INDEX ON headings USING hnsw (embedding vector_cosine_ops);
```

❌ Mistake 3: Building an IVFFlat index on an empty table
✅ Correct: load data first (IVFFlat learns centroids from existing rows), or prefer HNSW.

---

## 🧠 Tricky Interview Question

**Q**: "Your query has `WHERE country = 'IN'` plus `ORDER BY embedding <=> q LIMIT 5`. EXPLAIN shows the HNSW index is used, but you often get fewer than 5 rows. Why?"

**Answer**: With approximate indexes, Postgres first scans the index for the nearest `hnsw.ef_search` candidates (default 40) and THEN applies the WHERE filter. If most candidates are from other countries, fewer than 5 survive. Fixes: raise `hnsw.ef_search` (e.g. 200), use pgvector 0.8+ iterative index scans (`SET hnsw.iterative_scan = relaxed_order`) which keep scanning until enough rows pass the filter, create partial indexes per hot filter value, or partition the table by country so each partition has its own index. Verify with EXPLAIN ANALYZE and recall tests against an exact (index-less) query.

---

## ⚫ Interview Questions + Answers

Q1: What do `<->`, `<=>` and `<#>` mean?
A1: L2 (Euclidean) distance, cosine distance, and negative inner product. Lower is closer for all three; to get cosine similarity use `1 - (a <=> b)`.

Q2: HNSW or IVFFlat in pgvector?
A2: HNSW gives better speed/recall and can be created before data exists but builds slower and uses more memory. IVFFlat builds faster and is smaller but needs data first and lists/probes tuning.

Q3: What is the maximum dimension?
A3: A `vector` column supports up to 16,000 dimensions, but an index on it is limited to 2,000 dimensions; use `halfvec` (up to 4,000 indexed) or dimension reduction for bigger embeddings.

Q4: Why choose pgvector over Pinecone?
A4: One system, transactional consistency, SQL joins/filters, easy backups, lower cost at small to medium scale. Pinecone wins on managed scaling for very large or spiky workloads.

Q5: How would you scale pgvector to 50M vectors?
A5: Use HNSW with tuned `m`/`ef_construction`, give Postgres enough RAM so the index stays hot (`shared_buffers`, OS cache), use halfvec or binary quantisation to shrink memory, partition by tenant or time, add read replicas for queries, build indexes with `maintenance_work_mem` and parallel workers, use iterative scans for filtered queries, and keep an eye on vacuum and bloat. Benchmark recall vs latency; if the working set cannot fit in RAM or QPS is very high, consider a dedicated vector database.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You already run PostgreSQL and need vector search with SQL filters/joins
- Data under ~10M vectors (more with care)
- You want transactional consistency and one backup

❌ Avoid when:
- Very large, high-QPS vector-only workloads needing specialised scaling
- Your team cannot operate or tune Postgres

---

## 📊 Visual Diagram
```
 PostgreSQL
 ┌──────────────────────────────────────────────────────────┐
 │ headings                                                 │
 │ id | hs_code | country | body | embedding vector(1536)   │
 │                                   └── HNSW index         │
 │ duty_rates (JOIN)   customers (JOIN)                     │
 └──────────────────────────────────────────────────────────┘
 query ─embed─► q
 SELECT ... WHERE country='IN' ORDER BY embedding <=> q LIMIT 5
   ├─ index scan (ef_search candidates) ─► filter ─► top 5
   └─ same transaction / same backup as the rest of your data
```

---

## 💰 Cost Impact
- No extra service: reuse your Postgres bill. Storage per vector ~ 4 x dim bytes + ~8 bytes: 1M x 1536 = ~6 GB for data, plus HNSW index of roughly similar size.
- `halfvec` (16-bit floats) halves memory; binary quantisation shrinks it much more with a rerank step.
- Managed Postgres with pgvector (RDS, Cloud SQL, Supabase, Neon) bills as normal database instances; compare against Pinecone serverless read/write units at your query volume.
- Token costs are the same as any RAG system: query embedding ~20 tokens ($0.0000004) and an LLM prompt of top-k chunks (4 x 300 = 1,200 tokens). SQL filters keep that prompt small and relevant.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pgvector | Postgres extension for vectors | Vectors के लिए Postgres extension |
| vector(n) | Column type with n dimensions | n dimensions वाला column type |
| `<=>` | Cosine distance operator | Cosine distance operator |
| HNSW / IVFFlat | ANN index types in pgvector | pgvector के ANN index types |
| ef_search | HNSW query effort | HNSW query का effort |
| probes | IVFFlat clusters searched | IVFFlat में देखे जाने वाले clusters |
| halfvec | 16-bit float vector type | 16-bit float वाला vector type |

---

## ⚡ 3-Line Summary
English: pgvector adds vector columns, distance operators and HNSW/IVFFlat indexes to PostgreSQL, so semantic search becomes SQL with filters, joins and transactions. Match the index operator class to your query operator and tune ef_search or probes. Best when you already run Postgres and have moderate scale.
Hindi: pgvector PostgreSQL में vector columns, distance operators और HNSW/IVFFlat indexes जोड़ता है, इसलिए semantic search filters, joins और transactions वाली SQL बन जाती है। Index operator class को query operator से match करो और ef_search या probes tune करो। जब Postgres पहले से हो और scale मध्यम हो तब सबसे अच्छा।

---

## ➡️ Next Topic
**144. pgvector Setup** — installing the extension, creating tables and indexes, and connecting from Python step by step.
