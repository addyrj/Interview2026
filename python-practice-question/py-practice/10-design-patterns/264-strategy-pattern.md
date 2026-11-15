---

# Q264. Strategy Pattern
# Category: DESIGN PATTERNS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement the Strategy pattern: a `Cart` that can apply different discount algorithms (none, percentage, flat) which can be swapped at runtime, without `if/elif` inside `Cart`.

```python
cart = Cart([100, 50], discount=percent(10))
print(cart.total())   # 135.0
```

---

## 💡 Quick Concept (2 lines only)
Strategy = interchangeable algorithms behind one interface, chosen at runtime. In Python, functions are first-class, so a strategy is usually just a function (or `Callable`), not a class hierarchy.
हिंदी: Strategy में algorithm को function की तरह pass करते हैं — runtime पर बदल सकते हैं, `if/elif` की ज़रूरत नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections.abc import Callable             # strategy type

Discount = Callable[[float], float]              # takes subtotal, returns discounted total

def no_discount(subtotal: float) -> float:
    return subtotal                              # strategy 1: nothing

def percent(p: float) -> Discount:
    def apply(subtotal: float) -> float:
        return subtotal * (1 - p / 100)          # strategy 2: p% off
    return apply                                 # closure remembers p

def flat(amount: float) -> Discount:
    def apply(subtotal: float) -> float:
        return max(subtotal - amount, 0.0)       # strategy 3: fixed amount, never negative
    return apply

class Cart:
    def __init__(self, items: list[float], discount: Discount = no_discount) -> None:
        self.items = items                       # prices
        self.discount = discount                 # the strategy (swappable)

    def total(self) -> float:
        return self.discount(sum(self.items))    # delegate; Cart has no discount logic

# ============================================
# TEST CASES
# ============================================
cart = Cart([100, 50])                           # default strategy
print(cart.total())                              # 150
cart.discount = percent(10)                      # swap at runtime
print(cart.total())                              # 135.0
cart.discount = flat(200)                        # bigger than subtotal
print(cart.total())                              # clamped at 0.0

# Output:
# 150
# 135.0
# 0.0
```

---

## 🔍 Why This Works (3 lines max)
`Cart` depends only on "a callable that maps float to float", so any strategy fits and new ones need no changes to `Cart` (open/closed). Closures (`percent(10)`) carry their configuration. Swapping `cart.discount` changes behaviour at runtime.
हिंदी: Cart सिर्फ callable को call करता है, इसलिए नया discount जोड़ने पर Cart नहीं बदलता।

---

## ⚡ Alternative Solution
```python
# Class-based strategies with Protocol (when strategies need state or several methods)
from typing import Protocol                      # structural typing

class Discount(Protocol):
    def apply(self, subtotal: float) -> float: ...   # required method

class Percent:
    def __init__(self, p: float) -> None:
        self.p = p                               # state
    def apply(self, subtotal: float) -> float:
        return subtotal * (1 - self.p / 100)

class Flat:
    def __init__(self, amount: float) -> None:
        self.amount = amount
    def apply(self, subtotal: float) -> float:
        return max(subtotal - self.amount, 0.0)

def checkout(subtotal: float, strategy: Discount) -> float:
    return strategy.apply(subtotal)              # duck typing: any object with apply()

print(checkout(150, Percent(10)), checkout(150, Flat(20)))

# Output:
# 135.0 130.0
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: if/elif inside the class - must edit Cart for every new discount
class Cart:
    def total(self, kind, value):
        s = sum(self.items)
        if kind == "percent":
            return s * (1 - value / 100)
        elif kind == "flat":
            return s - value
        # new discount type -> edit this method again

# ✅ Correct: inject the strategy (a callable) as in the solution
```

---

## 🎯 Interview Tip (1 line)
Say: "In Python a strategy is often just a function passed in; I use a Protocol or ABC only when the strategy needs state or multiple methods."

---

## 🔗 Related Questions
→ Q262 (factory pattern) | Q085 (compose) | Q088 (partial application) | Q222 (dependency injection)
