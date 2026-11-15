---

# Q261. Singleton Pattern
# Category: DESIGN PATTERNS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a Singleton in Python: a class that always returns the same instance, no matter how many times it is created. Show the `__new__` way and a thread-safe version.

```python
# NOT RUN (question stub; Config is defined in the solution)
a = Config()
b = Config()
print(a is b)   # True
```

---

## 💡 Quick Concept (2 lines only)
Singleton = one instance per process. In Python override `__new__` to cache the instance; the simplest Pythonic singleton is just a module-level object (see Q275).
हिंदी: Singleton मतलब पूरे program में class का सिर्फ एक object — `__new__` में पहला instance cache कर लो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import threading                                 # lock for thread safety
from typing import Self                          # 3.11+ return type

class Config:
    _instance: "Config | None" = None            # class-level cache of the one instance
    _lock = threading.Lock()                     # protects instance creation

    def __new__(cls) -> Self:
        if cls._instance is None:                # fast path: no lock once created
            with cls._lock:                      # only one thread may create
                if cls._instance is None:        # double-checked: another thread may have won
                    cls._instance = super().__new__(cls)  # create the single object
                    cls._instance.settings = {}  # one-time initialisation
        return cls._instance                     # always return the same object

# ============================================
# TEST CASES
# ============================================
a = Config()                                     # first creation
b = Config()                                     # returns the cached one
a.settings["debug"] = True                       # mutate via a
print(a is b)                                    # same object?
print(b.settings)                                # change visible through b

results: list[int] = []                          # collect ids from threads
def make() -> None:
    results.append(id(Config()))                 # record identity
threads = [threading.Thread(target=make) for _ in range(20)]  # 20 racing threads
for t in threads: t.start()                      # start all
for t in threads: t.join()                       # wait for all
print(len(set(results)))                         # distinct instances

# Output:
# True
# {'debug': True}
# 1
```

---

## 🔍 Why This Works (3 lines max)
`__new__` runs before `__init__` and decides which object is returned; we return the cached one every time. Double-checked locking avoids taking the lock on every call while staying safe under threads. Put one-time setup in `__new__`, because `__init__` would re-run on every `Config()` call.
हिंदी: `__init__` हर बार चलता है, इसलिए one-time setup `__new__` में रखो।

---

## ⚡ Alternative Solution
```python
# Decorator-based and metaclass-based singletons
import functools                                 # wraps

def singleton(cls):
    instances: dict[type, object] = {}           # cache per decorated class
    @functools.wraps(cls)
    def get(*args, **kwargs):
        if cls not in instances:                 # first call creates
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]                    # later calls reuse
    return get

@singleton
class Db:
    def __init__(self) -> None:
        print("connecting once")                 # proves __init__ runs only once

class Meta(type):
    _inst: dict[type, object] = {}               # one instance per class using Meta
    def __call__(cls, *a, **k):
        if cls not in Meta._inst:                # intercept instance creation
            Meta._inst[cls] = super().__call__(*a, **k)
        return Meta._inst[cls]

class Cache(metaclass=Meta):
    pass

print(Db() is Db())                              # decorator version
print(Cache() is Cache())                        # metaclass version

# Output:
# connecting once
# True
# True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: setup in __init__ -> runs again every time and resets state
class Bad:
    _inst = None
    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst
    def __init__(self):
        self.items = []                          # ❌ reset on every Bad() call

x = Bad(); x.items.append(1)
y = Bad()                                        # __init__ runs again!
print(y.items)                                   # [] -> state lost

# ✅ Correct: initialise inside the "if _inst is None" branch of __new__

# Output:
# []
```

---

## 🎯 Interview Tip (1 line)
Say: "In Python a module is already a singleton; I use `__new__` or a metaclass only if I need a class, and add a lock for thread safety — and I mention singletons hurt testability."

---

## 🔗 Related Questions
→ Q030 (__init__ vs __new__) | Q168 (metaclasses) | Q275 (module pattern) | Q300 (__init__ vs __new__)
