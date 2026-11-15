---

# Q143. Complete Memoize Decorator
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks so repeated calls with the same arguments return the cached result.

```python
from functools import wraps
from typing import Any, Callable


def memoize(fn: Callable) -> Callable:
    cache: dict[Any, Any] = {}                     # key -> result

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, ____(sorted(kwargs.items())))  # BLANK 1: make kwargs hashable
        if key ____ cache:                          # BLANK 2: cache miss test
            cache[key] = ____(*args, **kwargs)      # BLANK 3: compute and store
        return cache[key]

    wrapper.cache = cache                          # expose the cache
    return wrapper
```

---

## 💡 Quick Concept (2 lines only)
Memoization stores `args -> result` in a dict; the key must be hashable, so kwargs are turned into a sorted tuple.
हिंदी: Memoize पुराने results dict में रखता है — key hashable होनी चाहिए, इसलिए kwargs को tuple बनाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from functools import wraps                        # keep metadata
from typing import Any, Callable


def memoize(fn: Callable) -> Callable:             # decorator
    cache: dict[Any, Any] = {}                     # Step 1: private cache

    @wraps(fn)                                     # Step 2: preserve name/docstring
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))  # BLANK 1: hashable key (order of kwargs ignored)
        if key not in cache:                       # BLANK 2: miss -> compute
            cache[key] = fn(*args, **kwargs)       # BLANK 3: call real function, store
        return cache[key]                          # Step 3: return cached value

    wrapper.cache = cache                          # expose for inspection/clearing
    return wrapper


# ============================================
# TEST CASES
# ============================================
calls = 0                                          # count real executions

@memoize
def fib(n: int) -> int:
    global calls                                   # modify the module counter
    calls += 1                                     # one real execution
    return n if n < 2 else fib(n - 1) + fib(n - 2)  # recursive calls hit the cache

print(fib(30))                                     # Expected: 832040
print(calls)                                       # Expected: 31  (not 1.6 million)
print(fib(30), calls)                              # Expected: 832040 31  (all cached)

@memoize
def area(w: int, h: int = 1) -> int:
    return w * h                                   # simple function with kwargs

area(2, h=3); area(2, h=3)                         # same key twice
print(len(area.cache))                             # Expected: 1
```

---

## 🔍 Why This Works (3 lines max)
The wrapper builds a hashable key, returns the stored value on a hit, and otherwise computes and stores it. Recursive `fib` calls go through the wrapper, so each `n` is computed exactly once.
हिंदी: Key बनाकर dict में देखते हैं — मिली तो वही result, नहीं तो compute करके store करते हैं।

---

## ⚡ Alternative Solution
```python
# Built-in: functools.cache (unbounded) / lru_cache (bounded)
from functools import cache, lru_cache

@cache                                             # unbounded memoization (3.9+)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)  # recursion is cached

print(fib(30))                                     # Expected: 832040
print(fib.cache_info())                            # Expected: CacheInfo(hits=28, misses=31, maxsize=None, currsize=31)

@lru_cache(maxsize=2)                              # keep only 2 newest results
def sq(n: int) -> int:
    return n * n

sq(1); sq(2); sq(3)                                # 1 gets evicted
print(sq.cache_info().currsize)                    # Expected: 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: unhashable arguments crash the cache key
# memoized_sum([1, 2, 3])   # TypeError: unhashable type: 'list'
#
# ❌ Wrong: key = args only -> f(1, x=2) and f(1, x=3) share one entry (wrong results)
#
# ✅ Correct: include kwargs in the key; for lists convert to tuple first, e.g. memoized_sum(tuple(xs))
```

---

## 🎯 Interview Tip (1 line)
Say: "Memoize only pure functions, keys must be hashable, and unbounded caches leak memory — prefer `lru_cache(maxsize=...)` in production."

---

## 🔗 Related Questions
→ Q083 (implement memoize) | Q099 (LRU cache) | Q150 (complete LRU) | Q215 (memoize async) | Q278 (lru_cache)
