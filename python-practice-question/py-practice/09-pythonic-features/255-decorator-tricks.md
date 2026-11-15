---

# Q255. Decorator Tricks
# Category: PYTHONIC + MODERN PYTHON FEATURES
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Show 3 decorator tricks: (1) a decorator that works both with and without arguments (`@log` and `@log(prefix=">>")`), (2) a decorator that keeps state (call counter), (3) a class-based decorator.

```python
# NOT RUN (question stub; log is defined in the solution)
@log
def add(a, b): return a + b

@log(prefix=">>")
def mul(a, b): return a * b
# both forms must work
```

---

## 💡 Quick Concept (2 lines only)
A decorator is just `f = decorator(f)`. To accept optional arguments, check whether the first argument is the function itself or a config value. Always use `functools.wraps` to keep `__name__` and `__doc__`.
हिंदी: Decorator = function को wrap करने वाला function — arguments के साथ/बिना दोनों चलाने के लिए पहले argument की type check करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools                                 # wraps
from collections.abc import Callable             # type hint
from typing import Any                           # type hint

# --- 1. optional-argument decorator ---
def log(func: Callable | None = None, *, prefix: str = "LOG"):
    def decorator(f: Callable) -> Callable:      # the real decorator
        @functools.wraps(f)                      # keep f's name and docstring
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            print(f"{prefix}: calling {f.__name__}{args}")  # log before the call
            return f(*args, **kwargs)            # call the original
        return wrapper
    if func is not None:                         # used as @log (no parentheses)
        return decorator(func)                   # func was passed directly
    return decorator                             # used as @log(prefix=...) -> return decorator

# --- 2. stateful decorator via function attribute ---
def count_calls(f: Callable) -> Callable:
    @functools.wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wrapper.calls += 1                       # increment the counter
        return f(*args, **kwargs)                # call the original
    wrapper.calls = 0                            # initial state stored on the wrapper
    return wrapper

# --- 3. class-based decorator ---
class CountClass:
    def __init__(self, f: Callable) -> None:
        functools.update_wrapper(self, f)        # copy __name__, __doc__ onto the instance
        self.f = f                               # store the function
        self.calls = 0                           # state
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1                          # count
        return self.f(*args, **kwargs)           # delegate

# ============================================
# TEST CASES
# ============================================
@log
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@log(prefix=">>")
def mul(a: int, b: int) -> int:
    return a * b

@count_calls
def hi() -> str:
    return "hi"

@CountClass
def bye() -> str:
    return "bye"

print(add(1, 2), add.__name__, add.__doc__)      # name/doc preserved by wraps
print(mul(3, 4))                                 # prefixed version
hi(); hi()                                       # two calls
print(hi.calls)                                  # counter value
bye(); bye(); bye()                              # three calls
print(bye.calls, bye.__name__)                   # class-based counter

# Output:
# LOG: calling add(1, 2)
# 3 add Add two numbers.
# >>: calling mul(3, 4)
# 12
# 2
# 3 bye
```

---

## 🔍 Why This Works (3 lines max)
`@log` passes the function as `func`; `@log(prefix=...)` first calls `log(prefix=...)` (func is `None`) and returns `decorator`, which Python then applies to the function. Functions are objects, so `wrapper.calls` stores state. A class with `__call__` is also a valid decorator.
हिंदी: `@log` में func सीधे मिलता है, `@log(prefix=..)` में पहले decorator वापस आता है — इसी फ़र्क से दोनों forms चलते हैं।

---

## ⚡ Alternative Solution
```python
# Decorating a method + registry decorator (returns the original function)
registry: dict[str, object] = {}                 # name -> function

def register(f):
    registry[f.__name__] = f                     # side effect: store it
    return f                                     # return unchanged (no wrapper)

@register
def a() -> int:
    return 1

@register
def b() -> int:
    return 2

print(sorted(registry))                          # names registered at import time
print(registry["b"]())                           # call via registry

# Output:
# ['a', 'b']
# 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting functools.wraps -> metadata lost
def deco(f):
    def wrapper(*a, **k):
        return f(*a, **k)
    return wrapper

@deco
def foo():
    """doc"""

print(foo.__name__, foo.__doc__)                 # wrapper None

# ✅ Correct: add @functools.wraps(f) above wrapper
import functools
def deco2(f):
    @functools.wraps(f)
    def wrapper(*a, **k):
        return f(*a, **k)
    return wrapper

@deco2
def foo2():
    """doc"""

print(foo2.__name__, foo2.__doc__)               # foo2 doc

# Output:
# wrapper None
# foo2 doc
```

---

## 🎯 Interview Tip (1 line)
Say: "Always `@functools.wraps`; for parameterised decorators it's three nested levels: factory -> decorator -> wrapper."

---

## 🔗 Related Questions
→ Q038 (decorator stacking order) | Q039 (decorator without wraps) | Q139 (fix decorator losing metadata) | Q166 (decorators with arguments) | Q296 (decorators real use case)
