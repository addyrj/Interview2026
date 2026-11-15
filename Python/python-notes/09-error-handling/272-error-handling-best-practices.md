---

# 272. Error Handling Best Practices
# हिंदी में: Error Handling की Best Practices

---

## 🔵 Simple Definition (English)
Good error handling means: catch specific exceptions, keep `try` blocks small, add context, never swallow errors silently, clean up resources, retry only transient failures, and translate errors once at the boundary.

## 🔵 सरल परिभाषा (Hindi)
अच्छी error handling का मतलब है: specific exceptions पकड़ना, `try` block छोटे रखना, context जोड़ना, errors को चुपचाप न निगलना, resources साफ़ करना, सिर्फ़ transient failures retry करना और boundary पर एक बार errors को translate करना।

---

## 🔴 Problem it Solves
Poor handling hides bugs (`except: pass`), leaks internal details to users, causes duplicate logs, and retries things that can never succeed. A few simple rules keep failures visible, debuggable and safe.

## 🔴 यह क्यों बना? (Hindi)
खराब handling bugs छुपाती है (`except: pass`), internal जानकारी users तक पहुँचाती है, duplicate logs बनाती है और ऐसी चीज़ें retry करती है जो कभी सफल नहीं होंगी। कुछ सरल नियम failures को दिखने योग्य, debug योग्य और सुरक्षित रखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Validate early and fail fast with clear, specific exceptions
Step 2 → Catch only what you can handle, and only around the risky line
Step 3 → Add context with raise NewError(...) from original (keeps the cause)
Step 4 → Use with/finally for cleanup so resources are always released
Step 5 → Retry only transient errors (timeouts), with backoff and a limit
Step 6 → Translate and log ONCE at the boundary (API handler, job runner)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → जल्दी validate करें और साफ़, specific exceptions के साथ तुरंत fail करें
Step 2 → सिर्फ़ वही पकड़ें जिसे संभाल सकें, और सिर्फ़ risky line के आसपास
Step 3 → raise NewError(...) from original से context जोड़ें (cause बचा रहता है)
Step 4 → सफ़ाई के लिए with/finally इस्तेमाल करें ताकि resources हमेशा छूटें
Step 5 → सिर्फ़ transient errors (timeouts) को backoff और limit के साथ retry करें
Step 6 → Boundary (API handler, job runner) पर एक ही बार translate और log करें
```

---

## 🟡 Real World Example
A Swiggy order service: input errors raise `ValueError` early, the DB call is wrapped by a context manager, the payment gateway call is retried 3 times on `Timeout` only, and one FastAPI handler converts `DomainError` to 4xx and everything else to a logged generic 500.

## 🟡 Real Example Hindi mein
Swiggy order service में: input की गलती पर `ValueError` जल्दी उठती है, DB call context manager में होती है, payment gateway call सिर्फ़ `Timeout` पर 3 बार retry होती है, और एक FastAPI handler `DomainError` को 4xx में और बाकी सब को log होने वाले generic 500 में बदलता है।

---

## 💻 Code Example — Basic
```python
# Basic best practices: specific catch, add context, re-raise, fail fast
from typing import Any  # type hint
import json  # parsing


def load_config(text: str) -> dict[str, Any]:  # parse JSON config
    try:  # only the risky line inside try
        data: dict[str, Any] = json.loads(text)  # may raise JSONDecodeError
    except json.JSONDecodeError as exc:  # specific exception, not bare except
        raise ValueError(f"config is not valid JSON: {exc.msg}") from exc  # add context, keep cause
    if "port" not in data:  # fail fast on missing field
        raise KeyError("config needs 'port'")  # clear error
    return data  # good config


print(load_config('{"port": 8000}'))  # ok

for bad in ("{oops", "{}"):  # two bad inputs
    try:  # call
        load_config(bad)  # raises
    except (ValueError, KeyError) as exc:  # expected errors
        print(type(exc).__name__, "->", exc, "| cause:", type(exc.__cause__).__name__)  # show cause

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# {'port': 8000}
# ValueError -> config is not valid JSON: Expecting property name enclosed in double quotes | cause: JSONDecodeError
# KeyError -> "config needs 'port'" | cause: NoneType
```

## 💻 Code Example — Advanced
```python
# Production style: error tree, boundary translation, retries only for transient errors, cleanup
import time  # sleep
import logging  # log at the boundary only
from typing import Callable, TypeVar  # typing

log = logging.getLogger("svc")  # logger
T = TypeVar("T")  # result type


class AppError(Exception):  # root
    pass  # marker


class Transient(AppError):  # safe to retry
    pass  # marker


class Permanent(AppError):  # never retry
    pass  # marker


def retry(fn: Callable[[], T], tries: int = 3) -> T:  # retry ONLY transient errors
    for n in range(1, tries + 1):  # attempts
        try:  # call
            return fn()  # success returns
        except Transient as exc:  # retryable
            if n == tries:  # last attempt
                raise  # re-raise unchanged (keeps traceback)
            print(f"retry {n} after: {exc}")  # visible retry
            time.sleep(0.01 * 2 ** n)  # exponential backoff
    raise AssertionError("unreachable")  # for type checkers


state: list[int] = [0]  # call counter


def bank_call() -> str:  # flaky dependency
    state[0] += 1  # count
    if state[0] < 3:  # fail twice
        raise Transient("bank busy")  # transient
    return "paid"  # then ok


print(retry(bank_call))  # recovers


def validate(amount: int) -> None:  # permanent failure
    if amount <= 0:  # invalid
        raise Permanent("amount must be positive")  # do not retry


def handler(amount: int) -> dict[str, str]:  # BOUNDARY: translate + log once
    try:  # call
        validate(amount)  # may raise
        return {"status": retry(bank_call)}  # may raise
    except Permanent as exc:  # client mistake
        return {"error": str(exc), "http": "400"}  # no stack trace needed
    except AppError:  # other app errors
        log.exception("unexpected app error")  # log once with traceback
        return {"error": "try later", "http": "503"}  # generic message


print(handler(-5))  # permanent
print(handler(10))  # success

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# retry 1 after: bank busy
# retry 2 after: bank busy
# paid
# {'error': 'amount must be positive', 'http': '400'}
# {'status': 'paid'}
```

---

## 🟠 JavaScript vs Python Comparison
In JS the same ideas apply, but `catch` receives anything (even strings), promises can fail without `await`, and unhandled rejections are a common bug. Python has typed `except` and structured chaining (`from`).

```python
try:
    data = load()
except FileNotFoundError as e:
    raise ConfigError('config missing') from e   # chained cause
```
```javascript
try {
  data = await load();
} catch (e) {
  throw new ConfigError('config missing', { cause: e }); // ES2022 cause
}
```

Key differences: Both support chaining causes (`from e` vs `{ cause: e }`). Python lets you pick the exception type in `except`; JS needs `instanceof` checks inside one `catch`.

---

## 🟠 FastAPI Connection
Keep endpoints free of `try/except`. Raise domain errors, register one handler per error family with `@app.exception_handler`, use `yield` dependencies for cleanup, and let Pydantic reject bad input with 422 before your code runs.

```python
# FastAPI: domain errors -> HTTP codes in ONE place; endpoints stay clean
from fastapi import FastAPI, Request  # app and request
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # client


class DomainError(Exception):  # root
    http_status: int = 400  # default status


class OutOfStock(DomainError):  # specific
    http_status = 409  # conflict


app: FastAPI = FastAPI()  # app


@app.exception_handler(DomainError)  # one translation point
async def domain_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.http_status, content={"error": type(exc).__name__, "msg": str(exc)})


@app.post("/buy/{sku}")  # endpoint has NO try/except
def buy(sku: str) -> dict[str, str]:
    if sku == "sold-out":  # business rule
        raise OutOfStock("item sold out")  # just raise
    return {"bought": sku}  # ok


c = TestClient(app)  # client
print(c.post("/buy/pen").json())  # ok
r = c.post("/buy/sold-out")  # error case
print(r.status_code, r.json())  # translated centrally

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# {'bought': 'pen'}
# 409 {'error': 'OutOfStock', 'msg': 'item sold out'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Swallowing errors
```python
# Wrong
try:
    save()
except Exception:
    pass  # bug hidden forever

# Right
try:
    save()
except IntegrityError as exc:
    raise DuplicateOrder(order_id) from exc
```

❌ Mistake 2: Huge try blocks
```python
# Wrong
try:
    a = load(); b = parse(a); c = save(b)   # which one failed?
except Exception:
    ...

# Right
a = load()
try:
    b = parse(a)
except ValueError as exc:
    raise BadFile() from exc
c = save(b)
```

❌ Mistake 3: Retrying permanent errors
```python
# Wrong
for _ in range(5):
    try: validate(x)
    except ValueError: continue  # will never succeed

# Right
# Retry only Transient errors (timeouts, 503). Fail fast on ValueError.
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def a() -> None:  # swallow with pass
    try:  # try
        raise ValueError("lost")  # error
    except Exception:  # too broad
        pass  # silent failure

print(a())  # None, error vanished

def b() -> None:  # raise vs raise e
    try:  # inner
        raise ValueError("orig")  # error
    except ValueError as e:  # catch
        raise RuntimeError("wrapped") from e  # keeps the cause chain

try:  # call
    b()  # raises RuntimeError
except RuntimeError as e:  # catch
    print(repr(e), "|", repr(e.__cause__))  # cause preserved

def c() -> int:  # EAFP vs LBYL
    d: dict[str, int] = {}  # empty dict
    try:  # EAFP: ask forgiveness
        return d["k"]  # KeyError
    except KeyError:  # handle
        return -1  # default

print(c())  # -1
```

**Answer**:
```
None
RuntimeError('wrapped') | ValueError('orig')
-1
```
`a()` returns `None` and the `ValueError` disappears completely, which is the classic silent failure. `raise ... from e` stores the original in `__cause__`, so tools and logs show the full chain. EAFP ("easier to ask forgiveness") lets `c()` handle the missing key with `except KeyError`, which is also safe against race conditions.

---

## ⚫ Interview Questions + Answers

Q1: EAFP vs LBYL?
A1: EAFP: try it and handle the exception (Pythonic, race-free). LBYL: check first with `if`. Use LBYL when the check is cheap and failure is common.

Q2: When should you re-raise?
A2: When you only add logging or cleanup. Use bare `raise` to keep the original traceback.

Q3: What does `raise ... from e` do?
A3: Sets `__cause__` so the traceback shows "The above exception was the direct cause". `from None` hides the original.

Q4: Which errors are safe to retry?
A4: Transient ones: timeouts, connection resets, HTTP 429/503. Never validation or permission errors. Add backoff and a limit; make the operation idempotent.

Q5: Where should errors be translated to HTTP?
A5: At one boundary (exception handlers), not inside every endpoint.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Write rules once: raise low, handle high
- Define an app exception tree for domain errors
- Use context managers for resources

❌ Avoid when:
- Bare `except:` or `except Exception: pass`
- Returning error codes like -1 or None for failures
- Leaking stack traces or secrets to API clients

---

## 📊 Visual Diagram

```
validate early ─► raise specific error ─► (add context: from e)
                                           │
                     retry only if Transient (backoff, limit)
                                           │
                     boundary: log once + translate (4xx / generic 5xx)
 cleanup always: with / finally
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EAFP | Try first, handle errors | पहले करो, error आए तो संभालो |
| LBYL | Look before you leap | पहले जाँचो फिर करो |
| fail fast | Stop at the first problem | पहली गड़बड़ी पर रुकना |
| backoff | Wait longer after each retry | हर retry पर ज़्यादा इंतज़ार |
| idempotent | Safe to repeat | दोहराना सुरक्षित |
| boundary | Edge where errors are handled | वह किनारा जहाँ errors संभलती हैं |

---

## ⚡ 3-Line Summary
English: Catch specific errors around small blocks, add context with `from`, clean up with `with`/`finally`, retry only transient failures and translate/log once at the boundary. Never swallow errors silently.
Hindi: छोटे blocks के आसपास specific errors पकड़ें, `from` से context जोड़ें, `with`/`finally` से सफ़ाई करें, सिर्फ़ transient failures retry करें और boundary पर एक बार translate/log करें। Errors को कभी चुपचाप न निगलें।

---

## ➡️ Next Topic
**273. Exception Groups (Python 3.11+)** — raising several errors at once.

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.
