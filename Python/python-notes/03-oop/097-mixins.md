---

# 097. Mixins
# हिंदी में: Mixins (Reusable Behavior के छोटे Classes)

---

## 🔵 Simple Definition (English)
A mixin is a small class that adds one focused behavior (like JSON export, logging or timestamps) to other classes through multiple inheritance. It is not meant to be used alone and usually has no `__init__` of its own.

## 🔵 सरल परिभाषा (Hindi)
Mixin एक छोटी class है जो multiple inheritance के ज़रिए दूसरी classes में एक focused behavior (जैसे JSON export, logging या timestamps) जोड़ती है। इसे अकेले इस्तेमाल करने के लिए नहीं बनाया जाता और आम तौर पर इसका अपना `__init__` नहीं होता।

---

## 🔴 Problem it Solves
Suppose `User`, `Order` and `Product` all need `to_json()`. Copy-paste means three places to fix bugs. A deep inheritance chain (`Order(JsonBase)`) forces unrelated classes into one tree. Mixins give "horizontal reuse": write `to_json()` once in `JsonMixin` and attach it to any class by listing it as a parent.

## 🔴 यह क्यों बना? (Hindi)
मान लो `User`, `Order` और `Product` तीनों को `to_json()` चाहिए। Copy-paste का मतलब तीन जगह bug fix। गहरी inheritance chain (`Order(JsonBase)`) असंबंधित classes को एक ही tree में डाल देती है। Mixin "horizontal reuse" देता है: `to_json()` एक बार `JsonMixin` में लिखो और किसी भी class में parent के रूप में जोड़ दो।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a small class with ONE behavior: class JsonMixin: def to_json(self): ...
Step 2 → It relies only on attributes the host class provides (e.g. self.__dict__)
Step 3 → Attach it: class User(JsonMixin, Base)  - mixins go BEFORE the main base
Step 4 → Python builds the MRO: User -> JsonMixin -> Base -> object
Step 5 → user.to_json() is found in JsonMixin through normal attribute lookup
Step 6 → If the mixin overrides a method, it calls super() so the chain continues
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक ही behavior वाली छोटी class लिखो: class JsonMixin: def to_json(self): ...
Step 2 → वह सिर्फ उन attributes पर निर्भर रहती है जो host class देती है (जैसे self.__dict__)
Step 3 → जोड़ो: class User(JsonMixin, Base)  - mixins मुख्य base से पहले लिखते हैं
Step 4 → Python MRO बनाता है: User -> JsonMixin -> Base -> object
Step 5 → user.to_json() normal attribute lookup से JsonMixin में मिल जाता है
Step 6 → Mixin अगर method override करे तो super() call करे ताकि chain चलती रहे
```

---

## 🟡 Real World Example
In a Django/SQLAlchemy backend, `TimestampMixin` adds `created_at` and `updated_at` columns to every model; `SoftDeleteMixin` adds `deleted_at`; `ReprMixin` gives readable debug output. Django's `LoginRequiredMixin` is the famous example: `class OrderView(LoginRequiredMixin, ListView)`. In Python's stdlib, `socketserver.ThreadingMixIn` adds threading to any server class.

## 🟡 Real Example Hindi mein
Django/SQLAlchemy backend में `TimestampMixin` हर model में `created_at` और `updated_at` columns जोड़ता है; `SoftDeleteMixin` `deleted_at` जोड़ता है; `ReprMixin` debug के लिए पढ़ने लायक output देता है। Django का `LoginRequiredMixin` मशहूर उदाहरण है: `class OrderView(LoginRequiredMixin, ListView)`। stdlib में `socketserver.ThreadingMixIn` किसी भी server class में threading जोड़ देता है।

---

## 💻 Code Example — Basic
```python
# Basic mixin example
import json                                     # to build JSON text


class JsonMixin:                                # mixin: one behavior only
    def to_json(self) -> str:                   # added to every host class
        return json.dumps(self.__dict__)        # uses the host's attributes


class ReprMixin:                                # second mixin
    def __repr__(self) -> str:                  # nicer debug text
        items: str = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())   # k=v list
        return f"{type(self).__name__}({items})"    # ClassName(a=1, b=2)


class User(JsonMixin, ReprMixin):               # combine two behaviors
    def __init__(self, name: str, age: int) -> None:    # normal constructor
        self.name: str = name                   # data
        self.age: int = age                     # data


class Product(JsonMixin):                       # unrelated class reuses the same mixin
    def __init__(self, title: str) -> None:
        self.title: str = title


u: User = User("Asha", 25)                      # create user
print(u.to_json())                              # from JsonMixin
print(u)                                        # from ReprMixin
print(Product("Pen").to_json())                 # same mixin, different class
print([c.__name__ for c in User.__mro__])       # lookup order

# Output:
# {"name": "Asha", "age": 25}
# User(name='Asha', age=25)
# {"title": "Pen"}
# ['User', 'JsonMixin', 'ReprMixin', 'object']
```

## 💻 Code Example — Advanced
```python
# Production style: cooperative mixins with super(), validation and audit trail
from datetime import datetime, timezone         # timestamps


class TimestampMixin:                           # adds created/updated tracking
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)       # cooperative: let the others init first
        self.created_at: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)   # fixed for demo
        self.updated_at: datetime = self.created_at     # starts equal

    def touch(self) -> None:                    # call after every change
        self.updated_at = datetime(2026, 1, 2, tzinfo=timezone.utc)    # fixed for demo


class SoftDeleteMixin:                          # "delete" without removing the row
    deleted: bool = False                       # class-level default

    def soft_delete(self) -> None:              # mark deleted
        self.deleted = True                     # instance attribute shadows the default

    def __init_subclass__(cls, **kw: object) -> None:   # validate the host at definition time
        super().__init_subclass__(**kw)         # keep chain intact
        if not hasattr(cls, "table"):           # host must declare a table name
            raise TypeError(f"{cls.__name__} needs a 'table' attribute")


class AuditMixin:                               # records method calls
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)       # cooperative
        self.audit: list[str] = []              # list of events

    def log(self, event: str) -> None:          # add an event
        self.audit.append(event)                # store it


class Model:                                    # plain base (end of the chain)
    def __init__(self, **fields: object) -> None:
        self.__dict__.update(fields)            # store fields as attributes


class Invoice(TimestampMixin, SoftDeleteMixin, AuditMixin, Model):   # compose behaviors
    table = "invoices"                          # required by SoftDeleteMixin


inv: Invoice = Invoice(number="INV-1", amount=500)    # fields go down to Model
inv.log("created")                              # AuditMixin
inv.touch()                                     # TimestampMixin
inv.soft_delete()                               # SoftDeleteMixin
print(inv.number, inv.amount, inv.deleted)      # Model + SoftDeleteMixin
print(inv.audit, inv.updated_at.day)            # AuditMixin + TimestampMixin
print([c.__name__ for c in Invoice.__mro__])    # full chain

try:                                            # host without 'table'
    class Bad(SoftDeleteMixin, Model):          # definition itself fails
        pass
except TypeError as e:                          # caught at class creation
    print("Error:", e)

# Output:
# INV-1 500 True
# ['created'] 2
# ['Invoice', 'TimestampMixin', 'SoftDeleteMixin', 'AuditMixin', 'Model', 'object']
# Error: Bad needs a 'table' attribute
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Mixin mechanism | Multiple inheritance | `Object.assign(Class.prototype, mixin)` or class-factory functions |
| Language support | Built in (`class A(M1, M2)`) | Pattern only, no keyword |
| Conflict resolution | MRO (predictable) | Last assignment wins |
| `super` in mixin | Works through MRO | Needs factory pattern `Base => class extends Base` |

```python
# Python way
class Walk:
    def walk(self) -> str:
        return "walking"     # mixin behavior

class Swim:
    def swim(self) -> str:
        return "swimming"    # mixin behavior

class Duck(Walk, Swim):      # combine both
    pass

d = Duck()
print(d.walk(), d.swim())    # walking swimming
```
```javascript
// JavaScript way — mixins as copied methods
const Walk = { walk() { return "walking"; } };     // plain object mixin
const Swim = { swim() { return "swimming"; } };    // plain object mixin
class Duck {}                                      // no multiple inheritance in JS
Object.assign(Duck.prototype, Walk, Swim);         // copy methods onto the prototype
const d = new Duck();
console.log(d.walk(), d.swim());                   // walking swimming
```

Key difference: JavaScript has single inheritance, so mixins are copied in manually (or built with "subclass factory" functions). Python lets you list several parents and resolves conflicts predictably with the MRO.

---

## 🟠 FastAPI Connection
In FastAPI projects, SQLAlchemy models use `TimestampMixin` and `SoftDeleteMixin`, and Pydantic schemas share fields through small base models. A mixin can also add `to_response()` helpers to ORM objects.

```python
# FastAPI example — Mixin adding to_dict() to domain objects used in responses
from dataclasses import dataclass, asdict       # dataclass tools
from fastapi import FastAPI                     # app
from fastapi.testclient import TestClient       # test client


class DictMixin:                                # reusable conversion
    def to_dict(self) -> dict[str, object]:     # needs the host to be a dataclass
        return asdict(self)                     # type: ignore[call-overload]


@dataclass
class Customer(DictMixin):                      # host class
    id: int
    name: str


app: FastAPI = FastAPI()                        # create app


@app.get("/customers/{cid}")                    # GET /customers/1
def get_customer(cid: int) -> dict[str, object]:
    return Customer(cid, "Asha").to_dict()      # mixin method used in the route


client: TestClient = TestClient(app)            # test client
print(client.get("/customers/1").json())        # {'id': 1, 'name': 'Asha'}

# Output:
# {'id': 1, 'name': 'Asha'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Putting the mixin AFTER the main base
✅ Correct: mixins first, so they can override and call `super()`

```python
class Base:
    def hello(self) -> str:
        return "base"

class LoudMixin:
    def hello(self) -> str:
        return super().hello().upper()    # decorates the next class in MRO

class Wrong(Base, LoudMixin):             # Base wins; mixin never used
    pass

class Right(LoudMixin, Base):             # mixin first
    pass

print(Wrong().hello(), Right().hello())   # base BASE
```

❌ Mistake 2: Giving the mixin its own state and a non-cooperative `__init__`
✅ Correct: accept `*args, **kwargs` and call `super().__init__`

```python
class Base:
    def __init__(self, x: int) -> None:
        self.x = x

class Wrong:                              # swallows arguments, breaks Base
    def __init__(self) -> None:
        self.flag = True

class Right:
    def __init__(self, *a: object, **k: object) -> None:
        super().__init__(*a, **k)         # forward everything
        self.flag = True

class H1(Wrong, Base): ...
class H2(Right, Base): ...
try:
    H1(5)                                 # Wrong.__init__ takes no x
except TypeError as e:
    print("Error:", e)
print(H2(5).x, H2(5).flag)                # 5 True
```

❌ Mistake 3: Mixin that silently depends on host attributes
✅ Correct: document and validate what the host must provide

```python
class PriceMixin:
    def total(self) -> float:
        return self.price * self.qty      # Wrong: assumes price/qty exist

class Item(PriceMixin):
    pass

try:
    Item().total()
except AttributeError as e:
    print("Error:", e)                    # 'Item' object has no attribute 'price'
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def who(self) -> str:
        return "A"

class M1:
    def who(self) -> str:
        return "M1>" + super().who()

class M2:
    def who(self) -> str:
        return "M2>" + super().who()

class C(M1, M2, A):
    pass

print(C().who())
print(M1().who())
```
Answer: The first line prints `M1>M2>A`. C's MRO is `C, M1, M2, A, object`, so `super()` in `M1` goes to `M2`, and in `M2` goes to `A`. The second line raises `AttributeError: 'super' object has no attribute 'who'`, because a standalone `M1` has only `object` after it. Mixins that call `super()` can only be used inside a host that provides the method.

---

## ⚫ Interview Questions + Answers

Q1: What is a mixin and how is it different from a normal base class?
A1: A mixin is a small, focused class not meant to be instantiated alone; it adds capabilities and is combined with a main base. A normal base defines the "is-a" identity of the object. Mixin means "can-do".

Q2: Why list mixins before the main base class?
A2: MRO searches left to right, so mixins come first and can override or wrap base methods (calling `super()`). If listed last, the base's version wins.

Q3: Mixins vs composition?
A3: Composition (`self.logger = Logger()`) is more explicit and easier to test. Mixins are shorter and add methods directly to the class, but couple everything into one namespace. Prefer composition unless you need the methods on the object itself.

Q4: What are the risks of mixins?
A4: Name clashes between mixins, hidden dependencies on host attributes, and confusing MRO when many are stacked. Keep each mixin tiny, name-prefixed methods, and document requirements.

Q5: Can mixins use `__init_subclass__`?
A5: Yes. It lets a mixin validate or register every host class at definition time (for example, requiring a `table` attribute), which catches mistakes before any object exists.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several unrelated classes need the same small feature (timestamps, JSON, audit)
- Framework extension points (Django views, SQLAlchemy models)
- The feature needs methods on the object itself

❌ Avoid when:
- The behavior needs lots of its own state (use composition)
- More than 3 or 4 mixins are stacked (MRO gets hard to reason about)
- A plain helper function would do

---

## 📊 Visual Diagram
```
  TimestampMixin   SoftDeleteMixin   AuditMixin
        \               |               /
         \              |              /
          +---------> Invoice <-------+          (also inherits Model)
                          |
                        Model
                          |
                       object

MRO: Invoice -> TimestampMixin -> SoftDeleteMixin -> AuditMixin -> Model -> object
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mixin | Small class adding one behavior | एक behavior जोड़ने वाली छोटी class |
| Host class | Class that uses the mixin | Mixin इस्तेमाल करने वाली class |
| MRO | Order of attribute lookup | Lookup का क्रम |
| Cooperative | Every class calls super() | हर class super() call करती है |
| `__init_subclass__` | Hook run when a subclass is defined | Subclass बनते ही चलने वाला hook |
| Composition | Holding another object as attribute | दूसरे object को attribute में रखना |

---

## ⚡ 3-Line Summary
English: A mixin is a small class that adds one capability to other classes via multiple inheritance. List mixins before the main base and make `__init__` cooperative with `super()`. Keep them tiny; use composition when state grows.
Hindi: Mixin एक छोटी class है जो multiple inheritance से दूसरी classes में एक capability जोड़ती है। Mixins को main base से पहले लिखें और `__init__` को `super()` से cooperative रखें। उन्हें छोटा रखें; state बढ़े तो composition इस्तेमाल करें।

---

## ➡️ Next Topic
**098. Encapsulation** — hide internal data behind clear interfaces using `_protected`, `__private` and properties.
