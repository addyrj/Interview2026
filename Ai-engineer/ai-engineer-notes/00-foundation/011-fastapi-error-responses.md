---

# 011. FastAPI Error Responses
# हिंदी में: FastAPI Error Responses

---

## 🔵 Simple Definition (English)
An error response is the HTTP reply (status code + JSON body) sent when something goes wrong. FastAPI provides `HTTPException`, automatic 422 validation errors, and custom `exception_handler`s. Good error responses tell the client what happened and whether to retry, without leaking internals.

## 🔵 सरल परिभाषा (Hindi)
Error response वह HTTP reply (status code + JSON body) है जो कुछ गलत होने पर भेजा जाता है। FastAPI में `HTTPException`, अपने आप 422 validation errors, और custom `exception_handler` मिलते हैं। अच्छा error response client को बताता है कि क्या हुआ और retry करना है या नहीं, बिना internals leak किए।

---

## 🔴 Problem it Solves
Unhandled exceptions give a plain 500 "Internal Server Error", so clients cannot tell a bad input from a provider outage, and they retry things that will never work. AI apps have special failures: rate limits, context too long, moderation blocks, timeouts. Each needs the right status code and a stable error format.

## 🔴 यह क्यों बना? (Hindi)
Unhandled exceptions सादा 500 "Internal Server Error" देते हैं, इसलिए client गलत input और provider outage में फ़र्क नहीं कर पाता, और ऐसी चीज़ें retry करता है जो कभी नहीं चलेंगी। AI apps के खास failures हैं: rate limit, context बहुत लंबा, moderation block, timeout। हर एक को सही status code और स्थिर error format चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Inside a route you `raise HTTPException(status_code=..., detail=...)`
Step 2 → FastAPI catches it and builds a JSON reply {"detail": ...} with that status
Step 3 → Invalid request data → RequestValidationError → automatic 422 with a list of problems
Step 4 → Your own exception classes can be registered: @app.exception_handler(MyError)
Step 5 → The handler returns a JSONResponse with your standard error shape (code, message, request_id)
Step 6 → A catch-all handler for Exception returns a safe 500 and logs the stack trace
Step 7 → Use `responses={...}` in the route so Swagger documents the error cases
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Route में `raise HTTPException(status_code=..., detail=...)`
Step 2 → FastAPI इसे पकड़कर उसी status के साथ JSON {"detail": ...} बनाता है
Step 3 → गलत request data → RequestValidationError → अपने आप 422 और समस्याओं की list
Step 4 → अपनी exception classes register करो: @app.exception_handler(MyError)
Step 5 → Handler अपने standard error shape (code, message, request_id) वाला JSONResponse देता है
Step 6 → Exception का catch-all handler सुरक्षित 500 देता है और stack trace log करता है
Step 7 → Route में `responses={...}` दो ताकि Swagger error cases document करे
```

---

## 🟡 Real World Example
**Tariff Classification System**: Error map: description empty or too long → 422; user's daily token budget used up → 429 with `Retry-After`; document over the model limit → 413; LLM provider timeout → 504; provider error → 502; unknown HS code lookup → 404; any other bug → 500 with a `request_id` the client can quote to support.

**Zomato AI**: If the LLM recommender is down, the API returns 200 with a normal ranked list and a `degraded: true` flag instead of failing the whole page.

## 🟡 Real Example Hindi mein
**Tariff System**: Error map: description खाली या बहुत लंबी → 422; user का daily token budget खत्म → 429 और `Retry-After`; document model limit से बड़ा → 413; LLM provider timeout → 504; provider error → 502; अज्ञात HS code → 404; बाकी bug → 500 और `request_id` जो client support को बता सके।

**Zomato AI**: LLM recommender down हो तो API पूरा page fail करने की जगह 200 के साथ सामान्य ranked list और `degraded: true` flag देता है।

---

## 💻 Code Example — Basic
```python
# Basic error responses - needs fastapi + httpx
from fastapi import FastAPI, HTTPException  # core
from fastapi.testclient import TestClient  # tests

app = FastAPI()  # app
CODES = {"8517": "Telephones", "8471": "Computers"}  # tiny lookup table


@app.get("/codes/{hs_code}")  # route
async def get_code(hs_code: str) -> dict[str, str]:  # handler
    if hs_code not in CODES:  # unknown code
        raise HTTPException(status_code=404, detail=f"HS code {hs_code} not found")  # 404 JSON
    return {"hs_code": hs_code, "name": CODES[hs_code]}  # success


client = TestClient(app)  # client
print(client.get("/codes/8517").json())  # found
r = client.get("/codes/9999")  # missing
print(r.status_code, r.json())  # 404 {'detail': 'HS code 9999 not found'}
```

## 💻 Code Example — Advanced
```python
# Production error layer: custom exception hierarchy, consistent error shape, request id,
# validation + catch-all handlers, Retry-After, async route, no internal leaks
import logging  # server-side logs
import uuid  # request ids

from fastapi import FastAPI, Request  # core
from fastapi.exceptions import RequestValidationError  # validation error type
from fastapi.responses import JSONResponse  # response
from fastapi.testclient import TestClient  # tests
from pydantic import BaseModel, Field  # models

log = logging.getLogger("api")  # logger


class AppError(Exception):  # base for our errors
    status_code = 500  # default HTTP status
    code = "internal_error"  # machine-readable code
    retry_after: int | None = None  # seconds, optional

    def __init__(self, message: str) -> None:  # message for humans
        super().__init__(message)  # keep standard behaviour
        self.message = message  # store


class RateLimited(AppError):  # 429
    status_code, code, retry_after = 429, "rate_limited", 30  # values


class ContextTooLong(AppError):  # 413
    status_code, code = 413, "context_too_long"  # values


class ProviderDown(AppError):  # 502
    status_code, code, retry_after = 502, "provider_error", 10  # values


def error_body(request: Request, code: str, message: str, extra: dict | None = None) -> dict:  # one shape everywhere
    return {"error": {"code": code, "message": message, "request_id": getattr(request.state, "request_id", None),
                      **(extra or {})}}  # standard envelope


app = FastAPI()  # app


@app.middleware("http")  # attach a request id to every request
async def add_request_id(request: Request, call_next):  # middleware
    request.state.request_id = uuid.uuid4().hex[:8]  # short id
    response = await call_next(request)  # continue
    response.headers["X-Request-ID"] = request.state.request_id  # echo to client
    return response  # done


@app.exception_handler(AppError)  # handle all our errors
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:  # handler
    headers = {"Retry-After": str(exc.retry_after)} if exc.retry_after else {}  # tell clients when to retry
    return JSONResponse(status_code=exc.status_code, content=error_body(request, exc.code, exc.message), headers=headers)  # reply


@app.exception_handler(RequestValidationError)  # reshape 422 into our envelope
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:  # handler
    fields = [{"field": ".".join(str(p) for p in e["loc"][1:]), "problem": e["msg"]} for e in exc.errors()]  # simplify
    return JSONResponse(status_code=422, content=error_body(request, "validation_error", "Invalid input", {"fields": fields}))  # reply


@app.exception_handler(Exception)  # catch-all, last resort
async def unhandled(request: Request, exc: Exception) -> JSONResponse:  # handler
    log.exception("unhandled error")  # full stack goes to logs only
    return JSONResponse(status_code=500, content=error_body(request, "internal_error", "Something went wrong"))  # safe message


class Body(BaseModel):  # request
    description: str = Field(min_length=3, max_length=200)  # bounded


@app.post("/classify", responses={429: {"description": "Rate limited"}, 502: {"description": "Provider error"}})  # documented errors
async def classify(body: Body) -> dict[str, str]:  # handler
    if "quota" in body.description:  # simulate rate limit
        raise RateLimited("daily token budget used")  # custom error
    if "down" in body.description:  # simulate provider failure
        raise ProviderDown("LLM provider unavailable")  # custom error
    if "bug" in body.description:  # simulate programming bug
        raise ZeroDivisionError("oops secret internal detail")  # not our error type
    return {"hs_code": "8517.13"}  # success


if __name__ == "__main__":  # demo
    c = TestClient(app, raise_server_exceptions=False)  # do not re-raise inside the client so we see the 500 JSON
    for text in ["Android phone", "quota please", "provider down", "found a bug", "x"]:  # five cases
        r = c.post("/classify", json={"description": text})  # call
        print(r.status_code, r.headers.get("retry-after"), r.json())  # show status, retry header, body
```

---

## 🟠 FastAPI Integration
Register handlers once in `main.py`. Use 4xx for caller mistakes (do not retry) and 5xx for server/provider problems (retry may help). For streaming routes, errors after the first byte must be sent as a stream event because the status code is already 200.

```python
# Documenting errors in OpenAPI + using status constants
from fastapi import FastAPI, HTTPException, status  # tools

app = FastAPI()  # app


@app.get("/lookup/{code}", responses={404: {"description": "Unknown HS code"}})  # shows in /docs
async def lookup(code: str) -> dict[str, str]:  # handler
    if not code.isdigit():  # bad format
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "code must be digits")  # readable constant
    raise HTTPException(status.HTTP_404_NOT_FOUND, "unknown code")  # always 404 in this demo
```

---

## 🔗 LangChain / LangGraph Connection
LangChain raises provider exceptions (for example `openai.RateLimitError`, `openai.APITimeoutError`) and `OutputParserException` for bad model output. Catch them in the service layer and translate to your own `AppError` classes so routes return stable codes. `.with_retry()` and `.with_fallbacks()` reduce how often errors reach the client.

```python
# Translate provider errors to app errors (openai>=1)
import openai  # provider SDK exceptions


class RateLimited(Exception): ...  # our error
class ProviderDown(Exception): ...  # our error


async def safe_invoke(chain, inputs: dict) -> str:  # service function
    try:  # call LangChain chain
        return str((await chain.ainvoke(inputs)).content)  # success
    except openai.RateLimitError as exc:  # 429 from provider
        raise RateLimited("provider rate limit") from exc  # translate
    except (openai.APITimeoutError, openai.APIConnectionError) as exc:  # timeouts / network
        raise ProviderDown("provider unreachable") from exc  # translate
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning 200 with an error message in the body
✅ Correct: use the right status code.

```python
# Wrong: clients and monitoring think it worked
return {"success": False, "error": "rate limited"}
# Right
raise HTTPException(status_code=429, detail="rate limited", headers={"Retry-After": "30"})
```

❌ Mistake 2: Leaking internals (stack traces, prompts, keys) in `detail`
✅ Correct: log the details server-side; return a safe message and a request id.

```python
# Wrong
raise HTTPException(500, detail=str(exc))   # may contain SQL, file paths or API keys
# Right
log.exception("classify failed")
raise HTTPException(500, detail="Internal error, quote request_id to support")
```

❌ Mistake 3: Using 500 for everything. Distinguish 4xx (client) from 502/503/504 (upstream) so clients and alerts behave correctly.

---

## 🧠 Tricky Interview Question

**Q**: "Your streaming `/chat` endpoint raised an exception halfway through the answer, but the client saw HTTP 200 and a truncated reply. How should errors be handled?"

**Answer**: The status line and headers are sent with the first chunk, so a later exception cannot change them (and exception handlers do not apply cleanly). Handle it in the generator: catch exceptions and yield a final error event (`event: error` with a JSON payload) then end the stream, and tell the client protocol to treat that event as failure. Do pre-flight checks (auth, input size, budget) before starting the stream so most errors still produce proper 4xx codes.

---

## ⚫ Interview Questions + Answers

Q1: What status code does FastAPI return for invalid request bodies? (Easy)
A1: 422 Unprocessable Entity, with a JSON `detail` list showing the location, message and type of each error.

Q2: How do you return a 404 from a route? (Easy)
A2: `raise HTTPException(status_code=404, detail="not found")`.

Q3: When do you use 429 vs 503? (Medium)
A3: 429 means the caller is sending too many requests or exceeded quota (their fault, include `Retry-After`). 503 means your service or its dependency is temporarily unavailable (your side). Clients should back off in both cases.

Q4: How do you give all errors the same JSON shape? (Medium)
A4: Define a custom exception hierarchy and register `exception_handler`s for it, for `RequestValidationError`, for `HTTPException` (Starlette's) and for `Exception`. Each returns the same envelope `{"error": {"code", "message", "request_id"}}`.

Q5: Which errors from an LLM provider map to which HTTP codes in your API? (Hard)
A5: Provider 429 maps to your 503 or 429 depending on whether it is your global quota (503, retry later) or the user's budget (429). Provider 400 context-length error maps to 413 or 422 with an actionable message. Provider 401/403 (your key is wrong) is a server misconfiguration: return 500, alert the team, do not expose it. Provider timeout maps to 504. Provider 5xx maps to 502. Content-policy block maps to 422 or 400 with a policy code. Also set `Retry-After` and ensure retries do not double-charge by checking whether tokens were already billed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Every public API endpoint
- You call unreliable upstreams (LLMs, vector DBs)
- You need clients to react differently to different failures

❌ Avoid when:
- You hide real failures behind a friendly 200 (breaks monitoring)
- You expose stack traces in production
- You use exceptions for normal control flow in hot paths

---

## 📊 Visual Diagram
```
  request ─► validation ──fail──► 422 {error: validation_error, fields: [...]}
                │ok
                ▼
             route ──raises RateLimited──► 429 + Retry-After
                │   ──raises ContextTooLong─► 413
                │   ──raises ProviderDown───► 502
                │   ──raises bug (Exception)► 500 (safe msg, full trace in logs)
                ▼
             200 JSON

  all errors share:  {"error": {"code", "message", "request_id"}}
```

---

## 💰 Cost Impact
Correct error design saves tokens: rejecting oversized or invalid input with 413/422 before the LLM call costs 0 tokens; correct 4xx codes stop clients from blindly retrying calls that will never succeed (each blind retry of a 3,000-token prompt wastes 3,000 input tokens); `Retry-After` reduces retry storms. Returning partial answers on failure may still be billed by the provider, so count tokens in error logs. Example: if 2 percent of 100K daily requests are oversized and retried 3 times by clients, that is 6K wasted calls; a 413 on the first try avoids all of them.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HTTPException | Raise an HTTP error | HTTP error raise करना |
| 422 | Invalid input | गलत input |
| 429 | Too many requests | बहुत ज़्यादा requests |
| 502/503/504 | Upstream/unavailable/timeout | upstream/अनुपलब्ध/timeout |
| exception_handler | Function that turns exception into response | exception से response बनाने वाला |
| Retry-After | Header: when to retry | कब दोबारा try करें |
| Request ID | Unique id to trace a request | request ट्रैक करने की id |
| Envelope | Standard error JSON shape | standard error JSON रूप |

---

## ⚡ 3-Line Summary
English: Use correct status codes (422, 429, 413, 502, 504) with one consistent JSON error shape and a request id. Register handlers for your own exceptions, validation errors and a catch-all that never leaks details. Early 4xx rejections save tokens.
Hindi: सही status codes (422, 429, 413, 502, 504) के साथ एक जैसा JSON error shape और request id दो। अपनी exceptions, validation errors और catch-all के लिए handlers register करो जो details leak न करे। जल्दी 4xx reject करने से tokens बचते हैं।

---

## ➡️ Next Topic
**012. FastAPI Async Routes** — now we look at how `async def` routes behave under load and how to avoid blocking the event loop.
