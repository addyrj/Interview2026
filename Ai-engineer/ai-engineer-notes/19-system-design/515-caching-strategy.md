---

# 515. Caching Strategy
# हिंदी में: Caching Strategy

---

## 🔵 Simple Definition (English)
Caching stores results of earlier work so repeated requests are answered instantly and for free. In AI systems you can cache at several layers: exact response cache, semantic cache (similar questions), embedding cache, retrieval cache, and provider prompt caching for long repeated prefixes.

## 🔵 सरल परिभाषा (Hindi)
Caching पिछले काम के results store करता है ताकि दोहराए गए requests तुरंत और मुफ़्त में जवाब पाएँ। AI systems में कई layers पर cache हो सकता है: exact response cache, semantic cache (मिलते-जुलते सवाल), embedding cache, retrieval cache, और लंबे दोहराए prefix के लिए provider prompt caching।

---

## 🔴 Problem it Solves
LLM calls are slow (seconds) and cost tokens. Many users ask the same or nearly the same questions. Without caching you pay repeatedly and overload the model during spikes.

## 🔴 यह क्यों बना? (Hindi)
LLM calls धीमी (सेकंड) और token-महँगी हैं। कई users वही या मिलते-जुलते सवाल पूछते हैं। Cache के बिना बार-बार पैसे देते हैं और spikes में model पर बोझ बढ़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Normalise the request (trim, lowercase, remove noise) and build a key
Step 2 → Include everything that changes the answer in the key: tenant, country, year, model, prompt version
Step 3 → L1: exact-match cache lookup (Redis / in-memory) -> hit: return
Step 4 → L2: semantic cache: embed query, find similar past query above threshold (e.g. 0.95) -> hit: return
Step 5 → Miss: run retrieval + LLM; store result with a TTL
Step 6 → Invalidate when source data or prompts change (version in key)
Step 7 → Track hit rate, savings, and wrong-hit incidents
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request normalise करो और key बनाओ
Step 2 → Key में वो सब रखो जो जवाब बदलता है: tenant, country, year, model, prompt version
Step 3 → L1: exact-match cache (Redis / memory) → hit तो return
Step 4 → L2: semantic cache: query embed करो, threshold (जैसे 0.95) से ऊपर similar मिले तो return
Step 5 → Miss: retrieval + LLM चलाओ, TTL के साथ store करो
Step 6 → Source data या prompt बदले तो invalidate करो (key में version)
Step 7 → Hit rate, बचत और गलत-hit incidents track करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: "HS code for iPhone 15" is asked hundreds of times a day. An exact cache (key includes country and tariff year) answers in 2 ms. "Which HS code applies to Apple iPhone 15 phones?" hits the semantic cache. When the tariff schedule updates in January, the tariff_year in the key changes and old answers are never served.
**Zomato-style example**: "Is this restaurant open now?" must NOT be cached for long; real-time data needs a tiny TTL or no cache.

## 🟡 Real Example Hindi mein
**Tariff System**: "iPhone 15 का HS code" दिन में सैकड़ों बार पूछा जाता है। Exact cache (key में country और tariff year) 2 ms में जवाब देता है। "Apple iPhone 15 phones पर कौन सा HS code लगेगा?" semantic cache hit करता है। जनवरी में tariff schedule बदलता है तो key का tariff_year बदल जाता है और पुराने जवाब नहीं दिखते।

---

## 💻 Code Example — Basic
```python
# Basic: exact-match cache with TTL (pure Python, offline)
import time  # for expiry checks


class TTLCache:  # tiny cache with expiry
    def __init__(self, ttl_seconds: float) -> None:  # set default TTL
        self.ttl = ttl_seconds  # remember
        self.store: dict[str, tuple[float, str]] = {}  # key -> (expires_at, value)

    def get(self, key: str) -> str | None:  # read
        item = self.store.get(key)  # lookup
        if item is None:  # not found
            return None  # miss
        expires, value = item  # unpack
        if time.time() > expires:  # expired
            del self.store[key]  # evict
            return None  # miss
        return value  # hit

    def set(self, key: str, value: str) -> None:  # write
        self.store[key] = (time.time() + self.ttl, value)  # store with expiry


cache = TTLCache(ttl_seconds=60)  # create
key = "IN|2025|iphone 15"  # key includes country and year
print(cache.get(key))  # None (miss)
cache.set(key, "8517.13")  # store
print(cache.get(key))  # 8517.13 (hit)
```

## 💻 Code Example — Advanced
```python
# Advanced: async two-level cache (exact + semantic) with single-flight to prevent stampedes
import asyncio  # async runtime
import math  # cosine

EXACT: dict[str, str] = {}  # L1
SEM: list[tuple[list[float], str]] = []  # L2: (embedding, answer)
INFLIGHT: dict[str, asyncio.Future[str]] = {}  # requests currently being computed


def embed(text: str) -> list[float]:  # toy embedding: letter histogram (replace with a real model)
    v = [0.0] * 26  # 26 letters
    for ch in text.lower():  # count letters
        if "a" <= ch <= "z":  # only letters
            v[ord(ch) - 97] += 1  # increment
    return v  # vector


def cos(a: list[float], b: list[float]) -> float:  # cosine similarity
    d = sum(x * y for x, y in zip(a, b))  # dot
    n = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))  # norms
    return d / n if n else 0.0  # safe


async def llm(q: str) -> str:  # mock expensive call
    await asyncio.sleep(0.05)  # simulate latency
    return f"answer({q})"  # fake answer


async def cached_answer(q: str, key_ctx: str, threshold: float = 0.97) -> str:  # main entry
    key = f"{key_ctx}|{q.strip().lower()}"  # exact key with context
    if key in EXACT:  # L1 hit
        return EXACT[key]  # fast path
    qv = embed(q)  # embed query
    for vec, ans in SEM:  # L2 scan (use a vector index in production)
        if cos(qv, vec) >= threshold:  # similar enough
            return ans  # semantic hit
    if key in INFLIGHT:  # someone already computing this
        return await INFLIGHT[key]  # wait, don't duplicate the LLM call
    fut: asyncio.Future[str] = asyncio.get_running_loop().create_future()  # shared future
    INFLIGHT[key] = fut  # register
    try:
        ans = await asyncio.wait_for(llm(q), timeout=5)  # compute with timeout
        EXACT[key] = ans  # fill L1
        SEM.append((qv, ans))  # fill L2
        fut.set_result(ans)  # wake waiters
        return ans  # result
    except Exception as exc:  # failure
        fut.set_exception(exc)  # propagate to waiters
        raise  # re-raise
    finally:
        INFLIGHT.pop(key, None)  # cleanup


async def main() -> None:  # demo: 3 identical concurrent requests cause one LLM call
    print(await asyncio.gather(*(cached_answer("hs code iphone", "IN|2025") for _ in range(3))))  # run


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Use a dependency for the cache client, set `Cache-Control` appropriately, and report `x-cache: HIT/MISS` for observability. Use Redis in production (`redis.asyncio`).

```python
from fastapi import FastAPI, Response  # app, response object
from pydantic import BaseModel  # schema

app = FastAPI()  # app
CACHE: dict[str, str] = {}  # replace with Redis


class Q(BaseModel):  # request
    text: str  # question
    country: str  # part of key
    tariff_year: int  # part of key


@app.post("/classify")  # route
async def classify(q: Q, resp: Response) -> dict[str, str]:
    key = f"{q.country}|{q.tariff_year}|{q.text.strip().lower()}"  # key with context
    if key in CACHE:  # hit
        resp.headers["x-cache"] = "HIT"  # observability
        return {"answer": CACHE[key]}  # return cached
    CACHE[key] = "8517.13"  # replace with the real pipeline
    resp.headers["x-cache"] = "MISS"  # observability
    return {"answer": CACHE[key]}  # return fresh
```

---

## 🔗 LangChain / LangGraph Connection
LangChain supports LLM caching via `set_llm_cache` with `InMemoryCache` (and SQLite/Redis integrations). LangChain has semantic caches in community integrations. Anthropic and OpenAI offer provider-side prompt caching for long static prefixes (check current docs for rules and pricing).

```python
from langchain_core.caches import InMemoryCache  # real class
from langchain_core.globals import set_llm_cache  # real function
from langchain_core.language_models.fake_chat_models import FakeListChatModel  # offline fake chat model

set_llm_cache(InMemoryCache())  # enable exact-match LLM cache globally
llm = FakeListChatModel(responses=["first", "second"])  # fake model returns responses in order
print(llm.invoke("hs code iphone").content)  # computed: "first"
print(llm.invoke("hs code iphone").content)  # served from cache: "first" again
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Cache key missing context
✅ Correct: include tenant, country, year, model and prompt version.
```python
# Wrong
key = question  # tenant A's answer served to tenant B
# Right
key = f"{tenant}|{country}|{year}|{prompt_ver}|{question}"  # safe
```

❌ Mistake 2: Semantic threshold too low
✅ Correct: start at 0.95+, review wrong hits ("Is X allowed?" vs "Is X banned?").
```python
# Wrong
if cos(q, cached) > 0.7: return cached  # wrong answers
# Right
if cos(q, cached) > 0.95 and same_context: return cached  # strict
```

---

## 🧠 Tricky Interview Question
**Q**: "Your semantic cache has a 40% hit rate but users complain about wrong answers. Why?"

**Answer**: Similarity threshold too loose or context missing from the cache key. Questions differing in a key detail (country, year, negation, numbers) embed close together but need different answers. Fixes: stricter threshold, keep exact-key fields in the match condition, cache only stable question types, add a verifier or short TTL, and log hits for sampled review.

---

## ⚫ Interview Questions + Answers

Q1: Why cache LLM responses? (Easy)
A1: To cut latency and cost for repeated questions and reduce load on the model.

Q2: What is TTL? (Easy)
A2: Time to live: how long a cached item stays valid before expiring.

Q3: Exact vs semantic cache? (Medium)
A3: Exact matches the same normalised string (safe, lower hit rate). Semantic matches similar meaning via embeddings (higher hit rate, risk of wrong hits).

Q4: What is provider prompt caching? (Medium)
A4: The provider reuses processing of a repeated long prompt prefix (like a big system prompt or documents), reducing cost and latency for that prefix. Rules, minimum lengths and prices vary by provider.

Q5: How do you prevent a cache stampede? (Hard)
A5: Single-flight (only one request computes while others wait), jittered TTLs, background refresh before expiry (stale-while-revalidate), and per-key locks in Redis.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Repeated or near-duplicate questions, stable data

❌ Avoid when:
- Real-time or personalised answers (live status, user-specific data) unless key includes user and TTL is tiny
- Compliance rules forbid storing responses

---

## 📊 Visual Diagram
```
 request ─▶ normalise + key(tenant,country,year,version)
              │
              ▼
        L1 exact cache ──hit──▶ answer (≈2 ms)
              │miss
              ▼
        L2 semantic cache ──hit (sim ≥ 0.95)──▶ answer (≈20 ms)
              │miss
              ▼
        retrieval + LLM (seconds, tokens) ──▶ store in L1+L2 (TTL) ──▶ answer
```

---

## 💰 Cost Impact
Each hit saves the full LLM cost. If 100,000 requests/day cost $0.002 each ($200/day, illustrative) and the hit rate is 35%, savings are about $70/day. Cache storage is small compared with that. Semantic cache adds an embedding call per request (cheap).
Optimise: raise hit rate with normalisation, cache expensive steps (embeddings, retrieval) too, use provider prompt caching for long static prompts, monitor wrong-hit rate so savings don't cost quality.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache hit/miss | Found / not found | मिला / नहीं मिला |
| TTL | Expiry time | समाप्ति समय |
| Semantic cache | Match by meaning | अर्थ से match |
| Invalidation | Removing stale entries | पुराना हटाना |
| Stampede | Many misses at once | एक साथ कई misses |
| Hit rate | Share of requests served from cache | cache से मिले requests का हिस्सा |

---

## ⚡ 3-Line Summary
English: Cache at several layers: exact, semantic, embeddings, retrieval, and provider prompt cache.
Put tenant, country, year and prompt version in the key and set sensible TTLs.
Watch hit rate and wrong hits; never cache real-time data blindly.
Hindi: कई layers पर cache करो: exact, semantic, embeddings, retrieval, provider prompt cache।
Key में tenant, country, year, prompt version रखो और सही TTL लगाओ।
Hit rate और गलत hits देखो; real-time data को आँख बंद करके cache मत करो।

---

## ➡️ Next Topic
**516. Scalability in AI Systems** — handling growth in users, data and tokens.
