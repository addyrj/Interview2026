---

# 096. Interfaces in Python
# हिंदी में: Python में Interfaces (Protocol और ABC)

---

## 🔵 Simple Definition (English)
An interface is a list of methods a class promises to provide, without any implementation. Python has no `interface` keyword. You build interfaces with `abc.ABC` (explicit: classes must inherit) or `typing.Protocol` (implicit: any class with the right methods qualifies).

## 🔵 सरल परिभाषा (Hindi)
Interface उन methods की सूची है जिन्हें class देने का वादा करती है, बिना implementation के। Python में `interface` keyword नहीं है। Interface आप `abc.ABC` (explicit: class को inherit करना पड़ता है) या `typing.Protocol` (implicit: सही methods वाली कोई भी class चलती है) से बनाते हैं।

---

## 🔴 Problem it Solves
Big codebases need loose coupling: your checkout code should depend on "something that can send a message", not on `TwilioClient`. Without an interface, tests need real Twilio, and swapping providers means editing everywhere. Interfaces let you write code against a small contract and plug in any implementation, including fakes for tests. `Protocol` goes further: third-party classes you cannot edit can match your interface without inheriting anything.

## 🔴 यह क्यों बना? (Hindi)
बड़े codebase में loose coupling चाहिए: checkout code को "message भेजने वाली कोई चीज़" पर निर्भर होना चाहिए, `TwilioClient` पर नहीं। Interface के बिना tests में असली Twilio चाहिए और provider बदलने पर हर जगह edit करना पड़ता है। Interface से आप छोटे contract के against code लिखते हैं और कोई भी implementation (tests के लिए fake भी) लगा सकते हैं। `Protocol` और आगे जाता है: जिन third-party classes को आप edit नहीं कर सकते वे भी बिना inherit किए आपके interface से match कर सकती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the contract: class Notifier(Protocol): def send(self, to: str, msg: str) -> bool: ...
Step 2 → Write functions that accept the contract:  def alert(n: Notifier) -> None
Step 3 → Any class with a matching send() method fits - no inheritance needed
Step 4 → A type checker (mypy / pyright) verifies the match BEFORE you run the code
Step 5 → At runtime Python does nothing special (duck typing) unless @runtime_checkable
Step 6 → With @runtime_checkable, isinstance() checks only that the method NAMES exist
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Contract बनाओ: class Notifier(Protocol): def send(self, to: str, msg: str) -> bool: ...
Step 2 → Contract लेने वाले functions लिखो:  def alert(n: Notifier) -> None
Step 3 → मिलते-जुलते send() वाली कोई भी class चलेगी - inheritance नहीं चाहिए
Step 4 → Type checker (mypy / pyright) code चलाने से पहले match verify करता है
Step 5 → Runtime पर Python कुछ खास नहीं करता (duck typing), जब तक @runtime_checkable न हो
Step 6 → @runtime_checkable के साथ isinstance() सिर्फ method के NAMES की मौजूदगी देखता है
```

---

## 🟡 Real World Example
A Swiggy-like order service needs to notify customers. Define a `Notifier` interface with `send()`. Production uses `SmsNotifier` and `WhatsAppNotifier`; unit tests use `FakeNotifier` that stores messages in a list. File-like objects are the classic Python example: anything with `read()` works with `json.load`, whether it is a file, `StringIO` or a network stream.

## 🟡 Real Example Hindi mein
Swiggy जैसी order service को customers को notify करना है। `send()` वाला `Notifier` interface बनाओ। Production में `SmsNotifier` और `WhatsAppNotifier`, unit tests में `FakeNotifier` जो messages को list में रखता है। File-like objects Python का classic उदाहरण हैं: `read()` वाली कोई भी चीज़ `json.load` के साथ चलती है, चाहे file हो, `StringIO` हो या network stream।

---

## 💻 Code Example — Basic
```python
# Basic: the same interface written two ways
from abc import ABC, abstractmethod             # explicit interface tools
from typing import Protocol                     # implicit interface tool


class SenderABC(ABC):                           # way 1: nominal (must inherit)
    @abstractmethod
    def send(self, msg: str) -> str: ...        # contract


class SenderProto(Protocol):                    # way 2: structural (no inheritance)
    def send(self, msg: str) -> str: ...        # contract


class Sms(SenderABC):                           # inherits the ABC explicitly
    def send(self, msg: str) -> str:            # implements it
        return f"SMS:{msg}"


class Email:                                    # does NOT inherit anything
    def send(self, msg: str) -> str:            # but has the same method
        return f"EMAIL:{msg}"


def notify(s: SenderProto, msg: str) -> str:    # accepts anything shaped like the protocol
    return s.send(msg)                          # call the contract method


print(notify(Sms(), "hi"))                      # works (Sms also matches structurally)
print(notify(Email(), "hi"))                    # works: Email matches by shape
print(isinstance(Sms(), SenderABC))             # True: real inheritance
print(isinstance(Email(), SenderABC))           # False: ABC needs inheritance

# Output:
# SMS:hi
# EMAIL:hi
# True
# False
```

## 💻 Code Example — Advanced
```python
# Production style: Protocol with runtime check, fake for tests, dependency injection
from dataclasses import dataclass, field        # simple data holders
from typing import Protocol, runtime_checkable  # protocol tools


@runtime_checkable                              # allow isinstance() checks (names only!)
class Notifier(Protocol):
    def send(self, to: str, msg: str) -> bool: ...    # the whole interface


@dataclass
class SmsNotifier:                              # "real" implementation (pretend)
    sender_id: str = "SWIGGY"                   # SMS header

    def send(self, to: str, msg: str) -> bool:
        if not to.startswith("+91"):            # simple validation
            return False                        # reject non-Indian numbers
        print(f"[{self.sender_id}] -> {to}: {msg}")     # pretend to call a provider
        return True


@dataclass
class FakeNotifier:                             # test double
    sent: list[tuple[str, str]] = field(default_factory=list)   # remembers messages

    def send(self, to: str, msg: str) -> bool:
        self.sent.append((to, msg))             # store instead of sending
        return True


class OrderService:                             # depends on the interface only
    def __init__(self, notifier: Notifier) -> None:
        if not isinstance(notifier, Notifier):  # runtime guard (checks method names)
            raise TypeError("notifier must provide send(to, msg)")
        self._notifier: Notifier = notifier     # keep it

    def place_order(self, phone: str, item: str) -> bool:
        return self._notifier.send(phone, f"Order placed: {item}")   # use the contract


fake: FakeNotifier = FakeNotifier()             # test setup
svc: OrderService = OrderService(fake)          # inject the fake
print(svc.place_order("+919999900000", "Biryani"))    # True
print(fake.sent)                                # we can assert on this in tests

print(OrderService(SmsNotifier()).place_order("+919999900000", "Pizza"))   # real-style path
print(OrderService(SmsNotifier()).place_order("12345", "Pizza"))           # validation says False

try:                                            # something that is not a Notifier
    OrderService(object())                      # no send() method
except TypeError as e:                          # guard raises
    print("Error:", e)                          # clear message

# Output:
# True
# [('+919999900000', 'Order placed: Biryani')]
# [SWIGGY] -> +919999900000: Order placed: Pizza
# True
# False
# Error: notifier must provide send(to, msg)
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| `interface` keyword | None | None (TypeScript has it) |
| Explicit interface | `ABC` + `@abstractmethod` | n/a (TS: `implements`) |
| Structural interface | `typing.Protocol` | TypeScript interfaces are structural too |
| Runtime check | `isinstance` (ABC) / `@runtime_checkable` | `typeof obj.send === "function"` |
| Enforcement time | Type checker or instantiation | Type checker only (TS) |

```python
# Python way
from typing import Protocol

class Greeter(Protocol):
    def greet(self) -> str: ...      # interface

class En:
    def greet(self) -> str:          # no inheritance, just the shape
        return "Hello"

def run(g: Greeter) -> str:
    return g.greet()

print(run(En()))                     # Hello
```
```javascript
// JavaScript / TypeScript way
// TypeScript: interface Greeter { greet(): string }
class En { greet() { return "Hello"; } }       // matches by shape
function run(g) { return g.greet(); }          // plain JS: pure duck typing
console.log(run(new En()));                    // Hello
```

Key difference: Python's `Protocol` is the same idea as a TypeScript interface (structural typing). If you know TS interfaces, you already understand `Protocol`. The checking is done by mypy/pyright, not by the interpreter.

---

## 🟠 FastAPI Connection
FastAPI's `Depends` plus a `Protocol` is the cleanest way to inject services. Routes depend on the interface, and tests override the dependency with a fake using `app.dependency_overrides`.

```python
# FastAPI example — Protocol-typed dependency with override in tests
from typing import Protocol                     # protocol tool
from fastapi import FastAPI, Depends            # app and DI
from fastapi.testclient import TestClient       # test client


class Mailer(Protocol):
    def send(self, to: str) -> str: ...         # interface


class RealMailer:                               # production class
    def send(self, to: str) -> str:
        return f"real mail to {to}"             # pretend SMTP


class FakeMailer:                               # test class
    def send(self, to: str) -> str:
        return f"fake mail to {to}"             # no network


def get_mailer() -> Mailer:                     # provider typed with the interface
    return RealMailer()                         # default


app: FastAPI = FastAPI()                        # create app


@app.post("/welcome")                           # POST /welcome?email=a@b.com
def welcome(email: str, mailer: Mailer = Depends(get_mailer)) -> dict[str, str]:
    return {"result": mailer.send(email)}       # depends on the contract only


client: TestClient = TestClient(app)            # test client
print(client.post("/welcome", params={"email": "a@b.com"}).json())   # real path
app.dependency_overrides[get_mailer] = lambda: FakeMailer()          # swap for tests
print(client.post("/welcome", params={"email": "a@b.com"}).json())   # fake path

# Output:
# {'result': 'real mail to a@b.com'}
# {'result': 'fake mail to a@b.com'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `isinstance` with a Protocol that is not `@runtime_checkable`
✅ Correct: add `@runtime_checkable` (and remember it checks names only)

```python
from typing import Protocol, runtime_checkable

class P(Protocol):
    def f(self) -> int: ...

class Impl:
    def f(self) -> int:
        return 1

try:
    isinstance(Impl(), P)               # Wrong: not runtime_checkable
except TypeError as e:
    print("Error:", e)

@runtime_checkable
class Q(Protocol):
    def f(self) -> int: ...

print(isinstance(Impl(), Q))            # Right: True
```

❌ Mistake 2: Believing `runtime_checkable` verifies signatures
✅ Correct: it only checks that attributes exist; use mypy for signatures

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Sender(Protocol):
    def send(self, a: int, b: int) -> None: ...

class Bad:
    def send(self) -> str:              # totally different signature
        return "x"

print(isinstance(Bad(), Sender))        # True  <- misleading!
```

❌ Mistake 3: Over-engineering an interface for one tiny function
✅ Correct: accept a `Callable` when you only need one function

```python
from collections.abc import Callable

# Wrong: whole class hierarchy just to send one message
# Right:
def notify(send: Callable[[str], str], msg: str) -> str:
    return send(msg)                    # any function works

print(notify(str.upper, "hi"))          # HI
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from typing import Protocol, runtime_checkable

@runtime_checkable
class HasLen(Protocol):
    def __len__(self) -> int: ...

print(isinstance([1, 2], HasLen))
print(isinstance("abc", HasLen))
print(isinstance(5, HasLen))
print(isinstance(range(3), HasLen))
```
Answer: `True`, `True`, `False`, `True`. `list`, `str` and `range` have `__len__`, `int` does not. None of them inherit from `HasLen`; the check is purely structural. This is how `collections.abc.Sized` works too.

---

## ⚫ Interview Questions + Answers

Q1: Does Python have interfaces?
A1: Not as a keyword. Python uses ABCs (explicit contracts), `Protocol` (structural contracts) and plain duck typing. All three serve the interface role.

Q2: ABC vs Protocol: when to pick which?
A2: Pick ABC when you control all implementations and want shared code plus runtime enforcement on instantiation. Pick Protocol when you want decoupling, need third-party classes to qualify, or want a light contract checked by mypy.

Q3: Who enforces a Protocol?
A3: Static type checkers (mypy, pyright). At runtime nothing is enforced unless you use `@runtime_checkable` with `isinstance`, and then only method names are checked.

Q4: What is structural vs nominal typing?
A4: Nominal: compatibility depends on declared inheritance (`class A(B)`). Structural: compatibility depends on having the right members. ABC is nominal, Protocol is structural (like TypeScript).

Q5: How do interfaces help testing?
A5: Code depends on a small contract, so tests pass a fake that records calls. No network, no real database, fast and deterministic tests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Swapping implementations (SMS vs WhatsApp, SQL vs in-memory repo, OpenAI vs Anthropic)
- Writing testable services with dependency injection
- Typing third-party objects you cannot modify

❌ Avoid when:
- Only one implementation exists and none is planned
- A plain `Callable` type is enough
- You need runtime signature validation (Protocol will not do it)

---

## 📊 Visual Diagram
```
            Notifier (Protocol)  send(to, msg) -> bool
                    ^
     matches by shape, no inheritance arrows
     +--------------+--------------+----------------+
 SmsNotifier   WhatsAppNotifier  FakeNotifier   (any 3rd-party class
 send()        send()            send()          with send())

 OrderService(notifier: Notifier)  ---- uses only send() ----> any of the above
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Interface | Promised set of methods | वादा किए गए methods की सूची |
| Protocol | Structural interface (`typing.Protocol`) | Shape पर आधारित interface |
| Nominal typing | Match by inheritance | Inheritance से match |
| Structural typing | Match by members | Members से match |
| runtime_checkable | Lets isinstance() work with a Protocol | Protocol पर isinstance चलाने देता है |
| Test double / fake | Fake implementation for tests | Tests के लिए नकली implementation |

---

## ⚡ 3-Line Summary
English: Python has no `interface` keyword; use `ABC` for explicit contracts and `Protocol` for structural ones. Code against the contract so you can swap implementations and use fakes in tests. `Protocol` is checked by mypy, not by the interpreter.
Hindi: Python में `interface` keyword नहीं है; explicit contract के लिए `ABC` और structural के लिए `Protocol` इस्तेमाल करें। Contract के against code लिखें ताकि implementations बदल सकें और tests में fakes लगा सकें। `Protocol` को mypy check करता है, interpreter नहीं।

---

## ➡️ Next Topic
**097. Mixins** — small reusable classes that add one behavior (logging, timestamps) to many classes through multiple inheritance.
