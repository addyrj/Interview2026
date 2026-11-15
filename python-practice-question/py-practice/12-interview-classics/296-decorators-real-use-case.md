---

# Q296. Decorators — real use case
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain decorators with a REAL use case. Write a `retry(times)` decorator that re-runs a flaky function, keeps its name/docstring, and works with arguments.

```python
# NOT RUN (question stub)
@retry(times=3)
def flaky_call() -> str:
    ...
```

---

## 💡 Quick Concept (2 lines only)
A decorator is a function that takes a function and returns a replacement (`@d` above `f` means `f = d(f)`). Use it for cross-cutting concerns: retry, logging, auth, caching, timing.
हिंदी: Decorator = function को wrap करने वाला function; retry, logging, auth जैसे common काम एक जगह।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import functools                                   # for wraps
from typing import Callable, Any                   # type hints


def retry(times: int) -> Callable:                 # decorator FACTORY: takes config
    def decorator(fn: Callable) -> Callable:       # real decorator: takes the function
        @functools.wraps(fn)                       # copy __name__, __doc__ onto wrapper
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # accept any arguments
            last_exc: Exception | None = None      # remember the last failure
            for attempt in range(1, times + 1):    # try up to `times` times
                try:
                    return fn(*args, **kwargs)     # success: return immediately
                except Exception as exc:           # failure: store and retry
                    last_exc = exc                 # keep the exception
                    print(f"attempt {attempt} failed: {exc}")  # show progress
            raise last_exc                         # all attempts failed: re-raise
        return wrapper                             # replace fn with wrapper
    return decorator                               # @retry(3) returns this decorator


# ============================================
# TEST CASES
# ============================================

calls = {"n": 0}                                   # counter to simulate flakiness

@retry(times=3)
def flaky_call(name: str) -> str:
    """Fails twice, then succeeds."""
    calls["n"] += 1                                # count calls
    if calls["n"] < 3:                             # first two calls fail
        raise ConnectionError(f"boom {calls['n']}")
    return f"hello {name}"                         # third call works

print(flaky_call("ada"))                           # retried transparently
print(flaky_call.__name__, "|", flaky_call.__doc__)  # metadata preserved by wraps

# Expected output:
# attempt 1 failed: boom 1
# attempt 2 failed: boom 2
# hello ada
# flaky_call | Fails twice, then succeeds.
```

---

## 🔍 Why This Works (3 lines max)
`@retry(times=3)` first CALLS `retry(3)`, which returns `decorator`; that is then applied to the function. The wrapper closes over `fn` and `times`, and `functools.wraps` keeps introspection (`__name__`, `__doc__`) intact.
हिंदी: `@retry(3)` पहले retry(3) call होता है, फिर उसका result function पर लगता है; `wraps` metadata बचाता है।

---

## ⚡ Alternative Solution
```python
import functools                                   # for cache and wraps

# Built-in decorator: memoize a pure function with zero code
@functools.cache                                   # Python 3.9+, unbounded cache
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)  # naive recursion, now O(n)

print(fib(50))                                     # instant instead of minutes
print(fib.cache_info())                            # hits/misses statistics


# Class-based decorator that counts calls
class CountCalls:
    def __init__(self, fn):
        functools.update_wrapper(self, fn)         # copy metadata onto the instance
        self.fn = fn                               # keep the original function
        self.count = 0                             # call counter

    def __call__(self, *args, **kwargs):
        self.count += 1                            # increment on every call
        return self.fn(*args, **kwargs)            # delegate

@CountCalls
def hi() -> str:
    return "hi"

hi(); hi()                                         # call twice
print(hi.count)

# Expected output:
# 12586269025
# CacheInfo(hits=48, misses=51, maxsize=None, currsize=51)
# 2
```

---

## ⚠️ Common Mistake
```python
import functools

# ❌ Wrong: no functools.wraps, metadata is lost
def bad(fn):
    def wrapper(*a, **k):
        return fn(*a, **k)
    return wrapper

@bad
def greet():
    """Say hi."""

print(greet.__name__, greet.__doc__)    # wrapper None

# ✅ Correct: add @functools.wraps(fn)
def good(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        return fn(*a, **k)
    return wrapper

@good
def greet2():
    """Say hi."""

print(greet2.__name__, greet2.__doc__)  # greet2 Say hi.

# Expected output:
# wrapper None
# greet2 Say hi.
```

---

## 🎯 Interview Tip (1 line)
Say: "A decorator is a closure returning a wrapper; I always use `functools.wraps`, and with arguments I need three levels: factory, decorator, wrapper."

---

## 🔗 Related Questions
→ Q038 (decorator stacking) | Q039 (without wraps) | Q083 (memoize) | Q089 (retry with backoff) | Q295 (*args/**kwargs)
