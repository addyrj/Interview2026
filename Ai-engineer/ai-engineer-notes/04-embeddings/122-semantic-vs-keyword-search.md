---

# 122. Semantic vs Keyword Search — Complete Guide
# हिंदी में: Semantic बनाम Keyword Search — पूरी Guide

---

## 🔵 Simple Definition (English)
Keyword search (BM25, SQL LIKE, full-text) matches the exact words in the query. Semantic search matches meaning using embeddings. Keyword is precise for IDs and rare terms; semantic is strong for paraphrases and synonyms. **Hybrid search** combines both for the best results.

## 🔵 सरल परिभाषा (Hindi)
Keyword search (BM25, SQL LIKE, full-text) query के exact शब्द match करता है। Semantic search embeddings से meaning match करता है। Keyword IDs और rare terms के लिए precise है; semantic paraphrases और synonyms के लिए strong। **Hybrid search** दोनों को मिलाकर सबसे अच्छे results देता है।

---

## 🔴 Problem it Solves
Each method alone has blind spots. Keyword misses "earbuds" when the document says "earphones". Semantic misses "HS 8518.30", "iPhone 15 Pro Max A2849" or negations, and can return plausible but wrong topics. Real systems need both exact and fuzzy matching.

## 🔴 यह क्यों बना? (Hindi)
हर method के अपने blind spots हैं। Document में "earphones" हो तो keyword "earbuds" miss करता है। Semantic "HS 8518.30", "iPhone 15 Pro Max A2849" या negations miss करता है और plausible पर गलत topics दे सकता है। Real systems को exact और fuzzy दोनों matching चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Keyword (BM25): tokenise, score by term frequency x rarity (IDF), length-normalised
Step 2 → Semantic: embed query, cosine against document vectors
Step 3 → Hybrid: run both searches in parallel (top 20-50 each)
Step 4 → Fuse the ranked lists:
          RRF: score(d) = sum over lists of 1 / (k + rank_in_list), k ~ 60
          or weighted sum of normalised scores: alpha*semantic + (1-alpha)*keyword
Step 5 → Sort by fused score; take top-k
Step 6 → Optional: cross-encoder rerank
Step 7 → Tune alpha / k on a labelled set (topic 120)
Step 8 → Route: ID-like queries -> keyword boost; natural language -> semantic boost
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Keyword (BM25): tokenise, term frequency x rarity (IDF) से score
Step 2 → Semantic: query embed, document vectors से cosine
Step 3 → Hybrid: दोनों search parallel चलाओ (हर एक के top 20-50)
Step 4 → Ranked lists मिलाओ:
          RRF: score(d) = हर list में 1 / (k + rank), k ~ 60
          या normalised scores का weighted sum: alpha*semantic + (1-alpha)*keyword
Step 5 → Fused score से sort करके top-k लो
Step 6 → चाहें तो cross-encoder rerank
Step 7 → Labelled set पर alpha / k tune करो (topic 120)
Step 8 → Routing: ID जैसी queries में keyword boost; natural language में semantic boost
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "8518.30 earbuds duty": the code "8518.30" is a rare token, so BM25 pinpoints exact tariff lines; "earbuds" is matched semantically to "earphones". Hybrid returns the right line at rank 1, while semantic-only ranked it 6th and keyword-only missed the synonym entirely.

**Amazon-style**: Model numbers (A2849) need keyword; "phone with great camera" needs semantic.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "8518.30 earbuds duty": "8518.30" rare token है, इसलिए BM25 exact tariff line पकड़ता है; "earbuds" semantic रूप से "earphones" से match होता है। Hybrid सही line rank 1 पर देता है, जबकि semantic-only ने उसे 6वें और keyword-only ने synonym पूरी तरह miss किया।

**Amazon-style**: Model numbers (A2849) के लिए keyword; "phone with great camera" के लिए semantic।

---

## 💻 Code Example — Basic
```python
# BM25-like keyword scoring + toy semantic scoring + Reciprocal Rank Fusion (runs offline)
import math
from collections import Counter

DOCS = [
    "8518.30 Headphones and earphones",
    "0901.11 Coffee, not roasted",
    "8517.13 Smartphones",
    "8504.40 Static converters chargers",
]


def tokens(t: str) -> list[str]:
    return t.lower().replace(",", " ").split()


def bm25(query: str, docs: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """Minimal BM25 over a tiny corpus."""
    toks = [tokens(d) for d in docs]
    avg = sum(map(len, toks)) / len(toks)
    df = Counter(w for t in toks for w in set(t))        # document frequency
    n = len(docs)
    scores = []
    for t in toks:
        tf = Counter(t)
        s = 0.0
        for w in tokens(query):
            if w not in tf:
                continue
            idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
            s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / avg))
        scores.append(s)
    return scores


SYN = {"earbuds": "earphones", "phone": "smartphones"}   # stand-in for embedding similarity


def semantic(query: str, docs: list[str]) -> list[float]:
    q = {SYN.get(w, w) for w in tokens(query)}
    return [len(q & set(tokens(d))) / (len(q) or 1) for d in docs]   # overlap after synonym mapping


def rrf(rank_lists: list[list[int]], k: int = 60) -> list[int]:
    """Fuse ranked lists of doc indexes."""
    score: dict[int, float] = {}
    for lst in rank_lists:
        for r, d in enumerate(lst, start=1):
            score[d] = score.get(d, 0.0) + 1.0 / (k + r)
    return sorted(score, key=lambda d: -score[d])


def ranking(scores: list[float]) -> list[int]:
    return sorted(range(len(scores)), key=lambda i: -scores[i])


q = "8518.30 earbuds"
kw, sem = ranking(bm25(q, DOCS)), ranking(semantic(q, DOCS))
print("keyword :", [DOCS[i] for i in kw[:2]])
print("semantic:", [DOCS[i] for i in sem[:2]])
print("hybrid  :", [DOCS[i] for i in rrf([kw, sem])[:2]])
```

## 💻 Code Example — Advanced
```python
# Hybrid search with Postgres full-text + pgvector, fused by RRF (async, psycopg/asyncpg style via SQL)
import asyncio
import asyncpg                                         # pip install asyncpg
from openai import AsyncOpenAI

client = AsyncOpenAI()

HYBRID_SQL = """
WITH sem AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> $1::vector) AS rnk
  FROM tariff_docs ORDER BY embedding <=> $1::vector LIMIT 30
),
kw AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank_cd(tsv, plainto_tsquery('english', $2)) DESC) AS rnk
  FROM tariff_docs WHERE tsv @@ plainto_tsquery('english', $2)
  ORDER BY ts_rank_cd(tsv, plainto_tsquery('english', $2)) DESC LIMIT 30
)
SELECT d.id, d.text,
       COALESCE(1.0 / (60 + sem.rnk), 0) + COALESCE(1.0 / (60 + kw.rnk), 0) AS score
FROM tariff_docs d
LEFT JOIN sem ON sem.id = d.id
LEFT JOIN kw  ON kw.id  = d.id
WHERE sem.id IS NOT NULL OR kw.id IS NOT NULL
ORDER BY score DESC LIMIT $3;
"""


async def hybrid_search(pool: asyncpg.Pool, query: str, k: int = 5) -> list[asyncpg.Record]:
    try:
        r = await client.embeddings.create(model="text-embedding-3-small", input=query)
        vec = "[" + ",".join(map(str, r.data[0].embedding)) + "]"    # pgvector text format
    except Exception as exc:
        raise RuntimeError(f"embedding failed: {exc}") from exc
    async with pool.acquire() as con:
        return await con.fetch(HYBRID_SQL, vec, query, k)


async def main() -> None:
    pool = await asyncpg.create_pool("postgresql://user:pass@localhost/tariff")
    for row in await hybrid_search(pool, "8518.30 earbuds"):
        print(row["id"], round(row["score"], 4), row["text"])


if __name__ == "__main__":
    asyncio.run(main())            # needs Postgres with pgvector, a tsv column, and an OpenAI key
```
(Table assumed: `tariff_docs(id, text, embedding vector(1536), tsv tsvector)` with HNSW and GIN indexes.)

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Query
from typing import Literal

app = FastAPI()


def looks_like_identifier(q: str) -> bool:
    """Digits with dots/dashes (HS codes, SKUs) favour keyword search."""
    return any(c.isdigit() for c in q) and len(q.split()) <= 3


@app.get("/search")
async def search(q: str = Query(min_length=2),
                 mode: Literal["auto", "keyword", "semantic", "hybrid"] = "auto") -> dict[str, str]:
    chosen = mode
    if mode == "auto":
        chosen = "keyword" if looks_like_identifier(q) else "hybrid"   # simple router
    # call keyword_search / semantic_search / hybrid_search here
    return {"query": q, "strategy": chosen}
```
Expose `mode` so you can A/B test strategies and log which one users prefer.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever      # pip install rank_bm25
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

texts = ["8518.30 Headphones and earphones", "0901.11 Coffee, not roasted", "8517.13 Smartphones"]
bm25 = BM25Retriever.from_texts(texts); bm25.k = 3                    # keyword retriever
vec = Chroma.from_texts(texts, OpenAIEmbeddings(model="text-embedding-3-small")).as_retriever(search_kwargs={"k": 3})
hybrid = EnsembleRetriever(retrievers=[bm25, vec], weights=[0.4, 0.6])  # weighted RRF
docs = hybrid.invoke("8518.30 earbuds")
```
In LangGraph, make `route_query` a conditional edge choosing keyword, semantic, or hybrid retriever nodes.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Adding raw scores from different systems
✅ Correct: BM25 and cosine scores have different scales; use RRF or normalise first.

```python
# Wrong
score = bm25_score + cosine_score
# Right
score = 1 / (60 + rank_bm25) + 1 / (60 + rank_vec)
```

❌ Mistake 2: Assuming semantic always beats keyword
✅ Correct: Test; keyword often wins on codes, names, and rare terms.

❌ Mistake 3: No evaluation split by query type
✅ Correct: Measure ID queries and natural-language queries separately.

---

## 🧠 Tricky Interview Question

**Q**: "Your semantic search handles 'cheap phones' well but returns 'NOT waterproof' products for 'waterproof phones'. Why, and how to fix?"

**Answer**: Embeddings capture topic similarity, so "not waterproof" is close to "waterproof"; negation and exact attributes are weak. Fixes: extract attributes into structured metadata (waterproof: true) and filter, add keyword matching, use a reranker/cross-encoder that understands negation, or an LLM verification step on the top results.

---

## ⚫ Interview Questions + Answers

Q1: What does BM25 do?
A1: A keyword ranking function using term frequency, inverse document frequency, and length normalisation.

Q2: What is hybrid search?
A2: Running keyword and semantic search together and fusing their results.

Q3: What is Reciprocal Rank Fusion?
A3: Combines ranked lists by summing 1/(k + rank) for each document; scale-free and simple.

Q4: Where does keyword search beat semantic?
A4: Exact IDs, product codes, names, rare jargon, legal citations, and negations.

Q5: How do you tune hybrid weights?
A5: Build a labelled set across query types, grid search alpha or RRF settings, optimise recall@k/MRR, and verify per segment; consider query-type routing instead of one global weight.

---

## 🔷 When to Use + When Not to Use
✅ Use semantic when:
- Natural-language, vague, multilingual queries

✅ Use keyword when:
- IDs, codes, names, exact phrases, and tiny corpora

✅ Use hybrid when:
- Mixed query types (most production systems)

❌ Avoid semantic-only when:
- Precision on exact terms is critical

---

## 📊 Visual Diagram
```
 query ──┬─► BM25 (exact terms) ───► ranked list A ─┐
         │                                          ├─► RRF fuse ─► (rerank) ─► results
         └─► embedding (meaning) ──► ranked list B ─┘

 "8518.30 earbuds":  A finds "8518.30" ;  B finds "earphones"  ;  fused = best of both
```

---

## 💰 Cost Impact
Keyword search costs no embedding tokens (search index CPU only). Semantic needs one embedding per query (tiny) plus vector index memory. Hybrid adds both but only slightly; in return fewer retrieval failures means fewer retries and fewer wasted LLM tokens. If a rerank model is added (e.g. Cohere Rerank charges per search), compare its cost against sending extra chunks to the LLM: reranking to the top 3 usually costs less than sending 10 chunks (about 3,000 tokens more per query).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BM25 | Keyword ranking formula | Keyword ranking formula |
| Hybrid search | Keyword + semantic | Keyword + semantic दोनों |
| RRF | Rank fusion method | Ranks मिलाने की विधि |
| IDF | Rarity weight of a term | Term की दुर्लभता का वज़न |
| Full-text search | Word index search | शब्द index पर search |
| Router | Chooses search type | Search type चुनने वाला |

---

## ⚡ 3-Line Summary
English: Keyword search matches exact words; semantic search matches meaning. Each fails where the other is strong, so hybrid search with rank fusion is the production default. Tune and evaluate by query type.
Hindi: Keyword search exact शब्द match करता है; semantic search meaning। हर एक वहाँ fail होता है जहाँ दूसरा strong है, इसलिए rank fusion वाला hybrid search production का default है। Query type के अनुसार tune और evaluate करो।

---

## ➡️ Next Topic
**123. Embedding Drift** - what happens when data, queries, or models change and your vectors go stale.
