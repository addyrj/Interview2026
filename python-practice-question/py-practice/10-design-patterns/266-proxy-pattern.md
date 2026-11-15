---

# Q266. Proxy Pattern
# Category: DESIGN PATTERNS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement the Proxy pattern: a stand-in object that controls access to a real one. Build (1) a lazy-loading proxy for an expensive object, (2) a protection proxy that checks permissions, and (3) a generic logging proxy using `__getattr__`.

```python
img = LazyImage("big.png")   # nothing loaded yet
img.show()                   # loads on first use
```

---

## 💡 Quick Concept (2 lines only)
A proxy has the same interface as the real object and sits in front of it to add lazy creation, access control, caching or logging. Python's `__getattr__` makes generic forwarding proxies short.
हिंदी: Proxy असली object के सामने खड़ा रहता है — lazy loading, permission check या logging वह करता है और बाकी काम असली object को देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any                           # generic attribute values

class RealImage:
    def __init__(self, path: str) -> None:
        self.path = path                         # file path
        print(f"loading {path} (expensive)")     # simulate costly load
    def show(self) -> str:
        return f"showing {self.path}"            # real work

# --- 1. virtual (lazy) proxy ---
class LazyImage:
    def __init__(self, path: str) -> None:
        self._path = path                        # remember what to load
        self._real: RealImage | None = None      # not created yet
    def show(self) -> str:
        if self._real is None:                   # first use?
            self._real = RealImage(self._path)   # create now (once)
        return self._real.show()                 # delegate

# --- 2. protection proxy ---
class ProtectedImage:
    def __init__(self, real: RealImage, role: str) -> None:
        self._real = real                        # wrapped object
        self._role = role                        # caller's role
    def show(self) -> str:
        if self._role != "admin":                # access control
            raise PermissionError("admins only") # block
        return self._real.show()                 # allow

# --- 3. generic logging proxy ---
class LoggingProxy:
    def __init__(self, target: object) -> None:
        self._target = target                    # wrapped object
    def __getattr__(self, name: str) -> Any:     # called only for attributes not found on the proxy
        attr = getattr(self._target, name)       # fetch from the real object
        if callable(attr):                       # wrap methods only
            def logged(*a: Any, **k: Any) -> Any:
                print(f"call {name}{a}")         # log before delegating
                return attr(*a, **k)             # delegate
            return logged
        return attr                              # plain attributes pass through

# ============================================
# TEST CASES
# ============================================
img = LazyImage("big.png")                       # nothing printed: not loaded
print("created proxy")                           # proves laziness
print(img.show())                                # loads now
print(img.show())                                # no second load

try:
    ProtectedImage(RealImage("a.png"), "guest").show()  # guest denied
except PermissionError as e:
    print("denied:", e)

p = LoggingProxy([3, 1, 2])                      # proxy a list
p.sort()                                         # logged + forwarded
print(p.__len__() if False else p._target)       # list was really sorted

# Output:
# created proxy
# loading big.png (expensive)
# showing big.png
# showing big.png
# loading a.png (expensive)
# denied: admins only
# call sort()
# [1, 2, 3]
```

---

## 🔍 Why This Works (3 lines max)
The proxy exposes the same methods as the real object, so callers can't tell the difference. The lazy proxy defers the expensive constructor until first use; the protection proxy checks a rule before delegating; `__getattr__` catches every missing attribute for generic forwarding.
हिंदी: `__getattr__` सिर्फ तब चलता है जब attribute proxy पर नहीं मिलता — इसलिए generic forwarding आसान है।

---

## ⚡ Alternative Solution
```python
# Caching proxy with functools.lru_cache (Pythonic, no class needed)
from functools import lru_cache                  # built-in cache

calls = 0                                        # count real calls

def slow_square(n: int) -> int:
    global calls
    calls += 1                                   # real work happened
    return n * n

cached_square = lru_cache(maxsize=None)(slow_square)  # a caching proxy around the function

print(cached_square(4), cached_square(4), cached_square(5))
print("real calls:", calls)                      # 4 was computed once

# Output:
# 16 16 25
# real calls: 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: __getattr__ on the proxy recurses forever if _target isn't set yet
class Bad:
    def __getattr__(self, name):
        return getattr(self._target, name)       # _target missing -> __getattr__('_target') -> ...

try:
    Bad().anything
except RecursionError:
    print("RecursionError")

# ✅ Correct: set self._target in __init__ (or use object.__getattribute__ / guard the name)

# Output:
# RecursionError
```

---

## 🎯 Interview Tip (1 line)
Say: "Proxy = same interface, controls access: virtual (lazy), protection, caching, remote; vs Decorator, which adds behaviour — and vs Adapter, which changes the interface."

---

## 🔗 Related Questions
→ Q178 (__getattr__ vs __getattribute__) | Q191 (lazy loader) | Q265 (decorator pattern) | Q278 (lru_cache)
