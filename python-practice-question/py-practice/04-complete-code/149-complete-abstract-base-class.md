---

# Q149. Complete Abstract Base Class
# Category: Complete The Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Complete `Shape` as an abstract base class so it cannot be instantiated and subclasses MUST implement `area()`.

```python
from ____ import ABC, ____                         # BLANK 1: module + the decorator name


class Shape(____):                                 # BLANK 2: base class
    @____                                          # BLANK 3: mark the method abstract
    def area(self) -> float: ...

    def describe(self) -> str:                     # concrete method shared by all
        return f"{type(self).__name__} with area {self.area():.2f}"
```

---

## 💡 Quick Concept (2 lines only)
An ABC with `@abstractmethod` blocks instantiation until every abstract method is overridden — it enforces an interface at object-creation time.
हिंदी: ABC में `@abstractmethod` वाले methods override किए बिना object नहीं बन सकता।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import math                                        # for pi
from abc import ABC, abstractmethod                # BLANK 1: abc module


class Shape(ABC):                                  # BLANK 2: ABC makes the abstract check work
    @abstractmethod                                # BLANK 3: subclasses must override
    def area(self) -> float: ...                   # no body needed

    def describe(self) -> str:                     # concrete method reuses the abstract one
        return f"{type(self).__name__} with area {self.area():.2f}"


class Circle(Shape):                               # concrete subclass
    def __init__(self, r: float) -> None:
        self.r = r                                 # radius

    def area(self) -> float:                       # implements the abstract method
        return math.pi * self.r ** 2


class Rect(Shape):                                 # another concrete subclass
    def __init__(self, w: float, h: float) -> None:
        self.w, self.h = w, h                      # sides

    def area(self) -> float:
        return self.w * self.h


class Broken(Shape):                               # forgets to implement area()
    pass


# ============================================
# TEST CASES
# ============================================
print(Circle(1).describe())                        # Expected: Circle with area 3.14
print(Rect(2, 3).describe())                       # Expected: Rect with area 6.00

for cls in (Shape, Broken):                        # both are still abstract
    try:
        cls()                                      # instantiation fails
    except TypeError as e:
        print(e)
# Expected: Can't instantiate abstract class Shape without an implementation for abstract method 'area'
# Expected: Can't instantiate abstract class Broken without an implementation for abstract method 'area'
print(isinstance(Rect(1, 1), Shape))               # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
`ABCMeta` records abstract method names in `__abstractmethods__`; `object.__new__` refuses to create an instance while that set is non-empty. Error arises at instantiation, not at class definition.
हिंदी: `ABCMeta` abstract methods की list रखता है — खाली न हो तो object बनाते समय `TypeError` आता है।

---

## ⚡ Alternative Solution
```python
# Structural typing: typing.Protocol (no inheritance needed, checked by type checkers)
from typing import Protocol, runtime_checkable


@runtime_checkable                                 # allow isinstance() checks
class HasArea(Protocol):
    def area(self) -> float: ...                   # required method signature

class Square:                                      # does NOT inherit HasArea
    def __init__(self, s: float) -> None:
        self.s = s

    def area(self) -> float:
        return self.s ** 2

print(isinstance(Square(2), HasArea))              # Expected: True  (duck typing)
print(isinstance(object(), HasArea))               # Expected: False
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: class Shape:  with @abstractmethod but NOT inheriting ABC
#    -> decorator has no effect, Shape() works silently
# ❌ Wrong: raising NotImplementedError only -> error appears late, at call time
# ✅ Correct: inherit ABC (or metaclass=ABCMeta) AND use @abstractmethod
```

---

## 🎯 Interview Tip (1 line)
Say: "ABC = nominal, enforced at instantiation; Protocol = structural, duck-typed and checked statically — pick by whether you control the subclasses."

---

## 🔗 Related Questions
→ Q031 (inheritance & super) | Q163 (MRO) | Q168 (metaclasses) | Q247 (Protocol, TypedDict) | Q264 (strategy pattern)
