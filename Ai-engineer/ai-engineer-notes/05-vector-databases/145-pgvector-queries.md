---

# 145. pgvector Queries
# हिंदी में: pgvector Queries (Similarity Search SQL)

---

## 🔵 Simple Definition (English)
pgvector queries use SQL distance operators (`<->`, `<=>`, `<#>`) in `ORDER BY` to return the nearest rows to a query vector. You can combine them with `WHERE` filters, joins and `LIMIT` like any other SQL.

## 🔵 सरल परिभाषा (Hindi)
pgvector queries में SQL distance operators (`<->`, `<=>`, `<#>`) को `ORDER BY` में use करते हैं, जिससे query vector के सबसे नज़दीकी rows मिलते हैं। इन्हें `WHERE`, join और `LIMIT` के साथ normal SQL की तरह मिला सकते हैं।

---

## 🔴 Problem it Solves
Pure keyword SQL (`LIKE '%earbuds%'`) misses "wireless headphones". Pure vector search ignores hard rules like country or year. pgvector lets one query do both: semantic ranking plus exact filters.

## 🔴 यह क्यों बना? (Hindi)
Keyword SQL ("LIKE") "wireless headphones" को miss कर देता है। Pure vector search country या year जैसे hard rules ignore करता है। pgvector एक ही query में semantic ranking और exact filters दोनों देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Embed the user question with the SAME model used for ingestion
Step 2 → Send the vector as a parameter: embedding <=> %s::vector
Step 3 → Postgres planner picks the HNSW/IVFFlat index (if the operator matches)
Step 4 → Index returns approximate nearest candidates (ef_search of them)
Step 5 → WHERE filters are applied (post-filter by default) and LIMIT k trims
Step 6 → Convert distance to similarity (1 - cosine_distance) and return rows
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Question को ingestion वाले ही model से embed करो
Step 2 → Vector को parameter की तरह भेजो: embedding <=> %s::vector
Step 3 → Planner operator match होने पर HNSW/IVFFlat index चुनता है
Step 4 → Index approximate nearest candidates (ef_search जितने) देता है
Step 5 → WHERE filter लगता है (default में post-filter) और LIMIT k काटता है
Step 6 → Distance को similarity (1 - cosine_distance) में बदलकर rows लौटाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: "men's cotton t-shirt" is embedded and matched against `tariff_codes` with `WHERE country = 'IN'`. The top 5 candidates go to an LLM that picks the final HS code (6109.10). Candidates with similarity below 0.35 are dropped so the LLM is not fed noise.

**Amazon-style search**: "running shoes under 3000" runs vector similarity with `price < 3000 AND in_stock`.

## 🟡 Real Example Hindi mein
**Tariff System**: "men's cotton t-shirt" को embed करके `country = 'IN'` filter के साथ `tariff_codes` में match करते हैं। Top 5 candidates LLM को जाते हैं जो final HS code (6109.10) चुनता है। 0.35 से कम similarity वाले candidates हटा देते हैं।

**Amazon-style search**: "3000 से सस्ते running shoes" में vector similarity के साथ `price < 3000 AND in_stock` चलता है।

---

## 💻 Code Example — Basic
```python
# pip install "psycopg[binary]"
import psycopg  # sync driver

DSN = "postgresql://postgres:pw@localhost:5432/postgres"  # local DB


def lit(vec: list[float]) -> str:
    """List -> pgvector literal."""
    return "[" + ",".join(map(str, vec)) + "]"  # '[1,2,3]'


def search(query_vec: list[float], country: str, k: int = 5) -> list[tuple]:
    """Top-k cosine search with a metadata filter."""
    sql = """
        SELECT hs_code, description,
               1 - (embedding <=> %(q)s::vector) AS similarity   -- cosine distance -> similarity
        FROM tariff_demo
        WHERE country = %(c)s                                    -- exact filter
        ORDER BY embedding <=> %(q)s::vector                     -- nearest first (uses the index)
        LIMIT %(k)s
    """
    with psycopg.connect(DSN) as conn:  # open and close connection safely
        return conn.execute(sql, {"q": lit(query_vec), "c": country, "k": k}).fetchall()


# The three operators side by side (same ORDER BY idea):
#   embedding <->  q   -> L2 distance
#   embedding <=>  q   -> cosine distance
#   embedding <#>  q   -> NEGATIVE inner product (smaller = more similar)
if __name__ == "__main__":
    print(search([0.9, 0.1, 0.0], "IN"))  # needs table with a country column
```

## 💻 Code Example — Advanced
```python
# Production: async, threshold, per-query ef_search, error handling, typed result
import asyncio
import logging
from dataclasses import dataclass

from openai import AsyncOpenAI
from psycopg_pool import AsyncConnectionPool

log = logging.getLogger("pgvector_query")  # logger


@dataclass(frozen=True)
class Hit:
    hs_code: str  # tariff code
    description: str  # text
    score: float  # cosine similarity 0..1


class Searcher:
    def __init__(self, pool: AsyncConnectionPool, client: AsyncOpenAI) -> None:
        self.pool = pool  # shared pool
        self.client = client  # shared OpenAI client

    async def search(self, text: str, country: str = "IN", k: int = 5,
                     min_score: float = 0.35, ef_search: int = 80) -> list[Hit]:
        if not text.strip():  # guard against empty input
            return []
        try:
            emb = await self.client.embeddings.create(model="text-embedding-3-small", input=text)
        except Exception:
            log.exception("embedding call failed")  # never hide failures silently
            raise
        vec = "[" + ",".join(map(str, emb.data[0].embedding)) + "]"  # literal
        async with self.pool.connection() as conn:  # borrow a connection
            async with conn.transaction():  # SET LOCAL only lives inside a transaction
                await conn.execute(f"SET LOCAL hnsw.ef_search = {int(ef_search)}")  # recall vs speed knob
                cur = await conn.execute(
                    """SELECT hs_code, description, 1 - (embedding <=> %s::vector) AS score
                       FROM tariff_codes
                       WHERE country = %s
                       ORDER BY embedding <=> %s::vector
                       LIMIT %s""",
                    (vec, country, vec, k),
                )
                rows = await cur.fetchall()  # list of tuples
        return [Hit(h, d, float(s)) for h, d, s in rows if s >= min_score]  # drop weak matches


async def demo() -> None:
    pool = AsyncConnectionPool("postgresql://postgres:pw@localhost:5432/postgres", open=False)
    await pool.open()
    s = Searcher(pool, AsyncOpenAI())
    print(await s.search("wireless bluetooth earbuds"))
    await pool.close()


if __name__ == "__main__":
    asyncio.run(demo())  # needs DB + OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
```python
from fastapi import Depends, FastAPI, Query, Request

app = FastAPI()  # lifespan creating pool + client omitted, see topic 144


def get_searcher(request: Request) -> "Searcher":
    return request.app.state.searcher  # built at startup


@app.get("/tariff/search")
async def tariff_search(
    q: str = Query(min_length=2, max_length=500),  # validate input
    country: str = "IN",
    k: int = Query(5, ge=1, le=20),  # cap k to protect the DB
    searcher: "Searcher" = Depends(get_searcher),
) -> dict:
    hits = await searcher.search(q, country=country, k=k)
    return {"query": q, "results": [h.__dict__ for h in hits]}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.runnables import RunnableLambda

# store = PGVector(...) from topic 144
retriever = store.as_retriever(
    search_type="similarity_score_threshold",  # filter by score
    search_kwargs={"k": 5, "score_threshold": 0.35, "filter": {"country": "IN"}},  # metadata filter
)

# LangGraph node: reads state["question"], writes state["docs"]
def retrieve_node(state: dict) -> dict:
    return {"docs": retriever.invoke(state["question"])}

chain = RunnableLambda(retrieve_node)  # usable in a graph or LCEL pipe
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Ordering by similarity expression instead of distance
```sql
-- Wrong: index cannot be used, full scan
SELECT * FROM t ORDER BY 1 - (embedding <=> q) DESC LIMIT 5;
-- Right: order by the raw operator ascending, compute similarity only in SELECT
SELECT *, 1 - (embedding <=> q) AS sim FROM t ORDER BY embedding <=> q LIMIT 5;
```

❌ Mistake 2: Strict filter returns fewer than k rows with HNSW
```sql
-- Wrong: WHERE country='IN' is applied AFTER the index returns ~40 candidates (ef_search),
-- so a rare country may return 0 rows.
-- Right: raise hnsw.ef_search, use pgvector 0.8 iterative scan
--   SET hnsw.iterative_scan = relaxed_order;
-- or partition / use a partial index per country
```

---

## 🧠 Tricky Interview Question

**Q**: "Your query asks `LIMIT 10` with a selective filter but returns only 3 rows, even though 500 matching rows exist. Is the data corrupt?"

**Answer**: No. ANN indexes find the nearest `ef_search` candidates first (default 40), then the filter removes non-matching ones. If few candidates match, you get fewer than k rows. Fixes: increase `hnsw.ef_search`, enable iterative index scans (pgvector 0.8+), build partial indexes (`WHERE country='IN'`), or partition the table. Exact scans (no index) always return correct counts but are slow.

---

## ⚫ Interview Questions + Answers

Q1: Which operator is cosine distance?
A1: `<=>`. `<->` is L2 and `<#>` is negative inner product.

Q2: How do you turn cosine distance into similarity?
A2: `1 - (embedding <=> q)`. Keep `ORDER BY embedding <=> q` so the index is usable.

Q3: What does `hnsw.ef_search` control?
A3: Candidate list size during search. Higher means better recall but slower queries. Set per transaction with `SET LOCAL`.

Q4: How do you verify an index is used?
A4: `EXPLAIN ANALYZE` the query and look for `Index Scan using ... hnsw`. A `Seq Scan` means the operator or LIMIT/ORDER BY shape prevents index use.

Q5: How do you measure recall of the ANN index?
A5: Run the same queries with the index disabled (`SET enable_indexscan = off`) for exact results, compare the top-k ids with ANN results, and compute overlap. Tune `ef_search`/`m` until recall is acceptable (for example above 0.95).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need semantic search plus relational filters
- Result lists are small (top 5-50)

❌ Avoid when:
- Filters are extremely selective and you rely on a plain HNSW index without iterative scan
- You need exact results for compliance (use exact scan or a rule engine)

---

## 📊 Visual Diagram
```
 SELECT ... WHERE country='IN'
 ORDER BY embedding <=> q LIMIT 5
          │
          ▼
   HNSW graph walk ──► ef_search candidates (e.g. 80)
          │
          ▼
   filter country='IN' ──► sort by distance ──► LIMIT 5
          │
          ▼
   [(8518.30, 0.82), (8518.21, 0.77), ...]
```

---

## 💰 Cost Impact
- Each search costs one query embedding (tiny, for example 10-30 tokens) plus DB CPU. Higher `ef_search` costs CPU, not tokens.
- Returning top-k chunks to an LLM dominates cost: 5 chunks x 300 tokens = 1,500 input tokens per question. A score threshold and small k cut LLM spend directly.
- Cache embeddings of frequent queries to skip repeated embedding calls.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cosine distance | 1 - cosine similarity | Cosine की दूरी |
| ef_search | Search-time candidate list size | Search में candidates की संख्या |
| Post-filtering | Filter after ANN candidates | ANN के बाद filter |
| Iterative scan | Keep scanning until k rows pass the filter | Filter पास होने तक scan |
| Recall | Share of true neighbours found | सही neighbours मिलने का अनुपात |

---

## ⚡ 3-Line Summary
English: Use `ORDER BY embedding <=> q LIMIT k` with the operator that matches your index. Filters are applied after ANN candidates, so tune `ef_search` or use iterative scans. Convert distance to similarity only in SELECT.
Hindi: `ORDER BY embedding <=> q LIMIT k` index वाले operator के साथ use करो। Filters ANN candidates के बाद लगते हैं, इसलिए `ef_search` tune करो या iterative scan use करो। Similarity सिर्फ SELECT में निकालो।

---

## ➡️ Next Topic
**146. pgvector vs Pinecone** — when Postgres is enough and when a managed vector DB wins.
