---

# 116. Functional Programming in Python — Complete Guide
# हिंदी में: Functional Programming — पूरी Guide

---

## 🔵 Simple Definition (English)
Functional programming (FP) treats functions as first-class values and avoids changing state. Python supports FP via: `map()`, `filter()`, `reduce()`, lambda functions, closures, and the `functools` module. Pure functions (same input → same output, no side effects) are easier to test and reason about. Python is multi-paradigm — use FP when it makes code cleaner.

## 🔵 सरल परिभाषा (Hindi)
Functional programming functions को first-class values treat करता है, state changing avoid करता है। Python FP support: `map()`, `filter()`, `reduce()`, lambda, closures, `functools`। Pure functions (same input → same output, no side effects) test करने में easy। Python multi-paradigm है — जब cleaner code हो, FP use करो।

---

## 💻 Code Example — map, filter, reduce
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# ─── map() — transform each element ─────────────────────────────
# map(function, iterable) → lazy iterator
squares = list(map(lambda x: x**2, numbers))
# [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# Python equivalent (list comprehension — more readable):
squares = [x**2 for x in numbers]

# map with multiple iterables:
a = [1, 2, 3]
b = [10, 20, 30]
sums = list(map(lambda x, y: x + y, a, b))   # [11, 22, 33]

# ─── filter() — keep elements matching condition ──────────────────
evens = list(filter(lambda x: x % 2 == 0, numbers))
# [2, 4, 6, 8, 10]

# Python equivalent:
evens = [x for x in numbers if x % 2 == 0]

# filter(None, iterable) — remove falsy values:
data = [0, 1, None, "", "hello", False, True, 42]
truthy = list(filter(None, data))   # [1, 'hello', True, 42]

# ─── reduce() — fold to single value ─────────────────────────────
total = reduce(lambda acc, x: acc + x, numbers)   # 55
product = reduce(lambda acc, x: acc * x, [1,2,3,4,5])   # 120

# With initial value:
result = reduce(lambda acc, x: acc + x, numbers, 100)   # 155 (starts at 100)

# Python equivalent:
total = sum(numbers)    # use built-ins when available!

# ─── When to use vs list comprehension ───────────────────────────
# USE map/filter when: passing existing function (not lambda)
import math
sqrt_all = list(map(math.sqrt, numbers))    # cleaner than comprehension

# USE comprehension when: using lambda or simple expression
sqrt_all = [math.sqrt(x) for x in numbers]  # same thing, more readable

# PREFER comprehensions in Python — they're more Pythonic:
# list(map(lambda x: x**2, nums)) vs [x**2 for x in nums]
# Comprehension wins on readability
```

## 💻 Code Example — functools, partial, lru_cache
```python
from functools import partial, lru_cache, reduce, wraps
from typing import Callable, Any

# ─── lru_cache — memoize expensive functions ──────────────────────
@lru_cache(maxsize=128)   # cache last 128 unique calls
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(50))   # instant — results cached!
print(fibonacci.cache_info())   # CacheInfo(hits=48, misses=51, maxsize=128, currsize=51)
fibonacci.cache_clear()   # clear cache

# @cache (Python 3.9+) — unlimited cache, slightly faster:
from functools import cache

@cache
def count_ways(n: int) -> int:
    if n <= 1: return n
    return count_ways(n-1) + count_ways(n-2)

# ─── partial — pre-fill function arguments ───────────────────────
def power(base: float, exponent: float) -> float:
    return base ** exponent

square = partial(power, exponent=2)   # pre-fill exponent
cube = partial(power, exponent=3)

print(square(4))   # 16.0
print(cube(3))     # 27.0

# Real use — configure with environment-specific settings:
import logging

debug_log = partial(logging.log, logging.DEBUG)
error_log = partial(logging.log, logging.ERROR)

debug_log("Debug message")   # same as logging.log(logging.DEBUG, "...")

# Partial with positional:
def greet(greeting: str, name: str) -> str:
    return f"{greeting}, {name}!"

say_hello = partial(greet, "Hello")   # pre-fills first arg
say_namaste = partial(greet, "Namaste")

print(say_hello("Priya"))     # "Hello, Priya!"
print(say_namaste("Raj"))     # "Namaste, Raj!"

# ─── Composing functions ──────────────────────────────────────────
def compose(*functions):
    """Create a new function that applies functions right to left."""
    def composed(x):
        result = x
        for f in reversed(functions):
            result = f(result)
        return result
    return composed

double = lambda x: x * 2
increment = lambda x: x + 1
square = lambda x: x ** 2

# Apply right to left: square first, then increment, then double:
transform = compose(double, increment, square)
print(transform(3))   # double(increment(square(3))) = double(increment(9)) = double(10) = 20

# ─── Pure functions (no side effects) ────────────────────────────
# Impure — modifies external state:
total = 0
def bad_add(x):
    global total        # side effect!
    total += x
    return total

# Pure — same input always same output:
def good_add(current_total: int, x: int) -> int:
    return current_total + x   # no side effects

# Pure functions are: testable, cacheable, parallelizable

# ─── Higher-order functions in FastAPI ────────────────────────────
from fastapi import FastAPI, Depends

def require_role(role: str) -> Callable:
    """Higher-order function that returns a dependency."""
    async def check_role(user=Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(403, f"Requires role: {role}")
        return user
    return check_role

# Usage:
@app.delete("/admin/users/{id}")
async def delete_user(
    id: int,
    user=Depends(require_role("admin"))   # requires admin role
):
    await user_service.delete(id)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python map/filter:
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x**2, numbers))
evens = list(filter(lambda x: x%2==0, numbers))

# Preferred: list comprehensions
squares = [x**2 for x in numbers]
evens = [x for x in numbers if x%2==0]

# functools.partial:
from functools import partial
add5 = partial(lambda x, y: x+y, 5)
```

```javascript
// JavaScript (built into Array.prototype):
const numbers = [1, 2, 3, 4, 5];
const squares = numbers.map(x => x**2);
const evens = numbers.filter(x => x%2===0);
const total = numbers.reduce((acc, x) => acc+x, 0);

// Partial (manual or lodash):
const add = (x, y) => x + y;
const add5 = (y) => add(5, y);   // or: _.partial(add, 5);
```

Key difference: JS array methods (`map`, `filter`, `reduce`) are built-in and return arrays. Python's `map`/`filter` are lazy iterators — need `list()` to materialize. Python generally prefers list comprehensions over `map`/`filter`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not realizing map/filter are lazy
```python
# Wrong — mapped result used once, then exhausted:
result = map(lambda x: x**2, [1, 2, 3])
first_pass = list(result)     # [1, 4, 9] ✓
second_pass = list(result)    # [] — EMPTY! iterator exhausted

# Correct — materialize immediately if needed multiple times:
result = list(map(lambda x: x**2, [1, 2, 3]))   # always a list
```

❌ Mistake 2: Using lru_cache with mutable arguments
```python
# Wrong — list is not hashable, can't be cached:
@lru_cache(maxsize=128)
def process(items: list) -> int:   # TypeError: unhashable type 'list'
    return sum(items)

# Correct — use tuple (immutable, hashable):
@lru_cache(maxsize=128)
def process(items: tuple) -> int:
    return sum(items)

process((1, 2, 3))   # works!
```

---

## 🧠 Tricky Interview Question

**Q**: What does `@lru_cache(maxsize=128)` actually cache and what happens at maxsize?

**Answer**: `lru_cache` caches the **return value** mapped from the **function arguments** (as a dict key). When `maxsize=128` is reached, it evicts the **Least Recently Used** entry (the one not accessed for the longest time). `maxsize=None` (or `@cache`): unlimited, never evicts. The "LRU" part is the eviction policy — recently accessed items stay in cache. Cache key: all function arguments must be hashable. `cache_info()` shows hits (returned from cache), misses (computed fresh), maxsize, and currsize.

---

## ⚫ Interview Questions + Answers

Q1: When should you use `map()`/`filter()` vs list comprehensions?
A1: In Python, list comprehensions are almost always preferred for readability: `[x**2 for x in nums]` vs `list(map(lambda x: x**2, nums))`. Use `map()` when: passing an already-defined function (not lambda): `list(map(str, numbers))` cleaner than `[str(n) for n in numbers]`. Use `filter(None, iterable)` to remove falsy values — concise. Use `reduce()` for custom fold operations not covered by `sum/max/min/all/any`. General rule: if you'd write a lambda, use comprehension instead.

Q2: What is a pure function and why does it matter?
A2: A pure function always returns the same output for the same input AND has no side effects (doesn't modify external state, doesn't print, doesn't write to DB). Benefits: (1) **Testable** — `assert pure_fn(5) == 10` works deterministically. (2) **Cacheable** — `@lru_cache` only works reliably with pure functions. (3) **Parallelizable** — no shared state = safe to run concurrently. (4) **Debuggable** — can test in isolation, no setup needed. FastAPI route handlers aren't pure (they have side effects), but business logic functions should be pure when possible.

Q3: What is `functools.wraps` and when must you use it?
A3: When writing a decorator, the wrapper function replaces the original — `func.__name__`, `func.__doc__`, etc. change to the wrapper's name. `@functools.wraps(func)` copies all the metadata from `func` to the wrapper. Without it: `help(my_decorated_func)` shows wrapper's docstring; `my_func.__name__` returns `"wrapper"`. Required when: writing decorators for FastAPI/Flask route handlers (frameworks use `__name__` for routing), logging, debugging. Rule: always use `@wraps(func)` inside every decorator.

Q4: What is currying vs partial application?
A4: **Partial application**: fix some arguments, return function expecting the rest. `partial(add, 5)` → function expecting one more argument. `partial(add, 5)(3)` = `add(5, 3)` = 8. **Currying**: transform a function taking N args into a chain of functions each taking 1 arg. `curry(add)(5)(3)` = 8. Python doesn't have built-in currying — use `partial` for partial application. `functools.partial` is the standard tool. Difference: partial application can fix multiple args at once; currying is always one-at-a-time.

Q5: What is `reduce()` and when is it appropriate?
A5: `reduce(function, iterable, initial)` applies function cumulatively: `reduce(lambda acc, x: acc + x, [1,2,3,4], 0)` = ((0+1)+2)+3)+4) = 10. Use it for: custom fold operations not covered by `sum/max/min/any/all`, flattening, building data structures, composing values. Avoid when: built-ins exist (`sum`, `max`, `min`, `all`, `any`, `str.join`). In Python 2 it was built-in; Python 3 moved to `functools` (less prominent). Comprehensions or explicit loops are often clearer. Use `reduce` only when the fold operation is non-trivial.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| First-class function | Function can be stored/passed | Function store/pass हो सकता है |
| Pure function | Same input → same output, no side effects | Same input → same output |
| Higher-order function | Takes/returns functions | Functions लेता/देता है |
| map() | Transform each element | हर element transform |
| filter() | Keep matching elements | Matching elements रखो |
| reduce() | Fold to single value | Single value में fold |
| partial | Pre-fill some arguments | कुछ arguments pre-fill |
| lru_cache | Memoize function results | Function results cache करो |

---

## ⚡ 3-Line Summary
English: Python supports functional programming — use `map(func, iterable)` to transform, `filter(pred, iterable)` to select, but prefer list comprehensions for readability. `@lru_cache` memoizes pure function results (arguments must be hashable), `functools.partial` pre-fills arguments. Write pure functions (no side effects) for testable, cacheable, reusable code.
Hindi: Python FP support करता है। `map/filter` transform/select के लिए, लेकिन comprehensions ज्यादा readable। `@lru_cache` = pure function memoization। `partial` = arguments pre-fill। Pure functions = testable + cacheable।

---

## ➡️ Next Topic
**117. map/filter/reduce Deep Dive** — edge cases, performance. **124. Closures** — captured variables, nonlocal. **127. functools Module** — total_ordering, cached_property.
