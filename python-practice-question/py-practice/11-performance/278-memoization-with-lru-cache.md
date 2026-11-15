---

# Q278. Memoization with lru_cache
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Recursive `fib(35)` is painfully slow. Speed it up with `functools.lru_cache`, show the cache statistics, and explain the limits (hashable arguments, memory growth).

---

## 💡 Quick Concept (2 lines only)
`lru_cache` stores results keyed by the arguments, so repeated calls return instantly. It turns exponential recursion O(2^n) into O(n).
हिंदी: `lru_cache` function के result को arguments के साथ याद रखता है, इसलिए वही call दोबारा तुरंत मिलती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import timeit  # Step 1: to measure the speedup
from functools import lru_cache  # Step 2: the cache decorator


def fib_slow(n: int) -> int:
    return n if n < 2 else fib_slow(n - 1) + fib_slow(n - 2)  # exponential recursion


@lru_cache(maxsize=None)  # Step 3: unlimited cache (3.9+: same as @cache)
def fib_fast(n: int) -> int:
    return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)  # each n computed once


# ============================================
# TEST CASES
# ============================================
print(fib_slow(25), fib_fast(25))  # Expected: 75025 75025
print(fib_fast(80))  # Expected: 23416728348467685  (fib_slow(80) would take years)
print(fib_fast.cache_info())  # Expected: CacheInfo(hits=78, misses=81, maxsize=None, currsize=81)
t_slow = timeit.timeit(lambda: fib_slow(25), number=1)  # time slow version once
fib_fast.cache_clear()  # empty cache so the test is fair
t_fast = timeit.timeit(lambda: fib_fast(25), number=1)  # time cached version
print(t_slow / t_fast > 100)  # Expected: True  (measured: ~8 ms vs ~8 us, about 1000x; varies)
```

---

## 🔍 Why This Works (3 lines max)
The first call for each `n` computes and stores the result; later calls are dict lookups. `fib(25)` drops from ~250k calls to 26 computations. `cache_info()` shows hits/misses.
हिंदी: हर `n` एक बार compute होता है और बाद में dict से मिलता है, इसलिए 2^n काम घटकर n रह जाता है।

---

## ⚡ Alternative Solution
```python
# Manual memoization with a dict, and a bounded LRU cache
from functools import lru_cache  # bounded cache


def fib(n: int, memo: dict[int, int] | None = None) -> int:
    memo = {} if memo is None else memo  # fresh dict per top-level call
    if n < 2:
        return n  # base cases
    if n not in memo:  # compute only if missing
        memo[n] = fib(n - 1, memo) + fib(n - 2, memo)  # store result
    return memo[n]  # return cached value


print(fib(50))  # Expected: 12586269025


@lru_cache(maxsize=2)  # keep only the 2 most recently used results
def square(x: int) -> int:
    return x * x  # pretend this is expensive


square(1); square(2); square(3)  # 3 misses; entry for 1 is evicted
square(2)  # hit (2 still cached)
square(1)  # miss again (was evicted)
print(square.cache_info())  # Expected: CacheInfo(hits=1, misses=4, maxsize=2, currsize=2)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: unhashable arguments (list) cannot be cache keys
from functools import lru_cache  # cache decorator


@lru_cache(maxsize=None)
def total(nums):
    return sum(nums)  # works only for hashable nums


try:
    total([1, 2, 3])  # list is unhashable
except TypeError as e:
    print(e)  # Output: unhashable type: 'list'

print(total((1, 2, 3)))  # Output: 6   ✅ pass a tuple instead
# Also: methods cached with lru_cache keep `self` alive (memory leak) - and impure functions return stale data.
```

---

## 🎯 Interview Tip (1 line)
Say: "lru_cache works for pure functions with hashable args; set maxsize to bound memory and use cache_info()/cache_clear() to inspect and reset."

---

## 🔗 Related Questions
→ Q083 (memoize decorator) | Q143 (complete memoize) | Q215 (memoize async) | Q251 (functools)
