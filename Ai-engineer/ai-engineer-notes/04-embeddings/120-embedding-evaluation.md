---

# 120. Embedding Evaluation — Complete Guide
# हिंदी में: Embedding Evaluation — पूरी Guide

---

## 🔵 Simple Definition (English)
Embedding evaluation measures how well an embedding model (plus chunking and index) finds the right documents for real queries. You build a labelled set of queries with their correct documents and compute metrics such as recall@k, precision@k, MRR, and nDCG.

## 🔵 सरल परिभाषा (Hindi)
Embedding evaluation नापता है कि embedding model (chunking और index के साथ) real queries के लिए सही documents कितनी अच्छी तरह ढूँढता है। आप queries और उनके सही documents का labelled set बनाते हैं और recall@k, precision@k, MRR, nDCG जैसे metrics निकालते हैं।

---

## 🔴 Problem it Solves
Without evaluation, model choice is guesswork: leaderboard scores (MTEB) do not reflect your domain, and "it looks good in the demo" hides failures. Evaluation lets you compare models, chunk sizes, dimensions, and indexes with numbers, catch regressions, and justify cost decisions.

## 🔴 यह क्यों बना? (Hindi)
Evaluation के बिना model चुनना अंदाज़ा है: leaderboard scores (MTEB) आपके domain को नहीं दिखाते, और "demo में अच्छा दिखता है" failures छुपा देता है। Evaluation से models, chunk sizes, dimensions और indexes की numbers से तुलना होती है, regressions पकड़ी जाती हैं और cost के फैसले justify होते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Collect 100 to 500 real queries (from logs or experts)
Step 2 → Label the relevant document(s) for each query (qrels)
          (or generate synthetic queries from chunks with an LLM, then review)
Step 3 → Embed corpus and queries with the candidate configuration
Step 4 → Retrieve top-k for each query
Step 5 → Compute metrics:
          Recall@k  = found relevant / all relevant
          Hit@k     = at least one relevant in top-k
          MRR       = mean of 1 / rank of first relevant
          nDCG@k    = rank-aware gain (graded relevance)
Step 6 → Compare configs; check per-segment (language, query type)
Step 7 → Inspect failures manually (what did we retrieve instead?)
Step 8 → Freeze the eval set; run it in CI on every change
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → 100-500 real queries इकट्ठा करो (logs या experts से)
Step 2 → हर query के सही document(s) label करो (qrels)
          (या LLM से synthetic queries बनाकर review करो)
Step 3 → Candidate configuration से corpus और queries embed करो
Step 4 → हर query के लिए top-k retrieve करो
Step 5 → Metrics निकालो: Recall@k, Hit@k, MRR, nDCG@k
Step 6 → Configs compare करो; segment (भाषा, query type) के अनुसार भी देखो
Step 7 → Failures हाथ से देखो (सही की जगह क्या मिला?)
Step 8 → Eval set freeze करो; हर बदलाव पर CI में चलाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: 300 historical declarations with officer-confirmed HS codes form the eval set. Metric: Hit@5 on the correct 6-digit HS code. Results: small 0.88, large 0.91, large at 1024 d 0.90, small + reranker 0.94. Decision: small + reranker (cheaper than large, better quality). Per-language breakdown shows Hindi queries at 0.79, which triggers a multilingual model trial.

**Zomato-style**: Click logs (query to clicked dish) used as weak labels.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer-confirmed HS codes वाली 300 historical declarations eval set बनाती हैं। Metric: सही 6-digit HS code पर Hit@5। Results: small 0.88, large 0.91, large (1024 d) 0.90, small + reranker 0.94। Decision: small + reranker (large से सस्ता, quality बेहतर)। भाषा के हिसाब से देखने पर Hindi queries 0.79 पर हैं, जिससे multilingual model का trial शुरू होता है।

**Zomato-style**: Click logs (query से clicked dish) weak labels की तरह।

(ऊपर के numbers उदाहरण हैं।)

---

## 💻 Code Example — Basic
```python
# Retrieval metrics in pure Python (runs offline)
import math


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Share of relevant docs found in the top-k."""
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def hit_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """1 if any relevant doc is in the top-k."""
    return 1.0 if set(retrieved[:k]) & relevant else 0.0


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    """1 / rank of the first relevant doc (0 if none)."""
    for i, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Binary-relevance nDCG."""
    dcg = sum(1.0 / math.log2(i + 1) for i, d in enumerate(retrieved[:k], start=1) if d in relevant)
    ideal = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


results = {"q1": ["d3", "d1", "d9"], "q2": ["d7", "d8", "d2"]}
truth = {"q1": {"d1"}, "q2": {"d2", "d5"}}
for k in (1, 3):
    r = sum(recall_at_k(results[q], truth[q], k) for q in truth) / len(truth)
    print(f"recall@{k} = {r:.3f}")
print("MRR =", sum(reciprocal_rank(results[q], truth[q]) for q in truth) / len(truth))
print("nDCG@3 =", round(sum(ndcg_at_k(results[q], truth[q], 3) for q in truth) / len(truth), 3))
```

## 💻 Code Example — Advanced
```python
# Evaluation harness: compare embedding configs on a labelled set, async, with per-segment report
import asyncio
from dataclasses import dataclass
import numpy as np
from openai import AsyncOpenAI

client = AsyncOpenAI()


@dataclass
class Example:
    query: str
    relevant: set[int]          # indexes of relevant docs
    segment: str = "all"        # e.g. language or query type


async def embed(model: str, texts: list[str], dims: int | None = None) -> np.ndarray:
    kwargs: dict = {"model": model, "input": texts}
    if dims:
        kwargs["dimensions"] = dims
    try:
        r = await client.embeddings.create(**kwargs)
    except Exception as exc:
        raise RuntimeError(f"embed failed for {model}: {exc}") from exc
    v = np.asarray([d.embedding for d in sorted(r.data, key=lambda d: d.index)], dtype=np.float32)
    return v / np.linalg.norm(v, axis=1, keepdims=True)


async def evaluate(model: str, docs: list[str], examples: list[Example],
                   dims: int | None = None, k: int = 5) -> dict[str, float]:
    d, q = await asyncio.gather(embed(model, docs, dims), embed(model, [e.query for e in examples], dims))
    ranks = np.argsort(-(q @ d.T), axis=1)[:, :k]
    by_seg: dict[str, list[float]] = {}
    for ex, row in zip(examples, ranks):
        hit = 1.0 if set(map(int, row)) & ex.relevant else 0.0     # hit@k
        by_seg.setdefault(ex.segment, []).append(hit)
        by_seg.setdefault("ALL", []).append(hit)
    return {seg: round(float(np.mean(v)), 3) for seg, v in by_seg.items()}


async def main() -> None:
    docs = ["Headphones and earphones", "Coffee, not roasted", "Mobile phones", "Wheat flour"]
    exs = [Example("wireless earbuds", {0}, "en"), Example("arabica beans", {1}, "en"),
           Example("smartphone", {2}, "en")]
    for model, dims in [("text-embedding-3-small", None), ("text-embedding-3-large", 1024)]:
        print(model, dims, await evaluate(model, docs, exs, dims, k=1))


if __name__ == "__main__":
    asyncio.run(main())                                          # needs OPENAI_API_KEY
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()


class EvalItem(BaseModel):
    retrieved: list[str]                        # doc ids in ranked order
    relevant: list[str] = Field(min_length=1)   # ground truth ids


class EvalReq(BaseModel):
    items: list[EvalItem] = Field(min_length=1)
    k: int = Field(default=5, ge=1, le=100)


@app.post("/eval/retrieval")
async def eval_retrieval(req: EvalReq) -> dict[str, float]:
    hits, rr = [], []
    for it in req.items:
        rel = set(it.relevant)
        hits.append(1.0 if set(it.retrieved[:req.k]) & rel else 0.0)
        rr.append(next((1 / (i + 1) for i, d in enumerate(it.retrieved) if d in rel), 0.0))
    return {f"hit@{req.k}": sum(hits) / len(hits), "mrr": sum(rr) / len(rr)}
```
Wire this endpoint into a CI job or a dashboard so each deployment reports retrieval quality.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.vectorstores import VectorStore

def hit_rate(store: VectorStore, examples: list[tuple[str, str]], k: int = 5) -> float:
    """examples = (query, expected_source_id) pairs; documents carry metadata['id']."""
    hits = 0
    for query, expected in examples:
        docs = store.similarity_search(query, k=k)
        hits += any(d.metadata.get("id") == expected for d in docs)
    return hits / len(examples)
```
Tools such as LangSmith datasets/evaluators, Ragas (context recall/precision), and the MTEB library automate parts of this. In LangGraph, run the eval set against the retrieve node alone (not the full graph) to isolate retrieval quality from generation quality.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Evaluating on a few hand-picked queries
✅ Correct: 100+ diverse queries, including hard and multilingual ones.

```python
# Wrong: 5 easy queries -> "looks great"
# Right: 300 labelled queries with per-segment metrics
```

❌ Mistake 2: Testing on the same data used to tune (or to fine-tune)
✅ Correct: Hold out a test set.

❌ Mistake 3: Judging only the final LLM answer
✅ Correct: Evaluate retrieval separately (recall@k), then end-to-end; otherwise you cannot tell which part failed.

---

## 🧠 Tricky Interview Question

**Q**: "Recall@10 improved from 0.85 to 0.92 after switching models, but users say answers got worse. How?"

**Answer**: Recall@10 only says the right chunk is somewhere in the top 10; the LLM may use only the top 3, or the new model might rank noisy chunks above the right one (MRR/nDCG fell), or the labels may not match real user intent. Also check the end-to-end answer quality, chunk ordering, and the "lost in the middle" effect. Track MRR, nDCG, and recall@3 together with answer faithfulness.

---

## ⚫ Interview Questions + Answers

Q1: What is recall@k?
A1: The fraction of all relevant documents that appear in the top-k results.

Q2: What is MRR?
A2: Mean reciprocal rank: average of 1/rank of the first relevant result across queries.

Q3: How do you get labels cheaply?
A3: Use logs (clicks, accepted answers), expert review, or LLM-generated synthetic questions per chunk, then manually spot-check a sample.

Q4: Why evaluate per segment?
A4: Averages hide failures; a model may be strong in English and weak in Hindi or on long queries.

Q5: How do you detect regression in production?
A5: Keep a frozen golden set run in CI; monitor online signals (click-through, thumbs down, empty-result rate); sample live queries for periodic labelling; alert when metrics fall below thresholds; compare against embedding drift checks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Choosing models, chunk sizes, dimensions, index settings
- Before and after every embedding or pipeline change

❌ Avoid relying only on:
- Public leaderboards
- Tiny, unrepresentative samples

---

## 📊 Visual Diagram
```
 labelled set: (query, relevant docs)
        │
        ▼ embed + search (top-k)
 ┌───────────────┐
 │ retrieved ids │ ──► recall@k   hit@k   MRR   nDCG
 └───────────────┘
        │
        ▼ compare configs: small / large / dims / chunk size / reranker
        ▼ choose by quality vs cost; run in CI
```

---

## 💰 Cost Impact
Evaluation is cheap: 500 queries x 20 tokens plus a 10,000-chunk corpus (3M tokens) costs about $0.06 per model with small, so you can test several configurations. Synthetic question generation with an LLM costs more (for 10,000 chunks and gpt-4o-mini, roughly a few dollars, depending on prompt size). The savings are large: a measured decision (for example small instead of large) avoids paying 6.5x for no gain.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Recall@k | Relevant found in top-k | Top-k में मिले relevant docs |
| Precision@k | Share of top-k that is relevant | Top-k में relevant का अनुपात |
| MRR | Mean reciprocal rank | पहले सही result की rank का average |
| nDCG | Rank-weighted gain | Rank के अनुसार gain |
| Qrels | Query to relevant doc labels | Query और सही docs के labels |
| Golden set | Frozen eval set | Frozen eval set |

---

## ⚡ 3-Line Summary
English: Evaluate embeddings with a labelled query set and metrics like recall@k, MRR, and nDCG. Compare models, dimensions and chunking by numbers, per segment. Freeze a golden set and run it on every change.
Hindi: Labelled query set और recall@k, MRR, nDCG जैसे metrics से embeddings evaluate करो। Models, dimensions और chunking की numbers से, segment-wise तुलना करो। Golden set freeze करो और हर बदलाव पर चलाओ।

---

## ➡️ Next Topic
**121. Semantic Search** - put embeddings to work: build the end-to-end search pipeline.
