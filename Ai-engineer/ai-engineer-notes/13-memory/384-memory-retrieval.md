---

# 384. Memory Retrieval
# हिंदी में: Memory Retrieval

---

## 🔵 Simple Definition (English)
Memory retrieval is choosing which stored memories to put in the prompt for the current question. Good retrieval scores each memory on relevance (similarity), recency, and importance, then returns the top few.

## 🔵 सरल परिभाषा (Hindi)
Memory retrieval का मतलब है current सवाल के लिए stored memories में से कौन सी prompt में जाएँ ये चुनना। अच्छा retrieval हर memory को relevance (similarity), recency और importance पर score करके top कुछ लौटाता है।

---

## 🔴 Problem it Solves
Similarity alone returns old, trivial or contradicting memories. Sending everything wastes tokens. Retrieval balances what is relevant, fresh and important.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ़ similarity पुरानी, मामूली या विरोधी memories लौटाती है। सब भेजना tokens बर्बाद करता है। Retrieval relevant, ताज़ा और ज़रूरी के बीच संतुलन बनाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Take the user query (optionally rewrite with chat context)
Step 2 → Candidate search: vector top-N (N = 20) + keyword/entity match
Step 3 → Filter by user_id, status (not deleted), type
Step 4 → Score = a*similarity + b*recency + c*importance
Step 5 → Rerank (optional cross-encoder / LLM)
Step 6 → Keep top-k within token budget (k = 3-5)
Step 7 → Format with dates and put into prompt
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User query लो (ज़रूरत हो तो chat context से rewrite)
Step 2 → Candidate search: vector top-N (N = 20) + keyword/entity match
Step 3 → user_id, status (deleted नहीं), type से filter
Step 4 → Score = a*similarity + b*recency + c*importance
Step 5 → Rerank (optional cross-encoder / LLM)
Step 6 → Token budget में top-k (k = 3-5) रखो
Step 7 → Dates के साथ format करके prompt में डालो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Query "what did we decide for the battery shipment?" Candidates: ruling (importance high, 2 days old), small talk about weather (old, low), an outdated origin note. Scoring surfaces the ruling first. **Zomato-style**: "order my usual" retrieves the most frequent and recent order, not an order from 2 years ago.

## 🟡 Real Example Hindi mein
**Tariff System**: Query "battery shipment पर क्या तय हुआ था?" Candidates: ruling (importance high, 2 दिन पुरानी), मौसम की बात (पुरानी, low), पुराना origin note। Scoring ruling को सबसे ऊपर लाती है। **Zomato-style**: "मेरा usual order करो" सबसे frequent और recent order लाता है, 2 साल पुराना नहीं।

---

## 💻 Code Example — Basic
```python
# Pure Python scoring: similarity + recency + importance. Runs offline.
import math                                                   # exp for decay

def sim(a: str, b: str) -> float:
    wa, wb = set(a.lower().split()), set(b.lower().split())   # word sets
    return len(wa & wb) / max(len(wa | wb), 1)                # Jaccard similarity

def score(query: str, m: dict) -> float:
    recency = math.exp(-m["age_days"] / 30)                   # 30-day decay
    return 0.6 * sim(query, m["text"]) + 0.2 * recency + 0.2 * m["importance"]

memories = [
    {"text": "ruling: battery shipment HS 8507.60 duty 20 percent", "age_days": 2, "importance": 1.0},
    {"text": "weather is nice today", "age_days": 90, "importance": 0.1},
    {"text": "battery origin China", "age_days": 60, "importance": 0.5},
]
q = "what was decided for battery shipment"
for m in sorted(memories, key=lambda m: score(q, m), reverse=True)[:2]:
    print(round(score(q, m), 3), m["text"])                   # top 2 with scores
```

## 💻 Code Example — Advanced
```python
# Production: async hybrid retrieval (vector + keyword) with weighted score, filter, error handling.
import asyncio                                                # gather
import logging                                                # logs
import math                                                   # decay
import time                                                   # timestamps
from dataclasses import dataclass                             # data class
from typing import Protocol                                   # interfaces

log = logging.getLogger("retrieval")                          # logger

@dataclass
class Memory:
    id: str                                                   # memory id
    user_id: str                                              # owner
    text: str                                                 # content
    created: float                                            # unix time
    importance: float = 0.5                                   # 0..1

class Backend(Protocol):
    async def vector_search(self, user_id: str, query: str, n: int) -> list[tuple[Memory, float]]: ...
    async def keyword_search(self, user_id: str, query: str, n: int) -> list[Memory]: ...

async def retrieve(be: Backend, user_id: str, query: str, k: int = 4,
                   w_sim: float = 0.6, w_rec: float = 0.2, w_imp: float = 0.2) -> list[Memory]:
    vec, kw = await asyncio.gather(                           # run both searches together
        be.vector_search(user_id, query, 20),
        be.keyword_search(user_id, query, 20),
        return_exceptions=True)                               # one failure should not kill both
    cands: dict[str, tuple[Memory, float]] = {}               # id -> (memory, similarity)
    if isinstance(vec, list):
        for m, s in vec:
            cands[m.id] = (m, s)                              # similarity from vectors
    else:
        log.warning("vector search failed: %s", vec)
    if isinstance(kw, list):
        for m in kw:
            old = cands.get(m.id)
            cands[m.id] = (m, max(old[1] if old else 0.0, 0.5))   # keyword hit gets a floor score
    else:
        log.warning("keyword search failed: %s", kw)
    now = time.time()                                         # current time
    def total(item: tuple[Memory, float]) -> float:
        m, s = item
        age_days = (now - m.created) / 86_400                 # age in days
        return w_sim * s + w_rec * math.exp(-age_days / 30) + w_imp * m.importance
    ranked = sorted(cands.values(), key=total, reverse=True)  # best first
    return [m for m, _ in ranked[:k]]                         # top-k
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Query                            # app + query params

app = FastAPI()                                               # app
backend: Backend = ...  # type: ignore                        # inject your Qdrant/pgvector backend

@app.get("/memories/search")
async def search(user_id: str, q: str, k: int = Query(4, le=10)) -> list[dict]:
    mems = await retrieve(backend, user_id, q, k)             # hybrid retrieval
    return [{"id": m.id, "text": m.text} for m in mems]       # JSON response
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_core.retrievers import BaseRetriever           # retriever interface
from langchain_core.documents import Document                 # document type
from langchain_core.callbacks import CallbackManagerForRetrieverRun

class MemoryRetriever(BaseRetriever):
    user_id: str                                              # pydantic field
    k: int = 4

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        # sync wrapper: call your scoring here
        return [Document(page_content="ruling: HS 8507.60", metadata={"user_id": self.user_id})]

retriever = MemoryRetriever(user_id="u1")                     # use in any LCEL chain: retriever | prompt | llm
# LangGraph: the "recall" node calls retriever.invoke(state["question"]) and stores docs in state.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Similarity only
✅ Correct: blend recency and importance.

```python
# Wrong
sorted(mems, key=lambda m: m.sim)
# Right
sorted(mems, key=lambda m: .6*m.sim + .2*m.recency + .2*m.importance)
```

❌ Mistake 2: Forgetting the user filter
✅ Correct: filter first; it is also a privacy requirement.

```python
# Wrong
search(query)
# Right
search(query, filter={"user_id": uid})
```

---

## 🧠 Tricky Interview Question
**Q**: "The user asks 'and what about the second one?' and retrieval returns nothing useful. Why?"

**Answer**: The query is not self-contained, so its embedding is meaningless. Rewrite it with recent turns into a standalone query ("duty for the second battery shipment") before retrieval, or retrieve by conversation-state entities.

---

## ⚫ Interview Questions + Answers

Q1: What signals rank memories? (Easy)
A1: Relevance, recency and importance.

Q2: What is k and why small? (Easy)
A2: Number of memories injected; small keeps prompts cheap and focused.

Q3: Why hybrid search? (Medium)
A3: Vectors catch meaning, keywords catch exact codes/names; combining raises recall.

Q4: What does reranking add? (Medium)
A4: A cross-encoder scores query-memory pairs jointly, improving precision on the top candidates.

Q5: How do you evaluate memory retrieval? (Hard)
A5: Build a labelled set (query -> must-have memories), measure recall@k and MRR, add tests for stale/conflicting memories, and track end-to-end answer correctness with Ragas-like metrics.

---

## 🔷 When to Use + When Not to Use
✅ Use scoring + hybrid when:
- Large memory stores
- Mixed exact and fuzzy queries

❌ Keep simple when:
- Few memories (send all)

---

## 📊 Visual Diagram
```
 query ─► rewrite ─► ┌ vector top-20 ┐
                     └ keyword top-20┘ ─► merge ─► filter(user)
                                         ─► score(sim,recency,importance)
                                         ─► rerank ─► top-k ─► prompt
```

---

## 💰 Cost Impact
Retrieval costs one query embedding (about $0.000001) and DB time. The saving is in prompt tokens: k=4 memories of 40 tokens = 160 tokens. A cross-encoder rerank adds latency (20-100 ms), an LLM rerank adds tokens - use only if needed. Cache embeddings for repeated queries.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Recall@k | Share of needed items in top-k | top-k में ज़रूरी items का हिस्सा |
| Hybrid search | Vector + keyword | vector + keyword खोज |
| Rerank | Re-order candidates | candidates को दोबारा क्रम देना |
| Recency decay | Older = lower score | पुराना = कम score |
| Query rewrite | Make query standalone | query को पूरा बनाना |

---

## ⚡ 3-Line Summary
English: Retrieve memories by blending similarity, recency and importance. Use hybrid search and filter by user. Rewrite vague queries first.
Hindi: Similarity, recency और importance मिलाकर memories retrieve करो। Hybrid search और user filter इस्तेमाल करो। अस्पष्ट queries पहले rewrite करो।

---

## ➡️ Next Topic
**385. Memory Update Strategy** - when to add, update, merge or forget memories.
