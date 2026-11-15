---

# 151. Descriptor Protocol
# हिंदी में: Descriptor Protocol (Attribute Access को Control करना)

---

## 🔵 Simple Definition (English)
A descriptor is an object stored as a class attribute that defines `__get__`, `__set__` or `__delete__`. When you read, assign or delete that attribute on an instance, Python calls these methods instead of touching the instance dictionary directly. Properties, methods, `classmethod`, `staticmethod`, `__slots__` and ORM columns are all built with descriptors.

## 🔵 सरल परिभाषा (Hindi)
Descriptor ऐसा object है जो class attribute के रूप में रखा जाता है और `__get__`, `__set__` या `__delete__` define करता है। जब आप instance पर वह attribute पढ़ते, assign करते या delete करते हैं, तो Python instance dictionary को सीधे छूने की जगह ये methods call करता है। Properties, methods, `classmethod`, `staticmethod`, `__slots__` और ORM columns सब descriptors से बने हैं।

---

## 🔴 Problem it Solves
Without descriptors, validation or computed access for one attribute needs a `@property` written separately in every class and for every field. If ten fields share the same rule ("must be positive"), you copy ten getters and setters. Descriptors let you write the rule once as a class and reuse it on many fields and many classes.

## 🔴 यह क्यों बना? (Hindi)
Descriptors के बिना एक attribute की validation या computed access के लिए हर class और हर field में अलग `@property` लिखनी पड़ती है। अगर दस fields पर एक ही नियम ("positive होना चाहिए") है तो दस getters और setters copy करने पड़ते हैं। Descriptor से नियम एक बार class के रूप में लिखें और कई fields व कई classes पर दोबारा इस्तेमाल करें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a class with __get__ / __set__ / __delete__ (the descriptor class)
Step 2 → Put an INSTANCE of it as a CLASS attribute:  price = Positive()
Step 3 → Python calls __set_name__(owner, "price") once, so the descriptor learns its name
Step 4 → obj.price           -> type(obj).price.__get__(obj, type(obj))
Step 5 → obj.price = 10      -> type(obj).price.__set__(obj, 10)
Step 6 → del obj.price       -> type(obj).price.__delete__(obj)
Step 7 → Class.price         -> __get__(None, Class)  (obj is None: return self)

Lookup priority on obj.attr:
   1. DATA descriptor (has __set__ or __delete__) on the class  -> wins over instance dict
   2. instance __dict__
   3. NON-DATA descriptor (only __get__) or plain class attribute
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → __get__ / __set__ / __delete__ वाली class बनाएं (descriptor class)
Step 2 → उसका INSTANCE CLASS attribute के रूप में रखें:  price = Positive()
Step 3 → Python एक बार __set_name__(owner, "price") call करता है, ताकि descriptor अपना नाम जान ले
Step 4 → obj.price           -> type(obj).price.__get__(obj, type(obj))
Step 5 → obj.price = 10      -> type(obj).price.__set__(obj, 10)
Step 6 → del obj.price       -> type(obj).price.__delete__(obj)
Step 7 → Class.price         -> __get__(None, Class)  (obj None है: self लौटाएं)

obj.attr पर lookup की priority:
   1. Class पर DATA descriptor (__set__ या __delete__ वाला)  -> instance dict से ऊपर
   2. instance का __dict__
   3. NON-DATA descriptor (सिर्फ __get__) या सादा class attribute
```

---

## 🟡 Real World Example
SQLAlchemy columns (`User.name`) are descriptors: reading `user.name` returns the loaded value, assigning it marks the row as dirty for the next flush. Django model fields work the same way. A Razorpay-style payments service can define a `Positive` descriptor and reuse it for `amount`, `tax` and `refund`, so negative money can never enter the system.

## 🟡 Real Example Hindi mein
SQLAlchemy columns (`User.name`) descriptors हैं: `user.name` पढ़ने पर loaded value मिलती है और assign करने पर row अगले flush के लिए dirty mark हो जाती है। Django model fields भी ऐसे ही काम करते हैं। Razorpay जैसी payments service `Positive` descriptor बनाकर `amount`, `tax` और `refund` तीनों पर इस्तेमाल कर सकती है, ताकि negative पैसा system में कभी न आए।

---

## 💻 Code Example — Basic
```python
# Descriptor protocol: an object in a class attribute that controls get/set/delete
from typing import Any                                    # any type


class Positive:
    """Data descriptor: only accepts positive numbers."""

    def __set_name__(self, owner: type, name: str) -> None:
        self.private_name: str = "_" + name               # where the real value is stored

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:                                   # accessed on the class: Product.price
            return self                                   # return the descriptor itself
        return getattr(obj, self.private_name)            # read the stored value

    def __set__(self, obj: Any, value: float) -> None:
        if value <= 0:                                    # validate on every assignment
            raise ValueError("must be positive")
        setattr(obj, self.private_name, value)           # store on the instance


class Product:
    price = Positive()                                    # descriptor lives on the CLASS

    def __init__(self, price: float) -> None:
        self.price = price                                # triggers Positive.__set__


p = Product(100)                                          # valid
print(p.price)                                            # triggers __get__ -> 100
p.price = 250                                             # triggers __set__
print(p.price, p.__dict__)                                # value stored as _price
try:
    p.price = -5                                          # invalid
except ValueError as e:
    print("Error:", e)
print(type(Product.price).__name__)                       # class access returns the descriptor

# Output:
# 100
# 250 {'_price': 250}
# Error: must be positive
# Positive
```

## 💻 Code Example — Advanced
```python
# Production style: reusable typed validators, lazy (non-data) descriptor
from typing import Any, Callable, Generic, TypeVar        # typing helpers

T = TypeVar("T")


class Field(Generic[T]):
    """Reusable validated field using __set_name__ and a validator function."""

    def __init__(self, validator: Callable[[T], None]) -> None:
        self.validator = validator                        # function that raises on bad data

    def __set_name__(self, owner: type, name: str) -> None:
        self.name: str = name                             # public attribute name
        self.storage: str = f"_{name}"                    # private storage name

    def __get__(self, obj: Any, objtype: type | None = None) -> T:
        if obj is None:
            return self                                   # type: ignore[return-value]
        return obj.__dict__[self.storage]                 # read from instance dict

    def __set__(self, obj: Any, value: T) -> None:
        self.validator(value)                             # reject bad values early
        obj.__dict__[self.storage] = value                # store value


def non_empty(v: str) -> None:
    if not v.strip():
        raise ValueError("must not be empty")


def valid_rating(v: int) -> None:
    if not 1 <= v <= 5:
        raise ValueError("rating must be 1..5")


class Review:
    author = Field(non_empty)                             # same descriptor class, different rules
    rating = Field(valid_rating)

    def __init__(self, author: str, rating: int) -> None:
        self.author = author                              # validated
        self.rating = rating                              # validated


r = Review("Riya", 5)
print(r.author, r.rating)
for bad in (("", 3), ("Aman", 9)):                        # two invalid inputs
    try:
        Review(*bad)
    except ValueError as e:
        print("Error:", e)


class lazy:
    """Non-data descriptor (only __get__): computes once, then caches in instance dict."""

    def __init__(self, func: Callable[[Any], Any]) -> None:
        self.func = func
        self.name = func.__name__

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        value = self.func(obj)                            # compute
        obj.__dict__[self.name] = value                   # instance dict wins next time
        return value


class Report:
    calls = 0

    @lazy
    def total(self) -> int:
        Report.calls += 1                                 # count real computations
        return sum(range(1000))


rep = Report()
print(rep.total, rep.total, Report.calls)                 # computed once

# Output:
# Riya 5
# Error: must not be empty
# Error: rating must be 1..5
# 499500 499500 1
```
Both blocks were run on Python 3.13.3 with real output as shown. `__set_name__` exists since Python 3.6.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Hook on attribute access | descriptor (`__get__`, `__set__`) | getter/setter via `Object.defineProperty` or `get`/`set` |
| Reusable across fields | yes, one class reused | no; define per property (or use a Proxy) |
| Intercept every property | `__getattr__` / `__getattribute__` | `Proxy` |
| Used by the language | methods, property, slots | class `get`/`set` accessors |

```python
# Python way — one descriptor class, reused
class Positive:
    def __set_name__(self, owner, name): self.n = "_" + name   # learn field name
    def __get__(self, o, t=None): return self if o is None else getattr(o, self.n)
    def __set__(self, o, v):
        if v <= 0: raise ValueError("must be positive")        # shared rule
        setattr(o, self.n, v)

class Order:
    qty = Positive()                                           # reuse for qty
    price = Positive()                                         # reuse for price
```
```javascript
// JavaScript way — getter/setter written per property
class Order {
  #qty = 1;
  get qty() { return this.#qty; }
  set qty(v) { if (v <= 0) throw new Error("must be positive"); this.#qty = v; }
  // price needs another get/set pair, or a helper using Object.defineProperty
}
```

Key difference: in Python the validation logic is a reusable object (a descriptor); in JavaScript accessors are tied to one property unless you build a helper with `Object.defineProperty` or a `Proxy`.

---

## 🟠 FastAPI Connection
SQLAlchemy models (the usual FastAPI persistence layer) use descriptors: `User.name` is an `InstrumentedAttribute`, and plain instances track changes through `__get__`/`__set__`. For pure domain objects you can use your own descriptor to guard values, and convert `ValueError` into `HTTPException`.

```python
# FastAPI example — descriptor-validated domain object behind a route
from typing import Any                                      # any type
from fastapi import FastAPI, HTTPException                  # FastAPI parts
from fastapi.testclient import TestClient                   # in-process client


class Positive:
    def __set_name__(self, owner: type, name: str) -> None:
        self.name: str = "_" + name                         # private storage name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        return self if obj is None else getattr(obj, self.name)

    def __set__(self, obj: Any, value: float) -> None:
        if value <= 0:                                      # business rule
            raise ValueError("amount must be positive")
        setattr(obj, self.name, value)


class Payment:
    amount = Positive()                                     # guarded field

    def __init__(self, amount: float) -> None:
        self.amount = amount                                # goes through __set__


app: FastAPI = FastAPI()                                    # create app


@app.post("/pay")
def pay(amount: float) -> dict[str, float]:
    try:
        return {"charged": Payment(amount).amount}          # valid payment
    except ValueError as e:                                 # descriptor rejected it
        raise HTTPException(status_code=400, detail=str(e))


client = TestClient(app)
print(client.post("/pay", params={"amount": 50}).json())    # {'charged': 50.0}
r = client.post("/pay", params={"amount": -1})
print(r.status_code, r.json())                              # 400 {'detail': 'amount must be positive'}
```
(Run with TestClient: output `{'charged': 50.0}` and `400 {'detail': 'amount must be positive'}`. Also verified: `type(User.name).__name__` for a SQLAlchemy 2.x `Mapped` column is `InstrumentedAttribute`, which defines `__get__`.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Storing the value on the descriptor itself
✅ Correct: store it on the instance (`obj.__dict__` or `setattr(obj, ...)`)

```python
# Wrong — one descriptor object is shared by ALL instances
class Bad:
    def __init__(self): self.v = None
    def __get__(self, o, t=None): return self.v
    def __set__(self, o, v): self.v = v
class Q:
    x = Bad()
a, b = Q(), Q()
a.x = 1; b.x = 2
print(a.x, b.x)          # 2 2  <- a's value was overwritten!
# Right: setattr(o, self.private_name, v) or o.__dict__[name] = v
```

❌ Mistake 2: Putting the descriptor in `__init__` (on the instance)
✅ Correct: descriptors only work as CLASS attributes

```python
class Wrong:
    def __init__(self):
        self.price = Positive()       # Wrong: stored in instance dict, __get__/__set__ never called
class Right:
    price = Positive()                # Right: class attribute
```

❌ Mistake 3: Reading before any value was set
✅ Correct: give a default or catch `AttributeError`

```python
class P:
    price = Positive()
p = P()
# print(p.price)   # AttributeError: 'P' object has no attribute '_price'
# Right: set a default in __init__ or handle the missing case inside __get__
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Data:
    def __get__(self, o, t=None): return "descriptor"
    def __set__(self, o, v): print("set called")

class NonData:
    def __get__(self, o, t=None): return "descriptor"

class A:
    d = Data()
    n = NonData()

a = A()
a.__dict__["d"] = "instance"
a.__dict__["n"] = "instance"
print(a.d, a.n)
a.d = 1
print(a.__dict__["d"])
```
Answer: `descriptor instance`, then `set called`, then `instance`. A data descriptor (has `__set__`) beats the instance dictionary, so `a.d` gives `"descriptor"`. A non-data descriptor loses to the instance dictionary, so `a.n` gives `"instance"`. The assignment `a.d = 1` calls `Data.__set__` which only prints, so the dictionary value stays `"instance"`.

---

## ⚫ Interview Questions + Answers

Q1: What is the descriptor protocol?
A1: Any object defining `__get__`, `__set__` or `__delete__` and stored as a class attribute. Python calls these hooks on attribute access of instances.

Q2: Data descriptor vs non-data descriptor?
A2: A data descriptor defines `__set__` or `__delete__` and overrides the instance dictionary. A non-data descriptor defines only `__get__`, so the instance dictionary can shadow it. Functions are non-data descriptors, which is why you can override a method on one instance.

Q3: What does `__set_name__` do?
A3: Called once when the class is created. It tells the descriptor its attribute name, so one class can serve many fields without repeating the name as a string.

Q4: Why is `obj` None in `__get__` sometimes?
A4: When the attribute is accessed on the class (`Product.price`). Return `self` so tools like help and ORMs can inspect the descriptor.

Q5: Which Python features are built on descriptors?
A5: `property`, `classmethod`, `staticmethod`, regular functions (method binding), `functools.cached_property`, `__slots__` members, and ORM fields like SQLAlchemy `InstrumentedAttribute`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The same validation or conversion rule is needed on many attributes
- You write a library or framework (ORM fields, config fields)
- You need lazy or computed attributes with caching

❌ Avoid when:
- Only one attribute needs custom behaviour, `@property` is simpler
- A dataclass or Pydantic model already validates the data
- The team is unfamiliar with descriptors and the rule is trivial

---

## 📊 Visual Diagram
```
class Product:
    price = Positive()          <── descriptor object, lives on the CLASS

p = Product(100)

p.price = 250    ──►  type(p).__mro__ lookup finds Positive (has __set__)
                       └─► Positive.__set__(descriptor, p, 250) ─► p._price = 250
print(p.price)   ──►  Positive.__get__(descriptor, p, Product)  ─► returns p._price
Product.price    ──►  Positive.__get__(descriptor, None, Product) ─► returns descriptor

Priority:  data descriptor  >  instance __dict__  >  non-data descriptor / class attr
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Descriptor | Class attribute object with `__get__` etc. | `__get__` आदि वाला class attribute object |
| Data descriptor | Has `__set__` or `__delete__` | `__set__` या `__delete__` वाला |
| Non-data descriptor | Only `__get__` | सिर्फ `__get__` वाला |
| `__set_name__` | Tells the descriptor its attribute name | Descriptor को उसका नाम बताता है |
| Owner | The class that holds the descriptor | Descriptor रखने वाली class |
| Binding | Turning a function into a bound method | Function को bound method बनाना |

---

## ⚡ 3-Line Summary
English: A descriptor is a class-level object whose `__get__`, `__set__` and `__delete__` control attribute access on instances. Data descriptors beat the instance dictionary; non-data ones do not. Properties, methods and ORM columns all use this protocol.
Hindi: Descriptor class-level object है जिसके `__get__`, `__set__` और `__delete__` instances पर attribute access को control करते हैं। Data descriptors instance dictionary से ऊपर होते हैं; non-data नहीं। Properties, methods और ORM columns सब इसी protocol का उपयोग करते हैं।

---

## ➡️ Next Topic
**152. `__get__` `__set__` `__delete__`** — a closer look at each of the three methods, their arguments and what they receive.
