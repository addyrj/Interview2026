---

# 430. Dependency Injection Pattern
# हिंदी में: Dependency Injection Pattern (Dependencies बाहर से देना)

---

## 🔵 Simple Definition (English)
Dependency Injection (DI) means an object receives the things it needs (mailer, database, clock) from outside, usually through its constructor, instead of creating them itself. This makes code easy to test and easy to reconfigure.

## 🔵 सरल परिभाषा (Hindi)
Dependency Injection (DI) का मतलब है कि object अपनी जरूरत की चीजें (mailer, database, clock) खुद बनाने की जगह बाहर से पाता है, आमतौर पर constructor के जरिए। इससे code test करना और बदलना आसान हो जाता है।

---

## 🔴 Problem it Solves
If `SignupService` creates `SmtpMailer()` inside itself, every test sends real emails or needs heavy patching, and you cannot switch providers without editing the service. Hidden global state and imports make code rigid. DI turns dependencies into visible parameters.

## 🔴 यह क्यों बना? (Hindi)
अगर `SignupService` अंदर `SmtpMailer()` खुद बनाती है तो हर test असली emails भेजता है या भारी patching मांगता है, और provider बदलने के लिए service बदलनी पड़ती है। Hidden global state और imports code को कठोर बना देते हैं। DI dependencies को दिखने वाले parameters बना देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → List what the class needs (gateway, clock, repository)
Step 2 → Declare them as constructor parameters typed with Protocols
Step 3 → The class stores them and only uses the interface
Step 4 → ONE place (composition root) builds real objects from settings
Step 5 → Tests build the class with fakes instead
Step 6 → No dependency is created inside business code
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → लिखो कि class को क्या चाहिए (gateway, clock, repository)
Step 2 → उन्हें Protocol type वाले constructor parameters बनाओ
Step 3 → Class उन्हें store करती है और सिर्फ interface इस्तेमाल करती है
Step 4 → एक जगह (composition root) settings से असली objects बनाती है
Step 5 → Tests class को fakes के साथ बनाते हैं
Step 6 → Business code के अंदर कोई dependency नहीं बनती
```

---

## 🟡 Real World Example
A checkout service receives a payment gateway and a clock. In production the composition root passes `RazorpayGateway(key)`; in tests it passes `FakeGateway()` and a fixed clock so results are repeatable. Settings, DB sessions, and HTTP clients in FastAPI services are all injected this way.

## 🟡 Real Example Hindi mein
Checkout service को payment gateway और clock मिलती है। Production में composition root `RazorpayGateway(key)` देता है; tests में `FakeGateway()` और fixed clock ताकि results दोहराने योग्य हों। FastAPI services में settings, DB sessions और HTTP clients सब इसी तरह inject होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic Dependency Injection: pass dependencies in, do not create them inside
class SmtpMailer:
    def send(self, to: str) -> str:
        return f"smtp:{to}"                   # real mailer


class FakeMailer:
    def send(self, to: str) -> str:
        return f"fake:{to}"                   # test mailer


class SignupService:
    def __init__(self, mailer: SmtpMailer | FakeMailer) -> None:
        self.mailer = mailer                  # injected from outside

    def signup(self, email: str) -> str:
        return self.mailer.send(email)


print(SignupService(SmtpMailer()).signup("a@x.com"))
print(SignupService(FakeMailer()).signup("a@x.com"))

# Output:
# smtp:a@x.com
# fake:a@x.com
```

## 💻 Code Example — Advanced
```python
# Production style: Protocol-based DI with a small composition root (wiring in ONE place)
from dataclasses import dataclass             # config
from typing import Protocol                   # interfaces


class Clock(Protocol):
    def now(self) -> str: ...


class PaymentGateway(Protocol):
    def charge(self, amount: int) -> str: ...


class SystemClock:
    def now(self) -> str: return "2026-01-01T10:00"    # fixed for repeatable demo


class RazorpayGateway:
    def __init__(self, key: str) -> None:
        if not key:
            raise ValueError("missing API key")
        self.key = key
    def charge(self, amount: int) -> str: return f"rzp charged {amount}"


class FakeGateway:
    def charge(self, amount: int) -> str: return f"fake charged {amount}"


class CheckoutService:
    def __init__(self, gateway: PaymentGateway, clock: Clock) -> None:
        self.gateway, self.clock = gateway, clock       # constructor injection

    def pay(self, amount: int) -> str:
        if amount <= 0:
            raise ValueError("amount must be positive")
        return f"{self.clock.now()} {self.gateway.charge(amount)}"


@dataclass(frozen=True)
class Settings:
    env: str
    razorpay_key: str


def build_checkout(s: Settings) -> CheckoutService:     # composition root
    gw: PaymentGateway = FakeGateway() if s.env == "test" else RazorpayGateway(s.razorpay_key)
    return CheckoutService(gw, SystemClock())


print(build_checkout(Settings("prod", "key_123")).pay(500))
print(build_checkout(Settings("test", "")).pay(500))
try:
    build_checkout(Settings("prod", ""))
except ValueError as e:
    print("Error:", e)

# Output:
# 2026-01-01T10:00 rzp charged 500
# 2026-01-01T10:00 fake charged 500
# Error: missing API key
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Manual DI | constructor parameters | constructor parameters |
| Framework DI | FastAPI `Depends`, `dependency-injector` | NestJS providers, Angular DI |
| Test swap | pass a fake / `dependency_overrides` | pass a mock / `jest.mock` |
| Container needed? | usually no | often yes in NestJS/Angular |

```python
# Python way
class CheckoutService:
    def __init__(self, gateway: PaymentGateway, clock: Clock) -> None:
        self.gateway, self.clock = gateway, clock    # injected, not created here
```
```javascript
// JavaScript way
class CheckoutService {
  constructor(gateway, clock) { this.gateway = gateway; this.clock = clock; }
}
// NestJS: constructor(private readonly gateway: PaymentGateway) {}  // injected by the framework
```

Key difference: Angular and NestJS ship a DI container that builds objects by type. In Python plain constructor injection is usually enough, and FastAPI's `Depends` covers per-request wiring. Containers (`dependency-injector`) are optional for very large apps.

---

## 🟠 FastAPI Connection
`Depends()` is FastAPI's built-in DI. Dependencies can depend on other dependencies, are cached per request, can `yield` (open/close a DB session), and can be replaced in tests with `app.dependency_overrides`. Use `Annotated[T, Depends(fn)]` as the modern style.

```python
# FastAPI example (run with fastapi.testclient — no server needed)
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app: FastAPI = FastAPI()


class Settings:
    greeting: str = "hello"


def get_settings() -> Settings:
    return Settings()


def get_service(s: Annotated[Settings, Depends(get_settings)]) -> str:   # dependency of a dependency
    return s.greeting.upper()


@app.get("/hi")
def hi(g: Annotated[str, Depends(get_service)]) -> dict[str, str]:
    return {"msg": g}


c = TestClient(app)
print(c.get("/hi").json())
app.dependency_overrides[get_service] = lambda: "TEST"   # swap in tests
print(c.get("/hi").json())

# Output:
# {'msg': 'HELLO'}
# {'msg': 'TEST'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Creating the dependency inside the class
✅ Correct: receive it

```python
class Wrong:
    def __init__(self) -> None:
        self.mailer = SmtpMailer()            # hard-wired, cannot be faked
class Right:
    def __init__(self, mailer: Mailer) -> None:
        self.mailer = mailer                  # injected
```

❌ Mistake 2: Calling a function in a default argument
✅ Correct: use `None` and create inside, or inject explicitly

```python
# Wrong
def __init__(self, stamp: int = now()): ...    # evaluated ONCE at definition time
# Right
def __init__(self, stamp: int | None = None) -> None:
    self.stamp = now() if stamp is None else stamp
```

❌ Mistake 3: Service Locator (global registry) disguised as DI
✅ Correct: pass dependencies explicitly

```python
# Wrong
def pay(a: int) -> str:
    return CONTAINER.get("gateway").charge(a)   # hidden dependency
# Right
def pay(gateway: PaymentGateway, a: int) -> str:
    return gateway.charge(a)                    # visible in the signature
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import itertools
tick = itertools.count()
def now() -> int: return next(tick)
class Service:
    def __init__(self, stamp: int = now()):   # default evaluated once, at definition
        self.stamp = stamp
print(Service().stamp, Service().stamp, Service(now()).stamp)
```
Answer: Output: `0 0 1`. The default `stamp=now()` is evaluated once, when `def __init__` runs at class creation (counter is 0). Both `Service()` calls reuse that same 0. `Service(now())` evaluates `now()` at the call site and gets 1. Default arguments are evaluated at definition time, so never put `datetime.now()` or other runtime values there.

---

## ⚫ Interview Questions + Answers

Q1: What is Dependency Injection?
A1: Giving an object its collaborators from outside (constructor, parameter, or framework) instead of letting it create or look them up itself.

Q2: Dependency Injection vs Dependency Inversion?
A2: Inversion is the principle: depend on abstractions, not concrete classes (the D in SOLID). Injection is the technique that supplies the concrete object at runtime.

Q3: Types of injection?
A3: Constructor injection (most common, makes requirements explicit), setter/attribute injection, and parameter/method injection (FastAPI `Depends`).

Q4: What is a composition root?
A4: The one place near program start (`main`, FastAPI `lifespan`, a `build_checkout()` function) where real objects are created and connected. Business code never builds dependencies.

Q5: Do you need a DI container in Python?
A5: Rarely. Manual wiring plus FastAPI `Depends` handle most apps. Containers help when the object graph is large; they add magic and indirection.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code needs databases, HTTP clients, clocks, or random sources that tests must control
- You want to switch implementations by config
- Services should be unit-testable without patching imports

❌ Avoid when:
- Tiny scripts where everything is one function
- Injecting trivial values or pure functions (just import them)
- A DI container where plain constructors would do

---

## 📊 Visual Diagram
```
composition root (build_checkout)
   settings --> RazorpayGateway(key) --+
   SystemClock() ----------------------+--> CheckoutService(gateway, clock)

tests:  FakeGateway() + FixedClock() ---> CheckoutService(gateway, clock)
Same class, different wiring, no code changes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dependency | Object another object needs | दूसरे object को चाहिए object |
| Injection | Providing it from outside | बाहर से देना |
| Composition root | Single place that wires objects | Objects जोड़ने की एक जगह |
| Service locator | Global registry lookup (anti-pattern) | Global registry से ढूंढना (anti-pattern) |
| Test double | Fake/mock replacement | Fake/mock विकल्प |

---

## ⚡ 3-Line Summary
English: Dependency Injection passes collaborators into a class instead of creating them inside it. Wire real objects in one composition root and fakes in tests. FastAPI's `Depends` and `dependency_overrides` give you this out of the box.
Hindi: Dependency Injection collaborators को class के अंदर बनाने की जगह बाहर से पास करता है। असली objects एक composition root में जोड़ें और tests में fakes। FastAPI का `Depends` और `dependency_overrides` यह सुविधा पहले से देते हैं।

---

## ➡️ Next Topic
**431. MVC Pattern** — separate data (Model), presentation (View) and request handling (Controller).
