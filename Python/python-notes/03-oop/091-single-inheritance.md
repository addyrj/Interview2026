---

# 091. Single Inheritance
# हिंदी में: Single Inheritance (एकल विरासत)

---

## 🔵 Simple Definition (English)
Single inheritance means a class has exactly one direct parent: `class Bike(Vehicle)`. It is the simplest and safest form of inheritance. Chains like Scooter to Bike to Vehicle are called multilevel inheritance.

## 🔵 सरल परिभाषा (Hindi)
Single inheritance में class का सिर्फ एक direct parent होता है: `class Bike(Vehicle)`। यह inheritance का सबसे सरल और सुरक्षित रूप है। Scooter से Bike से Vehicle जैसी chain को multilevel inheritance कहते हैं।

---

## 🔴 Problem it Solves
You need a specialised version of an existing class: a Bike is a Vehicle with 2 wheels, a `UserRepo` is a `Repository` with extra queries. Rewriting the whole class wastes effort. Single inheritance gives a clear, linear line of ancestors, so there is no doubt where a method comes from, unlike multiple inheritance.

## 🔴 यह क्यों बना? (Hindi)
आपको मौजूदा class का specialised रूप चाहिए: Bike दो पहियों वाला Vehicle है, `UserRepo` अतिरिक्त queries वाला `Repository` है। पूरी class दोबारा लिखना बेकार है। Single inheritance ancestors की सीधी रेखा देता है, इसलिए method कहाँ से आया इसमें शक नहीं रहता, multiple inheritance की तरह नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `class Bike(Vehicle)` records one base in `Bike.__bases__`
Step 2 → MRO is a straight line: Bike, Vehicle, object
Step 3 → `Bike('Hero')` runs `Bike.__init__`
Step 4 → `super().__init__(brand, wheels=2)` runs Vehicle's init with changed arguments
Step 5 → Bike adds its own attribute (`has_kick`)
Step 6 → `info()` in Bike calls `super().info()` and extends the text
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `class Bike(Vehicle)` एक base `Bike.__bases__` में रखता है
Step 2 → MRO सीधी रेखा है: Bike, Vehicle, object
Step 3 → `Bike('Hero')` `Bike.__init__` चलाता है
Step 4 → `super().__init__(brand, wheels=2)` बदले arguments के साथ Vehicle का init चलाता है
Step 5 → Bike अपना attribute (`has_kick`) जोड़ता है
Step 6 → Bike का `info()` `super().info()` बुलाकर text बढ़ाता है
```

---

## 🟡 Real World Example
Generic `Repository[T]` with `UserRepo(Repository[str])` adding `find_by_prefix`. An exception family: `AppError` as the base, `NotFound` as its child, handled by one FastAPI exception handler. Django models: `class Post(models.Model)`. Pydantic: `class UserOut(UserBase)`.

## 🟡 Real Example Hindi mein
Generic `Repository[T]` और उसका `UserRepo(Repository[str])` जो `find_by_prefix` जोड़ता है। Exception family: `AppError` base और उसका child `NotFound`, जिन्हें FastAPI का एक exception handler संभालता है। Django models: `class Post(models.Model)`। Pydantic: `class UserOut(UserBase)`।

---

## 💻 Code Example — Basic
```python
# Basic: single inheritance = exactly one parent
class Vehicle:                                    # parent
    def __init__(self, brand: str, wheels: int = 4) -> None:
        self.brand: str = brand
        self.wheels: int = wheels

    def info(self) -> str:
        return f"{self.brand} with {self.wheels} wheels"


class Bike(Vehicle):                              # one parent only
    def __init__(self, brand: str) -> None:
        super().__init__(brand, wheels=2)         # reuse parent init with 2 wheels
        self.has_kick: bool = True

    def info(self) -> str:                        # extend parent output
        return super().info() + " (bike)"


class Scooter(Bike):                              # multilevel chain: Scooter -> Bike -> Vehicle
    pass


b = Bike("Hero")
print(b.info())
print(Scooter("Ola").info())
print([c.__name__ for c in Scooter.__mro__])
print(Vehicle.__subclasses__()[0].__name__, Bike.__bases__)
print(hasattr(b, "has_kick"), hasattr(Vehicle("X"), "has_kick"))

# Output:
# Hero with 2 wheels (bike)
# Ola with 2 wheels (bike)
# ['Scooter', 'Bike', 'Vehicle', 'object']
# Bike (<class '__main__.Vehicle'>,)
# True False
```

## 💻 Code Example — Advanced
```python
# Advanced: a repository base class with typed subclasses (single inheritance + generics)
from __future__ import annotations
from typing import Generic, TypeVar

T = TypeVar("T")                                  # item type


class Repository(Generic[T]):                     # generic base: works for any entity
    def __init__(self) -> None:
        self._store: dict[int, T] = {}            # fake database
        self._next: int = 1

    def add(self, item: T) -> int:
        pk = self._next
        self._store[pk] = item
        self._next += 1
        return pk

    def get(self, pk: int) -> T:
        try:
            return self._store[pk]
        except KeyError:
            raise LookupError(f"{type(self).__name__}: id {pk} not found") from None

    def all(self) -> list[T]:
        return list(self._store.values())


class UserRepo(Repository[str]):                  # single parent, adds one method
    def find_by_prefix(self, p: str) -> list[str]:
        return [u for u in self.all() if u.startswith(p)]


repo = UserRepo()
repo.add("asha"); repo.add("ashok"); repo.add("raj")
print(repo.find_by_prefix("ash"), repo.get(3))
try:
    repo.get(99)
except LookupError as e:
    print("Error:", e)


class A:
    def __init__(self) -> None:
        print("A.init")


class B(A):
    def __init__(self) -> None:
        print("B.init")                            # forgot super().__init__()


B()                                               # A.init never runs -> parent state missing
print(UserRepo.__mro__[1].__name__)

# Output:
# ['asha', 'ashok'] raj
# Error: UserRepo: id 99 not found
# B.init
# Repository
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Syntax | `class B(A):` | `class B extends A` |
| Parent init | `super().__init__()` | `super()` mandatory |
| Multilevel chain | allowed | allowed |
| Forgot parent init | silent bug | ReferenceError on `this` |
| Parents allowed | one or many | exactly one |

```python
# Python way
class Vehicle:
    def __init__(self, brand: str) -> None:
        self.brand = brand

class Bike(Vehicle):
    def __init__(self, brand: str) -> None:
        super().__init__(brand)
        self.wheels = 2

print(Bike("Hero").wheels)
```
```javascript
// JavaScript way
class Vehicle {
  constructor(brand) { this.brand = brand; }
}
class Bike extends Vehicle {
  constructor(brand) {
    super(brand);           // must come before `this`
    this.wheels = 2;
  }
}
console.log(new Bike("Hero").wheels);
```

Key difference: JS only has single inheritance, so it is the default model there. In Python it is the style you should prefer as well, because it keeps the MRO simple. JS forces `super()` before `this`; Python does not enforce it.

---

## 🟠 FastAPI Connection
The cleanest FastAPI use: a hierarchy of exceptions with one handler. The example registers a handler for the base `AppError`, and every child (NotFound) automatically gets the same handling with its own status code.

```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()


class AppError(Exception):                        # base error
    status = 500


class NotFound(AppError):                         # single inheritance gives a family
    status = 404


@app.exception_handler(AppError)                  # one handler covers all children
async def handle(request, exc: AppError):
    from fastapi.responses import JSONResponse
    return JSONResponse({"error": type(exc).__name__}, status_code=exc.status)


@app.get("/x")
def x():
    raise NotFound()


r = TestClient(app).get("/x")
print(r.status_code, r.json())

# Output:
# 404 {'error': 'NotFound'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `super().__init__()`
✅ Correct: call it so the parent's attributes exist

```python
class A:
    def __init__(self) -> None:
        print("A.init")
class B(A):
    def __init__(self) -> None:
        print("B.init")              # Wrong: A.init never runs
class C(A):
    def __init__(self) -> None:
        super().__init__()           # Right
        print("C.init")
B(); C()
```

❌ Mistake 2: Calling the parent by name and breaking later refactors
✅ Correct: use `super()`

```python
class P:
    def hi(self) -> str:
        return "P"
class C(P):
    def hi(self) -> str:
        return P.hi(self) + "C"      # Wrong: hard-coded parent
class D(P):
    def hi(self) -> str:
        return super().hi() + "D"    # Right
print(C().hi(), D().hi())
```

❌ Mistake 3: Overriding with a different signature
✅ Correct: keep the parent's parameters (Liskov rule)

```python
class Base:
    def run(self, x: int) -> int:
        return x
class Bad(Base):
    def run(self) -> int:            # Wrong: callers using run(5) now break
        return 0
class Good(Base):
    def run(self, x: int, extra: int = 0) -> int:   # Right: compatible
        return x + extra
try:
    Bad().run(5)
except TypeError as e:
    print("Error:", e)
print(Good().run(5))
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class P:
    x = "P"
    def get(self):
        return self.x
class C(P):
    x = "C"
    def get(self):
        return super().get() + "!"
print(C().get(), P().get())
C.x = "changed"
print(C().get())
del C.x
print(C().get())
print(C.__bases__, C.__base__.__name__)
```

Output:
```
C! P
changed!
P!
(<class '__main__.P'>,) P
```

Answer: `super().get()` runs P's `get`, but `self` is still a `C` object, so `self.x` finds `C.x` = `C`; result `C!`, while `P().get()` is `P`. Setting `C.x = 'changed'` changes what `self.x` finds: `changed!`. After `del C.x` the attribute disappears from C and the lookup falls back to P: `P!`. `__bases__` is a tuple with the direct parents, `__base__` is the single main parent.

---

## ⚫ Interview Questions + Answers

Q1: What is single inheritance?
A1: A class that derives from exactly one parent class. Multilevel inheritance is a chain of single inheritance (A to B to C).

Q2: What does `super()` return?
A2: A proxy object that delegates attribute lookup to the next class after the current one in the MRO of `type(self)`. In single inheritance this is simply the parent.

Q3: Why prefer `super()` to `Parent.method(self)`?
A3: It follows the MRO, so it keeps working if the base class is renamed or if multiple inheritance is introduced later, and it avoids calling a shared base twice.

Q4: Is `object` always a parent?
A4: Yes. Every class implicitly inherits from `object` (Python 3), so `class A:` equals `class A(object):`. It is the last item of every MRO.

Q5: How do you stop a class from being subclassed?
A5: Python has no `final` keyword at runtime; use `typing.final` for type checkers, or raise an error in `__init_subclass__`. It is mainly a documentation tool.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A clear IS-A relationship with one parent
- Extending framework base classes (Exception, BaseModel)
- Generic repositories and services with small additions
- Keeping the MRO simple and predictable

❌ Avoid when:
- Deep chains of 4 or more levels; flatten or use composition
- Child that removes or disables parent behaviour
- Overrides that change method signatures

---

## 📊 Visual Diagram
```
object
  ^
Vehicle        brand, wheels, info()
  ^
Bike           + has_kick, info() -> super().info() + " (bike)"
  ^
Scooter        (inherits everything)

Scooter.__mro__ = (Scooter, Bike, Vehicle, object)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Single inheritance | One direct parent | एक direct parent |
| Multilevel | Chain of parents | Parents की chain |
| Base class | Top class others derive from | सबसे ऊपर की class |
| Derived class | Class built on a base | Base पर बनी class |
| Liskov principle | Child must work wherever parent works | Child parent की जगह चल सके |
| `object` | Root of all classes | सभी classes की जड़ |

---

## ⚡ 3-Line Summary
English: Single inheritance gives a class exactly one parent, keeping the MRO a straight line. Use `super().__init__()` and keep overridden signatures compatible. It is the safest form of inheritance.
Hindi: Single inheritance में class का एक ही parent होता है, इसलिए MRO सीधी रेखा रहती है। `super().__init__()` लगाएं और override की signature compatible रखें। यह inheritance का सबसे सुरक्षित रूप है।

---

## ➡️ Next Topic
**092. Multiple Inheritance** — a class with several parents, the diamond problem, and mixins.
