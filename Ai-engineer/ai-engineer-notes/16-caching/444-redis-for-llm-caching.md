---

# 444. Redis for LLM Caching
# हिंदी में: LLM Caching के लिए Redis

---

## 🔵 Simple Definition (English)
Redis is a very fast in-memory key-value store. For LLM apps, you save the model's answer under a key built from the prompt, so the same question next time is answered from Redis in ~1 ms instead of an LLM call that takes 1-3 seconds and costs tokens. Redis also gives TTL (auto-expiry) and works across many servers.

## 🔵 सरल परिभाषा (Hindi)
Redis एक बहुत तेज़ in-memory key-value store है। LLM app में हम prompt से बनी key के नीचे model का जवाब save कर देते हैं। अगली बार वही सवाल आए तो जवाब ~1 ms में Redis से मिलता है, LLM call (1-3 सेकंड + tokens का खर्च) नहीं करनी पड़ती। Redis में TTL (auto-expiry) भी है और यह कई servers के बीच share होता है।

---

## 🔴 Problem it Solves
- A Python `dict` cache lives inside one process. With 4 Uvicorn workers or 10 pods, each has its own cache, so hit rate is low and the cache dies on every restart.
- LLM calls are slow and paid per token. Many users ask the same thing (for example the HS code of "cotton t-shirt").
- Without TTL, stale answers (old tariff rates) live forever.

## 🔴 यह क्यों बना? (Hindi)
- Python `dict` cache सिर्फ़ एक process में रहता है। 4 workers या 10 pods हों तो हर एक का अलग cache, hit rate कम और restart पर सब गायब।
- LLM call धीमी और token के हिसाब से महंगी है। बहुत users एक जैसे सवाल पूछते हैं।
- TTL के बिना पुराने जवाब (पुराने tariff rates) हमेशा रह जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives: model + messages + params
Step 2 → Build a deterministic key: "llm:v1:" + sha256(normalised request)
Step 3 → GET key from Redis
Step 4 → HIT  → return cached answer (about 1 ms, 0 tokens)
Step 5 → MISS → call the LLM (1-3 s, tokens charged)
Step 6 → SET key = answer with EX=ttl seconds (only if the call succeeded)
Step 7 → Next identical request hits the cache; Redis evicts by TTL / maxmemory policy
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Request आती है: model + messages + params
Step 2 → पक्की (deterministic) key बनाओ: "llm:v1:" + sha256(normalised request)
Step 3 → Redis से GET key
Step 4 → HIT  → cached जवाब लौटाओ (~1 ms, 0 tokens)
Step 5 → MISS → LLM call करो (1-3 s, tokens का खर्च)
Step 6 → सफल होने पर ही SET key = जवाब, EX=ttl सेकंड
Step 7 → अगली वही request cache से; Redis TTL / maxmemory policy से पुराना हटाता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: Importers repeatedly ask "HS code for stainless steel water bottle". The first call costs ~600 input + 150 output tokens. We store the JSON answer in Redis with a 24 hour TTL (tariff schedules change rarely). The next 500 identical lookups that day cost zero tokens and return in 2 ms.
**Zomato AI**: "Is this restaurant veg-friendly?" summaries are cached per restaurant id for 6 hours, so a viral restaurant page does not trigger thousands of LLM calls.

## 🟡 Real Example Hindi mein
**Tariff System**: Importers बार-बार पूछते हैं "stainless steel water bottle का HS code"। पहली call में ~600 input + 150 output tokens लगते हैं। JSON जवाब 24 घंटे के TTL के साथ Redis में रखते हैं (tariff schedule कम बदलता है)। उस दिन के अगले 500 वैसे ही सवाल 0 token में 2 ms में मिलते हैं।
**Zomato AI**: "क्या यह restaurant veg-friendly है?" की summary restaurant id के हिसाब से 6 घंटे cache होती है, ताकि viral page पर हज़ारों LLM calls न हों।

---

## 💻 Code Example — Basic
```python
# Basic Redis-style LLM cache. Runs offline: we use a tiny fake Redis (dict + expiry)
# so the logic is identical to real redis-py: get / set(ex=ttl).
import hashlib  # to hash the prompt into a fixed-size key
import json  # to serialise the request deterministically
import time  # to simulate expiry


class FakeRedis:
    """Minimal stand-in for redis.Redis(decode_responses=True)."""

    def __init__(self) -> None:
        self.store: dict[str, tuple[str, float]] = {}  # key -> (value, expires_at)

    def get(self, key: str) -> str | None:
        item = self.store.get(key)  # look the key up
        if item is None:  # not stored
            return None
        value, expires_at = item  # unpack the tuple
        if time.time() > expires_at:  # TTL passed
            del self.store[key]  # expire it like Redis does
            return None
        return value  # fresh value

    def set(self, key: str, value: str, ex: int) -> None:
        self.store[key] = (value, time.time() + ex)  # save with expiry time


def make_key(model: str, prompt: str) -> str:
    payload = json.dumps({"m": model, "p": prompt.strip().lower()}, sort_keys=True)  # stable JSON
    return "llm:v1:" + hashlib.sha256(payload.encode()).hexdigest()  # prefix + hash


def fake_llm(prompt: str) -> str:
    return f"HS 7323.93 for: {prompt}"  # pretend LLM answer


calls = 0  # count real LLM calls


def cached_answer(r: FakeRedis, prompt: str) -> str:
    global calls  # we mutate the counter
    key = make_key("gpt-4o-mini", prompt)  # build the key
    hit = r.get(key)  # try the cache first
    if hit is not None:  # cache hit
        return hit  # no LLM call
    calls += 1  # a real call happens
    answer = fake_llm(prompt)  # call the model
    r.set(key, answer, ex=60)  # store for 60 seconds
    return answer  # return fresh answer


if __name__ == "__main__":
    r = FakeRedis()  # create the fake store
    for q in ["Steel bottle HS code", "steel bottle hs code ", "Steel bottle HS code"]:
        print(cached_answer(r, q))  # all three map to the same key
    print("LLM calls made:", calls)  # expect 1
```

## 💻 Code Example — Advanced
```python
# Production: async redis-py (redis>=5) + OpenAI, with error handling, TTL jitter and fail-open.
# pip install "redis>=5" openai
from __future__ import annotations

import hashlib  # key hashing
import json  # serialisation
import logging  # log cache problems
import random  # TTL jitter
from typing import Any

import redis.asyncio as redis  # asyncio client shipped inside redis-py
from openai import AsyncOpenAI, APIError  # async OpenAI client + base error

log = logging.getLogger("llm_cache")  # module logger


class RedisLLMCache:
    """Cache-aside wrapper around an async LLM call."""

    def __init__(self, url: str = "redis://localhost:6379/0", ttl: int = 86_400) -> None:
        self.r = redis.from_url(url, decode_responses=True)  # pooled async client
        self.llm = AsyncOpenAI()  # reads OPENAI_API_KEY from env
        self.ttl = ttl  # base TTL in seconds

    @staticmethod
    def key(model: str, messages: list[dict[str, str]], temperature: float) -> str:
        blob = json.dumps(  # canonical JSON: sorted keys, no spaces
            {"m": model, "msg": messages, "t": temperature}, sort_keys=True, separators=(",", ":")
        )
        return "llm:v1:" + hashlib.sha256(blob.encode()).hexdigest()  # namespaced key

    async def ask(self, messages: list[dict[str, str]], model: str = "gpt-4o-mini") -> dict[str, Any]:
        temperature = 0.0  # only cache deterministic calls
        k = self.key(model, messages, temperature)  # compute key
        try:
            cached = await self.r.get(k)  # 1) try Redis
            if cached is not None:  # hit
                return {**json.loads(cached), "cache": "hit"}  # zero tokens
        except redis.RedisError as exc:  # Redis down -> fail open, never break the app
            log.warning("redis get failed: %s", exc)

        try:
            resp = await self.llm.chat.completions.create(  # 2) miss -> call LLM
                model=model, messages=messages, temperature=temperature, max_tokens=300
            )
        except APIError as exc:  # LLM error: do NOT cache it
            log.error("llm failed: %s", exc)
            raise

        result = {  # data worth caching
            "answer": resp.choices[0].message.content,
            "tokens": resp.usage.total_tokens if resp.usage else 0,
        }
        try:
            ttl = int(self.ttl * random.uniform(0.9, 1.1))  # jitter avoids mass expiry together
            await self.r.set(k, json.dumps(result), ex=ttl)  # 3) store with TTL
        except redis.RedisError as exc:
            log.warning("redis set failed: %s", exc)  # still return the answer
        return {**result, "cache": "miss"}
```

---

## 🟠 FastAPI Integration
Create one Redis client at startup (lifespan) and share it through the app. Never create a client per request.

```python
from contextlib import asynccontextmanager  # lifespan helper
from typing import Any

from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel  # request validation (pydantic v2)

cache: RedisLLMCache | None = None  # reuses the class above


@asynccontextmanager
async def lifespan(app: FastAPI):
    global cache
    cache = RedisLLMCache()  # open pool once
    yield  # app runs here
    await cache.r.aclose()  # close pool on shutdown


app = FastAPI(lifespan=lifespan)  # attach lifespan


class ClassifyIn(BaseModel):
    product: str  # product description


@app.post("/classify")
async def classify(body: ClassifyIn) -> dict[str, Any]:
    assert cache is not None  # set by lifespan
    messages = [
        {"role": "system", "content": "Return the HS code and one-line reason."},
        {"role": "user", "content": body.product},
    ]
    try:
        return await cache.ask(messages)  # cache-aside call
    except Exception as exc:  # map LLM failure to HTTP 502
        raise HTTPException(status_code=502, detail="LLM unavailable") from exc
```

---

## 🔗 LangChain / LangGraph Connection
LangChain ships `RedisCache` in `langchain_community.cache`. Set it globally once and every `ChatOpenAI` call is cached by (prompt, llm-params).

```python
# pip install langchain-openai langchain-community redis
import redis  # sync redis client (RedisCache uses sync API)
from langchain_community.cache import RedisCache  # Redis-backed LLM cache
from langchain_core.globals import set_llm_cache  # global cache setter
from langchain_openai import ChatOpenAI  # chat model

set_llm_cache(RedisCache(redis_=redis.Redis.from_url("redis://localhost:6379/1"), ttl=86_400))  # global cache, 1 day
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # temperature 0 -> cache-friendly
print(llm.invoke("HS code for cotton t-shirt?").content)  # miss -> LLM
print(llm.invoke("HS code for cotton t-shirt?").content)  # hit -> Redis
# In LangGraph the same global cache applies to every LLM node; node-level cache policies also exist.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the raw prompt as key and no TTL
✅ Correct: hash a canonical JSON that includes model + params, and always set a TTL.

```python
# Wrong: huge keys, ignores model/temperature, lives forever
await r.set(prompt, answer)
# Right: namespaced hash key + expiry
await r.set("llm:v1:" + hashlib.sha256(blob.encode()).hexdigest(), answer, ex=86_400)
```

❌ Mistake 2: Letting a Redis outage take the whole API down
✅ Correct: catch `redis.RedisError` and fall through to the LLM (fail open).

```python
# Wrong: exception propagates -> 500 for every user
cached = await r.get(k)
# Right: treat cache as optional
try:
    cached = await r.get(k)
except redis.RedisError:
    cached = None
```

---

## 🧠 Tricky Interview Question
**Q**: "You added Redis caching with temperature=0.7 and the hit rate is great, but users complain every answer looks identical. Is that a bug?"

**Answer**: It is expected. A cache returns the stored sample, so the randomness of temperature is removed. For classification, extraction and FAQ this is good (consistency, cost). For creative tasks it is wrong. Decide per endpoint: cache only deterministic calls (temperature 0), or include a `variant` number in the key and rotate between N stored answers.

---

## ⚫ Interview Questions + Answers

Q1: Why use Redis instead of a Python dict for LLM caching? (Easy)
A1: A dict is per process and lost on restart. Redis is shared by all workers/pods, persists optionally, has TTL and eviction, and handles concurrent access.

Q2: What is cache-aside? (Easy)
A2: App checks cache first; on miss it calls the source (LLM), then writes the result to cache. The cache never calls the LLM itself.

Q3: How do you stop many identical requests from calling the LLM at the same moment (cache stampede)? (Medium)
A3: Use a short lock (`SET lock:key 1 NX EX 30`). The first request holds the lock and calls the LLM; others wait briefly and re-read the cache. Add TTL jitter so keys do not expire together.

Q4: What should be in the cache key? (Medium)
A4: Model name, full messages, temperature/top_p, max_tokens, tools/response schema, and a prompt-version number. Anything that changes the output must be in the key.

Q5: Redis memory is full. What happens and how do you design for it? (Hard)
A5: With `maxmemory` set, Redis evicts per `maxmemory-policy`. For a pure cache use `allkeys-lru` (or `allkeys-lfu`). Without a policy writes fail with OOM errors. Also keep values small (store the answer, not the full API response), set TTLs, and monitor `evicted_keys` and hit rate.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multiple API workers/pods need one shared cache
- Same or similar queries repeat often (FAQ, classification)
- You need TTL and eviction built in

❌ Avoid when:
- Every request is unique or creative (hit rate near 0)
- Answers contain private data and you have no isolation plan (see topics 457 and 458)
- A single-process script where `functools.lru_cache` is enough

---

## 📊 Visual Diagram
```
 Client ──► FastAPI ──► key = sha256(model+messages+params)
                          │
                          ▼
                    ┌───────────┐  hit   ┌──────────────┐
                    │   Redis   │──────► │ return ~1 ms │
                    └───────────┘        └──────────────┘
                          │ miss
                          ▼
                    ┌───────────┐  answer  ┌──────────────┐
                    │    LLM    │────────► │ SET key EX t │──► return
                    └───────────┘          └──────────────┘
```

---

## 💰 Cost Impact
**Token usage**: a hit uses 0 LLM tokens. Example: 600 input + 150 output on gpt-4o-mini costs about $0.00018 per miss. With 100,000 lookups a day and a 60 percent hit rate, 60,000 calls are saved (about $10.8 a day, around $320 a month).
**Optimisation**: cache only temperature 0 calls, use long TTL for stable data, normalise prompts (trim, lowercase) to raise hit rate, store compact answers, and watch Redis memory cost against LLM savings.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache-aside | App reads cache first, fills on miss | पहले cache देखो, miss पर भरो |
| TTL | Time before a key expires | key कितनी देर रहेगी |
| Eviction | Removing keys when memory is full | memory भरने पर keys हटाना |
| Cache stampede | Many misses at once for one key | एक key पर एक साथ कई misses |
| Fail open | App works even if cache fails | cache खराब हो तब भी app चले |
| Hit rate | Hits divided by total requests | कितने requests cache से मिले |

---

## ⚡ 3-Line Summary
English: Redis gives a shared, fast, expiring cache for LLM answers. Build a canonical hashed key, set a TTL, cache only successful deterministic calls and fail open. Every hit saves tokens and 1-3 seconds of latency.
Hindi: Redis LLM जवाबों के लिए shared, तेज़ और expire होने वाला cache देता है। Canonical hashed key बनाओ, TTL लगाओ, सिर्फ़ सफल deterministic calls cache करो और Redis fail हो तो भी app चलाओ। हर hit पर tokens और 1-3 सेकंड बचते हैं।

---

## ➡️ Next Topic
**445. GPTCache Library** — a ready-made library that adds semantic (similar-meaning) caching on top of this exact-match idea.
