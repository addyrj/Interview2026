---

# 285. patch Decorator
# हिंदी में: patch Decorator (कुछ समय के लिए असली चीज़ बदलना)

---

## 🔵 Simple Definition (English)
`unittest.mock.patch` temporarily replaces an object (a function, class, or attribute) with a `MagicMock` while a test runs, and puts the original back afterwards. You can use it as a decorator, as a `with` block, or manually with `start()` / `stop()`.

## 🔵 सरल परिभाषा (Hindi)
`unittest.mock.patch` test चलने के दौरान किसी object (function, class या attribute) को कुछ समय के लिए `MagicMock` से बदलता है और बाद में असली चीज़ वापस रख देता है। इसे decorator, `with` block या `start()` / `stop()` से इस्तेमाल कर सकते हैं।

---

## 🔴 Problem it Solves
Dependency injection (passing the gateway into the class) is the cleanest design, but a lot of real code imports and calls things directly: `httpx.post(...)`, `time.sleep(...)`, `datetime.now()`, `os.environ`. You cannot pass a fake into `httpx.post`. `patch` swaps the name inside the module under test and restores it automatically, even when the test fails, so you never leave a fake behind for the next test.

## 🔴 यह क्यों बना? (Hindi)
Dependency injection (gateway को class में पास करना) सबसे साफ design है, लेकिन बहुत सा असली code सीधे import करके call करता है: `httpx.post(...)`, `time.sleep(...)`, `datetime.now()`, `os.environ`। `httpx.post` में आप fake पास नहीं कर सकते। `patch` test किए जा रहे module के अंदर वह नाम बदल देता है और test fail होने पर भी अपने आप restore करता है, इसलिए अगले test के लिए कोई fake बचा नहीं रहता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → patch("package.module.name") finds the module and the attribute by string
Step 2 → It saves the original and sets the attribute to a MagicMock (or your replacement)
Step 3 → Decorator form: the mock is passed as an EXTRA argument to the test function
Step 4 → Test runs; code looking up that name now gets the mock
Step 5 → On exit (even on exception) the original is restored
Step 6 → Rule: patch the name WHERE IT IS LOOKED UP (the module that uses it), not where it is defined

Stacked decorators: the BOTTOM decorator provides the FIRST argument.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → patch("package.module.name") string से module और attribute ढूंढता है
Step 2 → असली चीज़ सुरक्षित रखकर attribute को MagicMock (या आपके replacement) पर set करता है
Step 3 → Decorator रूप में mock test function को EXTRA argument की तरह मिलता है
Step 4 → Test चलता है; उस नाम को देखने वाला code अब mock पाता है
Step 5 → बाहर निकलते समय (exception में भी) असली चीज़ वापस आ जाती है
Step 6 → नियम: उस जगह patch करो जहां नाम इस्तेमाल के समय देखा जाता है (इस्तेमाल करने वाला module), जहां define हुआ वहां नहीं

Stacked decorators में: सबसे नीचे वाला decorator पहला argument देता है।
```

---

## 🟡 Real World Example
A `charge()` function in a Razorpay-integrated backend calls `httpx.post` to the gateway. The test patches `payments.httpx.post` to return a fake 200 response (happy path), a 503 (gateway down), and raises `ConnectError` (network down) — three scenarios impossible to trigger reliably with the real service. Another common use is patching `time.sleep` in retry code so a test with three retries finishes instantly.

## 🟡 Real Example Hindi mein
Razorpay से जुड़े backend का `charge()` function gateway को `httpx.post` से call करता है। Test `payments.httpx.post` को patch करके fake 200 response (सही रास्ता), 503 (gateway बंद) और `ConnectError` (network बंद) देता है — तीन स्थितियां जिन्हें असली service से भरोसे से बनाना असंभव है। एक और आम इस्तेमाल है retry code में `time.sleep` patch करना ताकि तीन retries वाला test तुरंत खत्म हो।

---

## 💻 Code Example — Basic
```python
# Code under test — file: payments.py
import httpx                                      # HTTP client


class PaymentError(Exception):                    # domain error
    pass


def charge(user_id: int, amount: int) -> dict[str, str]:
    """Call the external gateway and return its JSON."""
    resp = httpx.post("https://gateway.example/charge", json={"user": user_id, "amount": amount}, timeout=5)
    if resp.status_code != 200:                   # gateway error
        raise PaymentError(f"gateway said {resp.status_code}")
    return resp.json()


# Test — file: test_payments.py  (verified: 7 passed on Python 3.13, pytest 9)
from unittest.mock import patch, MagicMock, Mock  # patching tools
import pytest                                     # test framework
import payments                                   # module under test


@patch("payments.httpx.post")                     # patch where it is LOOKED UP
def test_ok(mock_post: MagicMock) -> None:        # patch injects the mock as an argument
    mock_post.return_value = Mock(status_code=200, json=lambda: {"status": "ok"})   # fake response
    assert payments.charge(1, 500) == {"status": "ok"}     # code under test uses the fake
    mock_post.assert_called_once_with(            # verify how the gateway was called
        "https://gateway.example/charge", json={"user": 1, "amount": 500}, timeout=5
    )


def test_gateway_down() -> None:
    with patch("payments.httpx.post") as p:       # context-manager form
        p.return_value.status_code = 503          # fake status
        with pytest.raises(payments.PaymentError, match="503"):
            payments.charge(1, 10)                # error path


def test_network_error() -> None:
    with patch("payments.httpx.post", side_effect=payments.httpx.ConnectError("down")):
        with pytest.raises(payments.httpx.ConnectError):   # network failure simulated
            payments.charge(1, 10)

# After each test the real httpx.post is restored automatically.
```

## 💻 Code Example — Advanced
```python
# Advanced: stacking, patch.object, patch.dict, class decorator, the "where to patch" gotcha
import os                                         # environment
import sys, types                                 # to build two tiny modules for the demo
import unittest                                   # unittest style
from unittest.mock import patch, MagicMock, Mock  # patching tools
import payments                                   # from the Basic example


@patch("payments.httpx.post")                     # stacked: bottom decorator -> FIRST argument
@patch("payments.PaymentError")
def test_order(mock_err: MagicMock, mock_post: MagicMock) -> None:
    assert mock_err is payments.PaymentError      # first arg = nearest (bottom) decorator
    assert mock_post is payments.httpx.post       # second arg = decorator above it


def test_patch_object_and_dict() -> None:
    with patch.dict(os.environ, {"MODE": "test"}):                  # temporary dict change
        assert os.environ["MODE"] == "test"
    assert "MODE" not in os.environ               # restored afterwards
    with patch.object(payments, "charge", return_value={"x": 1}) as c:   # patch an attribute of an object
        assert payments.charge(1, 1) == {"x": 1}
        c.assert_called_once()


class TestWithClass(unittest.TestCase):
    @patch("payments.httpx.post")                 # works on unittest methods too
    def test_x(self, mock_post: MagicMock) -> None:        # mock arrives after self
        mock_post.return_value = Mock(status_code=200, json=lambda: {"a": 1})
        self.assertEqual(payments.charge(2, 1), {"a": 1})


# ---- The #1 gotcha: patch where the name is USED (verified output below) ----
from unittest.mock import patch as p2             # alias for the demo
util = types.ModuleType("util")                   # module that DEFINES now()
exec("def now():\n    return 'real'", util.__dict__)
sys.modules["util"] = util
consumer = types.ModuleType("consumer")           # module that does "from util import now"
exec("from util import now\ndef show():\n    return now()", consumer.__dict__)
sys.modules["consumer"] = consumer

with p2("util.now", return_value="fake"):         # WRONG target: consumer has its own reference
    print(consumer.show())                        # real
with p2("consumer.now", return_value="fake"):     # RIGHT target: the name inside consumer
    print(consumer.show())                        # fake

# Output of the demo: "real" then "fake".  The 7 pytest tests of payments + class pass in 0.03s.
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python `patch` | JavaScript (Jest) |
|---------|----------------|-------------------|
| Replace a module | `patch("pkg.mod.name")` | `jest.mock("./mod")` |
| Replace one method | `patch.object(obj, "m")` | `jest.spyOn(obj, "m").mockReturnValue(...)` |
| Auto-restore | when the decorator/with ends | `jest.restoreAllMocks()` (or config) |
| Env vars | `patch.dict(os.environ, {...})` | assign to `process.env` + restore manually |
| Where to patch | name in the USER's namespace | module registry (hoisted mock) |
| Fake timers | `patch("time.sleep")` | `jest.useFakeTimers()` |

```python
# Python way
from unittest.mock import patch

with patch("time.sleep") as fake_sleep:           # replace sleep
    import time
    time.sleep(10)                                # returns instantly
    fake_sleep.assert_called_once_with(10)
```
```javascript
// JavaScript way (Jest)
jest.useFakeTimers();                             // fake clock
const spy = jest.spyOn(global, "setTimeout");     // spy on a global
doWork();                                         // code that sets timers
expect(spy).toHaveBeenCalledWith(expect.any(Function), 10000);
```

Key difference: Jest's `jest.mock("./mod")` is hoisted and replaces the module for all importers. Python's `patch` changes one attribute in one namespace, so you must name the exact place where the code looks the name up (the "patch where it is used" rule).

---

## 🟠 FastAPI Connection
Prefer `Depends` and `dependency_overrides` for things FastAPI injects. Use `patch` for everything else a route calls directly: a third-party SDK, `datetime`, `uuid4`, a background task function. Patch the name in the module where the route lives.

```python
# FastAPI + patch: route calls an SDK directly (no Depends)
from unittest.mock import patch                           # patch
from fastapi import FastAPI                               # FastAPI
from fastapi.testclient import TestClient                 # client
import httpx                                              # HTTP lib

app: FastAPI = FastAPI()                                  # app


@app.get("/rate")
def rate() -> dict[str, float]:
    r = httpx.get("https://fx.example/usd-inr", timeout=3)   # direct call inside the route
    return {"usd_inr": r.json()["rate"]}


def test_rate() -> None:
    fake = type("R", (), {"json": lambda self: {"rate": 83.5}})()      # tiny fake response
    with patch("httpx.get", return_value=fake) as g:      # patch the attribute on the httpx module
        res = TestClient(app).get("/rate")                # route uses httpx.get(...) -> sees the fake
    assert res.json() == {"usd_inr": 83.5}                # the response uses our value
    g.assert_called_once()                                # the SDK was called once
```
(This one works with `patch("httpx.get")` because the route calls `httpx.get` through the module attribute. If the route had `from httpx import get`, you would patch `"yourmodule.get"` instead.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Patching where the object is defined, not where it is used
✅ Correct: patch the name inside the module under test (see the verified demo: "real" vs "fake")

```python
# consumer.py:  from util import now
# Wrong
with patch("util.now", return_value="fake"): ...      # consumer.show() still returns 'real'
# Right
with patch("consumer.now", return_value="fake"): ...  # consumer.show() returns 'fake'
```

❌ Mistake 2: Wrong argument order with stacked decorators
✅ Correct: the bottom decorator = first mock argument

```python
@patch("a.first")      # -> second argument
@patch("a.second")     # -> FIRST argument (closest to the function)
def test(mock_second, mock_first): ...
```

❌ Mistake 3: Forgetting that the decorator adds an argument (with pytest fixtures mixed in)
✅ Correct: patch arguments come FIRST, fixtures after (or use `with patch(...)` / `mocker.patch` to avoid the confusion)

❌ Mistake 4: Starting a patch manually and never stopping it
✅ Correct: `p = patch(...); p.start(); self.addCleanup(p.stop)` or just use the `with` / decorator form

---

## 🧠 Tricky Interview Question

```python
# util.py:      def now(): return "real"
# consumer.py:  import util
#               def show(): return util.now()
from unittest.mock import patch
import consumer

with patch("util.now", return_value="fake"):
    print(consumer.show())
```
Answer: `fake`. Here `consumer` does `import util` and calls `util.now()`, so it looks the name up on the `util` module object at call time — patching `util.now` works. The same patch fails with `from util import now` (that copies the reference into `consumer` at import time; verified: it prints `real`). The rule "patch where it is looked up" gives different targets for the two import styles.

---

## ⚫ Interview Questions + Answers

Q1: What is the "where to patch" rule?
A1: Patch the name in the namespace where the code under test looks it up. With `from x import y` in module `m`, patch `m.y`. With `import x` and `x.y()`, patch `x.y` (or `m.x.y`, same object). Patching the definition site does not change names that were already copied.

Q2: In what ways can you use `patch`?
A2: As a decorator (mock passed as extra argument), a context manager (`with patch(...) as m`), a class decorator (applies to every `test*` method), or manually with `start()`/`stop()` (pair with `addCleanup`). `patch.object` and `patch.dict` patch an object attribute and a dictionary.

Q3: What does `patch` replace the target with, by default?
A3: A `MagicMock` (or `AsyncMock` if the target is an `async def` function). You can pass `new=` for a custom replacement (then no argument is injected), `return_value=`, `side_effect=`, and `autospec=True` to keep the original signature.

Q4: Why use `autospec=True`?
A4: A default mock accepts any call, so if the real function signature changes, the test still passes. `autospec=True` makes the mock check arguments against the real signature and raises `TypeError` for wrong calls.

Q5: pytest `monkeypatch` or `patch`?
A5: `monkeypatch` (pytest fixture) is good for env vars, attributes, and simple replacements; it does not record calls. `patch`/`mocker.patch` returns a MagicMock that records calls and supports assertions. Use whichever the test needs; `pytest-mock`'s `mocker.patch` is the same as `patch` with automatic cleanup.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Code calls a library or global directly (httpx, requests, time, uuid, datetime)
- Simulating errors in third-party calls
- Making retry/sleep code instant

❌ Avoid when:
- You can inject the dependency (constructor argument, `Depends`): simpler and no string targets
- You are patching many internals of your own code (design smell)
- The patch target string is brittle and breaks on every refactor (prefer a thin wrapper to patch once)

---

## 📊 Visual Diagram
```
consumer.py:   from util import now            util.py:  def now(): ...
                    |                                       ^
        consumer.now ─┐ copied at import                    |
                      v                                     |
 patch("util.now")      -> changes util.now only       (consumer still has the old reference)
 patch("consumer.now")  -> changes consumer.now        (consumer.show() sees the mock)  ✅

 with patch(...):  [ original saved ] -> [ mock active ] -> [ original restored ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| patch | Temporarily replace an object | कुछ समय के लिए object बदलना |
| patch.object | Patch an attribute of a given object | किसी object का attribute patch करना |
| patch.dict | Temporarily modify a dict | Dict में अस्थायी बदलाव |
| target string | "module.name" to replace | बदलने वाला "module.name" |
| autospec | Mock that copies the real signature | असली signature वाला mock |
| Monkeypatch | Change code at runtime | Runtime पर code बदलना |

---

## ⚡ 3-Line Summary
English: `patch` swaps an object for a mock during a test and restores it afterwards, as a decorator, `with` block, or `start/stop`. Always patch the name where it is looked up, and remember the bottom decorator becomes the first argument. Prefer dependency injection when possible.
Hindi: `patch` test के दौरान object को mock से बदलता है और बाद में restore करता है, decorator, `with` block या `start/stop` के रूप में। हमेशा उस जगह patch करें जहां नाम देखा जाता है, और याद रखें कि सबसे नीचे वाला decorator पहला argument बनता है। संभव हो तो dependency injection चुनें।

---

## ➡️ Next Topic
**286. Side Effects in Mocking** — make mocks raise errors, return different values per call, or run a function using `side_effect`.
