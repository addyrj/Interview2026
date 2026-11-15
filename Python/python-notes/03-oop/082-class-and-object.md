---

# 082. Class + Object
# हिंदी में: Class + Object (क्लास और ऑब्जेक्ट)

---

## 🔵 Simple Definition (English)
A class is a blueprint that describes what data and behaviour something has. An object is one real thing built from that blueprint. One class can create many objects, and each object keeps its own data.

## 🔵 सरल परिभाषा (Hindi)
Class एक blueprint (नक्शा) है जो बताता है कि किसी चीज़ में कौन सा data और behaviour होगा। Object उस blueprint से बनी एक असली चीज़ है। एक class से कई objects बन सकते हैं और हर object का अपना data होता है।

---

## 🔴 Problem it Solves
Before classes, programs used loose variables and functions: `name1`, `age1`, `name2`, `age2` and functions that took many separate arguments. Data and the code that works on it lived apart, so large programs became messy and error-prone. A class bundles data (attributes) and behaviour (methods) in one place. In Python, a class is also an object itself (an instance of `type`), which makes it very flexible.

## 🔴 यह क्यों बना? (Hindi)
Classes से पहले programs में अलग-अलग variables और functions होते थे: `name1`, `age1`, `name2`, `age2` और ऐसे functions जिन्हें बहुत सारे arguments देने पड़ते थे। Data और उस पर काम करने वाला code अलग-अलग रहता था, इसलिए बड़े programs messy हो जाते थे। Class data (attributes) और behaviour (methods) को एक जगह जोड़ देती है। Python में class खुद भी एक object है (`type` का instance), इसलिए यह बहुत flexible है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → `class Dog:` runs and Python creates a class object named Dog (an instance of `type`)
Step 2 → Names defined inside (methods, class variables) are stored in `Dog.__dict__`
Step 3 → `Dog('Tommy', 3)` calls the class like a function
Step 4 → Python creates an empty object (`__new__`), then runs `__init__` to fill its data
Step 5 → The new object keeps its own data in `obj.__dict__` and a link to its class
Step 6 → `obj.bark()` → not found on obj → found on Dog → called with obj as `self`
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `class Dog:` चलता है और Python Dog नाम का class object बनाता है (`type` का instance)
Step 2 → अंदर के names (methods, class variables) `Dog.__dict__` में रखे जाते हैं
Step 3 → `Dog('Tommy', 3)` class को function की तरह call करता है
Step 4 → Python खाली object बनाता है (`__new__`), फिर `__init__` उसमें data भरता है
Step 5 → नया object अपना data `obj.__dict__` में रखता है और class का link रखता है
Step 6 → `obj.bark()` → obj में नहीं मिला → Dog में मिला → obj को `self` बनाकर call हुआ
```

---

## 🟡 Real World Example
A Razorpay-style payments service has a `Wallet` class: every user gets a Wallet object with their own owner and balance, but all wallets share the same rules (credit, debit, validation). A Zomato backend has `Restaurant`, `Order` and `Rider` classes. Each order in the database is loaded as an Order object.

## 🟡 Real Example Hindi mein
Razorpay जैसी payments service में `Wallet` class होती है: हर user को अपना Wallet object मिलता है जिसमें उसका owner और balance है, लेकिन सभी wallets के rules (credit, debit, validation) एक जैसे हैं। Zomato backend में `Restaurant`, `Order` और `Rider` classes होती हैं। Database की हर order एक Order object बनकर load होती है।

---

## 💻 Code Example — Basic
```python
# Basic: class = blueprint, object = real thing built from it
class Dog:                                        # define a class (blueprint)
    species: str = "Canis familiaris"             # class variable shared by all dogs

    def __init__(self, name: str, age: int) -> None:   # runs when object is created
        self.name: str = name                     # instance variable: own data of each object
        self.age: int = age                       # another instance variable

    def bark(self) -> str:                        # method: behaviour of the object
        return f"{self.name} says Woof!"          # self gives access to this object's data


d1: Dog = Dog("Tommy", 3)                         # create object 1 (instantiate)
d2: Dog = Dog("Bruno", 5)                         # create object 2 from same class
print(d1.bark())                                  # call method on d1
print(d2.bark())                                  # call method on d2
print(type(d1))                                   # the class of the object
print(isinstance(d1, Dog))                        # is d1 an instance of Dog?
print(d1 is d2, d1 == d2)                         # two separate objects, default == is identity
print(d1.__dict__)                                # instance data lives in a dict
print(Dog.__name__, Dog.species)                  # classes are objects too
d1.color = "brown"                                # Python allows adding attributes dynamically
print(d1.color, hasattr(d2, "color"))             # only d1 got it

# Output:
# Tommy says Woof!
# Bruno says Woof!
# <class '__main__.Dog'>
# True
# False False
# {'name': 'Tommy', 'age': 3}
# Dog Canis familiaris
# brown False
```

## 💻 Code Example — Advanced
```python
# Advanced: a domain class with validation, __repr__, and a factory
from __future__ import annotations                # allow Class names in annotations (safe on 3.13 too)
from decimal import Decimal                       # exact money arithmetic


class InsufficientFunds(Exception):               # custom error for the domain
    """Raised when a wallet does not have enough balance."""


class Wallet:                                     # a Razorpay-style wallet
    def __init__(self, owner: str, balance: Decimal = Decimal("0")) -> None:
        if balance < 0:                           # validate input at creation time
            raise ValueError("opening balance cannot be negative")   # fail early
        self.owner: str = owner                   # who owns this wallet
        self._balance: Decimal = balance          # _ means internal by convention

    def credit(self, amount: Decimal) -> None:    # add money
        if amount <= 0:                           # reject nonsense amounts
            raise ValueError("amount must be positive")
        self._balance += amount                   # update object state

    def debit(self, amount: Decimal) -> None:     # remove money
        if amount > self._balance:                # check before changing state
            raise InsufficientFunds(f"{self.owner}: need {amount}, have {self._balance}")
        self._balance -= amount                   # state changes only if valid

    @property
    def balance(self) -> Decimal:                 # read-only view of the balance
        return self._balance

    def __repr__(self) -> str:                    # developer friendly text
        return f"Wallet(owner={self.owner!r}, balance={self._balance})"

    @classmethod
    def with_bonus(cls, owner: str) -> Wallet:    # factory: signup bonus wallet
        return cls(owner, Decimal("100"))         # cls() creates an object of this class


w: Wallet = Wallet.with_bonus("Asha")             # build through the factory
w.credit(Decimal("250.50"))                       # add money
w.debit(Decimal("50"))                            # spend money
print(w)                                          # uses __repr__
try:                                              # error handling
    w.debit(Decimal("1000"))                      # too much
except InsufficientFunds as e:                    # catch the domain error
    print("Error:", e)
try:
    Wallet("Bad", Decimal("-5"))                  # invalid creation
except ValueError as e:
    print("Error:", e)
print(w.balance, Wallet("Raj") is Wallet("Raj"))  # each call makes a new object

# Output:
# Wallet(owner='Asha', balance=300.50)
# Error: Asha: need 1000, have 300.50
# Error: opening balance cannot be negative
# 300.50 False
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Define class | `class Dog:` | `class Dog {}` |
| Create object | `Dog('Tommy')` (no `new`) | `new Dog('Tommy')` |
| Constructor | `__init__(self, ...)` | `constructor(...)` |
| Current object | `self` (explicit first parameter) | `this` (implicit) |
| Add attribute later | allowed on any instance | allowed on any object |
| Classes are objects | yes (`type`) | yes (functions) |

```python
# Python way
class Dog:
    def __init__(self, name: str) -> None:   # self is written explicitly
        self.name: str = name

    def bark(self) -> str:
        return f"{self.name} says Woof!"

print(Dog("Tommy").bark())   # no `new` keyword
```
```javascript
// JavaScript way
class Dog {
  constructor(name) { this.name = name; }   // this is implicit
  bark() { return `${this.name} says Woof!`; }
}
console.log(new Dog("Tommy").bark());       // `new` is required
```

Key difference: Python never uses `new`; you call the class like a function. `self` must be written in every method signature, while JS `this` appears automatically. Python also has no `private` keyword; it uses naming conventions like `_name`.

---

## 🟠 FastAPI Connection
FastAPI services are built from classes: Pydantic models (request and response bodies), SQLAlchemy models (tables) and service classes (business logic). Remember that a module-level object is created once per worker process and shared by all requests, so it must not keep per-user data.

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()


class Counter:                                    # plain class used as an in-memory service
    def __init__(self) -> None:
        self.hits: int = 0

    def hit(self) -> int:
        self.hits += 1
        return self.hits


counter: Counter = Counter()                      # ONE object shared by all requests


@app.get("/hit")
def hit() -> dict[str, int]:
    return {"hits": counter.hit()}


c = TestClient(app)
print(c.get("/hit").json(), c.get("/hit").json())

# Output:
# {'hits': 1} {'hits': 2}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling a method on the class instead of the object
✅ Correct: create an object first (or pass one explicitly)

```python
class Dog:
    def bark(self) -> str:
        return "Woof"

# Wrong
try:
    Dog.bark()
except TypeError as e:
    print("Error:", e)
# Right
print(Dog().bark())
```

❌ Mistake 2: Forgetting `self` in the method definition
✅ Correct: always put `self` as the first parameter

```python
class Cat:
    def meow():                       # Wrong: no self
        return "meow"

try:
    Cat().meow()
except TypeError as e:
    print("Error:", e)

class Cat2:
    def meow(self) -> str:            # Right
        return "meow"

print(Cat2().meow())
```

❌ Mistake 3: Putting a mutable list at class level to store per-object data
✅ Correct: create it inside `__init__`

```python
class Box:
    items = []                        # Wrong: shared by all Box objects

class Box2:
    def __init__(self) -> None:
        self.items: list[int] = []    # Right: one list per object

a, b = Box(), Box()
a.items.append(1)
print(b.items)                        # [1] shared!
c, d = Box2(), Box2()
c.items.append(1)
print(d.items)                        # []
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class Box:
    items = []
    def __init__(self, n):
        self.n = n
a = Box(1); b = Box(2)
a.items.append(a.n)
print(b.items, a is b, Box(1) == Box(1))
print(a.__dict__, Box.items)
```

Output:
```
[1] False False
{'n': 1} [1]
```

Answer: `items` is a class variable, so `a.items` and `b.items` are the same list; appending through `a` changes what `b` sees, giving `[1]`. `a is b` is `False` because they are two different objects. `Box(1) == Box(1)` is `False` because without `__eq__` Python compares identity. The instance dictionary only holds `n`, because `items` was never assigned on the instance; the list lives on `Box`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a class and an object?
A1: A class is the blueprint; an object (instance) is one concrete thing created from it. `Dog` is a class, `Dog('Tommy')` is an object. Classes are created once, objects as many times as needed.

Q2: What does `self` mean?
A2: `self` is the object on which the method is being called. Python passes it automatically as the first argument: `d.bark()` becomes `Dog.bark(d)`. The name `self` is only a convention, but everyone follows it.

Q3: Is a class an object in Python?
A3: Yes. Everything is an object. A class is an instance of `type`, so you can store it in a variable, pass it to a function and create it at runtime with `type('Name', (), {})`.

Q4: How do you check if an object belongs to a class?
A4: `isinstance(obj, Dog)` returns True for Dog and its subclasses. `type(obj) is Dog` checks the exact class only. Prefer `isinstance` in normal code.

Q5: Where does Python store an object's attributes?
A5: In `obj.__dict__`, a normal dictionary, unless the class uses `__slots__`. Methods and class variables live in `Class.__dict__`. This is why attributes can be added dynamically.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have data and behaviour that belong together (User, Order, Wallet)
- You need many objects with the same structure but different state
- You want to model a domain with clear responsibilities
- A framework expects classes (Pydantic, SQLAlchemy, Django)

❌ Avoid when:
- A single small helper is enough, so a plain function is simpler
- You only hold a few values together, so a dataclass or tuple is shorter
- The class has only static methods, so a module of functions is cleaner

---

## 📊 Visual Diagram
```
class Dog (blueprint)
 +-----------------------------+
 | species = "Canis"  (shared) |
 | __init__(self, name, age)   |
 | bark(self)                  |
 +-----------------------------+
      ^                ^
      | instance-of    | instance-of
 +-------------+  +-------------+
 | d1          |  | d2          |
 | name=Tommy  |  | name=Bruno  |
 | age=3       |  | age=5       |
 +-------------+  +-------------+
   own data          own data
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Class | Blueprint for objects | Objects का नक्शा |
| Object / Instance | A thing built from a class | Class से बनी असली चीज़ |
| Attribute | Variable stored on an object | Object में रखा variable |
| Method | Function defined inside a class | Class के अंदर का function |
| self | The current object | वर्तमान object |
| Instantiate | Create an object from a class | Class से object बनाना |

---

## ⚡ 3-Line Summary
English: A class is a blueprint and an object is a real thing made from it. Each object stores its own data in `__dict__` and shares methods from the class. Python needs no `new`; call the class like a function.
Hindi: Class एक blueprint है और object उससे बनी असली चीज़। हर object अपना data `__dict__` में रखता है और methods class से share करता है। Python में `new` नहीं लगता, class को function की तरह call करो।

---

## ➡️ Next Topic
**083. `__init__` Method** — the constructor that sets up each new object: default values, validation and the difference from `__new__`.
