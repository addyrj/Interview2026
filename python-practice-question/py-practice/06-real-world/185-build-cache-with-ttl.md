---

# Q185. Build Cache with TTL
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a `TTLCache(ttl)` with `set(key, value, ttl=None)` and `get(key, default)`. Entries must expire after their time-to-live. Make the clock injectable so it can be tested without sleeping.

```python
c = TTLCache(ttl=10)
c.set("a", 1)
c.get("a")   # 1 now, None after 10 seconds
```

---

## 💡 Quick Concept (2 lines only)
Store `(value, expires_at)` per key; on `get`, compare the current time with `expires_at` and lazily delete stale entries. Use `time.monotonic` — it never goes backwards.
हिंदी: हर key के साथ expiry time रखो; get करते समय check करो — expire हो गया तो delete करके default दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time  # real clock
from typing import Any, Callable  # type hints

class TTLCache:
    def __init__(self, ttl: float, clock: Callable[[], float] = time.monotonic) -> None:
        self.ttl = ttl  # seconds an entry lives
        self.clock = clock  # injectable clock (testable)
        self._data: dict[Any, tuple[Any, float]] = {}  # key -> (value, expires_at)

    def set(self, key: Any, value: Any, ttl: float | None = None) -> None:
        self._data[key] = (value, self.clock() + (self.ttl if ttl is None else ttl))  # store expiry

    def get(self, key: Any, default: Any = None) -> Any:
        item = self._data.get(key)  # look up
        if item is None:
            return default  # missing
        value, expires = item  # unpack
        if self.clock() >= expires:  # expired?
            del self._data[key]  # lazy eviction
            return default  # treat as missing
        return value  # still fresh

    def __len__(self) -> int:
        now = self.clock()  # current time
        self._data = {k: v for k, v in self._data.items() if v[1] > now}  # purge expired
        return len(self._data)  # live count

# ============================================
# TEST CASES
# ============================================
t = [0.0]  # fake time
c = TTLCache(ttl=10, clock=lambda: t[0])  # cache with fake clock
c.set("a", 1)  # expires at 10
c.set("b", 2, ttl=3)  # expires at 3
print(c.get("a"), c.get("b"), len(c))  # Expected: 1 2 2
t[0] = 5  # advance 5s
print(c.get("a"), c.get("b", "gone"), len(c))  # Expected: 1 gone 1
t[0] = 10  # advance to expiry boundary
print(c.get("a", "gone"), len(c))  # Expected: gone 0
```

---

## 🔍 Why This Works (3 lines max)
Each entry carries its own deadline, so per-key TTLs are free. Expired entries are removed lazily on access (O(1)), and `__len__` sweeps the rest. The injected clock makes time-based tests deterministic.
हिंदी: हर entry की अपनी deadline है; access पर expired entry हट जाती है, और fake clock से test आसान होता है।

---

## ⚡ Alternative Solution
```python
import time  # clock
from functools import wraps  # metadata

def ttl_cache(ttl: float, clock=time.monotonic):  # decorator version
    def deco(fn):
        store: dict = {}  # args -> (value, expires)
        @wraps(fn)
        def wrapper(*args):
            now = clock()  # current time
            hit = store.get(args)  # lookup
            if hit and hit[1] > now:
                return hit[0]  # fresh hit
            val = fn(*args)  # recompute
            store[args] = (val, now + ttl)  # save
            return val
        return wrapper
    return deco

t = [0.0]  # fake time
calls = 0  # compute counter
@ttl_cache(5, clock=lambda: t[0])
def square(x: int) -> int:
    global calls
    calls += 1  # count real computations
    return x * x

print(square(4), square(4), calls)  # Expected: 16 16 1
t[0] = 6  # expire
print(square(4), calls)  # Expected: 16 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: time.time() can jump (NTP/clock change); never evicting -> memory leak (not run)
# self._data[key] = (value, time.time() + ttl)
# ... get() returns value without checking expiry, expired keys stay forever

# ✅ Correct: time.monotonic(), check expiry on get, and purge periodically
#             (or cap size with LRU so the cache cannot grow without bound)
```

---

## 🎯 Interview Tip (1 line)
Say: "Lazy expiry on read plus an injectable monotonic clock; mention max-size/LRU and thread-safety (a Lock) for production."

---

## 🔗 Related Questions
→ Q099 (LRU cache) | Q083 (memoize) | Q194 (data fetcher with caching) | Q278 (lru_cache)
