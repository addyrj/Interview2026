---

# 085. Instance Methods
# हिंदी में: Instance Methods (Object के Methods)

---

## 🔵 Simple Definition (English)
An instance method is a normal function inside a class whose first parameter is `self`. It works on one specific object and can read or change that object's data. It is the most common kind of method.

## 🔵 सरल परिभाषा (Hindi)
Instance method class के अंदर का सामान्य function है जिसका पहला parameter `self` होता है। यह किसी एक खास object पर काम करता है और उसका data पढ़/बदल सकता है। यह सबसे आम तरह का method है।

---

## 🔴 Problem it Solves
Data alone is not useful; you need operations on it. Without methods you would write free functions like `area(rect)` and `scale(rect, 2)` and pass the object everywhere. Instance methods keep the behaviour next to the data (`rect.area()`), make code read naturally and let you hide internal details.

## 🔴 यह क्यों बना? (Hindi)
सिर्फ data काफ़ी नहीं होता, उस पर operations भी चाहिए। Methods के बिना आप `area(rect)` और `scale(rect, 2)` जैसे free functions लिखते और object हर जगह पास करते। Instance methods behaviour को data के पास रखते हैं (`rect.area()`), code पढ़ने में स्वाभाविक होता है और internal details छुपाई जा सकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `def area(self)` is stored as a plain function in `Rectangle.__dict__`
Step 2 → You write `r.area()`
Step 3 → Python finds `area` on the class and uses the descriptor rule: functions create a bound method
Step 4 → Bound method = function + the object `r` stored as `__self__`
Step 5 → Calling it passes `r` automatically as the first argument
Step 6 → So `r.area()` is exactly `Rectangle.area(r)`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `def area(self)` `Rectangle.__dict__` में सामान्य function की तरह रखा जाता है
Step 2 → आप `r.area()` लिखते हैं
Step 3 → Python class में `area` ढूँढता है; descriptor rule से function एक bound method बन जाता है
Step 4 → Bound method = function + object `r` (`__self__` में)
Step 5 → Call करने पर `r` अपने आप पहले argument के रूप में जाता है
Step 6 → इसलिए `r.area()` बिल्कुल `Rectangle.area(r)` जैसा है
```

---

## 🟡 Real World Example
A `Cart` object in a shopping app has `add(sku, qty)`, `remove(sku)` and `total()`. A `Wallet` has `credit` and `debit`. An order state machine has `advance()` that moves from created to paid to shipped. An ORM query builder returns `self` from each call so you can chain `.where(...).limit(10)`.

## 🟡 Real Example Hindi mein
Shopping app के `Cart` object में `add(sku, qty)`, `remove(sku)` और `total()` होते हैं। `Wallet` में `credit` और `debit`। Order state machine में `advance()` है जो created से paid और फिर shipped पर ले जाता है। ORM query builder हर call में `self` return करता है ताकि `.where(...).limit(10)` chain हो सके।

---

## 💻 Code Example — Basic
```python
# Basic: instance methods receive the object as self
class Rectangle:                                  # a simple shape
    def __init__(self, w: float, h: float) -> None:
        self.w: float = w                         # width
        self.h: float = h                         # height

    def area(self) -> float:                      # instance method: needs self
        return self.w * self.h                    # uses this object's data

    def scale(self, k: float) -> None:            # changes the object (mutator)
        self.w *= k                               # update width
        self.h *= k                               # update height

    def bigger_than(self, other: "Rectangle") -> bool:   # works with another object
        return self.area() > other.area()         # call other methods through self


r: Rectangle = Rectangle(2, 3)                    # create
print(r.area())                                   # 6
r.scale(2)                                        # now 4 x 6
print(r.area(), r.bigger_than(Rectangle(1, 1)))   # 24 True
print(Rectangle.area(r))                          # same call written explicitly
m = r.area                                        # bound method
print(m.__self__ is r, m())                       # remembers r
print(type(Rectangle.area), type(r.area))         # function vs bound method
try:
    Rectangle.area()                              # forgot to pass the object
except TypeError as e:
    print("Error:", e)

# Output:
# 6
# 24 True
# 24
# True 24
# <class 'function'> <class 'method'>
# Error: Rectangle.area() missing 1 required positional argument: 'self'
```

## 💻 Code Example — Advanced
```python
# Advanced: method chaining, state machine, and delegation
from __future__ import annotations
from typing import Self                           # Python 3.11+ return type for chaining


class QueryBuilder:                               # tiny SQL builder like SQLAlchemy does
    def __init__(self, table: str) -> None:
        self._table: str = table                  # table name
        self._where: list[str] = []               # conditions
        self._limit: int | None = None            # optional limit

    def where(self, cond: str) -> Self:           # returns self so calls can chain
        self._where.append(cond)
        return self

    def limit(self, n: int) -> Self:
        if n < 1:                                 # guard rail
            raise ValueError("limit must be >= 1")
        self._limit = n
        return self

    def build(self) -> str:                       # produce final SQL
        sql = f"SELECT * FROM {self._table}"
        if self._where:
            sql += " WHERE " + " AND ".join(self._where)
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        return sql


print(QueryBuilder("orders").where("status='paid'").where("amount>100").limit(10).build())


class Order:                                      # state machine: methods guard legal transitions
    _FLOW = {"created": "paid", "paid": "shipped", "shipped": "delivered"}

    def __init__(self) -> None:
        self.state: str = "created"

    def advance(self) -> str:
        nxt = self._FLOW.get(self.state)          # next legal state
        if nxt is None:
            raise RuntimeError(f"cannot advance from {self.state}")
        self.state = nxt
        return nxt


o = Order()
print([o.advance() for _ in range(3)])
try:
    o.advance()
except RuntimeError as e:
    print("Error:", e)

try:
    QueryBuilder("t").limit(0)
except ValueError as e:
    print("Error:", e)
# methods live on the class, not copied per object:
print(Order().advance.__func__ is Order().advance.__func__)   # True

# Output:
# SELECT * FROM orders WHERE status='paid' AND amount>100 LIMIT 10
# ['paid', 'shipped', 'delivered']
# Error: cannot advance from delivered
# Error: limit must be >= 1
# True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Define | `def m(self, ...)` | `m(...) {}` in class |
| Current object | `self` explicit | `this` implicit |
| Detached method loses object? | no, bound method keeps it | yes, `this` is lost without `.bind` |
| Chaining | `return self` | `return this` |
| Call via class | `Class.m(obj)` | `Class.prototype.m.call(obj)` |

```python
# Python way
class Counter:
    def __init__(self) -> None:
        self.n: int = 0
    def inc(self) -> "Counter":
        self.n += 1
        return self

c = Counter()
f = c.inc          # bound method remembers c
f(); f()
print(c.n)         # 2
```
```javascript
// JavaScript way
class Counter {
  constructor() { this.n = 0; }
  inc() { this.n += 1; return this; }
}
const c = new Counter();
const f = c.inc;   // `this` is lost here!
try { f(); } catch (e) { console.log("TypeError"); }
```

Key difference: a Python bound method keeps its object forever (`f = c.inc` still works). In JavaScript, a method taken out of an object loses `this`, which is why React code uses `.bind` or arrow functions.

---

## 🟠 FastAPI Connection
Route functions stay thin and call instance methods on service objects. The cart example shows the pattern: validation lives in the method, the route only converts errors to HTTP codes. Class-based dependencies also use `__call__` as an instance method.

```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()


class Cart:
    def __init__(self) -> None:
        self.items: dict[str, int] = {}

    def add(self, sku: str, qty: int) -> None:    # instance method holds the logic
        if qty < 1:
            raise ValueError("qty must be >= 1")
        self.items[sku] = self.items.get(sku, 0) + qty

    def total_qty(self) -> int:
        return sum(self.items.values())


cart = Cart()


@app.post("/cart/{sku}")
def add_to_cart(sku: str, qty: int = 1) -> dict[str, int]:
    try:
        cart.add(sku, qty)                        # route stays thin, object does the work
    except ValueError as e:
        raise HTTPException(400, str(e))
    return {"total_qty": cart.total_qty()}


c = TestClient(app)
print(c.post("/cart/pen?qty=2").json(), c.post("/cart/pen?qty=0").status_code)

# Output:
# {'total_qty': 2} 400
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `self.` when using an attribute
✅ Correct: use `self.name`

```python
class A:
    def __init__(self) -> None:
        self.total = 0
    def add_wrong(self, n: int) -> None:
        total = self.total + n      # Wrong: local variable, lost
    def add_right(self, n: int) -> None:
        self.total += n             # Right
a = A()
a.add_wrong(5); print(a.total)      # 0
a.add_right(5); print(a.total)      # 5
```

❌ Mistake 2: Calling another method without `self.`
✅ Correct: use `self.other()`

```python
class B:
    def helper(self) -> int:
        return 1
    def main(self) -> int:
        return helper() + 1         # Wrong: NameError

class B2(B):
    def main(self) -> int:
        return self.helper() + 1    # Right
try:
    B().main()
except NameError as e:
    print("Error:", e)
print(B2().main())
```

❌ Mistake 3: Returning nothing in a method meant for chaining
✅ Correct: return `self`

```python
class Q:
    def __init__(self) -> None:
        self.parts: list[str] = []
    def add(self, p: str):
        self.parts.append(p)        # Wrong: returns None
class Q2(Q):
    def add(self, p: str):
        self.parts.append(p)
        return self                 # Right
try:
    Q().add("a").add("b")
except AttributeError as e:
    print("Error:", e)
print(Q2().add("a").add("b").parts)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class P:
    def show(self):
        return "P"
p = P()
f = p.show
P.show = lambda self: "patched"
print(f(), p.show())
p.show = lambda: "instance"
print(p.show(), P().show())
```

Output:
```
P patched
instance patched
```

Answer: `f = p.show` creates a bound method holding the ORIGINAL function, so patching the class later does not change `f()`; it still returns `P`. `p.show()` finds the patched class function and returns `patched`. Next, `p.show = lambda: ...` stores a plain function in the instance dictionary; instance attributes win over class functions, and since it is not bound it needs no `self`, so `p.show()` returns `instance`. A fresh `P()` has no such attribute and uses the patched class method: `patched`.

---

## ⚫ Interview Questions + Answers

Q1: What is `self` and who passes it?
A1: `self` is the object the method is called on. Python passes it automatically when you call `obj.method()`; the function becomes a bound method that stores the object in `__self__`.

Q2: What is the difference between a function and a bound method?
A2: Accessed on the class, `Class.m` is a plain function and needs the object passed by hand. Accessed on an object, `obj.m` is a bound method with the object already attached. Both live in `Class.__dict__` as a single function.

Q3: Can an instance method be called without an object?
A3: Yes, `Class.method(obj)` works and is how `super()` and explicit parent calls operate. `Class.method()` with nothing raises TypeError for the missing `self`.

Q4: How do you implement method chaining?
A4: Return `self` from each mutating method: `def where(self, c): ...; return self`. In Python 3.11+ annotate it with `typing.Self` so subclasses keep their own type.

Q5: Are methods copied for every object?
A5: No. Methods exist once on the class. Each object only stores its data; `obj.m` creates a cheap bound method when accessed. This is why 1 million objects do not mean 1 million copies of the code.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Behaviour that reads or changes one object's data
- State transitions (pay, ship, cancel)
- Business rules that depend on the object's fields
- Method chaining for builders

❌ Avoid when:
- The method never uses `self`; make it a static method or plain function
- Behaviour belongs to the class, not an object; use a classmethod
- Huge methods; split into small helpers

---

## 📊 Visual Diagram
```
r = Rectangle(2, 3)
r.area()
  |
  | 1. look in r.__dict__ -> no "area"
  | 2. look in Rectangle  -> function area
  | 3. bind: bound_method(__self__=r, __func__=area)
  v
Rectangle.area(r)   <- r passed as self automatically
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Instance method | Method that receives self | `self` लेने वाला method |
| Bound method | Function tied to an object | किसी object से जुड़ा function |
| self | The object itself | Object खुद |
| Mutator | Method that changes state | State बदलने वाला method |
| Method chaining | Calls joined with dots | Dot से जुड़े लगातार calls |
| Descriptor | Object that customises attribute access | Attribute access बदलने वाला object |

---

## ⚡ 3-Line Summary
English: Instance methods get the object as `self` and work on its data. `obj.m()` is the same as `Class.m(obj)`. Return `self` to allow method chaining.
Hindi: Instance methods को object `self` के रूप में मिलता है और वे उसके data पर काम करते हैं। `obj.m()` और `Class.m(obj)` एक ही हैं। Chaining के लिए `self` return करें।

---

## ➡️ Next Topic
**086. Class Methods (`@classmethod`)** — methods that receive the class instead of the object, used for alternate constructors.
