---

# Q083. Implement memoize decorator
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write a `@memoize` decorator that caches a function's results by its arguments (positional and keyword). Calling again with the same arguments must return the cached value without re-running the function.

```python
@memoize
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
fib(30)  # fast — each n computed once
```

---

## 💡 Quick Concept (2 lines only)
Store results in a dict keyed by `(args, sorted kwargs)`; return the cached value if present. Arguments must be hashable — and it only suits pure functions (same input, same output).
हिंदी: Arguments को key बनाकर result dict में रखो; दोबारा वही call आए तो cache से दो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools                                       # wraps + stdlib caches
from typing import Any, Callable                       # type hints

def memoize(fn: Callable[..., Any]) -> Callable[..., Any]:
    cache: dict = {}                                   # Step 1: key -> result store

    @functools.wraps(fn)                               # Step 2: keep fn.__name__ etc.
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, tuple(sorted(kwargs.items())))    # Step 3: hashable key; sorted so f(a=1,b=2) == f(b=2,a=1)
        if key not in cache:                           # Step 4: first time with these arguments?
            cache[key] = fn(*args, **kwargs)           # compute and store
        return cache[key]                              # Step 5: return stored value

    wrapper.cache = cache  # type: ignore[attr-defined]  # expose cache for inspection/clearing
    return wrapper                                     # Step 6: return decorated function

# ============================================
# TEST CASES
# ============================================
calls = 0                                              # counts real executions

@memoize
def fib(n: int) -> int:
    global calls                                       # update module-level counter
    calls += 1                                         # one real execution
    return n if n < 2 else fib(n - 1) + fib(n - 2)     # recursive calls also hit the cache

print(fib(30), calls)                                  # Expected: 832040 31   (31 calls instead of ~2.7 million)
print(fib(30), calls)                                  # Expected: 832040 31   (second call: pure cache hit)
print(len(fib.cache), fib.__name__)                    # Expected: 31 fib

@memoize
def add(a: int, b: int = 0) -> int:
    return a + b                                       # simple function with a keyword arg
print(add(1, b=2), add(1, b=2), len(add.cache))        # Expected: 3 3 1
try:
    add([1], 2)                                        # list is unhashable
except TypeError as e:
    print("TypeError:", e)                             # Expected: TypeError: unhashable type: 'list'
```

---

## 🔍 Why This Works (3 lines max)
The wrapper builds a hashable key from the arguments and only calls `fn` on a cache miss. Because the recursive `fib` calls the memoized name, every sub-problem is computed once, turning O(2^n) into O(n).
हिंदी: Key से cache check होता है; miss पर ही असली function चलता है, इसलिए fib O(n) हो जाता है।

---

## ⚡ Alternative Solution
```python
# Pythonic: functools.cache (unbounded) / lru_cache (bounded, evicts least-recently-used)
import functools                                       # stdlib caches

@functools.cache                                       # Python 3.9+, same as lru_cache(maxsize=None)
def fib2(n: int) -> int:
    return n if n < 2 else fib2(n - 1) + fib2(n - 2)   # recursive, cached

print(fib2(80), fib2.cache_info())                     # Expected: 23416728348467685 CacheInfo(hits=78, misses=81, maxsize=None, currsize=81)

@functools.lru_cache(maxsize=2)                        # keep only 2 results
def sq(n: int) -> int:
    print("calc", n)                                   # shows when real work happens
    return n * n
sq(1); sq(2); sq(1); sq(3); sq(2)                      # Expected prints: calc 1, calc 2, calc 3, calc 2  (3 evicted 2)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: key uses only the first argument -> different calls collide
def bad_memo(fn):
    cache: dict = {}                                   # store
    def w(*a):
        if a[0] not in cache:                          # ❌ ignores a[1:]
            cache[a[0]] = fn(*a)
        return cache[a[0]]
    return w

@bad_memo
def mul(a: int, b: int) -> int:
    return a * b

print(mul(2, 3), mul(2, 5))                            # Output: 6 6  <- second answer should be 10
# ✅ Correct: key on ALL arguments (args + sorted kwargs), or just use functools.cache
# ⚠️ Also: memoizing impure functions (time, random, DB) returns stale data
```

---

## 🎯 Interview Tip (1 line)
Say: "In real code I'd use functools.lru_cache with a maxsize to avoid unbounded memory — and only on pure functions with hashable args."

---

## 🔗 Related Questions
→ Q099 (LRU cache) | Q143 (complete memoize) | Q215 (memoize async) | Q278 (lru_cache) | Q251 (functools)
