---

# 115. Embedding Caching — Complete Guide
# हिंदी में: Embedding Caching — पूरी Guide

---

## 🔵 Simple Definition (English)
Embedding caching stores the vector for a text after the first computation, so the next time the same text appears you read the stored vector instead of calling the model again. The cache key is a hash of the text plus the model name (and dimensions).

## 🔵 सरल परिभाषा (Hindi)
Embedding caching पहली बार vector बनने के बाद उसे store कर लेती है, ताकि वही text दोबारा आने पर model call करने की बजाय stored vector पढ़ा जाए। Cache key = text का hash + model name (और dimensions)।

---

## 🔴 Problem it Solves
Many texts repeat: popular user queries, duplicated product descriptions, documents re-synced every night, tests that run in CI. Each repeat costs money and 100 to 300 ms of API latency. A cache makes repeats free and fast (about 1 ms from memory or Redis).

## 🔴 यह क्यों बना? (Hindi)
कई texts दोहराए जाते हैं: popular user queries, duplicate product descriptions, हर रात re-sync होने वाले documents, CI में चलने वाले tests। हर repeat पर पैसा और 100-300 ms latency लगती है। Cache से repeat मुफ्त और तेज़ (memory/Redis से लगभग 1 ms) हो जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise text (strip, collapse spaces; lowercase only if safe)
Step 2 → key = sha256(model + ":" + dims + ":" + text)
Step 3 → Look up key in cache (dict / Redis / disk / SQLite)
Step 4 → Hit  -> return stored vector (no API call)
Step 5 → Miss -> collect all missed texts, embed them in ONE batch
Step 6 → Store each new vector under its key (with optional TTL)
Step 7 → Return vectors in the original input order
Step 8 → Track hit rate; invalidate on model change (key includes model)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Text normalise करो (strip, extra spaces हटाओ)
Step 2 → key = sha256(model + ":" + dims + ":" + text)
Step 3 → Cache (dict / Redis / disk / SQLite) में key ढूँढो
Step 4 → Hit -> stored vector लौटाओ (API call नहीं)
Step 5 → Miss -> सभी missed texts को एक batch में embed करो
Step 6 → नए vectors key के साथ store करो (चाहें तो TTL)
Step 7 → Original input के क्रम में vectors लौटाओ
Step 8 → Hit rate track करो; model बदले तो key बदल जाती है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs officers search the same 3,000 popular product phrases ("lithium battery", "cotton t-shirt") all day. Caching query embeddings gives a 70% hit rate, saving 70% of query embedding calls and about 150 ms per hit. Document embeddings are cached on disk by content hash so nightly syncs are nearly free.

**Zomato-style**: Lunch-time spikes repeat "biryani near me" thousands of times.

## 🟡 Real Example Hindi mein
**Tariff System**: Customs officers दिन भर वही 3,000 popular phrases ("lithium battery", "cotton t-shirt") search करते हैं। Query embeddings cache करने से 70% hit rate मिलता है, 70% embedding calls और हर hit पर लगभग 150 ms बचते हैं। Document embeddings content hash से disk पर cache होते हैं, इसलिए nightly sync लगभग मुफ्त।

**Zomato-style**: Lunch time में "biryani near me" हज़ारों बार दोहराया जाता है।

---

## 💻 Code Example — Basic
```python
# In-memory embedding cache with a fake embedder (runs offline)
import hashlib
from typing import Callable

Embedder = Callable[[list[str]], list[list[float]]]   # batch embedding function type


class CachedEmbedder:
    """Wraps any embedder; only calls it for texts not seen before."""

    def __init__(self, embed_fn: Embedder, model: str) -> None:
        self.embed_fn = embed_fn                      # the real (paid) function
        self.model = model                            # part of the cache key
        self.cache: dict[str, list[float]] = {}       # key -> vector
        self.hits = 0                                 # stats
        self.misses = 0

    def _key(self, text: str) -> str:
        norm = " ".join(text.split())                 # collapse whitespace
        return hashlib.sha256(f"{self.model}:{norm}".encode()).hexdigest()

    def embed(self, texts: list[str]) -> list[list[float]]:
        keys = [self._key(t) for t in texts]
        missing = {k: t for k, t in zip(keys, texts) if k not in self.cache}   # unique misses
        self.hits += len(texts) - len(missing)
        self.misses += len(missing)
        if missing:
            vecs = self.embed_fn(list(missing.values()))   # ONE batched call
            for k, v in zip(missing, vecs):
                self.cache[k] = v
        return [self.cache[k] for k in keys]          # original order


calls = {"n": 0}


def fake_embed(texts: list[str]) -> list[list[float]]:
    calls["n"] += 1                                   # count paid calls
    return [[float(len(t)), 1.0] for t in texts]


ce = CachedEmbedder(fake_embed, "fake-v1")
ce.embed(["lithium battery", "cotton t-shirt"])
ce.embed(["lithium  battery", "new query"])           # first one is a hit (whitespace normalised)
print("api calls:", calls["n"], "hits:", ce.hits, "misses:", ce.misses)   # 2, 1, 3
```

## 💻 Code Example — Advanced
```python
# Redis-backed async cache for OpenAI embeddings (binary float32, TTL, error tolerant)
import asyncio
import hashlib
import numpy as np
import redis.asyncio as redis                         # pip install redis
from openai import AsyncOpenAI

client = AsyncOpenAI()
r = redis.Redis.from_url("redis://localhost:6379/0")
MODEL, DIMS, TTL = "text-embedding-3-small", 1536, 60 * 60 * 24 * 30   # 30 days


def key(text: str) -> str:
    return "emb:" + hashlib.sha256(f"{MODEL}:{DIMS}:{text}".encode()).hexdigest()


async def embed_cached(texts: list[str]) -> list[np.ndarray]:
    keys = [key(t) for t in texts]
    try:
        raw = await r.mget(keys)                      # one round trip
    except redis.RedisError:
        raw = [None] * len(texts)                     # cache down -> behave like all misses
    out: list[np.ndarray | None] = [
        np.frombuffer(b, dtype=np.float32) if b else None for b in raw
    ]
    miss_idx = [i for i, v in enumerate(out) if v is None]
    if miss_idx:
        uniq = list(dict.fromkeys(texts[i] for i in miss_idx))     # dedupe within batch
        try:
            resp = await client.embeddings.create(model=MODEL, input=uniq)
        except Exception as exc:
            raise RuntimeError(f"embedding failed: {exc}") from exc
        fresh = {t: np.asarray(d.embedding, dtype=np.float32) for t, d in zip(uniq, resp.data)}
        try:
            pipe = r.pipeline()
            for t, v in fresh.items():
                pipe.set(key(t), v.tobytes(), ex=TTL)            # store compactly
            await pipe.execute()
        except redis.RedisError:
            pass                                                 # cache write failure is not fatal
        for i in miss_idx:
            out[i] = fresh[texts[i]]
    return [v for v in out if v is not None]


if __name__ == "__main__":
    vs = asyncio.run(embed_cached(["lithium battery", "lithium battery"]))
    print(len(vs), vs[0].shape)                       # needs Redis + OpenAI key
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
_cache: dict[str, list[float]] = {}                  # replace with Redis in production
stats = {"hits": 0, "misses": 0}


class Req(BaseModel):
    text: str = Field(min_length=1)


async def real_embed(text: str) -> list[float]:
    return [float(len(text))]                        # placeholder for an API call


@app.post("/embed")
async def embed(req: Req) -> dict[str, object]:
    k = " ".join(req.text.split()).lower()
    if k in _cache:
        stats["hits"] += 1
        return {"cached": True, "vector": _cache[k]}
    stats["misses"] += 1
    _cache[k] = await real_embed(req.text)
    return {"cached": False, "vector": _cache[k]}


@app.get("/embed/stats")
async def get_stats() -> dict[str, float]:
    total = stats["hits"] + stats["misses"]
    return {**stats, "hit_rate": stats["hits"] / total if total else 0.0}
```

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore      # or RedisStore from langchain_community.storage
from langchain_openai import OpenAIEmbeddings

underlying = OpenAIEmbeddings(model="text-embedding-3-small")
cached = CacheBackedEmbeddings.from_bytes_store(
    underlying, LocalFileStore("./cache"), namespace=underlying.model   # avoids cross-model collisions
)
cached.embed_documents(["lithium battery"])       # computed
cached.embed_documents(["lithium battery"])       # read from disk
```
Note: by default `CacheBackedEmbeddings` caches documents only; pass `query_embedding_cache=True` (or a store) in newer versions to cache queries too.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Cache key = text only
✅ Correct: Include model and dimensions in the key.

```python
# Wrong
key = sha(text)
# Right
key = sha(f"{model}:{dims}:{text}")
```

❌ Mistake 2: One API call per miss
✅ Correct: Collect all misses and send one batch.

❌ Mistake 3: Lowercasing everything blindly
✅ Correct: Lowercase only if the model/domain is case-insensitive ("US" vs "us", HS codes, part numbers).

---

## 🧠 Tricky Interview Question

**Q**: "After a model upgrade your search quality suddenly dropped, but nothing in the code changed except the model name. The cache is suspected. Why?"

**Answer**: The cache key did not include the model name, so old vectors from the previous model were still served for repeated texts while new texts got vectors from the new model. The index then mixes two vector spaces, so cosine scores are meaningless. Fix: include model+dims in the key (or namespace), flush the cache, and re-embed the entire corpus.

---

## ⚫ Interview Questions + Answers

Q1: What should the cache key contain?
A1: Hash of the text plus model name and dimensions.

Q2: Where can you store the cache?
A2: Memory (fastest, lost on restart), Redis (shared, TTL), disk/SQLite (persistent), or the vector DB metadata.

Q3: Why batch the misses?
A3: Fewer API calls, lower latency, fewer rate limit problems.

Q4: How do you measure its value?
A4: Hit rate, dollars saved (hits x avg tokens x price), and p95 latency before/after.

Q5: How would you cache query embeddings safely for user-specific data?
A5: Query embeddings are derived from the text only, so sharing by text hash is fine unless the text contains PII. Hash keys avoid storing raw text, set TTLs, scope by tenant if the policy requires it, and encrypt Redis at rest. For privacy rules (GDPR) provide deletion by tenant or text hash.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Texts repeat (queries, re-syncs, tests)
- API latency or cost matters

❌ Avoid when:
- Every text is unique (low hit rate adds overhead)
- Privacy rules forbid storing derived data

---

## 📊 Visual Diagram
```
 texts ─► key = hash(model+dims+text)
              │
         ┌────┴─────┐
       hit        miss
        │           │
  stored vector   batch ─► embedding API ─► store (TTL)
        └────┬──────┘
             ▼
   vectors in original order
```

---

## 💰 Cost Impact
Savings = hit rate x tokens x price. Example: 2M query tokens/day at 70% hit rate saves 1.4M tokens/day; with small this is $0.028/day, small in money, but it saves about 150 ms for each hit, which users feel. For large documents (100M tokens) the dollar saving is real: $2 per avoided re-embed (small) or $13 (large). Redis memory cost: 1536 x 4 B = 6 KB per vector; 1M cached = 6 GB, so set TTL/eviction (LRU).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache hit/miss | Found / not found in cache | Cache में मिला / नहीं मिला |
| TTL | Time to live | Cache की उम्र |
| Namespace | Key prefix per model | हर model का अलग key prefix |
| Hit rate | Hits / total requests | Hits का अनुपात |
| LRU | Evict least recently used | सबसे कम उपयोग वाला हटाओ |
| Idempotent | Same input, same output | Same input पर same output |

---

## ⚡ 3-Line Summary
English: Cache embeddings by hash(model+dims+text) so repeats cost nothing. Batch the misses and keep order. Always include the model in the key to avoid mixing vector spaces.
Hindi: Embeddings को hash(model+dims+text) से cache करो ताकि repeats मुफ्त हों। Misses को batch करो और क्रम रखो। Vector spaces न मिलें, इसलिए key में model ज़रूर रखो।

---

## ➡️ Next Topic
**116. Batch Embedding** - embedding large datasets efficiently: batch sizes, concurrency, the Batch API and failure recovery.
