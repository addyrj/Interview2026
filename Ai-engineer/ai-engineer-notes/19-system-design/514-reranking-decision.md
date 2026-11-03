---

# 514. Reranking Decision
# हिंदी में: Reranking का फैसला

---

## 🔵 Simple Definition (English)
Reranking is a second step that re-scores the top candidates from first-stage retrieval using a stronger model (usually a cross-encoder that reads query and document together). The decision is whether the quality gain is worth the added latency and cost.

## 🔵 सरल परिभाषा (Hindi)
Reranking दूसरा step है जिसमें first-stage retrieval के top candidates को ज़्यादा मज़बूत model (आमतौर पर cross-encoder जो query और document साथ पढ़ता है) से दोबारा score किया जाता है। फैसला यह है कि quality का फायदा बढ़ी latency और cost के लायक है या नहीं।

---

## 🔴 Problem it Solves
Bi-encoder vector search is fast but coarse: query and chunk are embedded separately. The right chunk may sit at rank 12, and the LLM sees only the top 5. Reranking fixes ordering without sending more tokens to the LLM.

## 🔴 यह क्यों बना? (Hindi)
Bi-encoder vector search तेज़ पर मोटा होता है: query और chunk अलग-अलग embed होते हैं। सही chunk rank 12 पर रह सकता है और LLM सिर्फ top 5 देखता है। Reranking LLM को ज़्यादा tokens भेजे बिना क्रम सुधारता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Measure first: recall@5 vs recall@50 on your eval set
Step 2 → If recall@50 >> recall@5, ordering is the issue -> reranking can help
Step 3 → Stage 1: cheap retrieval returns ~30-100 candidates
Step 4 → Stage 2: cross-encoder / hosted rerank API scores each (query, chunk) pair
Step 5 → Keep top 3-5 and send to the LLM
Step 6 → Compare: quality gain vs +50-300 ms latency and extra cost
Step 7 → Keep reranking only if the gain justifies it (A/B on golden set)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → पहले recall@5 vs recall@50 मापो
Step 2 → recall@50 >> recall@5 है तो ordering की दिक्कत है → reranking मदद करेगा
Step 3 → Stage 1: सस्ता retrieval ~30-100 candidates देता है
Step 4 → Stage 2: cross-encoder / hosted rerank API हर (query, chunk) pair score करता है
Step 5 → Top 3-5 LLM को भेजो
Step 6 → Quality gain बनाम +50-300 ms latency और cost compare करो
Step 7 → Gain justify करे तभी रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: "Smartwatch with cellular calling" retrieves chapters on watches, phones and wearables. Vector search ranks watch chapter 91 first; the correct heading 8517.62 is at rank 9. A reranker reading the query with each note pushes the right note to rank 1, raising top-1 accuracy from 0.82 to 0.91 (illustrative).
**Amazon-style example**: Search results for "running shoes for flat feet": rerank the top 100 by deep relevance before showing 10.

## 🟡 Real Example Hindi mein
**Tariff System**: "Cellular calling वाली smartwatch" पर watches, phones, wearables के chapters आते हैं। Vector search watch chapter 91 को पहले रखता है; सही heading 8517.62 rank 9 पर है। Reranker query को हर note के साथ पढ़कर सही note को rank 1 पर लाता है; top-1 accuracy 0.82 से 0.91 (illustrative)।

---

## 💻 Code Example — Basic
```python
# Basic: two-stage ranking with a toy "cross-encoder" scorer (pure Python, offline)
def stage1(query: str, docs: list[str], n: int = 5) -> list[str]:  # cheap candidate generator
    q = set(query.lower().split())  # query words
    return sorted(docs, key=lambda d: len(q & set(d.lower().split())), reverse=True)[:n]  # word overlap


def toy_cross_score(query: str, doc: str) -> float:  # stand-in for a real cross-encoder
    q, d = query.lower().split(), doc.lower().split()  # tokens
    bonus = 2.0 if "cellular" in d and "cellular" in q else 0.0  # reads both together (toy rule)
    return len(set(q) & set(d)) + bonus  # score


docs = ["Watches chapter 91 wrist watches", "Telephone sets cellular network apparatus 8517",
        "Wearable accessories misc"]  # sample corpus
query = "smartwatch with cellular calling"  # query
cands = stage1(query, docs)  # stage 1
final = sorted(cands, key=lambda d: toy_cross_score(query, d), reverse=True)[:2]  # stage 2
print(final)  # cellular apparatus first
```

## 💻 Code Example — Advanced
```python
# Advanced: async reranker wrapper with timeout, skip rule, and fallback to stage-1 order
import asyncio  # async runtime
from typing import Protocol  # interface typing


class Reranker(Protocol):  # any reranker implements this
    async def score(self, query: str, docs: list[str]) -> list[float]: ...  # one score per doc


class MockReranker:  # offline stand-in; replace with a cross-encoder or a rerank API client
    async def score(self, query: str, docs: list[str]) -> list[float]:
        await asyncio.sleep(0.02)  # simulate 20 ms inference
        return [float(len(set(query.split()) & set(d.split()))) for d in docs]  # toy relevance


async def rerank(rr: Reranker, query: str, docs: list[str], top_n: int = 3,
                 timeout: float = 0.5, min_candidates: int = 4) -> list[str]:
    if len(docs) < min_candidates:  # too few to be worth reranking
        return docs[:top_n]  # skip: saves latency
    try:
        scores = await asyncio.wait_for(rr.score(query, docs), timeout)  # guarded call
    except (asyncio.TimeoutError, ConnectionError):  # reranker down or slow
        return docs[:top_n]  # fallback to stage-1 order
    order = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)  # sort indices by score
    return [docs[i] for i in order[:top_n]]  # best first


if __name__ == "__main__":
    ds = ["a b", "cellular phone note", "watch note", "other", "phone"]  # candidates
    print(asyncio.run(rerank(MockReranker(), "cellular phone", ds)))  # run
```

---

## 🟠 FastAPI Integration
Make the reranker a dependency with a feature flag so you can turn it off per route, per tenant, or when latency alarms fire.

```python
from fastapi import FastAPI  # app
from pydantic import BaseModel  # schema

app = FastAPI()  # app
RERANK_ENABLED = True  # feature flag (load from config)


class Ask(BaseModel):  # request
    question: str  # input


@app.post("/ask")  # route
async def ask(a: Ask) -> dict[str, object]:
    cands = [f"chunk-{i}" for i in range(30)]  # stage 1 results (stub)
    top = cands[:5]  # default: stage-1 order
    if RERANK_ENABLED:  # only if enabled
        top = list(reversed(cands))[:5]  # replace with a real reranker call
    return {"context": top, "reranked": RERANK_ENABLED}  # report what happened
```

---

## 🔗 LangChain / LangGraph Connection
LangChain's `ContextualCompressionRetriever` wraps a base retriever with a compressor such as a reranker (e.g. `CrossEncoderReranker` from langchain-community with a HuggingFace cross-encoder, or Cohere rerank integration).

```python
# Real API shape (needs a model/API key to run end to end):
# from langchain.retrievers import ContextualCompressionRetriever
# from langchain.retrievers.document_compressors import CrossEncoderReranker
# from langchain_community.cross_encoders import HuggingFaceCrossEncoder
# ce = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
# compressor = CrossEncoderReranker(model=ce, top_n=5)
# retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=base)
from langchain_core.documents import Document  # real type used throughout
print(Document(page_content="demo").page_content)  # offline sanity check
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reranking without measuring if ordering is the problem
✅ Correct: compare recall@5 and recall@50 first.
```python
# Wrong
add_reranker()  # assumed to help
# Right
if recall_at(50) - recall_at(5) > 0.15: add_reranker()  # evidence-based
```

❌ Mistake 2: Reranking too many candidates
✅ Correct: rerank 20-50, not 500; latency grows with candidates.
```python
# Wrong
rerank(query, retrieve(query, k=500))  # slow and costly
# Right
rerank(query, retrieve(query, k=30))[:5]  # bounded
```

---

## 🧠 Tricky Interview Question
**Q**: "Adding a reranker improved offline accuracy but production p95 latency breached the SLO. What are your options?"

**Answer**: Reduce candidates (50 to 20), use a smaller or distilled reranker or run it on GPU, batch pairs in one call, set a timeout with fallback to stage-1 order, rerank only when first-stage scores are ambiguous, cache results for repeated queries, and run retrieval and other steps in parallel. Verify each change against the golden set.

---

## ⚫ Interview Questions + Answers

Q1: Bi-encoder vs cross-encoder? (Easy)
A1: A bi-encoder embeds query and document separately (fast, precomputable). A cross-encoder reads both together (more accurate, slower, cannot precompute).

Q2: Why not use the cross-encoder on the whole corpus? (Easy)
A2: It would need a forward pass per query-document pair; far too slow at scale. Use it only on a shortlist.

Q3: When is reranking not worth it? (Medium)
A3: When recall@5 is already near recall@50, when latency budget is tight, or when the corpus is tiny.

Q4: LLM-as-reranker vs cross-encoder? (Medium)
A4: LLM reranking can be accurate and flexible but costs tokens and latency; cross-encoders are cheaper and faster for a fixed task.

Q5: How do you evaluate a reranker? (Hard)
A5: Labelled queries with relevant chunks; compare nDCG@k, MRR, recall@k before and after, plus end-to-end answer faithfulness, p95 latency and cost per query, ideally with an online A/B test.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Relevant chunk is found but ranked low
- Wrong-answer cost is high

❌ Avoid when:
- Strict latency budgets and good recall@5 already
- Very small candidate sets

---

## 📊 Visual Diagram
```
 query ─▶ Stage 1 retrieval (fast, 30 candidates)
                 │
                 ▼
        Cross-encoder rerank (slow, accurate)
                 │
        rank 9 ──▶ rank 1   (correct heading promoted)
                 ▼
        top 5 ─▶ LLM prompt
 fallback: timeout → keep stage-1 order
```

---

## 💰 Cost Impact
Reranking adds a model call per query: hosted rerank APIs usually charge per search or per document (check current pricing; illustrative here), and self-hosting needs GPU/CPU time. Benefit: fewer prompt tokens, because you can send 3-5 chunks instead of 10-15 (saving roughly 2,000-3,000 input tokens per query, illustrative).
Optimise: rerank only 20-30, cache, skip when scores are confident, use a small reranker, send fewer chunks to the LLM.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Reranker | Second-stage scorer | दूसरे चरण का scorer |
| Cross-encoder | Reads query+doc together | दोनों साथ पढ़ने वाला model |
| Bi-encoder | Embeds separately | अलग-अलग embed करने वाला |
| nDCG | Ranking quality metric | ranking गुणवत्ता metric |
| Candidate set | Shortlist from stage 1 | shortlist |
| Fallback | Use stage-1 order on failure | विफलता पर पुराना क्रम |

---

## ⚡ 3-Line Summary
English: Reranking re-scores a shortlist with a precise model to fix ordering.
Add it only when recall@50 is much higher than recall@5 and latency allows.
Bound candidates, set timeouts, and fall back to stage-1 order.
Hindi: Reranking shortlist को सटीक model से दोबारा score करके क्रम सुधारता है।
तभी जोड़ो जब recall@50, recall@5 से काफी ज़्यादा हो और latency चले।
Candidates सीमित रखो, timeout लगाओ, fail होने पर stage-1 क्रम इस्तेमाल करो।

---

## ➡️ Next Topic
**515. Caching Strategy** — avoiding repeated retrieval and LLM work entirely.
