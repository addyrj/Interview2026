---

# 087. Static Methods (@staticmethod)
# हिंदी में: Static Methods (@staticmethod)

---

## 🔵 Simple Definition (English)
A static method is a normal function that lives inside a class for organisation. It receives no automatic `self` or `cls`, so it cannot touch the object or the class. You call it as `Class.method(...)`.

## 🔵 सरल परिभाषा (Hindi)
Static method class के अंदर रखा सामान्य function है जो सिर्फ organisation के लिए है। इसे अपने आप `self` या `cls` नहीं मिलता, इसलिए यह object या class को नहीं छू सकता। इसे `Class.method(...)` से call करते हैं।

---

## 🔴 Problem it Solves
Some helper logic belongs to a class conceptually (a PAN validator in an `Invoice` module, a unit conversion in `Temperature`) but needs no object data. Placing it as a loose global function scatters related code; making it an instance method wastes a `self` that is never used. A static method keeps the helper next to the class and tells the reader: this does not use state.

## 🔴 यह क्यों बना? (Hindi)
कुछ helper logic class से जुड़ा होता है (`Invoice` में PAN validator, `Temperature` में unit conversion) लेकिन उसे object का data नहीं चाहिए। उसे अलग global function बनाने से related code बिखर जाता है; instance method बनाने से बेकार `self` आता है। Static method helper को class के पास रखता है और पाठक को बताता है कि यह state use नहीं करता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `@staticmethod` wraps the function in a staticmethod descriptor
Step 2 → You call `MathUtil.is_even(4)` or `obj.is_even(4)`
Step 3 → Python finds the descriptor and returns the ORIGINAL function unchanged
Step 4 → No binding happens: nothing is passed automatically
Step 5 → The function runs only with the arguments you pass
Step 6 → Result is returned; no object or class state was touched
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `@staticmethod` function को staticmethod descriptor में लपेटता है
Step 2 → आप `MathUtil.is_even(4)` या `obj.is_even(4)` call करते हैं
Step 3 → Python descriptor पाकर ORIGINAL function जैसा है वैसा लौटाता है
Step 4 → कोई binding नहीं: अपने आप कुछ pass नहीं होता
Step 5 → Function सिर्फ आपके दिए arguments से चलता है
Step 6 → Result return होता है; object या class की state नहीं छुई गई
```

---

## 🟡 Real World Example
A billing module has `Invoice.gst(amount)`, a KYC module has `Validators.is_pan(value)`, and a security helper has `Security.sha256(text)`. These are pure functions: same input, same output, easy to unit test with no objects.

## 🟡 Real Example Hindi mein
Billing module में `Invoice.gst(amount)`, KYC module में `Validators.is_pan(value)` और security helper में `Security.sha256(text)` होते हैं। ये pure functions हैं: same input, same output, बिना objects के unit test आसान।

---

## 💻 Code Example — Basic
```python
# Basic: @staticmethod = plain function placed inside a class (no self, no cls)
class MathUtil:                                   # a namespace for helpers
    @staticmethod                                 # no automatic first argument
    def is_even(n: int) -> bool:                  # does not need any object
        return n % 2 == 0

    @staticmethod
    def clamp(x: float, lo: float, hi: float) -> float:   # limit x to a range
        return max(lo, min(x, hi))


print(MathUtil.is_even(4))                        # call on the class
print(MathUtil().clamp(15, 0, 10))                # call via an instance also works
print(type(MathUtil.is_even))                     # plain function, nothing is bound
print(type(MathUtil.__dict__["is_even"]).__name__)   # stored as a staticmethod object


class Temperature:                                # static vs class vs instance
    def __init__(self, c: float) -> None:
        self.c = c

    @staticmethod
    def c_to_f(c: float) -> float:                # pure conversion, related to the class topic
        return c * 9 / 5 + 32

    def as_f(self) -> float:                      # instance method uses the static helper
        return Temperature.c_to_f(self.c)


print(Temperature.c_to_f(100), Temperature(37).as_f())

# Output:
# True
# 10
# <class 'function'>
# staticmethod
# 212.0 98.6
```

## 💻 Code Example — Advanced
```python
# Advanced: validators and parsers as static methods, easy to test without objects
from __future__ import annotations
import re
from datetime import date


class Validators:                                 # grouped pure functions
    _PAN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")     # Indian PAN card format

    @staticmethod
    def is_pan(value: str) -> bool:
        return bool(Validators._PAN.match(value))

    @staticmethod
    def is_adult(dob: date, today: date) -> bool:     # today passed in -> deterministic tests
        years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return years >= 18


class Invoice:
    def __init__(self, amount: float, pan: str) -> None:
        if not Validators.is_pan(pan):            # reuse the static validator
            raise ValueError(f"invalid PAN {pan}")
        self.amount, self.pan = amount, pan

    @staticmethod
    def gst(amount: float, rate: float = 0.18) -> float:  # does not touch the object
        return round(amount * rate, 2)

    def total(self) -> float:
        return self.amount + self.gst(self.amount)    # call static via self works too


print(Validators.is_pan("ABCDE1234F"), Validators.is_pan("abc"))
print(Validators.is_adult(date(2010, 6, 1), date(2026, 5, 31)))
print(Validators.is_adult(date(2000, 6, 1), date(2026, 5, 31)))
print(Invoice(1000, "ABCDE1234F").total())
try:
    Invoice(10, "BAD")
except ValueError as e:
    print("Error:", e)


class Base:
    @staticmethod
    def who() -> str:
        return "Base"                             # static cannot know the subclass

    @classmethod
    def who2(cls) -> str:
        return cls.__name__                       # class method does


class Child(Base): ...


print(Child.who(), Child.who2())                  # Base Child

# Output:
# True False
# False
# True
# 1180.0
# Error: invalid PAN BAD
# Base Child
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Syntax | `@staticmethod` | `static f() {}` |
| Receives class/object? | neither | may use `this` (= class) |
| Call | `Class.f()` or `obj.f()` | `Class.f()` only |
| Python alternative | module-level function | module function |

```python
# Python way
class MathUtil:
    @staticmethod
    def is_even(n: int) -> bool:
        return n % 2 == 0

print(MathUtil.is_even(4))
```
```javascript
// JavaScript way
class MathUtil {
  static isEven(n) { return n % 2 === 0; }
}
console.log(MathUtil.isEven(4));
```

Key difference: in Python, a module-level function is usually better than a static method; classes are not required as namespaces. JS `static` is the only way to attach a function to a class, so it is used more often. In Python use `@staticmethod` only when the helper really belongs to the class.

---

## 🟠 FastAPI Connection
Static methods are good for stateless helpers used by routes and services: hashing, slug creation, validators. They need no dependency injection, so they are trivial to test with `pytest`.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
import hashlib

app = FastAPI()


class Security:
    @staticmethod
    def sha256(text: str) -> str:                 # stateless helper
        return hashlib.sha256(text.encode()).hexdigest()


@app.get("/hash/{text}")
def hash_text(text: str) -> dict[str, str]:
    return {"sha256": Security.sha256(text)[:12]}


print(TestClient(app).get("/hash/hello").json())

# Output:
# {'sha256': '2cf24dba5fb0'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `@staticmethod` when the method has no `self`
✅ Correct: add the decorator

```python
class A:
    def f(x):                      # Wrong: x becomes the instance
        return x * 2
try:
    A().f(5)
except TypeError as e:
    print("Error:", e)
class B:
    @staticmethod
    def f(x: int) -> int:          # Right
        return x * 2
print(B().f(5))
```

❌ Mistake 2: Hard-coding the class name inside a static method that should follow subclasses
✅ Correct: use a classmethod

```python
class Base:
    @staticmethod
    def who() -> str:
        return "Base"
    @classmethod
    def who2(cls) -> str:
        return cls.__name__
class Child(Base): ...
print(Child.who(), Child.who2())
```

❌ Mistake 3: Trying to use instance data in a static method
✅ Correct: make it an instance method

```python
class U:
    def __init__(self) -> None:
        self.n = 1
    @staticmethod
    def get() -> int:
        return self.n              # Wrong: self is undefined
try:
    U.get()
except NameError as e:
    print("Error:", e)
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class T:
    @staticmethod
    def f(x):
        return x * 2
    g = f
    h = staticmethod(lambda x: x + 1)
print(T.g(2), T().f(3), T.h(4))
class U:
    def f(x):
        return x
print(U.f(5))
try:
    U().f(5)
except TypeError as e:
    print("TypeError")
```

Output:
```
4 6 5
5
TypeError
```

Answer: Inside the class body `g = f` copies the staticmethod object, so `T.g(2)` is 4; `T().f(3)` is 6 because static methods ignore the instance; `T.h(4)` is 5 (wrapping a lambda with `staticmethod()` works the same as the decorator). In class `U`, `f(x)` has no decorator: called on the class it is a plain function, so `U.f(5)` returns 5, but `U().f(5)` passes the instance AND 5, giving two arguments to a one-parameter function: TypeError.

---

## ⚫ Interview Questions + Answers

Q1: What is a static method?
A1: A function inside a class that receives neither `self` nor `cls`. It is called on the class or an instance and behaves exactly like a normal function.

Q2: When should you choose staticmethod over a module function?
A2: When the helper is conceptually tied to the class and you want it discoverable as `Invoice.gst`, or when subclasses should be able to override it. Otherwise a module-level function is simpler and more Pythonic.

Q3: Static vs class method?
A3: A class method gets `cls` and can create instances or read class data; a static method gets nothing. If you find yourself writing the class name inside a static method, you probably want a class method.

Q4: Can a static method access class variables?
A4: Only by naming the class explicitly (`Config.rate`). It has no `cls`, so it will not follow subclasses. Use a classmethod for that.

Q5: Does a static method create a bound method?
A5: No. `type(Class.m)` is a plain `function`, and `Class.__dict__['m']` is a `staticmethod` object. The descriptor returns the original function without binding.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Pure helper related to the class (validators, converters)
- Logic you want to unit test without creating objects
- Utility grouped in a class namespace for discoverability

❌ Avoid when:
- You need object data (use an instance method)
- You need the class or subclasses (use a classmethod)
- A plain module-level function would be clearer

---

## 📊 Visual Diagram
```
class Invoice
 |-- instance method  gets self  -> object data
 |-- @classmethod     gets cls   -> class data / factories
 |-- @staticmethod    gets NOTHING -> pure helper

Invoice.gst(1000)  -->  plain function  -->  180.0
(no self, no cls, no state)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Static method | Function inside class, no self/cls | Class में रखा function, बिना self/cls |
| Pure function | Same input gives same output | Same input, same output वाला function |
| Namespace | Named group of names | नामों का समूह |
| Stateless | Holds no data between calls | कोई data नहीं रखता |
| Helper / utility | Small supporting function | छोटा सहायक function |
| Descriptor | Object controlling access | Access नियंत्रित करने वाला object |

---

## ⚡ 3-Line Summary
English: A static method is a plain function placed inside a class; it gets no `self` and no `cls`. Use it for stateless helpers tied to the class. If you need the class or subclasses, use a classmethod instead.
Hindi: Static method class के अंदर रखा सामान्य function है; इसे `self` या `cls` नहीं मिलता। Class से जुड़े stateless helpers के लिए इस्तेमाल करें। Class या subclasses चाहिए तो classmethod लें।

---

## ➡️ Next Topic
**088. Properties (`@property`)** — methods that behave like attributes, giving validation and computed values without changing the calling code.
