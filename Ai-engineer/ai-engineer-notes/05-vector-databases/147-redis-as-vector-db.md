---

# 147. Redis as Vector DB
# हिंदी में: Redis को Vector Database की तरह use करना

---

## 🔵 Simple Definition (English)
Redis (with the Search module, included in Redis Stack / Redis 8) can store vectors inside hashes or JSON documents and run KNN search with FLAT or HNSW indexes. Everything lives in memory, so queries are very fast.

## 🔵 सरल परिभाषा (Hindi)
Redis (Search module के साथ, जो Redis Stack / Redis 8 में आता है) hashes या JSON documents में vectors store करके FLAT या HNSW index से KNN search चला सकता है। सब कुछ memory में रहता है, इसलिए queries बहुत तेज़ हैं।

---

## 🔴 Problem it Solves
Disk-based vector stores add milliseconds. Chat apps need sub-10 ms lookups, for example semantic caching ("have we answered this question before?") and session-aware retrieval. Many teams already run Redis, so adding vectors avoids another service.

## 🔴 यह क्यों बना? (Hindi)
Disk-based stores में milliseconds जुड़ते हैं। Chat apps को 10 ms से कम lookup चाहिए, जैसे semantic caching ("क्या यह सवाल पहले answer हुआ?")। कई teams के पास Redis पहले से है, तो vectors जोड़ना आसान है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run Redis Stack:  docker run -p 6379:6379 redis/redis-stack:latest
Step 2 → FT.CREATE an index over hash keys with a prefix, with a VECTOR field
         (algorithm FLAT or HNSW, dim, distance metric, type FLOAT32)
Step 3 → Store each doc as a HASH; the vector is raw float32 BYTES
Step 4 → Query: FT.SEARCH idx "*=>[KNN 5 @embedding $vec AS dist]" PARAMS 2 vec <bytes> DIALECT 2
Step 5 → Results come back sorted by dist (lower = closer for COSINE)
Step 6 → Optional pre-filter: "(@country:{IN})=>[KNN 5 @embedding $vec AS dist]"
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Redis Stack चलाओ: docker run -p 6379:6379 redis/redis-stack:latest
Step 2 → Prefix वाली hash keys पर FT.CREATE से VECTOR field वाला index बनाओ
         (FLAT या HNSW, dim, distance metric, type FLOAT32)
Step 3 → हर doc को HASH में रखो; vector raw float32 BYTES होता है
Step 4 → Query: FT.SEARCH idx "*=>[KNN 5 @embedding $vec AS dist]" PARAMS 2 vec <bytes> DIALECT 2
Step 5 → Results dist से sorted आते हैं (COSINE में कम = नज़दीक)
Step 6 → Optional pre-filter: "(@country:{IN})=>[KNN 5 @embedding $vec AS dist]"
```

---

## 🟡 Real World Example
**Tariff Classification System**: users keep asking "HS code for iPhone 15?" in many phrasings. A Redis **semantic cache** stores (question embedding -> answer). A new question within cosine distance 0.08 of a cached one returns the saved answer in milliseconds and skips the LLM call completely.

**Zomato AI**: recently viewed dishes per user session are embedded in Redis for instant "more like this" suggestions.

## 🟡 Real Example Hindi mein
**Tariff System**: users "iPhone 15 का HS code?" अलग-अलग शब्दों में पूछते हैं। Redis **semantic cache** में (question embedding -> answer) रहता है। 0.08 cosine distance के अंदर नया सवाल आए तो saved answer milliseconds में मिलता है और LLM call बिल्कुल नहीं होती।

**Zomato AI**: user session में देखी हुई dishes के embeddings Redis में रहते हैं, जिससे तुरंत "इसी जैसे और" suggestions मिलते हैं।

---

## 💻 Code Example — Basic
```python
# pip install redis numpy ; server: redis/redis-stack
import numpy as np  # for float32 bytes
import redis  # redis-py
from redis.commands.search.field import TagField, TextField, VectorField  # schema fields
from redis.commands.search.indexDefinition import IndexDefinition, IndexType  # index type
from redis.commands.search.query import Query  # query builder

r = redis.Redis(host="localhost", port=6379)  # connect (decode_responses must stay False for bytes)
DIM = 4  # tiny demo dimension

try:
    r.ft("idx:tariff").create_index(  # create the search index
        fields=[
            TextField("description"),  # full-text field
            TagField("country"),  # exact-match tag
            VectorField("embedding", "HNSW",  # vector field using HNSW
                        {"TYPE": "FLOAT32", "DIM": DIM, "DISTANCE_METRIC": "COSINE"}),
        ],
        definition=IndexDefinition(prefix=["tariff:"], index_type=IndexType.HASH),  # keys tariff:*
    )
except redis.exceptions.ResponseError as e:  # "Index already exists" is fine
    print("index:", e)

vec = np.array([0.9, 0.1, 0.0, 0.0], dtype=np.float32)  # example embedding
r.hset("tariff:8518.30", mapping={  # store a hash
    "description": "Headphones",
    "country": "IN",
    "embedding": vec.tobytes(),  # raw bytes, not a python list
})

q = (Query("(@country:{IN})=>[KNN 3 @embedding $v AS dist]")  # filter + KNN
     .sort_by("dist").return_fields("description", "dist").dialect(2))
res = r.ft("idx:tariff").search(q, query_params={"v": vec.tobytes()})  # run it
for d in res.docs:  # iterate results
    print(d.id, d.description, d.dist)
```

## 💻 Code Example — Advanced
```python
# Production: async redis, semantic cache with TTL, thresholds, error handling
import hashlib
import logging
from typing import Optional

import numpy as np
import redis.asyncio as aredis  # async client in redis-py>=4.2
from redis.commands.search.query import Query

log = logging.getLogger("redis_cache")


class SemanticCache:
    """Cache LLM answers by meaning, not by exact string."""

    def __init__(self, url: str = "redis://localhost:6379", threshold: float = 0.08, ttl: int = 86400) -> None:
        self.r = aredis.from_url(url)  # async connection pool
        self.threshold = threshold  # max cosine distance to count as a hit
        self.ttl = ttl  # entries expire after one day

    async def get(self, emb: list[float]) -> Optional[str]:
        q = (Query("*=>[KNN 1 @embedding $v AS dist]")  # nearest 1
             .sort_by("dist").return_fields("answer", "dist").dialect(2))
        try:
            res = await self.r.ft("idx:cache").search(
                q, query_params={"v": np.asarray(emb, dtype=np.float32).tobytes()})
        except aredis.RedisError:
            log.exception("cache read failed")  # cache must never break the request
            return None
        if res.docs and float(res.docs[0].dist) <= self.threshold:  # close enough?
            return res.docs[0].answer if isinstance(res.docs[0].answer, str) else res.docs[0].answer.decode()
        return None

    async def put(self, question: str, emb: list[float], answer: str) -> None:
        key = "cache:" + hashlib.sha1(question.encode()).hexdigest()  # stable key
        try:
            await self.r.hset(key, mapping={
                "answer": answer,
                "embedding": np.asarray(emb, dtype=np.float32).tobytes(),
            })
            await self.r.expire(key, self.ttl)  # TTL keeps memory bounded
        except aredis.RedisError:
            log.exception("cache write failed")  # swallow: caching is best-effort
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel

app = FastAPI()
client = AsyncOpenAI()
cache = SemanticCache()  # from Advanced example (index "idx:cache" created at startup)


class Ask(BaseModel):
    question: str


@app.post("/tariff/ask")
async def ask(body: Ask) -> dict:
    emb = (await client.embeddings.create(model="text-embedding-3-small", input=body.question)).data[0].embedding
    hit = await cache.get(emb)  # 1) try the cache
    if hit:
        return {"answer": hit, "cached": True}  # no LLM tokens spent
    resp = await client.chat.completions.create(  # 2) miss: call LLM
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": body.question}],
        max_tokens=200,
    )
    answer = resp.choices[0].message.content or ""
    await cache.put(body.question, emb, answer)  # 3) store for next time
    return {"answer": answer, "cached": False, "tokens": resp.usage.total_tokens}
```

---

## 🔗 LangChain / LangGraph Connection
```python
# pip install langchain-redis
from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisVectorStore

vs = RedisVectorStore.from_texts(
    texts=["Headphones", "Smartphones"],
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    redis_url="redis://localhost:6379",
    index_name="tariff",
)
retriever = vs.as_retriever(search_kwargs={"k": 3})  # plug into LCEL / LangGraph
# LangChain also has a Redis semantic cache (langchain_redis.RedisSemanticCache) for set_llm_cache().
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Storing the vector as a Python list or JSON string in a HASH
```python
# Wrong
r.hset("k", mapping={"embedding": str([0.1, 0.2])})
# Right: raw float32 bytes with the same dtype as the index
r.hset("k", mapping={"embedding": np.array([0.1, 0.2], dtype=np.float32).tobytes()})
```

❌ Mistake 2: `decode_responses=True` while reading binary fields
```python
# Wrong: UnicodeDecodeError when the vector bytes come back
r = redis.Redis(decode_responses=True)
# Right: keep bytes; decode text fields yourself
r = redis.Redis()
```

---

## 🧠 Tricky Interview Question

**Q**: "Your semantic cache returned a wrong answer: 'HS code for cotton shirts' got the answer for 'HS code for silk shirts'. How do you prevent it?"

**Answer**: Embeddings of near-identical sentences are very close, so a loose threshold causes false hits. Fixes: (1) tighten the threshold (for example 0.03-0.05) and measure on labelled pairs, (2) put critical attributes into an exact TAG filter (material, country, year) and filter before KNN, (3) cache only after validating answer quality, (4) include a cheap reranker or LLM check for borderline distances, (5) version keys when the tariff schedule changes and use TTLs.

---

## ⚫ Interview Questions + Answers

Q1: Which Redis module gives vector search?
A1: RediSearch (Search and Query), included in Redis Stack and Redis 8.

Q2: FLAT vs HNSW?
A2: FLAT is exact brute force (good for small sets), HNSW is approximate and fast for large sets with higher memory use.

Q3: Why is Redis fast for vectors?
A3: Data and index are in RAM, and there is no disk or network hop to a separate service if Redis is local.

Q4: Main drawback?
A4: RAM cost. 1M vectors x 1536 dims x 4 bytes is about 6 GB plus HNSW links, much costlier than disk storage. Persistence is configurable but not the main design goal.

Q5: How would you design a semantic cache at scale?
A5: Embed the query, KNN(1) with a tuned distance threshold plus exact TAG filters, TTL per entry, a namespace per prompt/model version, hit-rate metrics, a fallback to the LLM on any Redis error, and an eviction policy (`allkeys-lru`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Ultra-low latency, semantic caching, small to mid datasets (up to a few million)
- Redis is already in your stack

❌ Avoid when:
- Huge datasets where RAM cost explodes
- You need rich analytics/joins or strong durability as the system of record

---

## 📊 Visual Diagram
```
 question ─► embed ─► FT.SEARCH KNN 1 ─► dist <= 0.08 ?
                                   │            │
                                  yes           no
                                   ▼            ▼
                           cached answer    call LLM ─► store (vector, answer, TTL)
                           (0 tokens)       (tokens spent)
 RAM: [ hash:tariff:1 {desc, country, embedding bytes} ] + HNSW graph
```

---

## 💰 Cost Impact
- A semantic cache can remove 20-60 percent of LLM calls on repetitive traffic (depends on your data; measure hit rate). Each hit saves the full prompt and completion tokens, for example about 700 tokens per avoided call.
- Embedding each query still costs a few tokens, which is far cheaper than a full completion.
- RAM is the main infra cost: reduce dimension (512/768), use TTL and `maxmemory-policy allkeys-lru`, and store only what you need.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RediSearch | Redis search/vector module | Redis का search module |
| FT.CREATE | Command to create an index | Index बनाने की command |
| KNN | K nearest neighbours | K सबसे नज़दीकी |
| Semantic cache | Cache keyed by meaning | अर्थ के आधार पर cache |
| TTL | Time to live | Entry की उम्र |
| DIALECT 2 | Query syntax version needed for vectors | Vector query syntax version |

---

## ⚡ 3-Line Summary
English: Redis Stack can index float32 vectors with FLAT or HNSW and answer KNN queries in memory. It shines for semantic caching and low-latency retrieval. Mind RAM cost and tune thresholds carefully.
Hindi: Redis Stack float32 vectors को FLAT या HNSW से index करके memory में KNN queries का जवाब देता है। Semantic caching और low-latency retrieval में बढ़िया है। RAM cost और thresholds का ध्यान रखो।

---

## ➡️ Next Topic
**148. MongoDB Atlas Vector Search** — vectors inside a document database.
