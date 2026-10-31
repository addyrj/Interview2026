---

# 057. Named Tuple
# हिंदी में: Named Tuple (नाम वाला Tuple)

---

## 🔵 Simple Definition (English)
A named tuple is a tuple whose positions have names. Instead of `point[0]` you write `point.x`. It stays immutable, lightweight and unpackable like a normal tuple, but your code becomes self-explaining. Python gives two ways: `collections.namedtuple` and the typed `typing.NamedTuple` class.

## 🔵 सरल परिभाषा (Hindi)
Named tuple वह tuple है जिसके हर position का नाम होता है। `point[0]` की जगह `point.x` लिखते हैं। यह फिर भी immutable और हल्का रहता है, और code खुद समझ आता है। Python में दो तरीके हैं: `collections.namedtuple` और typed `typing.NamedTuple` class।

---

## 🔴 Problem it Solves
With plain tuples, `row[2]` means nothing: is it price, age or quantity? Readers must guess, and a changed column order silently breaks code. A full class solves readability but needs `__init__`, `__repr__`, `__eq__` and uses more memory. Named tuples give names + immutability + a free `__repr__` with almost zero cost.

## 🔴 यह क्यों बना? (Hindi)
Plain tuple में `row[2]` का मतलब पता नहीं — price है या age? Column order बदले तो code चुपचाप टूट जाता है। Full class में boilerplate और ज़्यादा memory लगती है। Named tuple: नाम + immutability + auto `__repr__`, लगभग बिना cost के।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Point = namedtuple("Point", ["x", "y"])   → Python builds a new tuple SUBCLASS called Point
Step 2 → p = Point(1, 2)                           → creates a tuple (1, 2) with field names x, y
Step 3 → p.x                                       → property that reads index 0 of the tuple
Step 4 → p[0], x, y = p                            → still works as a normal tuple
Step 5 → p.x = 5                                   → AttributeError (immutable)
Step 6 → p._replace(x=5)                           → returns a NEW named tuple, original unchanged
```

## 🟢 कैसे काम करता है? (Hindi)
```
namedtuple("Point", ["x","y"]) → tuple की नई subclass बनती है
p.x → असल में index 0 पढ़ता है
p[0] और unpacking भी चलते हैं (tuple ही है)
p.x = 5 → error, immutable
p._replace(x=5) → नया object देता है, पुराना वैसा ही
```

---

## 🟡 Real World Example
Razorpay: a payment record `Payment(id, amount, currency)` read from a CSV or DB row. Using a named tuple, `payment.amount` is clear and the record cannot be changed by accident. In a FastAPI service, raw SQLAlchemy rows are named-tuple-like (`row.email`), and `NamedTuple` classes are used for light internal records that do not need Pydantic validation.

## 🟡 Real Example Hindi mein
Razorpay में payment record `Payment(id, amount, currency)` CSV या DB row से आता है। Named tuple से `payment.amount` साफ़ है और record गलती से बदलता नहीं। FastAPI में SQLAlchemy की rows named-tuple जैसी हैं (`row.email`), और बिना validation वाले हल्के internal records के लिए `NamedTuple` काम आता है।

---

## 💻 Code Example — Basic
```python
# Basic: create and use a namedtuple
from collections import namedtuple           # factory for named tuples

Point = namedtuple("Point", ["x", "y"])      # class named Point with fields x and y
p: Point = Point(3, 4)                       # create an instance (positional)
q: Point = Point(x=1, y=2)                   # create using keywords

print(p)                                     # Output: Point(x=3, y=4)
print(p.x, p.y)                              # Output: 3 4   (access by name)
print(p[0], p[1])                            # Output: 3 4   (access by index)

x, y = p                                     # unpack like a normal tuple
print(x + y)                                 # Output: 7

print(isinstance(p, tuple))                  # Output: True  (it IS a tuple)
print(p == (3, 4))                           # Output: True  (compares equal to plain tuple)

try:                                         # namedtuple is immutable
    p.x = 10                                 # type: ignore  attempt to change
except AttributeError as err:                # expected error
    print("Error:", err)                     # Output: Error: can't set attribute

p2: Point = p._replace(x=10)                 # make a modified COPY
print(p, p2)                                 # Output: Point(x=3, y=4) Point(x=10, y=4)

print(p._asdict())                           # Output: {'x': 3, 'y': 4}
print(Point._fields)                         # Output: ('x', 'y')

d: dict[str, int] = {"x": 7, "y": 8}         # data from a dict (e.g. JSON)
print(Point(**d))                            # Output: Point(x=7, y=8)
```

## 💻 Code Example — Advanced
```python
# Advanced: typing.NamedTuple with defaults, methods and a CSV-like pipeline
from __future__ import annotations           # modern hint syntax
from typing import NamedTuple                # typed named tuple (class syntax)


class Payment(NamedTuple):                   # fields are class annotations
    """Immutable payment record."""
    id: int                                  # required field
    amount: float                            # required field
    currency: str = "INR"                    # field with default value

    def with_tax(self, rate: float = 0.18) -> float:
        """Return amount including tax (methods are allowed)."""
        return round(self.amount * (1 + rate), 2)   # compute using fields

    @property
    def is_large(self) -> bool:
        """True when amount is above 10000."""
        return self.amount > 10_000          # simple business rule


def parse_row(row: str) -> Payment:
    """Convert 'id,amount[,currency]' text into a Payment."""
    parts: list[str] = row.strip().split(",")        # split CSV text
    if len(parts) < 2:                               # validate minimum fields
        raise ValueError(f"Bad row: {row!r}")        # clear error message
    pid, amount, *rest = parts                       # star-unpack optional tail
    return Payment(int(pid), float(amount), *rest)   # rest fills currency if present


rows: list[str] = ["1,500", "2,25000,USD", "3,9999.5"]   # sample input
payments: list[Payment] = [parse_row(r) for r in rows]   # parse all rows
for pay in payments:                                     # show each
    print(pay, pay.with_tax(), pay.is_large)

# Sorting and max work with field names via key=
biggest: Payment = max(payments, key=lambda p: p.amount)   # find largest payment
print("Biggest:", biggest.id)                              # Output: Biggest: 2

# Field metadata and defaults
print(Payment._fields)                       # Output: ('id', 'amount', 'currency')
print(Payment._field_defaults)               # Output: {'currency': 'INR'}

# Make a namedtuple from an iterable (e.g. database row)
db_row: tuple[int, float, str] = (9, 100.0, "EUR")   # raw tuple from DB
print(Payment._make(db_row))                          # Output: Payment(id=9, amount=100.0, currency='EUR')

# Error handling for bad input
try:                                         # invalid row
    parse_row("only-one-field")              # missing amount
except ValueError as err:                    # handle it
    print("Error:", err)                     # Output: Error: Bad row: 'only-one-field'
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from typing import NamedTuple

class User(NamedTuple):              # fields + types in one place
    name: str
    age: int

u = User("Priya", 25)
print(u.name, u[1])                  # by name or by index
name, age = u                        # unpack
# u.age = 26  -> AttributeError (immutable)
```

```javascript
// JavaScript
const user = Object.freeze({ name: "Priya", age: 25 }); // frozen object
console.log(user.name);               // by name only (no index access)
const { name, age } = user;           // destructuring by NAME
user.age = 26;                        // silently ignored (or TypeError in strict mode)
```

Key difference: a JS object is unordered-by-position and has no index access; a Python named tuple is BOTH a tuple (index, unpack by position, hashable) and a record (names). FastAPI link: for request/response data use Pydantic models (validation + JSON); use `NamedTuple` for fast internal records.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Trying to modify a field
```python
# Wrong:
# p.x = 10                  # AttributeError: can't set attribute
# Correct:
# p = p._replace(x=10)      # create a new object and rebind the name
```

❌ Mistake 2: Mutable default in a NamedTuple
```python
# Wrong (shared mutable default, same list for every instance):
# class Cart(NamedTuple):
#     items: list = []
# Correct: make it required, or use a tuple / None
# class Cart(NamedTuple):
#     items: tuple = ()
```

❌ Mistake 3: Expecting validation like Pydantic
```python
# Wrong assumption:
# Payment("abc", "xyz")     # NO error, types in NamedTuple are NOT enforced
# Correct: use Pydantic BaseModel when you need runtime validation
```

---

## 🧠 Tricky Interview Question

**Q**: "Are `Point(1, 2) == (1, 2)` and `Point(1, 2) == Vector(1, 2)` both True, if both are namedtuples with fields x, y?"

**Answer**: Both are True. A named tuple inherits tuple's `__eq__`, which compares only the values by position, not the class name or field names. So `Point(1, 2) == Vector(1, 2)` is `True` even though they are different types. This can create surprising bugs (a `Celsius(30)` equal to a `Fahrenheit(30)`). If types must matter, use a `@dataclass(frozen=True)`, which compares classes too.

---

## ⚫ Interview Questions + Answers

Q1: What is a namedtuple and why use it?
A1: A tuple subclass whose positions have names. It gives readable access (`p.x`), keeps tuple features (indexing, unpacking, immutability, hashability) and costs about the same memory as a tuple, much less than a normal class with `__dict__`. It is ideal for small read-only records returned from functions or parsed from files.

Q2: `collections.namedtuple` vs `typing.NamedTuple`?
A2: Both create the same kind of object. `namedtuple("P", ["x","y"])` is the older factory function, no type hints. `class P(NamedTuple): x: int` uses class syntax, supports type annotations, default values, docstrings and methods in a clean way. Prefer `typing.NamedTuple` in modern typed code.

Q3: namedtuple vs dataclass?
A3: namedtuple is immutable, indexable, unpackable, hashable and compares equal to plain tuples; it is lighter. A dataclass is a normal class: mutable by default (or `frozen=True`), no indexing, supports inheritance, `__post_init__`, `field(default_factory=...)`. Choose namedtuple for tiny immutable records; dataclass when you need behaviour or mutability.

Q4: How do you "change" a field of a namedtuple?
A4: You cannot change it in place. Use `p._replace(x=10)`, which returns a new instance with that field changed. Original stays the same. This is the same idea as `dataclasses.replace()` for frozen dataclasses.

Q5: How to convert a namedtuple to dict and back?
A5: `p._asdict()` gives a dict (ordered by field order). `Point(**d)` rebuilds from a dict. `Point._make(iterable)` rebuilds from any iterable. In FastAPI, you can return `p._asdict()` and it becomes a JSON object.

---

## 🔷 When to Use Named Tuple

✅ Use namedtuple when:
- You need a small immutable record
- You return several values from a function and want names
- You process CSV/DB rows
- You want memory-light objects in large lists

❌ Avoid when:
- You need validation (use Pydantic)
- Fields must change (use dataclass)
- You need inheritance with behaviour

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| namedtuple | Factory creating tuple subclass with names | नाम वाले tuple की subclass बनाने वाली function |
| Field | A named position | नाम वाला position |
| `_replace` | Return copy with changes | बदलाव के साथ नई copy |
| `_asdict` | Convert to dict | Dict में बदलना |
| `_make` | Build from iterable | Iterable से object बनाना |
| Record | Small group of related values | संबंधित values का छोटा समूह |

---

## ⚡ 3-Line Summary
English: A named tuple is an immutable tuple with named fields, so `p.x` replaces `p[0]`. Use `typing.NamedTuple` for typed records with defaults and methods; use `_replace` to get a modified copy. It is lightweight but does no validation, so use Pydantic for API data.
Hindi: Named tuple नाम वाले fields के साथ immutable tuple है, `p.x` = `p[0]`। Typed records के लिए `typing.NamedTuple`; बदलाव के लिए `_replace` से नई copy। हल्का है पर validation नहीं करता — API data के लिए Pydantic।

---

## ➡️ Next Topic
**059. Dictionary Methods** — `get`, `keys`, `values`, `items`, `update`, `pop`, `setdefault` with real usage.
