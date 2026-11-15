---

# 095. Abstract Classes (ABC)
# हिंदी में: Abstract Classes (ABC — जो सीधे object नहीं बन सकतीं)

---

## 🔵 Simple Definition (English)
An abstract class is a class that cannot be instantiated directly. It declares methods (marked with `@abstractmethod`) that every child class MUST implement. In Python you build one by inheriting from `abc.ABC`.

## 🔵 सरल परिभाषा (Hindi)
Abstract class ऐसी class है जिसका object सीधे नहीं बन सकता। यह ऐसे methods declare करती है (`@abstractmethod` से) जिन्हें हर child class को ज़रूर लिखना पड़ता है। Python में इसे `abc.ABC` से inherit करके बनाते हैं।

---

## 🔴 Problem it Solves
Without a contract, a team can write `StripeGateway` that forgets `refund()`. The bug appears only at runtime, in production, when a customer asks for a refund. An abstract base class moves that failure to the moment the object is created: Python raises `TypeError` immediately if any abstract method is missing. It also documents what a "payment gateway" must look like.

## 🔴 यह क्यों बना? (Hindi)
Contract न हो तो team में कोई `StripeGateway` लिख सकता है जिसमें `refund()` भूल गया। यह bug production में तब दिखता है जब customer refund मांगता है। Abstract base class इस failure को object बनाते समय ही पकड़ लेती है: कोई abstract method missing हो तो Python तुरंत `TypeError` देता है। यह भी साफ documentation है कि "payment gateway" में क्या-क्या होना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → class Shape(ABC):  ABC uses the metaclass ABCMeta
Step 2 → @abstractmethod marks a function; its name goes into Shape.__abstractmethods__
Step 3 → A child class that overrides ALL abstract names clears the set (becomes concrete)
Step 4 → Shape() or Child() (with a missing method) -> object.__new__ checks the set
Step 5 → If the set is not empty -> TypeError: Can't instantiate abstract class ...
Step 6 → Abstract methods may still have a body; children can call it via super()
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → class Shape(ABC):  ABC का metaclass ABCMeta होता है
Step 2 → @abstractmethod function को mark करता है; उसका नाम Shape.__abstractmethods__ में जाता है
Step 3 → जो child सारे abstract names override कर दे, वह concrete बन जाती है
Step 4 → Shape() या कोई अधूरी Child() -> object.__new__ इस set को check करता है
Step 5 → Set खाली नहीं है -> TypeError: Can't instantiate abstract class ...
Step 6 → Abstract method में body भी हो सकती है; child उसे super() से call कर सकता है
```

---

## 🟡 Real World Example
Razorpay-style checkout supports several gateways. A `PaymentGateway` ABC demands `charge()` and `refund()`. `RazorpayGateway` and `StripeGateway` implement both. Checkout code only talks to `PaymentGateway`, so adding PayU later needs no change in checkout. Other examples: `BaseRepository` (`get`, `save`), `LLMClient` (`complete`) for swapping OpenAI and Anthropic, and the stdlib's own `collections.abc.Mapping`.

## 🟡 Real Example Hindi mein
Razorpay जैसा checkout कई gateways support करता है। `PaymentGateway` ABC में `charge()` और `refund()` ज़रूरी हैं। `RazorpayGateway` और `StripeGateway` दोनों लिखते हैं। Checkout code सिर्फ `PaymentGateway` से बात करता है, इसलिए बाद में PayU जोड़ने पर checkout नहीं बदलता। और उदाहरण: `BaseRepository` (`get`, `save`), OpenAI और Anthropic बदलने के लिए `LLMClient` (`complete`), और stdlib का `collections.abc.Mapping`।

---

## 💻 Code Example — Basic
```python
# Basic ABC example
from abc import ABC, abstractmethod             # tools for abstract classes
import math                                     # for pi


class Shape(ABC):                               # abstract base class
    @abstractmethod                             # children MUST override this
    def area(self) -> float:                    # contract: return the area
        ...                                     # no body needed

    def describe(self) -> str:                  # normal method shared by all children
        return f"{type(self).__name__} area={self.area():.2f}"   # uses the child's area()


class Circle(Shape):                            # concrete child
    def __init__(self, r: float) -> None:       # constructor
        self.r: float = r                       # radius

    def area(self) -> float:                    # implements the contract
        return math.pi * self.r ** 2            # pi r squared


class Square(Shape):                            # incomplete child on purpose
    pass                                        # forgot area()


print(Circle(2).describe())                     # works
try:                                            # abstract class cannot be created
    Shape()                                     # direct creation
except TypeError as e:                          # Python blocks it
    print("Error 1:", e)                        # message names the method
try:                                            # child forgot to implement
    Square()                                    # incomplete child
except TypeError as e:                          # also blocked
    print("Error 2:", e)                        # same kind of message
print(Shape.__abstractmethods__)                # frozenset of abstract names

# Output:
# Circle area=12.57
# Error 1: Can't instantiate abstract class Shape without an implementation for abstract method 'area'
# Error 2: Can't instantiate abstract class Square without an implementation for abstract method 'area'
# frozenset({'area'})
```
Note: the exact wording of the error changed in Python 3.12 (older versions say "with abstract method area"). The exception type, `TypeError`, is the same.

## 💻 Code Example — Advanced
```python
# Production style: payment gateway contract + abstract property + registry
from abc import ABC, abstractmethod             # ABC tools
from dataclasses import dataclass               # simple result type


@dataclass(frozen=True)                         # immutable result
class ChargeResult:
    ok: bool                                    # did it succeed
    txn_id: str                                 # gateway transaction id


class PaymentGateway(ABC):                      # the contract
    @property
    @abstractmethod                             # abstract read-only property
    def name(self) -> str: ...                  # every gateway needs a name

    @abstractmethod
    def charge(self, amount_paise: int) -> ChargeResult: ...    # must implement

    @abstractmethod
    def refund(self, txn_id: str) -> bool: ...  # must implement

    def charge_safe(self, amount_paise: int) -> ChargeResult:   # template method (shared logic)
        if amount_paise <= 0:                   # validation lives in ONE place
            raise ValueError("amount must be positive")   # reject bad input
        return self.charge(amount_paise)        # delegate to the child

    registry: dict[str, type["PaymentGateway"]] = {}   # name -> class

    def __init_subclass__(cls, **kwargs: object) -> None:   # runs when a subclass is defined
        super().__init_subclass__(**kwargs)     # keep cooperative chain
        PaymentGateway.registry[cls.__name__] = cls   # auto-register every subclass


class FakeRazorpay(PaymentGateway):             # concrete gateway
    @property
    def name(self) -> str:                      # implements the abstract property
        return "razorpay"

    def charge(self, amount_paise: int) -> ChargeResult:
        return ChargeResult(True, f"rzp_{amount_paise}")    # pretend success

    def refund(self, txn_id: str) -> bool:
        return txn_id.startswith("rzp_")        # pretend refund rule


gw: PaymentGateway = FakeRazorpay()             # program against the contract
print(gw.name, gw.charge_safe(500))             # shared validation + child logic
print(gw.refund("rzp_500"))                     # True
try:                                            # shared validation rejects it
    gw.charge_safe(0)                           # invalid amount
except ValueError as e:                         # handle
    print("Error:", e)                          # amount must be positive
print(list(PaymentGateway.registry))            # auto-registered subclasses

# Output:
# razorpay ChargeResult(ok=True, txn_id='rzp_500')
# True
# Error: amount must be positive
# ['FakeRazorpay']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Abstract class | `class X(ABC)` + `@abstractmethod` | No keyword in JS (TypeScript has `abstract`) |
| When error is raised | At instantiation (`TypeError`) | Only if you throw manually |
| Abstract property | `@property` + `@abstractmethod` | n/a |
| Block direct creation | Automatic | `if (new.target === Base) throw ...` |

```python
# Python way
from abc import ABC, abstractmethod

class Base(ABC):
    @abstractmethod
    def run(self) -> str: ...       # must be implemented

class Job(Base):
    def run(self) -> str:
        return "done"

print(Job().run())                  # done
```
```javascript
// JavaScript way — you must simulate it by hand
class Base {
  constructor() {
    if (new.target === Base) throw new TypeError("abstract!");   // block direct use
  }
  run() { throw new Error("not implemented"); }   // fails only when called
}
class Job extends Base { run() { return "done"; } }
console.log(new Job().run());       // done
```

Key difference: Python checks missing methods when you create the object, so mistakes show up early. In plain JavaScript the missing method fails later, at call time (TypeScript's `abstract` gives compile-time safety).

---

## 🟠 FastAPI Connection
FastAPI apps use ABCs for the service layer: an abstract `UserRepository` with an in-memory version for tests and a SQL version for production, injected via `Depends`. The route code never changes.

```python
# FastAPI example — abstract repository + dependency override
from abc import ABC, abstractmethod             # ABC tools
from fastapi import FastAPI, Depends            # app and DI
from fastapi.testclient import TestClient       # in-process test client


class UserRepo(ABC):                            # contract
    @abstractmethod
    def get_name(self, user_id: int) -> str: ...    # every repo must implement


class MemoryRepo(UserRepo):                     # test/dev implementation
    def get_name(self, user_id: int) -> str:
        return {1: "Asha", 2: "Ravi"}.get(user_id, "unknown")   # tiny fake db


def get_repo() -> UserRepo:                     # dependency provider
    return MemoryRepo()                         # swap with SqlRepo() in production


app: FastAPI = FastAPI()                        # create app


@app.get("/users/{user_id}")                    # GET /users/1
def read_user(user_id: int, repo: UserRepo = Depends(get_repo)) -> dict[str, str]:
    return {"name": repo.get_name(user_id)}     # route only knows the contract


client: TestClient = TestClient(app)            # test client
print(client.get("/users/1").json())            # {'name': 'Asha'}

# Output:
# {'name': 'Asha'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to inherit from `ABC` (no enforcement)
✅ Correct: inherit `ABC` (or use `metaclass=ABCMeta`)

```python
from abc import abstractmethod, ABC

class Wrong:                       # not an ABC
    @abstractmethod
    def f(self) -> None: ...

class Right(ABC):                  # real ABC
    @abstractmethod
    def f(self) -> None: ...

Wrong()                            # works silently - no protection!
try:
    Right()
except TypeError:
    print("Right is protected")    # Right is protected
```

❌ Mistake 2: Wrong decorator order for abstract properties
✅ Correct: `@property` on the outside, `@abstractmethod` directly above the function

```python
from abc import ABC, abstractmethod

class A(ABC):
    # Wrong order: @abstractmethod above @property raises
    # AttributeError: attribute '__isabstractmethod__' of 'property' objects is not writable
    # Right:
    @property
    @abstractmethod
    def name(self) -> str: ...

class B(A):
    @property
    def name(self) -> str:
        return "b"

print(B().name)                    # b
```

❌ Mistake 3: Expecting the abstract method's body to be skipped
✅ Correct: children can call it with `super()` — it is a normal function

```python
from abc import ABC, abstractmethod

class Base(ABC):
    @abstractmethod
    def hook(self) -> str:
        return "base default"      # abstract but has a body

class Child(Base):
    def hook(self) -> str:
        return super().hook() + " + child"    # reuse the body

print(Child().hook())              # base default + child
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from abc import ABC, abstractmethod

class A(ABC):
    @abstractmethod
    def f(self) -> int: ...

class B(A):
    pass

B.f = lambda self: 1          # patch the method AFTER class creation
try:
    print(B().f())
except TypeError as e:
    print("TypeError")
```
Answer: It prints `TypeError`. The set of abstract names (`__abstractmethods__`) is computed once, when the class is created. Adding `f` later does not update it, so `B` is still abstract. Fix: call `abc.update_abstractmethods(B)` (Python 3.10+) after patching; then `B().f()` returns `1`.

---

## ⚫ Interview Questions + Answers

Q1: How does Python stop you from instantiating an abstract class?
A1: `ABCMeta` stores abstract names in `__abstractmethods__`. `object.__new__` checks that the set is empty and otherwise raises `TypeError`. This check happens at instantiation, not at class definition.

Q2: ABC vs a normal base class that raises `NotImplementedError`?
A2: `NotImplementedError` fails only when the method is called (late). ABC fails when the object is created (early) and tools like mypy can see the contract. Use ABC for real contracts.

Q3: Can an abstract class have a constructor and normal methods?
A3: Yes. It can hold `__init__`, concrete helpers and class variables. Only the `@abstractmethod` ones must be overridden. This is the "template method" pattern.

Q4: What are abstract classmethods and staticmethods?
A4: Stack the decorators: `@classmethod` above `@abstractmethod`. Children must provide a classmethod with that name. Example: an abstract `from_config(cls, cfg)` factory.

Q5: ABC or `Protocol`?
A5: ABC uses nominal typing: classes must inherit it (and can share code). `typing.Protocol` uses structural typing: any class with the right methods qualifies, no inheritance. Use ABC when you need shared logic or runtime enforcement.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Defining a plugin or provider contract (payment gateway, storage, LLM client)
- Several classes share logic but must each supply specific steps (template method)
- You want errors at object creation, not at call time

❌ Avoid when:
- A simple function or a callable would do
- You do not need shared code and want duck typing flexibility (use `Protocol`)
- There is only one implementation and no plan for another

---

## 📊 Visual Diagram
```
            PaymentGateway (ABC)
            abstract: charge(), refund()
            concrete: charge_safe()
               /                 \
   RazorpayGateway          StripeGateway
   charge() refund()        charge() refund()      -> can be created
                            
   BrokenGateway (missing refund) -> TypeError at BrokenGateway()
   PaymentGateway()               -> TypeError (abstract)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ABC | Helper base class for abstract classes | Abstract class बनाने वाली base class |
| @abstractmethod | Marks a method children must override | जो method child को लिखना ही है |
| Concrete class | Class with all abstract methods done | पूरी तरह लागू की गई class |
| Template method | Base has the algorithm, child fills steps | Base में flow, child में steps |
| ABCMeta | Metaclass that enforces the rules | नियम लागू करने वाली metaclass |
| Contract | The set of methods a class promises | Class के वादा किए गए methods |

---

## ⚡ 3-Line Summary
English: An ABC defines methods that children must implement, using `@abstractmethod`. Python raises `TypeError` when you instantiate an incomplete class. Use it for contracts like gateways and repositories, with shared logic in the base.
Hindi: ABC उन methods को define करती है जो children को लिखने ही हैं (`@abstractmethod`)। अधूरी class का object बनाते ही Python `TypeError` देता है। Gateways और repositories जैसे contracts के लिए इसे इस्तेमाल करें, shared logic base में रखें।

---

## ➡️ Next Topic
**096. Interfaces in Python** — Python has no `interface` keyword; learn how ABCs and `typing.Protocol` act as interfaces.
