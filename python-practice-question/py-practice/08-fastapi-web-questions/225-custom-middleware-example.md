---

# Q225. Custom middleware example
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐

---

## ❓ Question
Write a FastAPI middleware that adds `X-Process-Time-Ms` and `X-Request-ID` headers to every response (reuse the client's id if sent). Then show a class-based middleware that blocks a bad `User-Agent`, and the order in which two middlewares run.

---

## 💡 Quick Concept (2 lines only)
Middleware wraps every request: code before `call_next` runs on the way in, code after it runs on the way out. Use it for logging, headers, timing, auth checks.
हिंदी: Middleware हर request के आगे-पीछे चलता है — `call_next` से पहले request, बाद में response पर काम करो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time  # for timing each request
import uuid  # for unique request ids
from fastapi import FastAPI, Request  # app + request type
from fastapi.testclient import TestClient  # in-process HTTP client

app = FastAPI()  # create the app

@app.middleware("http")  # Step 1: register a function middleware
async def add_headers(request: Request, call_next):  # call_next runs the rest of the app
    start = time.perf_counter()  # Step 2: note start time BEFORE the route
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:8]  # reuse or create id
    response = await call_next(request)  # Step 3: run route (and inner middleware)
    elapsed_ms = (time.perf_counter() - start) * 1000  # Step 4: time AFTER the route
    response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"  # add timing header
    response.headers["X-Request-ID"] = request_id  # add id header
    return response  # always return the response

@app.get("/ping")  # a simple route
async def ping() -> dict[str, str]:  # return a dict
    return {"msg": "pong"}  # JSON body

# ============================================
# TEST CASES
# ============================================
client = TestClient(app)  # build test client
r = client.get("/ping", headers={"X-Request-ID": "abc123"})  # call with our own id
print(r.status_code, r.json())  # Expected: 200 {'msg': 'pong'}
print(r.headers["x-request-id"])  # Expected: abc123
print("x-process-time-ms" in r.headers)  # Expected: True
print(client.get("/ping").headers["x-request-id"] != "abc123")  # Expected: True (new id generated)
```

---

## 🔍 Why This Works (3 lines max)
`call_next(request)` runs the rest of the app and returns the response, so we can time it and edit headers. A middleware can also return its own response early (short-circuit). The LAST middleware added is the OUTERMOST (runs first).
हिंदी: `call_next` बाकी app चलाता है; बाद में response में headers जोड़ सकते हैं। आख़िरी जोड़ा गया middleware सबसे बाहर होता है।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: class-based BaseHTTPMiddleware ----
from starlette.middleware.base import BaseHTTPMiddleware  # base class

class BlockBadAgent(BaseHTTPMiddleware):  # class-style middleware
    async def dispatch(self, request, call_next):  # same signature idea
        if request.headers.get("user-agent") == "bad-bot":  # short-circuit check
            from fastapi.responses import JSONResponse  # build own response
            return JSONResponse({"detail": "blocked"}, status_code=403)  # never reaches route
        return await call_next(request)  # otherwise continue

app2 = FastAPI()  # second app
app2.add_middleware(BlockBadAgent)  # register class middleware

@app2.get("/")  # route
async def home() -> dict[str, str]:  # handler
    return {"ok": "yes"}  # body

c2 = TestClient(app2)  # client
print(c2.get("/", headers={"user-agent": "bad-bot"}).status_code)  # Expected: 403
print(c2.get("/").json())  # Expected: {'ok': 'yes'}

# ---- Order of middleware (last added = outermost) ----
order: list[str] = []  # record call order
app3 = FastAPI()  # third app

@app3.middleware("http")  # added first -> inner
async def a(request: Request, call_next):  # middleware A
    order.append("A-in"); resp = await call_next(request); order.append("A-out"); return resp  # log in/out

@app3.middleware("http")  # added second -> outer
async def b(request: Request, call_next):  # middleware B
    order.append("B-in"); resp = await call_next(request); order.append("B-out"); return resp  # log in/out

@app3.get("/")  # route
async def r3() -> dict[str, bool]:  # handler
    order.append("route"); return {"ok": True}  # log route

TestClient(app3).get("/")  # fire request
print(order)  # Expected: ['B-in', 'A-in', 'route', 'A-out', 'B-out']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to return the response (request hangs / returns None -> 500)
@app.middleware("http")
async def bad(request, call_next):
    response = await call_next(request)
    response.headers["X-A"] = "1"
    # no return!  -> TypeError at runtime

# ❌ Wrong: blocking work inside middleware (time.sleep, requests.get) stalls the whole event loop
# ✅ Correct: always `return response`, and use async calls / asyncio.sleep / httpx.AsyncClient inside
```

---

## 🎯 Interview Tip (1 line)
Say: "Middleware = cross-cutting concerns (logging, CORS, timing); order matters, last added runs first; heavy per-route logic belongs in dependencies."

---

## 🔗 Related Questions
→ Q222 (dependency injection) | Q231 (CORS is a middleware) | Q232 (error handlers) | Q240 (lifespan)
