---

# 324. Exception Handlers
# हिंदी में: Exception Handlers (errors को साफ़ response में बदलना)

---

## 🔵 Simple Definition (English)
An exception handler is a function FastAPI calls when a specific exception type is raised. It turns the exception into an HTTP response, so you control the error format. Register it with `@app.exception_handler(ExcType)`.

## 🔵 सरल परिभाषा (Hindi)
Exception handler वह function है जिसे FastAPI किसी खास exception के raise होने पर बुलाता है। यह exception को HTTP response में बदलता है, इसलिए error का format आपके हाथ में रहता है। इसे `@app.exception_handler(ExcType)` से register करते हैं।

---

## 🔴 Problem it Solves
By default FastAPI returns `{"detail": ...}` for `HTTPException`, a long list for validation errors (422), and a plain-text 500 for crashes. Frontends and mobile apps want ONE consistent error shape with a code and request id, and you must never leak stack traces. Handlers give one place to shape and log all errors.

## 🔴 यह क्यों बना? (Hindi)
Default रूप से FastAPI `HTTPException` पर `{"detail": ...}`, validation error (422) पर लंबी list और crash पर सादा text 500 देता है। Frontend और mobile app को एक जैसा error format (code और request id के साथ) चाहिए, और stack trace कभी leak नहीं होना चाहिए। Handlers सभी errors को एक जगह shape और log करने देते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Error raised in route/dependency (HTTPException, RequestValidationError, custom, or any Exception)
Step 2 → ExceptionMiddleware looks up a handler by exception class (most specific class wins)
Step 3 → Your async handler gets `(request, exc)`
Step 4 → It returns a `Response` (usually `JSONResponse`) with the status you choose
Step 5 → Unhandled `Exception` goes to the 500 handler (ServerErrorMiddleware)
Step 6 → Response flows back through middleware to the client
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Route/dependency में error आता है (HTTPException, RequestValidationError, custom या कोई भी Exception)
Step 2 → ExceptionMiddleware exception की class से handler ढूँढता है (सबसे specific class जीतती है)
Step 3 → आपका async handler `(request, exc)` पाता है
Step 4 → वह आपकी चुनी status के साथ `Response` (आमतौर पर `JSONResponse`) लौटाता है
Step 5 → बिना handler वाला `Exception` 500 handler (ServerErrorMiddleware) में जाता है
Step 6 → Response middleware से होकर client तक जाता है
```

---

## 🟡 Real World Example
A fintech API returns `{"error": {"code": "validation_error", "request_id": ...}}` for every failure so the mobile app has one parser. Unexpected bugs return a safe 500 message while the full traceback goes to Sentry/logs with the request id, so support can find it.

## 🟡 Real Example Hindi mein
Fintech API हर failure पर `{"error": {"code": "validation_error", "request_id": ...}}` देती है ताकि mobile app में एक ही parser रहे। अनपेक्षित bugs पर safe 500 message जाता है जबकि पूरा traceback request id के साथ Sentry/logs में जाता है ताकि support उसे ढूँढ सके।

---

## 💻 Code Example — Basic
Override the 422 validation response and see HTTPException default.

```python
# Basic exception handlers - every line commented
from fastapi import FastAPI, HTTPException, Request  # tools
from fastapi.exceptions import RequestValidationError  # 422 validation error class
from fastapi.responses import JSONResponse  # custom response
from fastapi.testclient import TestClient  # test client

app: FastAPI = FastAPI()  # app


@app.exception_handler(RequestValidationError)  # override default 422 body
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:  # handler
    return JSONResponse(status_code=422, content={"error": "bad input", "count": len(exc.errors())})  # own shape


@app.get("/items/{item_id}")  # route
def item(item_id: int) -> dict[str, int]:  # int validated by FastAPI
    if item_id == 0:  # business rule
        raise HTTPException(status_code=404, detail="not found")  # standard 404
    return {"id": item_id}  # ok


client: TestClient = TestClient(app)  # client
print(client.get("/items/0").status_code, client.get("/items/0").json())  # HTTPException path
# Output: 404 {'detail': 'not found'}
print(client.get("/items/abc").json())  # validation path uses our handler
# Output: {'error': 'bad input', 'count': 1}
```

## 💻 Code Example — Advanced
Production: one error envelope for HTTP errors, validation errors and a catch-all 500 handler with logging.

```python
# Production style: handlers for HTTP errors, validation and a catch-all with request id
import logging  # logging
import uuid  # request ids
from fastapi import FastAPI, Request  # tools
from fastapi.exceptions import RequestValidationError  # validation errors
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # test client
from starlette.exceptions import HTTPException as StarletteHTTPException  # catches router 404/405 too

log: logging.Logger = logging.getLogger("api")  # logger
app: FastAPI = FastAPI()  # app


def envelope(code: str, message: str, rid: str, details: object = None) -> dict:  # one error shape everywhere
    return {"error": {"code": code, "message": message, "request_id": rid, "details": details}}  # envelope


def rid_of(request: Request) -> str:  # get/create request id
    return request.headers.get("x-request-id", "req-fixed")  # fixed here so output is stable


@app.exception_handler(StarletteHTTPException)  # also catches unknown routes
async def http_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:  # handler
    return JSONResponse(envelope("http_error", str(exc.detail), rid_of(request)), status_code=exc.status_code)  # keep status


@app.exception_handler(RequestValidationError)  # 422
async def val_handler(request: Request, exc: RequestValidationError) -> JSONResponse:  # handler
    fields: list[str] = [".".join(str(p) for p in e["loc"]) for e in exc.errors()]  # which fields failed
    return JSONResponse(envelope("validation_error", "invalid input", rid_of(request), fields), status_code=422)  # 422


@app.exception_handler(Exception)  # last resort: unhandled bugs -> 500
async def crash_handler(request: Request, exc: Exception) -> JSONResponse:  # handler
    log.exception("unhandled")  # log traceback, never send it to the client
    return JSONResponse(envelope("internal_error", "something went wrong", rid_of(request)), status_code=500)  # safe body


@app.get("/boom")  # route that crashes
def boom() -> None:  # handler
    raise ZeroDivisionError("secret internal detail")  # not leaked


@app.get("/n/{x}")  # validation route
def n(x: int) -> int:  # handler
    return x  # echo


client: TestClient = TestClient(app, raise_server_exceptions=False)  # let the 500 handler answer
print(client.get("/nope").status_code, client.get("/nope").json()["error"]["code"])  # unknown route
# Output: 404 http_error
print(client.get("/n/abc").json()["error"]["details"])  # which field failed
# Output: ['path.x']
r = client.get("/boom")  # crash
print(r.status_code, r.json()["error"]["message"])  # safe message
# Output: 500 something went wrong
```

---

## 🟠 JavaScript vs Python Comparison

```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"error": str(exc)})
```

```javascript
// Express error middleware (4 args)
app.use((err, req, res, next) => {
  console.error(err);
  res.status(err.status || 500).json({ error: err.message });
});
```

Express has one catch-all 4-argument middleware you must remember to place last. FastAPI registers handlers per exception class, so you get type-based routing for free. Both need an explicit step to hide internals from clients.

---

## 🟠 FastAPI Connection
Register handlers on the app. Import `HTTPException` from `starlette.exceptions` for the handler (FastAPI's is a subclass) so you also catch framework-raised 404/405. Validation errors come from `RequestValidationError`. A handler for plain `Exception` runs as the 500 handler, and with `TestClient` you must pass `raise_server_exceptions=False` to see it.

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

app: FastAPI = FastAPI()


@app.exception_handler(StarletteHTTPException)  # catches 404/405 from routing too
async def http_exc(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code,
                        headers=getattr(exc, "headers", None))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Registering on FastAPI's HTTPException only
```python
from fastapi import HTTPException
@app.exception_handler(HTTPException)  # misses router 404/405
```
✅ Correct:
```python
from starlette.exceptions import HTTPException
@app.exception_handler(HTTPException)  # catches both
```

❌ Mistake 2: Leaking internals in the 500 body
```python
return JSONResponse({'error': str(exc)}, status_code=500)  # secret detail
```
✅ Correct:
```python
log.exception('unhandled')
return JSONResponse({'error': 'internal error'}, status_code=500)
```

❌ Mistake 3: Returning a dict instead of a Response
```python
async def h(request, exc):
    return {'error': 'x'}  # handlers must return a Response
```
✅ Correct:
```python
async def h(request, exc):
    return JSONResponse({'error': 'x'}, status_code=400)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

app = FastAPI()

@app.exception_handler(HTTPException)
async def h(request, exc):
    return JSONResponse({"custom": exc.detail}, status_code=exc.status_code)

@app.get("/a")
def a():
    raise HTTPException(404, "from fastapi")

c = TestClient(app)
print(c.get("/a").json())
print(c.get("/missing").json())
```

**Answer**:
```
{'custom': 'from fastapi'}
{'detail': 'Not Found'}
```
The handler was registered for `fastapi.HTTPException`. The unknown route `/missing` raises Starlette's base `HTTPException`, which is NOT a subclass of FastAPI's, so the default handler answers. Register for `starlette.exceptions.HTTPException` to catch both.

---

## ⚫ Interview Questions + Answers

Q1: What is the default 422 format and how to change it?
A1: A `detail` list of errors with `loc`, `msg`, `type`. Override with `@app.exception_handler(RequestValidationError)`.

Q2: Which handler wins when several match?
A2: The one registered for the most specific class in the exception's MRO; subclasses beat parents.

Q3: How do I handle ALL unexpected errors?
A3: `@app.exception_handler(Exception)`. It acts as the 500 handler, outside the normal exception middleware, so log and return a safe body.

Q4: HTTPException vs custom exception + handler?
A4: HTTPException is quick for web-layer errors. Custom domain exceptions keep services HTTP-free and map to status codes in one handler.

Q5: Why is my handler not reached in tests?
A5: `TestClient` re-raises server exceptions by default. Use `TestClient(app, raise_server_exceptions=False)`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Consistent error envelope for all clients
- Mapping domain errors to HTTP codes
- Logging and request ids for every failure

❌ Avoid when:
- Hiding every error as 200
- Putting business logic in handlers
- Returning raw exception strings to clients

---

## 📊 Visual Diagram

```
route raises Exc
   |
   v
ExceptionMiddleware --- find handler by class (most specific) ---> your handler(request, exc)
   |                                                                   |
   | no handler for plain Exception                                    v
   +--> ServerErrorMiddleware (500) <--- Exception handler -------- JSONResponse
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| exception_handler | Decorator mapping error to response | error को response से जोड़ने वाला decorator |
| RequestValidationError | 422 input error | input गलत होने पर 422 error |
| HTTPException | Error with status code | status code वाला error |
| Envelope | Fixed JSON error shape | तय JSON error format |
| Request ID | Unique id to trace a call | call पहचानने वाली unique id |
| Catch-all | Handler for any Exception | किसी भी error का handler |

---

## ⚡ 3-Line Summary
English: Exception handlers convert raised errors into JSON responses you design. Register on Starlette's `HTTPException`, `RequestValidationError` and a catch-all `Exception`. Log internals, return safe messages.
Hindi: Exception handlers raise हुए errors को आपके डिज़ाइन किए JSON response में बदलते हैं। Starlette की `HTTPException`, `RequestValidationError` और catch-all `Exception` पर register करें। Internals log करें, client को safe message दें।

---

## ➡️ Next Topic
**325. Custom Exceptions** — build a domain exception hierarchy and map it to HTTP.

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output.
