---

# 318. Middleware in FastAPI
# हिंदी में: FastAPI में Middleware (हर request के आगे-पीछे चलने वाला code)

---

## 🔵 Simple Definition (English)
Middleware is code that wraps every request and response. It runs before the request reaches your endpoint and again after the response is created. Typical jobs: logging, timing, request ids, CORS, compression and security headers.

## 🔵 सरल परिभाषा (Hindi)
Middleware वह code है जो हर request और response को लपेटता है। यह request के endpoint तक पहुँचने से पहले चलता है और response बनने के बाद दोबारा चलता है। आम काम: logging, timing, request id, CORS, compression और security headers।

---

## 🔴 Problem it Solves
Cross-cutting tasks apply to every route: log each call, measure latency, attach a request id, add CORS headers. Copying that into every endpoint is noisy and easy to forget. One middleware handles all routes (even routes added later) in one place.

## 🔴 यह क्यों बना? (Hindi)
कुछ काम हर route पर लागू होते हैं: हर call का log, latency नापना, request id जोड़ना, CORS headers लगाना। इन्हें हर endpoint में copy करना शोर वाला है और भूलना आसान है। एक middleware सारे routes (बाद में जुड़े routes भी) को एक जगह से संभालता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives at the app
Step 2 → Outermost middleware runs its "before" code
Step 3 → It calls call_next(request) to pass control inward
Step 4 → ...inner middleware... then routing, dependencies, endpoint
Step 5 → Response travels back out through each middleware ("after" code)
Step 6 → Last-added middleware is the OUTERMOST (first in, last out)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request app तक पहुँचती है
Step 2 → सबसे बाहर वाला middleware अपना "पहले" वाला code चलाता है
Step 3 → वह call_next(request) से control अंदर भेजता है
Step 4 → ...अंदर के middleware, फिर routing, dependencies, endpoint
Step 5 → Response हर middleware से वापस गुज़रता है ("बाद" वाला code)
Step 6 → आख़िर में जोड़ा गया middleware सबसे बाहर रहता है (पहले अंदर, आख़िर में बाहर)
```

---

## 🟡 Real World Example
A Swiggy-like API gateway service adds an `X-Request-ID` to every request so one order can be traced across logs, measures `X-Process-Time` for dashboards, enables CORS for the web app, and gzip-compresses big menu responses. An AI app logs the token usage per call in a middleware.

## 🟡 Real Example Hindi mein
Swiggy जैसी API service हर request में `X-Request-ID` जोड़ती है ताकि एक order को सारे logs में trace किया जा सके, dashboard के लिए `X-Process-Time` नापती है, web app के लिए CORS चालू करती है और बड़े menu responses को gzip से छोटा करती है। AI app middleware में हर call का token usage log करता है।

---

## 💻 Code Example — Basic
```python
# Basic middleware - run directly (pip install fastapi httpx)
import time  # for timing
from typing import Awaitable, Callable  # type for call_next
from fastapi import FastAPI, Request, Response  # core
from fastapi.testclient import TestClient  # demo client

app: FastAPI = FastAPI()  # create app


@app.middleware("http")  # register a function middleware
async def add_process_time(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:  # signature is fixed
    start: float = time.perf_counter()  # BEFORE: note the start time
    response: Response = await call_next(request)  # pass the request to the next layer and wait
    elapsed_ms: float = (time.perf_counter() - start) * 1000  # AFTER: compute duration
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.2f}"  # add a header to every response
    return response  # send it on


@app.get("/hello")  # a normal route
def hello() -> dict:  # endpoint
    return {"msg": "hi"}  # response


c: TestClient = TestClient(app)  # demo client
r = c.get("/hello")  # call
print(r.json())  # body unchanged
# Output: {'msg': 'hi'}
print("x-process-time-ms" in r.headers)  # middleware added the header
# Output: True
print(float(r.headers["x-process-time-ms"]) >= 0)  # value is a number (exact value varies)
# Output: True
print(c.get("/missing").headers["x-process-time-ms"] is not None)  # even 404s pass through the middleware
# Output: True
```

## 💻 Code Example — Advanced
```python
# Production style: request id with contextvars, error catching, order, CORS, GZip, pure-ASGI note
import uuid  # unique ids
from contextvars import ContextVar  # per-request storage that works with async
from typing import Awaitable, Callable  # type for call_next
from fastapi import FastAPI, Request, Response  # core
from fastapi.middleware.cors import CORSMiddleware  # built-in CORS
from fastapi.middleware.gzip import GZipMiddleware  # built-in compression
from fastapi.responses import JSONResponse  # custom error response
from fastapi.testclient import TestClient  # demo client

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")  # visible anywhere in this request
ORDER: list[str] = []  # records execution order
app: FastAPI = FastAPI()  # app


@app.middleware("http")  # added FIRST -> runs INNER
async def inner(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:  # inner layer
    ORDER.append("inner before")  # before
    response: Response = await call_next(request)  # next
    ORDER.append("inner after")  # after
    return response  # pass on


@app.middleware("http")  # added SECOND -> runs OUTER
async def request_context(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:  # outer layer
    ORDER.append("outer before")  # before
    rid: str = request.headers.get("x-request-id") or uuid.uuid4().hex[:8]  # reuse the caller's id or make one
    token = request_id_var.set(rid)  # store it for this request
    try:  # make sure we reset the variable
        response: Response = await call_next(request)  # run the rest
    except Exception:  # unhandled error in the app
        response = JSONResponse({"detail": "Internal error", "request_id": rid}, status_code=500)  # safe message, no traceback
    finally:  # always
        request_id_var.reset(token)  # clean up
    response.headers["X-Request-ID"] = rid  # return the id so clients can quote it
    ORDER.append("outer after")  # after
    return response  # pass on


app.add_middleware(GZipMiddleware, minimum_size=100)  # compress bodies >= 100 bytes (added last = outermost)
app.add_middleware(  # CORS for a browser frontend
    CORSMiddleware,  # class
    allow_origins=["https://app.example.com"],  # exact origins, avoid "*" with credentials
    allow_methods=["GET", "POST"],  # allowed verbs
    allow_headers=["Authorization", "Content-Type"],  # allowed request headers
    allow_credentials=True,  # allow cookies
)


@app.get("/who")  # reads the request id from the context variable
def who() -> dict:  # endpoint (no Request needed!)
    return {"request_id": request_id_var.get()}  # available because of ContextVar


@app.get("/big")  # large body to trigger gzip
def big() -> dict:  # endpoint
    return {"data": "x" * 1000}  # compressible


@app.get("/crash")  # simulate a bug
def crash() -> dict:  # endpoint
    raise RuntimeError("boom")  # unhandled


c: TestClient = TestClient(app, raise_server_exceptions=False)  # let middleware convert the error
r = c.get("/who", headers={"X-Request-ID": "abc12345"})  # send our own id
print(r.json(), r.headers["x-request-id"])  # same id everywhere
# Output: {'request_id': 'abc12345'} abc12345
print(ORDER)  # outer wraps inner
# Output: ['outer before', 'inner before', 'inner after', 'outer after']
print(c.get("/big", headers={"Accept-Encoding": "gzip"}).headers["content-encoding"])  # compressed on the wire
# Output: gzip
r = c.get("/crash", headers={"X-Request-ID": "r-9"})  # failing route
print(r.status_code, r.json())  # clean 500 with the id
# Output: 500 {'detail': 'Internal error', 'request_id': 'r-9'}
pre = c.options("/who", headers={"Origin": "https://app.example.com", "Access-Control-Request-Method": "GET"})  # CORS preflight
print(pre.status_code, pre.headers["access-control-allow-origin"])  # allowed origin
# Output: 200 https://app.example.com
bad = c.options("/who", headers={"Origin": "https://evil.com", "Access-Control-Request-Method": "GET"})  # other origin
print(bad.status_code)  # preflight refused
# Output: 400
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python (FastAPI)
@app.middleware("http")
async def log(request: Request, call_next):
    print("before", request.url.path)
    response = await call_next(request)
    print("after", response.status_code)
    return response
```
```javascript
// JavaScript (Express): next() has no return value, so "after" code uses res.on("finish")
app.use((req, res, next) => {
  console.log("before", req.path);
  res.on("finish", () => console.log("after", res.statusCode));
  next();
});
// CORS: app.use(require("cors")({ origin: "https://app.example.com", credentials: true }));
```

Key difference: in FastAPI `await call_next(request)` returns the response, so before and after code live in one function. Express middleware is order-based with `next()` and uses event hooks to see the response. In both, registration order matters; in Starlette the last added is the outermost.

---

## 🟠 FastAPI Connection
FastAPI is built on Starlette, so middleware comes from Starlette: `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `HTTPSRedirectMiddleware`. Use `@app.middleware("http")` for quick custom code. For high performance or to avoid `BaseHTTPMiddleware` limits (such as problems with `contextvars` set in endpoints, and background tasks), write a pure ASGI middleware class. Route-specific logic (auth for some routes) belongs in dependencies, not middleware.

```python
# FastAPI: a pure ASGI middleware class (fast, no BaseHTTPMiddleware overhead)
from starlette.types import ASGIApp, Receive, Scope, Send  # ASGI types
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # demo client


class SecurityHeaders:  # pure ASGI middleware
    def __init__(self, app: ASGIApp) -> None:  # receives the next app
        self.app = app  # store it

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # ASGI entry point
        if scope["type"] != "http":  # ignore websockets/lifespan
            await self.app(scope, receive, send)  # pass through
            return  # done

        async def send_wrapper(message: dict) -> None:  # intercept outgoing messages
            if message["type"] == "http.response.start":  # response headers message
                headers: list = list(message.get("headers", []))  # copy
                headers.append((b"x-content-type-options", b"nosniff"))  # add a security header
                message["headers"] = headers  # replace
            await send(message)  # forward

        await self.app(scope, receive, send_wrapper)  # call inner app with the wrapper


app: FastAPI = FastAPI()  # app
app.add_middleware(SecurityHeaders)  # register class


@app.get("/")  # route
def root() -> dict:  # endpoint
    return {"ok": True}  # response


c: TestClient = TestClient(app)  # client
print(c.get("/").headers["x-content-type-options"])  # header present
# Output: nosniff
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to return the response or to await `call_next`
```python
# Wrong - returns None, request hangs or errors
async def mw(request, call_next):
    call_next(request)

# Correct
async def mw(request, call_next):
    response = await call_next(request)
    return response
```

❌ Mistake 2: Expecting HTTPException raised in middleware to be handled like in routes
```python
# Wrong - exception handlers for routes do not wrap middleware code; this becomes a 500
raise HTTPException(401)   # inside middleware

# Correct - return a response directly
return JSONResponse({"detail": "Unauthorized"}, status_code=401)
```

❌ Mistake 3: Wrong order for CORS
```python
# Wrong - an auth middleware that rejects requests BEFORE CORS adds headers makes browsers show a confusing CORS error
# Correct - add CORSMiddleware LAST so it is outermost and decorates every response, including errors
```

---

## 🧠 Tricky Interview Question

**Q**: What is printed?

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
log = []

@app.middleware("http")
async def a(request, call_next):
    log.append("a-in")
    r = await call_next(request)
    log.append("a-out")
    return r

@app.middleware("http")
async def b(request, call_next):
    log.append("b-in")
    r = await call_next(request)
    log.append("b-out")
    return r

@app.get("/")
def root():
    log.append("route")
    return {}

TestClient(app).get("/")
print(log)
```

**Answer**:
```
['b-in', 'a-in', 'route', 'a-out', 'b-out']
```
Middleware added later wraps the earlier ones, so `b` (added last) is outermost and runs first on the way in and last on the way out. The order is the reverse of the order in the file.

---

## ⚫ Interview Questions + Answers

Q1: Middleware vs dependency?
A1: Middleware wraps every request (including 404s and static files) and sees only the raw request/response. Dependencies run per route, can use typed parameters, show in OpenAPI and can be overridden in tests. Use middleware for global concerns (CORS, timing, request ids), dependencies for auth and per-route logic.

Q2: What is `call_next`?
A2: A function that passes the request to the next layer (and finally the route) and returns the response. Everything before the `await` is the request phase, everything after is the response phase.

Q3: What are the downsides of `@app.middleware("http")`?
A3: It uses `BaseHTTPMiddleware`, which adds overhead, can break `contextvars` propagation from endpoints to the middleware, and interacts badly with some streaming and background tasks. For hot paths use a pure ASGI middleware.

Q4: How does CORS middleware work?
A4: It answers preflight `OPTIONS` requests and adds `Access-Control-Allow-*` headers to responses for allowed origins. Browsers enforce CORS, tools like curl ignore it. With `allow_credentials=True` you must list exact origins (not `*`).

Q5: Can middleware read the request body?
A5: Yes, but reading `await request.body()` in `BaseHTTPMiddleware` has historically caused trouble because the stream can be consumed once; prefer a pure ASGI middleware that replays the body, or avoid reading bodies in middleware.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Logging, metrics, request ids, tracing
- CORS, GZip, trusted hosts, HTTPS redirect, security headers
- Global error-to-response conversion as a safety net

❌ Avoid when:
- Logic only some routes need (use dependencies)
- Heavy per-request work that slows every route
- Business logic or database access (keep it in services)

---

## 📊 Visual Diagram

```
 Request ──► [CORS] ──► [Request-ID] ──► [Timing] ──► Router ──► Endpoint
                                                                    │
 Response ◄── [CORS] ◄── [Request-ID] ◄── [Timing] ◄────────────────┘

 add_middleware(A); add_middleware(B)  ==>  B is OUTER, A is INNER
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Middleware | Wrapper around all requests | सभी requests का wrapper |
| call_next | Passes request to next layer | अगली परत को request देना |
| CORS | Browser cross-origin rules | browser के दूसरे origin के नियम |
| Preflight | OPTIONS check before real request | असली request से पहले की OPTIONS जाँच |
| ASGI | Async server/app interface | async server-app interface |
| ContextVar | Per-request variable | हर request का अपना variable |
| Request ID | Unique id to trace a call | call trace करने की unique id |

---

## ⚡ 3-Line Summary
English: Middleware wraps every request and response for global tasks like logging, timing, CORS and compression. The last added middleware is outermost. Use dependencies for route-specific logic and pure ASGI middleware for performance.
Hindi: Middleware हर request और response को लपेटकर logging, timing, CORS और compression जैसे global काम करता है। आख़िर में जोड़ा गया middleware सबसे बाहर रहता है। Route-specific logic के लिए dependencies और performance के लिए pure ASGI middleware इस्तेमाल करें।

---

## ➡️ Next Topic
**319. Background Tasks** — run work after the response is sent (emails, notifications).
