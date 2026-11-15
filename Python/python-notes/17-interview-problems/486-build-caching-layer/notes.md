---

# 486. Build Caching Layer
# हिंदी में: Caching Layer बनाना (TTL + LRU)

Full runnable solution: [main.py](main.py) (TTLCache, `@cached` decorator, fake clock tests).

---

## 🔵 Simple Definition (English)
A cache stores the result of expensive work so the next identical request is answered from memory. A TTL makes entries expire; an LRU rule removes the least recently used entry when the cache is full.

## 🔵 सरल परिभाषा (Hindi)
Cache महँगे काम का नतीजा memory में रखता है ताकि अगली वही request वहीं से मिल जाए। TTL से entry expire होती है, और LRU नियम cache भर जाने पर सबसे कम इस्तेमाल हुई entry हटाता है।

---

## 🔴 Problem it Solves
Repeating the same database query or API call for every request is slow and costly, and can overload the database. Caching cuts latency and load. But unlimited caches leak memory and never-expiring ones serve stale data, hence TTL and LRU.

## 🔴 यह क्यों बना? (Hindi)
हर request पर वही database query या API call दोहराना धीमा और महँगा है और database पर बोझ डालता है। Cache से latency और load घटता है। पर बिना सीमा का cache memory खाता है और कभी expire न होने वाला पुराना data देता है, इसलिए TTL और LRU चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Build key = (function name, args, kwargs)
Step 2 → get(key): missing or expired? -> miss (count it)
Step 3 → Miss: call the real function, set(key, value, expires_at=now+ttl)
Step 4 → Hit: move key to the end of OrderedDict (most recently used)
Step 5 → If len > max_size: popitem(last=False) removes the oldest (LRU)
Step 6 → invalidate(key) deletes it when the data changes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → key = (function का नाम, args, kwargs) बनता है
Step 2 → get(key): नहीं मिला या expire हुआ -> miss
Step 3 → Miss पर असली function चलता है और नतीजा expires_at=now+ttl के साथ सेव होता है
Step 4 → Hit पर key को OrderedDict के अंत में ले जाते हैं (सबसे हाल का)
Step 5 → size max_size से ज़्यादा हो तो सबसे पुरानी entry हटती है (LRU)
Step 6 → data बदले तो invalidate(key) से entry हटाते हैं
```

---

## 🟡 Real World Example
An e-commerce product page: the product details change rarely but are read thousands of times per minute. Cache them for 60 seconds, so the database sees one query per product per minute instead of thousands. For many servers, use Redis rather than an in-process cache.

## 🟡 Real Example Hindi mein
E-commerce product page: product की details कम बदलती हैं पर हर मिनट हज़ारों बार पढ़ी जाती हैं। 60 सेकंड cache करने पर database को हर product के लिए हज़ारों की जगह मिनट में एक query मिलती है। कई servers हों तो in-process की जगह Redis इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Built-in LRU cache from the standard library
from functools import lru_cache  # memoization decorator

calls: list[int] = []  # records real executions

@lru_cache(maxsize=2)  # keep the 2 most recently used results
def square(n: int) -> int:  # expensive function stand-in
    calls.append(n)  # note that the body really ran
    return n * n  # the result

square(3); square(3)  # second call is served from cache
square(4); square(5)  # cache full: 3 is evicted
square(3)  # recomputed because it was evicted
print(calls)  # which calls really ran
print(square.cache_info())  # hits, misses, size
# Output:
# [3, 4, 5, 3]
# CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: TTL + LRU, injectable clock for tests
class TTLCache:
    def __init__(self, max_size: int = 128, ttl: float = 60.0, clock=time.monotonic) -> None:
        self.max_size, self.ttl, self.clock = max_size, ttl, clock
        self._data: OrderedDict[Hashable, tuple[float, Any]] = OrderedDict()  # key -> (expires_at, value)
        self.hits = self.misses = 0

    def get(self, key: Hashable, default: Any = None) -> Any:
        item = self._data.get(key)
        if item is None or item[0] <= self.clock():  # missing or expired
            self._data.pop(key, None)
            self.misses += 1
            return default
        self._data.move_to_end(key)  # mark recently used
        self.hits += 1
        return item[1]
```
Real output of `python main.py`:
```
hits 1 misses 5 size 1
all ok
```

---

## 🟠 JavaScript vs Python Comparison
JS: `Map` keeps insertion order so LRU is `delete` + `set`; libraries like `lru-cache`. Python: `OrderedDict.move_to_end` or `functools.lru_cache`.

```python
# Python way
cache.move_to_end(key)       # mark recently used
cache.popitem(last=False)    # evict oldest
```
```javascript
// JavaScript way (Map keeps insertion order)
const v = map.get(key); map.delete(key); map.set(key, v); // mark recent
map.delete(map.keys().next().value);                      // evict oldest
```

---

## 🟠 FastAPI Connection
Cache expensive dependencies or endpoint results. `functools.lru_cache` on `get_settings()` is the standard FastAPI pattern. For response caching use Redis with `fastapi-cache2` or manual `get/set` with TTL.

```python
from functools import lru_cache  # cache the settings object
from fastapi import Depends, FastAPI  # framework

app = FastAPI()  # app

@lru_cache  # settings are built once per process
def get_settings() -> dict[str, str]:
    return {"env": "prod"}  # imagine reading .env here

@app.get("/env")
def env(s: dict[str, str] = Depends(get_settings)) -> dict[str, str]:
    return s  # same dict every time
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Caching without TTL or invalidation, so users see stale data forever.
✅ Correct: set a TTL and invalidate on writes.

❌ Mistake 2: Using `lru_cache` on methods or on functions with mutable results; the cache keeps `self` alive and callers can mutate the shared cached object.
✅ Correct: return immutable data (tuples, frozen dataclasses) or copies.

```python
# Wrong: cached list is shared and mutable
@lru_cache
def tags() -> list[str]: return ["a"]
tags().append("b")   # corrupts the cache
# Right
@lru_cache
def tags() -> tuple[str, ...]: return ("a",)
```

❌ Mistake 3: Cache stampede: when a hot key expires, 1000 requests hit the database together.
✅ Correct: lock per key, or refresh slightly before expiry.

---

## 🧠 Tricky Interview Question
```python
from functools import lru_cache
@lru_cache(maxsize=None)
def f(x): return x
print(f([1]))
```
Answer: `TypeError: unhashable type: 'list'`. `lru_cache` builds its key from the arguments, so they must be hashable. Also note in `main.py` the `_MISSING` sentinel: without it, a cached `None` would be treated as a miss.

---

## ⚫ Interview Questions + Answers

Q1: What are cache-aside, write-through and write-back?
A1: Cache-aside: app reads cache, on miss loads DB and fills cache. Write-through: write cache and DB together. Write-back: write cache first, DB later (fast, risk of loss).

Q2: How do you avoid stale data?
A2: TTL, explicit invalidation on update, versioned keys.

Q3: LRU vs LFU?
A3: LRU evicts least recently used; LFU evicts least frequently used. LRU is simpler and good for most workloads.

Q4: What is a cache stampede?
A4: Many requests recompute the same expired key at once. Use locks, request coalescing or early refresh.

Q5: In-process cache vs Redis?
A5: In-process is fastest but per-process and lost on restart; Redis is shared across servers and survives restarts but adds a network hop.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Read-heavy, expensive, slowly changing data

❌ Avoid when:
- Data must always be exact (account balance during payment)
- Keys are almost never repeated (low hit rate)

---

## 📊 Visual Diagram
```
 request ──► cache.get(key) ──hit──► return value
                 │ miss
                 ▼
            real function / DB ──► cache.set(key, value, ttl)
 OrderedDict: [oldest ... newest]   full -> popitem(last=False)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cache hit | Found in cache | cache में मिला |
| Cache miss | Not found, compute | cache में नहीं मिला |
| TTL | Time to live | जीवन-अवधि |
| LRU | Evict least recently used | सबसे कम हाल में इस्तेमाल हुआ हटाओ |
| Invalidation | Removing stale entry | पुरानी entry हटाना |

---

## ⚡ 3-Line Summary
English: A cache answers repeated requests from memory.
TTL expires old entries; LRU removes the least recently used when full.
Always plan invalidation and watch for stampedes.
Hindi: Cache दोहराई गई requests को memory से जवाब देता है।
TTL पुरानी entries expire करता है; भर जाने पर LRU सबसे कम इस्तेमाल वाली हटाता है।
Invalidation की योजना रखो और stampede से बचो।

---

## ➡️ Next Topic
487. Build Rate Limiter: caching protects your database from repeat reads; rate limiting protects your API from abusive callers.

---
