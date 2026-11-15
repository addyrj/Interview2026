---

# Q280. __slots__ for Memory
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
You create 100,000 small `Point` objects. How can `__slots__` reduce memory, and what do you give up?

---

## 💡 Quick Concept (2 lines only)
Normal instances store attributes in a per-object `__dict__`; `__slots__` replaces it with fixed slots, saving memory and blocking new attributes.
हिंदी: `__slots__` हर object का `__dict__` हटाकर memory बचाता है, पर नए attributes नहीं जोड़ सकते।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys  # for getsizeof
import tracemalloc  # to measure real allocations


class PointDict:  # regular class -> has __dict__
    def __init__(self, x: int, y: int) -> None:
        self.x = x  # stored in instance __dict__
        self.y = y  # stored in instance __dict__


class PointSlots:  # slotted class
    __slots__ = ("x", "y")  # Step 1: declare fixed attributes

    def __init__(self, x: int, y: int) -> None:
        self.x = x  # stored in a slot
        self.y = y  # stored in a slot


def measure(cls: type) -> int:  # Step 2: bytes allocated for 100k instances
    tracemalloc.start()  # begin tracing
    objs = [cls(1, 2) for _ in range(100_000)]  # create objects (kept alive)
    current, _peak = tracemalloc.get_traced_memory()  # current traced bytes
    tracemalloc.stop()  # stop tracing
    return current // 1000 if objs else 0  # KB


# ============================================
# TEST CASES
# ============================================
d, s = PointDict(1, 2), PointSlots(1, 2)  # one of each
print(sys.getsizeof(d) + sys.getsizeof(d.__dict__))  # Expected: 344 (object + dict; may differ by build)
print(sys.getsizeof(s))  # Expected: 48
print(hasattr(s, "__dict__"))  # Expected: False
print(measure(PointDict), measure(PointSlots))  # Expected: ~9604 ~5600 (KB; varies) -> slots smaller
try:
    s.z = 3  # adding an unlisted attribute
except AttributeError as e:  # slots forbid it
    print(type(e).__name__)  # Expected: AttributeError
```

---

## 🔍 Why This Works (3 lines max)
Without `__dict__` each instance is just a fixed-size struct holding pointers to values. The saving is per object, so it matters for millions of instances. Trade-off: no dynamic attributes, no weakrefs unless `__weakref__` is listed.
हिंदी: Fixed slots = छोटा object, पर dynamic attribute या weakref नहीं मिलेगा।

---

## ⚡ Alternative Solution
```python
from dataclasses import dataclass  # Python 3.10+ supports slots=True


@dataclass(slots=True)  # generates __slots__ automatically
class Point:
    x: int  # slot x
    y: int  # slot y


p = Point(1, 2)  # create
print(hasattr(p, "__dict__"))  # Expected: False
print(p)  # Expected: Point(x=1, y=2)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: inheriting from a non-slotted parent - __dict__ comes back
class Base:  # no __slots__
    pass

class Child(Base):
    __slots__ = ("x",)  # still has __dict__ via Base, saving is lost

# ✅ Correct: add __slots__ = () to every class in the hierarchy
class Base2:
    __slots__ = ()  # empty slots, no dict

class Child2(Base2):
    __slots__ = ("x",)  # now truly dict-free
```

---

## 🎯 Interview Tip (1 line)
Say: "__slots__ trades flexibility for memory (and slightly faster attribute access) - worth it for millions of small objects."

---

## 🔗 Related Questions
→ Q169 (explain __slots__) | Q246 (dataclasses) | Q289 (tracemalloc) | Q170 (weak references)
