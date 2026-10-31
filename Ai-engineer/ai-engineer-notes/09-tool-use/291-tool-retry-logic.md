---

# 291. Tool Retry Logic
# हिंदी में: Tool Retry Logic (फेल होने पर दोबारा कोशिश)

---

## 🔵 Simple Definition (English)
Tool retry logic automatically re-runs a failed tool call when the failure is temporary (timeout, 429, 503). It waits longer between attempts (exponential backoff with jitter), stops after a limit, and never blindly repeats calls that are permanent failures or unsafe to repeat.

## 🔵 सरल परिभाषा (Hindi)
Tool retry logic अस्थायी failure (timeout, 429, 503) पर tool call अपने आप दोबारा चलाता है। हर बार ज़्यादा देर रुकता है (exponential backoff + jitter), limit के बाद रुक जाता है, और स्थायी या खतरनाक failures को आँख बंद करके नहीं दोहराता।

---

## 🔴 Problem it Solves
Networks and APIs fail briefly all the time. Without retries, one 503 turns into a failed user request. With naive retries (instant, unlimited), a struggling service gets hammered by thousands of agents at once (retry storm), and non-idempotent actions (refund, send email) get executed twice.

## 🔴 यह क्यों बना? (Hindi)
Network और APIs थोड़ी देर के लिए अक्सर फेल होते हैं। Retry के बिना एक 503 = user की failed request। Naive retry (तुरंत, असीमित) से बीमार service पर हज़ारों agents टूट पड़ते हैं (retry storm), और refund/email जैसे actions दो बार चल जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Tool call fails with an exception or error status
Step 2 → Classify: retryable (timeout, 429, 5xx) vs permanent (400, 401, 404, validation)
Step 3 → Permanent -> return error to LLM immediately (no retry)
Step 4 → Retryable -> wait base * 2^attempt + random jitter (honour Retry-After)
Step 5 → Retry up to N attempts (usually 3) within a total deadline
Step 6 → Side-effect tool? send an idempotency key so repeats are safe
Step 7 → Still failing -> return structured error; circuit breaker opens if many fail
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Tool call exception या error status से फेल होता है
Step 2 → Classify: retryable (timeout, 429, 5xx) या permanent (400, 401, 404, validation)
Step 3 → Permanent -> तुरंत error LLM को लौटाओ (retry नहीं)
Step 4 → Retryable -> base * 2^attempt + random jitter रुको (Retry-After मानो)
Step 5 → ज़्यादा से ज़्यादा N बार (आमतौर पर 3), कुल deadline के भीतर
Step 6 → Side-effect tool? idempotency key भेजो ताकि दोहराव सुरक्षित हो
Step 7 → फिर भी फेल -> structured error; बहुत failures पर circuit breaker खुलता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: The exchange-rate API returns 503 once per minute during peak. Retry with backoff (0.5s, 1s, 2s) succeeds on the second attempt; the user never notices. A 404 for an unknown HS code is not retried, it goes straight back to the LLM.

**Zomato AI**: "Place order" tool carries an idempotency key `order-{cart_id}`; a timeout-retry cannot create two orders.

## 🟡 Real Example Hindi mein
**Tariff System**: Exchange-rate API peak पर हर मिनट एक बार 503 देती है। Backoff (0.5s, 1s, 2s) से दूसरी कोशिश में सफलता मिलती है; user को पता भी नहीं चलता। अज्ञात HS code पर 404 retry नहीं होता, सीधे LLM को जाता है।

**Zomato AI**: "Order place" tool में idempotency key `order-{cart_id}` है; timeout-retry से दो orders नहीं बनते।

---

## 💻 Code Example — Basic
```python
# Retry with exponential backoff + jitter (pure Python, runs offline)
import random                             # for jitter
import time                               # for sleep
from typing import Callable, TypeVar

T = TypeVar("T")                          # generic return type

class TransientError(Exception):
    """Temporary failure: safe to retry."""

class PermanentError(Exception):
    """Permanent failure: never retry."""

def retry(func: Callable[[], T], attempts: int = 3, base: float = 0.1) -> T:
    """Call func up to `attempts` times, backing off between tries."""
    for attempt in range(attempts):                       # attempt = 0, 1, 2
        try:
            return func()                                 # success -> return immediately
        except PermanentError:
            raise                                         # do not retry permanent errors
        except TransientError as exc:
            if attempt == attempts - 1:                   # last try failed -> give up
                raise
            delay = base * (2 ** attempt) + random.uniform(0, base)   # backoff + jitter
            print(f"attempt {attempt + 1} failed ({exc}); sleeping {delay:.2f}s")
            time.sleep(delay)                             # wait before next try
    raise RuntimeError("unreachable")                     # keeps type checkers happy

calls = {"n": 0}                                          # simulate a flaky service
def flaky_fx() -> float:
    calls["n"] += 1
    if calls["n"] < 3:                                    # first two calls fail
        raise TransientError("503 service unavailable")
    return 83.2

print(retry(flaky_fx))                                    # succeeds on 3rd attempt -> 83.2
```

## 💻 Code Example — Advanced
```python
# Production: async retry decorator, Retry-After, total deadline, circuit breaker
import asyncio, functools, random, time
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar
import httpx

P = ParamSpec("P")
R = TypeVar("R")
RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}        # statuses worth retrying

class CircuitOpen(Exception):
    """Raised when the breaker blocks calls to a failing service."""

class CircuitBreaker:
    """Opens after `threshold` consecutive failures; half-opens after `cooldown` seconds."""
    def __init__(self, threshold: int = 5, cooldown: float = 30.0) -> None:
        self.threshold, self.cooldown = threshold, cooldown
        self.failures = 0
        self.opened_at: float | None = None

    def allow(self) -> bool:
        if self.opened_at is None:
            return True
        if time.monotonic() - self.opened_at >= self.cooldown:   # probe again
            return True
        return False

    def record(self, ok: bool) -> None:
        if ok:
            self.failures, self.opened_at = 0, None
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = time.monotonic()

def with_retry(attempts: int = 3, base: float = 0.5, deadline: float = 10.0,
               breaker: CircuitBreaker | None = None):
    """Decorator for async tools."""
    def deco(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.monotonic()
            last: Exception | None = None
            for attempt in range(attempts):
                if breaker and not breaker.allow():
                    raise CircuitOpen("service temporarily disabled")
                try:
                    result = await fn(*args, **kwargs)
                    if breaker: breaker.record(True)
                    return result
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code not in RETRYABLE_STATUS:
                        raise                                  # 4xx: permanent
                    last = exc
                    retry_after = exc.response.headers.get("Retry-After")
                    wait = float(retry_after) if retry_after and retry_after.isdigit() else None
                except (httpx.TimeoutException, httpx.TransportError) as exc:
                    last, wait = exc, None
                if breaker: breaker.record(False)
                delay = wait if wait is not None else base * 2 ** attempt + random.uniform(0, base)
                if time.monotonic() - start + delay > deadline:   # respect total time budget
                    break
                await asyncio.sleep(delay)
            assert last is not None
            raise last
        return wrapper
    return deco

fx_breaker = CircuitBreaker()

@with_retry(attempts=3, base=0.5, deadline=8.0, breaker=fx_breaker)
async def fetch_rate(base: str, target: str) -> float:
    async with httpx.AsyncClient(timeout=3.0) as http:
        resp = await http.get("https://api.exchangerate.example/latest", params={"base": base})
        resp.raise_for_status()                                 # raises HTTPStatusError on 4xx/5xx
        return float(resp.json()["rates"][target])

async def fetch_rate_tool(base: str, target: str) -> dict[str, Any]:
    """Tool boundary: convert any final failure to a structured error for the LLM."""
    try:
        return {"ok": True, "rate": await fetch_rate(base, target)}
    except CircuitOpen as exc:
        return {"ok": False, "error_type": "circuit_open", "error": str(exc)}
    except httpx.HTTPError as exc:
        return {"ok": False, "error_type": "upstream", "error": f"failed after retries: {type(exc).__name__}"}
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/rate/{base}/{target}")
async def rate(base: str, target: str) -> dict:
    """Retries happen INSIDE the tool; the HTTP caller sees one result."""
    result = await fetch_rate_tool(base, target)
    return result

@app.get("/health/breaker")
async def breaker_state() -> dict:
    """Expose breaker state for monitoring/alerts."""
    return {"failures": fx_breaker.failures, "open": fx_breaker.opened_at is not None}
```
Also set a request-level timeout (`asyncio.wait_for`) so total retry time never exceeds the client's patience.

---

## 🔗 LangChain / LangGraph Connection
```python
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda

llm = ChatOpenAI(model="gpt-4o-mini", max_retries=3)    # built-in retry for LLM API calls (429/5xx)

# Any Runnable (including tools) can get retries:
tool_runnable = RunnableLambda(lambda x: flaky_fx())
robust = tool_runnable.with_retry(
    retry_if_exception_type=(TransientError,),          # only retry these
    wait_exponential_jitter=True,                       # backoff with jitter
    stop_after_attempt=3,
)
```
LangGraph supports `RetryPolicy` on nodes (`graph.add_node("fetch", fetch_node, retry=RetryPolicy(max_attempts=3))` in recent versions), and the `tenacity` library is a common alternative.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Retrying everything, including 4xx
✅ Correct: Retry only transient failures.

```python
# Wrong — retries a 404 three times for nothing:
for _ in range(3):
    try: return call()
    except Exception: continue
# Right:
except (TransientError, httpx.TimeoutException): ...   # retry
except PermanentError: raise                           # fail fast
```

❌ Mistake 2: Fixed delay without jitter
✅ Correct: Exponential backoff plus random jitter so clients do not retry in sync.

```python
# Wrong:
time.sleep(1)
# Right:
time.sleep(0.5 * 2 ** attempt + random.uniform(0, 0.5))
```

❌ Mistake 3: Retrying non-idempotent calls (refund, send email) without an idempotency key.

---

## 🧠 Tricky Interview Question

**Q**: "Your tool has 3 retries, the LLM loop has 5 iterations, and the HTTP client has its own 3 retries. The upstream is down. How many calls hit the upstream and what is the fix?"

**Answer**: Retries multiply: 3 (tool) x 3 (client) x 5 (loop) = up to 45 calls per user request, which causes a retry storm. Fix: retry in exactly one layer, use a total deadline, add a circuit breaker so later calls fail fast, and return a non-retryable error type to the LLM when retries are exhausted so it stops calling that tool.

---

## ⚫ Interview Questions + Answers

Q1: What is exponential backoff? (Easy)
A1: Delay doubles with each attempt (0.5s, 1s, 2s...) so a struggling service gets breathing room.

Q2: Why add jitter? (Easy)
A2: Random extra delay stops many clients retrying at the same instant, which would overload the service again.

Q3: Which errors should not be retried? (Medium)
A3: 400, 401, 403, 404, 422 and validation errors; retrying cannot fix them. Return them to the LLM so it can change arguments.

Q4: What is idempotency and why does it matter for retries? (Medium)
A4: An operation is idempotent if repeating it has the same effect as doing it once. Reads are; "create order" is not unless you send an idempotency key. Without it, a retry after a timeout can duplicate the action.

Q5: How do retries, rate limits and circuit breakers work together? (Hard)
A5: Rate limiting protects the upstream from you; retries handle transient errors; a circuit breaker stops retries when the failure is sustained. Use a single retry layer with a deadline, honour `Retry-After` on 429, open the breaker after N consecutive failures, serve a fallback or cached value, and expose breaker state in metrics.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Failures are temporary (timeouts, 429, 5xx)
- Operation is read-only or idempotent
- You have a total time budget

❌ Avoid when:
- Error is a validation or auth problem
- Action has side effects with no idempotency key
- User is waiting and latency budget is already used

---

## 📊 Visual Diagram
```
 call ──fail──► classify
                  │
        permanent ┴──────────► return error to LLM
        transient
           │
           ▼
  wait 0.5s ─► call ─fail─► wait 1s ─► call ─fail─► wait 2s ─► call
                  │                        │                      │
                 ok                       ok              fail -> give up
                  ▼                        ▼                      ▼
               result                   result          structured error
  (circuit breaker watches the failures and opens after N in a row)
```

---

## 💰 Cost Impact
Tool retries themselves cost no LLM tokens (they run in your code). But retries delegated to the LLM (it sees an error and calls again) re-send the whole history each round: a 3K-token conversation with 3 LLM-driven retries is about 9K extra input tokens. LLM API retries on 429 are free of tokens if the request was rejected, but add latency.

Optimize: retry inside the tool (not via the model), cap rounds, use circuit breakers to fail fast, cache successes, and return clear non-retryable errors so the model stops.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Exponential backoff | Doubling wait between retries | हर बार दुगना इंतज़ार |
| Jitter | Random extra delay | Random अतिरिक्त देरी |
| Idempotent | Repeat is safe | दोहराना सुरक्षित |
| Circuit breaker | Stops calls to failing service | खराब service पर call रोकना |
| Retry-After | Server-suggested wait | Server द्वारा बताया इंतज़ार |
| Retry storm | Many retries overload a service | Retries से service पर बोझ |

---

## ⚡ 3-Line Summary
English: Retry only transient failures, with exponential backoff, jitter and a total deadline. Use idempotency keys for side effects and a circuit breaker for sustained outages. Retry in one layer only to avoid multiplied calls.
Hindi: सिर्फ़ transient failures retry करो: exponential backoff, jitter और कुल deadline के साथ। Side effects के लिए idempotency key और लंबी outage के लिए circuit breaker। Retry सिर्फ़ एक layer में करो ताकि calls गुणा न हों।

---

## ➡️ Next Topic
**292. Tool Output Validation** — checking that what a tool returns (and what the LLM sends) is correct and safe before using it.
