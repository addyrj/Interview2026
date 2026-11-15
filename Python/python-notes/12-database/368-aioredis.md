---

# 368. aioredis
# हिंदी में: aioredis (Async Redis — अब redis.asyncio)

---

## 🔵 Simple Definition (English)
aioredis was a separate asyncio client for Redis. Since version 2.0 it was merged into redis-py, so today you write `import redis.asyncio as redis`. Every command is awaited, so Redis calls never block the event loop.

## 🔵 सरल परिभाषा (Hindi)
aioredis Redis का अलग asyncio client था। Version 2.0 से इसे redis-py में मिला दिया गया, इसलिए आज आप `import redis.asyncio as redis` लिखते हैं। हर command पर `await` लगता है, इसलिए Redis calls event loop को block नहीं करतीं।

---

## 🔴 Problem it Solves
Sync redis-py blocks the thread while waiting for Redis. In an `async def` FastAPI app one blocked call stops every other request on that worker. An async client lets the event loop serve others while it waits. The old `aioredis` package is archived and does not support new Python versions well, so new code should use `redis.asyncio`.

## 🔴 यह क्यों बना? (Hindi)
Sync redis-py, Redis का इंतज़ार करते समय thread को block करता है। `async def` FastAPI app में एक blocked call उस worker के हर दूसरे request को रोक देती है। Async client इंतज़ार के दौरान event loop को दूसरों को serve करने देता है। पुराना `aioredis` package archived है और नए Python versions को ठीक से support नहीं करता, इसलिए नया code `redis.asyncio` इस्तेमाल करे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → import redis.asyncio as redis        (NOT "import aioredis" in new code)
Step 2 → r = redis.from_url(url, decode_responses=True)   create once, inside the running loop
Step 3 → await r.set("k", "v", ex=30);  v = await r.get("k")
Step 4 → async with r.pipeline() as pipe: ... await pipe.execute()   batch commands
Step 5 → ps = r.pubsub(); await ps.subscribe("ch"); async for msg in ps.listen(): ...
Step 6 → await asyncio.gather(r.get("a"), r.get("b"))   concurrent commands
Step 7 → await r.aclose()     (redis-py >= 5.0.1; older versions: await r.close())
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → import redis.asyncio as redis        (नए code में "import aioredis" नहीं)
Step 2 → r = redis.from_url(url, decode_responses=True)   चल रहे loop के अंदर एक बार बनाओ
Step 3 → await r.set("k", "v", ex=30);  v = await r.get("k")
Step 4 → async with r.pipeline() as pipe: ... await pipe.execute()   commands का batch
Step 5 → ps = r.pubsub(); await ps.subscribe("ch"); async for msg in ps.listen(): ...
Step 6 → await asyncio.gather(r.get("a"), r.get("b"))   commands एक साथ
Step 7 → await r.aclose()     (redis-py >= 5.0.1; पुराने versions: await r.close())
```

---

## 🟡 Real World Example
A FastAPI chat service uses Redis pub/sub through `redis.asyncio` to push messages to WebSocket users across 4 server workers. A pricing API caches computed prices in Redis and serves 5,000 concurrent requests without blocking. A job-status endpoint polls a Redis hash that a Celery worker updates.

## 🟡 Real Example Hindi mein
FastAPI chat service 4 server workers के WebSocket users तक messages पहुंचाने के लिए `redis.asyncio` का pub/sub इस्तेमाल करती है। Pricing API calculated prices को Redis में cache करती है और 5,000 concurrent requests बिना block हुए serve करती है। Job-status endpoint ऐसा Redis hash पढ़ता है जिसे Celery worker update करता है।

---

## 💻 Code Example — Basic
```python
# Basic async Redis. NOTE: the old 'aioredis' package is archived; its code lives in redis-py as redis.asyncio
import asyncio                                    # event loop
import fakeredis                                  # demo backend (prod: redis.asyncio.from_url(...))


async def main() -> None:
    r = fakeredis.FakeAsyncRedis(decode_responses=True)   # async client; prod: redis.asyncio.Redis(...)
    await r.set("greeting", "hello", ex=30)       # every command is awaited
    print(await r.get("greeting"))                # hello
    await r.incr("hits")                          # atomic counter
    await r.hset("user:1", mapping={"name": "Asha"})   # hash
    print(await r.hgetall("user:1"))              # {'name': 'Asha'}
    await r.rpush("jobs", "a", "b", "c")          # list
    print(await r.lrange("jobs", 0, -1))          # ['a', 'b', 'c']
    async with r.pipeline(transaction=True) as pipe:   # batch commands in one round trip
        pipe.incr("hits"); pipe.get("hits")       # queue commands (not awaited individually)
        print(await pipe.execute())               # [2, '2']
    await r.aclose()                              # close (redis-py >= 5.0.1; older: close())


asyncio.run(main())                               # start loop

# Output (run with fakeredis, an in-memory Redis stand-in):
# hello
# {'name': 'Asha'}
# ['a', 'b', 'c']
# [2, '2']
```

## 💻 Code Example — Advanced
```python
# Production style: async cache with stampede protection, pub/sub, timeouts, error handling
import asyncio                                    # concurrency
import json                                       # serialise
from typing import Any, Awaitable, Callable       # types
import fakeredis                                  # demo backend; prod: redis.asyncio.Redis.from_url(url, socket_timeout=2)
import redis.asyncio as aioredis                  # the replacement for the 'aioredis' package
from redis.exceptions import RedisError           # base exception

r = fakeredis.FakeAsyncRedis(decode_responses=True)   # shared client
loads: dict[str, int] = {"n": 0}                  # how many times the slow loader ran
local_locks: dict[str, asyncio.Lock] = {}         # per-key lock inside this process


async def get_or_load(key: str, loader: Callable[[], Awaitable[dict[str, Any]]], ttl: int = 30) -> dict[str, Any]:
    """Cache-aside with a per-key lock so 50 concurrent misses run the loader once."""
    try:
        hit = await r.get(key)                    # fast path
        if hit is not None:
            return json.loads(hit)                # cache hit
    except RedisError:
        return await loader()                     # Redis down -> go to source
    lock = local_locks.setdefault(key, asyncio.Lock())   # one lock per key
    async with lock:                              # only one coroutine loads
        hit = await r.get(key)                    # re-check: someone may have filled it
        if hit is not None:
            return json.loads(hit)
        value = await loader()                    # slow work, once
        await r.set(key, json.dumps(value), ex=ttl)   # fill cache
        return value


async def slow_loader() -> dict[str, Any]:
    loads["n"] += 1                               # count executions
    await asyncio.sleep(0.05)                     # pretend slow DB call
    return {"price": 499}


async def subscriber(ready: asyncio.Event, got: list[str]) -> None:
    ps = r.pubsub()                               # pub/sub needs its own object
    await ps.subscribe("alerts")                  # listen on a channel
    ready.set()                                   # tell publisher we are subscribed
    async for msg in ps.listen():                 # iterate messages
        if msg["type"] == "message":              # skip the subscribe confirmation
            got.append(msg["data"]); break        # keep one message then stop
    await ps.aclose()                             # clean up


async def main() -> None:
    results = await asyncio.gather(*[get_or_load("product:1", slow_loader) for _ in range(50)])   # 50 parallel requests
    print(len(results), loads["n"])               # 50 1
    ready, got = asyncio.Event(), []              # sync helpers
    task = asyncio.create_task(subscriber(ready, got))   # start subscriber
    await ready.wait()                            # wait until it listens
    await r.publish("alerts", "stock-low")        # broadcast
    await asyncio.wait_for(task, timeout=2)       # wait for delivery, never hang
    print(got)                                    # ['stock-low']
    try:                                          # real connection failure handling
        bad = aioredis.Redis(host="127.0.0.1", port=1, socket_connect_timeout=0.3)   # nothing listens
        await bad.ping()                          # tries to connect
    except RedisError as e:                       # ConnectionError is a RedisError
        print("Error:", type(e).__name__)         # name only
    await r.aclose()                              # close demo client


asyncio.run(main())                               # run

# Output (run with fakeredis):
# 50 1
# ['stock-low']
# Error: ConnectionError
```

Verification note: no Redis server was available, so these examples ran against `fakeredis` (same async API). With a real server replace `fakeredis.FakeAsyncRedis(...)` with `redis.asyncio.from_url("redis://localhost", decode_responses=True)`.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (redis.asyncio) | JavaScript (node-redis) |
|---------|------------------------|-------------------------|
| Connect | `redis.from_url(url)` | `createClient({url}); await client.connect()` |
| Command | `await r.get(k)` | `await client.get(k)` |
| Parallel | `asyncio.gather(...)` | `Promise.all([...])` |
| Pub/Sub | `async for msg in ps.listen()` | `client.subscribe(ch, cb)` |
| Close | `await r.aclose()` | `await client.quit()` |

```python
# Python way — async client (fakeredis for the demo)
import asyncio                                     # loop
import fakeredis                                   # use redis.asyncio.from_url(...) in production
async def main() -> None:
    r = fakeredis.FakeAsyncRedis(decode_responses=True)
    await r.set("n", 1)                            # awaited
    print(await r.incr("n"))                       # 2
    await r.aclose()
asyncio.run(main())
```
```javascript
// JavaScript way — node-redis is async by design
const client = createClient(); await client.connect();
await client.set("n", 1);
console.log(await client.incr("n"));               // 2
```

Key difference: in Node everything is async already. In Python you must choose `redis` (sync) or `redis.asyncio` (async). Forgetting `await` gives a coroutine object, not the value.

---

## 🟠 FastAPI Connection
Create the async client once in FastAPI's `lifespan`, keep it on `app.state` (or in a dependency), and `await` every call in `async def` endpoints. Use it for async caching, rate limiting, counters and pub/sub. Always set timeouts (`socket_timeout`, `socket_connect_timeout`) so a dead Redis does not hang requests, and decide what to do when Redis is down (serve from DB, or fail fast).

```python
# FastAPI + redis.asyncio: lifespan-managed client, async cache (fakeredis for the demo)
from contextlib import asynccontextmanager       # lifespan
import fakeredis                                  # prod: redis.asyncio.from_url(url, decode_responses=True)
from fastapi import FastAPI, Request              # web
from fastapi.testclient import TestClient         # demo client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = fakeredis.FakeAsyncRedis(decode_responses=True)   # create at startup
    yield
    await app.state.redis.aclose()                # close at shutdown


app = FastAPI(lifespan=lifespan)


@app.get("/visits")
async def visits(request: Request) -> dict[str, int]:
    n = await request.app.state.redis.incr("visits")   # atomic, non-blocking
    return {"visits": n}


@app.get("/cache/{key}")
async def get_cache(key: str, request: Request) -> dict[str, str | None]:
    return {key: await request.app.state.redis.get(key)}   # None -> null in JSON


with TestClient(app) as c:
    print([c.get("/visits").json()["visits"] for _ in range(3)])
    print(c.get("/cache/nothing").json())

# Output:
# [1, 2, 3]
# {'nothing': None}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Still using `import aioredis`
✅ Correct: use `redis.asyncio` (aioredis is archived and breaks on new Python versions)

```python
# Wrong — old standalone package, no longer maintained
# import aioredis
# Right
import redis.asyncio as redis
r = redis.from_url("redis://localhost:6379", decode_responses=True)
```

❌ Mistake 2: Forgetting `await`
✅ Correct: `await` every command

```python
import asyncio, fakeredis
async def main():
    r = fakeredis.FakeAsyncRedis(decode_responses=True)
    # Wrong — returns a coroutine object, nothing is read
    x = r.get("k")
    print(type(x).__name__)           # coroutine  (and a "never awaited" RuntimeWarning later)
    await x                           # awaiting it now avoids the warning
    # Right
    print(await r.get("k"))           # None
    await r.aclose()
asyncio.run(main())
```

❌ Mistake 3: No timeouts, and creating a new client per request
✅ Correct: one client with timeouts

```python
import redis.asyncio as redis
# Wrong — a new connection pool per request, and it can hang forever
async def bad() -> None:
    r = redis.Redis(host="cache")
    await r.get("k")
# Right — module/app-level client with timeouts
r_global = redis.from_url("redis://cache:6379", socket_timeout=2, socket_connect_timeout=2, decode_responses=True)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import asyncio
import fakeredis

async def main() -> None:
    r = fakeredis.FakeAsyncRedis(decode_responses=True)
    x = r.get("k")
    print(type(x).__name__)
    print(await x)
    async with r.pipeline(transaction=True) as pipe:
        pipe.incr("hits")
        pipe.get("hits")
        print(await pipe.execute())
    await r.aclose()

asyncio.run(main())
```
Answer: `coroutine`, `None`, `[1, '1']`. Calling an async command without `await` only creates a coroutine object; nothing is sent until you await it. Inside a pipeline the commands are NOT awaited one by one: you queue them, then a single `await pipe.execute()` sends all and returns a list of results (the `INCR` result is an int, the `GET` is the string '1' because Redis stores strings). Run with fakeredis 2.40 / redis-py 8.1.

---

## ⚫ Interview Questions + Answers

Q1: What happened to aioredis?
A1: Version 2.0 of aioredis was merged into redis-py 4.2 as `redis.asyncio`; the standalone package is archived. Migrate with `import redis.asyncio as redis` and mostly the same method names.

Q2: Sync `redis` vs `redis.asyncio`?
A2: Same commands. The async client returns awaitables and must be used in a running event loop. Use sync for scripts, Flask and `def` endpoints; use async for `async def` FastAPI and websockets.

Q3: How do you do pub/sub safely?
A3: Create a `pubsub()` object (it holds its own connection), `subscribe`, then loop with `async for msg in ps.listen()` and filter `msg["type"] == "message"`. Run the listener in a background task and handle reconnects. Pub/sub is fire-and-forget; for durable messages use Redis Streams.

Q4: How do you prevent a cache stampede in async code?
A4: Use a per-key `asyncio.Lock` (single process) or a Redis lock (`SET NX EX`) so only one coroutine recomputes the value while the others wait and then read the cache.

Q5: How do you close the client?
A5: `await r.aclose()` (redis-py >= 5.0.1) or `await r.close()` on older versions, and `await r.connection_pool.disconnect()` if needed. Do it in the lifespan shutdown.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- `async def` FastAPI / Starlette / aiohttp apps
- Websocket fan-out, async caching, rate limiting
- Many concurrent Redis calls with `asyncio.gather`

❌ Avoid when:
- Sync code (scripts, Django, Flask) - use plain `redis`
- You need exactly-once messaging - Redis pub/sub does not store messages
- Blocking, CPU-heavy functions are in the same loop

---

## 📊 Visual Diagram
```
coroutine A: await r.get("a") --\
coroutine B: await r.incr("b") ---+--> one event loop --> pooled sockets --> Redis
coroutine C: await r.set(...)   --/                                   |
          ^                                                           |
          +------------- resumes when reply arrives <-----------------+

pub/sub:  publisher --PUBLISH alerts--> Redis --> every subscriber's listen() loop
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `redis.asyncio` | Async client inside redis-py | redis-py के अंदर async client |
| Coroutine | Awaitable function call | Await होने वाली call |
| Pub/Sub | Publish and subscribe to channels | Channels पर publish और subscribe |
| Pipeline | Batch commands | Commands का batch |
| Stampede | Many misses at once | एक साथ बहुत सारे cache miss |
| `aclose()` | Async close of client | Client का async close |

---

## ⚡ 3-Line Summary
English: aioredis is now `redis.asyncio` inside redis-py: the same Redis commands, but awaited so the event loop stays free. Create one client in the FastAPI lifespan, set timeouts, await every call, use pipelines, `gather` and pub/sub, and never import the archived `aioredis` package in new code.
Hindi: aioredis अब redis-py के अंदर `redis.asyncio` है: वही Redis commands, पर `await` के साथ ताकि event loop खाली रहे। FastAPI lifespan में एक client बनाएं, timeouts लगाएं, हर call पर await करें, pipelines, `gather` और pub/sub इस्तेमाल करें, और नए code में archived `aioredis` package कभी import न करें।

---

## ➡️ Next Topic
**369. Elasticsearch-py** — full-text search from Python (a later topic, already covered in this folder).
