---

# 017. FastAPI Middleware
# हिंदी में: FastAPI Middleware

---

## 🔵 Simple Definition (English)
Middleware is code that wraps every request and response. It runs before your route (to read or change the request) and after it (to read or change the response). In AI apps it adds request ids, timing, logging, CORS, auth checks, size limits and metrics in one place.

## 🔵 सरल परिभाषा (Hindi)
Middleware ऐसा code है जो हर request और response को लपेटता है। यह route से पहले (request पढ़ने या बदलने के लिए) और बाद में (response पढ़ने या बदलने के लिए) चलता है। AI apps में यह request id, timing, logging, CORS, auth checks, size limits और metrics एक ही जगह जोड़ता है।

---

## 🔴 Problem it Solves
Copy-pasting "log the time, add a request id, check the key, set CORS headers" into every route is repetitive and easy to forget. One missed check is a security hole or missing trace. Middleware applies cross-cutting behaviour to all routes automatically, including routes you add later.

## 🔴 यह क्यों बना? (Hindi)
हर route में "समय log करो, request id जोड़ो, key check करो, CORS headers लगाओ" copy-paste करना दोहराव वाला है और भूलना आसान है। एक छूटा check security hole या missing trace बन जाता है। Middleware cross-cutting behaviour सभी routes पर अपने आप लगाता है, बाद में जोड़े गए routes पर भी।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Register: app.add_middleware(SomeMiddleware) or @app.middleware("http")
Step 2 → Request enters the outermost middleware first (last added runs first)
Step 3 → Middleware does "before" work (start timer, read headers, check limits)
Step 4 → `response = await call_next(request)` passes control inward to the next layer / route
Step 5 → Route runs and returns a response; it travels back outward
Step 6 → Middleware does "after" work (add headers, log duration, record metrics)
Step 7 → Final response goes to the client; short-circuit is possible by returning a response early
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Register: app.add_middleware(SomeMiddleware) या @app.middleware("http")
Step 2 → Request सबसे बाहरी middleware में पहले जाती है (आख़िर में जोड़ा हुआ पहले चलता है)
Step 3 → Middleware "before" काम करता है (timer शुरू, headers पढ़ना, limits जाँचना)
Step 4 → `response = await call_next(request)` control अंदर की layer / route को देता है
Step 5 → Route चलकर response देता है; वह वापस बाहर की ओर जाता है
Step 6 → Middleware "after" काम करता है (headers जोड़ना, duration log, metrics)
Step 7 → अंतिम response client को; चाहें तो response जल्दी लौटाकर short-circuit कर सकते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: Middleware stack: (1) request-id + structured logging, (2) body-size limit (reject over 100 KB before any parsing, protecting token cost), (3) API-key auth for `/v1/*`, (4) timing header `X-Process-Time`, (5) CORS for the customs web app, (6) gzip for large batch responses (but not for streaming).

**Zomato AI**: Middleware attaches the city and user tier to the request so every route can use them, and records latency per route for dashboards.

## 🟡 Real Example Hindi mein
**Tariff System**: Middleware stack: (1) request-id + structured logging, (2) body-size limit (100 KB से बड़ा parse से पहले reject, token cost की रक्षा), (3) `/v1/*` के लिए API-key auth, (4) `X-Process-Time` timing header, (5) customs web app के लिए CORS, (6) बड़े batch responses के लिए gzip (streaming के लिए नहीं)।

**Zomato AI**: Middleware request पर city और user tier जोड़ता है ताकि हर route उन्हें use कर सके, और dashboards के लिए प्रति route latency record करता है।

---

## 💻 Code Example — Basic
```python
# Basic middleware - needs fastapi + httpx
import time  # timing

from fastapi import FastAPI, Request  # tools
from fastapi.testclient import TestClient  # tests

app = FastAPI()  # app


@app.middleware("http")  # function-style middleware
async def timing(request: Request, call_next):  # wraps every request
    start = time.perf_counter()  # before: start the clock
    response = await call_next(request)  # run the route (and inner middleware)
    elapsed_ms = (time.perf_counter() - start) * 1000  # after: compute duration
    response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.1f}"  # add header
    return response  # send to client


@app.get("/ping")  # route
async def ping() -> dict[str, str]:  # handler
    return {"pong": "ok"}  # response


r = TestClient(app).get("/ping")  # call it
print(r.json(), r.headers["X-Process-Time-ms"])  # {'pong': 'ok'} and a small number
```

## 💻 Code Example — Advanced
```python
# Production middleware: pure ASGI request-id + logging (safe for streaming), body size limit,
# API-key auth with public paths, CORS, error-safe logging, and a short-circuit response.
import json  # log lines
import logging  # logger
import time  # timing
import uuid  # request ids

from fastapi import FastAPI  # app
from fastapi.middleware.cors import CORSMiddleware  # CORS
from fastapi.testclient import TestClient  # tests
from starlette.datastructures import Headers, MutableHeaders  # header helpers
from starlette.responses import JSONResponse  # early responses
from starlette.types import ASGIApp, Message, Receive, Scope, Send  # ASGI types

log = logging.getLogger("access")  # access logger
logging.basicConfig(level=logging.INFO, format="%(message)s")  # print to console


class RequestContextMiddleware:  # pure ASGI: does not buffer streaming bodies like BaseHTTPMiddleware may
    def __init__(self, app: ASGIApp) -> None:  # receives next app
        self.app = app  # store

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # ASGI entry
        if scope["type"] != "http":  # ignore websockets/lifespan
            await self.app(scope, receive, send)  # pass through
            return  # done
        request_id = Headers(scope=scope).get("x-request-id") or uuid.uuid4().hex[:8]  # reuse or create
        scope.setdefault("state", {})["request_id"] = request_id  # available as request.state.request_id
        start = time.perf_counter()  # timer
        status = {"code": 500}  # captured status (default if crash)

        async def send_wrapper(message: Message) -> None:  # intercept outgoing messages
            if message["type"] == "http.response.start":  # headers are being sent
                status["code"] = message["status"]  # remember status
                headers = MutableHeaders(scope=message)  # mutable view
                headers["X-Request-ID"] = request_id  # echo id
            await send(message)  # forward

        try:  # ensure we log even on crash
            await self.app(scope, receive, send_wrapper)  # run inner app
        finally:  # always log
            log.info(json.dumps({"id": request_id, "path": scope["path"], "status": status["code"],
                                 "ms": round((time.perf_counter() - start) * 1000, 1)}))  # structured log


class BodyLimitMiddleware:  # reject huge bodies early (protects tokens and memory)
    def __init__(self, app: ASGIApp, max_bytes: int = 100_000) -> None:  # config
        self.app, self.max_bytes = app, max_bytes  # store

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # ASGI
        if scope["type"] == "http":  # only http
            length = Headers(scope=scope).get("content-length")  # declared size
            if length and int(length) > self.max_bytes:  # too big
                await JSONResponse({"error": "payload_too_large"}, status_code=413)(scope, receive, send)  # short-circuit
                return  # route never runs
        await self.app(scope, receive, send)  # continue


class ApiKeyMiddleware:  # simple auth for /v1 paths
    def __init__(self, app: ASGIApp, valid_keys: set[str]) -> None:  # config
        self.app, self.valid_keys = app, valid_keys  # store

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # ASGI
        if scope["type"] == "http" and scope["path"].startswith("/v1"):  # protected area
            if Headers(scope=scope).get("x-api-key") not in self.valid_keys:  # missing/invalid
                await JSONResponse({"error": "unauthorized"}, status_code=401)(scope, receive, send)  # reject
                return  # stop
        await self.app(scope, receive, send)  # continue


app = FastAPI()  # app
# Order matters: the LAST added runs FIRST. Request flow: Context -> CORS -> BodyLimit -> ApiKey -> route
app.add_middleware(ApiKeyMiddleware, valid_keys={"secret"})  # innermost
app.add_middleware(BodyLimitMiddleware, max_bytes=1000)  # next
app.add_middleware(CORSMiddleware, allow_origins=["https://customs.example.com"], allow_methods=["GET", "POST"],
                   allow_headers=["x-api-key", "content-type"])  # browsers from this origin only
app.add_middleware(RequestContextMiddleware)  # outermost: sees everything, including rejections


@app.post("/v1/classify")  # protected route
async def classify(payload: dict) -> dict[str, str]:  # handler
    return {"hs_code": "8517.13"}  # fake


if __name__ == "__main__":  # demo
    c = TestClient(app)  # client
    print(c.post("/v1/classify", json={"d": "x"}).status_code)  # 401 (no key)
    print(c.post("/v1/classify", json={"d": "x"}, headers={"x-api-key": "secret"}).json())  # 200
    print(c.post("/v1/classify", json={"d": "x" * 5000}, headers={"x-api-key": "secret"}).status_code)  # 413
```

---

## 🟠 FastAPI Integration
FastAPI includes `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `HTTPSRedirectMiddleware`. Use `@app.middleware("http")` for quick things, and pure ASGI middleware when you handle streaming (SSE) or need maximum performance. For logic that only some routes need (auth, per-user budgets), prefer dependencies over middleware, because dependencies can read the parsed body and path params and show up in the OpenAPI docs.

```python
# GZip: compress responses over 1 KB (do not use on SSE streams)
from fastapi import FastAPI  # app
from fastapi.middleware.gzip import GZipMiddleware  # built-in

app = FastAPI()  # app
app.add_middleware(GZipMiddleware, minimum_size=1000)  # compress large JSON (batch results)
```

---

## 🔗 LangChain / LangGraph Connection
LangChain has no HTTP middleware, but it has callbacks, and `langchain.agents.middleware` style hooks in newer agent APIs, that serve a similar "wrap every model call" role (logging, token counting, guardrails). Combine them: HTTP middleware provides `request_id`; pass it into the chain config so traces link together.

```python
# Pass the request id from middleware into LangChain tracing metadata
from fastapi import FastAPI, Request  # tools
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model

app = FastAPI()  # app
chain = ChatPromptTemplate.from_template("HS code for {item}") | ChatOpenAI(model="gpt-4o-mini")  # chain


@app.get("/hs")  # route
async def hs(request: Request, item: str) -> dict[str, str]:  # handler
    rid = getattr(request.state, "request_id", "none")  # set by middleware
    msg = await chain.ainvoke({"item": item}, config={"metadata": {"request_id": rid}, "tags": ["tariff"]})  # traceable
    return {"answer": str(msg.content)}  # result
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Reading the request body inside `@app.middleware("http")` (it can break the route or buffer large bodies)
✅ Correct: check `Content-Length` header, or validate in a dependency/model.

```python
# Wrong: consumes the body stream; route may then see an empty body
@app.middleware("http")
async def mw(request, call_next):
    body = await request.body()
    return await call_next(request)
# Right: limit by header early, parse body only in the route via Pydantic
```

❌ Mistake 2: Using `BaseHTTPMiddleware`-style (`@app.middleware("http")`) with streaming responses and background tasks, which can add buffering or cancellation quirks
✅ Correct: use pure ASGI middleware for SSE routes.

```python
# Wrong: heavy logic that buffers response.body_iterator
response = await call_next(request)
body = b"".join([c async for c in response.body_iterator])   # kills streaming!
# Right: only touch headers/status, or write ASGI middleware as shown above
```

❌ Mistake 3: Wrong order or CORS placed inside auth, so preflight `OPTIONS` requests get 401. Put CORS outside auth.

---

## 🧠 Tricky Interview Question

**Q**: "You added auth middleware and the browser app now fails with CORS errors, though CORS is configured. Why?"

**Answer**: Browsers send a preflight `OPTIONS` request without your API key. If the auth middleware runs before `CORSMiddleware`, it returns 401 with no CORS headers, and the browser reports a CORS error. Also error responses from inner layers need CORS headers. Order matters: add `CORSMiddleware` so that it is outside (runs before) auth (remember the last added middleware is the outermost), or let auth skip `OPTIONS`. Confirm by checking the preflight response in the browser's network tab.

---

## ⚫ Interview Questions + Answers

Q1: What is middleware? (Easy)
A1: Code that wraps every request/response, running before and after the route, used for cross-cutting needs like logging, CORS, auth and metrics.

Q2: Middleware vs dependency? (Easy)
A2: Middleware runs for every request (even for unknown routes) and sees raw requests/responses. Dependencies run per route, can use parsed params and the body, can be overridden in tests and appear in OpenAPI. Use middleware for global concerns, dependencies for route-specific ones.

Q3: In what order do middlewares run? (Medium)
A3: Like layers of an onion: the last one added is the outermost, so it sees the request first and the response last. Plan order deliberately: request id/logging outermost, then CORS, then limits, then auth.

Q4: Why can `@app.middleware("http")` be a problem for streaming? (Medium)
A4: It is built on `BaseHTTPMiddleware`, which wraps the response in extra streaming machinery; if you read `response.body_iterator` or buffer the body you destroy streaming, and background tasks or cancellation behave in subtle ways. Pure ASGI middleware only touches headers and passes body messages through.

Q5: How would you add per-tenant rate limiting and token accounting with middleware, and what are the limits of that approach? (Hard)
A5: Middleware can identify the tenant (API key header), do an atomic Redis `INCR` for requests per minute and return 429 early. Token accounting is harder: tokens are known only after the LLM responds, inside the route, so the route (or a dependency with `yield`) should report usage; middleware can read it from `request.state.tokens_used` after `call_next` and log or record metrics. For streaming, usage is known only at the end of the stream, so record it from the generator's `finally` block, not from the middleware's return path.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Behaviour applies to all routes: logging, request ids, CORS, security headers, compression
- Early rejection of bad traffic (size limits, auth) before any cost
- Collecting latency and status metrics

❌ Avoid when:
- Logic needs the parsed body or route-specific data (use dependencies)
- You would buffer large or streaming bodies
- Heavy blocking work inside middleware (it delays every request)

---

## 📊 Visual Diagram
```
 Client
   │ request
   ▼
 ┌─ RequestContext (outermost: id, log) ───────────────────────┐
 │  ┌─ CORS ────────────────────────────────────────────────┐  │
 │  │  ┌─ BodyLimit ────────────────────────────────────┐   │  │
 │  │  │  ┌─ ApiKey (innermost) ──────────────────────┐ │   │  │
 │  │  │  │          route handler  → LLM              │ │   │  │
 │  │  │  └───────────────────────────────────────────┘ │   │  │
 │  │  └────────────────────────────────────────────────┘   │  │
 │  └───────────────────────────────────────────────────────┘  │
 └──────────────────────────────────────────────────────────────┘
   ▲ response travels back outward (headers added, duration logged)
 Short-circuit: 401 / 413 returned by an inner layer never reaches the route (0 tokens)
```

---

## 💰 Cost Impact
Middleware is one of the cheapest places to prevent waste: size limits and auth reject abusive or accidental huge requests before parsing and before any LLM call; logging per-request ids and latency makes cost anomalies traceable. Compression reduces bandwidth cost for large batch responses. Poorly written middleware that buffers bodies raises memory use. Example: rejecting 50 KB+ payloads on a 2,000-character (about 500 tokens) feature stops a malicious 1 MB prompt (about 250K tokens, roughly $0.04 per call on gpt-4o-mini input pricing and far more on larger models) from ever reaching the model.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Middleware | Wraps every request/response | हर request/response को लपेटता है |
| call_next | Pass request to the next layer | अगली layer को request देना |
| ASGI | Async server interface standard | async server का standard interface |
| CORS | Browser cross-origin rules | browser की cross-origin नीति |
| Preflight | OPTIONS check before real request | असली request से पहले OPTIONS जाँच |
| Short-circuit | Return early, skip the route | route छोड़कर जल्दी लौटना |
| Request ID | Trace id per request | हर request की trace id |
| Onion model | Layers wrap each other | layers का एक-दूसरे को लपेटना |

---

## ⚡ 3-Line Summary
English: Middleware wraps every request to add request ids, logging, CORS, size limits and auth in one place. The last added runs first, so order carefully (CORS outside auth). Use pure ASGI middleware for streaming and dependencies for route-specific logic.
Hindi: Middleware हर request को लपेटकर request id, logging, CORS, size limits और auth एक जगह जोड़ता है। आख़िर में जोड़ा हुआ पहले चलता है, इसलिए क्रम सोचकर रखो (CORS, auth के बाहर)। Streaming के लिए pure ASGI middleware और route-specific logic के लिए dependencies लो।

---

## ➡️ Next Topic
**018. FastAPI Testing** — now that the app has many layers, we test routes, dependencies and LLM logic without paying for real model calls.
