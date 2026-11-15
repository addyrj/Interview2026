---

# 109. Dataclasses
# हिंदी में: Dataclasses (Data रखने वाली Classes, कम code में)

---

## 🔵 Simple Definition (English)
`@dataclass` is a decorator from the `dataclasses` module. You list fields with type hints and Python writes `__init__`, `__repr__`, `__eq__` (and optionally ordering, hashing, immutability and slots) for you. It removes the boilerplate from classes that mainly hold data.

## 🔵 सरल परिभाषा (Hindi)
`@dataclass` `dataclasses` module का decorator है। आप type hints के साथ fields लिखते हो और Python आपके लिए `__init__`, `__repr__`, `__eq__` (और चाहें तो ordering, hashing, immutability और slots) लिख देता है। जो classes मुख्य रूप से data रखती हैं, उनका boilerplate खत्म हो जाता है।

---

## 🔴 Problem it Solves
A normal data class needs an `__init__` that copies every argument, a `__repr__` for debugging, and `__eq__` for comparisons. For 6 fields that is 20+ lines of repeated code, and it is easy to forget a field in `__eq__` or `__repr__`. Without `__repr__` you see `<Order object at 0x...>` in logs, which is useless. Dataclasses generate all of it correctly from one field list.

## 🔴 यह क्यों बना? (Hindi)
सामान्य data class में हर argument copy करने वाला `__init__`, debugging के लिए `__repr__` और comparison के लिए `__eq__` लिखना पड़ता है। 6 fields के लिए यह 20+ lines का दोहराया हुआ code है, और `__eq__` या `__repr__` में कोई field भूलना आसान है। `__repr__` न हो तो logs में `<Order object at 0x...>` दिखता है, जो बेकार है। Dataclass एक field list से सब सही-सही बना देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You write @dataclass above a class with annotated fields
Step 2 → Python reads class.__annotations__ in order
Step 3 → It generates __init__(self, f1, f2, ...) with defaults
Step 4 → It generates __repr__ and __eq__ (compares fields as tuples)
Step 5 → Options change the result:
         frozen=True  -> immutable + hashable
         order=True   -> <, >, <=, >= by field order
         slots=True   -> uses __slots__ (3.10+)
         kw_only=True -> all args keyword-only (3.10+)
Step 6 → Mutable defaults need field(default_factory=list)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → आप annotated fields वाली class के ऊपर @dataclass लिखते हो
Step 2 → Python class.__annotations__ को क्रम से पढ़ता है
Step 3 → वह defaults के साथ __init__(self, f1, f2, ...) बनाता है
Step 4 → वह __repr__ और __eq__ बनाता है (fields को tuple की तरह compare करता है)
Step 5 → Options नतीजा बदलते हैं:
         frozen=True  -> immutable + hashable
         order=True   -> field क्रम से <, >, <=, >=
         slots=True   -> __slots__ use होता है (3.10+)
         kw_only=True -> सारे args keyword-only (3.10+)
Step 6 → Mutable defaults के लिए field(default_factory=list) चाहिए
```

---

## 🟡 Real World Example
Swiggy order service: `Order(id, user_id, items, total, status)` is a dataclass passed between the cart, payment and delivery modules. A `frozen=True` `Money(amount, currency)` is used as a dict key. Config objects (`DBConfig(host, port, user)`) loaded from environment variables are dataclasses. In ML code, `TrainConfig(lr, epochs, batch_size)` stores hyper-parameters and prints neatly in experiment logs.

## 🟡 Real Example Hindi mein
Swiggy order service में `Order(id, user_id, items, total, status)` dataclass है जो cart, payment और delivery modules के बीच जाती है। `frozen=True` वाली `Money(amount, currency)` dict key की तरह use होती है। Environment variables से load होने वाले config objects (`DBConfig(host, port, user)`) dataclass होते हैं। ML code में `TrainConfig(lr, epochs, batch_size)` hyper-parameters रखती है और experiment logs में साफ print होती है।

---

## 💻 Code Example — Basic
```python
# Basic dataclass examples
from dataclasses import dataclass, field, asdict, astuple, replace   # the toolbox


@dataclass                                        # generates __init__, __repr__, __eq__
class Product:
    name: str                                     # required field
    price: float                                  # required field
    tags: list[str] = field(default_factory=list) # mutable default must use default_factory
    in_stock: bool = True                         # simple default


p: Product = Product("Laptop", 55000.0)           # create with positional args
print(p)                                          # automatic __repr__
print(p == Product("Laptop", 55000.0))            # __eq__ compares all fields -> True
print(p is Product("Laptop", 55000.0))            # different objects -> False

p.tags.append("electronics")                      # each object has its own list
print(Product("Pen", 10.0).tags)                  # [] (not shared)

print(asdict(p))                                  # convert to dict (recursively)
print(astuple(p))                                 # convert to tuple
cheaper: Product = replace(p, price=49999.0)      # copy with one field changed
print(cheaper.price, p.price)                     # original is unchanged


@dataclass(frozen=True, order=True)               # immutable, sortable, hashable
class Version:
    major: int                                    # compared first
    minor: int                                    # compared second


v1, v2 = Version(1, 2), Version(1, 10)            # two versions
print(v1 < v2, sorted([v2, v1]))                  # ordering by (major, minor)
try:                                              # frozen blocks assignment
    v1.major = 5                                  # not allowed
except Exception as e:                            # FrozenInstanceError
    print(type(e).__name__)                       # name of the error
print({v1: "stable"}[Version(1, 2)])              # hashable, so it works as a dict key

# Output:
# Product(name='Laptop', price=55000.0, tags=[], in_stock=True)
# True
# False
# []
# {'name': 'Laptop', 'price': 55000.0, 'tags': ['electronics'], 'in_stock': True}
# ('Laptop', 55000.0, ['electronics'], True)
# 49999.0 55000.0
# True [Version(major=1, minor=2), Version(major=1, minor=10)]
# FrozenInstanceError
# stable
```

## 💻 Code Example — Advanced
```python
# Production style: validation, computed fields, InitVar, kw_only, slots, inheritance
from dataclasses import dataclass, field, InitVar   # advanced helpers
from datetime import datetime, timezone             # timestamps


@dataclass(slots=True, kw_only=True)                # memory-light, keyword-only (3.10+)
class OrderItem:
    sku: str                                        # product code
    qty: int                                        # quantity
    unit_price: float                               # price of one unit

    def __post_init__(self) -> None:                # runs right after __init__
        if self.qty <= 0:                           # business rule
            raise ValueError(f"qty must be positive, got {self.qty}")
        if self.unit_price < 0:                     # business rule
            raise ValueError("unit_price cannot be negative")

    @property
    def line_total(self) -> float:                  # computed value, not a stored field
        return round(self.qty * self.unit_price, 2) # rounded to paise


@dataclass(kw_only=True)                            # keyword-only avoids argument mix-ups
class Order:
    order_id: int                                   # unique id
    items: list[OrderItem] = field(default_factory=list)   # own list per order
    coupon: InitVar[str | None] = None              # used only in __init__, not stored
    discount: float = field(default=0.0, init=False)       # computed, not passed in
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), repr=False)
    status: str = field(default="NEW", compare=False)      # ignored by ==

    def __post_init__(self, coupon: str | None) -> None:   # InitVar arrives here
        if coupon == "SAVE10":                      # simple coupon rule
            self.discount = 0.10                    # 10 percent

    @property
    def total(self) -> float:                       # final payable amount
        gross: float = sum(i.line_total for i in self.items)   # sum of lines
        return round(gross * (1 - self.discount), 2)           # apply discount


@dataclass(kw_only=True)                            # inheritance works like normal classes
class ExpressOrder(Order):
    fee: float = 49.0                               # extra field with a default

    @property
    def total(self) -> float:                       # override the parent property
        return round(super().total + self.fee, 2)   # add delivery fee


order: Order = Order(order_id=1, coupon="SAVE10")   # coupon is an InitVar
order.items.append(OrderItem(sku="A1", qty=2, unit_price=250.0))   # add a line
order.items.append(OrderItem(sku="B2", qty=1, unit_price=99.5))    # add another line
print(order.total)                                  # (500 + 99.5) * 0.9
print(order)                                        # created_at hidden by repr=False
print("coupon" in vars(order))                      # InitVar value is not stored -> False
print(ExpressOrder(order_id=2, items=order.items).total)   # 599.5 + 49

try:                                                # validation in __post_init__
    OrderItem(sku="X", qty=0, unit_price=10.0)      # invalid quantity
except ValueError as e:                             # catch it
    print("Error:", e)                              # Error: qty must be positive, got 0

try:                                                # kw_only blocks positional use
    OrderItem("X", 1, 10.0)                         # type: ignore  - wrong style
except TypeError as e:                              # catch it
    print("TypeError:", "positional" in str(e))     # True

# Output:
# 539.55
# Order(order_id=1, items=[OrderItem(sku='A1', qty=2, unit_price=250.0), OrderItem(sku='B2', qty=1, unit_price=99.5)], discount=0.1, status='NEW')
# False
# 648.5
# Error: qty must be positive, got 0
# TypeError: True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Data class | `@dataclass` | plain `class` / object literal / TypeScript `interface` |
| Auto constructor | generated | hand-written (or TS parameter properties) |
| Auto equality | `==` compares fields | `===` compares references; need lodash `isEqual` |
| Pretty print | automatic `__repr__` | `console.log` prints object; `JSON.stringify` |
| Immutable | `frozen=True` | `Object.freeze` |
| Copy with change | `replace(obj, x=1)` | `{...obj, x: 1}` |

```python
# Python way
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Point:
    x: int                                    # field
    y: int                                    # field

a: Point = Point(1, 2)
b: Point = replace(a, y=5)                    # copy with change
print(a == Point(1, 2), b)                    # True Point(x=1, y=5)
```
```javascript
// JavaScript way
class Point {
  constructor(x, y) { this.x = x; this.y = y; Object.freeze(this); }  // manual constructor
}
const a = new Point(1, 2);
const b = { ...a, y: 5 };                    // spread copy (loses the class!)
console.log(a === new Point(1, 2));          // false - compares references
console.log(JSON.stringify(a) === JSON.stringify(new Point(1, 2)));  // true (hack)
```

Key difference: Python generates value-based equality and a readable repr for free. In JS you compare references, so you write helpers or use libraries.

---

## 🟠 FastAPI Connection
FastAPI accepts dataclasses as request/response models (it wraps them with Pydantic validation). For internal domain objects, plain dataclasses are lighter than Pydantic models. A common design: Pydantic at the API border (validate untrusted input), dataclass inside the service layer (trusted data).

```python
# FastAPI example - dataclass as body and response model
from dataclasses import dataclass                 # dataclass decorator
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # testing


@dataclass                                        # FastAPI validates dataclasses too
class Item:
    name: str                                     # required
    price: float                                  # required, validated as float
    in_stock: bool = True                         # default


app: FastAPI = FastAPI()                          # create app


@app.post("/items", response_model=Item)          # input and output are the dataclass
def create_item(item: Item) -> Item:
    return item                                   # FastAPI serializes it to JSON


client: TestClient = TestClient(app)              # test client
print(client.post("/items", json={"name": "Pen", "price": "12.5"}).json())   # "12.5" coerced
print(client.post("/items", json={"name": "Pen"}).status_code)               # missing price

# Output:
# {'name': 'Pen', 'price': 12.5, 'in_stock': True}
# 422
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Mutable default value (list/dict/set)
✅ Correct: use `field(default_factory=...)`

```python
from dataclasses import dataclass, field
# Wrong - dataclass refuses it at class creation
try:
    @dataclass
    class A:
        items: list[int] = []
except ValueError as e:
    print(e)        # mutable default <class 'list'> for field items is not allowed: use default_factory
# Right
@dataclass
class B:
    items: list[int] = field(default_factory=list)
print(B().items)    # []
```

❌ Mistake 2: Non-default field after a default field
✅ Correct: put required fields first, or use `kw_only=True`

```python
from dataclasses import dataclass
# Wrong
try:
    @dataclass
    class A:
        x: int = 1
        y: int
except TypeError as e:
    print(e)        # non-default argument 'y' follows default argument 'x'
# Right
@dataclass(kw_only=True)
class B:
    x: int = 1
    y: int
print(B(y=2))       # B(x=1, y=2)
```

❌ Mistake 3: `order=True` / `frozen` surprises - mutable dataclass is unhashable
✅ Correct: use `frozen=True` (or `unsafe_hash=True` carefully) when you need dict keys or set members

```python
from dataclasses import dataclass
@dataclass
class A:
    x: int
# Wrong
try:
    {A(1): "v"}
except TypeError as e:
    print(e)        # unhashable type: 'A'
# Right
@dataclass(frozen=True)
class B:
    x: int
print({B(1): "v"})  # {B(x=1): 'v'}
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from dataclasses import dataclass

@dataclass
class P:
    x: int
    y = 5            # no annotation!

a = P(1)
b = P(1)
P.y = 10
print(a == b, a.y, P.__dataclass_fields__.keys())
try:
    P(1, 2)
except TypeError as e:
    print("TypeError")
```
Answer: `True 10 dict_keys(['x'])` then `TypeError`. A dataclass field exists only when the class attribute has an annotation. `y = 5` is a plain class variable, so it is not a field: not in `__init__`, `__repr__` or `__eq__`. Changing `P.y` changes it for every instance (`a.y` is 10). That is why `P(1, 2)` raises TypeError (only one init argument). Use `ClassVar` annotation to make the intent explicit.

---

## ⚫ Interview Questions + Answers

Q1: What does `@dataclass` generate?
A1: `__init__`, `__repr__` and `__eq__` by default. With options: `__lt__` etc. (`order=True`), `__hash__` (`frozen=True` or `unsafe_hash=True`), `__slots__` (`slots=True`), keyword-only init (`kw_only=True`), and `__match_args__` for pattern matching.

Q2: Why do mutable defaults need `default_factory`?
A2: A default like `[]` would be one shared list for all instances, the classic Python bug. Dataclasses detect list, dict and set defaults and raise ValueError. `default_factory=list` calls `list()` for each new object.

Q3: What is `__post_init__` and `InitVar`?
A3: `__post_init__` runs after the generated `__init__`: use it for validation or computed fields. `InitVar[T]` is a pseudo-field passed to `__init__` and `__post_init__` but not stored as an attribute.

Q4: Dataclass vs NamedTuple vs Pydantic?
A4: Dataclass: mutable by default, no runtime validation, flexible. NamedTuple: immutable, tuple-like, unpackable. Pydantic: validates and coerces types, parses JSON, but heavier. Use dataclass for trusted internal data, Pydantic at the boundary.

Q5: How does `frozen=True` affect equality and hashing?
A5: With `eq=True, frozen=True` Python generates `__hash__` from the fields, so instances are hashable and safe as dict keys. With `eq=True` and not frozen, `__hash__` is set to None (unhashable). Frozen is shallow: a list inside can still be modified.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A class mainly stores data (configs, DTOs, events, domain objects)
- You want readable logs and value-based equality
- You need immutability (`frozen=True`) or sorting (`order=True`)

❌ Avoid when:
- You must validate or coerce untrusted input - use Pydantic
- You need a tuple-like, unpackable record - use `NamedTuple`
- The class is mostly behavior with little data
- You need dynamic fields (use a dict)

---

## 📊 Visual Diagram
```
@dataclass
class Order:                       Python generates
    id: int                 --->   __init__(self, id, items=...)
    items: list[...]               __repr__  -> "Order(id=1, ...)"
                                   __eq__    -> (id, items) == (id, items)
Options:
  frozen=True -> immutable + __hash__      order=True -> <  >  <=  >=
  slots=True  -> __slots__ (less memory)   kw_only=True -> Order(id=1)

__init__ flow:  fields assigned -> __post_init__(InitVars) -> object ready
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dataclass | Class with auto-generated methods | auto-generated methods वाली class |
| Field | Annotated attribute that becomes a parameter | annotated attribute जो parameter बनता है |
| `default_factory` | Function that makes a fresh default | हर बार नया default बनाने वाला function |
| `__post_init__` | Hook after `__init__` | `__init__` के बाद का hook |
| `frozen` | Instances cannot be changed | instance बदला नहीं जा सकता |
| `InitVar` | Init-only pseudo field | सिर्फ init में काम आने वाला field |

---

## ⚡ 3-Line Summary
English: `@dataclass` writes `__init__`, `__repr__` and `__eq__` from annotated fields. Options like `frozen`, `order`, `slots` and `kw_only` add safety and speed. Use `default_factory` for mutable defaults and `__post_init__` for validation.
Hindi: `@dataclass` annotated fields से `__init__`, `__repr__` और `__eq__` लिख देता है। `frozen`, `order`, `slots` और `kw_only` जैसे options safety और speed देते हैं। Mutable defaults के लिए `default_factory` और validation के लिए `__post_init__` use करें।

---

## ➡️ Next Topic
**110. Pydantic Models** - dataclass-like models that also validate and convert data, the backbone of FastAPI request and response handling.
