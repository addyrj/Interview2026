---

# 208. Cohere Reranker
# हिंदी में: Cohere Reranker

---

## 🔵 Simple Definition (English)
Cohere Rerank is a hosted API. You send a query and a list of documents; it returns them re-ordered with a relevance score between 0 and 1. No model hosting needed, and it supports many languages including Hindi.

## 🔵 सरल परिभाषा (Hindi)
Cohere Rerank एक hosted API है। आप query और documents की list भेजते हैं; यह उन्हें 0 से 1 के relevance score के साथ दोबारा order करके लौटाता है। Model host करने की ज़रूरत नहीं और Hindi सहित कई languages support होती हैं।

---

## 🔴 Problem it Solves
Running your own cross-encoder means GPUs, model updates, scaling and monitoring. Small teams want better ranking with a few lines of code. Cohere Rerank gives production-grade cross-encoder quality as a service, and it drops into an existing pipeline without changing the vector DB.

## 🔴 यह क्यों बना? (Hindi)
अपना cross-encoder चलाने का मतलब GPU, model updates, scaling और monitoring है। छोटी teams कुछ lines में बेहतर ranking चाहती हैं। Cohere Rerank service के रूप में production-grade quality देता है और मौजूदा pipeline में बिना vector DB बदले fit हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Retrieve top-N chunks from your vector DB (N up to ~100)
Step 2 → Call co.rerank(model, query, documents, top_n)
Step 3 → Cohere scores every (query, document) pair with its rerank model
Step 4 → Response: results sorted by relevance_score, each with original index
Step 5 → Map result.index back to your own chunk objects (keep metadata)
Step 6 → Apply a score threshold, build the prompt with the top chunks
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Vector DB से top-N chunks लाओ (N ~100 तक)
Step 2 → co.rerank(model, query, documents, top_n) call करो
Step 3 → Cohere हर (query, document) pair को score करता है
Step 4 → Response: relevance_score से sorted results, हर एक का original index
Step 5 → result.index से अपने chunk objects (metadata के साथ) map करो
Step 6 → Score threshold लगाओ और top chunks से prompt बनाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: Hindi-speaking officers type "मोबाइल चार्जर पर कितनी ड्यूटी है". Stage 1 returns 40 chunks from an English tariff schedule plus Hindi circulars. A multilingual Cohere rerank model (such as `rerank-multilingual-v3.0`) scores across languages and puts the charger chapter first. **Zomato**: rerank support-FAQ answers for a customer message. **Amazon**: rerank return-policy passages for "can I return opened headphones".

## 🟡 Real Example Hindi mein
**Tariff System**: Hindi बोलने वाले officers "मोबाइल चार्जर पर कितनी ड्यूटी है" टाइप करते हैं। Stage 1 से English tariff schedule और Hindi circulars के 40 chunks आते हैं। Multilingual Cohere rerank model (जैसे `rerank-multilingual-v3.0`) languages के पार score करके charger chapter को पहले रखता है। **Zomato**: customer message के लिए FAQ answers rerank। **Amazon**: "खुले headphones वापस हो सकते हैं?" के लिए return-policy passages।

---

## 💻 Code Example — Basic
```python
# Basic: call Cohere rerank if a key exists, otherwise use an offline mock so it always runs.
import os  # read env vars
from dataclasses import dataclass  # small result object
from typing import List  # type hints


@dataclass
class RerankHit:
    index: int  # position in the original list
    score: float  # relevance 0..1


def mock_rerank(query: str, docs: List[str], top_n: int) -> List[RerankHit]:
    """Offline stand-in that mimics Cohere's response shape."""
    q = set(query.lower().split())  # query words
    hits = [RerankHit(i, len(q & set(d.lower().split())) / max(len(q), 1)) for i, d in enumerate(docs)]  # overlap score
    hits.sort(key=lambda h: h.score, reverse=True)  # best first
    return hits[:top_n]  # keep top_n


def rerank(query: str, docs: List[str], top_n: int = 2) -> List[RerankHit]:
    """Use real Cohere when COHERE_API_KEY is set, else the mock."""
    key = os.getenv("COHERE_API_KEY")  # may be None
    if not key:  # no key -> offline
        return mock_rerank(query, docs, top_n)  # mock
    import cohere  # pip install cohere (only imported when needed)
    co = cohere.ClientV2(api_key=key)  # v2 client
    resp = co.rerank(model="rerank-v3.5", query=query, documents=docs, top_n=top_n)  # API call
    return [RerankHit(r.index, r.relevance_score) for r in resp.results]  # normalise shape


if __name__ == "__main__":
    docs = ["Mobile phone chargers HS 8504 duty", "Laptop bags duty", "Power adapters HS 8504 notes"]  # candidates
    for h in rerank("mobile charger duty", docs):  # run
        print(h.index, round(h.score, 2), docs[h.index])  # show result
```

## 💻 Code Example — Advanced
```python
# Production: async Cohere client, retries, timeout, threshold and fallback to retrieval order.
import asyncio  # async tools
import logging  # logs
import os  # env
from dataclasses import dataclass  # container

import cohere  # official SDK

logger = logging.getLogger("cohere_rerank")  # logger


@dataclass(frozen=True)
class Chunk:
    id: str  # chunk id
    text: str  # chunk text
    meta: dict  # source, page etc.


class CohereReranker:
    def __init__(self, model: str = "rerank-v3.5", timeout_s: float = 3.0, min_score: float = 0.1) -> None:
        self.client = cohere.AsyncClientV2(api_key=os.environ["COHERE_API_KEY"])  # async client
        self.model = model  # rerank model name
        self.timeout_s = timeout_s  # max wait
        self.min_score = min_score  # threshold

    async def rerank(self, query: str, chunks: list[Chunk], top_n: int = 5) -> list[tuple[Chunk, float]]:
        if not chunks:  # empty input
            return []  # nothing to rerank
        docs = [c.text for c in chunks]  # API takes plain strings
        for attempt in range(3):  # simple retry loop
            try:  # call can fail (rate limit, network)
                resp = await asyncio.wait_for(
                    self.client.rerank(model=self.model, query=query, documents=docs, top_n=top_n),  # request
                    timeout=self.timeout_s,  # timeout
                )
                out = [(chunks[r.index], r.relevance_score) for r in resp.results]  # map back by index
                return [(c, s) for c, s in out if s >= self.min_score]  # drop weak
            except Exception as exc:  # any failure
                logger.warning("rerank attempt %d failed: %s", attempt + 1, exc)  # log
                await asyncio.sleep(0.5 * 2 ** attempt)  # exponential backoff
        logger.error("rerank gave up, using retrieval order")  # final failure
        return [(c, 0.0) for c in chunks[:top_n]]  # graceful fallback
```

---

## 🟠 FastAPI Integration
Create the reranker once and reuse the HTTP connection pool. Keep chunk metadata so the answer can cite sources.

```python
from fastapi import FastAPI  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app
reranker = CohereReranker()  # one shared instance


class Q(BaseModel):
    query: str  # question
    top_n: int = 4  # chunks to keep


@app.post("/retrieve")  # POST /retrieve
async def retrieve(q: Q) -> list[dict]:
    candidates = [Chunk("c1", "Mobile chargers HS 8504 ...", {"page": 12})]  # stand-in for vector search top-50
    ranked = await reranker.rerank(q.query, candidates, q.top_n)  # rerank
    return [{"id": c.id, "text": c.text, "score": s, "meta": c.meta} for c, s in ranked]  # API output
```

---

## 🔗 LangChain / LangGraph Connection
Package `langchain-cohere` provides `CohereRerank`, a document compressor.

```python
from langchain.retrievers import ContextualCompressionRetriever  # wrapper
from langchain_cohere import CohereRerank  # compressor

# compressor = CohereRerank(model="rerank-v3.5", top_n=5)  # needs COHERE_API_KEY env
# retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=base_retriever)
# docs = await retriever.ainvoke("mobile charger duty")  # reranked Documents
# In LangGraph: put this retriever call in the `retrieve` node; no other change needed.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the English-only model for Hindi content
✅ Correct: Pick a multilingual rerank model for mixed-language corpora.

```python
# Wrong: English model on Hindi circulars
co.rerank(model="rerank-english-v3.0", query=q, documents=docs)

# Right: multilingual (or the current v3.5 which is multilingual)
co.rerank(model="rerank-multilingual-v3.0", query=q, documents=docs)
```

❌ Mistake 2: Sending huge or too many documents
✅ Correct: Chunk text and limit N; long documents get truncated and cost more.

```python
# Wrong: 1000 full pages
resp = co.rerank(model="rerank-v3.5", query=q, documents=all_pages)

# Right: top-50 chunks only
resp = co.rerank(model="rerank-v3.5", query=q, documents=top50_chunks, top_n=5)
```

---

## 🧠 Tricky Interview Question
**Q**: "Cohere returns relevance_score 0.92 for the top chunk and 0.05 for the second. Should you always send only chunks above, say, 0.5?"

**Answer**: Not blindly. Scores are only comparable within the same query and model; they are not calibrated probabilities across queries. A fixed 0.5 threshold may return zero chunks for a hard query. Better: always keep at least 1-2 chunks, use a relative cut (for example keep chunks within a margin of the top score), tune the threshold on your labelled data, and when the top score is very low, answer "not found" instead of hallucinating.

---

## ⚫ Interview Questions + Answers

Q1: What does Cohere Rerank take as input?
A1: A query, a list of documents (strings), a model name, and optionally `top_n`.

Q2: What does it return?
A2: A list of results, each with `index` (position in your input) and `relevance_score`, sorted best first.

Q3: Where does it sit in a RAG pipeline?
A3: After vector/hybrid retrieval and before prompt building.

Q4: Hosted reranker vs self-hosted cross-encoder trade-offs?
A4: Hosted: zero ops, good multilingual quality, per-search fee, data leaves your network, rate limits. Self-hosted: fixed infra cost, data stays private, tunable and fine-tunable, but you maintain GPUs and scaling.

Q5: How do you make a Cohere-dependent pipeline resilient?
A5: Timeouts, bounded retries with backoff, circuit breaker, fallback to stage-1 order (or a local small cross-encoder), caching on (query, doc-ids), monitoring score distribution to detect drift, and PII checks before sending text to a third party.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want quick quality gains with no infra
- Multilingual content (Hindi + English)
- Moderate traffic and acceptable per-request cost

❌ Avoid when:
- Data cannot leave your environment
- Very high QPS where per-search pricing is too costly
- Ultra-low latency (extra network hop)

---

## 📊 Visual Diagram
```
 Vector DB ──top-50──►  Your API  ──HTTPS──►  Cohere /rerank
                          ▲                        │
                          │   [{index:7, score:.93},│
                          │    {index:2, score:.71}]│
                          └─────────────────────────┘
                          map index → chunk + metadata
                                  ▼
                          top-5 → LLM prompt
```

---

## 💰 Cost Impact
- Billed per search (a search = one query with up to 100 documents; longer docs count as several). Check Cohere's pricing page for current rates.
- Saves LLM spend: fewer, better chunks. Example: cutting 10 chunks to 4 saves ~1,800 input tokens per query on gpt-4o-mini.
- Optimise: N of 30-50, cache repeated queries, skip rerank for high-confidence retrieval, keep chunks short.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Rerank API | Hosted reordering service | Hosted reordering सेवा |
| relevance_score | 0-1 match score | 0-1 match score |
| top_n | How many results to return | कितने results चाहिए |
| Multilingual model | Works across languages | कई भाषाओं वाला model |
| Backoff | Wait longer between retries | Retry के बीच बढ़ता इंतज़ार |

---

## ⚡ 3-Line Summary
English: Cohere Rerank is a hosted API that reorders retrieved chunks with a relevance score. It is easy to add, multilingual, and saves LLM tokens. Add timeouts, retries and a fallback for production.
Hindi: Cohere Rerank एक hosted API है जो retrieved chunks को relevance score से दोबारा order करता है। यह जोड़ना आसान है, multilingual है और LLM tokens बचाता है। Production के लिए timeout, retry और fallback रखो।

---

## ➡️ Next Topic
**209. ColBERT Reranking** — late interaction: token-level matching that sits between bi-encoders and cross-encoders.
