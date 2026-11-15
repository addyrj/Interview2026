---

# 101. Operator Overloading
# हिंदी में: Operator Overloading (अपने Objects पर +, -, == चलाना)

---

## 🔵 Simple Definition (English)
Operator overloading means defining what operators like `+`, `-`, `*`, `==`, `<` do for your own classes, by writing special methods such as `__add__`, `__sub__`, `__mul__`, `__eq__`, `__lt__`. Then `a + b` calls `a.__add__(b)`.

## 🔵 सरल परिभाषा (Hindi)
Operator overloading का मतलब है अपनी classes के लिए `+`, `-`, `*`, `==`, `<` जैसे operators का अर्थ तय करना, `__add__`, `__sub__`, `__mul__`, `__eq__`, `__lt__` जैसे special methods लिखकर। तब `a + b` असल में `a.__add__(b)` call करता है।

---

## 🔴 Problem it Solves
Without it, adding two `Money` objects needs `m1.add(m2)`, and chains look ugly: `a.add(b).add(c).multiply(2)`. For math-like types (money, vectors, matrices, durations) code should read like math: `(a + b + c) * 2`. Operator overloading gives natural syntax while keeping the validation logic (e.g., currencies must match) inside the class.

## 🔴 यह क्यों बना? (Hindi)
इसके बिना दो `Money` objects जोड़ने के लिए `m1.add(m2)` लिखना पड़ता है, और chain बदसूरत हो जाती है: `a.add(b).add(c).multiply(2)`. Money, vectors, matrices, durations जैसे math वाले types का code math की तरह पढ़ना चाहिए: `(a + b + c) * 2`. Operator overloading natural syntax देता है और validation (जैसे currency मेल खाए) class के अंदर ही रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write a + b
Step 2 → Python calls type(a).__add__(a, b)
Step 3 → If it returns NotImplemented (or does not exist), Python tries the reflected
         method type(b).__radd__(b, a)
Step 4 → If both fail -> TypeError: unsupported operand type(s) for +
Step 5 → In-place forms (a += b) use __iadd__ first, then fall back to __add__
Step 6 → Comparison: __eq__, __lt__, __le__, __gt__, __ge__;  unary: __neg__, __abs__
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप a + b लिखते हैं
Step 2 → Python type(a).__add__(a, b) call करता है
Step 3 → अगर वह NotImplemented लौटाए (या हो ही नहीं) तो Python reflected method
         type(b).__radd__(b, a) आज़माता है
Step 4 → दोनों fail -> TypeError: unsupported operand type(s) for +
Step 5 → In-place रूप (a += b) पहले __iadd__ देखता है, फिर __add__
Step 6 → Comparison: __eq__, __lt__, __le__, __gt__, __ge__;  unary: __neg__, __abs__
```

---

## 🟡 Real World Example
A payments service adds `Money` values: `price + gst - discount`. A game or maps backend adds `Vector2` positions. A scheduler adds `timedelta` to `datetime` (built-in operator overloading). NumPy arrays (`a * 2`), pandas Series (`df["a"] + df["b"]`), pathlib (`Path("a") / "b"`) and SQLAlchemy (`User.age > 18` builds SQL!) all use operator overloading.

## 🟡 Real Example Hindi mein
Payments service `Money` values जोड़ती है: `price + gst - discount`. Game या maps backend `Vector2` positions जोड़ता है. Scheduler `datetime` में `timedelta` जोड़ता है (built-in operator overloading). NumPy arrays (`a * 2`), pandas Series (`df["a"] + df["b"]`), pathlib (`Path("a") / "b"`) और SQLAlchemy (`User.age > 18` SQL बनाता है!) सब operator overloading इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic operator overloading with a 2D vector
import math                                     # for length


class Vector:                                   # simple 2D vector
    def __init__(self, x: float, y: float) -> None:   # constructor
        self.x: float = x                       # x part
        self.y: float = y                       # y part

    def __add__(self, other: "Vector") -> "Vector":   # v1 + v2
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":   # v1 - v2
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k: float) -> "Vector":    # v * 3
        return Vector(self.x * k, self.y * k)

    def __rmul__(self, k: float) -> "Vector":   # 3 * v (reflected)
        return self * k                         # reuse __mul__

    def __neg__(self) -> "Vector":              # -v
        return Vector(-self.x, -self.y)

    def __abs__(self) -> float:                 # abs(v) = length
        return math.hypot(self.x, self.y)

    def __eq__(self, other: object) -> bool:    # v1 == v2
        if not isinstance(other, Vector):       # different type
            return NotImplemented               # let Python decide
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self) -> str:                  # readable output
        return f"Vector({self.x}, {self.y})"


a: Vector = Vector(1, 2)                        # first vector
b: Vector = Vector(3, 4)                        # second vector
print(a + b, a - b, a * 3, 2 * a, -a)           # arithmetic operators
print(abs(b), a == Vector(1, 2), a == 5)        # length and equality
print(a + b * 2)                                # normal precedence rules still apply

# Output:
# Vector(4, 6) Vector(-2, -2) Vector(3, 6) Vector(2, 4) Vector(-1, -2)
# 5.0 True False
# Vector(7, 10)
```

## 💻 Code Example — Advanced
```python
# Production style: Money type with validation, ordering, hashing, sum() support
from __future__ import annotations              # allow Money in annotations
from dataclasses import dataclass               # compact class
from functools import total_ordering            # fill missing comparisons


@total_ordering                                 # we write __eq__ and __lt__, it adds <=, >, >=
@dataclass(frozen=True)                         # immutable + auto __eq__ and __hash__
class Money:
    paise: int                                  # integer paise: no float errors
    currency: str = "INR"                       # currency code

    def _check(self, other: Money) -> None:     # shared safety rule
        if self.currency != other.currency:     # never mix currencies
            raise ValueError(f"Currency mismatch: {self.currency} vs {other.currency}")

    def __add__(self, other: object) -> Money:
        if isinstance(other, int) and other == 0:   # supports sum() which starts with 0
            return self
        if not isinstance(other, Money):        # unsupported type
            return NotImplemented               # Python raises TypeError for us
        self._check(other)                      # validate currency
        return Money(self.paise + other.paise, self.currency)

    __radd__ = __add__                          # 0 + money (used by sum)

    def __sub__(self, other: Money) -> Money:
        self._check(other)
        return Money(self.paise - other.paise, self.currency)

    def __mul__(self, k: int | float) -> Money:
        return Money(round(self.paise * k), self.currency)    # scale by a number

    __rmul__ = __mul__                          # 2 * money

    def __lt__(self, other: Money) -> bool:     # needed by total_ordering
        self._check(other)
        return self.paise < other.paise

    def __bool__(self) -> bool:                 # if money:  -> non-zero
        return self.paise != 0

    def __str__(self) -> str:                   # friendly text
        return f"{self.currency} {self.paise / 100:.2f}"


price: Money = Money(49900)                     # 499.00
gst: Money = price * 0.18                       # 18% tax
total: Money = price + gst                      # natural syntax
print(price, gst, total)                        # str() output
print(sum([Money(100), Money(250), Money(50)])) # sum() works via __radd__
print(total > price, price <= price, Money(1) == Money(1))    # ordering and equality
print(sorted([Money(300), Money(100), Money(200)])[0])        # sorting uses __lt__
print({Money(100): "a"}[Money(100)])            # hashable because frozen dataclass
try:                                            # mixing currencies
    Money(100) + Money(100, "USD")              # business rule violated
except ValueError as e:
    print("Error:", e)
try:                                            # unsupported operand
    Money(100) + "5"                            # str is not Money
except TypeError as e:
    print("Error:", e)

# Output:
# INR 499.00 INR 89.82 INR 588.82
# INR 4.00
# True True True
# INR 1.00
# a
# Error: Currency mismatch: INR vs USD
# Error: unsupported operand type(s) for +: 'Money' and 'str'
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Operator overloading | Yes (`__add__`, `__eq__`, ...) | No (only `valueOf`/`toString` tricks) |
| Equality | `__eq__` | `===` cannot be changed |
| Reflected ops | `__radd__`, `__rmul__` | n/a |
| Indexing `a[i]` | `__getitem__` | Proxy objects only |
| Libraries using it | NumPy, pandas, pathlib, SQLAlchemy | none; uses methods (`a.add(b)`) |

```python
# Python way
class P:
    def __init__(self, n: int) -> None:
        self.n = n
    def __add__(self, o: "P") -> "P":
        return P(self.n + o.n)       # + works on P

print((P(1) + P(2)).n)               # 3
```
```javascript
// JavaScript way — + cannot be overloaded, so use a method
class P {
  constructor(n) { this.n = n; }
  add(o) { return new P(this.n + o.n); }    // must call .add()
}
console.log(new P(1).add(new P(2)).n);      // 3
console.log(new P(1) + new P(2));           // "[object Object][object Object]" (not what you want)
```

Key difference: JavaScript has no operator overloading, so libraries expose methods (`.add()`, `.plus()`). Python lets you write `a + b`, which is why NumPy, pandas and SQLAlchemy feel so natural.

---

## 🟠 FastAPI Connection
SQLAlchemy columns overload comparison operators: `User.age >= 18` returns a SQL expression, not a bool. FastAPI endpoints build filters with those operators. Also, `Path / "x"` from pathlib is common for file handling in uploads.

```python
# FastAPI example — operator overloading in a filter-building endpoint (pure Python stand-in)
from fastapi import FastAPI                     # app
from fastapi.testclient import TestClient       # test client


class Field:                                    # tiny version of what SQLAlchemy does
    def __init__(self, name: str) -> None:
        self.name: str = name                   # column name

    def __ge__(self, v: int) -> str:            # Field >= value  ->  SQL text
        return f"{self.name} >= {v}"

    def __lt__(self, v: int) -> str:            # Field < value
        return f"{self.name} < {v}"


age: Field = Field("age")                       # pretend column
app: FastAPI = FastAPI()                        # create app


@app.get("/adults")                             # GET /adults?min_age=21
def adults(min_age: int = 18) -> dict[str, str]:
    return {"where": age >= min_age}            # operator builds the filter text


client: TestClient = TestClient(app)            # test client
print(client.get("/adults", params={"min_age": 21}).json())

# Output:
# {'where': 'age >= 21'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Raising `TypeError` instead of returning `NotImplemented`
✅ Correct: return `NotImplemented` so Python can try the other operand's reflected method

```python
class A:
    def __add__(self, o: object) -> object:
        if not isinstance(o, A):
            return NotImplemented          # Right: gives B a chance

class B:
    def __radd__(self, o: object) -> str:
        return "B handled it"

print(A() + B())                           # B handled it
```

❌ Mistake 2: Defining `__eq__` without `__hash__` (object becomes unhashable)
✅ Correct: define `__hash__` too, or use a frozen dataclass

```python
class Wrong:
    def __init__(self, v: int) -> None:
        self.v = v
    def __eq__(self, o: object) -> bool:
        return isinstance(o, Wrong) and self.v == o.v

try:
    {Wrong(1)}                             # Wrong: __hash__ became None
except TypeError as e:
    print("Error:", e)

class Right(Wrong):
    def __hash__(self) -> int:
        return hash(self.v)                # Right

print(len({Right(1), Right(1)}))           # 1
```

❌ Mistake 3: Mutating `self` inside `__add__`
✅ Correct: return a NEW object; use `__iadd__` only for deliberate in-place changes

```python
class Bag:
    def __init__(self, items: list[int]) -> None:
        self.items = items
    def __add__(self, o: "Bag") -> "Bag":
        self.items.extend(o.items)         # Wrong: changes the left operand
        return self

a, b = Bag([1]), Bag([2])
c = a + b
print(a.items)                             # [1, 2]  <- a was modified, surprising!
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class N:
    def __init__(self, v: int) -> None:
        self.v = v
    def __add__(self, o: "N") -> "N":
        print("add")
        return N(self.v + o.v)
    def __iadd__(self, o: "N") -> "N":
        print("iadd")
        self.v += o.v
        return self

a = N(1)
b = a
a += N(2)
print(a is b, b.v)
x = (1, 2)
y = x
x += (3,)
print(x, y)
```
Answer: `iadd`, then `True 3`; next `(1, 2, 3) (1, 2)`. `+=` calls `__iadd__` when defined, and here it mutates the same object, so `b` (the same object) sees the change. Tuples are immutable and have no in-place add, so `x += (3,)` falls back to `x = x + (3,)` and creates a new tuple; `y` is unchanged. For lists, `+=` mutates in place (shared references change!).

---

## ⚫ Interview Questions + Answers

Q1: Which method runs for `a + b` and what is `__radd__`?
A1: `type(a).__add__(a, b)` first. If it is missing or returns `NotImplemented`, Python tries `type(b).__radd__(b, a)`. This is how `3 * vector` and `sum()` (which starts at `0 + x`) work.

Q2: What is `NotImplemented` and how is it different from `NotImplementedError`?
A2: `NotImplemented` is a special value returned from binary dunder methods to say "I don't know this type"; Python then tries the other side. `NotImplementedError` is an exception raised from abstract-like methods.

Q3: What happens to `__hash__` when you define `__eq__`?
A3: Python sets `__hash__ = None`, making instances unhashable (cannot be dict keys or set members) unless you define `__hash__`. Frozen dataclasses generate both.

Q4: How do you get all comparison operators cheaply?
A4: Use `functools.total_ordering` with `__eq__` and one of `<`, `<=`, `>`, `>=`, or a dataclass with `order=True`.

Q5: Can you overload `and`, `or`, `not`?
A5: Not `and`/`or` (they short-circuit and cannot be hooked). `not` uses `__bool__`/`__len__`. You can overload bitwise `&`, `|`, `~` instead (NumPy and pandas do this for boolean masks).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Math-like types (money, vectors, durations, matrices)
- Query builders and DSLs (`Column > 5`)
- The operator meaning is obvious to every reader

❌ Avoid when:
- The meaning is unclear (`user1 + user2`?)
- A named method is more readable (`cart.add_item(x)`)
- You would break expected rules (`==` that is not symmetric)

---

## 📊 Visual Diagram
```
   a + b
     |
     v
 type(a).__add__(a, b) --returns value--> done
     |
     +--returns NotImplemented-->  type(b).__radd__(b, a) --value--> done
                                          |
                                          +--NotImplemented--> TypeError

   a += b :  __iadd__ ?  yes -> use it (may mutate)
                         no  -> a = a + b
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Operator overloading | Custom meaning for operators | Operators का अपना अर्थ |
| Dunder method | `__name__` special method | Double underscore वाला method |
| Reflected method | `__radd__`: right operand's turn | दाएं operand की बारी वाला method |
| NotImplemented | Signal: "try the other side" | "दूसरी तरफ आज़माओ" का संकेत |
| In-place operator | `+=` that may mutate | जगह पर बदलने वाला operator |
| total_ordering | Decorator filling comparison methods | बाकी comparisons भरने वाला decorator |

---

## ⚡ 3-Line Summary
English: Operator overloading lets `a + b`, `a == b`, `a < b` work on your classes through dunder methods. Return `NotImplemented` for unsupported types, define `__hash__` with `__eq__`, and return new objects. Use it only when the meaning is obvious.
Hindi: Operator overloading से आपकी classes पर `a + b`, `a == b`, `a < b` dunder methods के ज़रिए चलते हैं। Unsupported types पर `NotImplemented` लौटाएं, `__eq__` के साथ `__hash__` भी रखें, और नया object लौटाएं। इसे तभी इस्तेमाल करें जब अर्थ साफ हो।

---

## ➡️ Next Topic
**103. `__str__` vs `__repr__`** — two ways to show an object as text: one for users, one for developers. (Topic 102, Magic Methods, is already covered.)
