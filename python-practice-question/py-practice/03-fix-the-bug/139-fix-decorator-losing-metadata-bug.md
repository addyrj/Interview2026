---

# Q139. Fix Decorator Losing Metadata Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
After decorating `add` with `@log_buggy`, `add.__name__` is `"wrapper"`, the docstring is gone and `help()`/introspection/route registries break. Find and fix the bug.

```python
# BUGGY CODE:
def log_buggy(fn):
    def wrapper(*args, **kwargs):      # ❌ wrapper has its own name/doc/signature
        return fn(*args, **kwargs)     # call the original function
    return wrapper                     # callers now get `wrapper`, not `fn`

@log_buggy
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

---

## 💡 Quick Concept (2 lines only)
A decorator replaces the function with `wrapper`, so `__name__`, `__doc__`, annotations and the signature belong to `wrapper`. `@functools.wraps(fn)` copies them back and adds `__wrapped__`.
हिंदी: decorator असली function की जगह `wrapper` रख देता है — `@functools.wraps(fn)` से metadata वापस मिलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools, inspect                       # wraps + signature inspection

def log_buggy(fn):
    def wrapper(*args, **kwargs):               # wrapper has its own identity
        """wrapper doc"""
        return fn(*args, **kwargs)              # delegate
    return wrapper                              # returns the wrapper

@log_buggy
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b                                # real work

print(add.__name__, add.__doc__)                # Expected: wrapper wrapper doc
print(inspect.signature(add))                   # Expected: (*args, **kwargs)

def log(fn):
    @functools.wraps(fn)                        # Step 1: copy __name__, __doc__, __module__, annotations, __dict__
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)              # delegate to the original
    return wrapper                              # return the wrapper

@log
def add2(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b                                # real work

# ============================================
# TEST CASES
# ============================================
print(add2.__name__, add2.__doc__)              # Expected: add2 Add two numbers.
print(inspect.signature(add2))                  # Expected: (a: int, b: int) -> int
print(add2.__wrapped__(1, 2), add2(1, 2))       # Expected: 3 3   (__wrapped__ = original function)
```

---

## 🔍 Why This Works (3 lines max)
`@functools.wraps(fn)` runs `update_wrapper`, copying `__module__`, `__name__`, `__qualname__`, `__doc__`, `__annotations__` and updating `__dict__`, and sets `__wrapped__`. `inspect.signature` follows `__wrapped__`, so tools like FastAPI/pytest see the real parameters. Without it, decorated functions collide in registries (all named `wrapper`).
हिंदी: `wraps` name, doc, signature copy करता है और `__wrapped__` सेट करता है।

---

## ⚡ Alternative Solution
```python
import functools                                   # wraps

# Alternative 1: copy metadata manually (what wraps automates)
def log3(fn):
    def wrapper(*a, **k):
        return fn(*a, **k)                         # delegate
    wrapper.__name__ = fn.__name__                 # copy name
    wrapper.__doc__ = fn.__doc__                   # copy docstring
    return wrapper

@log3
def f() -> None:
    "doc f"

print(f.__name__, f.__doc__)                       # Output: f doc f

# Alternative 2: decorator WITH arguments — wraps goes on the innermost wrapper
def repeat(n: int):
    def deco(fn):
        @functools.wraps(fn)                       # apply to the innermost wrapper
        def wrapper(*a, **k):
            for _ in range(n - 1):                 # first n-1 calls, result ignored
                fn(*a, **k)
            return fn(*a, **k)                     # last call's result returned
        return wrapper
    return deco

@repeat(2)
def hi() -> str:
    "say hi"
    return "hi"

print(hi.__name__, hi.__doc__, hi())               # Output: hi say hi hi
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: registry keyed by __name__ — undecorated wrappers all collide
registry: dict[str, object] = {}               # name -> function

def route(fn):
    registry[fn.__name__] = fn                 # uses the function's name as key
    return fn

def auth_buggy(fn):
    def wrapper(*a, **k):                      # no functools.wraps
        return fn(*a, **k)
    return wrapper

@route
@auth_buggy
def a() -> None: ...                           # registered as "wrapper"

@route
@auth_buggy
def b() -> None: ...                           # overwrites "wrapper"

print(list(registry))                          # Output: ['wrapper']   (two routes became one!)

# ✅ Correct: always put @functools.wraps(fn) on the wrapper
```

---

## 🎯 Interview Tip (1 line)
Say: "Every decorator I write uses `@functools.wraps(fn)` so name, docstring and signature survive — frameworks like FastAPI and pytest depend on them."

---

## 🔗 Related Questions
→ Q038 (decorator stacking order) | Q039 (decorator without functools.wraps) | Q166 (explain decorators with arguments) | Q255 (decorator tricks) | Q296 (decorators real use case)
