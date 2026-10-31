---

# 189. Retrieval Pipeline
# हिंदी में: Retrieval Pipeline (रिट्रीवल पाइपलाइन)

---

## 🔵 Simple Definition (English)
The retrieval pipeline is the online part of RAG that, for each question, finds the most relevant chunks: process the query, search (dense, sparse or hybrid) with filters, merge, rerank and return the best few chunks with scores and sources.

## 🔵 सरल परिभाषा (Hindi)
Retrieval pipeline RAG का online हिस्सा है जो हर सवाल के लिए सबसे relevant chunks ढूँढता है: query process करो, filters के साथ search (dense, sparse या hybrid) करो, merge करो, rerank करो, और सबसे अच्छे कुछ chunks scores और sources के साथ लौटाओ।

---

## 🔴 Problem it Solves
The LLM cannot read the whole knowledge base, and wrong context gives wrong answers. Retrieval decides the quality ceiling: the LLM cannot answer from a chunk it never saw. A weak retrieval pipeline (single top-k vector search) misses exact terms, ignores filters and returns near-duplicates.

## 🔴 यह क्यों बना? (Hindi)
LLM पूरा knowledge base नहीं पढ़ सकता, और गलत context से गलत जवाब मिलता है। Retrieval quality की upper limit तय करता है: जो chunk LLM ने देखा ही नहीं, उससे वह जवाब नहीं दे सकता। कमज़ोर retrieval (सिर्फ top-k vector search) exact terms miss करता है, filters ignore करता है और near-duplicates लौटाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise the query; optionally rewrite/expand
Step 2 → Extract metadata filters (country, year, chapter)
Step 3 → Dense search: embed query, ANN search top-N
Step 4 → Sparse search: BM25 top-N (in parallel)
Step 5 → Fuse results (RRF) and remove duplicates
Step 6 → Rerank top-N with a cross-encoder
Step 7 → Apply a score threshold and diversity (MMR) -> final k
Step 8 → Return chunks + scores + metadata for citation; log latency
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Query normalise करो; चाहें तो rewrite/expand
Step 2 → Metadata filters (country, year, chapter) निकालो
Step 3 → Dense search: query embed करके ANN search top-N
Step 4 → Sparse search: BM25 top-N (parallel)
Step 5 → Results fuse (RRF) करो और duplicates हटाओ
Step 6 → Cross-encoder से top-N rerank करो
Step 7 → Score threshold और diversity (MMR) लगाकर final k
Step 8 → Chunks + scores + metadata लौटाओ; latency log करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "import duty on wireless earbuds to India, 2025". Filters: `country=IN`, `year=2025`. Dense search finds "Bluetooth headsets", BM25 finds "8518.30", fusion puts both on top, the reranker picks the 8518.30 subheading chunk, and a threshold of 0.3 drops weak matches so the bot says "not found" rather than guessing.
**Zomato AI**: Retrieval finds restaurants by meaning ("cozy cafe") and by exact tokens ("Koramangala").

## 🟡 Real Example Hindi mein
**Tariff System**: Query "India में wireless earbuds पर import duty, 2025"। Filters: `country=IN`, `year=2025`। Dense search "Bluetooth headsets" ढूँढता है, BM25 "8518.30" ढूँढता है, fusion दोनों ऊपर रखता है, reranker 8518.30 वाला chunk चुनता है, और 0.3 threshold कमज़ोर matches हटा देता है ताकि bot अंदाज़ा लगाने की बजाय "नहीं मिला" कहे।
**Zomato AI**: Retrieval अर्थ ("cozy cafe") और exact शब्द ("Koramangala") दोनों से restaurants ढूँढता है।

---

## 💻 Code Example — Basic
```python
# Minimal retrieval: filter -> score -> threshold -> top-k (pure Python)
import math
from collections import Counter
from typing import Dict, List

CHUNKS: List[Dict] = [
    {"id": "a", "text": "wireless earbuds bluetooth headset hs 8518.30", "country": "IN"},
    {"id": "b", "text": "smartphones hs 8517.13 duty zero", "country": "IN"},
    {"id": "c", "text": "wireless earbuds bluetooth headset hs 8518.30", "country": "US"},
]

def vec(text: str) -> Counter:
    """Bag-of-words vector."""
    return Counter(text.lower().split())

def cos(a: Counter, b: Counter) -> float:
    """Cosine similarity."""
    dot = sum(a[w] * b[w] for w in a)  # overlap
    den = math.sqrt(sum(x * x for x in a.values())) * math.sqrt(sum(x * x for x in b.values()))
    return dot / den if den else 0.0

def retrieve(query: str, country: str, k: int = 2, min_score: float = 0.2) -> List[Dict]:
    """Return top-k chunks for the country that pass the score threshold."""
    q = vec(query)  # query vector
    pool = [c for c in CHUNKS if c["country"] == country]  # metadata filter first
    scored = [(cos(q, vec(c["text"])), c) for c in pool]  # score each
    scored.sort(key=lambda t: t[0], reverse=True)  # best first
    return [{**c, "score": round(s, 3)} for s, c in scored[:k] if s >= min_score]  # threshold

if __name__ == "__main__":
    print(retrieve("duty on wireless earbuds", "IN"))  # only IN chunk about earbuds passes
```

## 💻 Code Example — Advanced
```python
# Async hybrid retrieval: parallel dense + sparse, RRF fusion, dedupe, timeout, fallback
import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable

logger = logging.getLogger("retrieval")  # logger

@dataclass(frozen=True)
class Hit:
    id: str  # chunk id
    text: str  # chunk text
    score: float  # final score

Searcher = Callable[[str, int, dict | None], Awaitable[list[tuple[str, str]]]]  # returns [(id, text)] ranked

def rrf(rank_lists: list[list[tuple[str, str]]], k: int = 60) -> list[Hit]:
    """Reciprocal Rank Fusion: score = sum(1 / (k + rank))."""
    scores: dict[str, float] = {}; texts: dict[str, str] = {}  # accumulators
    for lst in rank_lists:
        for rank, (cid, text) in enumerate(lst, start=1):  # rank starts at 1
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
            texts[cid] = text
    ordered = sorted(scores, key=scores.get, reverse=True)  # high score first
    return [Hit(cid, texts[cid], scores[cid]) for cid in ordered]

class Retriever:
    def __init__(self, dense: Searcher, sparse: Searcher, timeout_s: float = 2.0) -> None:
        self.dense, self.sparse, self.timeout_s = dense, sparse, timeout_s  # deps

    async def _safe(self, name: str, fn: Searcher, q: str, n: int, flt: dict | None) -> list[tuple[str, str]]:
        try:
            return await asyncio.wait_for(fn(q, n, flt), self.timeout_s)  # bounded wait
        except Exception as exc:  # one backend down must not kill retrieval
            logger.warning("%s search failed: %r", name, exc)
            return []

    async def search(self, query: str, k: int = 5, n: int = 30, flt: dict | None = None) -> list[Hit]:
        dense, sparse = await asyncio.gather(  # run both searches in parallel
            self._safe("dense", self.dense, query, n, flt),
            self._safe("sparse", self.sparse, query, n, flt),
        )
        fused = rrf([dense, sparse])  # merge ranks
        seen: set[str] = set(); out: list[Hit] = []  # dedupe by normalised text
        for h in fused:
            key = " ".join(h.text.lower().split())  # normalise whitespace/case
            if key not in seen:
                seen.add(key); out.append(h)
        return out[:k]
```

---

## 🟠 FastAPI Integration
Expose retrieval as its own endpoint (`/search`). It helps debugging and lets other services reuse it. Return scores and ids, enforce `k` limits, and put per-user filters on the server side (never trust the client for ACL filters).

```python
# FastAPI /search endpoint with server-enforced tenant filter
from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel

app = FastAPI()  # app

class HitOut(BaseModel):
    id: str  # chunk id
    text: str  # chunk text
    score: float  # fused score

def current_tenant() -> str:
    return "tenant-1"  # replace with auth dependency (JWT)

@app.get("/search", response_model=list[HitOut])
async def search(q: str = Query(min_length=2, max_length=300), k: int = Query(5, ge=1, le=20),
                 tenant: str = Depends(current_tenant)) -> list[HitOut]:
    hits = await retriever.search(q, k=k, flt={"tenant": tenant})  # Retriever from Advanced example
    return [HitOut(id=h.id, text=h.text, score=h.score) for h in hits]
```

---

## 🔗 LangChain / LangGraph Connection
LangChain: `vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5, "filter": {...}})`, `BM25Retriever`, `EnsembleRetriever` (hybrid with RRF), `ContextualCompressionRetriever` (rerank/compress). In LangGraph, retrieval is a node that writes `documents` into state; a grader node can route back for retry.

```python
# EnsembleRetriever: BM25 + vector with RRF-style weighting (needs langchain, langchain-community, rank_bm25)
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

docs = [Document(page_content="wireless earbuds hs 8518.30"), Document(page_content="smartphones hs 8517.13")]  # corpus
bm25 = BM25Retriever.from_documents(docs); bm25.k = 2  # keyword retriever
# vector = Chroma.from_documents(docs, OpenAIEmbeddings()).as_retriever(search_kwargs={"k": 2})  # dense retriever
# hybrid = EnsembleRetriever(retrievers=[bm25, vector], weights=[0.4, 0.6])  # fused
print([d.page_content for d in bm25.invoke("8518.30")])  # BM25 alone works offline
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Applying metadata filters after top-k.
✅ Correct: Filter inside the vector search (pre-filter) so k results all satisfy the filter.

```python
# Wrong: top-5 then filter -> maybe 0 left
hits = [h for h in store.search(q, k=5) if h.meta["country"] == "IN"]
# Right: filter during search
hits = store.search(q, k=5, filter={"country": "IN"})
```

❌ Mistake 2: Always returning k results even when nothing is relevant.
✅ Correct: Use a score threshold; return empty and let the generator say "not found".

```python
# Wrong
return top_k
# Right
return [h for h in top_k if h.score >= 0.3]
```

---

## 🧠 Tricky Interview Question
**Q**: "Retrieval returns 5 chunks that are all almost the same paragraph from different versions of one document. How do you fix it?"

**Answer**: This is a duplicate / diversity problem. Options: dedupe by content hash at indexing time; keep only the latest `version` via a metadata filter; use MMR (max marginal relevance) to balance relevance and novelty; collapse by `doc_id` (max 1-2 chunks per document). This gives the LLM more varied evidence in the same token budget.

---

## ⚫ Interview Questions + Answers

Q1: What is top-k and how do you choose it?
A1: Number of chunks returned. Start with 20-30 for first-stage recall and 4-5 after rerank; tune with recall@k on a gold set.

Q2: What is the difference between dense and sparse retrieval?
A2: Dense uses embeddings (semantic meaning); sparse uses keyword statistics like BM25 (exact terms).

Q3: What is MMR?
A3: Max Marginal Relevance: picks results that are relevant to the query but different from already chosen ones; reduces redundancy.

Q4: Why pre-filter instead of post-filter?
A4: Post-filtering can leave fewer than k (or zero) results; pre-filtering guarantees k results from the allowed set, and enforces access control.

Q5: How do you measure retrieval quality?
A5: Build a labeled set (query -> relevant chunk ids). Measure recall@k, precision@k, MRR, nDCG. Track separately from generation quality; monitor in production with click/thumbs feedback.

---

## 🔷 When to Use + When Not to Use
✅ Use hybrid + rerank retrieval when:
- Queries mix meaning and exact codes/names
- Corpus is large and noisy
- Accuracy matters (legal, tariff, medical)

❌ Avoid complexity when:
- Corpus is tiny: simple dense top-k is enough
- Ultra-low latency needed: skip reranking or use a light model

---

## 📊 Visual Diagram
```
 Query ─► normalise ─► filters
              │
      ┌───────┴────────┐
      ▼                ▼
  Dense (ANN)      Sparse (BM25)      (parallel, top-30 each)
      └───────┬────────┘
              ▼
         RRF fusion + dedupe
              ▼
        Cross-encoder rerank
              ▼
   threshold + MMR ─► top-5 chunks (+scores, sources)
```

---

## 💰 Cost Impact
Dense search needs one query embedding (~20 tokens, about 0.0000004 USD). BM25 is free. Cross-encoder reranking has no token cost if self-hosted (cost is compute); hosted rerank APIs charge per search (roughly 1-2 USD per 1000 searches). The biggest saving is indirect: sending 4 precise chunks (~1600 tokens) instead of 10 noisy ones (~4000 tokens) to the LLM.
Optimize: cache query embeddings, tune k, apply thresholds, retrieve wide but send narrow.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Top-k | Number of results returned | लौटाए गए results की संख्या |
| ANN | Approximate nearest neighbour search | अनुमानित nearest-neighbour search |
| Pre-filter | Filter applied inside search | Search के दौरान filter |
| MMR | Relevance plus diversity | Relevance + विविधता |
| Score threshold | Minimum score to keep | न्यूनतम score |
| recall@k | Relevant found in top-k | Top-k में सही results का अनुपात |

---

## ⚡ 3-Line Summary
English: Retrieval finds the best chunks per query using filters, dense plus sparse search, fusion and reranking.
Use thresholds and diversity so the LLM gets precise, non-duplicate context.
Measure it separately with recall@k.
Hindi: Retrieval filters, dense + sparse search, fusion और reranking से हर query के best chunks ढूँढता है।
Thresholds और diversity लगाओ ताकि LLM को सटीक, non-duplicate context मिले।
इसे recall@k से अलग measure करो।

---

## ➡️ Next Topic
**190. Generation Pipeline**: how to turn retrieved chunks into a grounded, cited, validated answer.
