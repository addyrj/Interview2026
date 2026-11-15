---

# 426. Strategy Pattern
# हिंदी में: Strategy Pattern (Algorithm को runtime पर बदलना)

---

## 🔵 Simple Definition (English)
Strategy puts each algorithm behind the same interface so you can swap one for another at runtime. The calling code (context) does not care which one it gets. In Python a strategy is often just a function.

## 🔵 सरल परिभाषा (Hindi)
Strategy हर algorithm को एक ही interface के पीछे रखता है ताकि runtime पर एक की जगह दूसरा लगाया जा सके। बुलाने वाला code (context) परवाह नहीं करता कि कौन सा मिला। Python में strategy अक्सर सिर्फ एक function होती है।

---

## 🔴 Problem it Solves
Shipping cost, discount rules, or payment fees change by customer or season. A giant `if/elif` chain inside one function grows forever, is hard to test, and every new rule touches old code. Strategy moves each rule into its own small unit and lets you pick one by name or config.

## 🔴 यह क्यों बना? (Hindi)
Shipping cost, discount rules या payment fees customer या season के हिसाब से बदलते हैं। एक function में बड़ी `if/elif` chain हमेशा बढ़ती रहती है, test करना मुश्किल होता है और हर नए rule पर पुराना code छूना पड़ता है। Strategy हर rule को अपनी छोटी unit में रखता है और नाम या config से एक चुनने देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the common interface (a Protocol or just a function signature)
Step 2 → Write one strategy per algorithm (Standard, Express)
Step 3 → Keep strategies in a registry dict {name: strategy}
Step 4 → The context (quote function) receives the name or the strategy
Step 5 → Context validates input, looks up the strategy, calls it
Step 6 → Adding a new algorithm = adding one entry, no old code changes
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → साझा interface तय करो (Protocol या सिर्फ function signature)
Step 2 → हर algorithm के लिए एक strategy लिखो (Standard, Express)
Step 3 → Strategies को registry dict {name: strategy} में रखो
Step 4 → Context (quote function) को नाम या strategy मिलती है
Step 5 → Context input validate करता है, strategy ढूंढता है, उसे बुलाता है
Step 6 → नया algorithm जोड़ना = एक entry जोड़ना, पुराना code नहीं बदलता
```

---

## 🟡 Real World Example
An e-commerce checkout picks a discount strategy (flat, percent, coupon, festive sale). A delivery app prices Standard vs Express shipping. A scikit-learn style ML service switches the model (logistic regression vs random forest) by config. Sorting with `key=` is Strategy too: you pass the comparison rule.

## 🟡 Real Example Hindi mein
E-commerce checkout discount strategy चुनता है (flat, percent, coupon, festive sale)। Delivery app Standard बनाम Express shipping का दाम तय करता है। scikit-learn जैसी ML service config से model बदलती है (logistic regression बनाम random forest)। `key=` के साथ sorting भी Strategy है: आप तुलना का नियम पास करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic Strategy: swap algorithm at runtime; in Python functions ARE strategies
from typing import Callable                   # function type


def flat(price: float) -> float:
    return price - 50                         # flat Rs.50 off


def percent(price: float) -> float:
    return price * 0.9                        # 10% off


def none(price: float) -> float:
    return price                              # no discount


def checkout(price: float, strategy: Callable[[float], float]) -> float:
    return strategy(price)                    # context uses whichever strategy given


print(checkout(500, flat))
print(checkout(500, percent))
print(checkout(500, none))

# Output:
# 450
# 450.0
# 500
```

## 💻 Code Example — Advanced
```python
# Production style: Protocol-based strategies + registry chosen by string (config / API param)
from dataclasses import dataclass             # simple value classes
from typing import Protocol                   # structural interface


class ShippingStrategy(Protocol):
    def cost(self, weight_kg: float, distance_km: float) -> float: ...


@dataclass(frozen=True)
class Standard:
    per_km: float = 0.5
    def cost(self, weight_kg: float, distance_km: float) -> float:
        return round(distance_km * self.per_km + weight_kg * 2, 2)


@dataclass(frozen=True)
class Express:
    def cost(self, weight_kg: float, distance_km: float) -> float:
        return round(100 + distance_km * 1.2 + weight_kg * 5, 2)


STRATEGIES: dict[str, ShippingStrategy] = {"standard": Standard(), "express": Express()}


def quote(kind: str, weight_kg: float, distance_km: float) -> float:
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    try:
        strategy: ShippingStrategy = STRATEGIES[kind]
    except KeyError:
        raise ValueError(f"unknown shipping: {kind!r}") from None
    return strategy.cost(weight_kg, distance_km)


print(quote("standard", 2, 100))
print(quote("express", 2, 100))
for bad in (("drone", 1, 1), ("standard", 0, 1)):
    try:
        quote(*bad)
    except ValueError as e:
        print("Error:", e)

# Output:
# 54.0
# 230.0
# Error: unknown shipping: 'drone'
# Error: weight must be positive
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Strategy as function | `Callable[[float], float]` | `(price) => number` |
| Strategy as object | class with the method / `Protocol` | class or object literal |
| Registry | `dict[str, Strategy]` | `Map` or object |
| Built-in example | `sorted(key=...)` | `arr.sort((a, b) => ...)` |

```python
# Python way
def checkout(price: float, strategy: Callable[[float], float]) -> float:
    return strategy(price)                   # context just calls it
print(checkout(500, lambda p: p * 0.9))
```
```javascript
// JavaScript way
const checkout = (price, strategy) => strategy(price);   // context just calls it
console.log(checkout(500, (p) => p * 0.9));
```

Key difference: both languages have first-class functions, so the heavy class-based GoF version is rarely needed. In Python use plain functions for simple strategies and `Protocol` + dataclass when the strategy has its own settings.

---

## 🟠 FastAPI Connection
FastAPI gives you Strategy almost for free: use an `Enum` query parameter to select the strategy and let FastAPI reject unknown values with HTTP 422. Strategies can also be injected with `Depends` so tests can replace them.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from enum import Enum
from typing import Callable
from fastapi import FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()


class Mode(str, Enum):                        # FastAPI validates the strategy name for us
    standard = "standard"
    express = "express"


PRICE: dict[Mode, Callable[[float], float]] = {
    Mode.standard: lambda km: km * 0.5,
    Mode.express: lambda km: 100 + km * 1.2,
}


@app.get("/quote")
def quote(mode: Mode, km: float) -> dict[str, float]:
    return {"price": PRICE[mode](km)}


c = TestClient(app)
print(c.get("/quote", params={"mode": "express", "km": 10}).json())
print(c.get("/quote", params={"mode": "drone", "km": 10}).status_code)

# Output:
# {'price': 112.0}
# 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Growing if/elif chain instead of a registry
✅ Correct: dictionary of strategies

```python
# Wrong
if kind == "standard": cost = ...
elif kind == "express": cost = ...        # every new kind edits this function
# Right
cost = STRATEGIES[kind].cost(weight, km)  # new kind = new dict entry
```

❌ Mistake 2: Unknown strategy name raises a raw KeyError
✅ Correct: translate to a clear error

```python
# Wrong: STRATEGIES["drone"]            # KeyError: 'drone'
# Right
try:
    s = STRATEGIES[kind]
except KeyError:
    raise ValueError(f"unknown shipping: {kind!r}") from None
```

❌ Mistake 3: Late-binding closures when building strategies in a loop
✅ Correct: bind the value as a default argument (or use `functools.partial`)

```python
# Wrong: lambda p: p - p * rate / 100     # all lambdas see the LAST rate
# Right
strategies = {rate: (lambda p, r=rate: p - p * r / 100) for rate in (10, 20)}
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
strategies = {}
for rate in (10, 20):
    strategies[rate] = lambda p: p - p * rate / 100   # late binding
print(strategies[10](100), strategies[20](100))
```
Answer: Output: `80.0 80.0`. Both lambdas look up the variable `rate` when they are CALLED, not when they are created. After the loop `rate` is 20, so both subtract 20%. Fix with `lambda p, r=rate: ...` or `functools.partial`, or create the lambda inside a helper function.

---

## ⚫ Interview Questions + Answers

Q1: What is Strategy in one line?
A1: Different algorithms behind one interface, selectable at runtime.

Q2: Strategy vs if/else?
A2: if/else is fine for 2 stable cases. Strategy wins when cases grow, change independently, or need separate tests and configuration.

Q3: Do I need classes for Strategy in Python?
A3: No. A function is a strategy. Use classes (with `Protocol`) when a strategy has state or configuration like `Standard(per_km=0.5)`.

Q4: Strategy vs State pattern?
A4: Strategy: the caller chooses the algorithm, which rarely changes during the object's life. State: the object changes its own behaviour as its internal state changes.

Q5: Where does Python already use Strategy?
A5: `sorted(key=...)`, `max(key=...)`, `json.dumps(default=...)`, logging handlers/formatters, and `asyncio` event loop policies.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several interchangeable algorithms (pricing, shipping, parsing, ranking)
- Behaviour should be picked by config or user input
- You want to unit test each rule alone

❌ Avoid when:
- Only one algorithm will ever exist
- Two tiny stable branches: a plain `if` is clearer
- Strategies need heavy shared state: reconsider the design

---

## 📊 Visual Diagram
```
quote("express", 2, 100)
      |
      v   registry lookup
 STRATEGIES = {"standard": Standard(),
               "express" : Express()}
      |
      v
 Express().cost(2, 100) -> 230.0

Add "drone"?  -> add one class + one dict entry, no old code touched
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Strategy | One interchangeable algorithm | बदली जा सकने वाली एक algorithm |
| Context | Code that uses a strategy | Strategy इस्तेमाल करने वाला code |
| Protocol | Typing interface by shape | Shape के आधार पर typing interface |
| Registry | Name to strategy lookup | नाम से strategy ढूंढना |
| Late binding | Closure reads variable at call time | Closure call के समय variable पढ़ता है |

---

## ⚡ 3-Line Summary
English: Strategy keeps each algorithm in its own unit behind one interface and picks one at runtime. In Python a function or a small `Protocol` class plus a registry dict is enough. Beware late-binding closures when generating strategies in loops.
Hindi: Strategy हर algorithm को एक interface के पीछे अपनी unit में रखता है और runtime पर एक चुनता है। Python में function या छोटी `Protocol` class और registry dict काफी है। Loop में strategies बनाते समय late-binding closures से सावधान रहें।

---

## ➡️ Next Topic
**427. Decorator Pattern** — add behaviour by wrapping an object or function.
