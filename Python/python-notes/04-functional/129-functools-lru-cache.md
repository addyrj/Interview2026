---

# 129. functools.lru_cache
# हिंदी में: functools.lru_cache (results याद रखने वाला cache)

---

## 🔵 Simple Definition (English)
`@lru_cache(maxsize=128)` remembers the results of a function call, keyed by its arguments. If you call the function again with the same arguments, you get the stored result instantly. When the cache is full, the Least Recently Used entry is thrown away.

## 🔵 सरल परिभाषा (Hindi)
`@lru_cache(maxsize=128)` function call के results arguments के हिसाब से याद रखता है। वही arguments दोबारा आएं तो stored result तुरंत मिलता है। Cache भर जाए तो सबसे पुराना (Least Recently Used) entry हटा दिया जाता है।

---

## 🔴 Problem it Solves
Some functions are slow (a DB query, an API call, recursive Fibonacci) and are called repeatedly with the same inputs. Recomputing wastes time and money. Writing your own dict cache means handling size limits, eviction, thread safety and stats. `lru_cache` gives all that in one decorator line.

## 🔴 यह क्यों बना? (Hindi)
कुछ functions धीमे होते हैं (DB query, API call, recursive Fibonacci) और बार-बार वही inputs आते हैं। दोबारा compute करना समय और पैसा बर्बाद करता है। अपना dict cache लिखने पर size limit, eviction, thread safety और stats खुद संभालने पड़ते हैं। `lru_cache` यह सब एक decorator line में देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → @lru_cache wraps the function and creates a dict + a linked list
Step 2 → On call, args are turned into a hashable key
Step 3 → Key found (HIT): return stored value, mark as most recently used
Step 4 → Key missing (MISS): run the function, store the result
Step 5 → If size > maxsize: drop the least recently used entry
Step 6 → cache_info() shows hits/misses; cache_clear() empties it

maxsize=2:  f(1) f(2) f(1) f(3)  -> evicts f(2) (least recently used), keeps f(1), f(3)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → @lru_cache function को wrap करके dict + linked list बनाता है
Step 2 → Call पर arguments से hashable key बनती है
Step 3 → Key मिली (HIT): stored value लौटाओ, उसे सबसे हाल का use मार्क करो
Step 4 → Key नहीं मिली (MISS): function चलाओ, result सहेजो
Step 5 → size > maxsize हो तो सबसे पुराना use हुआ entry हटाओ
Step 6 → cache_info() hits/misses दिखाता है; cache_clear() खाली करता है
```

---

## 🟡 Real World Example
An AI app computes embeddings for product descriptions: `@lru_cache(maxsize=10_000)` skips repeat API calls. A FastAPI service loads settings once with `@lru_cache`. A pricing service caches `get_tax_rate(state)` since only ~30 states exist. Dynamic-programming interview solutions (Fibonacci, grid paths, coin change) become O(n) with one decorator.

## 🟡 Real Example Hindi mein
AI app product descriptions के embeddings निकालता है: `@lru_cache(maxsize=10_000)` दोहराए गए API calls बचाता है। FastAPI service settings एक बार `@lru_cache` से load करती है। Pricing service `get_tax_rate(state)` cache करती है क्योंकि सिर्फ ~30 states हैं। Dynamic-programming interview solutions (Fibonacci, grid paths, coin change) एक decorator से O(n) हो जाते हैं।

---

## 💻 Code Example — Basic
```python
# Basic lru_cache
from functools import lru_cache                    # the decorator

calls: int = 0                                     # count real executions


@lru_cache(maxsize=128)                            # keep up to 128 results
def square(n: int) -> int:
    global calls                                   # we modify the module-level counter
    calls += 1                                     # one real computation
    return n * n


print(square(4), square(4), square(5))             # 4 is computed once, 5 once
print("real calls:", calls)                         # only 2 despite 3 invocations
print(square.cache_info())                         # hits=1, misses=2
square.cache_clear()                               # forget everything
print(square.cache_info())                         # counters reset


@lru_cache(maxsize=None)                           # unbounded; same as @cache (3.9+)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2) # each n computed once


print(fib(80))                                     # would take forever without the cache
print(fib.cache_info().currsize)                   # 81 stored values (0..80)

@lru_cache(maxsize=2)                              # tiny cache to show LRU eviction
def f(x: int) -> int:
    print(f"computing {x}")                        # visible on a miss
    return x

f(1); f(2); f(1); f(3)                             # 3 evicts 2 (1 was used more recently)
f(1)                                               # still cached
f(2)                                               # recomputed

# Output:
# 16 16 25
# real calls: 2
# CacheInfo(hits=1, misses=2, maxsize=128, currsize=2)
# CacheInfo(hits=0, misses=0, maxsize=128, currsize=0)
# 23416728348467685
# 81
# computing 1
# computing 2
# computing 3
# computing 2
```

## 💻 Code Example — Advanced
```python
# Production style: cached lookups with TTL, tuple args, and safe use with classes
import time                                        # for TTL bucket
from functools import lru_cache                    # cache decorator
from typing import Hashable                        # type hint for cache keys


def ttl_bucket(seconds: int) -> int:
    """Changing number every `seconds`: use as an extra argument to expire entries."""
    return int(time.time() // seconds)             # same value inside one window


@lru_cache(maxsize=256)                            # bounded for servers
def _tax_rate(state: str, bucket: int) -> float:
    print(f"fetching rate for {state}")            # shows real fetches
    return {"MH": 0.18, "KA": 0.18}.get(state, 0.12)    # pretend remote call


def tax_rate(state: str, ttl: int = 3600) -> float:
    """Public API: result is cached for ~ttl seconds per state."""
    return _tax_rate(state.upper(), ttl_bucket(ttl))     # bucket changes -> new key


print(tax_rate("mh"), tax_rate("MH"))              # second call hits the cache
print(tax_rate("ka"))                              # different key: fetch again


@lru_cache(maxsize=32)                             # key must be hashable
def total(prices: tuple[int, ...]) -> int:
    return sum(prices)                             # tuples are hashable, lists are not


def total_of(xs: list[int]) -> int:
    return total(tuple(xs))                        # convert the list at the boundary


print(total_of([1, 2, 3]), total_of([1, 2, 3]))    # 6 6
print(total.cache_info().hits)                     # 1

# typed=True keeps 1 and 1.0 apart; default merges them
@lru_cache(maxsize=None, typed=True)
def ident(x: Hashable) -> Hashable:
    return x

ident(1); ident(1.0)                               # two entries because typed=True
print(ident.cache_info().currsize)                 # 2


# Methods: lru_cache on a method caches `self` too (keeps objects alive!)
class Repo:
    def __init__(self, name: str) -> None:
        self.name = name                           # simple state

    @lru_cache(maxsize=8)                          # caution: self is part of the key
    def load(self, key: int) -> str:
        return f"{self.name}:{key}"

r = Repo("db")                                     # object that gets cached
print(r.load(1), r.load(1))                        # works...
print(Repo.load.cache_info().currsize)             # ...but the cache now holds `r` alive

# Output:
# fetching rate for MH
# 0.18 0.18
# fetching rate for KA
# 0.18
# 6 6
# 1
# 2
# db:1 db:1
# 1
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Built-in memoize | `@lru_cache` / `@cache` | none (lodash `_.memoize`, no LRU) |
| Eviction | LRU automatic | manual (use `Map` order trick) |
| Stats | `cache_info()` | manual |
| Key | hashable arguments | usually `JSON.stringify(args)` |
| Clear | `cache_clear()` | clear your Map |

```python
# Python way
from functools import lru_cache
@lru_cache(maxsize=None)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(50))                                     # 12586269025
```
```javascript
// JavaScript way — hand-written memo
const memo = new Map();                            // cache storage
function fib(n) {
  if (n < 2) return n;                             // base case
  if (memo.has(n)) return memo.get(n);             // hit
  const v = fib(n - 1) + fib(n - 2);               // compute
  memo.set(n, v);                                  // store
  return v;
}
console.log(fib(50));                              // 12586269025
```

Key difference: Python gives memoization + eviction + stats in a single decorator; JS needs a Map and manual logic (and a hand-made LRU if you want eviction).

---

## 🟠 FastAPI Connection
The standard FastAPI pattern: `@lru_cache` on `get_settings()` so env vars are parsed once, then inject it with `Depends`. You can also cache pure lookups like country codes. Do NOT cache per-user or per-request data, and remember each worker process (uvicorn/gunicorn worker) has its OWN cache.

```python
# FastAPI example — cache a pure lookup and expose cache stats
from functools import lru_cache                    # cache decorator
from fastapi import FastAPI                        # app
from fastapi.testclient import TestClient          # in-process test client

app: FastAPI = FastAPI()                           # create app


@lru_cache(maxsize=512)                            # pure function: safe to cache
def gst_amount(price: int, rate: int) -> float:
    return round(price * rate / 100, 2)            # no side effects


@app.get("/gst")                                   # GET /gst?price=1000&rate=18
def gst(price: int, rate: int = 18) -> dict[str, float]:
    return {"gst": gst_amount(price, rate)}        # cached per (price, rate)


@app.get("/gst/stats")                             # monitoring endpoint
def stats() -> dict[str, int]:
    info = gst_amount.cache_info()                 # hit/miss counters
    return {"hits": info.hits, "misses": info.misses}


c = TestClient(app)                                # test it
c.get("/gst", params={"price": 1000}); c.get("/gst", params={"price": 1000})
print(c.get("/gst/stats").json())                  # {'hits': 1, 'misses': 1}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Caching functions with side effects or time-dependent results
✅ Correct: cache only pure functions, or add a TTL bucket argument

```python
from functools import lru_cache
import time
# Wrong — returns the same "now" forever
@lru_cache
def now() -> float: return time.time()
print(now() == now())       # True  <- stale
```

❌ Mistake 2: Passing lists / dicts
✅ Correct: pass tuples / frozensets

```python
from functools import lru_cache
@lru_cache
def f(xs): return sum(xs)
# Wrong: f([1, 2])  -> TypeError: unhashable type: 'list'
# Right
print(f((1, 2)))            # 3
```

❌ Mistake 3: Using it on instance methods and on unbounded input spaces
✅ Correct: use module-level functions, set `maxsize`, or use `cached_property`

```python
# Wrong: @lru_cache on a method keeps every `self` alive forever (memory leak)
# Right: cache a module-level function that takes only plain values,
#        or use functools.cached_property for per-instance results
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from functools import lru_cache

@lru_cache(maxsize=None)
def add(a, b):
    print("run")
    return a + b

add(1, 2)
add(1, 2)
add(a=1, b=2)
add(2, 1)
print(add.cache_info().misses)
```
Answer: Output is `run` three times, then `3`. `add(1, 2)` runs once and the second identical call is a hit. But `add(a=1, b=2)` is a DIFFERENT cache key (keyword arguments are cached separately from positional ones), so it runs again; `add(2, 1)` is also a different key. That makes 3 misses.

---

## ⚫ Interview Questions + Answers

Q1: What does LRU mean and how is it done in O(1)?
A1: Least Recently Used: when full, evict the entry unused for the longest time. CPython's C implementation uses a dict plus a circular doubly-linked list, so lookup, move-to-front and eviction are all O(1).

Q2: What is the difference between `lru_cache` and `cache`?
A2: `cache` (3.9+) is `lru_cache(maxsize=None)`: no eviction, slightly faster, can grow forever. `lru_cache(maxsize=N)` is bounded. Use `cache` for small fixed input sets (like Fibonacci), `lru_cache(maxsize=N)` for servers.

Q3: Is `lru_cache` thread-safe?
A3: The cache data structure is protected, so it won't be corrupted. But the wrapped function may run more than once concurrently for the same key (two threads can both miss and compute). It is not designed for asyncio coroutines: it would cache the coroutine object, not the awaited result.

Q4: How do I invalidate or inspect the cache?
A4: `f.cache_clear()` empties it; `f.cache_info()` returns `CacheInfo(hits, misses, maxsize, currsize)`; `f.cache_parameters()` (3.9+) shows settings. There is no per-key delete, so use a TTL bucket argument if you need expiry.

Q5: Can you cache an `async def`?
A5: Not with `lru_cache`: it would store the coroutine object, which can be awaited only once. Use a library like `async-lru` / `aiocache`, or cache the result with your own dict.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The function is pure and deterministic
- Same inputs repeat often (config, lookups, recursion, DP)
- Arguments are small and hashable

❌ Avoid when:
- It has side effects or depends on time / randomness / DB state
- Arguments are huge or unhashable
- It is an `async def` or a method on large objects
- You need shared cache across processes (use Redis)

---

## 📊 Visual Diagram
```
maxsize=2

call f(1) -> MISS  cache: [1]
call f(2) -> MISS  cache: [1, 2]
call f(1) -> HIT   cache: [2, 1]      (1 becomes most recent)
call f(3) -> MISS  cache: [1, 3]      (2 evicted: least recently used)

cache_info(): hits=1, misses=3, maxsize=2, currsize=2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memoization | Cache results by arguments | Arguments के हिसाब से results cache |
| LRU | Evict least recently used | सबसे पुराना use हुआ हटाओ |
| Hit / Miss | Found / not found in cache | Cache में मिला / नहीं मिला |
| Pure function | Same input -> same output, no side effects | Same input पर same output, side effect नहीं |
| TTL | Time to live of an entry | Entry की जीवन अवधि |
| Hashable | Usable as a dict key | Dict key बन सकने वाला |

---

## ⚡ 3-Line Summary
English: `@lru_cache` memoizes a pure function by its hashable arguments and evicts the least recently used entries beyond `maxsize`. Check it with `cache_info()` and reset with `cache_clear()`. Avoid it for side effects, unhashable arguments, async functions and methods.
Hindi: `@lru_cache` pure function को उसके hashable arguments से memoize करता है और `maxsize` से ज्यादा होने पर सबसे पुराने use हुए entries हटाता है। `cache_info()` से जाँचें और `cache_clear()` से reset करें। Side effects, unhashable arguments, async functions और methods में इसे न लगाएं।

---

## ➡️ Next Topic
**130. functools.partial** — freeze some arguments and get a simpler function.
