---

# 152. Hybrid Search Setup
# हिंदी में: Hybrid Search Setup (Keyword + Vector)

---

## 🔵 Simple Definition (English)
Hybrid search runs keyword search (BM25 / full-text) and vector (semantic) search together, then merges the two ranked lists, usually with Reciprocal Rank Fusion (RRF). You get exact-term precision and meaning-based recall in one result.

## 🔵 सरल परिभाषा (Hindi)
Hybrid search में keyword search (BM25 / full-text) और vector (semantic) search साथ चलते हैं, फिर दोनों ranked lists को आमतौर पर Reciprocal Rank Fusion (RRF) से मिलाया जाता है। एक ही result में exact-term precision और meaning-based recall मिलता है।

---

## 🔴 Problem it Solves
Vector search is weak on exact identifiers: "8518.30", "SKU-4471", rare names. Keyword search is weak on paraphrases: "earbuds" vs "in-ear headphones". Each alone misses relevant results; hybrid covers both.

## 🔴 यह क्यों बना? (Hindi)
Vector search exact identifiers पर कमज़ोर है: "8518.30", "SKU-4471", दुर्लभ नाम। Keyword search paraphrases पर कमज़ोर है: "earbuds" बनाम "in-ear headphones"। अकेले दोनों relevant results miss करते हैं; hybrid दोनों को कवर करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Index the same documents twice: full-text (tsvector / BM25) and vector (embedding)
Step 2 → At query time run BOTH searches (parallel), each returns top ~50
Step 3 → Merge by rank: RRF score = sum over lists of 1 / (60 + rank)
Step 4 → Sort by fused score, take top-k (for example 5)
Step 5 → (Optional) rerank the fused top 20 with a cross-encoder
Step 6 → Send final chunks to the LLM
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → वही documents दो तरह से index करो: full-text (tsvector / BM25) और vector (embedding)
Step 2 → Query पर दोनों searches चलाओ (parallel), हर एक top ~50 देती है
Step 3 → Rank से merge करो: RRF score = हर list के लिए 1 / (60 + rank) का जोड़
Step 4 → Fused score से sort करके top-k (जैसे 5) लो
Step 5 → (Optional) fused top 20 को cross-encoder से rerank करो
Step 6 → Final chunks LLM को भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: a user types "HS 8518.30 wireless". The exact code "8518.30" is found by keyword search; "wireless" semantically pulls "Bluetooth headsets". Fusion ranks the right chapter note first. Pure vector search would have buried the code match.

**Amazon-style**: "iPhone 15 Pro 256GB case" needs exact model tokens plus the idea of a protective accessory.

## 🟡 Real Example Hindi mein
**Tariff System**: user "HS 8518.30 wireless" लिखता है। Exact code "8518.30" keyword search पकड़ता है; "wireless" semantic रूप से "Bluetooth headsets" खींचता है। Fusion सही chapter note को ऊपर रखता है। Pure vector search code match को दबा देता।

**Amazon-style**: "iPhone 15 Pro 256GB case" में exact model tokens और सुरक्षा accessory का भाव दोनों चाहिए।

---

## 💻 Code Example — Basic
```python
# Runs offline: RRF fusion of two ranked lists (pure Python)
def rrf(rank_lists: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Fuse several ranked id lists. Higher fused score = better."""
    scores: dict[str, float] = {}  # id -> fused score
    for ranking in rank_lists:  # each retriever's results
        for pos, doc_id in enumerate(ranking, start=1):  # rank starts at 1
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + pos)  # add reciprocal rank
    return sorted(scores.items(), key=lambda t: t[1], reverse=True)  # best first


keyword_hits = ["8518.30", "8517.13", "8528.72"]  # BM25 order
vector_hits = ["8518.21", "8518.30", "8517.62"]  # semantic order
for doc_id, score in rrf([keyword_hits, vector_hits])[:3]:
    print(doc_id, round(score, 4))  # 8518.30 appears in both lists, so it wins
```

## 💻 Code Example — Advanced
```python
# Production: hybrid in ONE Postgres (tsvector + pgvector), async, parallel, RRF in SQL
import asyncio
import logging
from psycopg_pool import AsyncConnectionPool

log = logging.getLogger("hybrid")

SETUP_SQL = [
    # generated column keeps the full-text vector in sync automatically
    "ALTER TABLE tariff_codes ADD COLUMN IF NOT EXISTS tsv tsvector "
    "GENERATED ALWAYS AS (to_tsvector('english', description || ' ' || hs_code)) STORED",
    "CREATE INDEX IF NOT EXISTS ix_tariff_tsv ON tariff_codes USING gin (tsv)",  # keyword index
]

HYBRID_SQL = """
WITH semantic AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> %(vec)s::vector) AS rnk
    FROM tariff_codes WHERE country = %(country)s
    ORDER BY embedding <=> %(vec)s::vector LIMIT 50
), keyword AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(tsv, q) DESC) AS rnk
    FROM tariff_codes, websearch_to_tsquery('english', %(text)s) q
    WHERE tsv @@ q AND country = %(country)s
    ORDER BY ts_rank_cd(tsv, q) DESC LIMIT 50
)
SELECT t.hs_code, t.description,
       COALESCE(1.0 / (60 + s.rnk), 0) + COALESCE(1.0 / (60 + k.rnk), 0) AS score
FROM semantic s FULL OUTER JOIN keyword k USING (id)
JOIN tariff_codes t ON t.id = COALESCE(s.id, k.id)
ORDER BY score DESC LIMIT %(k)s
"""


async def setup(pool: AsyncConnectionPool) -> None:
    async with pool.connection() as conn:
        for stmt in SETUP_SQL:
            await conn.execute(stmt)  # idempotent DDL


async def hybrid_search(pool: AsyncConnectionPool, text: str, vec: list[float],
                        country: str = "IN", k: int = 5) -> list[dict]:
    lit = "[" + ",".join(map(str, vec)) + "]"
    try:
        async with pool.connection() as conn:
            cur = await conn.execute(HYBRID_SQL, {"vec": lit, "text": text, "country": country, "k": k})
            rows = await cur.fetchall()
    except Exception:
        log.exception("hybrid query failed")
        raise
    return [{"hs_code": h, "description": d, "score": float(s)} for h, d, s in rows]
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Query, Request
from openai import AsyncOpenAI

app = FastAPI()
oa = AsyncOpenAI()


@app.get("/tariff/hybrid")
async def hybrid(request: Request, q: str = Query(min_length=2), k: int = Query(5, le=20)) -> dict:
    emb = (await oa.embeddings.create(model="text-embedding-3-small", input=q)).data[0].embedding
    results = await hybrid_search(request.app.state.pool, q, emb, k=k)  # from Advanced example
    return {"query": q, "results": results}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain langchain-community rank_bm25
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

bm25 = BM25Retriever.from_texts(["Headphones 8518.30", "Smartphones 8517.13"], k=5)  # keyword side
vector = vs.as_retriever(search_kwargs={"k": 5})  # vs = any vector store from earlier topics

hybrid = EnsembleRetriever(retrievers=[bm25, vector], weights=[0.4, 0.6])  # uses weighted RRF internally
docs = hybrid.invoke("HS 8518.30 wireless")
# hybrid is a Runnable: use it as the retrieve node in a LangGraph graph
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Adding raw scores from BM25 and cosine
```python
# Wrong: different scales
final = bm25_score + cosine_score
# Right: fuse by rank (RRF) or normalise first
final = 1 / (60 + bm25_rank) + 1 / (60 + vec_rank)
```

❌ Mistake 2: Using different text fields for the two searches
```python
# Wrong: keyword index on title only, embedding on full body -> inconsistent results
# Right: index the same chunk text in both, and keep ids identical so fusion can join them
```

---

## 🧠 Tricky Interview Question

**Q**: "Hybrid search gave worse results than pure vector search on your evaluation. What could be wrong?"

**Answer**: Possible causes: (1) the keyword side uses a poor analyzer (stemming or language mismatch, for example Hindi text with an English config), (2) fusion weights over-favour noisy keyword hits, (3) stop-word-heavy natural-language queries produce garbage BM25 matches, (4) the keyword and vector indexes are out of sync, (5) the evaluation set contains only paraphrase queries where vectors already excel. Diagnose by evaluating each retriever separately (recall@k), then the fusion; tune weights or use query routing: identifiers go to keyword, long questions go to vector-heavy.

---

## ⚫ Interview Questions + Answers

Q1: What is hybrid search?
A1: Combining keyword and vector retrieval and merging their results.

Q2: What is RRF?
A2: Reciprocal Rank Fusion: each document gets the sum of 1/(k + rank) across result lists; k is usually 60. It needs no score normalisation.

Q3: Why is BM25 still useful with embeddings?
A3: Exact terms, codes, names and rare words match precisely; embeddings can blur them.

Q4: Where can you run hybrid search?
A4: Postgres (tsvector + pgvector), Elasticsearch/OpenSearch, Weaviate, Qdrant (sparse + dense), Pinecone (sparse-dense), or in application code with LangChain's EnsembleRetriever.

Q5: How would you evaluate and tune hybrid search?
A5: Build 100-300 labelled queries with relevant ids, compute recall@k and MRR for keyword-only, vector-only and hybrid, sweep fusion weight and `k`, segment by query type (identifier vs question), and add a reranker if the top-20 contains the answer but the top-5 does not.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Queries mix identifiers/jargon and natural language
- Domain has codes, SKUs, legal citations

❌ Avoid when:
- Corpus is tiny and queries are purely conversational (vector alone is enough)
- Latency budget cannot afford two retrievals (then pick one and add a reranker later)

---

## 📊 Visual Diagram
```
                    query "HS 8518.30 wireless"
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
     Keyword (BM25/GIN)          Vector (HNSW)
     1. 8518.30                  1. 8518.21
     2. 8517.13                  2. 8518.30
     3. 8528.72                  3. 8517.62
            └─────────────┬─────────────┘
                          ▼
               RRF: 1/(60+r1) + 1/(60+r2)
                          ▼
            8518.30 > 8518.21 > 8517.13 ...
```

---

## 💰 Cost Impact
- One query embedding (a few tokens) is the only extra token cost; keyword search costs only CPU.
- Better precision means you can send fewer chunks (top 3-5), which cuts LLM input tokens. Example: moving from k=8 to k=4 at 300 tokens per chunk saves about 1,200 tokens per request.
- A reranker adds a model call; use it only on the fused top 20, and cache results for popular queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BM25 | Keyword relevance scoring | Keyword relevance score |
| tsvector | Postgres full-text document type | Postgres full-text type |
| RRF | Rank-based fusion | Rank से मिलाना |
| Sparse vector | Mostly-zero keyword-style vector | अधिकतर शून्य वाला vector |
| Dense vector | Embedding with all values filled | पूरा भरा embedding |
| Reranker | Model reordering top results | Top results दोबारा क्रमबद्ध करने वाला model |

---

## ⚡ 3-Line Summary
English: Hybrid search merges keyword and vector rankings, typically with RRF. It fixes the weaknesses of each method alone. Index the same text in both and evaluate with labelled queries.
Hindi: Hybrid search keyword और vector rankings को आमतौर पर RRF से मिलाता है। यह दोनों तरीकों की अलग-अलग कमज़ोरियाँ दूर करता है। दोनों में एक ही text index करो और labelled queries से evaluate करो।

---

## ➡️ Next Topic
**153. Vector DB Performance** — measuring latency, recall and throughput, and fixing bottlenecks.
