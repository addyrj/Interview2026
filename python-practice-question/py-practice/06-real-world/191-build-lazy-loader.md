---

# Q191. Build Lazy Loader
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build two lazy utilities: (1) `LazyModule("json")` that imports the module only on first attribute access, and (2) a `lazy_property` decorator that computes a value once, on first access, then caches it on the instance.

```python
json = LazyModule("json")   # nothing imported yet
json.dumps({})              # imports now
```

---

## 💡 Quick Concept (2 lines only)
Lazy = delay expensive work until needed, then cache. `__getattr__` runs only for missing attributes, which is the perfect hook for deferred import.
हिंदी: Lazy मतलब काम तभी करो जब ज़रूरत हो, और result cache कर लो ताकि दोबारा न हो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import importlib  # dynamic imports
from typing import Any, Callable  # type hints

class LazyModule:
    def __init__(self, name: str) -> None:
        self._name = name  # module to import later
        self._mod: Any = None  # cache

    def __getattr__(self, attr: str) -> Any:  # only called when attribute not found normally
        if self._mod is None:
            print(f"[importing {self._name}]")  # show when import really happens
            self._mod = importlib.import_module(self._name)  # import on first use
        return getattr(self._mod, attr)  # delegate

def lazy_property(fn: Callable) -> property:
    name = "_lazy_" + fn.__name__  # cache attribute name
    @property
    def prop(self: Any) -> Any:
        if not hasattr(self, name):
            setattr(self, name, fn(self))  # compute once
        return getattr(self, name)  # cached
    return prop

class Report:
    @lazy_property
    def data(self) -> list[int]:
        print("[computing data]")  # visible side effect
        return [1, 2, 3]  # expensive work

# ============================================
# TEST CASES
# ============================================
json = LazyModule("json")  # nothing imported yet
print("created")  # Expected: created
print(json.dumps({"a": 1}))  # Expected: [importing json] then {"a": 1}
print(json.dumps([1]))  # Expected: [1]   (no second import message)
r = Report()  # no compute yet
print(r.data)  # Expected: [computing data] then [1, 2, 3]
print(r.data)  # Expected: [1, 2, 3]  (cached, no recompute)
```

---

## 🔍 Why This Works (3 lines max)
`__getattr__` is only called when normal lookup fails, so `_name` and `_mod` (set in `__init__`) never recurse. The first call imports and stores the module; later calls reuse it. `lazy_property` stores the result on the instance.
हिंदी: `__getattr__` तभी चलता है जब attribute नहीं मिलता; पहली बार import/compute करके cache कर लेते हैं।

---

## ⚡ Alternative Solution
```python
from functools import cached_property  # stdlib lazy attribute

class Report:
    @cached_property  # computes once, stores in instance __dict__
    def data(self) -> list[int]:
        print("[computing data]")  # runs once
        return [1, 2, 3]  # value cached

r = Report()  # no compute
print(r.data, r.data)  # Expected: [computing data] then [1, 2, 3] [1, 2, 3]
del r.data  # invalidate cache
print(r.data)  # Expected: [computing data] then [1, 2, 3]  (recomputed)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: plain @property recomputes on every access (not run)
# @property
# def data(self):
#     return expensive()      # called again and again

# ❌ Also: using __getattribute__ instead of __getattr__ -> infinite recursion on self._mod

# ✅ Correct: functools.cached_property (or __getattr__ for lazy modules)
```

---

## 🎯 Interview Tip (1 line)
Say: "cached_property for lazy attributes, deferred imports to cut startup time, and note it is not thread-safe by default."

---

## 🔗 Related Questions
→ Q162 (descriptors) | Q178 (__getattr__ vs __getattribute__) | Q036 (property setter) | Q278 (lru_cache)
