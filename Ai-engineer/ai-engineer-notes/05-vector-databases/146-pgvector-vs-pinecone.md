---

# 146. pgvector vs Pinecone
# हिंदी में: pgvector बनाम Pinecone

---

## 🔵 Simple Definition (English)
pgvector is a vector extension inside your own Postgres (you operate it). Pinecone is a fully managed, vector-only cloud service (they operate it). The choice is control and low cost versus zero operations and easy scale.

## 🔵 सरल परिभाषा (Hindi)
pgvector आपके अपने Postgres के अंदर vector extension है (operate आप करते हैं)। Pinecone पूरी तरह managed, सिर्फ vector वाली cloud service है (operate वो करते हैं)। चुनाव है: control और कम cost बनाम zero operations और आसान scale।

---

## 🔴 Problem it Solves
Teams ask "do we need a dedicated vector DB?" Picking wrongly means either paying for a service you do not need, or running a struggling Postgres at tens of millions of vectors. A clear comparison avoids both.

## 🔴 यह क्यों बना? (Hindi)
Teams पूछती हैं "क्या dedicated vector DB चाहिए?" गलत चुनाव का मतलब या तो बेकार service का पैसा, या करोड़ों vectors पर परेशान Postgres। साफ तुलना दोनों से बचाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Estimate vector count (now and in 12 months) and dimension
Step 2 → Estimate peak QPS and the latency target (p95)
Step 3 → List filter/metadata/transaction needs (joins? ACID?)
Step 4 → Check team: do you have someone to run Postgres tuning/backups?
Step 5 → Prototype both with the same 100K vectors, measure recall, latency, cost
Step 6 → Decide, and hide the choice behind a VectorStore interface to keep migration cheap
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Vectors की संख्या (अभी और 12 महीने बाद) और dimension अनुमानित करो
Step 2 → Peak QPS और latency target (p95) निकालो
Step 3 → Filter/metadata/transaction की ज़रूरतें लिखो (joins? ACID?)
Step 4 → देखो: Postgres tuning/backup संभालने वाला कोई है?
Step 5 → एक ही 100K vectors पर दोनों prototype करो: recall, latency, cost नापो
Step 6 → तय करो, और चुनाव को VectorStore interface के पीछे रखो ताकि migration सस्ता रहे
```

---

## 🟡 Real World Example
**Tariff Classification System**: 20K HS descriptions plus 2M historical classified items, all with relational audit tables. 2M vectors at 1536 dims is about 12 GB: comfortable in Postgres, and joins with audit tables are valuable. pgvector wins.

**Amazon-style catalog**: 300M product vectors, spiky traffic, a tiny platform team. A managed service (Pinecone) wins because scaling and index maintenance are handled for you.

## 🟡 Real Example Hindi mein
**Tariff System**: 20K HS descriptions और 2M पुराने classified items, सब relational audit tables के साथ। 2M vectors (1536 dims) लगभग 12 GB, Postgres में आराम से, और audit tables से join फायदेमंद। pgvector जीतता है।

**Amazon-style catalog**: 30 करोड़ product vectors, spiky traffic, छोटी platform team। Managed service (Pinecone) जीतती है क्योंकि scaling और index maintenance वही संभालते हैं।

---

## 💻 Code Example — Basic
```python
# Same interface, two backends. Pure-python skeleton you can run (no DB needed).
from typing import Protocol  # structural typing


class VectorStore(Protocol):
    """What the app needs; backends hide the details."""

    def upsert(self, id: str, vec: list[float], meta: dict) -> None: ...  # write
    def query(self, vec: list[float], k: int) -> list[tuple[str, float]]: ...  # read


class InMemoryStore:
    """Tiny stand-in so the example runs offline."""

    def __init__(self) -> None:
        self.rows: dict[str, tuple[list[float], dict]] = {}  # id -> (vector, metadata)

    def upsert(self, id: str, vec: list[float], meta: dict) -> None:
        self.rows[id] = (vec, meta)  # insert or replace

    def query(self, vec: list[float], k: int) -> list[tuple[str, float]]:
        def cos(a: list[float], b: list[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b))  # dot product
            na = sum(x * x for x in a) ** 0.5  # norm a
            nb = sum(y * y for y in b) ** 0.5  # norm b
            return dot / (na * nb) if na and nb else 0.0  # cosine similarity
        scored = [(i, cos(vec, v)) for i, (v, _) in self.rows.items()]  # score all rows
        return sorted(scored, key=lambda t: t[1], reverse=True)[:k]  # top-k


store: VectorStore = InMemoryStore()  # swap for PgVectorStore / PineconeStore
store.upsert("8518.30", [0.9, 0.1], {"d": "headphones"})
store.upsert("8517.13", [0.1, 0.9], {"d": "smartphones"})
print(store.query([0.8, 0.2], 1))  # [('8518.30', 0.99...)]
```

## 💻 Code Example — Advanced
```python
# Two real adapters behind the same async interface (syntax-level reference).
# pip install pinecone "psycopg[binary]" psycopg_pool
import asyncio
from typing import Any

from pinecone import Pinecone  # pinecone>=5 client (sync)
from psycopg_pool import AsyncConnectionPool


class PineconeStore:
    def __init__(self, api_key: str, index_name: str) -> None:
        pc = Pinecone(api_key=api_key)  # client
        self.index = pc.Index(index_name)  # existing index (dimension fixed at creation)

    async def upsert(self, id: str, vec: list[float], meta: dict[str, Any]) -> None:
        # Pinecone client is sync: run in a thread so the event loop is not blocked
        await asyncio.to_thread(self.index.upsert, vectors=[{"id": id, "values": vec, "metadata": meta}])

    async def query(self, vec: list[float], k: int, flt: dict | None = None) -> list[tuple[str, float]]:
        res = await asyncio.to_thread(
            self.index.query, vector=vec, top_k=k, filter=flt, include_metadata=True
        )
        return [(m["id"], m["score"]) for m in res["matches"]]  # (id, similarity)


class PgStore:
    def __init__(self, pool: AsyncConnectionPool) -> None:
        self.pool = pool  # shared pool

    async def upsert(self, id: str, vec: list[float], meta: dict[str, Any]) -> None:
        lit = "[" + ",".join(map(str, vec)) + "]"  # pgvector literal
        async with self.pool.connection() as conn:
            await conn.execute(
                "INSERT INTO tariff_codes (hs_code, description, country, embedding) "
                "VALUES (%s, %s, %s, %s::vector) ON CONFLICT DO NOTHING",
                (id, meta.get("d", ""), meta.get("country", "IN"), lit),
            )

    async def query(self, vec: list[float], k: int, flt: dict | None = None) -> list[tuple[str, float]]:
        lit = "[" + ",".join(map(str, vec)) + "]"
        country = (flt or {}).get("country", "IN")  # same filter semantics
        async with self.pool.connection() as conn:
            cur = await conn.execute(
                "SELECT hs_code, 1 - (embedding <=> %s::vector) FROM tariff_codes "
                "WHERE country = %s ORDER BY embedding <=> %s::vector LIMIT %s",
                (lit, country, lit, k),
            )
            return [(r[0], float(r[1])) for r in await cur.fetchall()]
```

---

## 🟠 FastAPI Integration
```python
import os
from fastapi import FastAPI

app = FastAPI()
BACKEND = os.getenv("VECTOR_BACKEND", "pg")  # config switch, no code change to migrate


def make_store():
    if BACKEND == "pinecone":
        return PineconeStore(os.environ["PINECONE_API_KEY"], "tariff")  # from Advanced example
    raise RuntimeError("build PgStore with a pool in lifespan")  # pool needs the event loop


@app.get("/backend")
async def backend() -> dict[str, str]:
    return {"backend": BACKEND}  # useful for debugging environments
```

---

## 🔗 LangChain / LangGraph Connection
LangChain gives the same `VectorStore` API for both, so swapping is a one-line change.

```python
from langchain_openai import OpenAIEmbeddings
emb = OpenAIEmbeddings(model="text-embedding-3-small")

# Option A: pgvector
from langchain_postgres import PGVector
vs = PGVector(embeddings=emb, collection_name="tariff", connection="postgresql+psycopg://postgres:pw@localhost/postgres")

# Option B: Pinecone (pip install langchain-pinecone)
# from langchain_pinecone import PineconeVectorStore
# vs = PineconeVectorStore(index_name="tariff", embedding=emb)

retriever = vs.as_retriever(search_kwargs={"k": 5})  # identical downstream code
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Choosing Pinecone "because everyone does" for 100K vectors
```python
# Wrong: paying a monthly bill + extra network hop + data sync for a tiny dataset
# Right: start with pgvector in the Postgres you already run; migrate only when metrics demand
```

❌ Mistake 2: Hard-coding the backend into business logic
```python
# Wrong
index.query(vector=v, top_k=5)          # Pinecone call scattered across 40 files
# Right
results = await store.query(v, 5)       # one interface, one adapter per backend
```

---

## 🧠 Tricky Interview Question

**Q**: "Pinecone benchmarks show lower latency than pgvector, yet your pgvector service is faster end to end. How?"

**Answer**: Benchmarks measure the vector call only. In a real request, Pinecone adds a network hop to another cloud/region and then you still need a second query to Postgres for the metadata/rows (or duplicate data). pgvector returns vectors and relational data in one local query with a transaction. For modest data sizes the removed hop beats raw ANN speed. At very large scale or high QPS, the ANN engine itself becomes the bottleneck and the result flips.

---

## ⚫ Interview Questions + Answers

Q1: What is the main difference?
A1: pgvector is an extension you self-operate inside Postgres; Pinecone is a managed vector-only service.

Q2: Name one advantage of pgvector.
A2: Joins, ACID transactions and one system for all data, with no extra service cost.

Q3: Name one advantage of Pinecone.
A3: Managed scaling, no index tuning or backups to run, strong performance at very large scale.

Q4: How do metadata filters differ?
A4: In Pinecone, metadata filters are native in the query. In pgvector, they are SQL `WHERE`, which is more expressive but with HNSW is applied after candidates unless iterative scan or partial indexes are used.

Q5: How would you migrate from pgvector to Pinecone with no downtime?
A5: Put a VectorStore interface in place, backfill Pinecone from Postgres in batches (`COPY`/cursor, upsert 100 per batch), dual-write new data, shadow-read from both and compare top-k overlap, then switch reads by feature flag, and finally remove the old path after a stable period.

---

## 🔷 When to Use + When Not to Use
✅ pgvector when:
- Under about 10-50M vectors, existing Postgres, relational joins needed

✅ Pinecone when:
- Very large or fast-growing data, tiny ops team, need managed multi-region

❌ Avoid pgvector when:
- Postgres is already CPU/RAM-bound or QPS is extreme

❌ Avoid Pinecone when:
- Data must stay inside your VPC or budget is tight at small scale

---

## 📊 Visual Diagram
```
        pgvector                         Pinecone
 ┌────────────────────┐          ┌──────────────────────┐
 │ App ─► Postgres     │          │ App ─► Pinecone API  │
 │  vectors + rows +   │          │  vectors + metadata  │
 │  transactions       │          │ App ─► Postgres (rows)│
 │  you run it         │          │  they run the vectors│
 └────────────────────┘          └──────────────────────┘
 1 system, 1 query                2 systems, 2 queries
```

---

## 💰 Cost Impact
- No token difference: both use the same embedding model, so embedding cost is identical.
- Infra: pgvector costs extra RAM/storage on a DB you already pay for. Managed services bill by storage, read/write units or pods. Check current pricing for your volume.
- Optimisation: reduce dimensions (`dimensions=512`), store only needed metadata, delete stale vectors, and keep the retrieval k small so the LLM prompt (the bigger cost) stays small.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Managed service | Vendor runs infrastructure | Vendor संभालता है |
| Self-hosted | You run it | आप खुद चलाते हैं |
| ACID | Reliable transactions | भरोसेमंद transactions |
| Adapter | Class wrapping a backend | Backend का wrapper |
| Vendor lock-in | Hard to switch provider | Provider बदलना मुश्किल |

---

## ⚡ 3-Line Summary
English: pgvector is cheap and simple when you already use Postgres; Pinecone removes operations at huge scale. Decide with real vector counts, QPS and team size. Hide the backend behind an interface so you can switch.
Hindi: Postgres पहले से है तो pgvector सस्ता और सरल है; बहुत बड़े scale पर Pinecone operations हटा देता है। असली vector count, QPS और team size से तय करो। Backend को interface के पीछे रखो ताकि बदल सको।

---

## ➡️ Next Topic
**147. Redis as Vector DB** — in-memory vector search for very low latency and caching.
