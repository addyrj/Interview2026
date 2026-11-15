---

# 423. Abstract Factory
# हिंदी में: Abstract Factory (संबंधित objects का पूरा परिवार बनाना)

---

## 🔵 Simple Definition (English)
Abstract Factory is a pattern where one factory object creates a whole family of related objects that belong together (for example all light-theme widgets, or all Razorpay classes). The client asks the factory and never names concrete classes.

## 🔵 सरल परिभाषा (Hindi)
Abstract Factory ऐसा pattern है जिसमें एक factory object संबंधित objects का पूरा परिवार बनाता है जो साथ में चलते हैं (जैसे सारे light-theme widgets, या Razorpay की सारी classes)। Client factory से मांगता है और concrete classes का नाम कभी नहीं लेता।

---

## 🔴 Problem it Solves
Imagine code that creates `RazorpayClient` and `StripeVerifier` by mistake: parts from different families get mixed and fail at runtime. Hard-coded `if gateway == 'razorpay'` branches spread everywhere. Abstract Factory puts the choice in ONE place and guarantees that products always match.

## 🔴 यह क्यों बना? (Hindi)
सोचो code गलती से `RazorpayClient` और `StripeVerifier` बना देता है: अलग-अलग परिवारों के हिस्से मिल जाते हैं और runtime पर fail होते हैं। `if gateway == 'razorpay'` जैसे branches हर जगह फैल जाते हैं। Abstract Factory यह चुनाव एक ही जगह रखता है और पक्का करता है कि products हमेशा आपस में मेल खाएं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define interfaces for each product (PaymentClient, WebhookVerifier)
Step 2 → Define an abstract factory interface with one method per product
Step 3 → Write one concrete factory per family (RazorpayFactory, StripeFactory)
Step 4 → Each concrete factory returns products of ITS family only
Step 5 → At startup, pick the factory from config (registry dict)
Step 6 → Client code uses only the abstract interfaces
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर product के लिए interface बनाओ (PaymentClient, WebhookVerifier)
Step 2 → Abstract factory interface बनाओ जिसमें हर product के लिए एक method हो
Step 3 → हर परिवार के लिए एक concrete factory लिखो (RazorpayFactory, StripeFactory)
Step 4 → हर concrete factory सिर्फ अपने परिवार के products लौटाती है
Step 5 → Startup पर config से factory चुनो (registry dict)
Step 6 → Client code सिर्फ abstract interfaces इस्तेमाल करता है
```

---

## 🟡 Real World Example
An Indian SaaS supports Razorpay for India and Stripe for international customers. Each gateway needs a client (charge money) and a webhook verifier (check signature). A `GatewayFactory` per provider guarantees the Razorpay client is never paired with the Stripe verifier. Cloud storage (S3 vs GCS: uploader + signer) and UI themes follow the same shape.

## 🟡 Real Example Hindi mein
एक भारतीय SaaS भारत के लिए Razorpay और विदेशी customers के लिए Stripe सपोर्ट करता है। हर gateway को client (पैसा charge करना) और webhook verifier (signature जांचना) चाहिए। हर provider की एक `GatewayFactory` पक्का करती है कि Razorpay client कभी Stripe verifier के साथ न जुड़े। Cloud storage (S3 बनाम GCS: uploader + signer) और UI themes भी इसी तरह के हैं।

---

## 💻 Code Example — Basic
```python
# Basic Abstract Factory: one factory creates a whole FAMILY of related objects
from abc import ABC, abstractmethod           # abstract base classes


class Button(ABC):                            # product 1 interface
    @abstractmethod
    def render(self) -> str: ...              # every button can render


class Checkbox(ABC):                          # product 2 interface
    @abstractmethod
    def render(self) -> str: ...              # every checkbox can render


class LightButton(Button):
    def render(self) -> str:
        return "[light button]"               # light-theme button


class LightCheckbox(Checkbox):
    def render(self) -> str:
        return "[light checkbox]"             # light-theme checkbox


class DarkButton(Button):
    def render(self) -> str:
        return "[dark button]"                # dark-theme button


class DarkCheckbox(Checkbox):
    def render(self) -> str:
        return "[dark checkbox]"              # dark-theme checkbox


class UIFactory(ABC):                         # the abstract factory
    @abstractmethod
    def button(self) -> Button: ...           # makes a button
    @abstractmethod
    def checkbox(self) -> Checkbox: ...       # makes a checkbox


class LightFactory(UIFactory):
    def button(self) -> Button:
        return LightButton()                  # family: light
    def checkbox(self) -> Checkbox:
        return LightCheckbox()                # family: light


class DarkFactory(UIFactory):
    def button(self) -> Button:
        return DarkButton()                   # family: dark
    def checkbox(self) -> Checkbox:
        return DarkCheckbox()                 # family: dark


def build_screen(factory: UIFactory) -> list[str]:
    return [factory.button().render(), factory.checkbox().render()]   # client never names concrete classes


print(build_screen(LightFactory()))           # whole light family
print(build_screen(DarkFactory()))            # whole dark family

# Output:
# ['[light button]', '[light checkbox]']
# ['[dark button]', '[dark checkbox]']
```

## 💻 Code Example — Advanced
```python
# Production style: payment-gateway family (Razorpay / Stripe), chosen by config
from abc import ABC, abstractmethod           # interfaces
from dataclasses import dataclass             # result type


@dataclass(frozen=True)
class ChargeResult:
    gateway: str                              # who processed it
    amount: int                               # amount in paise/cents
    ok: bool                                  # success flag


class PaymentClient(ABC):                     # product 1: charge money
    @abstractmethod
    def charge(self, amount: int) -> ChargeResult: ...


class WebhookVerifier(ABC):                   # product 2: verify webhook signature
    @abstractmethod
    def verify(self, payload: str, signature: str) -> bool: ...


class RazorpayClient(PaymentClient):
    def charge(self, amount: int) -> ChargeResult:
        return ChargeResult("razorpay", amount, True)


class RazorpayVerifier(WebhookVerifier):
    def verify(self, payload: str, signature: str) -> bool:
        return signature == f"rzp:{payload}"  # toy signature rule


class StripeClient(PaymentClient):
    def charge(self, amount: int) -> ChargeResult:
        return ChargeResult("stripe", amount, True)


class StripeVerifier(WebhookVerifier):
    def verify(self, payload: str, signature: str) -> bool:
        return signature == f"stripe:{payload}"   # toy signature rule


class GatewayFactory(ABC):                    # abstract factory
    @abstractmethod
    def client(self) -> PaymentClient: ...
    @abstractmethod
    def verifier(self) -> WebhookVerifier: ...


class RazorpayFactory(GatewayFactory):
    def client(self) -> PaymentClient: return RazorpayClient()
    def verifier(self) -> WebhookVerifier: return RazorpayVerifier()


class StripeFactory(GatewayFactory):
    def client(self) -> PaymentClient: return StripeClient()
    def verifier(self) -> WebhookVerifier: return StripeVerifier()


REGISTRY: dict[str, type[GatewayFactory]] = {"razorpay": RazorpayFactory, "stripe": StripeFactory}


def get_factory(name: str) -> GatewayFactory:
    try:
        return REGISTRY[name]()               # build the right family
    except KeyError:
        raise ValueError(f"unknown gateway: {name!r}") from None   # clear error


f: GatewayFactory = get_factory("razorpay")
print(f.client().charge(49900))               # ChargeResult(...)
print(f.verifier().verify("order1", "rzp:order1"))   # True: same family
print(get_factory("stripe").verifier().verify("order1", "rzp:order1"))   # False: wrong family
try:
    get_factory("paypal")
except ValueError as e:
    print("Error:", e)

# Output:
# ChargeResult(gateway='razorpay', amount=49900, ok=True)
# True
# False
# Error: unknown gateway: 'paypal'
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Interface | `ABC` / `Protocol` | TypeScript `interface` (or duck typing) |
| Family selection | registry dict of classes | object map `{razorpay: RazorpayFactory}` |
| Enforcement | `TypeError` if abstract method missing | none at runtime in plain JS |
| Classes needed | often a plain function works too | often a plain function works too |

```python
# Python way
FACTORIES: dict[str, type] = {"light": LightFactory, "dark": DarkFactory}   # registry
factory = FACTORIES["dark"]()                # pick the family once
screen = [factory.button().render(), factory.checkbox().render()]
```
```javascript
// JavaScript way
const factories = { light: new LightFactory(), dark: new DarkFactory() };  // registry
const factory = factories["dark"];           // pick the family once
const screen = [factory.button().render(), factory.checkbox().render()];
```

Key difference: Python's `abc.ABC` refuses to create a factory that forgets a method (runtime TypeError). Plain JavaScript has no such check; you need TypeScript. In both languages, functions and dicts often replace heavy class hierarchies.

---

## 🟠 FastAPI Connection
FastAPI's `Depends()` is a factory mechanism: a dependency function builds the right object per request. With `app.dependency_overrides` you swap the whole family for tests (real mailer vs fake mailer). For multi-provider code, build the abstract factory once in `lifespan` and inject it with `Depends`.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()


class Mailer:                                 # one family member
    def send(self, to: str) -> str: return f"smtp -> {to}"


class FakeMailer(Mailer):
    def send(self, to: str) -> str: return f"fake -> {to}"


def get_mailer() -> Mailer:                   # factory function used as dependency
    return Mailer()


@app.post("/welcome")
def welcome(to: str, m: Mailer = Depends(get_mailer)) -> dict[str, str]:
    return {"sent": m.send(to)}


app.dependency_overrides[get_mailer] = lambda: FakeMailer()   # swap the family in tests
print(TestClient(app).post("/welcome", params={"to": "a@x.com"}).json())

# Output:
# {'sent': 'fake -> a@x.com'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Client code names concrete classes
✅ Correct: client depends only on the abstract factory

```python
# Wrong
client = RazorpayClient()                 # hard-coded, cannot switch gateway
# Right
client = factory.client()                 # factory decides which class
```

❌ Mistake 2: Mixing products of different families
✅ Correct: get ALL products from the same factory object

```python
# Wrong
client = RazorpayFactory().client()
verifier = StripeFactory().verifier()     # families mixed -> signature checks fail
# Right
f = get_factory("razorpay")
client, verifier = f.client(), f.verifier()
```

❌ Mistake 3: Using Abstract Factory when only one product exists
✅ Correct: use a simple Factory function (topic 422)

```python
# Wrong: factory class + interface for a single product is over-engineering
# Right: def make_client(name: str) -> PaymentClient: ...
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from abc import ABC, abstractmethod
class Factory(ABC):
    @abstractmethod
    def make(self) -> str: ...
class Half(Factory):
    pass                                      # forgot make()
try:
    Half()
except TypeError as e:
    print(e)
print(Factory.__abstractmethods__)
```
Answer: Instantiating `Half()` raises `TypeError: Can't instantiate abstract class Half without an implementation for abstract method 'make'` (Python 3.12+ wording; older versions say 'with abstract method make'). The error appears at instantiation, not at class definition. The second print shows `frozenset({'make'})`: Python tracks unimplemented abstract names in `__abstractmethods__`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between Factory and Abstract Factory?
A1: A Factory creates ONE kind of product. An Abstract Factory creates a FAMILY of related products and guarantees they are compatible. Abstract Factory is often implemented with several factory methods.

Q2: When do you need Abstract Factory in Python?
A2: When two or more related objects must vary together: payment client + verifier, DB connection + query builder, UI widgets per theme. If only one object varies, a function or dict registry is enough.

Q3: How does it support testing?
A3: You pass a fake factory (FakeGateway) that returns in-memory products. Production code stays the same, tests run without network. In FastAPI use `dependency_overrides`.

Q4: What is the drawback?
A4: Many classes: every new product type must be added to the abstract factory and to every concrete factory. Adding a new family is easy; adding a new product kind is hard.

Q5: Can Python do this without classes?
A5: Yes. A dict of callables or a module per family works. `Protocol` gives type checking without inheritance. Use classes only when the structure helps readers.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Several related objects must always come from the same family
- You want to switch the whole family (prod vs test, Razorpay vs Stripe) with one config value
- Client code must stay unaware of concrete classes

❌ Avoid when:
- Only one product type varies: use a simple factory function
- The family will never change: direct construction is clearer
- You would create many tiny classes for a tiny app

---

## 📊 Visual Diagram
```
              GatewayFactory (abstract)
               client()   verifier()
                 ^            ^
     +-----------+            +-----------+
RazorpayFactory                     StripeFactory
 |-> RazorpayClient                  |-> StripeClient
 |-> RazorpayVerifier                |-> StripeVerifier

Client code:  f = get_factory("razorpay")  ->  f.client(), f.verifier()
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Abstract Factory | Factory that makes a family of products | Products का परिवार बनाने वाली factory |
| Product family | Objects designed to work together | साथ चलने वाले objects |
| Concrete factory | Real implementation for one family | एक परिवार की असली implementation |
| Registry | Dict mapping name to class | नाम से class का dict |
| Composition root | Single place where objects are wired | Objects जोड़ने की एक जगह |

---

## ⚡ 3-Line Summary
English: Abstract Factory creates whole families of related objects through one interface so products always match. Choose the factory once from config and let client code use only abstract types. In Python a registry dict plus `ABC` or `Protocol` is usually enough.
Hindi: Abstract Factory एक interface से संबंधित objects के पूरे परिवार बनाता है ताकि products हमेशा आपस में मेल खाएं। Factory config से एक बार चुनें और client code सिर्फ abstract types इस्तेमाल करे। Python में registry dict और `ABC` या `Protocol` अक्सर काफी होता है।

---

## ➡️ Next Topic
**424. Builder Pattern** — construct complex objects step by step with a fluent interface.
