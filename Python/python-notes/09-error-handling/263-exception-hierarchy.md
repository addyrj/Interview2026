---

# 263. Exception Hierarchy
# हिंदी में: Exception Hierarchy (exceptions का पेड़)

---

## 🔵 Simple Definition (English)
All Python exceptions are classes in one inheritance tree. `BaseException` is the root, `Exception` is the parent of normal errors, and specific errors like `KeyError` sit below groups like `LookupError`. Catching a parent also catches all its children.

## 🔵 सरल परिभाषा (Hindi)
Python की सारी exceptions एक inheritance tree की classes हैं। `BaseException` सबसे ऊपर है, `Exception` सामान्य errors का parent है, और `KeyError` जैसी specific errors `LookupError` जैसे groups के नीचे आती हैं। Parent पकड़ने पर उसके सारे children भी पकड़े जाते हैं।

---

## 🔴 Problem it Solves
Without a hierarchy you would need a separate `except` for every error type. A tree lets you catch a whole family (`OSError`, `LookupError`) in one line, or one precise error. It also separates "program bugs and errors" (`Exception`) from "stop signals" (`KeyboardInterrupt`, `SystemExit`).

## 🔴 यह क्यों बना? (Hindi)
Hierarchy के बिना हर error type के लिए अलग `except` लिखना पड़ता। Tree से एक line में पूरा परिवार (`OSError`, `LookupError`) या एक सटीक error पकड़ सकते हैं। यह "bugs और errors" (`Exception`) को "रुकने के signals" (`KeyboardInterrupt`, `SystemExit`) से अलग भी रखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every exception class inherits from BaseException
Step 2 → Normal errors inherit from Exception (use this as your catch-all, never bare except)
Step 3 → Related errors share a parent: KeyError and IndexError -> LookupError
Step 4 → except X catches X and every subclass of X (isinstance check)
Step 5 → Python checks except blocks top to bottom, first match wins
Step 6 → So list specific exceptions before general ones
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर exception class BaseException से inherit करती है
Step 2 → सामान्य errors Exception से inherit करती हैं (catch-all के लिए यही इस्तेमाल करें, bare except नहीं)
Step 3 → मिलती-जुलती errors का parent एक होता है: KeyError और IndexError -> LookupError
Step 4 → except X, X और उसकी हर subclass को पकड़ता है (isinstance check)
Step 5 → except blocks ऊपर से नीचे चेक होते हैं, पहला match जीतता है
Step 6 → इसलिए specific exceptions को general से पहले लिखें
```

---

## 🟡 Real World Example
A Razorpay-style service defines `PaymentError` with children `CardDeclined` and `GatewayTimeout`. One handler `except PaymentError` covers all payment failures, while `CardDeclined` gets special treatment. A FastAPI app registers one handler for the app's root `AppError` and every subclass gets proper JSON for free.

## 🟡 Real Example Hindi mein
Razorpay जैसी service में `PaymentError` के children `CardDeclined` और `GatewayTimeout` होते हैं। एक `except PaymentError` सभी payment failures संभालता है और `CardDeclined` को खास treatment मिलता है। FastAPI app में root `AppError` के लिए एक handler रजिस्टर करने पर हर subclass को अपने-आप सही JSON मिलता है।

---

## 💻 Code Example — Basic
```python
# Basic: walk the exception hierarchy using __mro__ - every line commented
print(ValueError.__mro__)  # parents of ValueError, child first
print(KeyError.__mro__[1].__name__)  # KeyError's direct parent is LookupError
print(issubclass(FileNotFoundError, OSError))  # True: file errors are OSErrors
print(issubclass(KeyboardInterrupt, Exception))  # False: it is a BaseException only
print(issubclass(ZeroDivisionError, ArithmeticError))  # True

try:  # catching a PARENT class also catches children
    {}["missing"]  # raises KeyError
except LookupError as exc:  # LookupError is parent of KeyError and IndexError
    print("caught by parent:", type(exc).__name__, exc)  # shows the real type

try:  # IndexError is also a LookupError
    [1, 2][5]  # raises IndexError
except LookupError as exc:  # same handler works
    print("caught by parent:", type(exc).__name__, exc)  # list index error

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# (<class 'ValueError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>)
# LookupError
# True
# False
# True
# caught by parent: KeyError 'missing'
# caught by parent: IndexError list index out of range
```

## 💻 Code Example — Advanced
```python
# Production style: print the full tree + design your own hierarchy
from typing import Iterator  # type hints


def walk(cls: type[BaseException], depth: int = 0) -> Iterator[str]:
    yield "    " * depth + cls.__name__  # name with indentation
    for sub in sorted(cls.__subclasses__(), key=lambda c: c.__name__):  # direct children
        if sub.__module__ == "builtins":  # only built-in exceptions
            yield from walk(sub, depth + 1)  # recurse down the tree


tree: list[str] = list(walk(BaseException))  # build whole tree
print("\n".join(tree[:12]))  # first lines are enough to read
print("total builtin exception classes:", len(tree) > 50)  # many classes


class AppError(Exception):  # base for ALL errors of our app
    """Root of the application exception tree."""


class PaymentError(AppError):  # domain group
    """Anything wrong with a payment."""


class CardDeclined(PaymentError):  # concrete error
    """Bank declined the card."""


class GatewayTimeout(PaymentError):  # concrete error
    """Bank did not answer in time."""


def charge(kind: str) -> None:  # simulate a payment call
    if kind == "declined":  # branch 1
        raise CardDeclined("card declined")  # specific
    if kind == "timeout":  # branch 2
        raise GatewayTimeout("bank timeout")  # specific
    raise KeyError(kind)  # unrelated bug


for kind in ("declined", "timeout", "bug"):  # run all three
    try:  # try to charge
        charge(kind)  # raises
    except CardDeclined:  # most specific first
        print(kind, "-> ask user for another card")  # business action
    except PaymentError as exc:  # any other payment error
        print(kind, "-> retry later:", exc)  # generic payment handling
    except AppError:  # any other app error
        print(kind, "-> app error")  # never reached here
    except Exception as exc:  # last safety net (not BaseException!)
        print(kind, "-> unexpected", type(exc).__name__)  # log the bug

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# BaseException
#     BaseExceptionGroup
#         ExceptionGroup
#     Exception
#         ArithmeticError
#             FloatingPointError
#             OverflowError
#             ZeroDivisionError
#         AssertionError
#         AttributeError
#         BufferError
#         EOFError
# total builtin exception classes: True
# declined -> ask user for another card
# timeout -> retry later: bank timeout
# bug -> unexpected KeyError
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has a flat model: you can `throw` anything and `catch` receives it. Built-in classes (`TypeError`, `RangeError`) exist but you filter manually with `instanceof`. Python makes the tree a first-class feature of `except`.

```python
try:
    {}['x']                      # KeyError
except LookupError as e:         # parent class catches it
    print(type(e).__name__)      # KeyError
```
```javascript
try {
  null.x;                         // TypeError
} catch (e) {                      // single catch
  if (e instanceof TypeError) {    // manual filter
    console.log(e.name);
  } else { throw e; }              // rethrow the rest
}
```

Key differences: Python filters by type in the `except` clause itself, JS needs `instanceof` inside one `catch`. In Python you can only raise `BaseException` subclasses, in JS you can throw strings or numbers (bad practice).

---

## 🟠 FastAPI Connection
FastAPI lets you register `@app.exception_handler(AppError)`. Because of the hierarchy, one handler serves the root class and every subclass. This is the standard way to turn domain errors into clean JSON responses.

```python
# FastAPI: one exception handler for the whole AppError tree
from fastapi import FastAPI, Request  # app and request type
from fastapi.responses import JSONResponse  # JSON response
from fastapi.testclient import TestClient  # in-process client


class AppError(Exception):  # root of our tree
    status_code: int = 500  # default HTTP status
    code: str = "app_error"  # machine readable code


class NotFound(AppError):  # child error
    status_code = 404  # override status
    code = "not_found"  # override code


class Conflict(AppError):  # another child
    status_code = 409  # override status
    code = "conflict"  # override code


app: FastAPI = FastAPI()  # create app


@app.exception_handler(AppError)  # handles AppError AND every subclass
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "msg": str(exc)})


@app.get("/orders/{oid}")  # sample endpoint
def get_order(oid: int) -> dict[str, int]:
    if oid == 0:  # missing order
        raise NotFound("order 0 not found")  # subclass of AppError
    if oid == 1:  # duplicate
        raise Conflict("order 1 already paid")  # subclass of AppError
    return {"id": oid}  # ok


c = TestClient(app)  # client
for i in (5, 0, 1):  # three requests
    r = c.get(f"/orders/{i}")  # call
    print(r.status_code, r.json())  # show result

# --- Real output (run on Python 3.13; ids/timings may vary) ---
# 200 {'id': 5}
# 404 {'code': 'not_found', 'msg': 'order 0 not found'}
# 409 {'code': 'conflict', 'msg': 'order 1 already paid'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Catching `BaseException` (or bare `except:`) as a catch-all
```python
# Wrong
try:
    work()
except BaseException:  # also stops Ctrl+C and sys.exit()
    pass

# Right
try:
    work()
except Exception as exc:  # normal errors only
    logger.exception('work failed')
```

❌ Mistake 2: Wrong order: parent before child
```python
# Wrong
try:
    risky()
except LookupError:
    ...
except KeyError:   # never reached

# Right
try:
    risky()
except KeyError:   # specific first
    ...
except LookupError:
    ...
```

❌ Mistake 3: Custom errors that inherit from `BaseException`
```python
# Wrong
class MyError(BaseException): ...  # `except Exception` will miss it

# Right
class MyError(Exception): ...  # always derive from Exception (or a subclass)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
class A(Exception): pass  # parent
class B(A): pass  # child of A

for exc in (B("x"), A("y")):  # raise a child then a parent
    try:  # try
        raise exc  # raise it
    except B:  # catches only B
        print("B handler")  # for B
    except A:  # catches A and its children
        print("A handler")  # for A

try:  # wrong order trap
    try:  # inner try
        raise B()  # raise child
    except A:  # parent first -> catches B too
        print("A first")  # always wins
    except B:  # dead code, never runs
        print("B never")  # unreachable
except Exception:  # not needed
    pass  # nothing

print(issubclass(Exception, BaseException), issubclass(KeyboardInterrupt, Exception))  # True False
print(OSError is IOError, OSError is EnvironmentError)  # True True (aliases)
try:  # catch-all trap
    raise SystemExit(0)  # SystemExit is BaseException
except Exception:  # does not catch it
    print("caught")  # not printed
except BaseException as e:  # catches it
    print("BaseException got", type(e).__name__)  # printed
```

**Answer**:
```
B handler
A handler
A first
True False
True True
BaseException got SystemExit
```
The first loop: `B` is handled by `except B`, `A` by `except A`. In the wrong-order block `except A` also catches `B` instances, so `except B` is dead code. `KeyboardInterrupt` is not a subclass of `Exception`. `IOError` and `EnvironmentError` are just aliases of `OSError` (since 3.3). `SystemExit` is only caught by `BaseException`.

---

## ⚫ Interview Questions + Answers

Q1: What is the root of all exceptions?
A1: `BaseException`. User code should normally catch `Exception` or a subclass, not `BaseException`.

Q2: Why is `KeyboardInterrupt` not an `Exception`?
A2: So that a normal `except Exception` does not swallow Ctrl+C, `sys.exit()` (`SystemExit`) or `GeneratorExit`. These are control-flow signals, not errors.

Q3: How do you see the parents of an exception?
A3: `ValueError.__mro__` or `inspect.getmro`. Children: `cls.__subclasses__()`.

Q4: Why define one base exception for your app?
A4: Callers can catch all your errors with one `except AppError` and framework handlers can be registered once.

Q5: What are the common mid-level parents?
A5: `OSError` (files, network), `LookupError` (`KeyError`, `IndexError`), `ArithmeticError` (`ZeroDivisionError`, `OverflowError`), `ValueError` (and `UnicodeError`).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You want to catch a whole family with one except
- You design your own error tree (AppError, PaymentError...)
- You register framework-wide handlers

❌ Avoid when:
- Catching BaseException unless you are writing a top-level runner
- Making a deep tree with 20 levels (keep it 2-3 levels)
- Creating one class per message instead of per failure type

---

## 📊 Visual Diagram

```
BaseException
 ├── SystemExit, KeyboardInterrupt, GeneratorExit
 ├── BaseExceptionGroup
 └── Exception
      ├── ArithmeticError ── ZeroDivisionError, OverflowError
      ├── LookupError ────── KeyError, IndexError
      ├── OSError ────────── FileNotFoundError, PermissionError, TimeoutError
      ├── ValueError ─────── UnicodeError
      ├── TypeError, AttributeError, RuntimeError ...
      └── YourAppError ───── PaymentError ── CardDeclined
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BaseException | Root of all exceptions | सभी exceptions की जड़ |
| Exception | Parent of normal errors | सामान्य errors का parent |
| Subclass | Child class | child class |
| MRO | Method/Class resolution order | class खोजने का क्रम |
| Catch-all | Handler for any error | हर error का handler |
| Alias | Another name for the same class | उसी class का दूसरा नाम |

---

## ⚡ 3-Line Summary
English: All exceptions form a tree rooted at `BaseException`; normal errors live under `Exception`. `except X` catches X and all its subclasses, so put specific handlers first. Build your own tree under one `AppError` base.
Hindi: सारी exceptions `BaseException` से शुरू होने वाला tree हैं; सामान्य errors `Exception` के नीचे हैं। `except X`, X और उसकी सभी subclasses पकड़ता है, इसलिए specific handlers पहले रखें। अपना tree एक `AppError` base के नीचे बनाएँ।

---

## ➡️ Next Topic
**264. Built-in Exceptions** — the most common exceptions (`ValueError`, `TypeError`, `KeyError`...) and when each is raised.

Verification: all code blocks above were executed on Python 3.13 and the "Real output" comments are the real output.
