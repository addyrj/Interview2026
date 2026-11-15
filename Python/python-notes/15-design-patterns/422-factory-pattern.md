---

# 422. Factory Pattern
# हिंदी में: Factory Pattern (Object बनाने वाली Factory)

---

## 🔵 Simple Definition (English)
A factory is a function or class whose only job is to create objects. The caller says what it wants (for example `"upi"`) and the factory decides which class to build and how. The caller never writes `UpiGateway(...)` directly.

## 🔵 सरल परिभाषा (Hindi)
Factory एक function या class है जिसका सिर्फ एक काम है: objects बनाना। Caller बताता है कि उसे क्या चाहिए (जैसे `"upi"`) और factory तय करती है कि कौन सी class कैसे बनानी है। Caller सीधे `UpiGateway(...)` नहीं लिखता।

---

## 🔴 Problem it Solves
Without a factory, `if/elif` chains that pick a class are copied all over the code base: in the checkout route, in the refund job, in the tests. Adding a new payment method means editing every copy, and one forgotten copy becomes a bug. Creation logic (config, API keys, retries) also mixes with business logic. A factory keeps "which class and how to build it" in one place.

## 🔴 यह क्यों बना? (Hindi)
Factory के बिना class चुनने वाली `if/elif` chains पूरे code में copy हो जाती हैं: checkout route में, refund job में, tests में। नया payment method जोड़ने पर हर copy बदलनी पड़ती है, और एक भूली हुई copy bug बन जाती है। Creation logic (config, API keys, retries) business logic में मिल जाता है। Factory "कौन सी class और कैसे बनानी है" एक ही जगह रखती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a common interface (Protocol / ABC): every product has pay()
Step 2 → Write concrete classes: UpiGateway, CardGateway, NetBankingGateway
Step 3 → Write the factory: a function (or registry dict) key -> class
Step 4 → Caller asks factory.create("upi") and receives an object of the interface
Step 5 → Caller only uses the interface; it never imports concrete classes
Step 6 → New product = new class + one registry entry; callers do not change
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक common interface (Protocol / ABC) बनाओ: हर product में pay() है
Step 2 → Concrete classes लिखो: UpiGateway, CardGateway, NetBankingGateway
Step 3 → Factory लिखो: function (या registry dict) key -> class
Step 4 → Caller factory.create("upi") माँगता है और interface का object पाता है
Step 5 → Caller सिर्फ interface इस्तेमाल करता है; concrete classes import नहीं करता
Step 6 → नया product = नई class + registry में एक entry; callers नहीं बदलते
```

---

## 🟡 Real World Example
Zomato-style checkout supports UPI, cards, wallets and cash on delivery. The route receives `method="upi"` from the mobile app. A `PaymentFactory` returns the right gateway object. A notification service does the same with "sms", "email", "push" senders. Tests use the same factory to return a fake gateway.

## 🟡 Real Example Hindi mein
Zomato जैसा checkout UPI, cards, wallets और cash on delivery support करता है। Route को mobile app से `method="upi"` मिलता है। `PaymentFactory` सही gateway object लौटाती है। Notification service "sms", "email", "push" senders के लिए यही करती है। Tests भी वही factory इस्तेमाल करके fake gateway लेते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: simple factory function that returns different classes
class Dog:                                        # first product
    def speak(self) -> str:                       # common method name
        return "Woof"                             # dog sound


class Cat:                                        # second product
    def speak(self) -> str:                       # same method name
        return "Meow"                             # cat sound


def animal_factory(kind: str) -> Dog | Cat:       # factory function
    if kind == "dog":                             # choose by key
        return Dog()                              # build a Dog
    if kind == "cat":                             # another key
        return Cat()                              # build a Cat
    raise ValueError(f"unknown animal: {kind}")   # fail loudly on bad input


for k in ["dog", "cat"]:                          # use the factory
    print(animal_factory(k).speak())              # caller never names Dog or Cat

try:                                              # unknown key
    animal_factory("cow")                         # not registered
except ValueError as e:                           # catch it
    print("Error:", e)                            # show message

# Output:
# Woof
# Meow
# Error: unknown animal: cow
```

## 💻 Code Example — Advanced
```python
# Production style: Protocol + registry + decorator-based registration
from __future__ import annotations                # allow forward references in hints
from typing import Protocol, ClassVar             # interface + class-level typing


class PaymentGateway(Protocol):                   # the interface callers rely on
    def pay(self, amount: float) -> str: ...      # every gateway must have pay()


class GatewayFactory:                             # factory with a registry
    _registry: ClassVar[dict[str, type[PaymentGateway]]] = {}   # key -> class

    @classmethod
    def register(cls, key: str):                  # decorator factory
        def deco(gateway_cls: type[PaymentGateway]) -> type[PaymentGateway]:
            cls._registry[key] = gateway_cls      # store class under key
            return gateway_cls                    # return class unchanged
        return deco                               # give decorator back

    @classmethod
    def create(cls, key: str, **config: str) -> PaymentGateway:
        try:                                      # look up the class
            gateway_cls = cls._registry[key]      # may raise KeyError
        except KeyError:                          # unknown key
            known: str = ", ".join(sorted(cls._registry))   # list valid keys
            raise ValueError(f"unknown gateway '{key}', use one of: {known}") from None
        return gateway_cls(**config)              # build with config (API keys etc.)


@GatewayFactory.register("upi")                   # self-registering product
class UpiGateway:
    def __init__(self, vpa: str = "shop@upi") -> None:
        self.vpa: str = vpa                       # merchant UPI id

    def pay(self, amount: float) -> str:
        return f"UPI Rs.{amount:.2f} to {self.vpa}"   # pretend to pay


@GatewayFactory.register("card")                  # another product
class CardGateway:
    def __init__(self, merchant: str = "acme") -> None:
        self.merchant: str = merchant             # merchant account

    def pay(self, amount: float) -> str:
        return f"CARD Rs.{amount:.2f} via {self.merchant}"   # pretend to pay


def checkout(method: str, amount: float) -> str:  # business code, no concrete classes
    gateway: PaymentGateway = GatewayFactory.create(method)   # ask factory
    return gateway.pay(amount)                    # use the interface only


print(checkout("upi", 499))                       # UPI path
print(checkout("card", 1200.5))                   # card path
print(GatewayFactory.create("upi", vpa="zomato@upi").pay(10))   # custom config
try:                                              # error handling
    checkout("bitcoin", 1)                        # not registered
except ValueError as e:                           # catch bad key
    print("Error:", e)                            # helpful message

# Output:
# UPI Rs.499.00 to shop@upi
# CARD Rs.1200.50 via acme
# UPI Rs.10.00 to zomato@upi
# Error: unknown gateway 'bitcoin', use one of: card, upi
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Factory | function / classmethod / registry dict | function returning object, or `static create()` |
| Classes are values | Yes: `type[X]` can be stored in a dict | Yes: classes are first-class |
| Interface | `Protocol` / `ABC` | TypeScript `interface` |
| Auto-register | decorator | decorator (TS) or manual map |

```python
# Python way — registry dict of classes
creators: dict[str, type] = {"list": list, "set": set}   # classes are values
print(creators["set"]([1, 1, 2]))                        # {1, 2}
```
```javascript
// JavaScript way — object map of constructors
const creators = { list: Array, set: Set };               // classes as values
console.log(new creators.set([1, 1, 2]));                 // Set(2) { 1, 2 }
```

Key difference: in Python the simplest factory is often just a dict of classes, because classes are normal objects. Python's `Protocol` gives duck-typed interfaces; no `implements` keyword is needed.

---

## 🟠 FastAPI Connection
Factories appear in FastAPI whenever the request or the environment decides the implementation: choose a payment gateway from the request body, or choose a storage backend (local vs S3) from settings. Combine with `Depends` so that routes stay clean.

```python
# FastAPI example — factory behind Depends
from typing import Annotated                      # for Depends typing
from fastapi import FastAPI, Depends, HTTPException   # core imports


class UpiGateway:                                 # product 1
    def pay(self, amount: float) -> str:
        return f"upi:{amount}"                    # fake payment


class CardGateway:                                # product 2
    def pay(self, amount: float) -> str:
        return f"card:{amount}"                   # fake payment


REGISTRY: dict[str, type] = {"upi": UpiGateway, "card": CardGateway}   # key -> class


def get_gateway(method: str) -> UpiGateway | CardGateway:   # factory used as dependency
    cls = REGISTRY.get(method)                    # find the class
    if cls is None:                               # unknown method
        raise HTTPException(status_code=400, detail="unknown method")   # client error
    return cls()                                  # build the object


app: FastAPI = FastAPI()                          # create app


@app.post("/pay")                                 # POST /pay?method=upi&amount=10
def pay(amount: float, gw: Annotated[UpiGateway | CardGateway, Depends(get_gateway)]) -> dict[str, str]:
    return {"result": gw.pay(amount)}             # route never names concrete classes
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Repeating `if/elif` class selection in many places
✅ Correct: one factory, one place

```python
# Wrong — same chain copied in checkout, refund, report
# if m == "upi": g = UpiGateway() elif m == "card": g = CardGateway() ...
# Right
# g = GatewayFactory.create(m)
```

❌ Mistake 2: Returning `None` for unknown keys
✅ Correct: raise a clear error that lists valid keys

```python
registry = {"a": int}
# Wrong
obj = registry.get("zzz")          # None, crashes later with AttributeError
# Right
try:
    registry["zzz"]
except KeyError:
    print("unknown key, valid: a")
```

❌ Mistake 3: Using a factory for a class that has only one version
✅ Correct: call the constructor directly (YAGNI, keep it simple)

```python
class Config: ...
# Wrong: ConfigFactory.create() when there is only one Config
# Right
cfg = Config()
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
class A:
    def __init__(self, v):
        self.v = v

def make(cls=A, items=[]):
    items.append(cls(len(items)))
    return items

print(len(make()))
print(len(make()))
print([o.v for o in make()])
```
Answer: `1`, `2`, `[0, 1, 2]`. The default `items=[]` is created once when the function is defined (mutable default argument), so all calls share the same list. A factory must never use a mutable default; use `items: list | None = None` and create a new list inside.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Simple Factory, Factory Method and Abstract Factory?
A1: Simple factory is one function with a switch. Factory Method lets subclasses decide which product to create (`create()` overridden). Abstract Factory creates whole families of related objects (see topic 423).

Q2: Why use a factory instead of calling constructors directly?
A2: It centralizes creation logic and configuration, hides concrete classes, and lets you swap implementations (including fakes in tests) without editing callers (Open/Closed principle).

Q3: Is `@classmethod` constructor like `datetime.fromisoformat` a factory?
A3: Yes. Alternative constructors implemented as classmethods are the Pythonic factory methods.

Q4: How do you add a new product without changing factory code?
A4: Use a registry plus a decorator (or entry points / plugin discovery), as in the advanced example. Products register themselves on import.

Q5: Do you need factories in Python as much as in Java?
A5: Less. Classes are first-class values and functions are flexible, so a dict of classes or a plain function is often enough. Use a formal factory only when creation logic is non-trivial.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Which class to build depends on input, config or environment
- Construction is complex (keys, retries, connections)
- You want to swap implementations (tests, plugins)

❌ Avoid when:
- Only one concrete class exists
- Constructor call is trivial and unlikely to change
- A simple dict lookup or `functools.partial` does the job

---

## 📊 Visual Diagram
```
 Caller ──create("upi")──▶ [ GatewayFactory ]
                                │ registry
                    ┌───────────┼─────────────┐
                    ▼           ▼             ▼
               UpiGateway  CardGateway  NetBankingGateway
                    └─────── all implement pay() ──────┘
 Caller receives PaymentGateway and calls pay(); it never imports a concrete class.
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Factory | Code that creates objects | Objects बनाने वाला code |
| Product | Object the factory returns | Factory से मिलने वाला object |
| Registry | Dict of key to class | Key से class का dict |
| Protocol | Duck-typed interface | Duck-typed interface |
| Factory Method | Subclass chooses product | Subclass तय करती है कौन सा product |
| Open/Closed | Open to extend, closed to edit | बढ़ाने के लिए खुला, बदलने के लिए बंद |

---

## ⚡ 3-Line Summary
English: A factory creates objects so callers depend on an interface, not concrete classes. In Python a registry dict plus a decorator is the cleanest version. Use it when creation depends on input or config, not for a single class.
Hindi: Factory objects बनाती है ताकि callers concrete classes की जगह interface पर निर्भर रहें। Python में registry dict और decorator सबसे साफ तरीका है। इसे तब इस्तेमाल करो जब creation input या config पर निर्भर हो, सिर्फ एक class के लिए नहीं।

---

## ➡️ Next Topic
**423. Abstract Factory** — create whole families of related objects (for example a Razorpay family vs a Stripe family) that always match each other.
