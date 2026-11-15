---

# Q300. __init__ vs __new__
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What is the difference between `__new__` and `__init__`? In what order are they called, and when would you override `__new__`? Implement a Singleton with it.

```python
# NOT RUN (question stub)
a = Config()
b = Config()
print(a is b)     # want: True
```

---

## 💡 Quick Concept (2 lines only)
`__new__(cls, ...)` CREATES the object (it is a static method returning the instance); `__init__(self, ...)` then INITIALISES it. Override `__new__` for singletons, caching, or subclassing immutable types (`int`, `str`, `tuple`).
हिंदी: `__new__` object बनाता है, `__init__` उसे set up करता है; singleton/immutable types में `__new__` चाहिए।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

class Config:
    _instance: "Config | None" = None               # cache for the one instance

    def __new__(cls, *args, **kwargs):
        print("__new__ called")                     # step 1: creation
        if cls._instance is None:                   # first time only
            cls._instance = super().__new__(cls)    # really allocate the object
        return cls._instance                        # always hand back the same object

    def __init__(self, name: str = "default") -> None:
        print("__init__ called")                    # step 2: initialisation
        self.name = name                            # NOTE: runs on EVERY Config(...) call


# ============================================
# TEST CASES
# ============================================

a = Config("first")                                 # __new__ then __init__
b = Config("second")                                # __new__ again, __init__ again
print(a is b)                                       # same object
print(a.name)                                       # __init__ overwrote the name

# Expected output:
# __new__ called
# __init__ called
# __new__ called
# __init__ called
# True
# second
```

---

## 🔍 Why This Works (3 lines max)
`Config(...)` runs `type.__call__`, which calls `__new__` and, only if it returns an instance of `cls`, then calls `__init__` on it. Returning the cached object makes both variables point to one instance, but `__init__` still re-runs each time.
हिंदी: `Config()` पहले `__new__` चलाता है, फिर (अगर cls का instance मिला) `__init__`; singleton में `__init__` हर बार चलता है।

---

## ⚡ Alternative Solution
```python
# Real reason to use __new__: subclass an IMMUTABLE type (value is fixed at creation)
class Upper(str):
    def __new__(cls, value: str):
        return super().__new__(cls, value.upper())  # transform BEFORE the str is created

u = Upper("hello")
print(u, type(u).__name__)

# If __new__ returns a different type, __init__ is skipped
class Weird:
    def __new__(cls):
        return 42                                   # not an instance of Weird
    def __init__(self):
        print("never printed")                      # skipped

print(Weird())

# Simpler singleton: just use a module-level instance (modules are imported once)
# or functools.cache on a factory function.
import functools

@functools.cache                                    # same args -> same cached result
def get_config() -> dict:
    return {"debug": True}                          # created once

print(get_config() is get_config())

# Expected output:
# HELLO Upper
# 42
# True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: trying to change an immutable value in __init__ (too late, str already created)
class Bad(str):
    def __init__(self, value: str) -> None:
        super().__init__()
        self = value.upper()                        # only rebinds a local name, no effect

print(Bad("hello"))                                 # hello (not HELLO)

# ❌ Also wrong: forgetting to return the instance from __new__
class Broken:
    def __new__(cls):
        super().__new__(cls)                        # missing `return`

print(Broken())                                     # None, and __init__ is never called

# ✅ Correct: use __new__ for creation-time work and always `return super().__new__(cls)`

# Expected output:
# hello
# None
```

---

## 🎯 Interview Tip (1 line)
Say: "`__new__` allocates and returns the instance, `__init__` configures it; I override `__new__` only for singletons, caching or immutable subclasses."

---

## 🔗 Related Questions
→ Q030 (__init__ vs __new__ call order output) | Q031 (inheritance and super) | Q306 (dunder methods) | Q292 (mutable vs immutable)
