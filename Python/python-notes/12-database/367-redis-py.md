---

# 367. Redis-py
# हिंदी में: Redis-py (Redis का Python client)

---

## 🔵 Simple Definition (English)
Redis is a very fast in-memory data store, and redis-py is its official Python client. It stores strings, hashes, lists, sets and sorted sets by key, with optional expiry. Typical uses are caching, counters, rate limiting, sessions and queues.

## 🔵 सरल परिभाषा (Hindi)
Redis बहुत तेज़ in-memory data store है, और redis-py उसका official Python client है। यह strings, hashes, lists, sets और sorted sets को key से रखता है, optional expiry के साथ। आम उपयोग हैं caching, counters, rate limiting, sessions और queues।

---

## 🔴 Problem it Solves
A database query takes milliseconds and every user request repeating the same query overloads it. Python process memory is lost on restart and is not shared between workers. Redis keeps hot data in RAM (microsecond reads), shared by all workers, with expiry (TTL) and atomic operations like `INCR`. redis-py gives a simple Python API to it.

## 🔴 यह क्यों बना? (Hindi)
Database query में milliseconds लगते हैं और हर user request वही query दोहराए तो database पर बोझ बढ़ता है। Python process की memory restart पर खो जाती है और workers के बीच share नहीं होती। Redis hot data को RAM में रखता है (microsecond reads), सभी workers share करते हैं, expiry (TTL) के साथ और `INCR` जैसे atomic operations के साथ। redis-py उसका सरल Python API देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → r = redis.Redis(host, port, decode_responses=True)      pool of connections inside
Step 2 → Strings:   r.set(k, v, ex=60) / r.get(k) / r.incr(k)          (TTL = time to live)
Step 3 → Hashes:    r.hset(k, mapping={...}) / r.hgetall(k)           small objects
Step 4 → Lists:     r.rpush(k, x) / r.lpop(k)                          queues
Step 5 → Sets / Sorted sets:  sadd, smembers / zadd, zrevrange         tags, leaderboards
Step 6 → pipeline(): batch many commands in one network round trip
Step 7 → Cache-aside: read Redis -> on miss read DB -> write Redis with TTL
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → r = redis.Redis(host, port, decode_responses=True)      अंदर connections का pool
Step 2 → Strings:   r.set(k, v, ex=60) / r.get(k) / r.incr(k)          (TTL = जीवन अवधि)
Step 3 → Hashes:    r.hset(k, mapping={...}) / r.hgetall(k)           छोटे objects
Step 4 → Lists:     r.rpush(k, x) / r.lpop(k)                          queues
Step 5 → Sets / Sorted sets:  sadd, smembers / zadd, zrevrange         tags, leaderboards
Step 6 → pipeline(): बहुत सारे commands एक ही network round trip में
Step 7 → Cache-aside: पहले Redis -> miss पर DB -> TTL के साथ Redis में लिखो
```

---

## 🟡 Real World Example
An e-commerce site caches product pages for 30 seconds so the database sees one query instead of 10,000. A login system stores OTPs with a 60-second TTL (`SET otp:99 4821 EX 60`). An API gateway limits each user to 100 requests per minute with `INCR` + `EXPIRE`. A game shows a live leaderboard from a sorted set (`ZADD`, `ZREVRANGE`).

## 🟡 Real Example Hindi mein
E-commerce site product pages को 30 सेकंड cache करती है ताकि database को 10,000 की जगह एक query मिले। Login system OTP को 60 सेकंड के TTL से रखता है (`SET otp:99 4821 EX 60`)। API gateway हर user को `INCR` + `EXPIRE` से 100 requests प्रति मिनट तक सीमित करता है। Game sorted set से live leaderboard दिखाता है (`ZADD`, `ZREVRANGE`)।

---

## 💻 Code Example — Basic
```python
# Basic redis-py usage (swap FakeRedis for redis.Redis(host="localhost") with a real server)
import fakeredis                                  # in-memory Redis stand-in used for this demo

r = fakeredis.FakeRedis(decode_responses=True)    # decode_responses -> str instead of bytes
r.set("greeting", "hello")                        # string SET
print(r.get("greeting"))                          # hello
r.set("otp:99", "4821", ex=60)                    # expire in 60 seconds
print(r.ttl("otp:99") <= 60)                      # TTL counts down
print(r.get("missing"))                           # None for a missing key
r.incr("visits"); r.incr("visits", 4)             # atomic counter
print(r.get("visits"))                            # '5' (Redis stores strings)
r.hset("user:1", mapping={"name": "Asha", "city": "Delhi"})   # hash = small object
print(r.hgetall("user:1"))                        # dict of strings
r.rpush("queue", "job1", "job2")                  # list as a queue
print(r.lpop("queue"), r.llen("queue"))           # job1 1
r.sadd("tags", "a", "b", "a")                     # set ignores duplicates
print(sorted(r.smembers("tags")))                 # ['a', 'b']
r.zadd("board", {"asha": 50, "ravi": 80})         # sorted set leaderboard
print(r.zrevrange("board", 0, 0, withscores=True))   # top player
print(r.delete("greeting"), r.exists("greeting")) # 1 0

# Output (run with fakeredis, an in-memory Redis stand-in):
# hello
# True
# None
# 5
# {'name': 'Asha', 'city': 'Delhi'}
# job1 1
# ['a', 'b']
# [('ravi', 80.0)]
# 1 0
```

## 💻 Code Example — Advanced
```python
# Production style: cache-aside decorator, rate limiter, distributed lock, pipeline, error handling
import json                                       # serialise values
import time                                       # sleep in demo
import uuid                                       # unique lock token
from typing import Any, Callable                  # type hints
import fakeredis                                  # demo backend; in prod: redis.Redis.from_url(...)
import redis                                      # real exception classes

r = fakeredis.FakeRedis(decode_responses=True)    # client (one shared instance)
calls: dict[str, int] = {"db": 0}                 # counts slow DB hits


def cached(ttl: int) -> Callable:
    """Cache-aside decorator: Redis first, function on miss."""
    def deco(fn: Callable[[int], dict[str, Any]]) -> Callable[[int], dict[str, Any]]:
        def wrapper(key: int) -> dict[str, Any]:
            k: str = f"{fn.__name__}:{key}"       # namespaced key
            try:                                  # Redis down must not kill the app
                hit = r.get(k)                    # try cache
                if hit is not None:               # cache hit
                    return json.loads(hit)        # decode JSON
            except redis.RedisError:              # connection trouble
                pass                              # fall through to the database
            value = fn(key)                       # real work
            try:
                r.set(k, json.dumps(value), ex=ttl)   # store with expiry
            except redis.RedisError:
                pass                              # caching is best effort
            return value
        return wrapper
    return deco


@cached(ttl=30)
def get_user(user_id: int) -> dict[str, Any]:
    calls["db"] += 1                              # pretend this is a slow SQL query
    return {"id": user_id, "name": "Asha"}


get_user(1); get_user(1); get_user(1)             # 1 miss, 2 hits
print(calls["db"])                                # 1


def allow(user: str, limit: int = 3, window: int = 60) -> bool:
    """Fixed-window rate limiter using INCR + EXPIRE."""
    k: str = f"rl:{user}"                         # per-user key
    pipe = r.pipeline()                           # send both commands together
    pipe.incr(k)                                  # count this request
    pipe.expire(k, window, nx=True)               # set TTL only on first hit (Redis 7+)
    count, _ = pipe.execute()                     # run
    return int(count) <= limit                    # under the limit?


print([allow("asha") for _ in range(5)])          # [True, True, True, False, False]


def with_lock(name: str, ttl: int = 5) -> str | None:
    """Acquire a lock with SET NX EX; returns the token or None."""
    token: str = uuid.uuid4().hex                 # owner id
    return token if r.set(f"lock:{name}", token, nx=True, ex=ttl) else None


def release(name: str, token: str) -> bool:
    """Release only if we still own the lock (compare-and-delete in Lua)."""
    script: str = "if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end"
    return bool(r.eval(script, 1, f"lock:{name}", token))   # atomic check+delete


t1 = with_lock("report")                          # first caller gets it
print(t1 is not None, with_lock("report"))        # second caller gets None
print(release("report", "wrong-token"), release("report", t1))   # False True

# Output (run with fakeredis + lupa for the Lua script):
# 1
# [True, True, True, False, False]
# True None
# False True
```

Verification note: no Redis server was available, so these examples ran against `fakeredis` (an in-memory re-implementation with the same API). Behaviour of the real server matches for these commands, but timings and network errors differ. Replace `fakeredis.FakeRedis(...)` with `redis.Redis(host="localhost", decode_responses=True)` for a real server.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (redis-py) | JavaScript (node-redis / ioredis) |
|---------|-------------------|----------------------------------|
| Connect | `redis.Redis(host=...)` | `createClient({ url }); await client.connect()` |
| Set with expiry | `r.set(k, v, ex=60)` | `client.set(k, v, { EX: 60 })` |
| Get | `r.get(k)` | `await client.get(k)` |
| Pipeline | `r.pipeline()` | `client.multi()` / `pipeline()` |
| Return type | bytes unless `decode_responses=True` | string / Buffer |

```python
# Python way — sync calls (fakeredis for the demo)
import fakeredis                                   # use redis.Redis(...) with a real server
r = fakeredis.FakeRedis(decode_responses=True)     # strings, not bytes
r.set("name", "Asha", ex=30)                       # expires in 30 seconds
print(r.get("name"))                               # Asha
```
```javascript
// JavaScript way — node-redis (always async)
const client = createClient(); await client.connect();
await client.set("name", "Asha", { EX: 30 });
console.log(await client.get("name"));             // Asha
```

Key difference: node-redis is promise-based; redis-py is synchronous (use `redis.asyncio` for async). redis-py returns `bytes` by default, so set `decode_responses=True` or you get `b'hello'` instead of `'hello'`.

---

## 🟠 FastAPI Connection
In FastAPI, redis-py (sync) fits plain `def` endpoints and dependencies; for `async def` endpoints use `redis.asyncio` (next topic) so Redis calls do not block the loop. Typical uses: a cache-aside layer for expensive queries, a rate-limit dependency (429 responses), session/OTP storage, and a lock around cron-like jobs. Build one client at startup (it pools connections) and read the URL from env vars.

```python
# FastAPI + redis-py (sync): cache dependency + rate limit (fakeredis for the demo)
import json                                       # serialise
import fakeredis                                  # prod: redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
from fastapi import Depends, FastAPI, HTTPException   # web
from fastapi.testclient import TestClient         # demo client

r = fakeredis.FakeRedis(decode_responses=True)    # one client (it has a connection pool inside)
app = FastAPI()
hits = {"db": 0}


def rate_limit(user: str = "anon") -> None:
    k = f"rl:{user}"
    n = r.incr(k)                                 # atomic
    if n == 1:
        r.expire(k, 60)                           # window starts on first request
    if n > 3:
        raise HTTPException(429, "too many requests")


@app.get("/product/{pid}", dependencies=[Depends(rate_limit)])
def product(pid: int) -> dict[str, object]:
    key = f"product:{pid}"
    cached = r.get(key)
    if cached:
        return {**json.loads(cached), "source": "cache"}
    hits["db"] += 1                               # pretend DB query
    data = {"id": pid, "price": 499}
    r.set(key, json.dumps(data), ex=30)
    return {**data, "source": "db"}


c = TestClient(app)
print([c.get("/product/1").json()["source"] for _ in range(3)])
print(c.get("/product/1").status_code, hits)

# Output:
# ['db', 'cache', 'cache']
# 429 {'db': 1}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `decode_responses=True` and comparing bytes with str
✅ Correct: set it once on the client

```python
import fakeredis
r = fakeredis.FakeRedis()                 # no decoding
r.set("k", "hello"); r.incr("n")
# Wrong — values come back as bytes
print(r.get("k"), r.get("n"))             # b'hello' b'1'
print(r.get("k") == "hello")              # False
# Right
r = fakeredis.FakeRedis(decode_responses=True)
r.set("k", "hello")
print(r.get("k") == "hello")              # True
```

❌ Mistake 2: Overwriting a key with `SET` and silently losing its TTL
✅ Correct: pass `ex=` again (or `keepttl=True`)

```python
import fakeredis
r = fakeredis.FakeRedis(decode_responses=True)
r.set("e", "x", ex=100)
print(r.ttl("e"))                         # 100
# Wrong — plain SET removes the expiry; key now lives forever
r.set("e", "y")
print(r.ttl("e"))                         # -1  (no expiry)
# Right
r.set("e", "z", ex=100)                   # or r.set("e", "z", keepttl=True)
```

❌ Mistake 3: `GET` then `SET` for counters/locks (race condition) and `KEYS *` in production
✅ Correct: atomic commands (`INCR`, `SET NX EX`) and `SCAN`

```python
# Wrong — two workers read 5 and both write 6
n = int(r.get("visits") or 0); r.set("visits", n + 1)
# Right — atomic on the server
r.incr("visits")
# Wrong in production: r.keys("*") blocks Redis while it scans every key
# Right: iterate in small batches
for key in r.scan_iter(match="otp:*", count=100):
    pass
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import fakeredis
r = fakeredis.FakeRedis()
r.set("k", "hello")
r.incr("n")
print(r.get("k"))
print(r.get("n"))
r.set("e", "x", ex=100)
r.set("e", "y")
print(r.ttl("e"))
```
Answer: `b'hello'`, `b'1'`, `-1`. Without `decode_responses=True` redis-py returns bytes. `INCR` creates the key if missing and stores the number as a string. A plain `SET` on an existing key clears its TTL, so `ttl` returns `-1` (no expiry; `-2` would mean the key does not exist). Verified with redis-py 8.1 and fakeredis 2.40.

---

## ⚫ Interview Questions + Answers

Q1: Why is Redis fast?
A1: Data lives in RAM, it uses simple data structures, and commands run in a single thread (no locking), with an efficient network loop. Typical latency is well under a millisecond.

Q2: What is cache-aside and what is a cache stampede?
A2: Cache-aside: app checks Redis, on miss loads from DB and stores in Redis with a TTL. A stampede happens when a hot key expires and thousands of requests hit the DB at once. Fix with a lock per key, jittered TTLs, or refresh-ahead.

Q3: How do you build a safe distributed lock?
A3: `SET lock:name token NX EX 5` to acquire. Release with a Lua script that deletes only if the stored token still equals yours (compare-and-delete). For serious cases use Redlock or avoid locks with idempotent design.

Q4: Pipeline vs transaction (`MULTI`/`EXEC`)?
A4: A pipeline just batches commands to save network round trips. With `transaction=True` (the default for `r.pipeline()`) redis-py wraps them in MULTI/EXEC so they run together without interleaving. Neither rolls back on a command error.

Q5: Is Redis a database? Will data survive restart?
A5: It can be, with persistence: RDB snapshots and/or AOF log. But it is mainly a cache/broker, memory is limited, and by default you should treat data as recoverable from a source of truth.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Caching expensive reads, sessions, OTPs, tokens
- Counters, rate limiters, leaderboards, deduplication
- Queues, pub/sub, locks, Celery broker

❌ Avoid when:
- Data must be the only copy and must never be lost
- Data is larger than RAM or needs complex queries and joins
- You are inside `async def` endpoints with sync redis-py - use `redis.asyncio`

---

## 📊 Visual Diagram
```
            +-------------+  hit    +-------+
 request -> | FastAPI app | ------> | Redis |  (RAM, ~0.2 ms)
            +-------------+ <------ +-------+
                   | miss
                   v
              +----------+  rows   fill Redis with TTL
              | Postgres | ---------------------------->
              +----------+

keys:  "product:1" -> JSON string (EX 30)     "rl:asha" -> counter (EX 60)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| TTL | Time before a key expires | Key के expire होने का समय |
| Cache-aside | App fills cache on miss | Miss पर app खुद cache भरती है |
| Pipeline | Batch commands in one trip | कई commands एक trip में |
| Atomic | Runs as one indivisible step | अविभाज्य एक step |
| Sorted set | Set with scores | Scores वाला set |
| Pub/Sub | Broadcast messages | Messages का प्रसारण |

---

## ⚡ 3-Line Summary
English: redis-py is the Python client for Redis: fast key-value storage in RAM with TTL, atomic counters, hashes, lists, sets and sorted sets. Use it for caching, rate limiting and locks, set `decode_responses=True`, use atomic commands instead of read-modify-write, and use `redis.asyncio` in async code.
Hindi: redis-py, Redis का Python client है: RAM में तेज़ key-value storage, TTL, atomic counters, hashes, lists, sets और sorted sets के साथ। इसे caching, rate limiting और locks के लिए इस्तेमाल करें, `decode_responses=True` रखें, read-modify-write की जगह atomic commands लगाएं, और async code में `redis.asyncio` इस्तेमाल करें।

---

## ➡️ Next Topic
**368. aioredis** — async Redis with asyncio (now part of redis-py as `redis.asyncio`).
