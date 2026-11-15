---

# Q265. Decorator Pattern
# Category: DESIGN PATTERNS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement the (GoF) Decorator pattern: add behaviour to an object by wrapping it, without changing its class. Example: a coffee whose price/description is extended by Milk and Sugar wrappers. Then compare with Python's `@decorator` syntax.

```python
coffee = Sugar(Milk(Coffee()))
print(coffee.description(), coffee.cost())   # Coffee, Milk, Sugar 2.8
```

---

## 💡 Quick Concept (2 lines only)
The Decorator pattern wraps an object that has the same interface and adds behaviour before/after delegating to it; wrappers can be stacked. Python's `@decorator` is the function-level version of the same idea.
हिंदी: Decorator pattern में object को उसी interface वाले wrapper में लपेट कर नया behaviour जोड़ते हैं — class बदले बिना।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from abc import ABC, abstractmethod              # common interface

class Beverage(ABC):
    @abstractmethod
    def cost(self) -> float: ...                 # price
    @abstractmethod
    def description(self) -> str: ...            # text

class Coffee(Beverage):
    def cost(self) -> float:
        return 2.0                               # base price
    def description(self) -> str:
        return "Coffee"                          # base text

class AddOn(Beverage):                           # base wrapper: same interface, holds a Beverage
    def __init__(self, inner: Beverage) -> None:
        self.inner = inner                       # the wrapped object

class Milk(AddOn):
    def cost(self) -> float:
        return self.inner.cost() + 0.5           # delegate + extend
    def description(self) -> str:
        return self.inner.description() + ", Milk"

class Sugar(AddOn):
    def cost(self) -> float:
        return self.inner.cost() + 0.3
    def description(self) -> str:
        return self.inner.description() + ", Sugar"

# ============================================
# TEST CASES
# ============================================
coffee = Sugar(Milk(Coffee()))                   # stack wrappers
print(coffee.description(), coffee.cost())       # combined behaviour
print(Milk(Milk(Coffee())).cost())               # same wrapper twice is fine

# Output:
# Coffee, Milk, Sugar 2.8
# 3.0
```

---

## 🔍 Why This Works (3 lines max)
Each wrapper implements `Beverage` and holds another `Beverage`, so wrappers can be nested in any order and any number of times, avoiding a subclass explosion (`MilkSugarCoffee`...). Python's function `@decorator` does the same: wraps a callable, same call signature.
हिंदी: हर wrapper उसी interface को implement करता है, इसलिए उन्हें किसी भी क्रम में नेस्ट कर सकते हैं।

---

## ⚡ Alternative Solution
```python
# Pythonic function decorator: same idea applied to callables
import functools                                 # wraps

def uppercase(f):
    @functools.wraps(f)
    def wrapper(*a, **k):
        return f(*a, **k).upper()                # extend result of wrapped function
    return wrapper

def exclaim(f):
    @functools.wraps(f)
    def wrapper(*a, **k):
        return f(*a, **k) + "!"
    return wrapper

@exclaim
@uppercase                                       # applied bottom-up, runs outer-first
def greet(name: str) -> str:
    return f"hello {name}"

print(greet("bob"))

# Output:
# HELLO BOB!
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: subclass for every combination
class Coffee: ...
class MilkCoffee(Coffee): ...
class SugarCoffee(Coffee): ...
class MilkSugarCoffee(MilkCoffee): ...           # explosion: 2^n classes for n add-ons

# ✅ Correct: n small wrappers composed at runtime (Sugar(Milk(Coffee())))
```

---

## 🎯 Interview Tip (1 line)
Say: "GoF Decorator = composition with the same interface, stackable at runtime; Python's `@decorator` is the same idea for functions, but the GoF version is for objects."

---

## 🔗 Related Questions
→ Q038 (decorator stacking order) | Q166 (decorators with arguments) | Q255 (decorator tricks) | Q266 (proxy pattern)
