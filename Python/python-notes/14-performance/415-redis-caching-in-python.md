---

# 415. Redis Caching in Python
# हिंदी में: Python में Redis Caching

---

## 🔵 Simple Definition (English)
Redis is an in-memory key-value store. As a cache, you save the result of slow work (a database query, an API call) under a key with an expiry time (TTL). The next request reads it from Redis in under a millisecond instead of repeating the slow work.

## 🔵 सरल परिभाषा (Hindi)
Redis एक in-memory key-value store है। Cache के रूप में आप धीमे काम का नतीजा (database query, API call) एक key के नीचे expiry time (TTL) के साथ रखते हैं। अगली request वही काम दोहराने की बजाय Redis से एक millisecond से भी कम में पढ़ लेती है।

---

## 🔴 Problem it Solves
The same expensive query runs thousands of times (home page, product details, leaderboards). It loads the database and makes users wait. A per-process dictionary cache is lost on restart and not shared between workers. Redis is a shared, fast, network-accessible cache that all your app instances use.

## 🔴 यह क्यों बना? (Hindi)
वही महँगी query हज़ारों बार चलती है (home page, product details, leaderboards)। इससे database पर बोझ पड़ता है और users को इंतज़ार करना पड़ता है। Process के अंदर का dict cache restart पर मिट जाता है और workers के बीच साझा नहीं होता। Redis साझा, तेज़, network से मिलने वाला cache है जिसे आपके सभी app instances इस्तेमाल करते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives; build a cache key (e.g. "product:42")
Step 2 → GET the key from Redis
Step 3 → HIT: found -> deserialize and return (about 1 ms or less)
Step 4 → MISS: run the slow query / API call
Step 5 → SET key value EX ttl (store with an expiry)
Step 6 → On data change: DELETE the key (invalidate) so users do not see stale data
This is the "cache-aside" pattern. Redis removes expired keys by itself.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request आती है; cache key बनाएँ (जैसे "product:42")
Step 2 → Redis से key GET करें
Step 3 → HIT: मिल गई -> deserialize करके लौटाएँ (लगभग 1 ms या कम)
Step 4 → MISS: धीमी query / API call चलाएँ
Step 5 → SET key value EX ttl (expiry के साथ रखें)
Step 6 → Data बदले तो key DELETE करें (invalidate) ताकि पुराना data न दिखे
इसे "cache-aside" pattern कहते हैं। Expired keys Redis खुद हटा देता है।
```

---

## 🟡 Real World Example
A Flipkart-style product page: product details are cached for 5 minutes, the "trending" list for 30 seconds. Login OTPs are stored with a 5-minute TTL. An AI app caches LLM answers for repeated prompts (saving money), and a rate limiter uses `INCR` with expiry to count requests per user per minute.

## 🟡 Real Example Hindi mein
Flipkart जैसे product page में product details 5 मिनट और "trending" list 30 सेकंड cache होती है। Login OTP 5 मिनट के TTL के साथ रखे जाते हैं। AI app बार-बार आने वाले prompts के LLM जवाब cache करता है (पैसे बचते हैं), और rate limiter `INCR` और expiry से हर user की प्रति मिनट requests गिनता है।

---

## 💻 Code Example — Basic
```python
# Basic Redis caching (pip install redis fakeredis)
# fakeredis behaves like Redis in-process, so this runs without a server.
# In production use:  r = redis.Redis(host="localhost", port=6379, decode_responses=True)
import time  # sleep / timing
from typing import Optional  # type hints

import fakeredis  # in-memory Redis stand-in

r: fakeredis.FakeRedis = fakeredis.FakeRedis(decode_responses=True)  # str in, str out

r.set("greeting", "hello")  # store a string
print(r.get("greeting"))  # read it back
# Output: hello
print(r.get("missing"))  # absent key returns None
# Output: None

r.set("otp:9876543210", "123456", ex=300)  # ex = expire after 300 seconds
print(0 < r.ttl("otp:9876543210") <= 300)  # remaining life in seconds
# Output: True

r.set("short", "x", px=100)  # px = expire after 100 milliseconds
time.sleep(0.2)  # wait longer than the TTL
print(r.get("short"))  # already gone
# Output: None

print(r.incr("page:views"), r.incr("page:views"))  # atomic counter (safe across processes)
# Output: 1 2

# Cache-aside pattern: look in the cache first, else compute and store
CALLS: dict[str, int] = {"db": 0}  # count slow calls


def slow_db_lookup(user_id: int) -> str:
    CALLS["db"] += 1  # record that we hit the database
    time.sleep(0.05)  # pretend the query is slow
    return f"user-{user_id}"  # value from the "database"


def get_user(user_id: int) -> str:
    key: str = f"user:{user_id}"  # namespaced key
    cached: Optional[str] = r.get(key)  # 1) try the cache
    if cached is not None:  # cache hit
        return cached  # fast path
    value: str = slow_db_lookup(user_id)  # 2) miss: do the slow work
    r.set(key, value, ex=60)  # 3) store for a minute
    return value  # return fresh value


print(get_user(7), get_user(7), get_user(7))  # same user three times
# Output: user-7 user-7 user-7
print("database calls:", CALLS["db"])  # only the first call hit the DB
# Output: database calls: 1
```

## 💻 Code Example — Advanced
```python
# Advanced: JSON cache decorator, invalidation, stampede lock, hashes, pipeline
import functools  # wraps
import json  # serialize values
import time  # timing
from typing import Any, Callable, Dict, Optional, TypeVar

import fakeredis  # in-memory Redis stand-in (use redis.Redis in production)

r: fakeredis.FakeRedis = fakeredis.FakeRedis(decode_responses=True)  # client
T = TypeVar("T")  # generic return type
STATS: Dict[str, int] = {"computed": 0}  # how often real work ran


def cached(prefix: str, ttl: int = 60) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Cache a function's JSON-serializable result in Redis."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)  # keep name/docstring
        def wrapper(*args: Any) -> T:
            key: str = f"{prefix}:{':'.join(map(str, args))}"  # e.g. product:42
            hit: Optional[str] = r.get(key)  # try cache
            if hit is not None:  # found
                return json.loads(hit)  # deserialize
            result: T = func(*args)  # compute
            r.set(key, json.dumps(result), ex=ttl)  # store with a TTL (never cache forever)
            return result  # return
        return wrapper
    return decorator


@cached("product", ttl=30)  # cache for 30 seconds
def get_product(pid: int) -> Dict[str, Any]:
    STATS["computed"] += 1  # count real work
    return {"id": pid, "name": f"Item {pid}", "price": pid * 100}  # "database" row


print(get_product(1) == get_product(1))  # second call comes from Redis
# Output: True
print("computed:", STATS["computed"])  # only once
# Output: computed: 1

# Invalidate on write: delete the key when the source data changes
r.delete("product:1")  # remove stale entry
get_product(1)  # recomputed
print("computed after invalidate:", STATS["computed"])  # now 2
# Output: computed after invalidate: 2

# Stampede protection: only ONE caller rebuilds an expired hot key
def rebuild_with_lock(key: str) -> str:
    got_lock: Optional[bool] = r.set(f"lock:{key}", "1", nx=True, ex=10)  # NX = only if absent
    if got_lock:  # we won the lock
        value: str = "fresh-value"  # expensive rebuild happens here
        r.set(key, value, ex=60)  # store
        r.delete(f"lock:{key}")  # release lock
        return value  # return
    time.sleep(0.05)  # others wait briefly...
    return r.get(key) or "stale-fallback"  # ...then read, or serve a fallback


print(rebuild_with_lock("hot:home"), "|", r.get("hot:home"))  # first caller rebuilds
# Output: fresh-value | fresh-value

# Hash for structured data, pipeline to send many commands in one round trip
r.hset("session:abc", mapping={"user": "42", "role": "admin"})  # store fields
pipe = r.pipeline()  # buffer commands
pipe.hget("session:abc", "user")  # queued
pipe.hget("session:abc", "role")  # queued
pipe.ttl("session:abc")  # queued (-1 means no expiry set)
print(pipe.execute())  # one network round trip
# Output: ['42', 'admin', -1]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (redis-py)
import redis
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
r.set("k", "v", ex=60)
print(r.get("k"))
```
```javascript
// JavaScript (node-redis v4+)
import { createClient } from 'redis';
const r = createClient({ url: 'redis://localhost:6379' });
await r.connect();
await r.set('k', 'v', { EX: 60 });
console.log(await r.get('k'));
```

Key differences: the Redis commands are the same; only the client API differs. node-redis is promise-based and needs `connect()`. redis-py is synchronous by default and has `redis.asyncio` for async code. Remember `decode_responses=True` in Python, otherwise you get `bytes`.

---

## 🟠 FastAPI Connection
Inject the Redis client with `Depends` so tests can override it. In `async def` endpoints use `redis.asyncio.Redis` (a sync client would block the event loop). Add a TTL to everything you cache, namespace keys (`product:42`), and delete keys when data changes. The `fastapi-cache2` library offers a ready-made decorator on top of this.

```python
# FastAPI + Redis cache dependency (pip install fastapi redis fakeredis httpx)
import json  # serialize
from typing import Any, Optional  # type hints

import fakeredis  # in-memory stand-in; production: redis.asyncio.Redis(...)
from fastapi import Depends, FastAPI  # app + DI
from fastapi.testclient import TestClient  # test client

app: FastAPI = FastAPI()  # create app
_redis: fakeredis.FakeRedis = fakeredis.FakeRedis(decode_responses=True)  # one shared client
CALLS: dict[str, int] = {"db": 0}  # count DB hits


def get_redis() -> fakeredis.FakeRedis:  # dependency: easy to override in tests
    return _redis  # shared client


@app.get("/products/{pid}")  # GET /products/5
def product(pid: int, cache: fakeredis.FakeRedis = Depends(get_redis)) -> dict[str, Any]:
    key: str = f"product:{pid}"  # cache key
    hit: Optional[str] = cache.get(key)  # try the cache
    if hit is not None:  # hit
        return {**json.loads(hit), "cached": True}  # fast path
    CALLS["db"] += 1  # miss: pretend DB query
    data: dict[str, Any] = {"id": pid, "price": pid * 10}  # row
    cache.set(key, json.dumps(data), ex=30)  # fill cache with TTL
    return {**data, "cached": False}  # fresh response


client: TestClient = TestClient(app)  # test client
print(client.get("/products/5").json())  # first call: miss
# Output: {'id': 5, 'price': 50, 'cached': False}
print(client.get("/products/5").json())  # second call: hit
# Output: {'id': 5, 'price': 50, 'cached': True}
print("db calls:", CALLS["db"])  # DB touched once
# Output: db calls: 1
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Caching without a TTL
```python
# Wrong - the key lives forever, memory grows and data goes stale:
r.set("product:1", data)

# Correct:
r.set("product:1", data, ex=300)
```

❌ Mistake 2: Forgetting Redis stores strings/bytes only
```python
# Wrong - storing a dict raises an error; numbers come back as str:
r.set("user", {"id": 1})          # DataError

# Correct - serialize to JSON and parse after reading:
r.set("user", json.dumps({"id": 1}), ex=60)
user = json.loads(r.get("user"))
```

❌ Mistake 3: Cache stampede and stale data
```python
# Wrong - when a hot key expires, 1,000 requests all hit the database at once;
# and updating the DB without clearing the cache shows old data.

# Correct - use a lock (SET NX), add random jitter to TTLs, and DELETE the key on every write.
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print (with `decode_responses=True`)?

```python
import fakeredis, json
r = fakeredis.FakeRedis(decode_responses=True)
r.set("n", 1)
print(repr(r.get("n")))
r.set("t", "x", ex=100)
r.set("t", "y")
print(r.ttl("t"))
print(json.loads(json.dumps({1: "a"})))
print(r.ttl("nokey"))
```

**Answer**:
```
'1'
-1
{'1': 'a'}
-2
```
Redis stores everything as strings, so `1` comes back as `'1'`. A plain `SET` on an existing key removes its TTL (`-1` means "no expiry"), so re-setting a value without `ex=` makes it permanent. JSON turns integer dict keys into strings. `TTL` of a missing key is `-2`.

---

## ⚫ Interview Questions + Answers

Q1: What is the cache-aside pattern?
A1: The application checks the cache first; on a miss it loads from the database and writes the value to the cache. Writes go to the database and invalidate (delete) the cache key. It is the most common caching pattern.

Q2: How do you prevent a cache stampede?
A2: Lock the rebuild with `SET key NX EX` so only one request recomputes, serve slightly stale data meanwhile, add random jitter to TTLs, or refresh hot keys before they expire.

Q3: How do you choose a TTL?
A3: Based on how stale the data may be: seconds for trending lists, minutes for product pages, hours for static config. Also set `maxmemory` and an eviction policy (like `allkeys-lru`) so Redis never runs out of memory.

Q4: Is Redis single-threaded and is `INCR` safe?
A4: Commands run one at a time on the main thread, so each command is atomic. `INCR` is therefore safe for counters even with many clients. A sequence of commands is atomic only inside a transaction or Lua script.

Q5: Redis vs in-process `lru_cache`?
A5: `lru_cache` is per process, lost on restart and not shared across workers or servers. Redis is shared and survives app restarts, but adds network latency (about 0.2-1 ms) and serialization cost.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- The same read happens often and the source is slow
- Several app instances need one shared cache
- You need TTL-based data: sessions, OTPs, rate limits, leaderboards

❌ Avoid when:
- The data changes constantly and must be perfectly fresh
- The value is cheap to recompute (cache overhead is bigger than the gain)
- Redis is the only copy of important data (it is a cache; persist it elsewhere)

---

## 📊 Visual Diagram

```
Client ──► FastAPI ──► Redis GET product:42
                         │
              ┌──── HIT ─┴─ MISS ────┐
              ▼                      ▼
       return in ~1 ms        query database (slow)
                                     │
                              Redis SET product:42 EX 300
                                     ▼
                                return to client

Write path:  update DB ──► Redis DEL product:42   (invalidate)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache hit / miss | Found / not found in cache | cache में मिला / नहीं मिला |
| TTL | Time-to-live before auto-delete | auto-delete होने तक का समय |
| Cache-aside | App manages cache read and fill | app खुद cache पढ़ता और भरता है |
| Invalidation | Removing stale cached data | पुराना cached data हटाना |
| Stampede | Many requests rebuild one expired key | एक expired key पर कई requests का टूट पड़ना |
| Eviction | Redis removing keys when memory is full | memory भरने पर keys हटाना |

---

## ⚡ 3-Line Summary
English: Redis caching stores slow results in memory with a TTL so repeated requests are served in about a millisecond. Use the cache-aside pattern, serialize values (JSON), and invalidate on writes. Guard hot keys against stampedes.
Hindi: Redis caching धीमे नतीजों को TTL के साथ memory में रखता है ताकि दोहराई गई requests लगभग एक millisecond में मिलें। Cache-aside pattern, JSON serialization और write पर invalidation अपनाएँ। Hot keys को stampede से बचाएँ।

---

## ➡️ Next Topic
**416. Database Query Optimization** — fix the slow query itself with indexes and better SQL, so you cache less.
