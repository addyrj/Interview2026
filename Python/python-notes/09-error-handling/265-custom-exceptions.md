---

# 265. Custom Exceptions
# हिंदी में: Custom Exceptions (अपनी खुद की Exception classes)

---

## 🔵 Simple Definition (English)
A custom exception is your own class that inherits from `Exception`. It gives a business problem (like "insufficient balance") a clear name, so callers can catch exactly that problem and nothing else.

## 🔵 सरल परिभाषा (Hindi)
Custom exception आपकी अपनी class होती है जो `Exception` से inherit करती है। यह business problem (जैसे "balance कम है") को साफ़ नाम देती है, ताकि caller ठीक वही problem पकड़े और कुछ और नहीं।

---

## 🔴 Problem it Solves
Built-in errors like `ValueError` or `RuntimeError` are too generic. If a payment fails because of low balance, and also because of a bad amount, both look like `ValueError`. The caller cannot tell them apart without parsing the message string, which is fragile. Custom exceptions carry a type, extra data (error code, amount) and a place in a hierarchy.

## 🔴 यह क्यों बना? (Hindi)
`ValueError` या `RuntimeError` जैसी built-in errors बहुत generic हैं। Payment कम balance से fail हो या गलत amount से, दोनों `ValueError` दिखते हैं। Caller को message string parse करनी पड़ती है, जो कमज़ोर तरीका है। Custom exception में अपना type, extra data (error code, amount) और hierarchy मिलती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create one base class for your app: class AppError(Exception)
Step 2 → Create specific children: class InsufficientFunds(AppError)
Step 3 → Store useful data in __init__ (code, amount, ...) and call super().__init__(message)
Step 4 → raise InsufficientFunds(...) where the problem is detected
Step 5 → Catch the child for specific handling, or AppError for "any of ours"
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → App की एक base class बनाइए: class AppError(Exception)
Step 2 → Specific children बनाइए: class InsufficientFunds(AppError)
Step 3 → __init__ में ज़रूरी data रखिए और super().__init__(message) call कीजिए
Step 4 → जहाँ problem मिले वहाँ raise InsufficientFunds(...) कीजिए
Step 5 → Specific handling के लिए child पकड़िए, "हमारी कोई भी" के लिए AppError
```

---

## 🟡 Real World Example
Razorpay-style payment service: `PaymentError` is the base; `InsufficientFunds`, `CardExpired`, `GatewayTimeout` are children. The API layer maps each to an HTTP status (402, 400, 504). A Swiggy order service raises `RestaurantClosed` and the app shows a friendly screen.

## 🟡 Real Example Hindi mein
Razorpay जैसी payment service में `PaymentError` base है; `InsufficientFunds`, `CardExpired`, `GatewayTimeout` उसके children हैं। API layer हर एक को HTTP status (402, 400, 504) में बदलती है। Swiggy का order service `RestaurantClosed` raise करता है और app friendly screen दिखाती है।

---

## 💻 Code Example — Basic
```python
# Basic custom exception - every line commented
class InsufficientFunds(Exception):  # inherit from Exception (never BaseException)
    """Raised when the wallet has less money than needed."""  # docstring explains purpose


def withdraw(balance: int, amount: int) -> int:  # returns the new balance
    if amount > balance:  # business rule check
        raise InsufficientFunds(f"need {amount}, have {balance}")  # raise with message
    return balance - amount  # normal path


try:  # code that may fail
    withdraw(100, 500)  # asks for more than available
except InsufficientFunds as exc:  # catch only our specific error
    print("Caught:", exc)  # str(exc) is the message
# Output: Caught: need 500, have 100

print(issubclass(InsufficientFunds, Exception))  # it is a normal Exception subclass
# Output: True
print(InsufficientFunds.__mro__[1].__name__)  # direct parent in the MRO
# Output: Exception
print(repr(InsufficientFunds("x")))  # repr shows class name and args
# Output: InsufficientFunds('x')
```

## 💻 Code Example — Advanced
```python
# Production style: hierarchy + extra data + error codes + HTTP mapping
from __future__ import annotations  # allow forward references in hints

from typing import Any, Dict  # type hints


class PaymentError(Exception):  # base class for the whole payment module
    code: str = "payment_error"  # machine readable code (class attribute)
    http_status: int = 400  # default HTTP status for this error

    def __init__(self, message: str, **details: Any) -> None:  # message + extra data
        super().__init__(message)  # keep Exception behaviour (args, str)
        self.message: str = message  # store for easy access
        self.details: Dict[str, Any] = details  # e.g. amount, order_id

    def to_dict(self) -> Dict[str, Any]:  # JSON friendly form for API responses
        return {"code": self.code, "message": self.message, **self.details}


class InsufficientFunds(PaymentError):  # specific child
    code = "insufficient_funds"  # override code
    http_status = 402  # Payment Required


class GatewayTimeout(PaymentError):  # another child
    code = "gateway_timeout"  # override code
    http_status = 504  # Gateway Timeout


def charge(balance: int, amount: int) -> int:  # business function
    if amount <= 0:  # invalid input
        raise PaymentError("amount must be positive", amount=amount)  # base error
    if amount > balance:  # not enough money
        raise InsufficientFunds("balance too low", need=amount, have=balance)  # child
    return balance - amount  # success


for amt in (50, 500, -1):  # three scenarios
    try:  # attempt a charge
        print("new balance:", charge(100, amt))  # success path
    except InsufficientFunds as exc:  # most specific first
        print(exc.http_status, exc.to_dict())  # status + payload
    except PaymentError as exc:  # any other payment error (catches the base)
        print(exc.http_status, exc.to_dict())  # same handling, different data
# Output:
# new balance: 50
# 402 {'code': 'insufficient_funds', 'message': 'balance too low', 'need': 500, 'have': 100}
# 400 {'code': 'payment_error', 'message': 'amount must be positive', 'amount': -1}

print(str(GatewayTimeout("slow")), GatewayTimeout("slow").args)  # str and args
# Output: slow ('slow',)
print(isinstance(InsufficientFunds("x"), PaymentError))  # child is-a parent
# Output: True
```

---

## 🟠 JavaScript vs Python Comparison
Both languages let you subclass `Error`. In JS you must set `this.name` yourself; in Python the class name is used automatically.

```python
# Python way
class ValidationError(Exception):  # subclass Exception
    def __init__(self, field: str) -> None:  # store the field
        super().__init__(f"{field} is invalid")  # message
        self.field: str = field  # extra data

try:
    raise ValidationError("email")  # throw
except ValidationError as e:  # catch by class
    print(e, e.field)  # email is invalid email
```
```javascript
// JavaScript way
class ValidationError extends Error {        // subclass Error
  constructor(field) {
    super(`${field} is invalid`);            // message
    this.name = "ValidationError";           // must set manually
    this.field = field;                      // extra data
  }
}
try { throw new ValidationError("email"); }  // throw
catch (e) { if (e instanceof ValidationError) console.log(e.message, e.field); }
```

Key differences: Python's `except ValidationError` filters by class directly (JS needs `instanceof` inside one `catch`). Python's `raise` takes any `BaseException` instance; JS can throw anything.

---

## 🟠 FastAPI Connection
Define domain errors once, then register one `exception_handler` so every route returns a consistent JSON error without try/except in each route.

```python
# FastAPI: custom exception handler (pip install fastapi httpx)
from fastapi import FastAPI, Request  # app and request type
from fastapi.responses import JSONResponse  # JSON response class

app: FastAPI = FastAPI()  # create the app


class OutOfStock(Exception):  # domain error
    def __init__(self, sku: str) -> None:  # store the sku
        super().__init__(f"{sku} is out of stock")  # message
        self.sku: str = sku  # extra data


@app.exception_handler(OutOfStock)  # run for every OutOfStock raised in a route
async def out_of_stock_handler(request: Request, exc: OutOfStock) -> JSONResponse:
    return JSONResponse(status_code=409, content={"error": str(exc), "sku": exc.sku})


@app.get("/buy/{sku}")  # GET /buy/abc
async def buy(sku: str) -> dict:
    raise OutOfStock(sku)  # handler converts it to a 409 response
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Inheriting from `BaseException`
```python
# Wrong - `except Exception` will not catch it (also catches Ctrl+C level stuff)
class MyError(BaseException): ...

# Right
class MyError(Exception): ...
```

❌ Mistake 2: Extra constructor arguments that are not passed to `super().__init__()`
```python
import pickle  # exceptions cross process boundaries (multiprocessing, Celery) via pickle

# Wrong - args holds only ("hi",), so unpickling calls E("hi") and loses `code`
class E(Exception):
    def __init__(self, msg, code):
        super().__init__(msg)
        self.code = code
# pickle.loads(pickle.dumps(E("hi", 5)))
# TypeError: E.__init__() missing 1 required positional argument: 'code'

# Right - pass every positional argument to super().__init__
class E2(Exception):
    def __init__(self, msg, code):
        super().__init__(msg, code)
        self.code = code
print(pickle.loads(pickle.dumps(E2("hi", 5))).code)   # 5
```

❌ Mistake 3: One exception class for everything, or too many tiny ones
```python
# Wrong - callers must parse the message
raise Exception("insufficient funds")

# Right - a small hierarchy with one app base class
raise InsufficientFunds("insufficient funds")
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
class E(Exception):
    def __init__(self, msg, code):
        self.msg = msg
        self.code = code

e = E("boom", 42)
print(e.args, str(e))
try:
    raise E("bad", 7)
except E as err:
    print(err.msg, err.code)
```

**Answer**:
```
('boom', 42) ('boom', 42)
bad 7
```
`BaseException.__new__` stores all constructor arguments in `args` before `__init__` runs, so `args` is filled even though `super().__init__` was never called. With two args, `str(e)` is the tuple text `('boom', 42)`. With one arg it would be just that arg. Calling `super().__init__(msg)` explicitly is still the clean way.

---

## ⚫ Interview Questions + Answers

Q1: Why inherit from `Exception` and not `BaseException`?
A1: `BaseException` is for system-exiting events (`KeyboardInterrupt`, `SystemExit`). A bare `except Exception` should not swallow those, so app errors go under `Exception`.

Q2: Why create an app-level base exception?
A2: One `except AppError` catches everything your code raises on purpose, while real bugs (`TypeError`, `KeyError`) still propagate. It also gives one place to add shared fields like `code`.

Q3: How do you attach extra data?
A3: Store it in `__init__` as attributes (`self.code`) and pass the human message to `super().__init__`. Keep it JSON-friendly if it goes to an API.

Q4: Should the name end in `Error`?
A4: By convention yes for error conditions (`ValidationError`), and plain names for non-errors. PEP 8 recommends the `Error` suffix.

Q5: Where should custom exceptions live?
A5: In a small module like `exceptions.py` in the package so every layer (service, repository, API) imports from the same place and avoids circular imports.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- A business rule fails and callers need to react differently
- You want to carry data (code, ids) with the error
- You build a library or service API

❌ Avoid when:
- A built-in fits perfectly (`ValueError` for a bad argument, `KeyError` for a missing key)
- You are only wrapping a message with no new meaning
- You would create a class per line of code (hierarchy explosion)

---

## 📊 Visual Diagram

```
BaseException
   └── Exception
         └── PaymentError            (your app base: code, to_dict)
               ├── InsufficientFunds (402)
               ├── CardExpired       (400)
               └── GatewayTimeout    (504)

except InsufficientFunds → only that
except PaymentError      → all payment errors
except Exception         → everything (too wide)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Custom exception | Your own Exception subclass | अपनी बनाई exception class |
| Hierarchy | Parent and child exception classes | parent-child classes का ढाँचा |
| Base error | Common parent for app errors | app की साझा parent error |
| args | Tuple of constructor arguments | constructor arguments का tuple |
| Error code | Machine readable error id | मशीन के लिए error पहचान |
| Exception handler | Function mapping error to response | error को response में बदलने वाला function |

---

## ⚡ 3-Line Summary
English: A custom exception is a subclass of `Exception` that names a specific failure. Build one base error per app and small children under it, carrying useful data. Callers catch the child for specific handling or the base for all.
Hindi: Custom exception `Exception` की subclass है जो किसी specific failure को नाम देती है। हर app की एक base error और उसके नीचे छोटे children बनाइए, जिनमें ज़रूरी data हो। Caller child पकड़कर specific handling करे या base पकड़कर सब संभाले।

---

## ➡️ Next Topic
**266. Exception Chaining (raise from)** — keep the original cause when you convert a low-level error into your custom one.
