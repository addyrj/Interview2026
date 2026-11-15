---

# Q138. Fix Shared Class Variable State Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Two different shopping carts show each other's items. After `a.add("apple")`, `b.items` also contains `"apple"`. Find and fix the bug.

```python
# BUGGY CODE:
class CartBuggy:
    items: list[str] = []                # ❌ class attribute: ONE list shared by all instances
    def __init__(self, owner: str) -> None:
        self.owner = owner               # per-instance data
    def add(self, item: str) -> None:
        self.items.append(item)          # mutates the shared class-level list
```

---

## 💡 Quick Concept (2 lines only)
A mutable object assigned in the class body lives on the CLASS and is shared by every instance. Create per-instance state in `__init__` (`self.items = []`) or use `field(default_factory=list)` in dataclasses.
हिंदी: class body का list सब instances में shared होता है — उसे `__init__` में बनाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

class CartBuggy:
    items: list[str] = []                    # one list stored on the class
    def __init__(self, owner: str) -> None:
        self.owner = owner                   # owner name
    def add(self, item: str) -> None:
        self.items.append(item)              # looks up `items` on the class -> shared

a, b = CartBuggy("A"), CartBuggy("B")        # two separate carts
a.add("apple")                               # add to cart A only
print(b.items, a.items is b.items)           # Expected: ['apple'] True   (bug: B has A's item)

class Cart:
    def __init__(self, owner: str) -> None:
        self.owner = owner                   # owner name
        self.items: list[str] = []           # Step 1: a NEW list per instance
    def add(self, item: str) -> None:
        self.items.append(item)              # mutates this instance's list only

# ============================================
# TEST CASES
# ============================================
a, b = Cart("A"), Cart("B")                  # two separate carts
a.add("apple")                               # add to cart A only
print(a.items, b.items, a.items is b.items)  # Expected: ['apple'] [] False
```

---

## 🔍 Why This Works (3 lines max)
Attribute lookup checks the instance `__dict__` first, then the class. `self.items.append(...)` finds no instance attribute, so it mutates the class-level list. Assigning in `__init__` puts a fresh list in each instance's `__dict__`.
हिंदी: lookup पहले instance फिर class में होता है — instance में list न हो तो class वाली share होती है।

---

## ⚡ Alternative Solution
```python
from dataclasses import dataclass, field          # dataclass helpers
from typing import ClassVar                       # marks intentional class-level data

@dataclass                                        # generates __init__
class CartDC:
    owner: str                                    # required field
    items: list[str] = field(default_factory=list)  # new list for every instance

a, b = CartDC("A"), CartDC("B")                   # two carts
a.items.append("x")                               # change only A
print(a.items, b.items)                           # Output: ['x'] []

try:
    @dataclass                                    # dataclass refuses mutable defaults
    class Bad:
        items: list[str] = []                     # ❌ shared-state trap
except ValueError as e:
    print("ValueError:", e)                       # Output: ValueError: mutable default <class 'list'> for field items is not allowed: use default_factory

class Registry:
    registry: ClassVar[dict[str, int]] = {}       # ✅ intentionally shared, declared as ClassVar

Registry.registry["k"] = 1                        # write via the class
print(Registry().registry)                        # Output: {'k': 1}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: thinking `+=` on a class-level list is safe
class T:
    tags: list[str] = []                 # shared list
    def add(self, t: str) -> None:
        self.tags += [t]                 # list += mutates IN PLACE, then rebinds self.tags

x, y = T(), T()                          # two instances
x.add("a")                               # add through x
print(y.tags, "tags" in x.__dict__)      # Output: ['a'] True   (y sees it; x also got an instance attr)

# ✅ Correct: initialise mutable state in __init__ — immutable class attrs (ints, str, tuple) are fine
```

---

## 🎯 Interview Tip (1 line)
Say: "Class attributes are shared; mutable state belongs in `__init__` or `field(default_factory=...)` — dataclasses even raise `ValueError` on a mutable default."

---

## 🔗 Related Questions
→ Q001 (mutable default argument) | Q028 (class vs instance variable) | Q029 (class attribute mutation via instance) | Q121 (mutable default argument bug) | Q148 (complete dataclass)
