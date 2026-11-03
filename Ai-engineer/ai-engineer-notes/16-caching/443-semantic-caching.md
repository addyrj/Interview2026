
# 443. Semantic Caching
# हिंदी में: Semantic Caching

---

## 🔵 Simple Definition (English)
Semantic caching matches a new request to earlier ones by meaning, not by exact text. It converts the query to an embedding vector, searches for a close stored query (cosine similarity above a threshold) and returns that stored answer. "HS code for earbuds" and "tariff number for wireless ear buds" can share one answer.

## 🔵 सरल परिभाषा (Hindi)
Semantic caching नई request को पुरानी requests से अर्थ (meaning) के आधार पर match करता है, exact text से नहीं। Query को embedding vector में बदलकर पास का stored query ढूँढता है (cosine similarity threshold से ऊपर) और उसका stored answer लौटाता है। "HS code for earbuds" और "wireless ear buds का tariff number" एक ही answer share कर सकते हैं।

---

## 🔴 Problem it Solves
Exact caching misses paraphrases: users phrase the same question in many ways, so hit rate stays low and you keep paying for near-duplicate calls. Semantic caching raises hit rate by treating similar meanings as the same request.

## 🔴 यह क्यों बना? (Hindi)
Exact caching paraphrases miss कर देता है: users एक ही सवाल कई तरह से पूछते हैं, इसलिए hit rate कम रहता है और near-duplicate calls के पैसे लगते रहते हैं। Semantic caching समान अर्थ वाली requests को एक मानकर hit rate बढ़ाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Embed the incoming query with an embedding model (costs a few tokens, much cheaper than generation)
Step 2 → Nearest-neighbour search in a vector index of past queries (Redis, Qdrant, FAISS, ...)
Step 3 → Take the best match and its similarity score
Step 4 → score >= threshold (e.g. 0.92) -> HIT: return stored answer
Step 5 → score <  threshold -> MISS: call LLM
Step 6 → Store (query embedding, query text, answer, metadata, TTL)
Step 7 → Tune the threshold using labelled pairs; monitor false hits
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Incoming query को embedding model से embed करो (कुछ tokens, generation से बहुत सस्ता)
Step 2 → पुराने queries के vector index में nearest-neighbour search (Redis, Qdrant, FAISS...)
Step 3 → Best match और उसका similarity score लो
Step 4 → score >= threshold (जैसे 0.92) -> HIT: stored answer लौटाओ
Step 5 → score < threshold -> MISS: LLM call
Step 6 → (query embedding, query text, answer, metadata, TTL) store करो
Step 7 → Labelled pairs से threshold tune करो; false hits monitor करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: "HS code for Bluetooth earphones", "tariff heading for wireless earbuds" and "classification of true wireless stereo headset" all map to heading 8518. A semantic cache serves all three from one stored answer. Danger: "earbuds" vs "earbud charging case" may embed very close but have different codes, so use a high threshold, include metadata filters (destination country, schedule version) and keep a human-reviewed list of "never share" categories.

**Zomato AI**: "Is there a veg pizza under 300?" and "cheap vegetarian pizza below Rs 300" share an answer, only within the same city and menu version.

## 🟡 Real Example Hindi mein
**Tariff System**: "Bluetooth earphones का HS code", "wireless earbuds की tariff heading" और "true wireless stereo headset की classification" सब heading 8518 पर जाते हैं। Semantic cache तीनों को एक stored answer से serve करता है। ख़तरा: "earbuds" और "earbud charging case" embedding में पास हो सकते हैं पर code अलग है, इसलिए high threshold, metadata filters (destination country, schedule version) और "कभी share न हों" categories की सूची रखो।

**Zomato AI**: "300 से कम में veg pizza है?" और "सस्ता vegetarian pizza Rs 300 के नीचे" एक answer share करते हैं, पर सिर्फ़ same city और menu version में।

---

## 💻 Code Example — Basic
```python
# Pure-Python semantic cache using a toy bag-of-words embedding (no installs; real systems use a neural embedding model)
import math  # for sqrt
from collections import Counter  # word counts


def embed(text: str) -> Counter:
    """Toy embedding: word-count vector (illustrative only)."""
    return Counter(text.lower().split())  # count each word


def cosine(a: Counter, b: Counter) -> float:
    """Cosine similarity between two sparse vectors."""
    dot = sum(a[w] * b[w] for w in a if w in b)  # shared word weights
    na = math.sqrt(sum(v * v for v in a.values()))  # norm of a
    nb = math.sqrt(sum(v * v for v in b.values()))  # norm of b
    return dot / (na * nb) if na and nb else 0.0  # avoid divide by zero


class SemanticCache:
    def __init__(self, threshold: float = 0.7) -> None:
        self.threshold = threshold  # minimum similarity for a hit
        self.items: list[tuple[Counter, str]] = []  # (embedding, answer)

    def get(self, query: str) -> str | None:
        q = embed(query)  # embed query
        best_score, best_answer = 0.0, None  # track best match
        for emb, ans in self.items:  # linear scan (use an ANN index in production)
            s = cosine(q, emb)  # similarity
            if s > best_score:  # better match
                best_score, best_answer = s, ans  # update
        return best_answer if best_score >= self.threshold else None  # apply threshold

    def put(self, query: str, answer: str) -> None:
        self.items.append((embed(query), answer))  # store


if __name__ == "__main__":
    c = SemanticCache(threshold=0.7)  # create cache
    c.put("hs code for wireless earbuds", "8518.30")  # seed
    print(c.get("what is the hs code for wireless earbuds"))  # similar -> 8518.30
    print(c.get("hs code for cotton shirts"))  # different -> None
```

## 💻 Code Example — Advanced
```python
# Production-style async semantic cache with a pluggable embedder and vector store (interfaces shown; implement with your stack)
import logging  # logs
import time  # TTL
from dataclasses import dataclass  # records
from typing import Awaitable, Callable, Optional, Protocol  # typing helpers

logger = logging.getLogger("semcache")  # logger


class VectorStore(Protocol):
    async def search(self, vec: list[float], k: int, filters: dict[str, str]) -> list[tuple[float, dict]]: ...  # (score, payload)
    async def upsert(self, vec: list[float], payload: dict) -> None: ...  # store


@dataclass
class SemanticCacheConfig:
    threshold: float = 0.93  # high = safer
    ttl_seconds: int = 86_400  # freshness


class SemanticLLMCache:
    def __init__(
        self,
        embed: Callable[[str], Awaitable[list[float]]],  # async embedding function
        store: VectorStore,  # vector index
        cfg: SemanticCacheConfig = SemanticCacheConfig(),
    ) -> None:
        self.embed, self.store, self.cfg = embed, store, cfg  # keep deps

    async def ask(
        self, query: str, llm: Callable[[str], Awaitable[str]], filters: dict[str, str]
    ) -> tuple[str, bool]:
        vec: Optional[list[float]] = None  # embedding holder
        try:
            vec = await self.embed(query)  # embed (small token cost)
            hits = await self.store.search(vec, 1, filters)  # nearest neighbour within filters
            if hits and hits[0][0] >= self.cfg.threshold:  # similarity check
                payload = hits[0][1]  # stored record
                if payload["expires_at"] > time.time():  # still fresh
                    return payload["answer"], True  # cache hit
        except Exception as exc:  # fail open on any cache problem
            logger.warning("semantic cache lookup failed: %s", exc)  # log
        answer = await llm(query)  # real model call
        if vec is not None:  # store only if embedding worked
            try:
                await self.store.upsert(vec, {
                    "query": query, "answer": answer, **filters,  # data + filter fields
                    "expires_at": time.time() + self.cfg.ttl_seconds,  # expiry
                })
            except Exception as exc:  # ignore write errors
                logger.warning("semantic cache write failed: %s", exc)  # log
        return answer, False  # fresh answer
```
Token usage: a lookup costs embedding tokens only (a short query, a few dozen tokens at embedding prices, far below generation prices). A hit saves all generation tokens.

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI  # web framework
from pydantic import BaseModel  # validation

app = FastAPI()  # app
cache = SemanticCache(threshold=0.7)  # basic cache from the first example (use SemanticLLMCache in production)


class Q(BaseModel):
    query: str  # question
    country: str = "IN"  # filter dimension


@app.post("/ask")
async def ask(q: Q) -> dict:
    hit = cache.get(f"{q.country} {q.query}")  # include country so countries never share answers
    if hit is not None:  # semantic hit
        return {"answer": hit, "cached": True}  # instant
    answer = "8518.30"  # placeholder for `await llm.ainvoke(...)`
    cache.put(f"{q.country} {q.query}", answer)  # store
    return {"answer": answer, "cached": False}  # fresh
```

---

## 🔗 LangChain / LangGraph Connection
LangChain offers semantic cache classes (for example `RedisSemanticCache` in `langchain-community`) that take an embedding model and a score threshold. Class names and arguments vary by version; verify in the docs.

```python
from langchain_core.globals import set_llm_cache  # global setter
from langchain_community.cache import RedisSemanticCache  # semantic cache (needs Redis with vector search)
from langchain_openai import OpenAIEmbeddings  # embedding model

set_llm_cache(RedisSemanticCache(
    redis_url="redis://localhost:6379",  # Redis server
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),  # embedder
    score_threshold=0.1,  # distance threshold in this class (lower = stricter); check docs
))
# Any ChatOpenAI call now checks the semantic cache first.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Threshold too low, returning wrong answers confidently
✅ Correct: Start strict (0.92-0.95), measure false-hit rate on labelled pairs, loosen carefully.
```python
# Wrong
SemanticCache(threshold=0.5)  # "earbuds" matches "earbud charger"
# Right
SemanticCache(threshold=0.93)  # then tune with a labelled set
```

❌ Mistake 2: Sharing hits across tenants, countries or data versions
✅ Correct: Apply metadata filters (tenant, country, schedule version) before similarity.
```python
# Wrong: search all entries
hits = await store.search(vec, 1, {})
# Right
hits = await store.search(vec, 1, {"tenant": tenant, "schedule": "2026-10"})
```

---

## 🧠 Tricky Interview Question
**Q**: "Your semantic cache saves 55% of LLM spend, but a compliance review finds some importers received another country's duty rate. How did it happen and how do you prevent it?"

**Answer**: Embeddings capture topic, not every critical detail: "duty on laptops to India" and "duty on laptops to USA" are very close vectors, so one answer was reused for the other. Prevention: put critical attributes (country, date, tenant) in metadata filters or in the cache key, never rely on similarity for them; raise the threshold; add a cheap verification step (extract entities from both queries and require they match); exclude high-risk categories from semantic caching; log and audit hits with sampled human review.

---

## ⚫ Interview Questions + Answers

Q1: What is semantic caching?
A1: Reusing cached answers when a new query is semantically similar, found through embedding similarity.

Q2: What is the main risk?
A2: False hits: similar-looking queries with different correct answers.

Q3: How do you pick the similarity threshold?
A3: Build a labelled set of query pairs (same answer or not), plot precision and recall against threshold, and choose the point meeting your false-hit tolerance. Re-check after embedding model changes.

Q4: Does semantic caching cost tokens?
A4: Yes, a small embedding cost per lookup, much less than a generation call. Hits remove generation cost.

Q5: Compare exact, semantic and provider prompt caching.
A5: Exact: safest, low hit rate. Semantic: higher hit rate, risk of wrong matches, needs embeddings and a vector index. Provider prompt caching: still calls the model but discounts repeated prompt prefix tokens and reduces latency; it works with unique questions. A good system layers them: exact first, semantic for safe categories, provider caching for long shared prompts.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many paraphrased FAQ-style queries
- Wrong-answer risk is low or can be filtered by metadata
- Generation is costly or slow

❌ Avoid when:
- Small differences change the correct answer (legal, medical, pricing, duty rates) and cannot be filtered
- Personalised or real-time answers
- Query volume is too low for savings to cover embedding and index costs

---

## 📊 Visual Diagram
```
 query --> embed --> vector [0.12, -0.4, ...]
                         |
                 nearest neighbour search  (filters: tenant, country, version)
                         |
                 best score s
              +----------+-----------+
              | s >= 0.93            | s < 0.93
              v                      v
        return stored answer     call LLM, then store
        (no generation tokens)   (query vector + answer + TTL)
```

---

## 💰 Cost Impact
Per request you pay embedding tokens (small) plus vector search (infra). On a hit you save the full generation. Illustrative: 100K queries/day, exact cache hit 20%, semantic adds 35% more hits: if a generation call costs $0.0004, the extra 35K hits save about $14/day, while embedding 100K short queries (about 30 tokens each = 3M tokens at an illustrative $0.02/1M) costs about $0.06/day. Net positive, if quality holds.

Optimise: check exact cache first (cheaper), cache embeddings, use a small embedding model, tight threshold, TTL, and monitor false-hit rate via sampled review.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Vector of meaning | अर्थ का vector |
| Cosine similarity | Angle-based closeness | Vectors की समानता |
| Threshold | Minimum score for a hit | Hit के लिए न्यूनतम score |
| False hit | Wrong cached answer used | ग़लत cached answer का use |
| ANN index | Fast approximate nearest neighbour | तेज़ nearest-neighbour search |
| Metadata filter | Restrict by attributes | Attributes से सीमित करना |
| Paraphrase | Same meaning, other words | वही अर्थ, अलग शब्द |

---

## ⚡ 3-Line Summary
English: Semantic caching reuses answers for queries with similar meaning using embeddings and a similarity threshold. It raises hit rate but risks wrong matches, so use strict thresholds and metadata filters. Layer it after exact caching.
Hindi: Semantic caching embeddings और similarity threshold से समान अर्थ वाले queries के answers reuse करता है। इससे hit rate बढ़ता है पर ग़लत match का risk है, इसलिए strict threshold और metadata filters रखो। इसे exact caching के बाद layer करो।

---

## ➡️ Next Topic
**444. Redis for LLM Caching** — the most common production store for both exact and semantic caches.
