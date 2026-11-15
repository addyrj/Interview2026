---

# Q170. Explain Weak References
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is a weak reference in Python? Show how it behaves when the object dies, and give a real use case (cache).

---

## 💡 Quick Concept (2 lines only)
A weak reference points to an object without keeping it alive; when the last strong reference goes away, the weakref returns `None`.
हिंदी: Weakref object को ज़िंदा नहीं रखता — strong reference खत्म होते ही object मर जाता है और weakref `None` देता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import weakref                               # Step 1: weakref module

class Node:                                  # Step 2: normal class (supports weakrefs)
    def __init__(self, name: str) -> None:
        self.name = name                     # some data

n = Node("a")                                # Step 3: strong reference
r = weakref.ref(n)                           # weak reference (doesn't count)

# ============================================
# TEST CASES
# ============================================
print(r() is n)                              # Expected: True   (calling r() gives the object)
del n                                        # drop the only strong ref -> refcount 0 -> freed
print(r())                                   # Expected: None   (object is gone)
```

---

## 🔍 Why This Works (3 lines max)
CPython frees an object the moment its strong reference count hits zero; weak references are not counted, so they just get cleared. Always call `r()` and check for `None` before use.
हिंदी: Refcount 0 होते ही CPython object हटा देता है; weakref गिनती में नहीं आता, इसलिए `None` मिलता है।

---

## ⚡ Alternative Solution
```python
import weakref, gc                           # modules

class Node:                                  # same class
    def __init__(self, name: str) -> None:
        self.name = name                     # data

# 1) WeakValueDictionary: auto-evicting cache
cache: weakref.WeakValueDictionary[str, Node] = weakref.WeakValueDictionary()  # values held weakly
obj = Node("big")                            # strong ref
cache["k"] = obj                             # store weakly
print(len(cache), cache["k"].name)           # Expected: 1 big
del obj                                      # last strong ref gone
print(len(cache))                            # Expected: 0   (entry vanished automatically)

# 2) Callback / finalize when object dies
def on_dead(ref: weakref.ref) -> None:       # callback receives the dead ref
    print("finalized")                       # runs at death
m = Node("m")                                # object
r2 = weakref.ref(m, on_dead)                 # attach callback
del m                                        # Expected print: finalized
f = weakref.finalize(Node("tmp"), print, "finalize called")  # Expected: finalize called (object dies immediately)
gc.collect()                                 # helps for reference cycles

# 3) Not everything can be weakly referenced
for bad in ([1], 5):                         # list and int
    try:
        weakref.ref(bad)                     # fails
    except TypeError as e:
        print("TypeError:", e)               # Expected: cannot create weak reference to 'list' object / 'int' object
```

---

## ⚠️ Common Mistake
```python
import weakref                               # module

class Node: ...                              # simple class

# ❌ Wrong: weakref to a temporary — nobody holds a strong ref
r3 = weakref.ref(Node())                     # object dies immediately
print(r3())                                  # Output: None  (surprise!)

# ✅ Correct: keep a strong reference somewhere as long as you need it
keep = Node()                                # strong ref
r4 = weakref.ref(keep)                       # weak ref
print(r4() is keep)                          # Output: True
```

---

## 🎯 Interview Tip (1 line)
Say: "Weakrefs avoid memory leaks in caches, observers and parent/child back-references — but list, dict, int, str can't be weakly referenced (subclass them, or `__slots__` needs `__weakref__`)."

---

## 🔗 Related Questions
→ Q307 (memory management & GC) | Q169 (__slots__) | Q185 (cache with TTL) | Q289 (tracemalloc)
