---

# Q169. Explain __slots__
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What does `__slots__` do? Show what changes versus a normal class (memory, dynamic attributes) and the inheritance gotcha.

---

## 💡 Quick Concept (2 lines only)
`__slots__` replaces the per-instance `__dict__` with fixed slots, so instances use less memory and cannot get new attributes.
हिंदी: `__slots__` हर object का `__dict__` हटा देता है — memory कम, और नए attributes जोड़ना बंद।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys                                   # Step 1: for getsizeof

class Plain:                                 # Step 2: normal class (has __dict__)
    def __init__(self, x: int, y: int) -> None:
        self.x = x                           # stored in per-instance dict
        self.y = y

class Slim:                                  # Step 3: slotted class
    __slots__ = ("x", "y")                   # only these attributes allowed
    def __init__(self, x: int, y: int) -> None:
        self.x = x                           # stored in a fixed slot
        self.y = y

# ============================================
# TEST CASES
# ============================================
p, s = Plain(1, 2), Slim(1, 2)               # create both
print(hasattr(p, "__dict__"), hasattr(s, "__dict__"))  # Expected: True False
p.z = 3                                      # dynamic attribute: fine
print(p.z)                                   # Expected: 3
try:
    s.z = 3                                  # not in __slots__
except AttributeError as e:
    print("AttributeError:", e)              # Expected: AttributeError: 'Slim' object has no attribute 'z' and no __dict__ for setting new attributes
print(sys.getsizeof(p) + sys.getsizeof(p.__dict__), sys.getsizeof(s))  # Expected (3.13.3 64-bit; varies by version): 344 48
```

---

## 🔍 Why This Works (3 lines max)
Normal instances carry a dict (hash table) for attributes; slots store values in fixed offsets inside the object itself. That saves memory (big win with millions of objects) and slightly speeds attribute access, but you lose dynamic attributes.
हिंदी: Slots में values object के अंदर fixed जगह पर रहती हैं, dict नहीं बनता — इसलिए memory बचती है।

---

## ⚡ Alternative Solution
```python
from dataclasses import dataclass            # dataclass can generate __slots__ for you (3.10+)

@dataclass(slots=True)                       # slots=True adds __slots__ automatically
class Pt:
    x: int                                   # field 1
    y: int                                   # field 2

pt = Pt(1, 2)                                # create instance
print(pt, hasattr(pt, "__dict__"))           # Expected: Pt(x=1, y=2) False
try:
    pt.z = 1                                 # new attribute blocked
except AttributeError as e:
    print("AttributeError:", e)              # Expected: AttributeError: 'Pt' object has no attribute 'z' and no __dict__ for setting new attributes

# Inheritance: subclass WITHOUT __slots__ gets a __dict__ again
class Sub(Slim):                             # Slim from above
    pass                                     # no __slots__ here
sub = Sub(1, 2)                              # create
sub.z = 9                                    # works again
print(sub.z, hasattr(sub, "__dict__"))       # Expected: 9 True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming a subclass stays slotted
class Base:
    __slots__ = ("a",)                       # base is slotted
class Child(Base):
    pass                                     # forgot __slots__ -> __dict__ is back
print(hasattr(Child(), "__dict__"))          # Output: True  (savings lost)

# ✅ Correct: declare __slots__ in every subclass (empty tuple if no new fields)
class Child2(Base):
    __slots__ = ("b",)                       # only NEW names, not parent's
print(hasattr(Child2(), "__dict__"))         # Output: False
```

---

## 🎯 Interview Tip (1 line)
Say: "`__slots__` trades flexibility for memory — also no `__weakref__` unless you list it, and every subclass must declare slots too."

---

## 🔗 Related Questions
→ Q280 (__slots__ for memory) | Q148 (complete dataclass) | Q162 (descriptors) | Q246 (dataclasses)
