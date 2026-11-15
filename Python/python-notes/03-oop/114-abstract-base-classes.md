---

# 114. Abstract Base Classes
# हिंदी में: Abstract Base Classes (ABC) — Interface का नियम

---

## 🔵 Simple Definition (English)
An Abstract Base Class (ABC) is a class that cannot be instantiated and declares methods that every subclass MUST implement (`@abstractmethod`). It defines a contract: "if you inherit from me, you must provide these methods". Python checks this when you try to create an object, not when you define the class.

## 🔵 सरल परिभाषा (Hindi)
Abstract Base Class (ABC) ऐसी class है जिसका object नहीं बन सकता और जो ऐसे methods declare करती है जिन्हें हर subclass को लागू करना ही होगा (`@abstractmethod`)। यह एक contract है: "मुझसे inherit करो तो ये methods देने ही होंगे"। Python यह जांच class define करते समय नहीं, object बनाते समय करता है।

---

## 🔴 Problem it Solves
In plain Python, a base class can have `def pay(self): raise NotImplementedError`. A subclass that forgets `pay` still gets created, and the program crashes only later, in production, when someone calls `pay()`. With an ABC the mistake shows up immediately when you create the object: `TypeError: Can't instantiate abstract class ...`. ABCs also let you define a clear interface (payment gateway, storage backend, repository) so the rest of the code depends on the interface, not on one implementation.

## 🔴 यह क्यों बना? (Hindi)
सामान्य Python में base class में `def pay(self): raise NotImplementedError` हो सकता है। जो subclass `pay` भूल गई, वह फिर भी बन जाती है, और program बहुत बाद में, production में, `pay()` call होने पर crash होता है। ABC में गलती object बनाते ही दिखती है: `TypeError: Can't instantiate abstract class ...`। ABC साफ interface (payment gateway, storage backend, repository) भी तय करती है ताकि बाकी code किसी एक implementation पर नहीं, interface पर निर्भर रहे।

---

## 🟢 How it Works — Step by Step

```
Step 1 → class Base(ABC):  (ABC uses metaclass ABCMeta)
Step 2 → Mark required methods with @abstractmethod
Step 3 → ABCMeta collects them in Base.__abstractmethods__ (a frozenset)
Step 4 → Base() -> TypeError, because the set is not empty
Step 5 → class Child(Base) overrides ALL abstract methods -> set becomes empty
Step 6 → Child() works. Missing even one -> Child() still raises TypeError

Extras: abstract properties, concrete helper methods in the ABC,
        Base.register(SomeClass) for "virtual subclasses",
        isinstance(x, Base) works with collections.abc (Iterable, Mapping...)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → class Base(ABC):  (ABC, metaclass ABCMeta use करता है)
Step 2 → जरूरी methods पर @abstractmethod लगाएं
Step 3 → ABCMeta उन्हें Base.__abstractmethods__ (frozenset) में जमा करता है
Step 4 → Base() -> TypeError, क्योंकि set खाली नहीं है
Step 5 → class Child(Base) सारे abstract methods override करे -> set खाली हो जाता है
Step 6 → Child() बन जाता है। एक भी छूटा तो Child() फिर भी TypeError देता है

Extras: abstract properties, ABC में concrete helper methods,
        Base.register(SomeClass) से "virtual subclasses",
        isinstance(x, Base) collections.abc (Iterable, Mapping...) के साथ काम करता है
```

---

## 🟡 Real World Example
A Swiggy-like backend supports several payment gateways. A `PaymentGateway` ABC requires `charge()` and `refund()`. `RazorpayGateway` and `StripeGateway` implement them. The checkout code accepts any `PaymentGateway`, and adding PayU later cannot silently skip `refund()`. Likewise a `Storage` ABC with `save()` / `load()` has `LocalStorage` for tests and `S3Storage` for production.

## 🟡 Real Example Hindi mein
Swiggy जैसा backend कई payment gateways support करता है। `PaymentGateway` ABC में `charge()` और `refund()` जरूरी हैं। `RazorpayGateway` और `StripeGateway` उन्हें लागू करते हैं। Checkout code कोई भी `PaymentGateway` लेता है, और बाद में PayU जोड़ते समय `refund()` चुपचाप छूट नहीं सकता। इसी तरह `Storage` ABC में `save()` / `load()` हैं, tests के लिए `LocalStorage` और production के लिए `S3Storage` है।

---

## 💻 Code Example — Basic
```python
# Basic ABC examples
from abc import ABC, abstractmethod               # the tools


class Shape(ABC):                                 # abstract base class
    @abstractmethod                               # every subclass must implement this
    def area(self) -> float:
        """Return the area."""

    def describe(self) -> str:                    # concrete method shared by all shapes
        return f"{type(self).__name__} with area {self.area():.2f}"


class Circle(Shape):                              # complete implementation
    def __init__(self, r: float) -> None:
        self.r: float = r                         # radius

    def area(self) -> float:                      # satisfies the contract
        return 3.14159 * self.r ** 2


class Broken(Shape):                              # forgot to implement area()
    pass


try:                                              # cannot instantiate the abstract class
    Shape()                                       # abstract
except TypeError as e:                            # catch the error
    print(e)

try:                                              # incomplete subclass fails too
    Broken()
except TypeError as e:
    print(e)

c: Shape = Circle(2)                              # concrete subclass works
print(c.describe())                               # inherited concrete method uses area()
print(Shape.__abstractmethods__)                  # what must be implemented
print(isinstance(c, Shape), issubclass(Circle, Shape))   # normal inheritance checks

# Output (messages shown are from CPython 3.13; wording differs slightly in 3.11 and older):
# Can't instantiate abstract class Shape without an implementation for abstract method 'area'
# Can't instantiate abstract class Broken without an implementation for abstract method 'area'
# Circle with area 12.57
# frozenset({'area'})
# True True
```

## 💻 Code Example — Advanced
```python
# Production style: payment gateway interface, abstract property, virtual subclass, collections.abc
from abc import ABC, abstractmethod               # ABC tools
from collections.abc import Iterator, Sequence    # standard ABCs (use these, don't re-invent)
from dataclasses import dataclass                 # simple result object


@dataclass(frozen=True)
class Receipt:                                    # what every gateway returns
    gateway: str                                  # which gateway handled it
    txn_id: str                                   # transaction id
    amount: int                                   # amount in paise


class PaymentError(Exception):                    # domain error
    """Raised when a gateway rejects a payment."""


class PaymentGateway(ABC):
    """Contract for all payment providers."""

    @property
    @abstractmethod                               # abstract property: must be provided
    def name(self) -> str: ...

    @abstractmethod
    def charge(self, amount: int) -> Receipt:     # must implement
        ...

    @abstractmethod
    def refund(self, txn_id: str) -> bool:        # must implement
        ...

    def charge_safe(self, amount: int) -> Receipt:   # template method: shared validation
        if amount <= 0:                           # business rule in ONE place
            raise PaymentError("amount must be positive")
        return self.charge(amount)                # delegate to the subclass


class RazorpayGateway(PaymentGateway):
    name = "razorpay"                             # a plain class attribute satisfies the property

    def charge(self, amount: int) -> Receipt:
        return Receipt(self.name, f"rzp_{amount}", amount)

    def refund(self, txn_id: str) -> bool:
        return txn_id.startswith("rzp_")          # pretend validation


class IncompleteGateway(PaymentGateway):          # forgot refund and name
    def charge(self, amount: int) -> Receipt:
        return Receipt("x", "x", amount)


def checkout(gateway: PaymentGateway, amount: int) -> str:
    """Depends on the interface, not on a concrete gateway."""
    try:
        receipt = gateway.charge_safe(amount)     # same call for every provider
        return f"{receipt.gateway}: {receipt.txn_id}"
    except PaymentError as exc:                   # shared error handling
        return f"failed: {exc}"


print(checkout(RazorpayGateway(), 49900))         # razorpay: rzp_49900
print(checkout(RazorpayGateway(), 0))             # failed: amount must be positive

try:
    IncompleteGateway()                           # caught immediately, not at payment time
except TypeError as e:
    print("TypeError:", sorted(PaymentGateway.__abstractmethods__))   # what the contract needs


# Virtual subclass: register a class you cannot edit (no inheritance)
class LegacyGateway:                              # third-party class, no base class
    name = "legacy"
    def charge(self, amount: int) -> Receipt: return Receipt("legacy", "L1", amount)
    def refund(self, txn_id: str) -> bool: return True


PaymentGateway.register(LegacyGateway)            # declare it as a virtual subclass
print(isinstance(LegacyGateway(), PaymentGateway))   # True (but nothing is enforced!)


# Using collections.abc: implement 2 methods, get many for free
class Playlist(Sequence[str]):                    # needs only __getitem__ and __len__
    def __init__(self, *songs: str) -> None:
        self._songs: list[str] = list(songs)

    def __getitem__(self, i):                     # type: ignore[override]
        return self._songs[i]

    def __len__(self) -> int:
        return len(self._songs)


pl = Playlist("a", "b", "c")
print("b" in pl, pl.index("c"), list(reversed(pl)))   # mixin methods came from Sequence

# Output:
# razorpay: rzp_49900
# failed: amount must be positive
# TypeError: ['charge', 'name', 'refund']
# True
# True 2 ['c', 'b', 'a']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Abstract class | `ABC` + `@abstractmethod` | TypeScript `abstract class` |
| Interface | ABC or `Protocol` | TypeScript `interface` |
| Enforcement | runtime, at instantiation | compile time only (erased at runtime) |
| Plain JS | none; manual check `new.target === Base` | same |

```python
# Python way
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str: ...               # must be overridden

class Dog(Animal):
    def speak(self) -> str:
        return "woof"

print(Dog().speak())                          # woof
# Animal() -> TypeError at runtime
```
```javascript
// JavaScript way - no abstract keyword in plain JS; you fake it
class Animal {
  constructor() {
    if (new.target === Animal) throw new TypeError("abstract!");   // block direct use
  }
  speak() { throw new Error("not implemented"); }   // fails only when called
}
class Dog extends Animal { speak() { return "woof"; } }
console.log(new Dog().speak());               // woof
// TypeScript: abstract class Animal { abstract speak(): string }  (compile-time only)
```

Key difference: Python enforces abstract methods at runtime the moment you instantiate the class. In JavaScript the check is manual, or compile-time-only with TypeScript.

---

## 🟠 FastAPI Connection
In FastAPI apps, ABCs define the boundaries that you swap in tests: a `UserRepository` ABC with `get()` / `add()`, a real SQL implementation, and an in-memory one for tests. Dependency injection (`Depends`) hands the endpoint the right implementation, and `app.dependency_overrides` replaces it during testing.

```python
# FastAPI example - repository interface with swappable implementations
from abc import ABC, abstractmethod               # ABC tools
from fastapi import Depends, FastAPI, HTTPException   # FastAPI pieces
from fastapi.testclient import TestClient         # tests


class UserRepo(ABC):                              # the contract
    @abstractmethod
    def get(self, user_id: int) -> str | None: ...


class MemoryRepo(UserRepo):                       # simple implementation
    def get(self, user_id: int) -> str | None:
        return {1: "Amit", 2: "Neha"}.get(user_id)


class OtherRepo(UserRepo):                        # another one, for override demo
    def get(self, user_id: int) -> str | None:
        return "from-other"


def get_repo() -> UserRepo:                       # dependency returns the interface type
    return MemoryRepo()


app: FastAPI = FastAPI()                          # create app


@app.get("/users/{user_id}")
def read_user(user_id: int, repo: UserRepo = Depends(get_repo)) -> dict[str, str]:
    name = repo.get(user_id)                      # works with any UserRepo
    if name is None:
        raise HTTPException(404, "user not found")
    return {"name": name}


client: TestClient = TestClient(app)              # client
print(client.get("/users/1").json())              # real dependency
app.dependency_overrides[get_repo] = OtherRepo    # swap implementation (tests)
print(client.get("/users/99").json())             # now served by OtherRepo

# Output:
# {'name': 'Amit'}
# {'name': 'from-other'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to inherit from `ABC` (or use `metaclass=ABCMeta`)
✅ Correct: `@abstractmethod` only works in a class whose metaclass is `ABCMeta`

```python
from abc import abstractmethod, ABC
# Wrong - no enforcement at all
class A:
    @abstractmethod
    def f(self): ...
print(A())                    # <__main__.A object at 0x...>  (address varies)
# Right
class B(ABC):
    @abstractmethod
    def f(self): ...
try:
    B()
except TypeError:
    print("blocked")          # blocked
```

❌ Mistake 2: Wrong decorator order on abstract properties / classmethods
✅ Correct: `@property` (or `@classmethod`) on the OUTSIDE, `@abstractmethod` closest to `def`

```python
from abc import ABC, abstractmethod
class A(ABC):
    @property
    @abstractmethod            # Right: abstractmethod is the innermost
    def name(self) -> str: ...
class B(A):
    name = "b"
print(B().name)                # b
```

❌ Mistake 3: Putting real logic only in abstract methods, or expecting `super().f()` to be required
✅ Correct: abstract methods CAN have a body; subclasses call it with `super()` if useful. Put shared logic in concrete (template) methods.

```python
from abc import ABC, abstractmethod
class Base(ABC):
    @abstractmethod
    def start(self) -> str:
        return "base-start"      # default body, still must be overridden
class Child(Base):
    def start(self) -> str:
        return super().start() + "+child"
print(Child().start())           # base-start+child
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from abc import ABC, abstractmethod

class A(ABC):
    @abstractmethod
    def f(self): ...

class B(A):
    pass

class C(B):
    def f(self):
        return "C"

try:
    B()
except TypeError:
    print("B abstract")
print(C().f())

class D:
    def f(self):
        return "D"

A.register(D)
print(isinstance(D(), A), issubclass(D, A), D.__mro__[-1].__name__)
```
Answer: `B abstract`, then `C`, then `True True object`. `B` inherits `f` without overriding, so it is still abstract. `C` overrides `f`, so the abstract set becomes empty and it can be created. `A.register(D)` makes `D` a "virtual subclass": `isinstance` and `issubclass` return True, but `D` does not actually inherit from `A` (its MRO is just `D, object`) and nothing forces `D` to implement `f`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between an ABC and a normal base class that raises `NotImplementedError`?
A1: The ABC fails at instantiation (early, in tests), the plain class fails only when the missing method is called (late, maybe in production). ABCs also give you `__abstractmethods__`, `register()` and clearer intent.

Q2: Can an ABC have concrete methods and `__init__`?
A2: Yes. ABCs often mix abstract methods (the contract) with concrete ones (shared behavior, the template method pattern). Only classes with unimplemented abstract methods cannot be instantiated.

Q3: ABC vs `Protocol`?
A3: ABC is nominal typing: a class must inherit (or be registered) to count. `Protocol` is structural typing: any class with the right methods qualifies, with no inheritance, checked mostly by type checkers. Use ABC when you want shared code and runtime enforcement, Protocol for flexible duck-typed interfaces.

Q4: What is `register()`, i.e. a virtual subclass?
A4: `Base.register(Other)` tells `isinstance`/`issubclass` that `Other` counts as a subclass of `Base` without inheritance. It is useful for third-party classes. Python does not verify methods and the registered class does not get the ABC's concrete methods.

Q5: What are `collections.abc` classes good for?
A5: They are ready-made ABCs (`Iterable`, `Sequence`, `Mapping`, `MutableMapping`, `Callable`...). Inherit from one, implement a few required dunders, and you get many mixin methods free. Also use them for `isinstance(x, Mapping)` checks instead of `dict`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You define a plugin or interface that many classes implement (gateways, storage, repositories)
- You want to fail early when a subclass is incomplete
- You share template-method logic in a base class
- You need `isinstance` checks against an interface (`collections.abc`)

❌ Avoid when:
- Only one implementation exists and will ever exist
- Duck typing or `Protocol` is enough and you do not want inheritance
- The hierarchy gets deep just to satisfy the pattern
- A simple function or callable would do

---

## 📊 Visual Diagram
```
          +----------------------+
          |  PaymentGateway(ABC) |   __abstractmethods__ = {charge, refund, name}
          |  @abstractmethod ... |   PaymentGateway()  -> TypeError
          +----------+-----------+
                     |
        +------------+-------------+
        |                          |
+-------+---------+      +---------+-----------+
| RazorpayGateway |      | IncompleteGateway   |
| implements all  |      | missing refund,name |
| Razorpay() OK   |      | Incomplete() -> TypeError
+-----------------+      +---------------------+

Gateway.register(Legacy) -> isinstance(Legacy(), Gateway) is True (no inheritance)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ABC | Base class that cannot be instantiated | जिसका object नहीं बन सकता ऐसी base class |
| `@abstractmethod` | Marks a method subclasses must override | subclass को override करना जरूरी बताता है |
| Interface | Set of methods a type must offer | methods का contract |
| Virtual subclass | Registered, not inherited | register की हुई, inherit नहीं |
| Template method | Concrete method calling abstract steps | abstract steps बुलाने वाला concrete method |
| Nominal typing | Compatibility by declared inheritance | declared inheritance से compatibility |

---

## ⚡ 3-Line Summary
English: An ABC declares methods subclasses must implement, and Python blocks creating objects of incomplete classes. It turns a runtime surprise into an immediate `TypeError` and defines clean interfaces. Use `collections.abc` for standard containers and `Protocol` when you do not want inheritance.
Hindi: ABC उन methods को declare करती है जो subclasses को लागू करने ही हैं, और अधूरी class का object Python बनने नहीं देता। इससे runtime का आश्चर्य तुरंत `TypeError` बन जाता है और साफ interfaces मिलते हैं। Standard containers के लिए `collections.abc` और inheritance से बचना हो तो `Protocol` use करें।

---

## ➡️ Next Topic
**115. Protocol (Structural Subtyping)** - interfaces by shape instead of inheritance: if it has the right methods, it fits.
