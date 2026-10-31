---

# 199. Hybrid Search (BM25 + Dense)
# हिंदी में: Hybrid Search (BM25 + Dense)

---

## 🔵 Simple Definition (English)
Hybrid search runs a keyword retriever (BM25) and a semantic retriever (dense embeddings) for the same query and merges their results into one ranked list. It keeps exact-match power for codes and names and semantic power for paraphrases.

## 🔵 सरल परिभाषा (Hindi)
Hybrid search एक ही query पर keyword retriever (BM25) और semantic retriever (dense embeddings) दोनों चलाता है और उनके results को एक ranked list में मिलाता है। इससे codes और नामों के लिए exact match और paraphrase के लिए semantic ताकत दोनों मिलती हैं।

---

## 🔴 Problem it Solves
BM25 misses synonyms ("mobile" vs "smartphone"); dense misses exact identifiers ("8518.30" vs "8518.40"). Real queries mix both: "duty on 8518.30 wireless earphones". Neither alone gives reliable recall; hybrid covers the weak spots of each.

## 🔴 यह क्यों बना? (Hindi)
BM25 synonyms ("mobile" बनाम "smartphone") miss करता है; dense exact identifiers ("8518.30" बनाम "8518.40") miss करता है। असली queries दोनों मिलाती हैं: "8518.30 wireless earphones पर duty"। कोई अकेला भरोसेमंद recall नहीं देता; hybrid दोनों की कमज़ोरियाँ ढक देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Same query goes to BM25 and to dense search (in parallel)
Step 2 → Each returns top-N (e.g., 30) with its own scores/ranks
Step 3 → Scores are on different scales, so do NOT add raw scores directly
Step 4 → Fuse: (a) RRF on ranks (robust, default) or (b) weighted sum of normalised scores
Step 5 → Deduplicate by chunk id and keep top-K
Step 6 → Optional: rerank with a cross-encoder; apply metadata filters in both retrievers
Step 7 → Tune weights/alpha on a labeled set (e.g., 0.3 keyword / 0.7 dense)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → वही query BM25 और dense search दोनों को जाती है (parallel)
Step 2 → हर एक अपने scores/ranks के साथ top-N (जैसे 30) लौटाता है
Step 3 → Scores अलग scale पर हैं, इसलिए raw scores सीधे न जोड़ो
Step 4 → Fuse: (a) ranks पर RRF (robust, default) या (b) normalised scores का weighted sum
Step 5 → Chunk id से dedupe करो और top-K रखो
Step 6 → Optional: cross-encoder से rerank; दोनों retrievers में metadata filters
Step 7 → Labeled set पर weights/alpha tune करो (जैसे 0.3 keyword / 0.7 dense)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "duty on 8518.30 wireless earphones for India". BM25 nails the chunk with token "8518.30"; dense finds chunks about "Bluetooth headsets"; fusion places the chunk that appears in both lists at the top. Result: correct code chunk first, plus helpful related notes.
**Amazon AI**: "sony wh-1000xm5 noise cancelling" mixes a model number (keyword) and a concept (semantic).

## 🟡 Real Example Hindi mein
**Tariff System**: Query "India के लिए 8518.30 wireless earphones पर duty"। BM25 "8518.30" token वाला chunk पकड़ता है; dense "Bluetooth headsets" वाले chunks ढूँढता है; fusion उस chunk को सबसे ऊपर रखता है जो दोनों lists में है। नतीजा: सही code वाला chunk पहले, साथ में उपयोगी related notes।
**Amazon AI**: "sony wh-1000xm5 noise cancelling" में model number (keyword) और concept (semantic) दोनों हैं।

---

## 💻 Code Example — Basic
```python
# Hybrid search = BM25 ranks + keyword-free "semantic" ranks, merged with a weighted score (pure Python)
import math
import re
from collections import Counter
from typing import Dict, List

DOCS: Dict[str, str] = {
    "d1": "HS 8518.30 earphones and headsets duty 0 percent",
    "d2": "HS 8518.40 audio amplifiers duty 0 percent",
    "d3": "wireless bluetooth headset for listening to music",
    "d4": "HS 6403.99 leather footwear duty 20 percent",
}
SYNONYMS = {"earphones": "audio", "headset": "audio", "headsets": "audio", "bluetooth": "audio", "amplifiers": "audio"}  # toy semantics

def tokens(t: str) -> List[str]:
    return re.findall(r"\d+\.\d+|\w+", t.lower())

def bm25_scores(q: str, k1: float = 1.5, b: float = 0.75) -> Dict[str, float]:
    toks = {d: tokens(t) for d, t in DOCS.items()}  # tokenised docs
    avg = sum(len(t) for t in toks.values()) / len(toks)  # avg length
    df = Counter(w for t in toks.values() for w in set(t))  # doc frequency
    out: Dict[str, float] = {}
    for d, t in toks.items():
        tf = Counter(t); s = 0.0  # tf and score
        for w in tokens(q):
            if tf[w]:
                idf = math.log(1 + (len(DOCS) - df[w] + 0.5) / (df[w] + 0.5))
                s += idf * tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(t) / avg))
        out[d] = s
    return out

def semantic_scores(q: str) -> Dict[str, float]:
    """Toy semantic score: map words to concept tokens and compare concept overlap."""
    concept = lambda t: Counter(SYNONYMS.get(w, w) for w in tokens(t) if w in SYNONYMS)  # only concept words
    qc = concept(q)
    return {d: float(sum((qc & concept(t)).values())) for d, t in DOCS.items()}  # shared concepts

def minmax(scores: Dict[str, float]) -> Dict[str, float]:
    lo, hi = min(scores.values()), max(scores.values())  # range
    return {d: 0.0 if hi == lo else (s - lo) / (hi - lo) for d, s in scores.items()}  # scale to 0..1

def hybrid(q: str, alpha: float = 0.5, k: int = 3) -> List[str]:
    kw, sem = minmax(bm25_scores(q)), minmax(semantic_scores(q))  # comparable scales
    fused = {d: alpha * kw[d] + (1 - alpha) * sem[d] for d in DOCS}  # weighted sum
    return sorted(fused, key=fused.get, reverse=True)[:k]  # best first

if __name__ == "__main__":
    print(hybrid("8518.30 wireless earphones"))  # d1 first (code + concept), d3 next (concept only)
```

## 💻 Code Example — Advanced
```python
# Async hybrid retriever: parallel backends, graceful degradation, RRF or weighted fusion, per-source debug info
import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, Literal

logger = logging.getLogger("hybrid")  # logger
Searcher = Callable[[str, int], Awaitable[list[str]]]  # query, n -> ranked list of chunk ids

@dataclass
class HybridHit:
    id: str  # chunk id
    score: float  # fused score
    sources: dict[str, int]  # retriever name -> rank (1-based)

class HybridRetriever:
    def __init__(self, sparse: Searcher, dense: Searcher, mode: Literal["rrf", "weighted"] = "rrf",
                 w_sparse: float = 0.4, w_dense: float = 0.6, rrf_k: int = 60, timeout_s: float = 2.0) -> None:
        self.sparse, self.dense, self.mode = sparse, dense, mode  # retrievers and fusion mode
        self.w = {"sparse": w_sparse, "dense": w_dense}  # weights for weighted rank fusion
        self.rrf_k, self.timeout_s = rrf_k, timeout_s  # config

    async def _safe(self, name: str, fn: Searcher, q: str, n: int) -> list[str]:
        try:
            return await asyncio.wait_for(fn(q, n), self.timeout_s)  # bounded wait
        except Exception as exc:  # one backend failing must not fail the request
            logger.warning("%s failed: %r (degrading)", name, exc)
            return []

    async def search(self, q: str, k: int = 5, n: int = 30) -> list[HybridHit]:
        sp, de = await asyncio.gather(self._safe("sparse", self.sparse, q, n), self._safe("dense", self.dense, q, n))
        ranks = {"sparse": sp, "dense": de}  # per-source ranked ids
        fused: dict[str, HybridHit] = {}
        for name, lst in ranks.items():
            for rank, cid in enumerate(lst, start=1):  # rank 1 = best
                contrib = 1 / (self.rrf_k + rank) if self.mode == "rrf" else self.w[name] * (1 - (rank - 1) / n)
                hit = fused.setdefault(cid, HybridHit(cid, 0.0, {}))
                hit.score += contrib; hit.sources[name] = rank  # accumulate and remember
        return sorted(fused.values(), key=lambda h: -h.score)[:k]

async def demo_sparse(q: str, n: int) -> list[str]: return ["d1", "d2"]
async def demo_dense(q: str, n: int) -> list[str]: return ["d3", "d1"]

if __name__ == "__main__":
    h = HybridRetriever(demo_sparse, demo_dense)
    for hit in asyncio.run(h.search("8518.30 wireless earphones")):
        print(hit)  # d1 first: it appears in both lists
```

---

## 🟠 FastAPI Integration
Expose a `mode` and `alpha` for A/B tests, return which retrievers contributed to each hit (great for debugging), and log latency per backend.

```python
# FastAPI hybrid search endpoint
from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()  # app
hybrid_retriever = HybridRetriever(demo_sparse, demo_dense)  # replace demo_* with BM25 index + vector DB calls

class Req(BaseModel):
    query: str = Field(min_length=2, max_length=300)
    k: int = Field(5, ge=1, le=20)
    mode: Literal["rrf", "weighted"] = "rrf"

@app.post("/hybrid-search")
async def hybrid_search(req: Req) -> list[dict]:
    hybrid_retriever.mode = req.mode  # (better: build per-mode instances; mutation is for brevity)
    hits = await hybrid_retriever.search(req.query, k=req.k)
    return [{"id": h.id, "score": round(h.score, 5), "sources": h.sources} for h in hits]
```

---

## 🔗 LangChain / LangGraph Connection
`EnsembleRetriever` (in `langchain.retrievers`) fuses retrievers with weighted Reciprocal Rank Fusion. Many vector DBs (Weaviate, Qdrant, Elasticsearch, Pinecone sparse-dense, pgvector + tsvector) also offer native hybrid queries, which is faster than two round trips.

```python
# EnsembleRetriever: BM25 + dense (pip install langchain langchain-community rank_bm25 langchain-chroma langchain-openai)
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

docs = [Document(page_content="HS 8518.30 earphones duty 0"), Document(page_content="HS 6403.99 shoes duty 20")]
bm25 = BM25Retriever.from_documents(docs, k=3)  # keyword side
# dense = Chroma.from_documents(docs, OpenAIEmbeddings()).as_retriever(search_kwargs={"k": 3})   # semantic side
# hybrid = EnsembleRetriever(retrievers=[bm25, dense], weights=[0.4, 0.6])                        # weighted RRF
# print(hybrid.invoke("8518.30 earphones"))
print([d.page_content for d in bm25.invoke("8518.30")])  # keyword half works offline
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Adding raw BM25 scores and cosine similarities directly.
✅ Correct: Use rank-based fusion (RRF) or normalise each score list first.

```python
# Wrong: BM25 ranges 0-30, cosine 0-1 -> BM25 dominates
score = bm25 + cosine
# Right
score = 1 / (60 + rank_bm25) + 1 / (60 + rank_dense)
```

❌ Mistake 2: Fixing weights by gut feeling and never evaluating.
✅ Correct: Tune alpha/weights on a labeled query set, separately for code-heavy and conceptual queries.

```python
# Wrong
weights = [0.5, 0.5]       # "looks fair"
# Right
best = max(grid, key=lambda w: recall_at_k(w, eval_queries))
```

---

## 🧠 Tricky Interview Question
**Q**: "Hybrid search is better on average in your eval, but a specific class of queries (pure conceptual questions) got worse. Why and what do you do?"

**Answer**: The keyword side adds noise when queries share few distinctive terms: common words match many chunks and pollute the fused top-K. Fix: query-adaptive weights (code-like queries get more BM25; long natural-language questions more dense), stopword handling or minimum BM25 score, retrieve more candidates and rerank with a cross-encoder, and evaluate per query segment instead of only average recall.

---

## ⚫ Interview Questions + Answers

Q1: What is hybrid search?
A1: Running keyword (BM25) and semantic (dense) search and merging the results.

Q2: Why not simply sum the scores?
A2: The scores live on different scales and distributions; use RRF on ranks or normalise first.

Q3: What is `alpha` in hybrid search?
A3: The weighting between dense and keyword scores (e.g., Weaviate: alpha=1 pure dense, 0 pure keyword).

Q4: When is dense-only enough?
A4: Conceptual Q&A over prose with few identifiers, small corpora, when evals show no gain from BM25.

Q5: How do you evaluate and deploy hybrid search?
A5: Build a labeled set with query types (code, concept, mixed); compare BM25, dense, hybrid on recall@k, MRR, nDCG; tune weights/k per segment; shadow-test in production; monitor latency (two retrievers, run parallel) and add a reranker if precision is lacking.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Corpus has IDs, codes, names AND natural language
- Domain vocabulary differs from user wording
- You need robust recall

❌ Avoid when:
- Tiny corpus where either method already gets ~100 percent
- Latency budget cannot afford two searches (use native hybrid in one DB)

---

## 📊 Visual Diagram
```
                   query
                 ┌───┴────┐
                 ▼        ▼
             BM25 top-30  Dense top-30        (parallel)
                 └───┬────┘
                     ▼
            Fusion: RRF = Σ 1/(60 + rank)
                     ▼
              dedupe by chunk id
                     ▼
         (optional) cross-encoder rerank
                     ▼
                 top-5 chunks
```

---

## 💰 Cost Impact
Hybrid adds almost no token cost: BM25 is free and the dense side needs one query embedding. Compute/latency increases slightly (parallel). The payoff is fewer missed chunks: better recall at small k, so you can send 4 chunks instead of 8 (saving ~1600 input tokens, about 0.00024 USD per query on gpt-4o-mini).
Optimize: use a DB with native hybrid, cache results for frequent queries, retrieve N=30 but send K=4.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hybrid search | Keyword + semantic together | Keyword + semantic एक साथ |
| Fusion | Merging ranked lists | Ranked lists मिलाना |
| RRF | Rank-based fusion formula | Rank आधारित fusion |
| Alpha | Dense vs keyword weight | Dense बनाम keyword का वज़न |
| Score normalisation | Scale scores to a common range | Scores को एक range में लाना |
| Sparse | Keyword-style retrieval | Keyword आधारित retrieval |

---

## ⚡ 3-Line Summary
English: Hybrid search merges BM25 (exact terms) and dense (meaning) results.
Fuse by rank (RRF) rather than raw scores and tune weights on your own eval set.
It raises recall cheaply, often followed by reranking.
Hindi: Hybrid search BM25 (exact शब्द) और dense (अर्थ) के results मिलाता है।
Raw scores की जगह rank (RRF) से fuse करो और अपने eval set पर weights tune करो।
यह सस्ते में recall बढ़ाता है, अक्सर इसके बाद reranking आती है।

---

## ➡️ Next Topic
**200. Reciprocal Rank Fusion (RRF)**: the exact formula behind rank-based fusion, with worked numbers.
