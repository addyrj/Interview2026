---

# 284. unittest.mock
# हिंदी में: unittest.mock (नकली objects बनाना)

---

## 🔵 Simple Definition (English)
`unittest.mock` is a standard-library module that gives you fake objects (`Mock`, `MagicMock`, `AsyncMock`) which record how they were used. You tell them what to return, run your code, then check which calls were made. It works with both `unittest` and `pytest`.

## 🔵 सरल परिभाषा (Hindi)
`unittest.mock` standard library का module है जो नकली objects (`Mock`, `MagicMock`, `AsyncMock`) देता है, जो याद रखते हैं कि उन्हें कैसे इस्तेमाल किया गया। आप बताते हैं कि क्या return करना है, अपना code चलाते हैं और फिर जांचते हैं कि कौन से calls हुए। यह `unittest` और `pytest` दोनों के साथ चलता है।

---

## 🔴 Problem it Solves
Real code talks to slow, costly, or dangerous things: payment gateways, email servers, databases, the clock. A test that really calls Razorpay is slow, can charge money, and fails when the network is down. Mocks replace those dependencies with controllable fakes so tests are fast, deterministic, and can simulate failures (timeouts, 500 errors) that are hard to create for real.

## 🔴 यह क्यों बना? (Hindi)
असली code धीमी, महंगी या खतरनाक चीज़ों से बात करता है: payment gateway, email server, database, घड़ी। जो test सच में Razorpay को call करे वह धीमा होता है, पैसे कट सकते हैं, और network बंद हो तो fail होता है। Mocks उन dependencies को नियंत्रित नकली objects से बदल देते हैं ताकि tests तेज़ और predictable हों और timeouts, 500 errors जैसी failures भी simulate हो सकें।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a Mock: any attribute or call you access is auto-created
Step 2 → Configure: m.method.return_value = ...   or   side_effect = ...
Step 3 → Run the code under test with the mock in place of the real object
Step 4 → The mock records calls: call_count, call_args, call_args_list, mock_calls
Step 5 → Assert: assert_called_once_with(...), assert_not_called(), assert_any_call(...)
Step 6 → Use spec / create_autospec so the mock rejects wrong attributes and wrong signatures

Mock = flexible fake | MagicMock = Mock + magic methods (__len__, __getitem__ ...) | AsyncMock = awaitable
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Mock बनाओ: जो भी attribute या call करो वह अपने आप बन जाता है
Step 2 → Configure करो: m.method.return_value = ...   या   side_effect = ...
Step 3 → असली object की जगह mock लगाकर test किया जाने वाला code चलाओ
Step 4 → Mock calls याद रखता है: call_count, call_args, call_args_list, mock_calls
Step 5 → Assert करो: assert_called_once_with(...), assert_not_called(), assert_any_call(...)
Step 6 → spec / create_autospec इस्तेमाल करो ताकि गलत attribute या signature पर mock error दे

Mock = लचीला नकली | MagicMock = Mock + magic methods (__len__, __getitem__ ...) | AsyncMock = await हो सकने वाला
```

---

## 🟡 Real World Example
An order service in a Zomato-style app calls a payment gateway and then an SMS provider. In tests, the gateway is replaced by `create_autospec(Gateway, instance=True)` returning `False` to test the "payment declined" flow, and the SMS client is a `Mock` so the test can assert that no SMS was sent. Nothing touches the network, and the whole suite finishes in milliseconds.

## 🟡 Real Example Hindi mein
Zomato जैसे app की order service payment gateway और फिर SMS provider को call करती है। Tests में gateway की जगह `create_autospec(Gateway, instance=True)` है जो "payment declined" flow जांचने के लिए `False` देता है, और SMS client एक `Mock` है ताकि test assert कर सके कि कोई SMS नहीं भेजा गया। Network कहीं नहीं छुआ जाता और पूरी suite मिलीसेकंड में खत्म होती है।

---

## 💻 Code Example — Basic
```python
# Basic Mock / MagicMock / autospec (verified on Python 3.13)
from unittest.mock import Mock, MagicMock, call, create_autospec   # mock tools

m = Mock()                                        # object that accepts any attribute/call
m.send.return_value = "sent"                      # fix the return value of m.send(...)
print(m.send("a@b.com", subject="Hi"))            # call it -> "sent"
m.send.assert_called_once_with("a@b.com", subject="Hi")   # verify the exact call
print(m.send.call_count, m.send.call_args)        # inspect usage
print(m.anything.deep.chain())                    # auto-created children return a new Mock

mm = MagicMock()                                  # MagicMock also supports magic methods
mm.__len__.return_value = 3                       # configure len(mm)
print(len(mm), bool(mm))                          # 3 True
mm.__getitem__.return_value = "x"                 # configure mm[...]
print(mm[0])                                      # x


class Gateway:                                    # real class to imitate
    def charge(self, amount: int) -> bool:
        return True


g = create_autospec(Gateway, instance=True)       # mock with the SAME signatures as the real class
g.charge.return_value = False                     # pretend the charge is declined
print(g.charge(100))                              # False
try:
    g.charge()                                    # missing argument
except TypeError as e:
    print("TypeError:", e)                        # autospec checks the signature
try:
    g.refund(1)                                   # method does not exist on the real class
except AttributeError as e:
    print("AttributeError:", e)

m2 = Mock()
m2.a(1); m2.a(2)                                  # two calls
print(m2.a.mock_calls == [call(1), call(2)])      # True: full call history
m2.reset_mock()                                   # clear history
print(m2.a.call_count)                            # 0
try:
    Mock().assert_called()                        # never called
except AssertionError as e:
    print("AssertionError:", e)

# Output (the id number in the Mock repr differs on every run):
# sent
# 1 call('a@b.com', subject='Hi')
# <Mock name='mock.anything.deep.chain()' id='4357894704'>
# 3 True
# x
# False
# TypeError: missing a required argument: 'amount'
# AttributeError: Mock object has no attribute 'refund'
# True
# 0
# AssertionError: Expected 'mock' to have been called.
```

## 💻 Code Example — Advanced
```python
# Production style: test a service with an injected gateway and notifier
from dataclasses import dataclass                 # simple data model
from typing import Protocol                       # interface description
from unittest.mock import Mock, create_autospec, call   # mock tools
import pytest                                     # test framework


class Gateway(Protocol):                          # what the service needs
    def charge(self, user_id: int, amount: int) -> bool: ...


class Notifier(Protocol):
    def send(self, user_id: int, text: str) -> None: ...


@dataclass
class OrderService:                               # code under test (dependencies injected)
    gateway: Gateway
    notifier: Notifier

    def place(self, user_id: int, amount: int) -> str:
        if amount <= 0:                           # validate first
            raise ValueError("amount must be positive")
        if not self.gateway.charge(user_id, amount):          # external call
            return "declined"                     # do NOT notify on decline
        self.notifier.send(user_id, f"paid {amount}")         # side effect
        return "paid"


class RealGateway:                                # a concrete class used only for the spec
    def charge(self, user_id: int, amount: int) -> bool:
        raise RuntimeError("real network!")


class RealNotifier:
    def send(self, user_id: int, text: str) -> None:
        raise RuntimeError("real SMS!")


def make_service(ok: bool) -> tuple[OrderService, Mock, Mock]:
    gw = create_autospec(RealGateway, instance=True)          # same signature as real class
    gw.charge.return_value = ok                   # decide the outcome
    nt = create_autospec(RealNotifier, instance=True)
    return OrderService(gw, nt), gw, nt


def test_paid() -> None:
    svc, gw, nt = make_service(True)
    assert svc.place(1, 500) == "paid"
    gw.charge.assert_called_once_with(1, 500)     # exactly one charge, right args
    nt.send.assert_called_once_with(1, "paid 500")


def test_declined_sends_no_sms() -> None:
    svc, gw, nt = make_service(False)
    assert svc.place(1, 500) == "declined"
    nt.send.assert_not_called()                   # important negative check


def test_validation() -> None:
    svc, gw, nt = make_service(True)
    with pytest.raises(ValueError):
        svc.place(1, 0)
    assert gw.mock_calls == []                    # gateway untouched on invalid input


# Run: pytest -q   -> 3 passed (verified)
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python `unittest.mock` | JavaScript (Jest) |
|---------|------------------------|-------------------|
| Fake function | `Mock()` / `MagicMock()` | `jest.fn()` |
| Return value | `m.return_value = 1` | `fn.mockReturnValue(1)` |
| Different per call | `side_effect=[1, 2]` | `mockReturnValueOnce(1).mockReturnValueOnce(2)` |
| Assert call | `assert_called_once_with(a)` | `expect(fn).toHaveBeenCalledWith(a)` |
| Call count | `m.call_count` | `fn.mock.calls.length` |
| Strict fake | `create_autospec(Cls)` | `jest.mocked(...)` / TS types |
| Fake module | `patch("mod.name")` | `jest.mock("module")` |

```python
# Python way
from unittest.mock import Mock

send = Mock(return_value=True)                    # fake function
send("a@b.com")                                   # call it
send.assert_called_once_with("a@b.com")           # verify
```
```javascript
// JavaScript way (Jest)
const send = jest.fn().mockReturnValue(true);     // fake function
send("a@b.com");                                  // call it
expect(send).toHaveBeenCalledWith("a@b.com");     // verify
```

Key difference: a Python `Mock` auto-creates every attribute you touch (very flexible, but a typo like `m.asert_called_once()` used to silently pass; modern Python raises an AttributeError for names starting with `assert`/`assret`). Use `spec` or `create_autospec` to get strict mocks like typed Jest mocks.

---

## 🟠 FastAPI Connection
In FastAPI, dependencies are injected with `Depends`, so mocks plug in through `app.dependency_overrides`. Use `MagicMock(spec=RealClass)` for services (mailer, payment client) and check calls after the request. For code that does not use `Depends`, use `patch` (next topics).

```python
# FastAPI + Mock via dependency_overrides (verified: 2 tests OK)
from unittest.mock import MagicMock                       # fake object
from fastapi import Depends, FastAPI                      # FastAPI
from fastapi.testclient import TestClient                 # client

app: FastAPI = FastAPI()                                  # app


class Mailer:                                             # real dependency
    def send(self, to: str) -> bool:
        raise RuntimeError("real SMTP!")


def get_mailer() -> Mailer:                               # provider
    return Mailer()


@app.post("/signup")
def signup(email: str, mailer: Mailer = Depends(get_mailer)) -> dict[str, bool]:
    return {"mailed": mailer.send(email)}


def test_signup() -> None:
    fake = MagicMock(spec=Mailer)                         # only attributes of Mailer allowed
    fake.send.return_value = True                         # fake success
    app.dependency_overrides[get_mailer] = lambda: fake   # swap dependency
    try:
        r = TestClient(app).post("/signup", params={"email": "a@b.c"})
    finally:
        app.dependency_overrides.clear()                  # always reset
    assert r.json() == {"mailed": True}
    fake.send.assert_called_once_with("a@b.c")            # was the mailer called correctly?
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Plain `Mock()` that accepts anything, so typos and wrong signatures pass
✅ Correct: use `spec=` or `create_autospec`

```python
from unittest.mock import Mock, create_autospec
class Gateway:
    def charge(self, amount: int) -> bool: return True

# Wrong — gateway.chrge(1) silently works, test is meaningless
Mock().chrge(1)
# Right — AttributeError: Mock object has no attribute 'chrge'
create_autospec(Gateway, instance=True).charge(1)
```

❌ Mistake 2: Asserting what the mock returns instead of what the code did
✅ Correct: assert the result of the code under test and the calls made to dependencies

```python
# Wrong — only tests the mock itself
m = Mock(return_value=5); assert m() == 5
# Right — test real logic, verify the collaboration
svc.place(1, 500); gateway.charge.assert_called_once_with(1, 500)
```

❌ Mistake 3: Over-mocking (mocking your own pure functions and internals)
✅ Correct: mock only boundaries (network, DB, clock, filesystem); test logic for real

❌ Mistake 4: Forgetting `reset_mock()` or sharing a module-level mock between tests
✅ Correct: create mocks per test (fixtures) so call history does not leak

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from unittest.mock import Mock

m = Mock()
print(bool(m), m.x is m.x, m() is m())
m.return_value = 7
print(m(), m.x())
```
Answer: Line 1 is `True True True`. A `Mock` is truthy (a `MagicMock` too unless `__bool__` is set); attribute access returns the SAME child mock every time, and calling returns the same `return_value` object each call. Line 2 is `7` followed by a new Mock: `<Mock name='mock.x()' id='...'>`. Setting `m.return_value = 7` changes only `m()`; `m.x()` is a different child mock with its own `return_value`. (id varies per run.)

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `Mock` and `MagicMock`?
A1: `MagicMock` is a `Mock` with default implementations of magic (dunder) methods like `__len__`, `__iter__`, `__getitem__`, `__enter__`. Use it when the code uses `len(x)`, indexing, iteration, or `with x:`. `Mock` is simpler and raises on unsupported magic methods.

Q2: What does `spec` / `autospec` give you?
A2: `spec=Cls` allows only attributes that exist on `Cls`. `create_autospec(Cls)` also copies method signatures, so wrong argument counts raise `TypeError`. This stops tests from passing against an API that does not exist.

Q3: How do you check a call was made with certain arguments?
A3: `assert_called_with` (last call), `assert_called_once_with` (exactly one call), `assert_any_call`, `assert_has_calls([call(1), call(2)])` for sequences, `assert_not_called`. Inspect with `call_args`, `call_args_list`, `mock_calls`.

Q4: How do you mock something async?
A4: Use `AsyncMock` (Python 3.8+). Awaiting it returns `return_value`, and `assert_awaited_once_with` checks awaits. `patch` auto-uses `AsyncMock` when the target is an `async def`.

Q5: Is mocking always good?
A5: No. Mocks verify implementation details; too many make tests brittle (they break on refactor) and can hide real integration bugs. Mock external boundaries, use real objects or fakes (in-memory DB) for the rest, and add a few integration tests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dependency is slow, costly, or non-deterministic (network, time, randomness)
- You must simulate failures (timeouts, 500s)
- You need to verify an outgoing call (email sent, event published)

❌ Avoid when:
- A real in-memory implementation or fake is simple (SQLite, dict-based repo)
- You are mocking pure logic you own
- The mock mirrors the implementation line by line (brittle test)

---

## 📊 Visual Diagram
```
 Real:   OrderService ──► Gateway ──► network ──► bank        (slow, risky)

 Test:   OrderService ──► Mock(Gateway)                       (instant)
                              |  records: charge(1, 500) x1
                              |  returns: True (configured)
                              v
        asserts:  result == "paid"
                  gateway.charge.assert_called_once_with(1, 500)
                  notifier.send.assert_called_once_with(1, "paid 500")
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Mock | Fake object that records calls | कॉल याद रखने वाला नकली object |
| MagicMock | Mock with magic methods | Magic methods वाला Mock |
| return_value | What the mock returns | Mock जो लौटाए |
| spec / autospec | Restrict mock to the real API | Mock को असली API तक सीमित करना |
| call_args | Arguments of the last call | आखिरी call के arguments |
| Test double | Any stand-in object | Test में असली की जगह वस्तु |

---

## ⚡ 3-Line Summary
English: `unittest.mock` gives fake objects that return what you set and remember every call. Use `MagicMock` for magic methods, `AsyncMock` for async code, and `create_autospec` to keep fakes faithful to the real API. Mock boundaries, not your own logic.
Hindi: `unittest.mock` ऐसे नकली objects देता है जो आपका तय किया return देते हैं और हर call याद रखते हैं। Magic methods के लिए `MagicMock`, async के लिए `AsyncMock` और असली API से मेल के लिए `create_autospec` लें। सिर्फ boundaries को mock करें, अपने logic को नहीं।

---

## ➡️ Next Topic
**285. patch Decorator** — temporarily replace a real object (function, class, attribute) inside your code with a mock, and the "patch where it is used" rule.
