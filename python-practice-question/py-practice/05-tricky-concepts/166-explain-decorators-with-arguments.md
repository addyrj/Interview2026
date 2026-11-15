---

# Q166. Explain Decorators (with Arguments)
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain how decorators work and how to write one that takes arguments (like `@repeat(3)`). Why are there three nested functions?

---

## 💡 Quick Concept (2 lines only)
`@deco` is just `fn = deco(fn)`. A decorator with arguments is a function that RETURNS a decorator: `@deco(3)` means `fn = deco(3)(fn)`.
हिंदी: `@deco(3)` का मतलब `deco(3)(fn)` है — पहले argument लेने वाला function, फिर decorator, फिर wrapper।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools                                   # Step 1: for wraps
from typing import Callable                        # Step 2: type hint

def repeat(times: int):                            # Level 1: takes the decorator's ARGUMENTS
    def decorator(fn: Callable):                   # Level 2: takes the FUNCTION being decorated
        @functools.wraps(fn)                       # keep name/docstring of fn
        def wrapper(*args, **kwargs):              # Level 3: replaces fn at call time
            result = None                          # holds the last result
            for _ in range(times):                 # call fn `times` times
                result = fn(*args, **kwargs)       # forward all arguments
            return result                          # return the last result
        return wrapper                             # decorator returns the wrapper
    return decorator                               # repeat() returns the decorator

# ============================================
# TEST CASES
# ============================================
@repeat(3)                                         # same as greet = repeat(3)(greet)
def greet(name: str) -> str:                       # function to decorate
    """Say hi."""                                  # docstring (kept by wraps)
    print(f"hi {name}")                            # side effect
    return name.upper()                            # return value

print(greet("ada"))                                # Expected: hi ada (x3) then ADA
print(greet.__name__, greet.__doc__)               # Expected: greet Say hi.

# Decorators stack bottom-up on definition, and run outer-first on call
def tag(name: str):                                # simple decorator factory
    def deco(fn):                                  # receives function
        @functools.wraps(fn)                       # keep metadata
        def w(*a, **k):                            # wrapper
            return f"<{name}>{fn(*a, **k)}</{name}>"   # wrap the result in a tag
        return w                                   # return wrapper
    return deco                                    # return decorator

@tag("b")                                          # applied second (outer)
@tag("i")                                          # applied first (inner)
def text() -> str:                                 # base function
    return "x"                                     # plain text
print(text())                                      # Expected: <b><i>x</i></b>
```

---

## 🔍 Why This Works (3 lines max)
Python evaluates `repeat(3)` first, getting `decorator`, then applies it to the function. The wrapper closes over `times` and `fn`. `functools.wraps` copies `__name__`, `__doc__` and sets `__wrapped__`, so introspection and debugging still work.
हिंदी: `repeat(3)` पहले चलता है, उसका returned decorator function पर लगता है, और wrapper `times` को closure में याद रखता है।

---

## ⚡ Alternative Solution
```python
# One decorator usable BOTH as @repeat and @repeat(3) (optional arguments)
import functools                                   # wraps

def repeat(_fn=None, *, times: int = 2):           # keyword-only config, optional function
    def decorator(fn):                             # the real decorator
        @functools.wraps(fn)                       # keep metadata
        def wrapper(*a, **k):                      # wrapper
            for _ in range(times - 1):             # first times-1 calls
                fn(*a, **k)                        # discard results
            return fn(*a, **k)                     # last call returns
        return wrapper                             # return wrapper
    return decorator(_fn) if callable(_fn) else decorator   # @repeat vs @repeat(...)

calls: list[int] = []                              # record calls

@repeat                                            # no parentheses -> default times=2
def a() -> None:                                   # function
    calls.append(1)                                # record
a()                                                # call it
print(len(calls))                                  # Expected: 2

@repeat(times=3)                                   # with arguments
def b() -> None:                                   # function
    calls.append(2)                                # record
b()                                                # call it
print(len(calls))                                  # Expected: 5

# Class-based decorator with arguments
class Timer:                                       # decorator as a class
    def __init__(self, label: str) -> None:        # receives arguments
        self.label = label                         # store them
    def __call__(self, fn):                        # receives the function
        @functools.wraps(fn)                       # keep metadata
        def w(*a, **k):                            # wrapper
            return f"{self.label}: {fn(*a, **k)}"  # prefix the result
        return w                                   # return wrapper

@Timer("result")                                   # instance is called with fn
def one() -> int:                                  # function
    return 1                                       # value
print(one())                                       # Expected: result: 1
```

---

## ⚠️ Common Mistake
```python
# (not run — fragments) ❌ Wrong: forgetting the parentheses on a decorator factory
@repeat            # fn is passed as `times`! repeat(greet) returns `decorator`, not a wrapper
def greet(): ...   # greet() later fails: decorator() missing argument 'fn' (TypeError)

# ❌ Wrong: no functools.wraps -> greet.__name__ == "wrapper"

# ✅ Correct: @repeat(3) with parentheses, and always use @functools.wraps(fn)
```

---

## 🎯 Interview Tip (1 line)
Say: "A decorator is a callable that takes a function and returns a function; with arguments you add one more level, and always use `functools.wraps`."

---

## 🔗 Related Questions
→ Q038 (decorator stacking) | Q039 (decorator without wraps) | Q083 (memoize decorator) | Q139 (decorator metadata bug) | Q255 (decorator tricks)
