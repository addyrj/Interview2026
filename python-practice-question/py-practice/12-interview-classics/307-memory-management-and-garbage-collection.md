---

# Q307. Memory Management and Garbage Collection
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
How does CPython free memory? Show reference counting in action, show a reference cycle that refcounting alone cannot free, and show how the cyclic garbage collector and `weakref` help.

```python
# NOT RUN (question stub)
import sys
a = []
b = a
print(sys.getrefcount(a))   # what number, and why?
del b
```

---

## 💡 Quick Concept (2 lines only)
CPython frees an object the moment its reference count hits 0 (deterministic). A separate generational cyclic GC (`gc` module) finds unreachable reference cycles that refcounting can never free. `weakref` references do not increase the count.
हिंदी: Refcount 0 होते ही object तुरंत free; cycles के लिए अलग cyclic GC चलता है; weakref count नहीं बढ़ाता।

---

## ✅ Answer / Solution

```python
import gc                                               # cyclic garbage collector control
import sys                                              # getrefcount
import weakref                                          # references that do not keep objects alive


class Node:
    def __init__(self, name: str) -> None:               # simple node
        self.name = name                                 # label
        self.other: "Node | None" = None                 # slot to build a cycle

    def __del__(self) -> None:                           # finalizer: runs just before memory is freed
        print(f"freed {self.name}")                      # proof of destruction


# 1) Reference counting
a: list = []                                             # refcount: 1 (name a) + 1 (getrefcount arg)
print(sys.getrefcount(a))                                # 2
b = a                                                    # another name -> +1
print(sys.getrefcount(a))                                # 3
del b                                                    # name removed -> -1
print(sys.getrefcount(a))                                # 2 again

# 2) Immediate free when the count reaches 0
x = Node("x")                                            # one reference
del x                                                    # count -> 0 -> __del__ runs RIGHT NOW

# 3) Reference cycle: refcount never reaches 0
gc.disable()                                             # stop automatic collection for the demo
m, n = Node("m"), Node("n")                              # two nodes
m.other, n.other = n, m                                  # m -> n -> m cycle
del m, n                                                 # names gone, but each still referenced by the other
print("after del (cycle still alive)")                   # nothing was freed yet
print("collected:", gc.collect())                        # cyclic GC finds and frees them
gc.enable()                                              # restore default behaviour

# Expected output:
# 2
# 3
# 2
# freed x
# after del (cycle still alive)
# freed m
# freed n
# collected: 9   (count varies by version: includes the nodes AND their __dict__s etc.)
```

---

## 🔍 Why This Works (3 lines max)
`sys.getrefcount` shows one extra reference because passing `a` as an argument creates a temporary one. `x` hits zero on `del`, so `__del__` runs immediately; `m` and `n` keep each other at count 1, so only `gc.collect()` (which traces unreachable containers) frees them and returns the number of unreachable objects found (9 here, not 2, because instance dicts and other internals are counted; the exact number varies by version).
हिंदी: Cycle में दोनों objects एक-दूसरे को पकड़े रहते हैं इसलिए count 0 नहीं होता; `gc.collect()` unreachable cycle पहचान कर free करता है।

---

## ⚡ Alternative Solution
```python
import gc                                                # collector stats
import weakref                                           # weak references


class Cache:
    pass                                                 # plain objects can be weakly referenced


obj = Cache()                                            # strong reference
ref = weakref.ref(obj)                                   # weak reference: does NOT keep obj alive
print(ref() is obj)                                      # still alive -> returns the object
del obj                                                  # last strong reference gone -> freed
print(ref())                                             # dead -> None

# WeakValueDictionary: a cache that never leaks
wd: weakref.WeakValueDictionary[str, Cache] = weakref.WeakValueDictionary()  # values held weakly
item = Cache()                                           # strong ref
wd["k"] = item                                           # stored weakly
print(len(wd))                                           # 1
del item                                                 # object dies
print(len(wd))                                           # entry vanished automatically

print(len(gc.get_threshold()))                           # (gen0, gen1, gen2) thresholds -> 3 values
print(gc.isenabled())                                    # automatic GC is on by default

# Expected output:
# True
# None
# 1
# 0
# 3
# True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: relying on __del__ for cleanup (timing is not guaranteed, esp. in cycles / other interpreters)
# class Conn:
#     def __del__(self): self.close()    # may run late, or at interpreter shutdown

# ✅ Correct: deterministic cleanup with a context manager
class Conn:
    def __enter__(self) -> "Conn":
        return self                                      # acquire
    def __exit__(self, *exc) -> None:
        print("closed")                                  # release ALWAYS runs

with Conn():                                             # cleanup is guaranteed here
    pass

# ❌ Wrong: believing "del x" deletes the object (it only removes a NAME)
data = [1, 2, 3]
alias = data
del data                                                 # list still alive via alias
print(alias)

# Expected output:
# closed
# [1, 2, 3]
```

---

## 🎯 Interview Tip (1 line)
Say: "CPython = reference counting (immediate) + generational cyclic GC (gen0/1/2) for cycles; use context managers for resources, `weakref` for caches/back-pointers, and note free-threaded 3.13 builds change the details."

---

## 🔗 Related Questions
→ Q298 (the GIL) | Q305 (the with statement) | Q304 (pass by object reference) | Q292 (mutable vs immutable)
