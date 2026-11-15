---

# 286. Side Effects in Mocking
# हिंदी में: Mocking में Side Effects (हर call पर अलग व्यवहार)

---

## 🔵 Simple Definition (English)
`side_effect` is a mock setting that controls what happens when the mock is called. It can raise an exception, return a different value on each call (from a list or iterator), or run a function to compute the result. It is how you simulate failures, retries, and stateful behaviour.

## 🔵 सरल परिभाषा (Hindi)
`side_effect` mock की एक setting है जो तय करती है कि mock को call करने पर क्या होगा। यह exception raise कर सकती है, हर call पर अलग value (list या iterator से) दे सकती है, या नतीजा निकालने के लिए function चला सकती है। Failures, retries और state वाले व्यवहार को simulate करने का यही तरीका है।

---

## 🔴 Problem it Solves
`return_value` gives the same answer on every call. Real systems are not like that: a network call fails twice and then works, a database raises a timeout, a counter increases, a function returns something that depends on its arguments. Without `side_effect` you could not test retry logic, error handling, pagination, or "first call fails, second succeeds" flows.

## 🔴 यह क्यों बना? (Hindi)
`return_value` हर call पर एक ही जवाब देता है। असली systems ऐसे नहीं होते: network call दो बार fail होकर फिर चल जाता है, database timeout देता है, counter बढ़ता है, कोई function अपने arguments पर निर्भर नतीजा देता है। `side_effect` के बिना retry logic, error handling, pagination या "पहली call fail, दूसरी सफल" जैसे flows test नहीं हो सकते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → side_effect = Exception class or instance  -> raised on every call
Step 2 → side_effect = list / iterable              -> next item per call;
                                                       an exception item is RAISED, others returned
Step 3 → list exhausted                             -> StopIteration on the next call
Step 4 → side_effect = function                     -> called with the same args; its return value is used
Step 5 → function returns mock.DEFAULT              -> falls back to return_value
Step 6 → side_effect = None                         -> disabled again

Priority: side_effect (if it produces a value) beats return_value.
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → side_effect = Exception class या instance  -> हर call पर raise होता है
Step 2 → side_effect = list / iterable              -> हर call पर अगला item;
                                                       exception वाला item RAISE होता है, बाकी return
Step 3 → list खत्म हो गई                            -> अगली call पर StopIteration
Step 4 → side_effect = function                     -> वही args के साथ चलता है; उसका return value इस्तेमाल होता है
Step 5 → function mock.DEFAULT लौटाए               -> return_value पर वापस
Step 6 → side_effect = None                         -> फिर बंद

प्राथमिकता: side_effect (अगर value बनाए) return_value से ऊपर है।
```

---

## 🟡 Real World Example
A report job in a Swiggy-style backend downloads data from a partner API with retries: attempt 1 times out, attempt 2 gets a connection error, attempt 3 succeeds. With `side_effect=[ConnectError, ReadTimeout, good_response]` the test proves three things at once: the code retries, it waits with an increasing delay, and it returns the data. Another test makes every attempt fail to verify the final error is raised after the last retry.

## 🟡 Real Example Hindi mein
Swiggy जैसे backend का report job partner API से retries के साथ data उतारता है: पहली कोशिश timeout, दूसरी में connection error, तीसरी सफल। `side_effect=[ConnectError, ReadTimeout, good_response]` से test एक साथ तीन चीज़ें साबित करता है: code retry करता है, बढ़ती देरी के साथ रुकता है और data लौटाता है। दूसरा test हर कोशिश fail कराकर जांचता है कि आखिरी retry के बाद error raise होता है।

---

## 💻 Code Example — Basic
```python
# side_effect basics (verified on Python 3.13)
from unittest.mock import Mock, DEFAULT           # mock tools

m = Mock(side_effect=ConnectionError("db down"))  # exception: raised on every call
try:
    m()                                           # call it
except ConnectionError as e:
    print("raised:", e)                           # raised: db down

m = Mock(side_effect=[1, 2, ValueError("third")]) # sequence: one item per call
print(m(), m())                                   # 1 2
try:
    m()                                           # exception item is raised, not returned
except ValueError as e:
    print("raised:", e)                           # raised: third
try:
    m()                                           # list exhausted
except StopIteration:
    print("StopIteration (sequence exhausted)")

m = Mock(side_effect=lambda x: x * 2)             # function: computes the result from the args
print(m(21))                                      # 42

m = Mock(return_value="ignored", side_effect=lambda x: x)   # side_effect result wins
print(m("fn result"))                             # fn result

m = Mock(return_value="rv", side_effect=lambda x: DEFAULT if x == 0 else x + 1)
print(m(0), m(5))                                 # rv 6   (DEFAULT -> use return_value)

# Output:
# raised: db down
# 1 2
# raised: third
# StopIteration (sequence exhausted)
# 42
# fn result
# rv 6
```

## 💻 Code Example — Advanced
```python
# Production style: retry with back-off, tested with side_effect (verified: 4 passed)
import logging                                    # log failures
import time                                       # sleep between attempts
import httpx                                      # HTTP client

log: logging.Logger = logging.getLogger("svc")    # module logger


def fetch_with_retry(url: str, retries: int = 3, delay: float = 0.5) -> str:
    """Retry on network errors with a growing delay; raise after the last attempt."""
    for attempt in range(1, retries + 1):         # attempts 1..retries
        try:
            r = httpx.get(url, timeout=2)         # may raise a TransportError
            r.raise_for_status()                  # raise on 4xx/5xx
            return r.text                         # success
        except httpx.TransportError as exc:       # transient network problem
            log.warning("attempt %s failed: %s", attempt, exc)
            if attempt == retries:                # out of attempts
                raise                             # re-raise the last error
            time.sleep(delay * attempt)           # back-off: 0.5s, 1.0s, ...
    raise RuntimeError("unreachable")             # satisfies type checkers


# ---- tests ----
from unittest.mock import patch, Mock, call       # mock tools
import pytest                                     # framework


def ok(text: str) -> Mock:                        # helper: fake successful response
    r = Mock()
    r.text = text
    r.raise_for_status.return_value = None
    return r


@patch("time.sleep")                              # never really sleep in tests
@patch("httpx.get")
def test_succeeds_on_third(get: Mock, sleep: Mock) -> None:
    get.side_effect = [httpx.ConnectError("1"), httpx.ReadTimeout("2"), ok("data")]   # fail, fail, success
    assert fetch_with_retry("http://x") == "data"
    assert get.call_count == 3                    # tried three times
    assert sleep.call_args_list == [call(0.5), call(1.0)]    # back-off verified


@patch("time.sleep")
@patch("httpx.get", side_effect=httpx.ConnectError("always"))
def test_gives_up(get: Mock, sleep: Mock) -> None:
    with pytest.raises(httpx.ConnectError):       # last error is re-raised
        fetch_with_retry("http://x", retries=2)
    assert get.call_count == 2


def test_stateful_fake() -> None:
    db: dict[int, str] = {}                       # tiny in-memory store
    store = Mock(side_effect=lambda k, v: db.__setitem__(k, v))   # side effect performs real work
    store(1, "a")
    assert db == {1: "a"}                         # the "fake" really changed state


def test_context_manager_mock() -> None:
    with patch("builtins.open", create=True) as m_open:      # mock open()
        m_open.return_value.__enter__.return_value.read.return_value = "file text"
        with open("any.txt") as f:                # uses the mock, no real file
            assert f.read() == "file text"

# Real run (single file, pytest): 4 passed.
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript (Jest) |
|---------|--------|-------------------|
| Always raise | `side_effect=ValueError("x")` | `fn.mockImplementation(() => { throw new Error("x") })` |
| Different per call | `side_effect=[1, 2, 3]` | `.mockReturnValueOnce(1).mockReturnValueOnce(2)` |
| Compute from args | `side_effect=lambda x: x*2` | `fn.mockImplementation(x => x * 2)` |
| Reject a promise | `AsyncMock(side_effect=Exc())` | `fn.mockRejectedValueOnce(new Error())` |
| After list ends | `StopIteration` | falls back to default implementation / `undefined` |

```python
# Python way
from unittest.mock import Mock

api = Mock(side_effect=[TimeoutError("t"), {"ok": True}])   # fail then succeed
try:
    api()
except TimeoutError:
    pass
print(api())                                      # {'ok': True}
```
```javascript
// JavaScript way (Jest)
const api = jest.fn()
  .mockRejectedValueOnce(new Error("t"))          // first call rejects
  .mockResolvedValueOnce({ ok: true });           // second call resolves
await api().catch(() => {});                      // swallow the first error
console.log(await api());                         // { ok: true }
```

Key difference: Python puts everything in one `side_effect` argument (exception, list, or function). Jest has separate chained helpers. When a Python list runs out you get `StopIteration`, which is easy to mistake for a bug in your code.

---

## 🟠 FastAPI Connection
`side_effect` is how you test your FastAPI error handlers: make the dependency raise `TimeoutError` or a database exception and check that the route returns a 503 or 500 with a clean JSON body, not a stack trace. With `AsyncMock` the same works for `async def` services.

```python
# FastAPI: simulate an upstream failure and check the error response
from unittest.mock import MagicMock                       # fake object
from fastapi import Depends, FastAPI, HTTPException       # FastAPI
from fastapi.testclient import TestClient                 # client

app: FastAPI = FastAPI()                                  # app


class Payments:                                           # real dependency
    def charge(self, amount: int) -> str:
        return "ok"


def get_payments() -> Payments:                           # provider
    return Payments()


@app.post("/pay")
def pay(amount: int, svc: Payments = Depends(get_payments)) -> dict[str, str]:
    try:
        return {"status": svc.charge(amount)}             # call the dependency
    except TimeoutError:
        raise HTTPException(status_code=503, detail="payment service unavailable")   # clean error


def test_pay_timeout() -> None:
    fake = MagicMock(spec=Payments)                       # strict fake
    fake.charge.side_effect = TimeoutError("slow")        # simulate the outage
    app.dependency_overrides[get_payments] = lambda: fake
    try:
        r = TestClient(app).post("/pay", params={"amount": 10})
    finally:
        app.dependency_overrides.clear()                  # reset overrides
    assert r.status_code == 503 and r.json()["detail"] == "payment service unavailable"
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing an exception inside a list but expecting it to be returned
✅ Correct: exceptions (classes or instances) in a list are RAISED; wrap in a function if you want to return one

```python
from unittest.mock import Mock
m = Mock(side_effect=[ValueError("boom")])
# Wrong thinking: x = m()  -> x is the ValueError object   (actually raises)
# Right: use pytest.raises / try-except around the call
```

❌ Mistake 2: Setting both `return_value` and a list side_effect and expecting `return_value`
✅ Correct: `side_effect` wins; use `DEFAULT` from a function to fall back

❌ Mistake 3: Calling the mock more times than the list has items
✅ Correct: provide enough items (or use `itertools.cycle` / a function) — otherwise `StopIteration` appears (inside a generator it can even become a `RuntimeError`)

```python
from unittest.mock import Mock
import itertools
m = Mock(side_effect=itertools.cycle([1, 2]))     # endless alternating values
print(m(), m(), m())                              # 1 2 1
```

❌ Mistake 4: Not patching `time.sleep` in retry tests
✅ Correct: patch it; otherwise the test really waits (slow CI) — and assert the delays with `call_args_list`

---

## 🧠 Tricky Interview Question

```python
# What will this output?
from unittest.mock import Mock

m = Mock(side_effect=[1, 2], return_value=99)
print(m(), m())
try:
    print(m())
except StopIteration:
    print("stop")
m.side_effect = None
print(m())
```
Answer: `1 2`, then `stop`, then `99`. The list side effect is used first (it beats `return_value`), the third call raises `StopIteration` because the list is exhausted, and after `m.side_effect = None` the mock falls back to `return_value`, so it prints `99`.

---

## ⚫ Interview Questions + Answers

Q1: What are the three kinds of `side_effect`?
A1: An exception (class or instance) is raised on every call; an iterable returns its next item each call (exception items are raised); a callable is called with the same arguments and its return value becomes the result (unless it returns `mock.DEFAULT`).

Q2: How would you test that your code retries 3 times and then succeeds?
A2: Patch the network call with `side_effect=[Error, Error, good_response]`, patch `time.sleep`, then assert the final result, `call_count == 3`, and the sleep delays with `call_args_list`.

Q3: How is `side_effect` different from `return_value`?
A3: `return_value` is a fixed answer for every call. `side_effect` can vary per call, raise errors, or compute from arguments. If a side_effect function returns something other than `DEFAULT`, it overrides `return_value`.

Q4: How do you make an `AsyncMock` raise?
A4: `AsyncMock(side_effect=TimeoutError())`: awaiting it raises. A list works too: the first `await` returns the first item. `assert_awaited_*` methods check the awaits.

Q5: What happens when the side_effect list runs out?
A5: The next call raises `StopIteration`. Inside generators/async code it can turn into `RuntimeError`, so give enough items or use a function or `itertools.cycle`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Testing retries, timeouts, and failover
- First call fails, later calls succeed
- The fake needs to compute a result from its arguments or keep state
- Checking your error handlers (503/500 responses)

❌ Avoid when:
- A fixed `return_value` is enough
- The side_effect function grows into a full fake implementation (write a real fake class instead)
- You are mocking so much of the flow that the test checks nothing real

---

## 📊 Visual Diagram
```
side_effect = [ConnectError, ReadTimeout, response]      retry loop (3 attempts)

call 1 ──► raises ConnectError   ──► sleep(0.5) ─┐
call 2 ──► raises ReadTimeout    ──► sleep(1.0) ─┤  attempt counter 1,2,3
call 3 ──► returns response      ──► return text ◄┘
call 4 ──► StopIteration  (list exhausted - test bug)

Asserts:  call_count == 3     sleep.call_args_list == [call(0.5), call(1.0)]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| side_effect | Per-call behaviour of a mock | Mock का हर call पर व्यवहार |
| DEFAULT | Sentinel meaning "use return_value" | "return_value इस्तेमाल करो" का संकेत |
| StopIteration | List of results exhausted | Results की list खत्म |
| Back-off | Growing delay between retries | Retries के बीच बढ़ती देरी |
| Transient error | Temporary failure | अस्थायी failure |
| AsyncMock | Mock for coroutines | Coroutines के लिए mock |

---

## ⚡ 3-Line Summary
English: `side_effect` makes a mock raise exceptions, return a different item on each call, or run a function. It overrides `return_value` unless the function returns `DEFAULT`. Use it to test retries, timeouts, and error handlers.
Hindi: `side_effect` mock को exception raise करने, हर call पर अलग item देने या function चलाने देता है। यह `return_value` को override करता है, जब तक function `DEFAULT` न लौटाए। Retries, timeouts और error handlers test करने में इसका इस्तेमाल करें।

---

## ➡️ Next Topic
**287. Testing Async Code** — `pytest-asyncio`, `AsyncMock`, and testing `async def` FastAPI endpoints with `httpx.AsyncClient`.
