---

# 578. Build Hybrid Search
# हिंदी में: Hybrid Search बनाना

---

## 🔵 Simple Definition (English)
Hybrid search runs two retrievers on the same query: a keyword engine (BM25) and a semantic engine (vector similarity). It then merges the two ranked lists, usually with Reciprocal Rank Fusion (RRF). You get exact matches (like "8517.13") and meaning matches (like "mobile phone" = "smartphone").

## 🔵 सरल परिभाषा (Hindi)
Hybrid search एक ही query पर दो retriever चलाता है: keyword वाला (BM25) और semantic वाला (vector similarity)। फिर दोनों ranked lists को RRF से merge करता है। इससे exact match ("8517.13") भी मिलता है और meaning match ("mobile phone" = "smartphone") भी।

---

## 🔴 Problem it Solves
Pure vector search is weak on exact tokens: HS codes, SKU numbers, legal clause IDs and rare names get "blurred" in embeddings. Pure keyword search misses synonyms and paraphrases. Interviewers ask this problem because real RAG quality usually jumps when you combine both. Raw scores from BM25 and cosine are on different scales, so you cannot just add them. RRF solves that by using ranks only.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ vector search में HS code, SKU, clause number जैसे exact tokens कमजोर पड़ते हैं। सिर्फ keyword search synonyms miss करता है। BM25 और cosine के scores की scale अलग होती है, इसलिए सीधे जोड़ नहीं सकते। RRF सिर्फ rank इस्तेमाल करके यह problem हल करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise + tokenise the query (keep codes like 8517.13 intact)
Step 2 → BM25 ranks documents by term frequency and rarity (IDF)
Step 3 → Embed the query, rank documents by cosine similarity
Step 4 → Fuse: score(d) = sum over lists of 1 / (k + rank_in_list), k = 60
Step 5 → Sort by fused score, take top-k
Step 6 → (Optional) rerank the top 20-50 with a cross-encoder
Step 7 → Send top chunks to the LLM as context
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Query को साफ़ करो, tokens बनाओ (8517.13 जैसे codes न टूटें)
Step 2 → BM25 term frequency और IDF से documents rank करता है
Step 3 → Query का embedding बनाओ, cosine से rank करो
Step 4 → Fusion: score = हर list के लिए 1/(k + rank) का जोड़
Step 5 → Fused score से sort करो, top-k लो
Step 6 → (Optional) cross-encoder से rerank
Step 7 → Top chunks LLM को context में दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: An officer searches "HS 8517.13". BM25 finds the exact code instantly; vectors might return laptops. Another officer types "mobile phone duty". BM25 finds nothing (the doc says "smartphones") but vectors match. Hybrid returns the right chunk for both. **Amazon-style**: product search "iphone 15 128gb" needs exact model tokens (BM25) plus intent like "cheap phone for kids" (vectors). **Zomato-style**: "paneer butter masala near me" mixes dish keywords and semantic similarity.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer "HS 8517.13" search करता है। BM25 exact code तुरंत पकड़ता है, vectors शायद laptops दे दें। दूसरा officer "mobile phone duty" लिखता है: doc में "smartphones" है, BM25 को कुछ नहीं मिलता पर vectors पकड़ लेते हैं। Hybrid दोनों case सही हल करता है। **Amazon**: "iphone 15 128gb" में exact tokens चाहिए। **Zomato**: "paneer butter masala" में dish keywords + semantic similarity दोनों।

---

## 💻 Code Example — Basic
Full runnable solution: `main.py` (BM25 + fake vector search + RRF, offline).

```python
# Basic: fuse two ranked lists with Reciprocal Rank Fusion
def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:  # fusion function
    scores: dict[str, float] = {}  # doc_id -> fused score
    for ranking in rankings:  # loop over each retriever's ranked list
        for rank, doc_id in enumerate(ranking, start=1):  # ranks start at 1
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)  # add reciprocal rank
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)  # best first

bm25_list = ["d1", "d2", "d3"]  # keyword results
vector_list = ["d3", "d1", "d9"]  # semantic results
print(rrf([bm25_list, vector_list]))  # d1 and d3 win because both lists like them
```

## 💻 Code Example — Advanced
See `main.py`: `BM25` class (k1=1.5, b=0.75), `vector_search`, `rrf`, `hybrid_search` with input validation (`ValueError` on empty query) and `ahybrid_search` (async wrapper via `asyncio.to_thread`).

```python
# Production shape: parallel retrievers + weighted RRF + error isolation
import asyncio
from typing import Awaitable, Callable

Ranked = list[tuple[str, float]]  # (doc_id, score) list

async def safe(retriever: Callable[[str], Awaitable[Ranked]], q: str) -> Ranked:  # wrap one retriever
    try:  # a failing retriever must not kill the request
        return await asyncio.wait_for(retriever(q), timeout=1.0)  # latency budget
    except Exception:  # timeout or backend error
        return []  # degrade gracefully to the other retriever

async def hybrid(q: str, bm25: Callable, vec: Callable, w: tuple[float, float] = (1.0, 1.0)) -> Ranked:
    a, b = await asyncio.gather(safe(bm25, q), safe(vec, q))  # run both in parallel
    fused: dict[str, float] = {}  # accumulator
    for weight, ranking in ((w[0], a), (w[1], b)):  # weighted fusion
        for rank, (doc_id, _) in enumerate(ranking, 1):  # use rank not raw score
            fused[doc_id] = fused.get(doc_id, 0.0) + weight / (60 + rank)  # weighted RRF
    return sorted(fused.items(), key=lambda x: x[1], reverse=True)  # final order
```

---

## 🟠 FastAPI Integration
Expose `/search` and return which retriever contributed, so you can debug relevance.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from main import ahybrid_search  # the function from main.py

app = FastAPI()  # app instance

class SearchIn(BaseModel):  # request schema
    query: str = Field(min_length=1, max_length=200)  # validate length
    k: int = Field(default=3, ge=1, le=20)  # bounded top-k

@app.post("/search")  # route
async def search(body: SearchIn) -> dict:  # async handler
    try:  # guard the call
        hits = await ahybrid_search(body.query, body.k)  # run hybrid
    except ValueError as exc:  # bad input
        raise HTTPException(status_code=422, detail=str(exc))  # client error
    return {"results": [{"id": d, "score": s} for d, s in hits]}  # JSON response
```

---

## 🔗 LangChain / LangGraph Connection
LangChain ships `EnsembleRetriever` (RRF-based) and `BM25Retriever` (needs `rank_bm25`). Many vector DBs (Weaviate, Qdrant, Elasticsearch, pgvector + tsvector) offer native hybrid queries. In LangGraph, put hybrid retrieval in a `retrieve` node and loop back to "rewrite query" if results are weak.

```python
# Needs: pip install langchain langchain-community rank_bm25 (illustrative wiring)
from langchain.retrievers import EnsembleRetriever  # import path may vary by version
from langchain_community.retrievers import BM25Retriever

def build(docs, vector_store):  # docs: list[Document]
    bm25 = BM25Retriever.from_documents(docs)  # keyword retriever
    bm25.k = 5  # top-5
    vec = vector_store.as_retriever(search_kwargs={"k": 5})  # semantic retriever
    return EnsembleRetriever(retrievers=[bm25, vec], weights=[0.5, 0.5])  # RRF-style fusion
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Adding raw BM25 and cosine scores
✅ Correct: Fuse by rank (RRF) or normalise scores first.

```python
# Wrong: scales differ (BM25 ~ 0-20, cosine ~ 0-1), BM25 always wins
score = bm25_score + cosine_score
# Right: reciprocal rank fusion
score = 1 / (60 + bm25_rank) + 1 / (60 + vector_rank)
```

❌ Mistake 2: Tokenizer that destroys codes
✅ Correct: Keep dots and dashes inside tokens.

```python
import re
# Wrong: splits "8517.13" into "8517" and "13"
bad = re.findall(r"\w+", "HS 8517.13")
# Right: keep the full code as one token
good = re.findall(r"[a-z0-9][a-z0-9.\-]*", "hs 8517.13")
print(bad, good)
```

---

## 🧠 Tricky Interview Question
**Q**: "Hybrid search made recall better overall, but one query class got worse: long natural-language questions. Why, and what do you do?"

**Answer**: Long questions contain many common words, so BM25 returns noisy matches and RRF gives them equal weight to good vector hits. Fixes: drop stop words or use query-length-aware weights (lower BM25 weight for long queries), rewrite the query with an LLM into keywords for BM25 and a clean sentence for vectors, and add a cross-encoder reranker. Always measure per query class, not only average recall.

---

## ⚫ Interview Questions + Answers

Q1: What does BM25 score depend on? (Easy)
A1: Term frequency in the document (with saturation via k1), inverse document frequency (rare terms matter more) and document length normalisation (b).

Q2: Why hybrid instead of only vectors? (Easy)
A2: Vectors miss exact identifiers and rare terms; keywords miss synonyms. Hybrid covers both failure modes.

Q3: Why RRF and what is k=60? (Medium)
A3: RRF uses ranks, so incompatible score scales do not matter. k dampens the dominance of rank 1; 60 is the common default from the original paper. It is robust with no tuning.

Q4: How do you evaluate that hybrid helps? (Medium)
A4: Build a golden set with labelled relevant docs, compare BM25, vector and hybrid on recall@k and MRR, and slice by query type (code lookups, paraphrases, long questions).

Q5: Design hybrid search for 50M chunks with 200 ms p95. (Hard)
A5: Use a store with native hybrid (Elasticsearch/OpenSearch, Qdrant, Weaviate) or shard both indexes. Run both retrievers in parallel with per-retriever timeouts, fetch top 50 each, fuse with RRF, rerank only the top 20 with a small cross-encoder, cache frequent queries, and use ANN (HNSW) with filters pushed down (country, year) to shrink the candidate set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Corpus has IDs, codes, names, numbers and natural language mixed
- Users type both short keywords and long questions
- You need better recall without fine-tuning

❌ Avoid when:
- Tiny corpus (under ~100 docs) where simple vector search is enough
- Pure conversational content with no exact tokens
- Latency budget cannot afford two retrievers

---

## 📊 Visual Diagram
```
            Query
              │
     ┌────────┴────────┐
     ▼                 ▼
  BM25 (keyword)   Embedding (semantic)
  d1 d2 d3          d3 d1 d9
     └────────┬────────┘
              ▼
        RRF: 1/(60+rank)
              ▼
      fused: d1, d3, d2, d9
              ▼
     (optional) cross-encoder rerank
              ▼
        top-k -> LLM context
```

---

## 💰 Cost Impact
BM25 is nearly free (CPU). The query embedding costs a few dozen tokens per search (tiny, and many embedding models are priced per 1M tokens; check current pricing). The big cost is the LLM: better retrieval means fewer, more relevant chunks in the prompt. Example (illustrative): sending 3 chunks x 300 tokens instead of 8 chunks x 300 saves 1,500 input tokens per query. Optimise: cache query embeddings, rerank only the top 20, keep k small, and compress context.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BM25 | Keyword ranking function | Keyword ranking formula |
| IDF | Rare words weigh more | दुर्लभ शब्द ज़्यादा important |
| RRF | Rank-based list fusion | Rank से lists जोड़ना |
| Dense retrieval | Embedding similarity search | Vector आधारित search |
| Reranker | Second-stage precise scorer | दूसरा, ज़्यादा सटीक scorer |
| Recall@k | Share of relevant docs in top-k | Top-k में सही docs का हिस्सा |

---

## ⚡ 3-Line Summary
English: Hybrid search = BM25 + vector search merged with RRF. It handles both exact codes and paraphrases. Fuse by rank, not raw score, and measure per query type.
Hindi: Hybrid search = BM25 + vector search, RRF से merge। यह exact codes और paraphrase दोनों संभालता है। Raw score नहीं, rank से fuse करो और query type के हिसाब से measure करो।

---

## ➡️ Next Topic
**579. Build Multi-turn Chatbot** — after retrieval, you need conversation memory so follow-up questions work.
