---

# Q134. Fix __eq__ Without __hash__ Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
After adding `__eq__` to `Point`, putting points in a set or using them as dict keys crashes with `TypeError: unhashable type: 'Point'`. Find and fix the bug.

```python
# BUGGY CODE:
class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y                    # coordinates
    def __eq__(self, other: object) -> bool:     # ❌ defined __eq__ but no __hash__
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

seen = {Point(1, 2)}   # TypeError: unhashable type: 'Point'
```

---

## 💡 Quick Concept (2 lines only)
If a class defines `__eq__` without `__hash__`, Python sets `__hash__ = None`, making instances unhashable. Equal objects MUST have equal hashes, so define `__hash__` from the same fields (immutable ones).
हिंदी: `__eq__` लिखा और `__hash__` नहीं — तो object unhashable हो जाता है; दोनों साथ define करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

class Point:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y                            # coordinates
    def __eq__(self, other: object) -> bool:             # equality by value
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

print(Point.__hash__)                                    # Expected: None  (Python removed it)
try:
    seen = {Point(1, 2)}                                 # needs hash()
except TypeError as e:                                   # catch
    print("TypeError:", e)                               # Expected: TypeError: unhashable type: 'Point'

class PointOk:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y                            # coordinates
    def __eq__(self, other: object) -> bool:             # Step 1: equality by value
        return isinstance(other, PointOk) and (self.x, self.y) == (other.x, other.y)
    def __hash__(self) -> int:                           # Step 2: hash from the SAME fields
        return hash((self.x, self.y))                    # tuple hash combines both

# ============================================
# TEST CASES
# ============================================
s = {PointOk(1, 2), PointOk(1, 2), PointOk(3, 4)}        # duplicates collapse
print(len(s), PointOk(1, 2) in s)                        # Expected: 2 True
print({PointOk(1, 2): "a"}[PointOk(1, 2)])               # Expected: a  (lookup by equal key)
```

---

## 🔍 Why This Works (3 lines max)
Sets/dicts find items by `hash()` first, then confirm with `==`. The rule: `a == b` implies `hash(a) == hash(b)`; hash the same fields that `__eq__` compares. That is why Python blocks hashing when you override only `__eq__`.
हिंदी: set/dict पहले hash देखते हैं फिर `==` — इसलिए दोनों methods एक ही fields पर होने चाहिए।

---

## ⚡ Alternative Solution
```python
from dataclasses import dataclass              # auto-generates __eq__ and __hash__

@dataclass(frozen=True)                        # frozen=True + eq=True -> generates __hash__
class P:
    x: int                                     # field 1
    y: int                                     # field 2

print(len({P(1, 2), P(1, 2)}), P(1, 2) == P(1, 2))   # Output: 1 True

@dataclass                                     # plain dataclass: eq=True, not frozen
class Q:
    x: int                                     # field

try:
    hash(Q(1))                                 # mutable dataclass is unhashable
except TypeError as e:
    print("TypeError:", e)                     # Output: TypeError: unhashable type: 'Q'

@dataclass(unsafe_hash=True)                   # force a hash (you promise not to mutate)
class R:
    x: int                                     # field

print(len({R(1), R(1)}))                       # Output: 1
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: hashing MUTABLE fields, then mutating the object inside a set
class PointOk:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y                          # mutable coordinates
    def __eq__(self, other: object) -> bool:
        return isinstance(other, PointOk) and (self.x, self.y) == (other.x, other.y)
    def __hash__(self) -> int:
        return hash((self.x, self.y))                  # hash depends on mutable state

p = PointOk(1, 2)               # create point
st = {p}                        # stored under hash((1, 2))
p.x = 9                         # hash changes, set still looks in the old bucket
print(p in st)                  # Output: False  (item is "lost")

# ✅ Correct: make the object immutable (frozen dataclass / __slots__ + read-only properties)
```

---

## 🎯 Interview Tip (1 line)
Say: "Equal objects must have equal hashes — I define `__hash__` from the same immutable fields as `__eq__`, or use `@dataclass(frozen=True)`."

---

## 🔗 Related Questions
→ Q034 (__eq__ without __hash__ output) | Q148 (complete dataclass) | Q175 (mutability and hashability) | Q246 (dataclasses) | Q292 (mutable vs immutable)
