---

# 015. FastAPI + Redis Integration
# हिंदी में: FastAPI + Redis Integration

---

## 🔵 Simple Definition (English)
Redis is a very fast in-memory key-value store. With FastAPI it is used for caching LLM answers, rate limiting, per-user token counters, sessions and job status. The async client is `redis.asyncio` (part of the `redis` package, version 4.2 and later).

## 🔵 सरल परिभाषा (Hindi)
Redis बहुत तेज़ in-memory key-value store है। FastAPI के साथ यह LLM answers को cache करने, rate limiting, प्रति user token counters, sessions और job status के लिए use होता है। Async client `redis.asyncio` है (`redis` package के version 4.2 और बाद में शामिल)।

---

## 🔴 Problem it Solves
LLM calls are slow (seconds) and cost money, and many users ask the same question. Postgres is durable but too slow for per-request counters. Redis answers in under a millisecond, so you can check a cache before paying for tokens, count requests atomically, and expire data automatically with TTL.

## 🔴 यह क्यों बना? (Hindi)
LLM calls धीमी (seconds) और महंगी हैं, और कई users एक ही सवाल पूछते हैं। Postgres durable है पर हर request के counters के लिए धीमा। Redis एक millisecond से कम में जवाब देता है, इसलिए tokens खर्च करने से पहले cache देखो, requests atomically गिनो, और TTL से data अपने आप expire करो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → At startup create a client: redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)
Step 2 → Build a stable cache key: "tariff:v3:" + sha256(normalised_description + model + prompt_version)
Step 3 → GET key → if found, return it (cache hit: 0 tokens, ~1 ms)
Step 4 → If missing, call the LLM, then SET key value EX 86400 (expires in 1 day)
Step 5 → Rate limit: INCR "rl:user:minute" ; on first hit EXPIRE 60 ; if count > limit → 429
Step 6 → Token budget: INCRBY "tokens:user:day" used_tokens (atomic, safe under concurrency)
Step 7 → On shutdown: await client.aclose()
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Startup पर client बनाओ: redis.asyncio.from_url("redis://localhost:6379", decode_responses=True)
Step 2 → स्थिर cache key बनाओ: "tariff:v3:" + sha256(normalised_description + model + prompt_version)
Step 3 → GET key → मिला तो return (cache hit: 0 tokens, ~1 ms)
Step 4 → न मिले तो LLM call, फिर SET key value EX 86400 (1 दिन में expire)
Step 5 → Rate limit: INCR "rl:user:minute" ; पहली बार EXPIRE 60 ; count > limit → 429
Step 6 → Token budget: INCRBY "tokens:user:day" used_tokens (atomic, concurrency में सुरक्षित)
Step 7 → Shutdown पर: await client.aclose()
```

---

## 🟡 Real World Example
**Tariff Classification System**: Many importers classify the same products ("cotton t-shirt men"). The service normalises the description (lowercase, trimmed), hashes it, and looks in Redis first. A hit returns the HS code in 2 ms for 0 tokens. It also enforces 30 requests per minute per user and a daily token budget using Redis counters.

**Zomato AI**: Popular queries like "best biryani near me" are cached per city for 10 minutes; session context for the chat assistant is kept in Redis with a TTL.

## 🟡 Real Example Hindi mein
**Tariff System**: कई importers वही products classify करते हैं ("cotton t-shirt men")। Service description normalise (lowercase, trim) करके hash बनाती है और पहले Redis में देखती है। Hit पर HS code 2 ms में, 0 tokens में मिलता है। Redis counters से प्रति user 30 requests/minute और daily token budget भी लागू होता है।

**Zomato AI**: "best biryani near me" जैसी popular queries शहर के हिसाब से 10 मिनट cache होती हैं; chat assistant का session context TTL के साथ Redis में रहता है।

---

## 💻 Code Example — Basic
```python
# Basic Redis cache (pip install redis). Needs Redis running: docker run -p 6379:6379 redis
import asyncio  # run async main
import hashlib  # stable hash for keys

import redis.asyncio as redis  # async redis client


def cache_key(description: str, model: str = "gpt-4o-mini", version: str = "v1") -> str:  # build key
    normalised = " ".join(description.lower().split())  # lowercase + collapse spaces
    digest = hashlib.sha256(f"{model}|{version}|{normalised}".encode()).hexdigest()[:32]  # short stable hash
    return f"tariff:{version}:{digest}"  # namespaced key


async def main() -> None:  # demo
    r = redis.from_url("redis://localhost:6379", decode_responses=True)  # str in, str out
    try:  # ensure close
        key = cache_key("Android  Phone")  # same key as "android phone"
        hit = await r.get(key)  # look up
        if hit:  # cache hit
            print("HIT:", hit)  # no tokens used
        else:  # miss
            answer = "8517.13"  # pretend LLM answer
            await r.set(key, answer, ex=3600)  # store for 1 hour
            print("MISS, stored:", answer)  # first time
        print("ttl:", await r.ttl(key))  # seconds left
    finally:  # cleanup
        await r.aclose()  # close connection pool


if __name__ == "__main__":  # entry
    asyncio.run(main())  # run (requires Redis)
```

## 💻 Code Example — Advanced
```python
# Production: shared client in lifespan, cache dependency, atomic rate limit (INCR+EXPIRE via pipeline),
# token budget, cache stampede lock, graceful degradation if Redis is down. Needs Redis.
import hashlib  # hashing
import json  # serialise
import os  # env
from contextlib import asynccontextmanager  # lifespan
from typing import Annotated, AsyncIterator  # typing

import redis.asyncio as redis  # client
from fastapi import Depends, FastAPI, HTTPException, Request  # FastAPI
from pydantic import BaseModel, Field  # models
from redis.exceptions import RedisError  # base redis error

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")  # config
RATE_LIMIT = 30  # requests per minute per user
DAILY_TOKENS = 200_000  # tokens per user per day


@asynccontextmanager  # lifespan
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # hook
    app.state.redis = redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=0.5)  # fast timeouts
    yield  # run
    await app.state.redis.aclose()  # close


app = FastAPI(lifespan=lifespan)  # app


def get_redis(request: Request) -> redis.Redis:  # dependency
    return request.app.state.redis  # shared client


R = Annotated[redis.Redis, Depends(get_redis)]  # type shortcut


class In(BaseModel):  # body
    description: str = Field(min_length=3, max_length=2000)  # bounded input


async def rate_limit(r: redis.Redis, user: str) -> None:  # fixed-window limiter
    key = f"rl:{user}"  # per-user key
    try:  # redis may fail
        pipe = r.pipeline()  # batch commands in one round trip
        pipe.incr(key)  # count this request
        pipe.expire(key, 60, nx=True)  # set TTL only if none exists (Redis 7+)
        count, _ = await pipe.execute()  # run both
    except RedisError:  # Redis down
        return  # fail open: availability over strictness (choose by policy)
    if count > RATE_LIMIT:  # exceeded
        raise HTTPException(429, "rate limit exceeded", headers={"Retry-After": "60"})  # reject


async def fake_llm(text: str) -> tuple[str, int]:  # stand-in for the real call
    return "8517.13", 650  # answer and tokens used


@app.post("/classify")  # route
async def classify(body: In, r: R, user: str = "anon") -> dict:  # handler
    await rate_limit(r, user)  # 429 before any cost
    norm = " ".join(body.description.lower().split())  # normalise
    key = "tariff:v1:" + hashlib.sha256(norm.encode()).hexdigest()[:32]  # cache key
    try:  # cache read
        cached = await r.get(key)  # lookup
        if cached:  # hit
            return {**json.loads(cached), "cached": True}  # 0 tokens
    except RedisError:  # ignore cache failure
        pass  # continue to LLM
    try:  # budget lookup
        spent = int(await r.get(f"tokens:{user}") or 0)  # tokens used today
    except RedisError:  # Redis down
        spent = 0  # best effort: allow
    if spent >= DAILY_TOKENS:  # budget check
        raise HTTPException(429, "daily token budget exhausted")  # stop spending
    code, tokens = await fake_llm(norm)  # miss: pay for LLM
    result = {"hs_code": code, "tokens": tokens}  # response data
    try:  # write back
        await r.set(key, json.dumps(result), ex=86400)  # cache 1 day
        await r.incrby(f"tokens:{user}", tokens)  # atomic counter
        await r.expire(f"tokens:{user}", 86400)  # reset daily
    except RedisError:  # cache write failed
        pass  # do not fail the request
    return {**result, "cached": False}  # response
```

---

## 🟠 FastAPI Integration
Create one Redis client per process in `lifespan` (it manages a connection pool internally). Use dependencies for the client, and short socket timeouts so a Redis outage does not freeze the API. Decide fail-open (skip cache or limiter) or fail-closed (reject) per feature. FastAPI-specific libraries such as `fastapi-limiter` and `fastapi-cache2` exist, but the manual approach above shows what they do.

```python
# Prevent cache stampede: only one request calls the LLM for a missing key
import asyncio  # sleep
import redis.asyncio as redis  # client


async def get_or_compute(r: redis.Redis, key: str, compute, ttl: int = 3600) -> str:  # helper
    cached = await r.get(key)  # try cache
    if cached:  # hit
        return cached  # done
    got_lock = await r.set(f"lock:{key}", "1", nx=True, ex=30)  # only one winner gets True
    if got_lock:  # we compute
        try:  # protect
            value = await compute()  # call LLM
            await r.set(key, value, ex=ttl)  # fill cache
            return value  # done
        finally:  # always
            await r.delete(f"lock:{key}")  # release lock
    for _ in range(50):  # others wait up to ~5 s
        await asyncio.sleep(0.1)  # poll
        cached = await r.get(key)  # check again
        if cached:  # filled by winner
            return cached  # done
    return await compute()  # give up waiting, compute ourselves
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has LLM caches (`set_llm_cache`) with `RedisCache` and `RedisSemanticCache` (in `langchain-community`/`langchain-redis`) that avoid repeat model calls. LangGraph can store checkpoints in Redis with `langgraph-checkpoint-redis`. Chat history can be kept per session in `RedisChatMessageHistory`.

```python
# LangChain exact-match LLM cache in Redis (pip install langchain-community redis)
from langchain_community.cache import RedisCache  # cache class
from langchain_core.globals import set_llm_cache  # global switch
from langchain_openai import ChatOpenAI  # model
from redis import Redis  # sync client is used by RedisCache

set_llm_cache(RedisCache(redis_=Redis.from_url("redis://localhost:6379"), ttl=3600))  # enable cache for 1 hour

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # temperature 0 = cache works well
# llm.invoke("HS code for a smartphone")  # first call: paid
# llm.invoke("HS code for a smartphone")  # second call: served from Redis, 0 tokens
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Caching without versioning or with weak keys
✅ Correct: include model, prompt version and normalised input; use a TTL.

```python
# Wrong: after you change the prompt, users still get old-style answers forever
r.set(description, answer)
# Right
r.set(f"tariff:{PROMPT_VERSION}:{model}:{sha256(norm)}", answer, ex=86400)
```

❌ Mistake 2: Non-atomic rate limiting (GET then SET)
✅ Correct: `INCR` (atomic), then set expiry.

```python
# Wrong: two concurrent requests both read 29 and both pass
n = int(await r.get(k) or 0)
await r.set(k, n + 1)
# Right
n = await r.incr(k)
if n == 1:
    await r.expire(k, 60)
```

❌ Mistake 3: Caching personal or tenant-specific answers under a shared key (data leak). Include `tenant_id` in the key or skip caching.

---

## 🧠 Tricky Interview Question

**Q**: "You added Redis caching with temperature 0.7 and the cache hit rate is 60 percent, but users complain that answers feel repetitive and sometimes outdated after a prompt change. What did you miss?"

**Answer**: With temperature above 0 an LLM gives varied answers; caching freezes one sample, which is fine for factual classification but not for creative text. Cache only deterministic or factual tasks. The staleness comes from a key that does not include the prompt/model version and a TTL that is too long. Add version fields to the key, use a sensible TTL, invalidate by bumping the version on deploy, and consider semantic caching (embedding similarity) only where slightly different questions should share an answer, with a strict similarity threshold to avoid wrong matches.

---

## ⚫ Interview Questions + Answers

Q1: Why is Redis fast? (Easy)
A1: It keeps data in memory, uses simple data structures, and is mostly single-threaded for commands, avoiding lock overhead. Typical latency is under a millisecond.

Q2: What is a TTL? (Easy)
A2: Time to live: the number of seconds after which a key is deleted automatically (`SET key value EX 3600`). It stops caches growing forever and limits staleness.

Q3: How do you implement per-user rate limiting in Redis? (Medium)
A3: Fixed window: `INCR rl:user:minute` and `EXPIRE 60` on first increment. Sliding window: a sorted set of timestamps (`ZADD`, `ZREMRANGEBYSCORE`, `ZCARD`) in a Lua script for atomicity. Token bucket via a Lua script is smoother. Return 429 with `Retry-After`.

Q4: Exact cache vs semantic cache? (Medium)
A4: Exact cache keys on the hash of the normalised input: fast, safe, but only hits identical queries. Semantic cache embeds the query and looks for a near neighbour above a similarity threshold: higher hit rate but risk of wrong answers (for example "HS code for men's shoes" versus "women's shoes") and extra embedding cost. Use it for FAQs, with careful thresholds and evaluation.

Q5: What happens when Redis goes down and how do you design for it? (Hard)
A5: Decide per feature. Cache: fail open (skip cache, call LLM) but protect the LLM with a local in-process limiter so a cache outage does not cause a cost spike. Rate limiter: fail open for availability, or fail closed for strict budgets. Use short timeouts, a circuit breaker, Redis replication/Sentinel or managed Redis with failover, and alert on hit rate drops. Avoid cache stampede after recovery with locks or request coalescing and jittered TTLs.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Caching repeated LLM or embedding results
- Rate limiting and token budgets
- Short-lived state: sessions, job status, locks

❌ Avoid when:
- You need durable, auditable records (use Postgres)
- Data is large (full documents) and rarely re-read
- The answers are personalised or non-deterministic and caching would hurt quality

---

## 📊 Visual Diagram
```
 request ─► rate_limit (INCR rl:user)──over──► 429
              │ ok
              ▼
        GET tariff:v1:<hash> ──hit──► return (0 tokens, ~1 ms)
              │ miss
              ▼
        budget check (tokens:user)──over──► 429
              │ ok
              ▼
        LLM call (paid) ──► SET key EX 86400 ; INCRBY tokens:user used
              │
              ▼
           response
```

---

## 💰 Cost Impact
Caching is the cheapest optimisation. A cache hit costs about 0 tokens versus roughly 700 for a miss. With 100K daily queries at 700 tokens on gpt-4o-mini ($0.15 per 1M input; output extra), a 40 percent hit rate avoids 28M tokens a day. Token counters in Redis prevent runaway bills from one user or a retry loop. Track hit rate as a metric. Optimise by normalising inputs (case, whitespace), versioned keys, longer TTL for stable facts, and caching only temperature-0 tasks. Redis memory cost is tiny compared with tokens.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Redis | In-memory key-value store | in-memory key-value store |
| TTL | Auto-expiry time of a key | key की expiry अवधि |
| Cache hit/miss | Found / not found in cache | cache में मिला / नहीं मिला |
| INCR | Atomic counter increment | atomic गिनती बढ़ाना |
| Rate limit | Max requests per time window | समय में अधिकतम requests |
| Stampede | Many misses at once | एक साथ कई misses |
| Semantic cache | Cache by meaning similarity | अर्थ की समानता से cache |
| Fail open | Allow when the guard is down | guard बंद हो तो अनुमति |

---

## ⚡ 3-Line Summary
English: Use `redis.asyncio` with a client created in `lifespan` for caching LLM answers, atomic rate limits and token budgets. Version your keys, set TTLs, and decide fail-open or fail-closed. A cache hit costs zero tokens.
Hindi: `lifespan` में बने `redis.asyncio` client से LLM answers cache करो, atomic rate limits और token budgets लगाओ। Keys को version दो, TTL रखो, और fail-open या fail-closed तय करो। Cache hit पर 0 tokens लगते हैं।

---

## ➡️ Next Topic
**016. FastAPI Project Structure for AI** — with routes, models, database and cache in place, we organise everything into a clean, scalable project layout.
