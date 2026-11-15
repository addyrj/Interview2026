---

# 099. Polymorphism
# हिंदी में: Polymorphism (एक नाम, कई रूप)

---

## 🔵 Simple Definition (English)
Polymorphism means "many forms": the same method call or operator behaves differently depending on the object. You write code once (`shape.area()`), and each class supplies its own behavior.

## 🔵 सरल परिभाषा (Hindi)
Polymorphism का मतलब है "कई रूप": एक ही method call या operator object के हिसाब से अलग व्यवहार करता है। आप code एक बार लिखते हैं (`shape.area()`) और हर class अपना behavior देती है।

---

## 🔴 Problem it Solves
Without polymorphism you write long `if type == "card": ... elif type == "upi": ... elif type == "wallet": ...` chains in many places. Every new payment type means editing all of them, and one forgotten spot is a bug. With polymorphism, each type is a class with the same method, and the calling code never changes.

## 🔴 यह क्यों बना? (Hindi)
Polymorphism के बिना कई जगह लंबी `if type == "card": ... elif type == "upi": ...` chains लिखनी पड़ती हैं। हर नया payment type आने पर सब जगह edit करना पड़ता है और एक जगह छूटी तो bug। Polymorphism में हर type एक class है जिसमें वही method है, और calling code कभी नहीं बदलता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Several classes define a method with the same name (pay(), area(), speak())
Step 2 → Caller holds an object and calls obj.pay(100) - it does not check the type
Step 3 → At runtime Python finds pay() on the object's real class (dynamic dispatch)
Step 4 → That class's version runs
Step 5 → Types of polymorphism in Python:
         - subtype (inheritance + override)   - duck typing (same method names)
         - operator (__add__)                 - built-ins (len() works on many types)
Step 6 → Adding a new class needs zero change in the caller (open/closed principle)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → कई classes एक ही नाम का method बनाती हैं (pay(), area(), speak())
Step 2 → Caller के पास object है और वह obj.pay(100) call करता है - type check नहीं करता
Step 3 → Runtime पर Python object की असली class में pay() ढूंढता है (dynamic dispatch)
Step 4 → उसी class का version चलता है
Step 5 → Python में polymorphism के प्रकार:
         - subtype (inheritance + override)   - duck typing (same method names)
         - operator (__add__)                 - built-ins (len() कई types पर चलता है)
Step 6 → नई class जोड़ने पर caller में कोई बदलाव नहीं (open/closed principle)
```

---

## 🟡 Real World Example
Checkout in a Razorpay-like system: `CardPayment`, `UpiPayment` and `WalletPayment` all have `pay(amount)`. The checkout loops over the customer's chosen method and calls `pay()`. Another example: `print()`, `len()`, and `for` work on strings, lists, dicts, files and your own classes - the built-ins are polymorphic.

## 🟡 Real Example Hindi mein
Razorpay जैसे system में checkout: `CardPayment`, `UpiPayment` और `WalletPayment` सबमें `pay(amount)` है। Checkout customer के चुने method पर `pay()` call करता है। और उदाहरण: `print()`, `len()` और `for` strings, lists, dicts, files और आपकी अपनी classes पर चलते हैं - built-ins polymorphic हैं।

---

## 💻 Code Example — Basic
```python
# Basic polymorphism example
class Animal:                                   # base class
    def speak(self) -> str:                     # common interface
        return "..."                            # default sound


class Dog(Animal):                              # child 1
    def speak(self) -> str:                     # override
        return "Woof"


class Cat(Animal):                              # child 2
    def speak(self) -> str:                     # override
        return "Meow"


animals: list[Animal] = [Dog(), Cat(), Animal()]    # different types in one list
for a in animals:                               # same call for every object
    print(type(a).__name__, "->", a.speak())    # right version is chosen at runtime

print(len("abc"), len([1, 2]), len({1: 2}))     # built-in len() is polymorphic
print(3 + 4, "a" + "b", [1] + [2])              # operator + is polymorphic

# Output:
# Dog -> Woof
# Cat -> Meow
# Animal -> ...
# 3 2 1
# 7 ab [1, 2]
```

## 💻 Code Example — Advanced
```python
# Production style: payment strategies, polymorphic dispatch, easy extension
from abc import ABC, abstractmethod             # contract tools
from dataclasses import dataclass               # simple classes


@dataclass(frozen=True)
class Receipt:
    method: str                                 # which payment method was used
    amount: int                                 # amount charged (rupees)
    fee: int                                    # fee taken


class Payment(ABC):                             # common interface
    @abstractmethod
    def pay(self, amount: int) -> Receipt: ...  # every method implements this


class Card(Payment):
    def pay(self, amount: int) -> Receipt:
        return Receipt("card", amount, round(amount * 0.02))    # 2% fee


class Upi(Payment):
    def pay(self, amount: int) -> Receipt:
        return Receipt("upi", amount, 0)        # UPI is free for the customer


class Wallet(Payment):
    def __init__(self, balance: int) -> None:
        self.balance: int = balance             # wallet money

    def pay(self, amount: int) -> Receipt:
        if amount > self.balance:               # wallet-specific rule
            raise ValueError("Insufficient wallet balance")
        self.balance -= amount                  # deduct
        return Receipt("wallet", amount, 0)


def checkout(method: Payment, amount: int) -> Receipt:
    """Does not know or care which payment type it received."""
    if amount <= 0:                             # shared validation
        raise ValueError("amount must be positive")
    return method.pay(amount)                   # polymorphic call


for m in (Card(), Upi(), Wallet(1000), Wallet(10)):    # four objects, one loop
    try:
        print(checkout(m, 500))                 # same call, different behavior
    except ValueError as e:                     # wallet with 10 fails
        print("Error:", e)

# Output:
# Receipt(method='card', amount=500, fee=10)
# Receipt(method='upi', amount=500, fee=0)
# Receipt(method='wallet', amount=500, fee=0)
# Error: Insufficient wallet balance
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Method overriding | Yes | Yes |
| Method overloading (same name, different params) | No (last definition wins); use defaults, `*args`, `singledispatch` | No |
| Operator overloading | Yes (`__add__`) | No |
| Duck typing | Yes | Yes |
| Base needed | No | No |

```python
# Python way
class Cat:
    def speak(self) -> str:
        return "Meow"

class Robot:                       # unrelated class, same method name
    def speak(self) -> str:
        return "Beep"

for x in (Cat(), Robot()):
    print(x.speak())               # Meow, Beep
```
```javascript
// JavaScript way
class Cat { speak() { return "Meow"; } }
class Robot { speak() { return "Beep"; } }   // unrelated class, same method name
for (const x of [new Cat(), new Robot()]) console.log(x.speak());   // Meow, Beep
```

Key difference: both are duck-typed, so polymorphism does not need a shared parent. Python additionally lets you overload operators (`+`, `==`, `[]`), which JavaScript cannot do.

---

## 🟠 FastAPI Connection
FastAPI route handlers are polymorphic through dependencies: the route calls `storage.save(file)` and the actual storage (local disk, S3) is picked by the dependency. Also, response models using a `Union` return different shapes of objects.

```python
# FastAPI example — polymorphic storage backend chosen by dependency
from typing import Protocol                     # interface
from fastapi import FastAPI, Depends            # app and DI
from fastapi.testclient import TestClient       # test client


class Storage(Protocol):
    def save(self, name: str) -> str: ...       # common method


class LocalStorage:
    def save(self, name: str) -> str:
        return f"/var/data/{name}"              # saved on disk


class S3Storage:
    def save(self, name: str) -> str:
        return f"s3://bucket/{name}"            # saved in the cloud


def get_storage(kind: str = "local") -> Storage:    # kind comes from ?kind=...
    return S3Storage() if kind == "s3" else LocalStorage()   # pick implementation


app: FastAPI = FastAPI()                        # create app


@app.post("/upload")                            # POST /upload?name=a.txt&kind=s3
def upload(name: str, storage: Storage = Depends(get_storage)) -> dict[str, str]:
    return {"path": storage.save(name)}         # polymorphic call


client: TestClient = TestClient(app)            # test client
print(client.post("/upload", params={"name": "a.txt"}).json())
print(client.post("/upload", params={"name": "a.txt", "kind": "s3"}).json())

# Output:
# {'path': '/var/data/a.txt'}
# {'path': 's3://bucket/a.txt'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `isinstance` chains instead of polymorphism
✅ Correct: put the behavior in each class

```python
class Dog:
    def speak(self) -> str:
        return "Woof"

class Cat:
    def speak(self) -> str:
        return "Meow"

def wrong(x: object) -> str:
    if isinstance(x, Dog):       # must edit for every new class
        return "Woof"
    elif isinstance(x, Cat):
        return "Meow"
    return "?"

def right(x: Dog | Cat) -> str:
    return x.speak()             # no edits needed for new classes

print(wrong(Dog()), right(Cat()))   # Woof Meow
```

❌ Mistake 2: Expecting method overloading by parameters
✅ Correct: the last definition wins; use defaults or `functools.singledispatch`

```python
from functools import singledispatch

class Wrong:
    def area(self, r: float) -> float:
        return 3.14 * r * r
    def area(self, w: float, h: float) -> float:   # replaces the first one!
        return w * h

try:
    Wrong().area(2)
except TypeError as e:
    print("Error:", e)

@singledispatch                      # Right: dispatch on the first argument's type
def show(x: object) -> str:
    return f"object {x}"

@show.register
def _(x: int) -> str:
    return f"int {x}"

@show.register
def _(x: str) -> str:
    return f"str {x}"

print(show(5), show("a"), show(2.5))
```

❌ Mistake 3: Override that changes the meaning or signature (breaks substitutability)
✅ Correct: keep the same parameters and return type (Liskov principle)

```python
class Base:
    def total(self, items: list[int]) -> int:
        return sum(items)

class Wrong(Base):
    def total(self, items: list[int]) -> str:    # returns a str now!
        return str(sum(items))

class Right(Base):
    def total(self, items: list[int]) -> int:
        return sum(items) + 10                   # same type, different logic

print(Wrong().total([1, 2]) + 1 if False else "mypy would flag Wrong")
print(Right().total([1, 2]) + 1)                 # 14
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Parent:
    def show(self) -> None:
        print("Parent.show ->", self.name())

    def name(self) -> str:
        return "Parent"

class Child(Parent):
    def name(self) -> str:
        return "Child"

Child().show()
Parent.show(Child())
```
Answer: Both lines print `Parent.show -> Child`. `show` is defined only in `Parent`, but `self` is a `Child` object, so `self.name()` is looked up on the real class (`Child`) first. This is dynamic dispatch: the method chosen depends on the runtime type of the object, not on where the calling code was written. This is the basis of the "template method" pattern.

---

## ⚫ Interview Questions + Answers

Q1: What are the kinds of polymorphism in Python?
A1: Subtype polymorphism (override in subclasses), duck typing (any object with the right methods), operator overloading (`__add__`, `__eq__`), and ad-hoc/generic dispatch (`functools.singledispatch`). Built-ins like `len()` are polymorphic via dunder methods.

Q2: Does Python support method overloading?
A2: Not in the Java sense. Defining a method twice replaces the first. Use default arguments, `*args/**kwargs`, `typing.overload` (for type hints only), or `singledispatch` / `singledispatchmethod`.

Q3: Overriding vs overloading?
A3: Overriding: a child redefines a parent's method with the same name and signature. Overloading: several methods with the same name but different parameters (not natively supported in Python).

Q4: How does Python decide which method runs?
A4: It looks at the object's class and walks the MRO until it finds the name. This happens at call time (late binding), which is why one call site can run different code for different objects.

Q5: Why is polymorphism good for maintainability?
A5: New behavior is added by creating a new class, not by editing existing `if/elif` chains. Existing code stays untouched and tested (open/closed principle).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several variants share one operation (payment types, exporters, notifiers)
- You catch yourself writing `if type == ...` in several places
- Plugin-style extension points

❌ Avoid when:
- Only one variant exists and no growth is expected
- The variants differ so much that a shared method name would mislead
- A simple dict of functions is clearer (`handlers[kind](data)`)

---

## 📊 Visual Diagram
```
                 checkout(method, 500)
                         |
                  method.pay(500)         <- one call
        +----------------+----------------+
        v                v                v
   Card.pay()       Upi.pay()       Wallet.pay()
   fee 2%           fee 0           checks balance
        (decided at runtime from the object's real class)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Polymorphism | Same call, different behavior | एक call, अलग व्यवहार |
| Overriding | Child redefines parent method | Child द्वारा parent method दोबारा लिखना |
| Overloading | Same name, different parameters | एक नाम, अलग parameters |
| Dynamic dispatch | Method chosen at runtime | Runtime पर method चुनना |
| Duck typing | Judge by methods, not class | Methods देखकर पहचानना |
| Liskov principle | Child must be usable wherever parent is | Child को parent की जगह चलना चाहिए |

---

## ⚡ 3-Line Summary
English: Polymorphism lets one method call run different code depending on the object. In Python it works through overriding, duck typing and operator overloading. It removes `if/elif` type checks and makes code easy to extend.
Hindi: Polymorphism में एक ही method call object के हिसाब से अलग code चलाता है। Python में यह overriding, duck typing और operator overloading से काम करता है। यह `if/elif` type checks हटाता है और code बढ़ाना आसान करता है।

---

## ➡️ Next Topic
**100. Duck Typing** — "if it quacks like a duck": Python cares about what an object can do, not what class it is.
