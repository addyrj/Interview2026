---

# 206. Reranking — What + Why
# हिंदी में: Reranking — क्या और क्यों

---

## 🔵 Simple Definition (English)
Reranking is a second pass after retrieval. A stronger model re-scores the top 20-100 retrieved chunks against the query and keeps only the best 3-5. Retrieval is fast but rough; reranking is slower but precise.

## 🔵 सरल परिभाषा (Hindi)
Reranking retrieval के बाद दूसरा pass है। एक stronger model top 20-100 chunks को query के against दोबारा score करता है और सिर्फ़ best 3-5 रखता है। Retrieval तेज़ पर rough होता है; reranking धीमा पर precise।

---

## 🔴 Problem it Solves
Vector search compares one fixed embedding per chunk with one embedding of the query (bi-encoder). The query and chunk never "see" each other, so near-misses rank high: "duty on laptop bags" can outrank "duty on laptops". Also LLMs get confused by noisy context and "lost in the middle". Reranking fixes ordering and lets you send fewer, better chunks.

## 🔴 यह क्यों बना? (Hindi)
Vector search में query और chunk के embeddings अलग-अलग बनते हैं (bi-encoder), वे एक-दूसरे को कभी साथ में नहीं देखते। इसलिए "laptop bags की duty" का chunk "laptops की duty" से ऊपर आ सकता है। Noisy context से LLM भी confuse होता है। Reranking ordering ठीक करता है और कम, बेहतर chunks भेजने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Stage 1 retrieval: vector/hybrid search returns top-N (N = 30-100), fast
Step 2 → Pair each candidate with the query: (query, chunk_i)
Step 3 → Reranker model gives each pair a relevance score
Step 4 → Sort by new score, descending
Step 5 → Keep top-K (K = 3-5), optionally drop below a score threshold
Step 6 → Send only those K chunks to the LLM prompt
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Stage 1: vector/hybrid search top-N (30-100) लाता है, तेज़
Step 2 → हर candidate को query के साथ pair करो: (query, chunk_i)
Step 3 → Reranker हर pair को relevance score देता है
Step 4 → नए score से sort करो (बड़ा पहले)
Step 5 → Top-K (3-5) रखो, चाहो तो threshold से कम score हटाओ
Step 6 → सिर्फ़ ये K chunks LLM prompt में भेजो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "HS code for lithium-ion power bank". Stage 1 returns 50 chunks: batteries (8507), chargers (8504), phone cases, bags. The reranker moves the 8507.60 lithium-ion accumulators note to rank 1 and the notes on "portable power units" to rank 2. Without reranking, the LLM might see a charger chapter first and classify wrongly. **Amazon search**: retrieve 500 products cheaply, rerank 50 with a heavy model. **Zomato**: retrieve nearby restaurants, rerank by predicted relevance.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "lithium-ion power bank का HS code"। Stage 1 से 50 chunks आते हैं: batteries (8507), chargers (8504), phone cases, bags। Reranker 8507.60 वाले note को rank 1 पर लाता है। बिना reranking के LLM को पहले charger chapter दिख सकता है और classification गलत हो सकती है। **Amazon**: 500 products सस्ते में लाओ, 50 को भारी model से rerank करो। **Zomato**: पास के restaurants लाओ, फिर relevance से rerank।

---

## 💻 Code Example — Basic
```python
# Pure Python: two-stage ranking with a toy "reranker". No API key needed.
from typing import List, Tuple  # type hints

DOCS: List[str] = [  # pretend these came from vector search (stage 1)
    "Laptop bags and cases customs duty 18 percent",
    "Laptops portable computers HS 8471 duty 0 percent",
    "Lithium-ion power bank HS 8507 duty 20 percent",
    "Mobile phone chargers HS 8504 duty 15 percent",
]


def stage1_scores(query: str, docs: List[str]) -> List[Tuple[float, str]]:
    """Cheap score: fraction of query words present in the doc."""
    q = set(query.lower().split())  # query words
    out: List[Tuple[float, str]] = []  # (score, doc)
    for d in docs:  # each doc
        words = set(d.lower().split())  # doc words
        out.append((len(q & words) / max(len(q), 1), d))  # overlap ratio
    return out  # unsorted list


def rerank(query: str, candidates: List[str], top_k: int = 2) -> List[Tuple[float, str]]:
    """Stricter score: reward exact phrase + penalise accessory words."""
    scored: List[Tuple[float, str]] = []  # result list
    for d in candidates:  # each candidate
        s = 0.0  # start score
        if query.lower() in d.lower():  # exact phrase match
            s += 2.0  # big boost
        s += sum(1 for w in query.lower().split() if w in d.lower())  # word hits
        if any(bad in d.lower() for bad in ("bags", "cases")):  # accessory penalty
            s -= 1.5  # demote accessories
        scored.append((s, d))  # store
    scored.sort(key=lambda x: x[0], reverse=True)  # best first
    return scored[:top_k]  # keep top-k


if __name__ == "__main__":
    query = "laptops"  # user query
    cands = [d for _, d in sorted(stage1_scores(query, DOCS), reverse=True)]  # stage 1 order
    print("Stage 1 order:", cands[0])  # what stage 1 puts first
    for score, doc in rerank(query, cands):  # stage 2
        print(f"{score:.1f}  {doc}")  # show reranked results
```

## 💻 Code Example — Advanced
```python
# Production pattern: a pluggable reranker interface with timeout + fallback.
import asyncio  # async + timeout
import logging  # logging
from dataclasses import dataclass  # simple data container
from typing import Protocol, Sequence  # interface typing

logger = logging.getLogger("rerank")  # logger


@dataclass(frozen=True)
class Scored:
    """A chunk with its relevance score and original rank."""
    text: str  # chunk text
    score: float  # relevance
    orig_rank: int  # rank before reranking


class Reranker(Protocol):
    """Any reranker (cross-encoder, Cohere, LLM) must implement this."""
    async def score(self, query: str, docs: Sequence[str]) -> list[float]: ...


class RerankPipeline:
    """Wraps a reranker with timeout, threshold and safe fallback."""

    def __init__(self, reranker: Reranker, timeout_s: float = 2.0, min_score: float = 0.0) -> None:
        self.reranker = reranker  # injected implementation
        self.timeout_s = timeout_s  # max wait
        self.min_score = min_score  # drop weak chunks

    async def run(self, query: str, docs: Sequence[str], top_k: int = 5) -> list[Scored]:
        try:  # reranker may be slow or down
            scores = await asyncio.wait_for(self.reranker.score(query, docs), self.timeout_s)  # guarded call
            if len(scores) != len(docs):  # sanity check
                raise ValueError("score count mismatch")  # bad output
        except Exception as exc:  # timeout / network / bug
            logger.warning("rerank failed, using retrieval order: %s", exc)  # log
            return [Scored(d, 0.0, i) for i, d in enumerate(docs[:top_k])]  # fallback keeps stage-1 order
        ranked = sorted(
            (Scored(d, s, i) for i, (d, s) in enumerate(zip(docs, scores))),  # build objects
            key=lambda x: x.score, reverse=True,  # highest first
        )
        return [r for r in ranked if r.score >= self.min_score][:top_k]  # threshold + top-k
```

---

## 🟠 FastAPI Integration
Expose reranking inside the retrieval route and return both original and new rank, which is helpful when debugging relevance.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app


class SearchReq(BaseModel):
    query: str  # user query
    top_k: int = 5  # chunks to keep


class Hit(BaseModel):
    text: str  # chunk
    score: float  # new score
    orig_rank: int  # rank from stage 1


@app.post("/search", response_model=list[Hit])  # POST /search
async def search(req: SearchReq) -> list[Hit]:
    candidates = ["chunk a", "chunk b", "chunk c"]  # replace with vector search top-50
    pipeline = RerankPipeline(reranker=...)  # inject real reranker (see 207/208)
    ranked = await pipeline.run(req.query, candidates, req.top_k)  # rerank
    return [Hit(text=r.text, score=r.score, orig_rank=r.orig_rank) for r in ranked]  # map to API
```

---

## 🔗 LangChain / LangGraph Connection
LangChain wraps rerankers as document compressors. `ContextualCompressionRetriever` runs the base retriever, then the compressor (reranker). In LangGraph, rerank is a node between `retrieve` and `generate`.

```python
from langchain.retrievers import ContextualCompressionRetriever  # wrapper retriever
# compressor can be CohereRerank, CrossEncoderReranker, LLMChainFilter, etc.
# base = vectorstore.as_retriever(search_kwargs={"k": 30})  # wide recall
# retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=base)
# docs = await retriever.ainvoke("HS code for power bank")  # returns reranked docs
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reranking only 5 documents
✅ Correct: Retrieve wide (30-100), rerank, then keep few.

```python
# Wrong: nothing to improve, rank-1 might not even be in the 5
docs = retriever.search(q, k=5)
best = rerank(q, docs)[:5]

# Right: wide recall, narrow precision
docs = retriever.search(q, k=50)  # recall stage
best = rerank(q, docs)[:5]  # precision stage
```

❌ Mistake 2: Mixing scores from different models/stages
✅ Correct: Compare only scores from the same reranker.

```python
# Wrong: add cosine similarity (0-1) to cross-encoder logit (-10..10)
final = cosine + ce_score

# Right: sort purely by reranker score, or normalise first (e.g. rank fusion)
final = ce_score
```

---

## 🧠 Tricky Interview Question
**Q**: "Your reranker improved NDCG offline, but users complain answers got worse. Why?"

**Answer**: Common causes: (1) the reranker was trained on web search, not your domain (tariff legal text), (2) chunks were truncated by the reranker's max input length (e.g. 512 tokens) so key clauses were cut, (3) the threshold removed all but one chunk, hurting multi-fact answers, (4) offline labels were relevance-only while users need completeness. Fix: evaluate on your own labelled set, chunk to fit the reranker window, keep K adaptive, and fine-tune or switch the reranker.

---

## ⚫ Interview Questions + Answers

Q1: What does a reranker do?
A1: It re-scores retrieved chunks with a stronger model and reorders them, keeping the most relevant.

Q2: Why not just use the best model for retrieval directly?
A2: Cross-style models are too slow to run on millions of chunks. Two stages: cheap recall first, expensive precision on a small set.

Q3: Bi-encoder vs cross-encoder?
A3: Bi-encoder embeds query and doc separately (fast, precomputable, less accurate). Cross-encoder reads query and doc together (slow, more accurate).

Q4: How do you choose N (candidates) and K (kept)?
A4: Choose N so recall@N is near 95 percent on your eval set (often 30-100). Choose K from the LLM context budget and answer needs (3-8). Measure latency; rerank cost grows linearly with N.

Q5: How would you design reranking for 200 QPS with p95 under 500 ms?
A5: Batch pairs per request, use a small cross-encoder on GPU or a hosted API, cap N at 30, truncate chunks to the model limit, cache results for hot queries, set a timeout with fallback to retrieval order, and autoscale the reranker service independently.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Top-1 accuracy matters (legal, tariff, medical)
- Corpus is large and embeddings return near-miss results
- You want to shrink prompt size

❌ Avoid when:
- Corpus is tiny and retrieval is already precise
- Very strict latency budget with no GPU or API option
- Queries are simple exact-match lookups (use keyword/filters)

---

## 📊 Visual Diagram
```
 Query ──► Vector/Hybrid Search ──► top-50 chunks   (fast, ~50ms, recall)
                                         │
                                         ▼
                              ┌────────────────────┐
                              │ Reranker (slower)  │  score(query, chunk)
                              └─────────┬──────────┘
                                        ▼
                         sorted best 5 (precision)
                                        ▼
                                   LLM prompt
```

---

## 💰 Cost Impact
- Reranking itself costs: Cohere per 1,000 searches (check current pricing), or GPU time for open-source cross-encoders; LLM-based rerank costs tokens.
- It SAVES LLM tokens: sending 4 chunks x 300 tokens = 1,200 instead of 10 x 300 = 3,000 input tokens (60 percent less).
- Optimise: rerank at most 30-50, truncate chunks, cache by (query, doc-id set), skip rerank when stage-1 top score is already confident.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reranker | Model that re-scores candidates | दोबारा score करने वाला model |
| Recall | Did we fetch the right chunk at all | सही chunk मिला या नहीं |
| Precision | How many fetched chunks are right | मिले chunks में कितने सही |
| Bi-encoder | Separate embeddings, fast | अलग-अलग embedding |
| Cross-encoder | Joint query+doc scoring | साथ में scoring |
| NDCG | Ranking quality metric | Ranking quality का मापदंड |

---

## ⚡ 3-Line Summary
English: Reranking re-scores a wide candidate set with a precise model and keeps the best few. It improves answer quality and cuts prompt tokens, at the price of added latency. Always keep a fallback to retrieval order.
Hindi: Reranking चौड़े candidate set को precise model से दोबारा score करता है और best कुछ रखता है। इससे answer quality बढ़ती है और prompt tokens घटते हैं, पर latency थोड़ी बढ़ती है। हमेशा retrieval order का fallback रखो।

---

## ➡️ Next Topic
**207. Cross-Encoder Reranking** — the most common open-source reranker: how it works, how to run it, and its speed limits.
