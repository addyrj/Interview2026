---

# 088. Properties (@property)
# हिंदी में: Properties (@property)

---

## 🔵 Simple Definition (English)
`@property` turns a method into something you read like an attribute: `c.area` instead of `c.area()`. The value can be computed on access, and later you can add validation without changing the code that uses it.

## 🔵 सरल परिभाषा (Hindi)
`@property` एक method को ऐसा बना देता है जिसे attribute की तरह पढ़ते हैं: `c.area()` की जगह `c.area`। Value हर बार access पर compute हो सकती है और बाद में validation जोड़ने पर उसे इस्तेमाल करने वाला code बदलना नहीं पड़ता।

---

## 🔴 Problem it Solves
In Java you write `getPrice()` and `setPrice()` from day one because changing a public field into a method later breaks callers. In Python you can start with a plain attribute and turn it into a property later with zero change for callers. Properties also give read-only values and computed fields (`full_name`, `price_with_gst`) that always stay in sync with the stored data.

## 🔴 यह क्यों बना? (Hindi)
Java में शुरू से `getPrice()` और `setPrice()` लिखते हैं क्योंकि public field को बाद में method बनाने से callers टूट जाते हैं। Python में आप सामान्य attribute से शुरू करके बाद में property बना सकते हैं और callers को कुछ बदलना नहीं पड़ता। Properties read-only values और computed fields (`full_name`, `price_with_gst`) भी देती हैं जो stored data के साथ हमेशा sync रहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `@property` creates a `property` object stored on the class
Step 2 → You write `c.area` (no brackets)
Step 3 → Python finds a data descriptor on the class, which takes priority over `c.__dict__`
Step 4 → The descriptor calls your function with `c` as `self`
Step 5 → The returned value is what `c.area` evaluates to
Step 6 → Assigning `c.area = 5` fails with AttributeError unless a setter is defined
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `@property` class पर एक `property` object बनाता है
Step 2 → आप `c.area` लिखते हैं (बिना brackets)
Step 3 → Python को class पर data descriptor मिलता है, जो `c.__dict__` से ऊपर priority रखता है
Step 4 → Descriptor आपका function `c` को `self` बनाकर चलाता है
Step 5 → लौटी value ही `c.area` की value होती है
Step 6 → `c.area = 5` AttributeError देता है जब तक setter न हो
```

---

## 🟡 Real World Example
An e-commerce `Product` has a stored `price` and a computed `price_with_gst`. An `Order` has a read-only `total` property. A heavy `Report` uses `functools.cached_property` so the total is computed once. Pydantic v2 `@computed_field` puts a property into the API response.

## 🟡 Real Example Hindi mein
E-commerce `Product` में stored `price` और computed `price_with_gst` होता है। `Order` में read-only `total` property। भारी `Report` `functools.cached_property` से total सिर्फ एक बार निकालती है। Pydantic v2 का `@computed_field` property को API response में डाल देता है।

---

## 💻 Code Example — Basic
```python
# Basic: @property makes a method look like an attribute
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius: float = radius              # internal storage

    @property                                     # read as c.radius (no brackets)
    def radius(self) -> float:
        return self._radius

    @property
    def area(self) -> float:                      # computed on every access
        return round(3.14159 * self._radius ** 2, 2)


c: Circle = Circle(2)
print(c.radius, c.area)                           # 2 12.57
c._radius = 3                                     # area follows automatically
print(c.area)                                     # 28.27
try:
    c.area = 5                                    # read-only property
except AttributeError as e:
    print("Error:", e)
print(type(Circle.area), Circle.area.fget.__name__)   # property object on the class

# Output:
# 2 12.57
# 28.27
# Error: property 'area' of 'Circle' object has no setter
# <class 'property'> area
```

## 💻 Code Example — Advanced
```python
# Advanced: validated property, cached computed property, and lazy loading
from __future__ import annotations
from functools import cached_property            # computed once, then stored on the instance


class Product:
    def __init__(self, name: str, price: float) -> None:
        self.name: str = name
        self.price = price                        # goes through the setter -> validated at init

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("price cannot be negative")
        self._price = round(float(value), 2)

    @property
    def price_with_gst(self) -> float:
        return round(self._price * 1.18, 2)


class Report:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows
        self.calls = 0

    @cached_property                              # heavy work done once
    def total(self) -> int:
        self.calls += 1
        return sum(self.rows)


p = Product("Pen", 10.456)
print(p.price, p.price_with_gst)
p.price = 99
print(p.price)
try:
    Product("Bad", -1)
except ValueError as e:
    print("Error:", e)
r = Report([1, 2, 3])
print(r.total, r.total, r.calls)                  # 6 6 1
print("total" in r.__dict__)                      # cached_property stores into __dict__

# Output:
# 10.46 12.34
# 99.0
# Error: price cannot be negative
# 6 6 1
# True
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Read-only computed value | `@property` | `get area() {}` |
| Setter | `@x.setter` | `set x(v) {}` |
| Cache computed value | `functools.cached_property` | manual memo |
| Looks like attribute | yes | yes |
| Private by convention | `_x` | `#x` (truly private) |

```python
# Python way
class Circle:
    def __init__(self, r: float) -> None:
        self._r = r
    @property
    def area(self) -> float:
        return 3.14159 * self._r ** 2

print(round(Circle(2).area, 2))   # 12.57
```
```javascript
// JavaScript way
class Circle {
  #r;
  constructor(r) { this.#r = r; }
  get area() { return 3.14159 * this.#r ** 2; }
}
console.log(new Circle(2).area.toFixed(2)); // 12.57
```

Key difference: syntax differs (`@property` vs `get`), but the idea is identical. JS has truly private `#fields`; Python only has the `_name` convention, so a property is how you control access in Python.

---

## 🟠 FastAPI Connection
Pydantic v2 supports `@computed_field` on top of `@property` so derived values appear in the JSON response. SQLAlchemy models use `@property` (and `hybrid_property`) for derived columns like `full_name`.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, computed_field

app = FastAPI()


class Item(BaseModel):
    price: float
    qty: int

    @computed_field                               # pydantic v2: property included in the JSON
    @property
    def total(self) -> float:
        return round(self.price * self.qty, 2)


@app.post("/items")
def create(item: Item) -> Item:
    return item


print(TestClient(app).post("/items", json={"price": 9.99, "qty": 3}).json())

# Output:
# {'price': 9.99, 'qty': 3, 'total': 29.97}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling a property with brackets
✅ Correct: read it without ()

```python
class A:
    @property
    def v(self) -> int:
        return 5
try:
    A().v()               # Wrong: 5 is not callable
except TypeError as e:
    print("Error:", e)
print(A().v)              # Right
```

❌ Mistake 2: Infinite recursion by using the same name for storage
✅ Correct: store in `_name`

```python
class Bad:
    @property
    def v(self) -> int:
        return self.v     # Wrong: calls itself
try:
    Bad().v
except RecursionError:
    print("RecursionError")
class Good:
    def __init__(self) -> None:
        self._v = 1
    @property
    def v(self) -> int:
        return self._v    # Right
print(Good().v)
```

❌ Mistake 3: Putting slow work in a property that is read many times
✅ Correct: use `cached_property`

```python
from functools import cached_property
class R:
    calls = 0
    @property
    def slow(self) -> int:       # Wrong: runs every time
        R.calls += 1
        return 42
    @cached_property
    def fast(self) -> int:       # Right: runs once
        R.calls += 100
        return 42
r = R()
r.slow; r.slow
print(R.calls)
r.fast; r.fast
print(R.calls)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class R:
    def __init__(self):
        self.calls = 0
    @property
    def v(self):
        self.calls += 1
        return self.calls
r = R()
print(r.v, r.v, r.calls)
r.__dict__["v"] = 99
print(r.v)
class S:
    @property
    def v(self):
        return self.v
try:
    S().v
except RecursionError:
    print("RecursionError")
```

Output:
```
1 2 2
3
RecursionError
```

Answer: Each read of `r.v` runs the function, so `r.v` gives 1, then 2, and `r.calls` is 2: output `1 2 2`. Writing `v` directly into `r.__dict__` does not help: a property is a data descriptor, so it always beats the instance dictionary. Reading `r.v` runs the function again (calls becomes 3) and returns `3`, not 99. Class `S` returns `self.v` which calls the same property again forever, so Python raises `RecursionError`.

---

## ⚫ Interview Questions + Answers

Q1: What is a property and why use it?
A1: A property exposes a method as an attribute. Use it for validation, read-only values, computed fields and for evolving a public attribute into logic without breaking callers.

Q2: How do you make a read-only attribute?
A2: Define only the getter with `@property`. Assigning raises `AttributeError: property 'x' of 'C' object has no setter`.

Q3: Difference between `@property` and `@cached_property`?
A3: `property` runs the function on every access. `functools.cached_property` runs it once and stores the result in the instance `__dict__`, so later reads are plain attribute reads. It needs a `__dict__` (not slots) and is not thread-locked since Python 3.12.

Q4: Why does a property beat the instance dictionary?
A4: `property` defines both `__get__` and `__set__`, making it a data descriptor, which Python checks before `obj.__dict__`. A non-data descriptor (a plain function) loses to the instance dictionary.

Q5: Should you start with getters and setters in Python?
A5: No. Start with plain public attributes. If you later need validation or computation, convert to a property; callers do not change. This is why Python code has few `get_x()` methods.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Computed values derived from other fields (area, full_name, total)
- Read-only attributes
- Validation on assignment (with a setter)
- Replacing a plain attribute with logic later

❌ Avoid when:
- Expensive or network operations hidden behind attribute syntax (surprising); use a method
- Anything that can fail often; a method name like `fetch()` is clearer
- Simple data with no rules; keep a plain attribute

---

## 📊 Visual Diagram
```
c.area
  |
  v
type(c).__mro__ -> finds `area` = property object (data descriptor)
  |
  | data descriptor wins over c.__dict__["area"]
  v
property.__get__(c) -> calls  area(self=c)  -> returns value

c.area = 5 -> property.__set__ -> no setter -> AttributeError
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Property | Method used like an attribute | Attribute की तरह इस्तेमाल होने वाला method |
| Getter | Reads the value | Value पढ़ने वाला |
| Computed attribute | Value calculated on access | Access पर निकलने वाली value |
| Read-only | Cannot be assigned | जिसमें value डाली नहीं जा सकती |
| cached_property | Computed once, then stored | एक बार compute, फिर stored |
| Data descriptor | Descriptor with get and set | get और set वाला descriptor |

---

## ⚡ 3-Line Summary
English: `@property` lets a method be read like an attribute, giving computed and read-only values. It beats the instance dictionary because it is a data descriptor. Use `_name` for storage and `cached_property` for expensive values.
Hindi: `@property` method को attribute की तरह पढ़ने देता है, जिससे computed और read-only values मिलते हैं। यह data descriptor है इसलिए instance dictionary से ऊपर चलता है। Storage के लिए `_name` और भारी values के लिए `cached_property` लें।

---

## ➡️ Next Topic
**089. Getter + Setter + Deleter** — the full property trio: validate on assignment and clean up on `del`.
