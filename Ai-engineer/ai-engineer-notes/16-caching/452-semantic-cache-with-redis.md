---

# 452. Semantic Cache with Redis
# हिंदी में: Redis के साथ Semantic Cache

---

## 🔵 Simple Definition (English)
A semantic cache returns a stored LLM answer when a new question has the same meaning as an old one, even if the words differ. Redis can do this using its vector search (RediSearch / Redis Stack): store the question embedding with the answer, then run a KNN search and accept the nearest neighbour only if its distance is under a threshold.

## 🔵 सरल परिभाषा (Hindi)
Semantic cache तब stored LLM जवाब देता है जब नया सवाल पुराने सवाल के अर्थ में एक जैसा हो, भले शब्द अलग हों। Redis अपने vector search (RediSearch / Redis Stack) से यह कर सकता है: सवाल का embedding जवाब के साथ store करो, फिर KNN search चलाओ और सबसे पास वाला तभी लो जब उसकी distance threshold से कम हो।

---

## 🔴 Problem it Solves
- Exact-match caches miss "HS code for steel flask" when "steel bottle" is cached.
- Users rarely type identical text, so hit rates stay low (5-15 percent).
- Redis is already in many stacks, so using it for vectors avoids another database.

## 🔴 यह क्यों बना? (Hindi)
- Exact-match cache "steel flask का HS code" पर miss करता है जबकि "steel bottle" cached है।
- Users शायद ही एक जैसा text लिखते हैं, इसलिए hit rate कम रहती है (5-15 प्रतिशत)।
- कई stacks में Redis पहले से है, तो vectors के लिए अलग database नहीं चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a Redis search index with fields: tenant (TAG), answer (TEXT), embedding (VECTOR, COSINE, dim N)
Step 2 → Query arrives -> embed it (same embedding model every time)
Step 3 → FT.SEARCH with KNN 1 on embedding, filtered by tenant TAG
Step 4 → Redis returns nearest entry + cosine distance (0 = identical, 2 = opposite)
Step 5 → distance <= threshold (for example 0.12) -> HIT, return stored answer
Step 6 → Else MISS -> call LLM -> store HASH with embedding bytes + answer + EXPIRE
Step 7 → Tune threshold with labelled pairs; monitor false hits
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Redis search index बनाओ: tenant (TAG), answer (TEXT), embedding (VECTOR, COSINE, dim N)
Step 2 → Query आई -> embed करो (हर बार वही embedding model)
Step 3 → embedding पर KNN 1 के साथ FT.SEARCH, tenant TAG से filter
Step 4 → Redis सबसे पास की entry + cosine distance देता है (0 = बिल्कुल एक जैसा)
Step 5 → distance <= threshold (जैसे 0.12) -> HIT, stored जवाब दो
Step 6 → वरना MISS -> LLM call -> embedding bytes + answer + EXPIRE के साथ HASH store
Step 7 → Labelled pairs से threshold tune करो; गलत hits पर नज़र रखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Brokers ask "HS code for ladies cotton kurta", "women cotton kurti tariff heading", "cotton kurta for women import code". All three embed close together (distance under 0.12), so only the first pays for the LLM. The tenant TAG ensures one customer's cached notes never answer another customer.
**Zomato AI**: "Best biryani near me under 300" and "cheap good biryani nearby" share one cached recommendation text per city.

## 🟡 Real Example Hindi mein
**Tariff System**: Brokers पूछते हैं "ladies cotton kurta का HS code", "women cotton kurti tariff heading", "women के cotton kurta का import code"। तीनों embeddings पास हैं (distance 0.12 से कम), इसलिए LLM का खर्च सिर्फ़ पहले पर। Tenant TAG से एक customer के cached notes दूसरे को जवाब नहीं देते।
**Zomato AI**: "300 से कम में best biryani पास में" और "सस्ती अच्छी biryani nearby" का शहर के हिसाब से एक cached recommendation text।

---

## 💻 Code Example — Basic
```python
# Basic: semantic cache logic with cosine DISTANCE like Redis uses. Pure Python, offline.
# A toy embedding (hashed bag of words) replaces a real model so the example runs without keys.
import hashlib  # stable hashing of words
import math  # sqrt


def embed(text: str, dim: int = 64) -> list[float]:
    v = [0.0] * dim  # empty vector
    for w in text.lower().split():  # each word adds weight to one slot
        idx = int(hashlib.md5(w.encode()).hexdigest(), 16) % dim  # stable slot for the word
        v[idx] += 1.0
    n = math.sqrt(sum(x * x for x in v)) or 1.0  # vector length
    return [x / n for x in v]  # unit vector


def cosine_distance(a: list[float], b: list[float]) -> float:
    return 1.0 - sum(x * y for x, y in zip(a, b))  # 0 identical, up to 2 opposite


class SemanticCache:
    def __init__(self, threshold: float = 0.35) -> None:
        self.t = threshold  # accept if distance <= t
        self.rows: list[tuple[str, list[float], str]] = []  # (tenant, vec, answer)

    def get(self, tenant: str, q: str) -> tuple[str | None, float]:
        qv = embed(q)  # embed query
        best, best_d = None, 9.0
        for tn, vec, ans in self.rows:
            if tn != tenant:  # tenant filter
                continue
            d = cosine_distance(qv, vec)
            if d < best_d:
                best, best_d = ans, d
        return (best if best_d <= self.t else None), best_d

    def put(self, tenant: str, q: str, answer: str) -> None:
        self.rows.append((tenant, embed(q), answer))


if __name__ == "__main__":
    c = SemanticCache()
    c.put("acme", "hs code for ladies cotton kurta", "6204.42")
    print(c.get("acme", "hs code for cotton kurta ladies"))  # close -> hit
    print(c.get("acme", "diesel engine import duty"))  # far -> miss
    print(c.get("other", "hs code for ladies cotton kurta"))  # other tenant -> miss
```

## 💻 Code Example — Advanced
```python
# Production: Redis Stack vector index with redis-py (redis>=5) + OpenAI embeddings, async.
# Needs Redis Stack / Redis 8 (RediSearch). pip install redis numpy openai
from __future__ import annotations

import hashlib
import logging
import numpy as np
import redis.asyncio as redis
from openai import AsyncOpenAI
from redis.commands.search.field import TagField, TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import RedisError, ResponseError

log = logging.getLogger("semcache")
DIM = 1536  # text-embedding-3-small dimension
INDEX = "idx:semcache"
PREFIX = "sem:"


class RedisSemanticCache:
    def __init__(self, url: str = "redis://localhost:6379/0", threshold: float = 0.12, ttl: int = 86_400) -> None:
        self.r = redis.from_url(url)  # bytes mode: vectors are raw bytes
        self.ai = AsyncOpenAI()
        self.threshold, self.ttl = threshold, ttl

    async def setup(self) -> None:
        try:
            await self.r.ft(INDEX).create_index(
                [
                    TagField("tenant"),
                    TextField("answer"),
                    VectorField("embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": DIM, "DISTANCE_METRIC": "COSINE"}),
                ],
                definition=IndexDefinition(prefix=[PREFIX], index_type=IndexType.HASH),
            )
        except ResponseError as exc:
            if "Index already exists" not in str(exc):  # idempotent setup
                raise

    async def _embed(self, text: str) -> bytes:
        res = await self.ai.embeddings.create(model="text-embedding-3-small", input=text)
        return np.array(res.data[0].embedding, dtype=np.float32).tobytes()  # Redis wants float32 bytes

    async def get(self, tenant: str, question: str) -> str | None:
        try:
            vec = await self._embed(question)
            q = (
                Query(f"(@tenant:{{{tenant}}})=>[KNN 1 @embedding $vec AS dist]")  # filtered KNN
                .sort_by("dist")
                .return_fields("answer", "dist")
                .dialect(2)
            )
            res = await self.r.ft(INDEX).search(q, query_params={"vec": vec})
            if res.docs and float(res.docs[0].dist) <= self.threshold:
                return res.docs[0].answer if isinstance(res.docs[0].answer, str) else res.docs[0].answer.decode()
        except (RedisError, Exception) as exc:  # cache must never break requests
            log.warning("semantic get failed: %s", exc)
        return None

    async def put(self, tenant: str, question: str, answer: str) -> None:
        try:
            key = PREFIX + hashlib.sha256(f"{tenant}:{question}".encode()).hexdigest()
            await self.r.hset(key, mapping={"tenant": tenant, "answer": answer, "embedding": await self._embed(question)})
            await self.r.expire(key, self.ttl)  # TTL per entry
        except Exception as exc:
            log.warning("semantic put failed: %s", exc)
```
(Tenant ids used in a TAG filter must not contain special characters; sanitise them, for example by hashing.)

---

## 🟠 FastAPI Integration
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header
from pydantic import BaseModel

sem: RedisSemanticCache | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global sem
    sem = RedisSemanticCache()
    await sem.setup()  # create index at startup
    yield


app = FastAPI(lifespan=lifespan)


class In(BaseModel):
    question: str


@app.post("/ask")
async def ask(body: In, x_tenant: str = Header(...)) -> dict:
    tenant = hashlib.sha1(x_tenant.encode()).hexdigest()[:16]  # safe TAG value
    hit = await sem.get(tenant, body.question)
    if hit:
        return {"answer": hit, "source": "semantic-cache"}
    answer = await call_llm(body.question)  # your LLM call
    await sem.put(tenant, body.question, answer)
    return {"answer": answer, "source": "llm"}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_community.cache import RedisSemanticCache  # semantic cache backed by Redis
from langchain_core.globals import set_llm_cache
from langchain_openai import OpenAIEmbeddings

set_llm_cache(
    RedisSemanticCache(
        redis_url="redis://localhost:6379",  # Redis Stack
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),  # embedding model
        score_threshold=0.2,  # distance threshold (lower = stricter)
    )
)
# All chat model calls in chains and LangGraph nodes now use semantic lookup.
```
The `langchain-redis` package also provides `RedisSemanticCache` with a similar interface.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Changing the embedding model without re-indexing
✅ Correct: Vectors from different models are not comparable. Put the model name in the index/prefix and rebuild.

```python
# Wrong: switch to text-embedding-3-large, same index (dim mismatch or garbage matches)
# Right: PREFIX = "sem:te3s:" and a new index; old entries expire by TTL
```

❌ Mistake 2: Semantic matching on prompts that include user-specific data
✅ Correct: Filter by tenant, or skip semantic caching for personalised questions.

```python
# Wrong
res = search(KNN 1 @embedding $vec)                       # any tenant
# Right
res = search("(@tenant:{abc})=>[KNN 1 @embedding $vec]")  # tenant scoped
```

---

## 🧠 Tricky Interview Question
**Q**: "'How do I import 5 laptops?' and 'How do I import 50 laptops?' have cosine similarity 0.98. Your semantic cache treats them as the same. Is that fine?"

**Answer**: Not necessarily. Embeddings capture topic well but are weak on numbers, negation and small but decisive details; the answer may differ above a quantity limit. Mitigations: extract such attributes into the exact key (a TAG field or hash), use a stricter threshold, add a cheap verification step (small LLM or cross-encoder) for borderline distances, and evaluate false-hit rate with labelled pairs.

---

## ⚫ Interview Questions + Answers

Q1: What is a semantic cache? (Easy)
A1: A cache that finds stored answers by meaning using embeddings and vector search rather than by exact text.

Q2: Which Redis features are needed? (Easy)
A2: Redis Stack or Redis 8 with the search module (vector fields, HNSW or FLAT index, KNN queries).

Q3: What is the cost of a semantic lookup? (Medium)
A3: One embedding call (about 20-50 tokens, very cheap) plus a Redis vector query (milliseconds). Both are far cheaper than a typical LLM call.

Q4: Cosine similarity vs distance in Redis? (Medium)
A4: Redis returns cosine distance = 1 minus similarity. So lower is better, and a threshold of 0.12 means similarity at least 0.88.

Q5: How do you pick and monitor the threshold in production? (Hard)
A5: Build labelled pairs (same intent / different intent) from real logs. Compute precision and recall across thresholds, choose the point satisfying the accuracy target. In production log score, hit/miss and sampled hits for review, run shadow mode (compute the LLM answer in parallel for 1-5 percent of hits and compare), and alert when disagreement rises.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Natural-language FAQ or support traffic with paraphrases
- Redis is already in your stack
- Approximate answers are acceptable

❌ Avoid when:
- Answers depend on numbers, dates or personal data in the question
- Exact reproducibility or audit trail of each answer is required
- Very low traffic (embedding plus index overhead is not worth it)

---

## 📊 Visual Diagram
```
 question ─► embed ─► vector (1536 floats)
                         │
              Redis FT.SEARCH  @tenant:{t} KNN 1
                         │
                nearest entry, dist
               ┌─────────┴─────────┐
        dist <= 0.12          dist > 0.12
               │                   │
         return answer        call LLM ─► HSET(vector, answer) + EXPIRE
```

---

## 💰 Cost Impact
**Token usage**: Each lookup costs one embedding (about 30 tokens at $0.02 per 1M for text-embedding-3-small = $0.0000006). An LLM miss with 700 input + 150 output tokens on gpt-4o-mini is about $0.00020. A hit therefore saves roughly 300 times its lookup cost.
**Optimisation**: cache embeddings of frequent queries, use a smaller embedding dimension, tune the threshold, set TTL, and use FLAT index for small caches (under about 100k entries) or HNSW for large ones.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Semantic cache | Cache matched by meaning | अर्थ से match होने वाला cache |
| KNN | k nearest neighbours search | सबसे पास के k पड़ोसी |
| Cosine distance | 1 minus cosine similarity | 1 घटा cosine similarity |
| HNSW | Fast approximate vector index | तेज़ approximate vector index |
| Threshold | Max distance to accept | स्वीकार की अधिकतम distance |
| TAG field | Exact-match filter field | exact filter वाला field |

---

## ⚡ 3-Line Summary
English: Redis vector search lets you cache LLM answers by meaning, not exact text. Store embedding plus answer, run KNN, and accept only within a tuned distance threshold and the right tenant. Watch false hits on numbers and personal data.
Hindi: Redis vector search से LLM जवाब अर्थ के आधार पर cache होते हैं, exact text से नहीं। Embedding और answer store करो, KNN चलाओ और सिर्फ़ tuned distance threshold व सही tenant में ही मानो। संख्याओं और personal data पर गलत hits से सावधान रहो।

---

## ➡️ Next Topic
**453. Semantic Cache with Qdrant** — the same pattern on a dedicated vector database with richer payload filtering.
