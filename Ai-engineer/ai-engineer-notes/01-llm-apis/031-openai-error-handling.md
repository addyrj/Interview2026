---

# 031. OpenAI API — Error Handling
# हिंदी में: OpenAI API — Error Handling

---

## 🔵 Simple Definition (English)
Error handling means catching the exceptions the OpenAI SDK raises (rate limit, timeout, bad request, authentication, server errors) and reacting correctly: retry the temporary ones, fix or report the permanent ones, and never crash the user's request. The SDK has typed exceptions that map to HTTP status codes.

## 🔵 सरल परिभाषा (Hindi)
Error handling का मतलब है OpenAI SDK जो exceptions raise करता है (rate limit, timeout, bad request, authentication, server errors) उन्हें पकड़ना और सही प्रतिक्रिया देना: temporary errors को retry करना, permanent errors को fix या report करना, और user की request को crash न होने देना। SDK में typed exceptions हैं जो HTTP status codes से जुड़ी हैं।

---

## 🔴 Problem it Solves
Network calls fail. OpenAI can return 429 (too many requests), 500/503 (server trouble), 400 (your request is invalid), 401 (bad key), or a timeout. If you treat all errors the same you either retry things that can never succeed (wasting money) or give up on things that would succeed in one second (bad uptime).

## 🔴 यह क्यों बना? (Hindi)
Network calls fail होती हैं। OpenAI 429 (बहुत ज़्यादा requests), 500/503 (server problem), 400 (आपकी request गलत), 401 (गलत key) या timeout दे सकता है। सब errors को एक जैसा मानो तो या तो ऐसी चीज़ें retry होती हैं जो कभी सफल नहीं होंगी (पैसा बर्बाद), या वो चीज़ें छोड़ दी जाती हैं जो एक सेकंड में चल जातीं (खराब uptime)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Wrap the call in try/except
Step 2 → Catch the most specific exceptions first, base classes last
Step 3 → Classify each error: retryable or permanent
Step 4 → Retryable: APIConnectionError, APITimeoutError, RateLimitError (429), InternalServerError (5xx)
Step 5 → Permanent: BadRequestError (400), AuthenticationError (401), PermissionDeniedError (403), NotFoundError (404)
Step 6 → Retry with exponential backoff + jitter (limited attempts)
Step 7 → On permanent error: log, alert, return a clear message to the caller
Step 8 → Always log request id (exc.request_id) to share with OpenAI support
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Call को try/except में रखो
Step 2 → पहले specific exceptions पकड़ो, base classes आख़िर में
Step 3 → हर error को classify करो: retryable या permanent
Step 4 → Retryable: APIConnectionError, APITimeoutError, RateLimitError (429), InternalServerError (5xx)
Step 5 → Permanent: BadRequestError (400), AuthenticationError (401), PermissionDeniedError (403), NotFoundError (404)
Step 6 → Exponential backoff + jitter से retry करो (सीमित attempts)
Step 7 → Permanent error पर: log, alert, caller को साफ़ message दो
Step 8 → Request id (exc.request_id) हमेशा log करो ताकि OpenAI support को दे सको
```

---

## 🟡 Real World Example
**Tariff Classification System**: During month-end, brokers submit thousands of classifications.
- 429: slow down and retry later.
- 400 `context_length_exceeded`: do not retry; chunk the document or switch to RAG.
- 401: page the on-call engineer; the key is wrong or revoked.
- 503: retry, then fall back to a second model/provider so customs filings are not blocked.

**Zomato AI**: If the LLM is down, the app falls back to a normal keyword search instead of showing an error.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: Month-end पर brokers हज़ारों classifications भेजते हैं।
- 429: धीमे हो जाओ और बाद में retry करो।
- 400 `context_length_exceeded`: retry मत करो; document chunk करो या RAG पर जाओ।
- 401: on-call engineer को बुलाओ; key गलत या revoke है।
- 503: retry करो, फिर दूसरे model/provider पर fallback ताकि customs filings न रुकें।

**Zomato AI**: LLM down हो तो app error दिखाने की जगह normal keyword search पर चला जाता है।

---

## 💻 Code Example — Basic
```python
# Basic error handling with typed exceptions (needs OPENAI_API_KEY)
import openai                                    # import module to reach exception classes
from openai import OpenAI                        # sync client

client = OpenAI(max_retries=0)                   # turn off SDK retries so we see errors directly

try:
    r = client.chat.completions.create(
        model="gpt-4o-mini",                     # model name
        messages=[{"role": "user", "content": "HS code for power bank?"}],
        max_tokens=30,                           # small output
        timeout=20,                              # per-request timeout in seconds
    )
    print(r.choices[0].message.content)          # success path
except openai.AuthenticationError:               # 401: bad or missing key
    print("Check OPENAI_API_KEY")
except openai.RateLimitError:                    # 429: too many requests or quota
    print("Rate limited - retry later")
except openai.BadRequestError as e:              # 400: our request is invalid
    print("Fix the request:", e.message)
except openai.APITimeoutError:                   # request took too long
    print("Timed out")
except openai.APIConnectionError:                # network problem
    print("Network issue")
except openai.APIStatusError as e:               # any other HTTP error (5xx etc.)
    print("HTTP", e.status_code, e.request_id)  # request id helps support
```

## 💻 Code Example — Advanced
```python
# Production: classify errors, map to app-level results, sync + async
import asyncio                                           # async runner
import logging                                           # logs
from dataclasses import dataclass                        # result container
from typing import Optional                              # optional type

import openai                                            # exception classes
from openai import AsyncOpenAI                           # async client

logger = logging.getLogger(__name__)                     # logger
client = AsyncOpenAI(timeout=30.0, max_retries=0)        # we control retries ourselves


@dataclass
class LLMOutcome:
    ok: bool                                             # success flag
    text: Optional[str] = None                           # answer if ok
    error_kind: Optional[str] = None                     # "retryable" | "permanent"
    detail: Optional[str] = None                         # message for logs/users


RETRYABLE = (
    openai.APIConnectionError,                           # includes APITimeoutError
    openai.RateLimitError,                               # 429
    openai.InternalServerError,                          # 5xx
)


def classify(exc: Exception) -> str:
    # Order matters only for readability here; tuple isinstance handles subclasses
    return "retryable" if isinstance(exc, RETRYABLE) else "permanent"


async def safe_chat(prompt: str, attempts: int = 3) -> LLMOutcome:
    for attempt in range(1, attempts + 1):                       # bounded retries
        try:
            r = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
            return LLMOutcome(ok=True, text=r.choices[0].message.content)
        except openai.APIError as exc:                           # base class for SDK errors
            kind = classify(exc)                                 # decide strategy
            rid = getattr(exc, "request_id", None)               # for support tickets
            logger.warning("attempt %d failed (%s) req=%s: %s", attempt, kind, rid, exc)
            if kind == "permanent" or attempt == attempts:       # stop retrying
                return LLMOutcome(ok=False, error_kind=kind, detail=str(exc))
            await asyncio.sleep(2 ** attempt * 0.5)              # simple backoff (see topic 033)
    return LLMOutcome(ok=False, error_kind="retryable", detail="exhausted")


if __name__ == "__main__":
    print(asyncio.run(safe_chat("HS code for a laptop?")))
```

---

## 🟠 FastAPI Integration
Map SDK errors to meaningful HTTP responses. Do not leak raw upstream messages or keys to clients.

```python
import openai                                          # exception classes
from fastapi import FastAPI, Request                   # framework
from fastapi.responses import JSONResponse             # custom error response
from pydantic import BaseModel                         # models
from openai import AsyncOpenAI                         # client

app = FastAPI()                                        # app
client = AsyncOpenAI(max_retries=2, timeout=30.0)      # SDK-level retries for transient errors


@app.exception_handler(openai.RateLimitError)          # 429 from upstream
async def rate_limit_handler(request: Request, exc: openai.RateLimitError):
    return JSONResponse(status_code=429, content={"detail": "Busy, retry shortly"},
                        headers={"Retry-After": "5"})


@app.exception_handler(openai.BadRequestError)         # our request was invalid
async def bad_request_handler(request: Request, exc: openai.BadRequestError):
    return JSONResponse(status_code=422, content={"detail": "Input could not be processed"})


@app.exception_handler(openai.APIError)                # everything else from the SDK
async def api_error_handler(request: Request, exc: openai.APIError):
    return JSONResponse(status_code=502, content={"detail": "AI service unavailable"})


class Q(BaseModel):
    text: str


@app.post("/ask")
async def ask(q: Q) -> dict:
    r = await client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": q.text}], max_tokens=200)
    return {"answer": r.choices[0].message.content}
```

---

## 🔗 LangChain / LangGraph Connection
`ChatOpenAI(max_retries=...)` retries transient failures. `.with_retry()` adds retry logic to any Runnable, and `.with_fallbacks([...])` switches model on failure. In LangGraph, wrap risky nodes in try/except and write an `error` field into state, or attach a `RetryPolicy` to a node.

```python
from langchain_openai import ChatOpenAI                    # wrapper
import openai                                              # exception types

primary = ChatOpenAI(model="gpt-4o-mini", max_retries=2, timeout=30)   # SDK retries
backup = ChatOpenAI(model="gpt-4o", max_retries=1, timeout=30)         # other model

# Retry only on rate-limit style errors, then fall back on any exception
robust = primary.with_retry(
    retry_if_exception_type=(openai.RateLimitError, openai.APIConnectionError),
    stop_after_attempt=3,
).with_fallbacks([backup])
# robust.invoke("HS code for a laptop?")

# LangGraph:  from langgraph.pregel import RetryPolicy
# builder.add_node("classify", classify_fn, retry=RetryPolicy(max_attempts=3))
# (the retry= argument name varies by version; check the docs for your langgraph release)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: A bare `except Exception: pass`
✅ Correct: Catch specific errors and log them.

```python
# Wrong — hides every bug, user gets an empty answer
try:
    r = client.chat.completions.create(...)
except Exception:
    pass
# Right
except openai.RateLimitError:
    ...  # backoff
except openai.BadRequestError as e:
    logger.error("bad request %s", e.message)
```

❌ Mistake 2: Retrying 400 or 401 errors
✅ Correct: Those never succeed on retry; fix the request or the key.

❌ Mistake 3: Stacked retries (SDK retries x your retries x gateway retries)
✅ Correct: Choose one retry layer or multiply the attempt counts carefully.

❌ Mistake 4: Showing raw exception text to end users
✅ Correct: Return a friendly message and log details internally.

---

## 🧠 Tricky Interview Question

**Q**: "You get HTTP 429 errors, but your traffic is tiny. Is it always a rate limit?"

**Answer**: No. A 429 can be a rate limit (requests or tokens per minute) OR `insufficient_quota` (billing or credit exhausted). Retrying the second never helps. Read `exc.code` / the error body: `rate_limit_exceeded` is transient, `insufficient_quota` is permanent until billing is fixed. Treating both the same causes endless retries that look like an outage while the real issue is an empty balance.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Which errors should you retry?
A1: Connection errors, timeouts, 429 rate limits (not quota), and 5xx server errors.

Q2: [Easy] What does a 400 `BadRequestError` mean?
A2: Your request is invalid (bad parameters, context too long, wrong message format). Retrying will not help.

Q3: [Medium] What is `request_id` useful for?
A3: Each response and error carries a request id. Log it so OpenAI support can trace the exact failed call.

Q4: [Medium] How do you set timeouts?
A4: `OpenAI(timeout=30.0)` for the client, or per request with `timeout=`; use `httpx.Timeout` for fine control of connect and read times. Streaming calls need longer read timeouts.

Q5: [Hard] How do you design graceful degradation for LLM outages?
A5: Circuit breaker to stop hammering a failing service; fallback model or provider; cached answers for repeat questions; non-LLM fallback (rules/keyword search); queue and retry later for non-urgent jobs; clear user messaging; and alerts based on error-rate SLOs.

---

## 🔷 When to Use + When Not to Use
✅ Retry when:
- Error is transient (429 rate limit, 5xx, timeout, connection)

❌ Do not retry when:
- 400, 401, 403, 404, or `insufficient_quota`
- Content was blocked by policy (change the input)

---

## 📊 Visual Diagram
```
            call OpenAI
                 |
        +--------+---------+
        |                  |
     success             exception
        |                  |
     return        is it retryable?
                     /           \
                  yes             no
                   |               |
          backoff + retry     log + alert
          (max N attempts)    return clear error
                   |
          still failing?
                   |
        fallback model / cache / non-LLM path
```

---

## 💰 Cost Impact
- Retrying permanent errors wastes time but usually little money (a rejected 400 request is typically not billed), whereas retrying timeouts on long generations can double-bill because the first call may still complete server-side.
- Unbounded retry loops plus concurrency can create traffic storms and hit rate limits harder.
- Optimise: classify errors, cap attempts, use backoff with jitter, set `max_tokens`, fail fast on permanent errors, and use cheaper fallbacks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| RateLimitError | HTTP 429 too many requests | बहुत ज़्यादा requests (429) |
| BadRequestError | HTTP 400 invalid request | गलत request (400) |
| AuthenticationError | HTTP 401 bad key | गलत key (401) |
| APIConnectionError | Network failure | Network की दिक्कत |
| Retryable | Might succeed on retry | दोबारा करने पर सफल हो सकता है |
| Fallback | Backup path on failure | Failure पर backup रास्ता |
| request_id | ID of a call for support | Support के लिए call की ID |

---

## ⚡ 3-Line Summary
English: Catch specific OpenAI exceptions and split them into retryable (429, 5xx, timeout, connection) and permanent (400, 401, quota). Retry with a limit and backoff, log request ids, and return friendly errors. Add fallbacks so users still get an answer.
Hindi: OpenAI की specific exceptions पकड़ो और retryable (429, 5xx, timeout, connection) व permanent (400, 401, quota) में बाँटो। सीमित retry और backoff के साथ retry करो, request ids log करो, और friendly errors लौटाओ। Fallbacks जोड़ो ताकि user को फिर भी जवाब मिले।

---

## ➡️ Next Topic
**032. OpenAI API — Rate Limits** — RPM, TPM, headers, and how to stay under the limit.
