---

# Q039. Decorator without functools.wraps output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What do `add.__name__` and `add.__doc__` print vs the `functools.wraps` version?

```python
import functools

def log(fn):
    def wrapper(*a, **k):
        """wrapper doc"""
        return fn(*a, **k)
    return wrapper

def log2(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        return fn(*a, **k)
    return wrapper

@log
def add(a, b):
    """Add two numbers."""
    return a + b

@log2
def mul(a, b):
    """Multiply two numbers."""
    return a * b

print(add.__name__, add.__doc__)
print(mul.__name__, mul.__doc__)
```

---

## 💡 Quick Concept (2 lines only)
A decorator replaces your function with the wrapper, so name, docstring and signature are the wrapper's. `functools.wraps` copies the metadata back and sets `__wrapped__`.
हिंदी: Decorator के बाद function असल में wrapper बन जाता है — `wraps` के बिना नाम और docstring खो जाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import functools                        # provides wraps
import inspect                          # to inspect signatures

def log(fn):
    def wrapper(*a, **k):               # NO wraps -> metadata is wrapper's
        """wrapper doc"""
        return fn(*a, **k)              # call the original
    return wrapper

def log2(fn):
    @functools.wraps(fn)                # copy __name__, __doc__, __wrapped__ etc.
    def wrapper(*a, **k):
        return fn(*a, **k)              # call the original
    return wrapper

@log
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@log2
def mul(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# ============================================
# TEST CASES
# ============================================
print(add.__name__, "|", add.__doc__)   # Expected: wrapper | wrapper doc
print(mul.__name__, "|", mul.__doc__)   # Expected: mul | Multiply two numbers.
print(hasattr(add, "__wrapped__"), mul.__wrapped__.__name__)  # Expected: False mul
print(inspect.signature(add), inspect.signature(mul))
# Expected: (*a, **k) (a: int, b: int) -> int
```

---

## 🔍 Why This Works (3 lines max)
`@log` means `add = log(add)`, so `add` IS `wrapper`. `functools.wraps` copies `__module__`, `__name__`, `__qualname__`, `__doc__`, `__dict__` (and annotations) and sets `__wrapped__`, which `inspect.signature` follows.
हिंदी: `wraps` metadata copy करता है और `__wrapped__` जोड़ता है जिससे `inspect` सही signature दिखाता है।

---

## ⚡ Alternative Solution
```python
# Reusable decorator template (always include wraps)
from functools import wraps
from typing import Callable, Any

def timed(fn: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(fn)                                   # preserve metadata
    def inner(*args: Any, **kwargs: Any) -> Any:
        return fn(*args, **kwargs)               # delegate
    return inner

@timed
def f() -> None:
    """doc"""

print(f.__name__, f.__doc__)                     # Expected: f doc
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no wraps -> help(), logging, pytest names, FastAPI/Flask route names
#    all show "wrapper" (Flask even raises on duplicate endpoint names)
# ✅ Correct: @functools.wraps(fn) on every inner wrapper
```

---

## 🎯 Interview Tip (1 line)
Say: "Always use `functools.wraps` in decorators so introspection, docs, debugging and frameworks that rely on `__name__`/signatures keep working."

---

## 🔗 Related Questions
→ Q038 (decorator stacking) | Q139 (fix decorator losing metadata) | Q166 (decorators with arguments) | Q251 (functools)
