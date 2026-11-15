---

# 340. Redis with FastAPI
# हिंदी में: FastAPI के साथ Redis (Cache, Rate Limit, Counters)

---

## 🔵 Simple Definition (English)
Redis is a very fast in-memory key-value store. With FastAPI you use it for caching expensive results, rate limiting, counters, sessions, leaderboards and as a message broker. In Python you use the `redis` package: `redis.asyncio` for async routes.

## 🔵 सरल परिभाषा (Hindi)
Redis बहुत तेज़ in-memory key-value store है। FastAPI के साथ इसे महंगे results को cache करने, rate limiting, counters, sessions, leaderboards और message broker के लिए उपयोग करते हैं। Python में `redis` package उपयोग होता है: async routes के लिए `redis.asyncio`।

---

## 🔴 Problem it Solves
A database query that takes 80 ms and is asked 1,000 times a second will overload the database. Rate limits kept in a Python variable break the moment you run two uvicorn workers or two servers. Redis gives one shared, microsecond-fast store with automatic expiry (TTL), atomic counters (`INCR`) and data structures (lists, hashes, sorted sets), usable by every worker.

## 🔴 यह क्यों बना? (Hindi)
80 ms लेने वाली database query अगर 1,000 बार प्रति सेकंड पूछी जाए तो database पर भार पड़ेगा। Python variable में रखी rate limits तब टूट जाती हैं जब दो uvicorn workers या दो servers चलें। Redis एक साझा, microsecond-तेज़ store देता है जिसमें अपने आप expiry (TTL), atomic counters (`INCR`) और data structures (lists, hashes, sorted sets) हैं, और हर worker इसे उपयोग कर सकता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Run Redis (docker run -p 6379:6379 redis:7) and pip install redis
Step 2 → Create ONE client/pool at startup: redis.from_url("redis://localhost:6379/0", decode_responses=True)
Step 3 → Cache-aside: on request, GET key
Step 4 → HIT  -> return cached value (no DB call)
Step 5 → MISS -> read DB, SET key value EX=60, return value
Step 6 → Rate limit: INCR key; on first hit EXPIRE key 60; reject if count > limit
Step 7 → Redis deletes expired keys by itself
Step 8 → On shutdown: await client.aclose()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Redis चलाएं (docker run -p 6379:6379 redis:7) और pip install redis
Step 2 → startup पर एक ही client/pool बनाएं: redis.from_url("redis://localhost:6379/0", decode_responses=True)
Step 3 → Cache-aside: request आने पर key को GET करें
Step 4 → HIT  -> cached value लौटाएं (DB call नहीं)
Step 5 → MISS -> DB से पढ़ें, SET key value EX=60, फिर लौटाएं
Step 6 → Rate limit: INCR key; पहली बार EXPIRE key 60; count > limit तो reject
Step 7 → Redis expired keys खुद हटा देता है
Step 8 → Shutdown पर: await client.aclose()
```

---

## 🟡 Real World Example
An e-commerce product page (Flipkart/Meesho style): product details change rarely but are read constantly, so they are cached for 60 seconds. The login API allows 5 attempts per minute per IP using `INCR` + `EXPIRE`. The sales leaderboard uses a sorted set. All uvicorn workers share the same Redis, so limits and caches are consistent.

## 🟡 Real Example Hindi mein
E-commerce product page (Flipkart/Meesho जैसा): product details कम बदलती हैं पर लगातार पढ़ी जाती हैं, इसलिए 60 सेकंड cache होती हैं। Login API `INCR` + `EXPIRE` से प्रति IP प्रति मिनट 5 attempts की अनुमति देती है। Sales leaderboard sorted set से बनता है। सभी uvicorn workers एक ही Redis साझा करते हैं, इसलिए limits और cache सुसंगत रहते हैं।

---

## 💻 Code Example — Basic
```python
# Basic Redis commands (using fakeredis, an in-process fake with the same API; verified)
# For a real server replace FakeRedis(...) with redis.Redis(host="localhost", port=6379, decode_responses=True)
import fakeredis                                          # pip install fakeredis

r = fakeredis.FakeRedis(decode_responses=True)            # decode_responses=True => str instead of bytes
r.set("name", "Asha", ex=30)                              # string value that expires in 30 seconds
print(r.get("name"), r.ttl("name"), r.get("missing"))     # value, seconds left, None for missing key
r.hset("user:1", mapping={"name": "Asha", "plan": "pro"}) # hash = a small dict stored under one key
print(r.hgetall("user:1"))                                # read the whole hash
r.lpush("queue", "a", "b")                                # list: push two items on the left
print(r.rpop("queue"), r.llen("queue"))                   # pop oldest from the right, length left
r.zadd("lb", {"x": 10, "y": 30, "z": 20})                 # sorted set: member -> score
print(r.zrevrange("lb", 0, 1, withscores=True))           # top 2 by score
print(r.incr("hits"), r.incr("hits"))                     # atomic counter 1 then 2
print(r.set("lock", "1", nx=True), r.set("lock", "2", nx=True))   # nx=True: set only if absent (simple lock)

# Output (verified):
# Asha 30 None
# {'name': 'Asha', 'plan': 'pro'}
# a 1
# [('y', 30.0), ('z', 20.0)]
# 1 2
# True None
```

## 💻 Code Example — Advanced
```python
# Production style: lifespan-managed async client, cache-aside, rate limiter (verified with fakeredis)
import asyncio                                            # run the demo
import json                                               # serialize dicts for Redis
from collections.abc import AsyncIterator                 # lifespan type
from contextlib import asynccontextmanager                # lifespan helper
from typing import Annotated, Any                         # typing helpers
import fakeredis                                          # in-process fake; swap for real Redis in prod
from fastapi import Depends, FastAPI, HTTPException, Request   # FastAPI
from httpx import ASGITransport, AsyncClient              # async test client
import redis.asyncio as redis                             # the real async client module (for type hints)


@asynccontextmanager                                      # startup + shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # FastAPI lifespan
    # production: app.state.redis = redis.from_url("redis://localhost:6379/0", decode_responses=True)
    app.state.redis = fakeredis.FakeAsyncRedis(decode_responses=True)   # one shared client (pool inside)
    yield                                                 # app runs
    await app.state.redis.aclose()                        # close connections on shutdown


app: FastAPI = FastAPI(lifespan=lifespan)                 # create app


def get_redis(request: Request) -> redis.Redis:           # dependency returning the shared client
    return request.app.state.redis                        # no new connection per request


R = Annotated[redis.Redis, Depends(get_redis)]            # alias for route signatures
DB_CALLS: dict[str, int] = {"n": 0}                       # counts how often we "hit the database"


async def slow_db_lookup(pid: int) -> dict[str, Any]:     # pretend database query
    DB_CALLS["n"] += 1                                    # count the call
    return {"id": pid, "name": f"Product {pid}"}          # fake row


@app.get("/products/{pid}")                               # cache-aside endpoint
async def product(pid: int, r: R) -> dict[str, Any]:      # async route
    key: str = f"product:{pid}"                           # namespaced key
    if (hit := await r.get(key)) is not None:             # 1) try the cache
        return {**json.loads(hit), "cache": "hit"}        # served from Redis
    data = await slow_db_lookup(pid)                      # 2) miss: ask the database
    await r.set(key, json.dumps(data), ex=60)             # 3) store for 60 s (always set a TTL!)
    return {**data, "cache": "miss"}                      # served from DB


@app.get("/limited")                                      # fixed-window rate limit: 3 per minute
async def limited(request: Request, r: R) -> dict[str, int]:   # async route
    key: str = f"rl:{request.client.host}"                # one counter per client IP
    count: int = await r.incr(key)                        # atomic increment (safe with many workers)
    if count == 1:                                        # first request of this window
        await r.expire(key, 60)                           # window length = 60 seconds
    if count > 3:                                         # over the limit
        raise HTTPException(429, "too many requests")     # Too Many Requests
    return {"count": count}                               # remaining logic ok


async def main() -> None:                                 # demo driver
    async with app.router.lifespan_context(app):          # start lifespan manually
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            print((await c.get("/products/7")).json())    # first call: miss
            print((await c.get("/products/7")).json())    # second call: hit
            print("db calls:", DB_CALLS["n"])              # only 1 database call
            print(await app.state.redis.ttl("product:7")) # TTL just set
            print([(await c.get("/limited")).status_code for _ in range(5)])   # 3 ok then 429s


asyncio.run(main())                                       # run

# Output (verified):
# {'id': 7, 'name': 'Product 7', 'cache': 'miss'}
# {'id': 7, 'name': 'Product 7', 'cache': 'hit'}
# db calls: 1
# 60
# [200, 200, 200, 429, 429]
```
Not run against a real Redis server (none installed here); `fakeredis` implements the same commands. Test against real Redis before production.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (`redis-py`) | JavaScript (`ioredis` / `node-redis`) |
|---------|---------------------|----------------------------------------|
| Connect | `redis.from_url(url)` | `new Redis(url)` |
| Set with TTL | `await r.set(k, v, ex=60)` | `await r.set(k, v, "EX", 60)` |
| Get | `await r.get(k)` | `await r.get(k)` |
| Strings vs bytes | `decode_responses=True` for str | strings by default |
| Async | `redis.asyncio` | always promises |

```python
# Python way
await r.set("k", "v", ex=60)          # value expires in 60 s
value = await r.get("k")              # "v" or None
```
```javascript
// JavaScript way (ioredis)
await redis.set("k", "v", "EX", 60);  // value expires in 60 s
const value = await redis.get("k");   // "v" or null
```

Key difference: Python's client returns `bytes` unless `decode_responses=True`. In Node you get strings by default, so Python beginners often see `b'value'` and get confused.

---

## 🟠 FastAPI Connection
Create one `redis.asyncio` client in `lifespan`, put it in `app.state`, and expose it through a `Depends(get_redis)` function (as above). Use it for response caching, rate limiting (or the `fastapi-limiter` package), sessions/JWT blacklists, and as the broker/backend for Celery (topic 341) and ARQ. FastAPI's `BackgroundTasks` can refresh the cache after responding.

```python
# FastAPI example — cache invalidation on update
@app.put("/products/{pid}")                               # update a product
async def update_product(pid: int, r: R) -> dict[str, str]:
    # ... update the database here ...
    await r.delete(f"product:{pid}")                      # remove stale cache; next GET refills it
    return {"status": "updated"}                          # done
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Caching without a TTL
✅ Correct: always set `ex=` (or `px=`) so stale and unbounded data cannot pile up

```python
# Wrong — lives forever, memory grows, data goes stale
await r.set("product:7", payload)
# Right
await r.set("product:7", payload, ex=60)
```

❌ Mistake 2: Using the sync `redis` client inside `async def`
✅ Correct: `import redis.asyncio as redis` and `await` every call

```python
# Wrong — blocks the event loop on each Redis call
import redis
r = redis.Redis()
async def f():
    return r.get("k")
# Right
import redis.asyncio as redis
r = redis.Redis()
async def g():
    return await r.get("k")
```

❌ Mistake 3: Non-atomic "read then write" counters
✅ Correct: use atomic commands (`INCR`, `SET NX`, Lua scripts)

```python
# Wrong — two workers read 5 and both write 6 (lost update)
n = int(await r.get("hits") or 0)
await r.set("hits", n + 1)
# Right
await r.incr("hits")
```

---

## 🧠 Tricky Interview Question

```python
# Rate limiter: INCR then EXPIRE in two calls. What can go wrong?
count = await r.incr(key)
if count == 1:
    await r.expire(key, 60)
```
Answer: If the process crashes (or the connection drops) between `INCR` and `EXPIRE`, the key is created without a TTL and the counter never resets, so that client is blocked forever. Fix: do both atomically with a pipeline/transaction (`async with r.pipeline(transaction=True) as p: p.incr(key); p.expire(key, 60, nx=True); await p.execute()`) or a small Lua script. Another gotcha: with a fixed window, a user can send 3 requests at 0:59 and 3 more at 1:01, which is 6 in two seconds; use a sliding window (sorted set) if that matters.

---

## ⚫ Interview Questions + Answers

Q1: What is cache-aside?
A1: The app checks the cache first; on a miss it loads from the database and stores the result in the cache with a TTL. Writes update the database and delete (or update) the cache key.

Q2: Why is Redis fast?
A2: Data lives in RAM, it uses efficient data structures, and its command execution is single-threaded (no locks), plus pipelining reduces round trips. Typical latency is well under a millisecond.

Q3: What is a cache stampede and how do you avoid it?
A3: When a hot key expires, many requests miss at once and hammer the database. Mitigate with locking (`SET NX`) so one request rebuilds, jittered/randomized TTLs, or serving stale data while refreshing in the background.

Q4: What are persistence options in Redis?
A4: RDB snapshots and AOF (append-only file); both can be combined. For a pure cache you may disable persistence. Redis is not a replacement for your primary database.

Q5: How do you handle Redis being down?
A5: Treat the cache as optional: catch `redis.exceptions.ConnectionError`, fall back to the database, and log a warning. Rate limiters decide between fail-open (allow) and fail-closed (reject).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Caching hot, read-heavy data
- Rate limiting, counters, short-lived sessions, locks
- Leaderboards (sorted sets), queues/broker, pub/sub

❌ Avoid when:
- It is the only copy of important data (without persistence/replication planned)
- Data is larger than RAM budget
- You need complex queries and joins: use a real database

---

## 📊 Visual Diagram
```
 Client ─► FastAPI ─► GET product:7 ─► Redis
                          │               │
                    HIT ◄─┴── value       │ MISS
                                          ▼
                    DB query ─► SET product:7 EX=60 ─► Redis
                          │
                    response (cache: hit / miss)

 Rate limit:  INCR rl:ip  ─► count 1,2,3 ok ─► 4 => 429   (key expires after 60 s)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TTL | Time before key auto-deletes | Key अपने आप हटने का समय |
| Cache-aside | Check cache, else DB then fill cache | पहले cache, नहीं तो DB और फिर cache भरें |
| `INCR` | Atomic increment | Atomic बढ़ोतरी |
| Sorted set | Members with scores, ordered | Score के साथ क्रमबद्ध members |
| Pipeline | Send many commands in one trip | कई commands एक बार में |
| Cache stampede | Many misses at once | एक साथ कई cache misses |

---

## ⚡ 3-Line Summary
English: Redis is a shared in-memory store for caching, rate limits, counters and sessions. Use `redis.asyncio` with one client created in `lifespan`, always set a TTL, and use atomic commands like `INCR`. Treat the cache as optional and invalidate it when data changes.
Hindi: Redis caching, rate limits, counters और sessions के लिए साझा in-memory store है। `lifespan` में बनाए एक client के साथ `redis.asyncio` उपयोग करें, हमेशा TTL सेट करें, और `INCR` जैसे atomic commands उपयोग करें। Cache को वैकल्पिक मानें और data बदलने पर उसे invalidate करें।

---

## ➡️ Next Topic
**341. Celery with FastAPI** — move slow work (emails, invoices, reports) out of the request into background workers, with Redis as the broker.
