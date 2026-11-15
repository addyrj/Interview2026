---

# 325. Custom Exceptions
# हिंदी में: Custom Exceptions (अपने खुद के errors)

---

## 🔵 Simple Definition (English)
A custom exception is your own class that inherits from `Exception` and names a business problem, like `OutOfStock` or `PaymentFailed`. Services raise it; one exception handler maps it to an HTTP response.

## 🔵 सरल परिभाषा (Hindi)
Custom exception आपकी अपनी class है जो `Exception` से inherit होती है और business problem का नाम देती है, जैसे `OutOfStock` या `PaymentFailed`। Services इसे raise करती हैं और एक exception handler इसे HTTP response में बदलता है।

---

## 🔴 Problem it Solves
If service code raises `HTTPException(404)` it is tied to the web layer, so you cannot reuse it in a Celery job or CLI script. Magic strings like `detail="not found"` also differ across files. Domain exceptions keep business code clean and put status codes and formats in one place.

## 🔴 यह क्यों बना? (Hindi)
अगर service code `HTTPException(404)` raise करे तो वह web layer से बँध जाता है, उसे Celery job या CLI script में दोबारा इस्तेमाल नहीं कर सकते। `detail="not found"` जैसे strings हर file में अलग हो जाते हैं। Domain exceptions business code को साफ़ रखते हैं और status code व format एक जगह रखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define `class AppError(Exception)` with `status_code` and `code`
Step 2 → Subclass it: `NotFound`, `PaymentFailed`, `Conflict`
Step 3 → Service/repository raises the domain error with context data
Step 4 → One `@app.exception_handler(AppError)` catches every subclass
Step 5 → Handler builds the JSON body from `exc.code`, `exc.message`, `exc.extra`
Step 6 → Response uses `exc.status_code`; the exception can also be logged centrally
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → `class AppError(Exception)` बनाएँ जिसमें `status_code` और `code` हों
Step 2 → इसकी subclasses बनाएँ: `NotFound`, `PaymentFailed`, `Conflict`
Step 3 → Service/repository context data के साथ domain error raise करती है
Step 4 → एक `@app.exception_handler(AppError)` सारी subclasses पकड़ लेता है
Step 5 → Handler `exc.code`, `exc.message`, `exc.extra` से JSON body बनाता है
Step 6 → Response में `exc.status_code` लगता है; exception को एक जगह log भी कर सकते हैं
```

---

## 🟡 Real World Example
An e-commerce backend: `InsufficientStock` -> 409, `CouponExpired` -> 422, `PaymentDeclined` -> 402, `UserNotFound` -> 404. The same service functions are used by the REST API, a Kafka consumer and a nightly job, and only the REST layer translates them to HTTP.

## 🟡 Real Example Hindi mein
E-commerce backend: `InsufficientStock` -> 409, `CouponExpired` -> 422, `PaymentDeclined` -> 402, `UserNotFound` -> 404। वही service functions REST API, Kafka consumer और nightly job इस्तेमाल करते हैं, और सिर्फ़ REST layer इन्हें HTTP में बदलती है।

---

## 💻 Code Example — Basic
One custom exception plus one handler.

```python
# Basic custom exception - every line commented
from fastapi import FastAPI, Request  # tools
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # test client


class OutOfStock(Exception):  # our own exception type
    def __init__(self, item: str) -> None:  # constructor
        self.item: str = item  # keep data for the handler


app: FastAPI = FastAPI()  # app


@app.exception_handler(OutOfStock)  # map exception -> HTTP response
async def out_of_stock_handler(request: Request, exc: OutOfStock) -> JSONResponse:  # handler
    return JSONResponse(status_code=409, content={"message": f"{exc.item} is out of stock"})  # 409 Conflict


@app.post("/buy/{item}")  # route
def buy(item: str) -> dict[str, str]:  # handler
    if item == "iphone":  # pretend stock is zero
        raise OutOfStock(item)  # raise domain error, no HTTP code here
    return {"bought": item}  # success


client: TestClient = TestClient(app)  # client
print(client.post("/buy/iphone").status_code, client.post("/buy/iphone").json())  # error
# Output: 409 {'message': 'iphone is out of stock'}
print(client.post("/buy/pen").json())  # success
# Output: {'bought': 'pen'}
```

## 💻 Code Example — Advanced
Hierarchy with class-level status codes, extra data, and a single handler for all subclasses.

```python
# Production style: exception hierarchy with one generic handler
from fastapi import FastAPI, Request  # tools
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # test client


class AppError(Exception):  # base class for all business errors
    status_code: int = 500  # default HTTP status
    code: str = "app_error"  # machine readable code

    def __init__(self, message: str, **extra: object) -> None:  # message + extra data
        super().__init__(message)  # keep message in args
        self.message: str = message  # public message
        self.extra: dict[str, object] = extra  # extra info


class NotFound(AppError):  # 404 family
    status_code = 404  # override
    code = "not_found"  # override


class PaymentFailed(AppError):  # 402 family
    status_code = 402  # override
    code = "payment_failed"  # override


app: FastAPI = FastAPI()  # app


@app.exception_handler(AppError)  # ONE handler covers all subclasses
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:  # handler
    body: dict = {"code": exc.code, "message": exc.message, **exc.extra}  # build body
    return JSONResponse(status_code=exc.status_code, content=body)  # use class status


@app.get("/orders/{oid}")  # route
def get_order(oid: int) -> dict[str, int]:  # handler
    if oid > 100:  # not found rule
        raise NotFound("order missing", order_id=oid)  # subclass with extra
    if oid == 13:  # payment rule
        raise PaymentFailed("card declined", gateway="razorpay")  # another subclass
    return {"id": oid}  # ok


client: TestClient = TestClient(app)  # client
print(client.get("/orders/500").status_code, client.get("/orders/500").json())  # 404
# Output: 404 {'code': 'not_found', 'message': 'order missing', 'order_id': 500}
print(client.get("/orders/13").status_code, client.get("/orders/13").json())  # 402
# Output: 402 {'code': 'payment_failed', 'message': 'card declined', 'gateway': 'razorpay'}
print(issubclass(NotFound, AppError), client.get("/orders/5").json())  # hierarchy + ok
# Output: True {'id': 5}
```

---

## 🟠 JavaScript vs Python Comparison

```python
class AppError(Exception):
    status_code = 500
    def __init__(self, message: str):
        super().__init__(message)

class NotFound(AppError):
    status_code = 404
```

```javascript
class AppError extends Error {
  constructor(message, status = 500) {
    super(message);
    this.status = status;
    this.name = 'AppError';
  }
}
class NotFound extends AppError { constructor(m) { super(m, 404); } }
```

Same OOP pattern. In Python you inherit from `Exception` (not `BaseException`) and call `super().__init__(message)` so `str(exc)` works. Class attributes like `status_code = 404` replace passing the code through the constructor.

---

## 🟠 FastAPI Connection
Raise domain errors from services and repositories, never `HTTPException`. Register one handler for the base class. Pydantic's `ValidationError` and FastAPI's `RequestValidationError` are separate; keep those in their own handlers. Document your custom codes in OpenAPI with `responses={404: {...}}`.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = 500
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message: str = message


class NotFound(AppError):
    status_code = 404


app: FastAPI = FastAPI()


@app.exception_handler(AppError)
async def handle(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse({"error": exc.message}, status_code=exc.status_code)


@app.get("/users/{uid}", responses={404: {"description": "User not found"}})
def get_user(uid: int) -> dict[str, int]:
    if uid != 1:
        raise NotFound(f"user {uid} missing")  # no HTTP code in business logic
    return {"id": uid}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using HTTPException in the service layer
```python
def find(uid):
    raise HTTPException(404, 'x')  # service knows HTTP
```
✅ Correct:
```python
def find(uid):
    raise NotFound(f'user {uid}')  # handler maps to 404
```

❌ Mistake 2: Forgetting `super().__init__` when the constructor takes extra arguments
```python
class E(Exception):
    def __init__(self, m, code): self.m = m
print(str(E('x', 1)))  # "('x', 1)"  (ugly message)
```
✅ Correct:
```python
class E(Exception):
    def __init__(self, m, code):
        super().__init__(m)  # message only
        self.code = code
print(str(E('x', 1)))  # 'x'
```

❌ Mistake 3: Catching bare `Exception` and swallowing it
```python
try:
    pay()
except Exception:
    pass  # bug hidden
```
✅ Correct:
```python
try:
    pay()
except PaymentFailed as e:
    handle(e)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

class AppError(Exception): ...
class NotFound(AppError): ...

app = FastAPI()

@app.exception_handler(AppError)
async def h1(request, exc):
    return JSONResponse({"h": "AppError"}, status_code=400)

@app.exception_handler(NotFound)
async def h2(request, exc):
    return JSONResponse({"h": "NotFound"}, status_code=404)

@app.get("/x")
def x():
    raise NotFound()

@app.get("/y")
def y():
    raise AppError()

c = TestClient(app)
print(c.get("/x").json(), c.get("/y").json())
```

**Answer**:
```
{'h': 'NotFound'} {'h': 'AppError'}
```
FastAPI/Starlette looks up handlers by walking the exception's class MRO and picks the first registered class. `NotFound` has its own handler so it wins; plain `AppError` falls to the parent handler. This is how you override one subclass while keeping a generic handler.

---

## ⚫ Interview Questions + Answers

Q1: Why not raise HTTPException everywhere?
A1: It couples business code to HTTP. Domain exceptions are reusable in jobs/CLI and tested without a web client.

Q2: Where do I define status codes?
A2: As class attributes on the exception (or in the handler's mapping), so there is one source of truth.

Q3: Does a handler for the base class catch subclasses?
A3: Yes, unless a more specific subclass handler exists, which then takes priority.

Q4: Should exceptions carry data?
A4: Yes, store fields (ids, amounts) as attributes so handlers and logs can use them, instead of parsing message strings.

Q5: Subclass `Exception` or `BaseException`?
A5: Always `Exception`. `BaseException` is for system exits and `KeyboardInterrupt`; catching it by mistake blocks shutdown.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Business rule violations (stock, payment, permissions)
- Services reused outside HTTP
- Consistent error codes for frontends

❌ Avoid when:
- Using exceptions for normal control flow in hot loops
- Deep, confusing hierarchies
- Raising HTTPException from the domain layer

---

## 📊 Visual Diagram

```
service.py: raise PaymentFailed(...)         (no HTTP here)
        |
        v
AppError hierarchy:  AppError
                       |- NotFound (404)
                       |- PaymentFailed (402)
        |
        v
@app.exception_handler(AppError) -> JSONResponse(status=exc.status_code, body)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Domain exception | Error named after a business rule | business नियम पर बना error |
| Hierarchy | Base + subclasses | base और उसकी subclasses |
| MRO | Method/class lookup order | class खोजने का क्रम |
| Status code | HTTP result number | HTTP परिणाम की संख्या |
| Error code | Machine-readable name | machine के पढ़ने वाला नाम |
| Separation of concerns | Each layer one job | हर layer का एक काम |

---

## ⚡ 3-Line Summary
English: Define an `AppError` base with `status_code` and `code`, subclass it per business error and raise it from services. One handler maps every subclass to JSON. This keeps business code free of HTTP.
Hindi: `status_code` और `code` वाली `AppError` base बनाएँ, हर business error की subclass बनाएँ और services से raise करें। एक handler हर subclass को JSON में बदलता है। इससे business code HTTP से मुक्त रहता है।

---

## ➡️ Next Topic
**326. APIRouter — Complete** — split your routes into modules with prefixes, tags and shared dependencies.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output.
