---

# Q251. functools — 5 Use Cases
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 5 `functools` tools: `lru_cache`/`cache`, `partial`, `reduce`, `wraps`, and `singledispatch` (plus `cached_property`).

---

## 💡 Quick Concept (2 lines only)
`functools` has higher-order helpers: cache results, pre-fill arguments, fold a sequence, keep decorator metadata and dispatch by argument type.
हिंदी: functools = functions को सजाने/cache करने के tools — memoize, partial, reduce, wraps।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from functools import cache, partial, reduce, singledispatch, wraps, cached_property  # imports

calls = 0                                             # count real computations

@cache                                                # Use case 1: memoize (unbounded)
def fib(n: int) -> int:                               # slow recursive fib becomes fast
    global calls                                      # modify module counter
    calls += 1                                        # count a real call
    return n if n < 2 else fib(n - 1) + fib(n - 2)    # classic recursion
print(fib(30), calls)                                 # Expected: 832040 31  (only 31 computations)
print(fib.cache_info())                               # Expected: CacheInfo(hits=28, misses=31, maxsize=None, currsize=31)

power = partial(pow, exp=2)                           # Use case 2: pre-fill keyword arg
print(power(5))                                       # Expected: 25

print(reduce(lambda a, b: a * b, [1, 2, 3, 4], 1))    # Use case 3: fold -> Expected: 24

def logged(fn):                                       # Use case 4: decorator that keeps metadata
    @wraps(fn)                                        # copy __name__ and __doc__ from fn
    def wrapper(*a, **k):                             # wrapper accepts anything
        return fn(*a, **k)                            # call original
    return wrapper                                    # return wrapper
@logged                                               # apply decorator
def hello() -> None:                                  # target function
    """Say hi."""                                     # docstring to preserve
print(hello.__name__, hello.__doc__)                  # Expected: hello Say hi.

@singledispatch                                       # Use case 5: dispatch on arg type
def show(x: object) -> str:                           # default implementation
    return f"object {x}"                              # fallback
@show.register                                        # register for int (from annotation)
def _(x: int) -> str:                                 # int version
    return f"int {x}"                                 # int output
@show.register                                        # register for list
def _(x: list) -> str:                                # list version
    return f"list of {len(x)}"                        # list output

# ============================================
# TEST CASES
# ============================================
print(show(5), "|", show([1, 2]), "|", show("s"))     # Expected: int 5 | list of 2 | object s

class Circle:                                         # cached_property demo
    def __init__(self, r: float) -> None:             # store radius
        self.r = r                                    # radius
    @cached_property                                  # computed once, then stored on instance
    def area(self) -> float:                          # expensive property
        print("computing")                            # shows it runs once
        return 3.14 * self.r ** 2                     # area formula
c = Circle(2)                                         # create
print(c.area, c.area)                                 # Expected: computing  then  12.56 12.56
```

---

## 🔍 Why This Works (3 lines max)
`cache` stores results by arguments, turning exponential `fib` into linear (31 calls for n=30). `wraps` copies metadata so debugging/introspection still sees the real function. `cached_property` stores the value in the instance `__dict__`.
हिंदी: `cache` पुराने results याद रखता है — `wraps` function का नाम/docstring बचाता है।

---

## ⚡ Alternative Solution
```python
# lru_cache with a size limit (evicts least-recently-used) and cache_clear()
from functools import lru_cache                       # bounded cache

@lru_cache(maxsize=2)                                 # keep only 2 results
def sq(n: int) -> int:                                # simple function
    print(f"calc {n}")                                # shows real computations
    return n * n                                      # square

sq(1); sq(2); sq(1); sq(3)                            # 1,2 computed; 1 hit; 3 evicts 2
sq(2)                                                 # 2 was evicted -> recomputed
# Expected prints: calc 1, calc 2, calc 3, calc 2
print(sq.cache_info().hits)                           # Expected: 1
sq.cache_clear()                                      # empty the cache
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: caching a function with unhashable args (list) -> TypeError
from functools import cache                           # import
@cache                                                # decorate
def total(xs: list[int]) -> int:                      # list arg is unhashable
    return sum(xs)                                    # sum
try:                                                  # call it
    total([1, 2])                                     # fails
except TypeError as e:                                # catch
    print(e)                                          # Expected: unhashable type: 'list'

# ✅ Correct: pass a tuple; also remember @cache on methods keeps `self` alive (memory leak)
print(total((1, 2)))                                  # Expected: 3
```

---

## 🎯 Interview Tip (1 line)
Say: "`lru_cache` needs hashable args and can leak memory on methods; I always use `@wraps` in decorators and `partial` instead of throwaway lambdas."

---

## 🔗 Related Questions
→ Q083 (memoize) | Q099 (LRU cache) | Q039 (decorator without wraps) | Q088 (partial application)
