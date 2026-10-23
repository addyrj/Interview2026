---

# 102. Magic Methods (Dunder Methods) — Complete Guide
# हिंदी में: Magic Methods (Dunder Methods) — पूरी Guide

---

## 🔵 Simple Definition (English)
Magic methods (also called dunder methods — double underscore) are special methods like `__init__`, `__str__`, `__len__` that Python calls automatically in specific situations. They let your classes work with Python's built-in operators and functions — `len(obj)`, `obj + obj`, `str(obj)`, `with obj`, `obj[key]`.

## 🔵 सरल परिभाषा (Hindi)
Magic methods (dunder methods — double underscore) special methods हैं जैसे `__init__`, `__str__`, `__len__` जिन्हें Python specific situations में automatically call करता है। ये आपकी class को Python के built-in operators और functions के साथ काम करने देते हैं।

---

## 🔴 Problem it Solves
Without magic methods: you can't use `+` to add two Money objects, can't use `len()` on your custom collection, can't print objects meaningfully, can't use `with` statement for resource management. Magic methods make your classes first-class Python citizens.

## 🔴 यह क्यों बना? (Hindi)
Magic methods के बिना: दो Money objects को `+` से add नहीं कर सकते, custom collection पर `len()` नहीं चला सकते, objects को meaningfully print नहीं कर सकते। Magic methods आपकी class को Python का proper part बनाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You perform an operation: obj + other, len(obj), str(obj)
Step 2 → Python looks for the corresponding dunder method: __add__, __len__, __str__
Step 3 → Python calls your class's dunder method automatically
Step 4 → Your method performs the operation and returns the result
Step 5 → If dunder method not found → Python raises TypeError/AttributeError
```

---

## 🟡 Real World Example
A Money class at Razorpay: `payment1 + payment2` should add amounts, `str(payment)` should show "₹500.00", `payment1 == payment2` should compare amounts, `payment1 < payment2` should compare for sorting, `len(cart)` should count items.

---

## 💻 Code Example — Basic
```python
# Basic dunder methods — the most essential ones
class Product:
    def __init__(self, name: str, price: float, stock: int) -> None:
        self.name = name            # __init__: called on creation
        self.price = price
        self.stock = stock

    def __str__(self) -> str:
        """Called by str(), print() — human readable."""
        return f"{self.name} - ₹{self.price:.2f}"

    def __repr__(self) -> str:
        """Called by repr(), REPL — developer readable (should be unambiguous)."""
        return f"Product(name={self.name!r}, price={self.price}, stock={self.stock})"

    def __len__(self) -> int:
        """Called by len() — return stock count."""
        return self.stock

    def __bool__(self) -> bool:
        """Called by bool(), if statements — True if in stock."""
        return self.stock > 0

    def __eq__(self, other: object) -> bool:
        """Called by == operator."""
        if not isinstance(other, Product):
            return NotImplemented       # let Python handle, don't raise
        return self.name == other.name and self.price == other.price

p = Product("iPhone", 79999, 5)
print(p)                    # iPhone - ₹79999.00  (calls __str__)
print(repr(p))              # Product(name='iPhone', price=79999, stock=5) (calls __repr__)
print(len(p))               # 5  (calls __len__)
print(bool(p))              # True (calls __bool__)
if p:                       # calls __bool__ → True
    print("In stock!")
```

## 💻 Code Example — Advanced
```python
# Production: Money class with full operator support
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import functools

@functools.total_ordering    # auto-generates __le__, __gt__, __ge__ from __lt__ + __eq__
@dataclass(eq=False)         # eq=False: we define our own __eq__
class Money:
    amount: float
    currency: str = "INR"

    def __post_init__(self) -> None:
        """Called after __init__ in dataclass — for validation."""
        if self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")
        self.amount = round(self.amount, 2)  # round to 2 decimal places

    def __str__(self) -> str:
        symbol = {"INR": "₹", "USD": "$", "EUR": "€"}.get(self.currency, "")
        return f"{symbol}{self.amount:,.2f}"

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency={self.currency!r})"

    def __add__(self, other: Money) -> Money:
        """Called by m1 + m2."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        """Called by m1 - m2."""
        if self.currency != other.currency:
            raise ValueError(f"Currency mismatch")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: float) -> Money:
        """Called by money * 1.18 (for tax)."""
        return Money(self.amount * factor, self.currency)

    def __rmul__(self, factor: float) -> Money:
        """Called by 1.18 * money (reversed operands)."""
        return self.__mul__(factor)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __lt__(self, other: Money) -> bool:
        """Called by m1 < m2. With @total_ordering, also generates <=, >, >=."""
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount

    def __hash__(self) -> int:
        """Required when defining __eq__! Makes Money usable in sets/dict keys."""
        return hash((self.amount, self.currency))

# Custom container — implements sequence protocol:
class Cart:
    def __init__(self) -> None:
        self._items: list[Product] = []

    def __len__(self) -> int:
        return len(self._items)              # len(cart)

    def __getitem__(self, index: int) -> Product:
        return self._items[index]            # cart[0], cart[1:3]

    def __setitem__(self, index: int, value: Product) -> None:
        self._items[index] = value           # cart[0] = new_product

    def __delitem__(self, index: int) -> None:
        del self._items[index]               # del cart[0]

    def __contains__(self, item: Product) -> bool:
        return item in self._items           # product in cart

    def __iter__(self):
        return iter(self._items)             # for product in cart:

    def __repr__(self) -> str:
        return f"Cart({len(self)} items)"

    def __enter__(self) -> Cart:
        """Called when entering 'with cart:' — return self to use as context var."""
        print("Starting checkout...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Called when exiting 'with cart:' — cleanup."""
        if exc_type is None:
            print("Checkout complete!")
        else:
            print(f"Checkout failed: {exc_val}")
        return False   # False = don't suppress exceptions

# Usage:
price = Money(100, "INR")
tax = price * 1.18            # calls __mul__  → ₹118.00
total = price + Money(50)     # calls __add__  → ₹150.00
print(price < Money(200))     # calls __lt__   → True

cart = Cart()
with cart:                    # calls __enter__
    print(len(cart))          # calls __len__
# calls __exit__ on block end
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: operator overloading via dunder methods
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)      # Vector(4, 6) ← calls __add__ automatically
```

```javascript
// JavaScript: NO operator overloading!
class Vector {
    constructor(x, y) { this.x = x; this.y = y; }
    
    add(other) {           // must call .add() explicitly
        return new Vector(this.x + other.x, this.y + other.y);
    }
    
    toString() {           // JavaScript's equivalent to __str__
        return `Vector(${this.x}, ${this.y})`;
    }
}

const v1 = new Vector(1, 2);
const v2 = new Vector(3, 4);
console.log(v1.add(v2).toString());  // must call method — can't use +
// v1 + v2 would do string concatenation: "[object Object][object Object]"
```

---

## 🟠 FastAPI Connection

```python
# Pydantic models (used everywhere in FastAPI) use __init__, __eq__, __repr__
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # Pydantic auto-generates __init__, __repr__, __eq__, __hash__
    # (plus validation in __init__, JSON serialization from __dict__)

# Custom response objects with __str__ for logging:
class APIError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(message)

    def __str__(self) -> str:
        return f"APIError({self.code}): {self.message}"

    def __repr__(self) -> str:
        return f"APIError(code={self.code!r}, message={self.message!r}, status={self.status})"

# Context manager for DB transaction (uses __enter__/__exit__):
from sqlalchemy.ext.asyncio import AsyncSession

class DBTransaction:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):       # async context manager!
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        return False

# Usage in FastAPI route:
async def create_user(user_data: dict, db: AsyncSession):
    async with DBTransaction(db) as session:
        user = User(**user_data)
        session.add(user)
        # __aexit__ commits on success, rolls back on exception
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Defining `__eq__` without `__hash__`
```python
# Wrong — objects become unhashable (can't put in sets/dict keys)!
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    # No __hash__! Python sets __hash__ = None automatically
    
p = Point(1, 2)
s = {p}    # TypeError: unhashable type: 'Point'

# Correct — define __hash__ when you define __eq__:
class Point:
    def __eq__(self, other): ...
    def __hash__(self):
        return hash((self.x, self.y))  # hash based on the same fields as __eq__
```

❌ Mistake 2: Returning wrong types from comparison methods
```python
# Wrong — __eq__ should return bool or NotImplemented (not raise)
def __eq__(self, other):
    if not isinstance(other, MyClass):
        raise TypeError("Can't compare!")   # ← wrong! Break Python's comparison protocol

# Correct — return NotImplemented to let Python try the reverse:
def __eq__(self, other):
    if not isinstance(other, MyClass):
        return NotImplemented   # Python will try other.__eq__(self)
    return self.value == other.value
```

---

## 🧠 Tricky Interview Question

```python
class Weird:
    def __init__(self, val):
        self.val = val

    def __bool__(self):
        return False        # always False!

    def __len__(self):
        return 42

w = Weird(10)
print(bool(w))          # A
print(len(w))           # B

class NoLen:
    def __init__(self):
        pass

    def __len__(self):
        return 0

n = NoLen()
print(bool(n))          # C
```
Answer:
- A: `False` — `__bool__` defined, returns `False`
- B: `42` — `__len__` returns 42
- C: `False` — no `__bool__`, Python falls back to `__len__`. `len() == 0` → `False`

Priority: `__bool__` takes precedence over `__len__` for truthiness. If neither defined, objects are always `True`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `__str__` and `__repr__`?
A1: `__str__`: human-readable, called by `print()` and `str()`. Should be concise and user-friendly: `"₹500.00"`. `__repr__`: developer-readable, called by `repr()` and in the REPL. Should be unambiguous and ideally recreatable: `"Money(amount=500.0, currency='INR')"`. Rule: if only one is defined, `__str__` falls back to `__repr__`. `__repr__` should look like valid Python that recreates the object.

Q2: What is `__slots__` and why use it?
A2: `__slots__ = ['x', 'y']` tells Python NOT to create a `__dict__` for instances — instead use a fixed C array. Benefits: ~30-50% less memory per instance (no dict overhead), slightly faster attribute access. Downside: can't add new attributes dynamically, can't use `__dict__`. Use for classes with many instances (data records, nodes in data structures).

Q3: What is `__call__` and when would you use it?
A3: `__call__` makes an instance callable like a function: `instance()`. Use cases: callable classes that maintain state (like a partial function), function factories, mock objects, classes that act as decorators. Example: `class Multiplier: def __init__(self, factor): self.factor = factor; def __call__(self, n): return n * self.factor` → `double = Multiplier(2); double(5)  # 10`.

Q4: What does `__enter__` and `__exit__` enable?
A4: They implement the context manager protocol — used with `with` statements. `__enter__` runs on block entry and its return value is assigned to `as` variable. `__exit__` runs on block exit with `(exc_type, exc_val, exc_tb)`. Return `True` to suppress exceptions, `False` (or `None`) to propagate them. Used for: file handling, DB transactions, locks, temporary state changes.

Q5: What is `__new__` vs `__init__`?
A5: `__new__` creates the instance (allocates memory, returns the new object). `__init__` initializes it (sets attributes). `__new__` is called first. Most classes only need `__init__`. Override `__new__` for: Singleton pattern, immutable types (subclassing `int`, `str`, `tuple`), controlling instance creation (caching, pooling). `__new__(cls, ...)` must return an instance of `cls`.

---

## 🔷 When to Use + When Not to Use

✅ Use magic methods when:
- You want `+`, `-`, `*` to work on your objects
- You want `len()`, `bool()`, `str()` to work naturally
- Building collection classes (list-like, dict-like)
- Building context managers (`with` statement)
- Making objects iterable (`for x in obj`)
- Making objects callable (`obj()`)

❌ Avoid when:
- The operation isn't natural for the type (don't make `+` do subtraction)
- Just wanting to add a method — use a regular method name instead
- Overcomplicating simple data classes (just use `@dataclass`)

---

## 📊 Visual Diagram
```
Python operator → Dunder method called
─────────────────────────────────────
str(obj)        → __str__
repr(obj)       → __repr__
len(obj)        → __len__
bool(obj)       → __bool__ (then __len__ as fallback)
obj + other     → __add__ (or other.__radd__)
obj - other     → __sub__
obj * other     → __mul__
obj == other    → __eq__
obj < other     → __lt__
obj[key]        → __getitem__
obj[key] = val  → __setitem__
del obj[key]    → __delitem__
item in obj     → __contains__
for x in obj    → __iter__
with obj as x   → __enter__ / __exit__
obj()           → __call__
hash(obj)       → __hash__
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dunder method | Double underscore method (__X__) | Double underscore वाली method |
| Operator overloading | Custom behavior for operators | Operators को custom behavior देना |
| Context manager | Object that works with `with` | `with` के साथ काम करने वाला object |
| NotImplemented | Singleton to decline an operation | Operation decline करने का signal |
| __hash__ | Makes object usable in sets/dicts | Object को hashable बनाता है |
| total_ordering | Decorator generating comparison methods | Comparison methods auto-generate |

---

## ⚡ 3-Line Summary
English: Magic methods let your classes integrate seamlessly with Python's syntax — `+`, `len()`, `str()`, `with`, `for`. Always define `__repr__` as a minimum; add `__hash__` whenever you define `__eq__`. Return `NotImplemented` (not raise) from comparison methods when types don't match.
Hindi: Magic methods आपकी class को Python syntax के साथ integrate करते हैं। `__repr__` minimum define करो; `__eq__` define करो तो `__hash__` भी। Comparison methods में type mismatch पर `NotImplemented` return करो।

---

## ➡️ Next Topic
**103. `__str__` vs `__repr__`** — deep dive, logging implications, then **104. `__len__`, `__getitem__`, `__setitem__`** — building sequence and mapping protocols.
