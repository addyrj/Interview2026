---

# 090. Inheritance — Complete Guide
# हिंदी में: Inheritance (विरासत) — पूरी Guide

---

## 🔵 Simple Definition (English)
Inheritance lets a new class (child) reuse the attributes and methods of an existing class (parent). The child can add new behaviour or override the parent's. It models an IS-A relationship: a Dog is an Animal.

## 🔵 सरल परिभाषा (Hindi)
Inheritance में नई class (child) किसी मौजूदा class (parent) के attributes और methods दोबारा इस्तेमाल करती है। Child नया behaviour जोड़ सकती है या parent का बदल सकती है। यह IS-A रिश्ता दिखाता है: Dog एक Animal है।

---

## 🔴 Problem it Solves
Many classes share the same code: User, Admin and Customer all have name, email and login. Copy-pasting means one bug fix must be repeated everywhere. Inheritance puts shared code in one base class and lets children specialise. It also gives polymorphism: code written for the parent works with any child.

## 🔴 यह क्यों बना? (Hindi)
कई classes में एक जैसा code होता है: User, Admin और Customer तीनों में name, email और login है। Copy-paste करने पर एक bug fix हर जगह दोहराना पड़ता है। Inheritance साझा code को एक base class में रखता है और children उसे specialise करते हैं। इससे polymorphism भी मिलता है: parent के लिए लिखा code किसी भी child के साथ चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `class Dog(Animal):` stores Animal in `Dog.__bases__`
Step 2 → Python computes the MRO: Dog, Animal, object
Step 3 → `d.speak()` searches the object, then each class in MRO order
Step 4 → First match wins; a method defined in Dog overrides Animal's
Step 5 → `super()` jumps to the next class in the MRO to reuse parent code
Step 6 → Abstract base classes (`ABC`) force children to implement required methods
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `class Dog(Animal):` Animal को `Dog.__bases__` में रखता है
Step 2 → Python MRO निकालता है: Dog, Animal, object
Step 3 → `d.speak()` पहले object फिर MRO के क्रम में हर class में ढूँढता है
Step 4 → पहला match जीतता है; Dog का method Animal वाले को override करता है
Step 5 → `super()` MRO की अगली class पर जाकर parent का code reuse करता है
Step 6 → Abstract base classes (`ABC`) children को ज़रूरी methods लिखने पर मजबूर करती हैं
```

---

## 🟡 Real World Example
A payments app defines `PaymentGateway` (abstract) with `pay()` and children `Razorpay`, `Stripe`, `PayU`. Checkout code only knows `PaymentGateway`. In FastAPI, `UserBase` holds shared fields, `UserCreate` adds a password and `UserOut` adds an id. Custom exceptions inherit from one `AppError` base.

## 🟡 Real Example Hindi mein
Payments app में abstract `PaymentGateway` है जिसमें `pay()` है और children `Razorpay`, `Stripe`, `PayU` हैं। Checkout code सिर्फ `PaymentGateway` जानता है। FastAPI में `UserBase` में साझा fields, `UserCreate` में password और `UserOut` में id जुड़ता है। Custom exceptions एक `AppError` base से बनते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: child class reuses and extends parent class
class Animal:                                     # parent (base) class
    def __init__(self, name: str) -> None:
        self.name: str = name

    def speak(self) -> str:                       # default behaviour
        return f"{self.name} makes a sound"

    def eat(self) -> str:
        return f"{self.name} eats"


class Dog(Animal):                                # child inherits from Animal
    def __init__(self, name: str, breed: str) -> None:
        super().__init__(name)                    # run the parent's __init__
        self.breed: str = breed

    def speak(self) -> str:                       # override
        return f"{self.name} barks"

    def fetch(self) -> str:                       # new behaviour only for Dog
        return f"{self.name} fetches"


d: Dog = Dog("Tommy", "Lab")
print(d.speak(), "|", d.eat(), "|", d.fetch())
print(isinstance(d, Dog), isinstance(d, Animal), issubclass(Dog, Animal))
print(type(d) is Animal, Dog.__bases__, Dog.__mro__[1].__name__)
print(super(Dog, d).speak())                      # call the parent's version explicitly

# Output:
# Tommy barks | Tommy eats | Tommy fetches
# True True True
# False (<class '__main__.Animal'>,) Animal
# Tommy makes a sound
```

## 💻 Code Example — Advanced
```python
# Advanced: template method, abstract base class, and composition vs inheritance
from __future__ import annotations
from abc import ABC, abstractmethod


class PaymentGateway(ABC):                        # contract every gateway must follow
    def pay(self, amount: float) -> str:          # template method: fixed algorithm
        if amount <= 0:
            raise ValueError("amount must be positive")
        ref = self._charge(amount)                # step that children customise
        return self._receipt(ref, amount)

    @abstractmethod
    def _charge(self, amount: float) -> str: ...  # children MUST implement

    def _receipt(self, ref: str, amount: float) -> str:   # shared default
        return f"{type(self).__name__}:{ref}:{amount:.2f}"


class Razorpay(PaymentGateway):
    def _charge(self, amount: float) -> str:
        return "rzp_001"


class Stripe(PaymentGateway):
    def _charge(self, amount: float) -> str:
        return "stp_001"

    def _receipt(self, ref: str, amount: float) -> str:   # override + reuse parent
        return super()._receipt(ref, amount).upper()


for g in (Razorpay(), Stripe()):
    print(g.pay(499))
try:
    PaymentGateway()                              # cannot instantiate an abstract class
except TypeError as e:
    print("Error:", e)
try:
    Stripe().pay(-1)
except ValueError as e:
    print("Error:", e)


class Engine:
    def start(self) -> str:
        return "vroom"


class Car:                                        # HAS-A engine (composition), not IS-A
    def __init__(self) -> None:
        self.engine = Engine()

    def start(self) -> str:
        return self.engine.start()


print(Car().start())
print(issubclass(Razorpay, PaymentGateway), Razorpay.__mro__[-2].__name__)

# Output:
# Razorpay:rzp_001:499.00
# STRIPE:STP_001:499.00
# Error: Can't instantiate abstract class PaymentGateway without an implementation for abstract method '_charge'
# Error: amount must be positive
# vroom
# True ABC
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Syntax | `class B(A):` | `class B extends A {}` |
| Call parent init | `super().__init__(...)` | `super(...)` (required first) |
| Override | same method name | same method name |
| Multiple parents | allowed | not allowed (use mixins) |
| Abstract class | `ABC` + `@abstractmethod` | no keyword; throw error |
| Check relation | `issubclass`, `isinstance` | `instanceof` |

```python
# Python way
class Animal:
    def __init__(self, name: str) -> None:
        self.name = name
    def speak(self) -> str:
        return f"{self.name} makes a sound"

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} barks"

print(Dog("Tommy").speak())
```
```javascript
// JavaScript way
class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a sound`; }
}
class Dog extends Animal {
  speak() { return `${this.name} barks`; }
}
console.log(new Dog("Tommy").speak());
```

Key difference: Python lists the parent in brackets and supports several parents; JS uses `extends` with exactly one. In JS a child constructor must call `super()` before using `this`; in Python forgetting `super().__init__()` is silent and leaves the parent's attributes unset.

---

## 🟠 FastAPI Connection
Pydantic schemas are the biggest everyday use of inheritance in FastAPI: one base with shared fields, children for create, update and output. Exceptions and repository classes also use inheritance.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()


class UserBase(BaseModel):                        # shared fields
    name: str
    email: str


class UserCreate(UserBase):                       # adds password for input
    password: str


class UserOut(UserBase):                          # adds id for output, never password
    id: int


@app.post("/users", response_model=UserOut)
def create(u: UserCreate) -> dict:
    return {**u.model_dump(), "id": 1}


print(TestClient(app).post("/users", json={"name": "A", "email": "a@b.c", "password": "secret"}).json())

# Output:
# {'name': 'A', 'email': 'a@b.c', 'id': 1}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Overriding `__init__` without calling the parent
✅ Correct: call `super().__init__()`

```python
class P:
    def __init__(self) -> None:
        self.ready = True
class C(P):
    def __init__(self) -> None:
        self.extra = 1               # Wrong: parent init skipped
class C2(P):
    def __init__(self) -> None:
        super().__init__()           # Right
        self.extra = 1
print(hasattr(C(), "ready"), hasattr(C2(), "ready"))
```

❌ Mistake 2: Using inheritance for HAS-A relationships
✅ Correct: use composition

```python
class Engine:
    def start(self) -> str:
        return "vroom"
class CarWrong(Engine):              # Wrong: a Car is not an Engine
    pass
class Car:                           # Right: a Car has an Engine
    def __init__(self) -> None:
        self.engine = Engine()
    def start(self) -> str:
        return self.engine.start()
print(Car().start())
```

❌ Mistake 3: Checking the exact type instead of the family
✅ Correct: use isinstance

```python
class A: ...
class B(A): ...
b = B()
print(type(b) == A)              # Wrong: False
print(isinstance(b, A))          # Right: True
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __init__(self):
        self.v = self.val()
    def val(self):
        return "A"
class B(A):
    def val(self):
        return "B"
class C(A):
    def __init__(self):
        self.extra = 1
print(B().v)
print(hasattr(C(), "v"))
print(isinstance(True, int), issubclass(bool, int), type(True) == int)
```

Output:
```
B
False
True True False
```

Answer: In `A.__init__`, `self.val()` is looked up on the real object, which is a `B`, so it calls B's `val` and prints `B` (this is polymorphism, and also why calling overridable methods inside `__init__` is risky). Class `C` overrides `__init__` without calling the parent, so `v` is never set: `False`. Finally `bool` is a subclass of `int`, so `isinstance(True, int)` and `issubclass(bool, int)` are `True`, but `type(True)` is exactly `bool`, so the last comparison is `False`.

---

## ⚫ Interview Questions + Answers

Q1: What is inheritance and why use it?
A1: It lets a child class reuse and extend a parent class. It removes duplicated code and enables polymorphism, where code written for the parent works with all children.

Q2: What is method overriding?
A2: A child defines a method with the same name as the parent. Python finds the child's version first in the MRO. Use `super().method()` inside it to extend rather than replace the parent logic.

Q3: Inheritance vs composition?
A3: Inheritance is IS-A (Dog is an Animal); composition is HAS-A (Car has an Engine). Prefer composition when the relation is not truly IS-A, because inheritance couples the child tightly to the parent's internals.

Q4: What is an abstract base class?
A4: A class using `ABC` with `@abstractmethod` that cannot be instantiated until children implement every abstract method. It documents a contract, like an interface.

Q5: How do you check inheritance relations?
A5: `issubclass(Child, Parent)` for classes, `isinstance(obj, Parent)` for objects, `Child.__bases__` for direct parents and `Child.__mro__` for the full search order.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- A true IS-A relationship exists
- Several classes share most of their code
- You need polymorphism with a common interface
- Extending a framework class (Exception, BaseModel)

❌ Avoid when:
- The relation is HAS-A; use composition
- The child would use only a small part of the parent
- Deep inheritance trees (more than 2-3 levels) that are hard to follow

---

## 📊 Visual Diagram
```
            object
              ^
              |
          PaymentGateway (ABC)   pay() template, _charge() abstract
           ^           ^
           |           |
       Razorpay      Stripe       each implements _charge()

checkout(gateway: PaymentGateway)   works with ANY child
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Inheritance | Child reuses parent's code | Child का parent का code reuse करना |
| Parent / Base class | Class being inherited from | जिससे inherit किया जाए |
| Child / Subclass | Class that inherits | जो inherit करे |
| Override | Replace parent's method | Parent का method बदलना |
| super() | Access the next class in MRO | MRO की अगली class तक पहुँचना |
| Abstract class | Class that cannot be instantiated alone | जिसका सीधा object नहीं बनता |

---

## ⚡ 3-Line Summary
English: Inheritance lets a child class reuse and override a parent's code, modelling IS-A. Use `super()` to extend the parent and `ABC` to force required methods. Prefer composition when the relation is HAS-A.
Hindi: Inheritance में child class parent का code reuse और override करती है, यह IS-A दिखाता है। Parent को extend करने के लिए `super()` और ज़रूरी methods के लिए `ABC` इस्तेमाल करें। HAS-A हो तो composition चुनें।

---

## ➡️ Next Topic
**091. Single Inheritance** — one parent only: multilevel chains, `super()` in practice and generic base classes.
