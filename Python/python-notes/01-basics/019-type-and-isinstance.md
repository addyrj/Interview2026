---

# 019. type() + isinstance()
# हिंदी में: type() और isinstance() — type पहचानना

---

## 🔵 Simple Definition (English)
`type(x)` returns the exact class of an object. `isinstance(x, Class)` returns True if `x` is an instance of `Class` or of any subclass of it. Use `isinstance` for checks and `type` for inspecting or creating classes.

## 🔵 सरल परिभाषा (Hindi)
`type(x)` object की exact class बताता है। `isinstance(x, Class)` True देता है अगर `x` उस `Class` का या उसकी किसी subclass का instance हो। Checks के लिए `isinstance` use करें, `type` inspect करने या class बनाने के लिए।

---

## 🔴 Problem it Solves
Python is dynamically typed, so a function may receive an int, a str or None. You need a safe way to ask "what is this?" at runtime — to validate input, branch on type, or debug. `type()` and `isinstance()` answer that, and `isinstance` respects inheritance.

## 🔴 यह क्यों बना? (Hindi)
Python dynamically typed है, function को int, str या None कुछ भी मिल सकता है। Runtime पर पूछने का तरीका चाहिए "यह क्या है?" — input validate करने, type के हिसाब से branch करने, debug करने के लिए। `type()` और `isinstance()` यही करते हैं, और `isinstance` inheritance को समझता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every object stores a pointer to its class (obj.__class__)
Step 2 → type(obj) just returns that class
Step 3 → isinstance(obj, C) walks obj's class MRO (parent chain)
Step 4 → If C appears anywhere in the chain -> True
Step 5 → If C is a tuple, any match is enough
Step 6 → ABCs (like Iterable) can say True via __instancecheck__
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर object अपनी class का pointer रखता है (obj.__class__)
Step 2 → type(obj) वही class लौटाता है
Step 3 → isinstance(obj, C) class की MRO (parent chain) में देखता है
Step 4 → C chain में कहीं भी मिले -> True
Step 5 → C अगर tuple है तो कोई एक match काफी है
Step 6 → ABCs (जैसे Iterable) __instancecheck__ से भी True दे सकते हैं
```

---

## 🟡 Real World Example
A payment service receives `amount` that may be `int`, `float` or `str` from different clients — it checks `isinstance(amount, (int, float))` before calculating GST. A logging library prints `type(err).__name__` to show the exception class. Pydantic uses these checks internally while validating.

## 🟡 Real Example Hindi mein
Payment service को अलग clients से `amount` int, float या str में मिल सकता है — GST calculate करने से पहले `isinstance(amount, (int, float))` check होता है। Logging library exception class दिखाने के लिए `type(err).__name__` print करती है। Pydantic validation में यही checks अंदर use करता है।

---

## 💻 Code Example — Basic
```python
# type() and isinstance() basics

# type() returns the class:
print(type(10))                     # <class 'int'>
print(type("hi"))                   # <class 'str'>
print(type([1, 2]))                 # <class 'list'>
print(type(None))                   # <class 'NoneType'>
print(type(10).__name__)            # int

# isinstance() checks type (and subclasses):
age: int = 25                       # an int
print(isinstance(age, int))         # True
print(isinstance(age, str))         # False

# Tuple of types = "any of these":
print(isinstance(3.5, (int, float)))    # True

# bool is a subclass of int:
print(isinstance(True, int))        # True
print(type(True) == int)            # False
print(type(True) is bool)           # True

# Inheritance example:
class Animal:                       # parent class
    pass

class Dog(Animal):                  # child class
    pass

d: Dog = Dog()                      # create a Dog
print(isinstance(d, Dog))           # True
print(isinstance(d, Animal))        # True  (subclass counts)
print(type(d) == Animal)            # False (exact type only)
print(issubclass(Dog, Animal))      # True  (class vs class)
```

## 💻 Code Example — Advanced
```python
# Advanced — validation, ABCs, and type() as a class factory
from collections.abc import Iterable, Mapping
from typing import Any


def to_amount(value: Any) -> float:
    """Convert incoming value to float with strict type checks."""
    if isinstance(value, bool):                  # bool is int, so reject it first
        raise TypeError("bool is not a valid amount")
    if isinstance(value, (int, float)):          # numbers are fine
        return float(value)
    if isinstance(value, str):                   # numeric string
        try:
            return float(value)                  # try parsing
        except ValueError:
            raise ValueError(f"not numeric: {value!r}") from None
    raise TypeError(f"unsupported type: {type(value).__name__}")


def describe(obj: object) -> str:
    """Describe objects using ABCs (duck-typing friendly)."""
    if isinstance(obj, (str, bytes)):            # str is Iterable, so check first
        return "text"
    if isinstance(obj, Mapping):                 # dict-like
        return "mapping"
    if isinstance(obj, Iterable):                # list, tuple, set, generator...
        return "iterable"
    return "scalar"


def main() -> None:
    print(to_amount(10))                         # 10.0
    print(to_amount("99.5"))                     # 99.5

    for bad in (True, None, "abc"):              # three invalid inputs
        try:
            to_amount(bad)
        except (TypeError, ValueError) as exc:   # catch both error kinds
            print(type(exc).__name__, "->", exc)
    # TypeError -> bool is not a valid amount
    # TypeError -> unsupported type: NoneType
    # ValueError -> not numeric: 'abc'

    print(describe("hi"))                        # text
    print(describe({"a": 1}))                    # mapping
    print(describe([1, 2]))                      # iterable
    print(describe(42))                          # scalar

    # type() with 3 args builds a class dynamically:
    Point = type("Point", (), {"x": 0, "y": 0})  # name, bases, attributes
    p = Point()                                  # instance of dynamic class
    print(type(p).__name__, p.x, p.y)            # Point 0 0

    # Everything is an object; classes are instances of `type`:
    print(type(int))                             # <class 'type'>
    print(type(type))                            # <class 'type'>


if __name__ == "__main__":
    main()
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
x = [1, 2]
print(type(x))                       # <class 'list'>
print(isinstance(x, list))           # True
print(isinstance(5, (int, float)))   # True
print(isinstance(None, type(None)))  # True
```
```javascript
// JavaScript
const x = [1, 2];
console.log(typeof x);               // "object"  (not helpful!)
console.log(Array.isArray(x));       // true
console.log(x instanceof Array);     // true
console.log(typeof null);            // "object"  (famous bug)
console.log(typeof 5 === "number");  // true
```

Key differences: Python `type()` gives the precise class (`list`), JS `typeof` gives only broad strings (`"object"`). JS `instanceof` ~ Python `isinstance`. Python accepts a tuple of classes in one call.

---

## 🟠 FastAPI Connection
FastAPI and Pydantic read type hints with `typing.get_type_hints` and validate with isinstance-like checks. In your own code you often use `isinstance` for dependency results, exception handlers and polymorphic responses.

```python
# FastAPI example (needs: pip install fastapi)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()                                          # create app


class DomainError(Exception):                            # base custom error
    pass


class NotFound(DomainError):                             # child error
    pass


@app.exception_handler(DomainError)                      # handles DomainError AND subclasses
async def domain_handler(request: Request, exc: DomainError) -> JSONResponse:
    status = 404 if isinstance(exc, NotFound) else 400   # choose code by type
    return JSONResponse({"error": type(exc).__name__}, status_code=status)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `type(x) == Class` for checks
```python
# Wrong — breaks with subclasses (and bool):
class MyInt(int): ...
print(type(MyInt(5)) == int)       # False

# Correct:
print(isinstance(MyInt(5), int))   # True
```

❌ Mistake 2: Forgetting bool is an int
```python
# Wrong — True passes as a number:
def double(n):
    if isinstance(n, int):
        return n * 2
print(double(True))                # 2

# Correct — exclude bool first:
def double(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("need int")
    return n * 2
```

❌ Mistake 3: Passing a list instead of a tuple
```python
# Wrong:
# isinstance(5, [int, float])    # TypeError: arg 2 must be a type... 

# Correct:
isinstance(5, (int, float))      # True
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A: pass
class B(A): pass

b = B()
print(type(b) is A)
print(isinstance(b, A))
print(type(type(b)))
print(isinstance(A, object), isinstance(object, type))
```
Answer: `False`, `True`, `<class 'type'>`, `True True`. `type(b)` is exactly `B`, so `is A` fails. `isinstance` follows inheritance. The type of a class is `type`. Every class is an `object`, and `object` itself is an instance of `type` — a circular design in Python's core.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `type()` and `isinstance()`?
A1: `type(x)` returns the exact class and `type(x) == C` is only True for that exact class. `isinstance(x, C)` is True for C and all subclasses, and accepts a tuple. Prefer `isinstance` for checks (PEP 8 recommends it) because it supports inheritance and ABCs.

Q2: What is the difference between `isinstance` and `issubclass`?
A2: `isinstance(obj, C)` takes an object. `issubclass(K, C)` takes a class and checks if K inherits from C. Example: `issubclass(bool, int)` is True; `isinstance(True, int)` is True.

Q3: Should you check types a lot in Python?
A3: Usually no — Python prefers duck typing ("EAFP": easier to ask forgiveness than permission). Use try/except or just call the method. Use `isinstance` at boundaries: validating external input, polymorphic dispatch, or error handlers. Inside code, rely on type hints + mypy.

Q4: What does `type(name, bases, dict)` do?
A4: With 3 arguments, `type` creates a new class dynamically. `type("Point", (), {"x": 0})` is the same as `class Point: x = 0`. This is how metaclasses and ORMs build classes at runtime. `class` statements actually call `type` behind the scenes.

Q5: Why does `isinstance("abc", Iterable)` return True?
A5: `collections.abc.Iterable` uses `__subclasshook__` to check if the class defines `__iter__`. Strings have it, so True. That is "virtual subclassing" — no real inheritance needed. It is why you check `str` before `Iterable` when you want to treat strings as scalars.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Validating external input (API, files, JSON)
- Branching on several accepted types (`(int, float)`)
- Exception handlers choosing a response by error class
- Debugging with `type(x).__name__`

❌ Avoid when:
- Duck typing works — just call the method
- Using `type(x) == Class` (use `isinstance`)
- Long `if/elif isinstance` chains — use polymorphism or `match`/`singledispatch`

---

## 📊 Visual Diagram
```
        object
          |
        Animal            isinstance(d, Dog)    -> True
          |               isinstance(d, Animal) -> True
         Dog              type(d) is Dog        -> True
          |               type(d) is Animal     -> False
          d (instance)

 instance --type()--> class --type()--> type --type()--> type
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| type() | Exact class of object | Object की exact class |
| isinstance() | Instance of class or subclass | Class/subclass का instance? |
| issubclass() | Class inherits from class | Class दूसरी से inherit करती है? |
| MRO | Method resolution order | Parent classes का क्रम |
| ABC | Abstract base class | Abstract base class |
| Duck typing | Check behavior, not type | Behavior देखो, type नहीं |

---

## ⚡ 3-Line Summary
English: `type(x)` gives the exact class; `isinstance(x, C)` also accepts subclasses and tuples of classes. Prefer `isinstance` for checks, and remember `bool` is a subclass of `int`. Use checks at boundaries, duck typing inside.
Hindi: `type(x)` exact class देता है; `isinstance(x, C)` subclasses और tuple भी accept करता है। Checks के लिए `isinstance` चुनें, और याद रखें `bool`, `int` की subclass है। Boundaries पर checks, अंदर duck typing।

---

## ➡️ Next Topic
**020. Type Hints (Python 3.5+)** — how to declare expected types so tools and FastAPI can use them.
