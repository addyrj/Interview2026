
---

# 453. Semantic Cache with Qdrant
# हिंदी में: Qdrant के साथ Semantic Cache

---

## 🔵 Simple Definition (English)
A semantic cache stores past LLM answers together with the **embedding** of the question. A new question is embedded and searched in the vector store; if a stored question is similar enough (above a score threshold), we return the stored answer and skip the LLM call. Qdrant is an open-source vector database that is a good fit for this.

## 🔵 सरल परिभाषा (Hindi)
Semantic cache पुराने LLM answers को question के **embedding** के साथ store करता है। नया question embed करके vector store में search होता है; अगर कोई stored question काफ़ी similar है (score threshold से ऊपर), तो stored answer लौटा देते हैं और LLM call बच जाती है। Qdrant एक open-source vector database है जो इसके लिए अच्छा है।

---

## 🔴 Problem it Solves
An exact-match cache (Redis key = hash of prompt) misses "HS code for iPhone 15?" vs "iphone 15 hs code please". Users phrase the same question in many ways, so exact-match hit rate stays low (often 5-15%). Each miss costs tokens and 1-3 seconds. We need a cache that understands **meaning**, not just identical strings.

## 🔴 यह क्यों बना? (Hindi)
Exact-match cache में "HS code for iPhone 15?" और "iphone 15 hs code please" अलग keys बन जाती हैं, इसलिए hit rate कम रहता है। हर miss पर tokens और 1-3 second लगते हैं। हमें ऐसा cache चाहिए जो **meaning** समझे, सिर्फ़ identical string नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Incoming question → embedding model → vector (e.g. 1536 dims)
Step 2 → Search Qdrant collection "llm_cache" for nearest vector (cosine)
Step 3 → If top score >= threshold (e.g. 0.92) → HIT: return payload["answer"]
Step 4 → If below threshold → MISS: call the LLM
Step 5 → Upsert new point: vector + payload {question, answer, created_at}
Step 6 → TTL: periodically delete points older than N days (payload filter)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Question → embedding model → vector
Step 2 → Qdrant collection में सबसे नज़दीकी vector search (cosine)
Step 3 → Score >= threshold हो तो HIT: stored answer लौटाओ
Step 4 → कम हो तो MISS: LLM call करो
Step 5 → नया point upsert करो: vector + payload {question, answer, created_at}
Step 6 → पुराने points को TTL के बाद delete करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Thousands of importers ask "What is the HS code for lithium-ion power banks?" in different words. With a semantic cache at threshold 0.92, all paraphrases hit one stored answer. Danger: "HS code for lithium battery" vs "HS code for lithium battery **pack with device**" are close in vector space but have different codes, so the threshold and a metadata filter (country, HS version) matter a lot.
**Zomato-style**: "Is there a veg restaurant near me?" and "veg restaurants nearby" share one cached answer, but the cache must be keyed by city.

## 🟡 Real Example Hindi mein
**Tariff System**: कई importers "lithium-ion power bank का HS code?" अलग शब्दों में पूछते हैं। 0.92 threshold पर सब paraphrases एक ही stored answer पर hit करते हैं। ख़तरा: "lithium battery" और "lithium battery pack with device" vector में पास हैं पर codes अलग हैं, इसलिए threshold और metadata filter (country, HS version) ज़रूरी हैं।

---

## 💻 Code Example — Basic
```python
# Basic semantic cache: pure Python, in-memory, fake embeddings (runs offline)
import math                                   # for cosine similarity math
from collections import Counter               # to build bag-of-words vectors

def embed(text: str) -> Counter[str]:         # toy "embedding": word counts
    return Counter(text.lower().split())      # lowercase and split on spaces

def cosine(a: Counter[str], b: Counter[str]) -> float:   # cosine similarity
    dot = sum(a[w] * b[w] for w in a)         # dot product over shared words
    na = math.sqrt(sum(v * v for v in a.values()))        # length of vector a
    nb = math.sqrt(sum(v * v for v in b.values()))        # length of vector b
    return dot / (na * nb) if na and nb else 0.0          # avoid divide by zero

cache: list[tuple[Counter[str], str]] = []    # list of (vector, answer)
THRESHOLD = 0.7                               # toy threshold for toy vectors

def lookup(question: str) -> str | None:      # return cached answer or None
    q = embed(question)                       # embed the new question
    best_score, best_answer = 0.0, None       # track the best match so far
    for vec, answer in cache:                 # scan every cached entry
        score = cosine(q, vec)                # similarity to this entry
        if score > best_score:                # keep the highest score
            best_score, best_answer = score, answer
    return best_answer if best_score >= THRESHOLD else None  # apply threshold

cache.append((embed("hs code for iphone 15"), "8517.13"))     # seed the cache
print(lookup("what is hs code for iphone 15"))                # similar -> 8517.13
print(lookup("recipe for paneer"))                            # unrelated -> None
```

## 💻 Code Example — Advanced
```python
# Production: async Qdrant semantic cache with tenant filter, TTL and error handling
# pip install qdrant-client openai
import time                                                   # timestamps for TTL
import uuid                                                   # unique point ids
from typing import Optional                                   # optional types
from openai import AsyncOpenAI                                # async OpenAI client
from qdrant_client import AsyncQdrantClient, models           # async Qdrant client

COLLECTION = "llm_cache"                                      # collection name
DIM = 1536                                                    # text-embedding-3-small dims
THRESHOLD = 0.92                                              # similarity cut-off
TTL_SECONDS = 7 * 24 * 3600                                   # 7 day freshness

class QdrantSemanticCache:
    def __init__(self, url: str = "http://localhost:6333") -> None:
        self.qdrant = AsyncQdrantClient(url=url)              # connect to Qdrant
        self.oai = AsyncOpenAI()                              # embedding client

    async def setup(self) -> None:
        exists = await self.qdrant.collection_exists(COLLECTION)   # check first
        if not exists:                                        # create only once
            await self.qdrant.create_collection(
                collection_name=COLLECTION,
                vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE),
            )
            await self.qdrant.create_payload_index(           # fast tenant filter
                COLLECTION, field_name="tenant_id",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

    async def _embed(self, text: str) -> list[float]:
        resp = await self.oai.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding                         # list of floats

    async def get(self, question: str, tenant_id: str) -> Optional[str]:
        try:
            vec = await self._embed(question)                 # embed query
            res = await self.qdrant.query_points(             # nearest neighbour search
                collection_name=COLLECTION,
                query=vec,
                limit=1,                                      # only best match
                score_threshold=THRESHOLD,                    # server-side cut-off
                query_filter=models.Filter(must=[             # isolate tenant
                    models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id)),
                    models.FieldCondition(key="created_at",   # drop expired entries
                        range=models.Range(gte=time.time() - TTL_SECONDS)),
                ]),
            )
            return res.points[0].payload["answer"] if res.points else None
        except Exception:                                     # cache must never break the app
            return None                                       # treat any error as a miss

    async def put(self, question: str, answer: str, tenant_id: str) -> None:
        try:
            vec = await self._embed(question)                 # embed the question
            await self.qdrant.upsert(
                collection_name=COLLECTION,
                points=[models.PointStruct(
                    id=str(uuid.uuid4()), vector=vec,
                    payload={"question": question, "answer": answer,
                             "tenant_id": tenant_id, "created_at": time.time()},
                )],
            )
        except Exception:                                     # failing to write is not fatal
            pass
```

---

## 🟠 FastAPI Integration
Create the cache once in the lifespan, inject it, and check it before the LLM.

```python
from contextlib import asynccontextmanager                    # lifespan helper
from fastapi import FastAPI, Request                          # FastAPI basics
from pydantic import BaseModel                                # request schema
from openai import AsyncOpenAI                                # LLM client

llm = AsyncOpenAI()                                           # shared LLM client

class Ask(BaseModel):
    question: str                                             # user question
    tenant_id: str                                            # who is asking

@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = QdrantSemanticCache()                             # build cache once
    await cache.setup()                                       # ensure collection exists
    app.state.cache = cache                                   # share via app.state
    yield                                                     # app runs here

app = FastAPI(lifespan=lifespan)

@app.post("/classify")
async def classify(body: Ask, request: Request) -> dict:
    cache: QdrantSemanticCache = request.app.state.cache      # get the cache
    hit = await cache.get(body.question, body.tenant_id)      # 1) try the cache
    if hit is not None:
        return {"answer": hit, "cached": True}                # HIT: zero LLM tokens
    r = await llm.chat.completions.create(                    # 2) MISS: call LLM
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": body.question}],
        max_tokens=300,
    )
    answer = r.choices[0].message.content or ""               # extract text
    await cache.put(body.question, answer, body.tenant_id)    # 3) store for next time
    return {"answer": answer, "cached": False, "tokens": r.usage.total_tokens}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has a global `set_llm_cache`, and a `QdrantVectorStore` in `langchain-qdrant`. A simple pattern is a **cache node** at the start of a LangGraph graph: if hit, route straight to END.

```python
from langgraph.graph import StateGraph, END                   # graph builder
from typing import TypedDict                                  # state schema

class S(TypedDict, total=False):
    question: str; tenant_id: str; answer: str; cached: bool  # graph state

async def cache_node(state: S) -> S:
    hit = await cache.get(state["question"], state["tenant_id"])   # check Qdrant
    return {"answer": hit, "cached": True} if hit else {"cached": False}

async def llm_node(state: S) -> S:
    r = await llm.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role": "user", "content": state["question"]}])
    ans = r.choices[0].message.content or ""
    await cache.put(state["question"], ans, state["tenant_id"])    # write back
    return {"answer": ans}

g = StateGraph(S)
g.add_node("cache", cache_node); g.add_node("llm", llm_node)
g.set_entry_point("cache")
g.add_conditional_edges("cache", lambda s: END if s["cached"] else "llm")
g.add_edge("llm", END)
app_graph = g.compile()                                       # run with ainvoke(...)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: One threshold for everything, no filters
```python
# Wrong — different countries' tariff answers get mixed:
await qdrant.query_points(COLLECTION, query=vec, limit=1)

# Correct — filter by tenant/country/HS-version and use a score threshold:
await qdrant.query_points(COLLECTION, query=vec, limit=1, score_threshold=0.92,
    query_filter=models.Filter(must=[models.FieldCondition(
        key="country", match=models.MatchValue(value="IN"))]))
```

❌ Mistake 2: Crashing when the cache is down
```python
# Wrong — Qdrant outage = whole API down:
hit = await cache.get(q, t)

# Correct — treat errors as a miss (see get() above with try/except)
```

❌ Mistake 3: Never expiring entries
```python
# Wrong — stale tariff rates served forever
# Correct — store created_at and filter by range, or delete old points in a cron job
```

---

## 🧠 Tricky Interview Question
**Q**: "Your semantic cache hit rate is 60% but users complain about wrong answers. Do you lower or raise the threshold?"

**Answer**: Raise it (stricter) and add filters. Wrong answers from a cache are **false positives**: two questions that look similar but need different answers (e.g. different HS version or country). Measure with a labelled set: plot precision vs hit rate at several thresholds. Also cache only deterministic answers (temperature 0), add metadata filters, and consider a cheap reranker or exact-key check for entity values (numbers, product codes) before returning a hit.

---

## ⚫ Interview Questions + Answers

Q1: What is a semantic cache?
A1: A cache whose key is the embedding of the question. Similar questions return the same stored answer via vector similarity search.

Q2: Why Qdrant for caching?
A2: Fast ANN search, payload filtering (tenant, TTL), `score_threshold`, async client, easy self-hosting, and persistence. Redis with vector search is another valid option.

Q3: How do you choose the similarity threshold?
A3: Build a labelled set of question pairs (same intent / different intent). Compute scores, pick the threshold that gives the precision you need (e.g. 99%), then check the hit rate. It depends on the embedding model, so re-tune when you change it.

Q4: How do you handle expiry in Qdrant?
A4: Qdrant has no built-in TTL on points. Store `created_at` in the payload, filter by range at query time, and delete old points with `delete` + filter in a scheduled job.

Q5: (Hard) How do you prevent cache poisoning and cross-tenant leakage?
A5: Always include tenant_id in the filter (and index it), never cache answers produced from untrusted tool output, store only answers that passed output guardrails, authenticate writes, and keep per-tenant collections or a tenant-indexed payload for strong isolation.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many users ask paraphrased versions of the same FAQ-style questions
- Answers are stable for days (tariff lookups, policies, docs Q&A)
- LLM cost or latency is a major concern

❌ Avoid when:
- Answers depend on live data (stock, order status) or user-specific context
- Questions contain precise numbers/IDs where near-matches are wrong
- Traffic is low (embedding cost + complexity not worth it)

---

## 📊 Visual Diagram
```
 Question ──► Embed ──► Qdrant search (cosine, filter tenant, TTL)
                              │
              score >= 0.92 ? │
                 ┌────────────┴────────────┐
                YES                        NO
                 │                          │
          return cached answer         call LLM
          (0 LLM tokens, ~50 ms)            │
                                      upsert(vector+answer)
                                            │
                                      return answer
```

---

## 💰 Cost Impact
- Hit: one embedding call (about 20-50 tokens, very cheap) and no LLM tokens. Miss: embedding + full LLM cost, so a miss is slightly more expensive than no cache.
- Example (illustrative): 500 input + 200 output tokens on gpt-4o-mini is about $0.000195/query. At a 40% hit rate and 100K queries/day you save roughly $7.80/day; embedding cost is a small fraction of that.
- Optimise: tune threshold, normalise queries before embedding, cache only popular intents, use a small embedding model, keep payload small.
- Prices are illustrative; check current provider pricing.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Semantic cache | Cache keyed by meaning | अर्थ पर आधारित cache |
| Embedding | Vector representing text meaning | text का vector रूप |
| Cosine similarity | Angle-based closeness score | दो vectors की समानता |
| Score threshold | Minimum similarity for a hit | hit के लिए न्यूनतम score |
| Payload | Metadata stored with a point | point के साथ metadata |
| Upsert | Insert or update a point | जोड़ो या अपडेट करो |
| False positive hit | Wrong answer from a similar-looking question | ग़लत cache hit |

---

## ⚡ 3-Line Summary
English: A semantic cache embeds questions and reuses answers for similar ones via Qdrant search. Tune the threshold, filter by tenant and add expiry to avoid wrong or stale hits. It cuts both cost and latency for repeated intents.
Hindi: Semantic cache questions को embed करके Qdrant से similar questions के answers दोबारा use करता है। Threshold tune करो, tenant filter और expiry लगाओ ताकि ग़लत या पुराने hits न आएँ। यह repeated intents पर cost और latency दोनों घटाता है।

---

## ➡️ Next Topic
**454. Cost Savings from Caching** — how to calculate real savings (hit rate x cost per call) and the break-even point of a cache.
