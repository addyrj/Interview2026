---

# 153. Property vs Descriptor
# हिंदी में: Property बनाम Descriptor — कब कौन सा इस्तेमाल करें

---

## 🔵 Simple Definition (English)
`property` is a ready-made descriptor for one attribute of one class: you write a getter (and optionally a setter) as methods. A custom descriptor is a class you write yourself that implements `__get__`/`__set__`, so the same logic can be reused for many attributes and many classes. In fact, `property` itself is implemented as a descriptor.

## 🔵 सरल परिभाषा (Hindi)
`property` एक class के एक attribute के लिए बना-बनाया descriptor है: आप getter (और चाहें तो setter) methods के रूप में लिखते हैं। Custom descriptor आपकी अपनी लिखी class है जो `__get__`/`__set__` लागू करती है, ताकि वही logic कई attributes और कई classes में दोबारा इस्तेमाल हो सके। असल में `property` खुद एक descriptor है।

---

## 🔴 Problem it Solves
Public attributes (`obj.price = -5`) have no protection. Java-style `get_price()`/`set_price()` methods ruin the clean syntax. `property` keeps the `obj.price` syntax while running code. But when ten fields need the same rule, ten properties means ten copies of nearly identical getters and setters. A descriptor removes the repetition. Choosing the right tool keeps the code short and clear.

## 🔴 यह क्यों बना? (Hindi)
Public attributes (`obj.price = -5`) की कोई सुरक्षा नहीं होती। Java-style `get_price()`/`set_price()` methods साफ syntax बिगाड़ देते हैं। `property` `obj.price` वाला syntax रखते हुए code चलाती है। लेकिन जब दस fields पर एक ही नियम हो, तो दस properties का मतलब लगभग एक जैसे दस getters और setters है। Descriptor यह दोहराव हटाता है। सही tool चुनने से code छोटा और साफ रहता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → @property turns a method into a property object stored on the CLASS
Step 2 → property implements __get__, __set__ and __delete__ (it IS a data descriptor)
Step 3 → obj.x            -> property.__get__ -> calls your getter function with obj
Step 4 → obj.x = v        -> property.__set__ -> calls your setter; no setter -> AttributeError
Step 5 → A custom descriptor does the same, but the logic is in a reusable class
Step 6 → property needs the field name written in the method; a descriptor gets it from __set_name__
Step 7 → property is per-attribute; a descriptor can be reused by many attributes

Choose:
   one attribute, one class, simple logic      -> property
   same rule on many attributes / many classes -> descriptor
   compute once and cache                      -> functools.cached_property
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → @property एक method को property object बनाकर CLASS पर रखता है
Step 2 → property में __get__, __set__ और __delete__ हैं (यह खुद data descriptor है)
Step 3 → obj.x            -> property.__get__ -> आपका getter obj के साथ call होता है
Step 4 → obj.x = v        -> property.__set__ -> आपका setter चलता है; setter न हो -> AttributeError
Step 5 → Custom descriptor भी यही करता है, लेकिन logic reusable class में होता है
Step 6 → property में field का नाम method में लिखना पड़ता है; descriptor को नाम __set_name__ से मिलता है
Step 7 → property एक attribute के लिए है; descriptor कई attributes में reuse हो सकता है

चुनाव:
   एक attribute, एक class, सरल logic           -> property
   कई attributes / कई classes पर वही नियम       -> descriptor
   एक बार compute करके cache करना               -> functools.cached_property
```

---

## 🟡 Real World Example
An e-commerce invoice has `subtotal`, `tax` and `shipping`, all stored as integer paise to avoid float rounding errors but shown in rupees. One reusable `Money` descriptor handles all three. A computed `total` that is only needed on `Invoice` is a normal `@property`, and a heavy `label` is a `cached_property`. Razorpay and Stripe store money as integers for exactly this reason.

## 🟡 Real Example Hindi mein
E-commerce invoice में `subtotal`, `tax` और `shipping` हैं, जो float rounding गलतियों से बचने के लिए integer paise में store होते हैं पर rupees में दिखते हैं। एक reusable `Money` descriptor तीनों संभालता है। सिर्फ `Invoice` में चाहिए वाला computed `total` सामान्य `@property` है, और भारी `label` `cached_property` है। Razorpay और Stripe इसी कारण पैसे को integers में रखते हैं।

---

## 💻 Code Example — Basic
```python
# property is a built-in descriptor; here is the same idea with both styles
from typing import Any                                    # any type


class CelsiusProp:
    def __init__(self, c: float) -> None:
        self._c: float = c                                # private storage

    @property                                             # getter
    def c(self) -> float:
        return self._c

    @c.setter                                             # setter
    def c(self, value: float) -> None:
        if value < -273.15:                               # physical limit
            raise ValueError("below absolute zero")
        self._c = value

    @property                                             # read-only computed property
    def fahrenheit(self) -> float:
        return self._c * 9 / 5 + 32


t = CelsiusProp(100)
print(t.c, t.fahrenheit)                                  # 100 212.0
t.c = 0
print(t.fahrenheit)                                       # 32.0
print(type(CelsiusProp.c).__name__, hasattr(CelsiusProp.c, "__get__"), hasattr(CelsiusProp.c, "__set__"))
try:
    t.fahrenheit = 50                                     # no setter defined
except AttributeError as e:
    print("AttributeError:", e)


class MyProperty:
    """A simplified re-implementation of property using the descriptor protocol."""

    def __init__(self, fget: Any = None, fset: Any = None) -> None:
        self.fget, self.fset = fget, fset                 # getter and setter functions

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        return self if obj is None else self.fget(obj)    # call getter with instance

    def __set__(self, obj: Any, value: Any) -> None:
        if self.fset is None:
            raise AttributeError("read-only")
        self.fset(obj, value)

    def setter(self, fset: Any) -> "MyProperty":
        return MyProperty(self.fget, fset)                # new property with setter


class Box:
    def __init__(self) -> None:
        self._w = 1

    @MyProperty
    def w(self) -> int:
        return self._w

    @w.setter
    def w(self, v: int) -> None:
        self._w = v


b = Box(); b.w = 7
print(b.w)

# Output:
# 100 212.0
# 32.0
# property True True
# AttributeError: property 'fahrenheit' of 'CelsiusProp' object has no setter
# 7
```

## 💻 Code Example — Advanced
```python
# Production style: property for one field vs descriptor reused for many fields
import functools                                          # cached_property
from typing import Any                                    # any type


class Money:
    """Reusable descriptor: stores paise (int) but exposes rupees (float)."""

    def __set_name__(self, owner: type, name: str) -> None:
        self.storage: str = f"_{name}_paise"              # integer storage avoids float errors

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        return obj.__dict__[self.storage] / 100           # paise -> rupees

    def __set__(self, obj: Any, rupees: float) -> None:
        if rupees < 0:
            raise ValueError("money cannot be negative")
        obj.__dict__[self.storage] = round(rupees * 100)  # rupees -> paise


class Invoice:
    subtotal = Money()                                    # reused ...
    tax = Money()                                         # ... for every money field
    shipping = Money()

    def __init__(self, subtotal: float, tax: float, shipping: float) -> None:
        self.subtotal, self.tax, self.shipping = subtotal, tax, shipping

    @property                                             # property: one-off computed value
    def total(self) -> float:
        return self.subtotal + self.tax + self.shipping

    @functools.cached_property                            # computed once, then stored in __dict__
    def label(self) -> str:
        print("building label")                           # shows it runs only once
        return f"INV-{int(self.total * 100)}"


inv = Invoice(499.5, 89.91, 40)
print(inv.total, inv.__dict__["_subtotal_paise"])
print(inv.label, inv.label)                               # second access is cached
try:
    inv.tax = -1
except ValueError as e:
    print("Error:", e)

# Output:
# 629.41 49950
# building label
# INV-62941 INV-62941
# Error: money cannot be negative
```
Both blocks were run on Python 3.13.3 and the output is real. The `AttributeError` wording for a missing setter (`property 'fahrenheit' of 'CelsiusProp' object has no setter`) is the Python 3.11+ message; older versions say only `can't set attribute`.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| One computed/validated attribute | `@property` + `@x.setter` | `get x()` / `set x(v)` in a class |
| Reusable across attributes | custom descriptor | helper with `Object.defineProperty` |
| Read-only attribute | property without setter | getter without setter (silent fail in sloppy mode, error in strict mode) |
| Cached computed value | `functools.cached_property` | manual memo or `Object.defineProperty` trick |

```python
# Python way
class Temp:
    def __init__(self) -> None:
        self._c = 0.0
    @property
    def f(self) -> float:                  # read like an attribute
        return self._c * 9 / 5 + 32
t = Temp()
print(t.f)                                 # 32.0 (no parentheses)
```
```javascript
// JavaScript way
class Temp {
  #c = 0;
  get f() { return this.#c * 9 / 5 + 32; }   // read like a property
}
console.log(new Temp().f);                   // 32 (no parentheses)
```

Key difference: syntax and behaviour are very close for single attributes. Python goes further: because `property` is just a descriptor, you can build your own reusable version, while JavaScript needs `Object.defineProperty` or `Proxy` helpers.

---

## 🟠 FastAPI Connection
Pydantic models used in FastAPI responses can include derived values using `@computed_field` on top of `@property`. The value is calculated on access and included in the JSON response and OpenAPI schema.

```python
# FastAPI example — computed property in a response model
from fastapi import FastAPI                                 # FastAPI app
from fastapi.testclient import TestClient                   # in-process client
from pydantic import BaseModel, computed_field              # model + computed field


class OrderOut(BaseModel):
    price: float                                            # stored field
    qty: int                                                # stored field

    @computed_field                                         # include in output and schema
    @property
    def total(self) -> float:
        return round(self.price * self.qty, 2)              # derived, never stored


app: FastAPI = FastAPI()


@app.post("/order", response_model=OrderOut)
def order(o: OrderOut) -> OrderOut:
    return o                                                # total added automatically


print(TestClient(app).post("/order", json={"price": 19.99, "qty": 3}).json())
# {'price': 19.99, 'qty': 3, 'total': 59.97}
```
(This code was run with FastAPI + Pydantic v2; the printed result matches the comment.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Getter or setter using the same public name -> infinite recursion
✅ Correct: store data under a private name (`_x`)

```python
class A:
    @property
    def x(self): return self.x         # Wrong: calls the property again -> RecursionError
class B:
    def __init__(self): self._x = 0
    @property
    def x(self): return self._x        # Right: read the private attribute
    @x.setter
    def x(self, v): self._x = v        # Right: write the private attribute
```

❌ Mistake 2: Using a property when many fields share the rule
✅ Correct: write one descriptor and reuse it

```python
# Wrong: copy-paste 3 properties for subtotal, tax, shipping
# Right: subtotal = Money(); tax = Money(); shipping = Money()
```

❌ Mistake 3: Assigning in `__init__` to a property that has no setter
✅ Correct: assign to the private name, or add a setter

```python
class C:
    def __init__(self):
        self.v = 1                     # Wrong: property 'v' has no setter -> AttributeError
    @property
    def v(self): return 5
# Right: self._v = 1 in __init__, and expose `v` through the getter
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __init__(self):
        self._x = 0

    @property
    def x(self):
        return self._x

a = A()
a.__dict__["x"] = 99
print(a.x)
```
Answer: `0`. `property` is a data descriptor (it defines `__set__`), so it has higher priority than the instance dictionary. Writing `"x"` directly into `a.__dict__` is ignored on reads. If the property were replaced by a non-data descriptor such as `functools.cached_property` (which only defines `__get__`), the instance dictionary entry would win and `a.x` would be `99`. That is exactly how `cached_property` caches its value.

---

## ⚫ Interview Questions + Answers

Q1: How is `property` related to descriptors?
A1: `property` is a built-in class implementing `__get__`, `__set__` and `__delete__`. `@property` creates an instance of it and stores it on the class. So every property is a data descriptor.

Q2: When do you choose a custom descriptor over property?
A2: When the same validation or conversion logic is needed on several attributes or classes (money, positive numbers, typed fields), or when you need `__set_name__` to learn the field name automatically.

Q3: What is the difference between `property` and `functools.cached_property`?
A3: `property` runs the function on every access and can have a setter. `cached_property` runs once, stores the result in the instance `__dict__`, and later reads bypass the descriptor (non-data descriptor). It needs a writable `__dict__` (so not usable with `__slots__` without `__dict__`).

Q4: Is a property slower than a plain attribute?
A4: Yes, a property read calls a Python function, which is slower than a dictionary lookup (measured: property read slower than plain attribute read). For hot loops use a plain attribute or cache the value.

Q5: Can a property be read-only?
A5: Yes, define only the getter. Assigning raises `AttributeError: property 'x' of 'A' object has no setter` in Python 3.11+.

---

## 🔷 When to Use + When Not to Use
✅ Use property when:
- One attribute needs validation or a computed value
- You want to keep the `obj.x` syntax while adding logic later (backward compatible)
- A read-only derived value is needed (`full_name`, `total`)

✅ Use a descriptor when:
- The rule is shared by many fields or classes
- You build a library, ORM or validation layer

❌ Avoid when:
- A plain attribute is enough (no rule at all)
- Pydantic or dataclasses already validate the data
- Hot loops where the function-call overhead matters

---

## 📊 Visual Diagram
```
                     ┌─── property ───┐       ┌── custom descriptor ──┐
 one attribute  ───► │ getter / setter│       │ __get__ / __set__     │ ◄─── many attributes
 one class           │ in the class   │       │ in a separate class   │      many classes
                     └───────┬────────┘       └──────────┬────────────┘
                             │   property IS a descriptor │
                             └────────────┬───────────────┘
                                          ▼
                    obj.attr  ─►  type(obj).__dict__["attr"].__get__(obj, type(obj))

 Priority: data descriptor (property) > instance __dict__ > non-data (cached_property)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `property` | Built-in data descriptor | Built-in data descriptor |
| Getter / setter | Functions run on read / write | Read / write पर चलने वाले functions |
| `cached_property` | Computes once, then caches | एक बार compute करके cache करता है |
| `computed_field` | Pydantic: include a property in output | Property को output में शामिल करना |
| Derived value | Calculated from other fields | दूसरे fields से निकाली गई value |
| Reuse | Same logic on many attributes | कई attributes पर वही logic |

---

## ⚡ 3-Line Summary
English: `property` is a built-in descriptor for one attribute; write a custom descriptor when the same rule applies to many fields. Always store data under a private name to avoid recursion. `cached_property` is a non-data descriptor that stores the computed value in `__dict__`.
Hindi: `property` एक attribute के लिए built-in descriptor है; जब वही नियम कई fields पर हो तो custom descriptor लिखें। Recursion से बचने के लिए data हमेशा private नाम से store करें। `cached_property` non-data descriptor है जो computed value `__dict__` में रखता है।

---

## ➡️ Next Topic
**154. Slots vs Dict** — how `__slots__` removes the per-instance dictionary to save memory and speed up attribute access.
