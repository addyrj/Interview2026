---

# 522. Reliability in AI Systems
# हिंदी में: AI Systems में Reliability

---

## 🔵 Simple Definition (English)
Reliability means the AI system keeps giving correct, usable answers even when parts fail: provider outages, timeouts, rate limits, bad model output. You get it with retries, timeouts, circuit breakers, validation, idempotency, and clear SLOs.

## 🔵 सरल परिभाषा (Hindi)
Reliability का मतलब है कि कुछ हिस्से fail होने पर भी (provider outage, timeout, rate limit, खराब model output) AI system सही और काम लायक जवाब देता रहे। यह retries, timeouts, circuit breakers, validation, idempotency और साफ SLOs से मिलती है।

---

## 🔴 Problem it Solves
LLM APIs are remote, shared, and non-deterministic. They return 429/500/503, time out, give malformed JSON, or answer wrongly with confidence. Without reliability design, one provider hiccup becomes a user-facing outage, and failed calls retried carelessly cause retry storms that make outages worse.

## 🔴 यह क्यों बना? (Hindi)
LLM APIs remote, shared और non-deterministic हैं। ये 429/500/503 देती हैं, timeout होती हैं, खराब JSON लौटाती हैं या गलत जवाब पूरे confidence से देती हैं। Reliability design के बिना provider की एक hiccup user की outage बन जाती है, और लापरवाह retries retry storm बनाकर हालत बिगाड़ते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define SLOs: availability (99.9%), p95 latency, answer-validity rate
Step 2 → Timeouts on every network call (connect + read) so nothing hangs
Step 3 → Retry only transient errors (429, 5xx, timeouts) with exponential backoff + jitter
Step 4 → Circuit breaker: after N failures stop calling for a cool-down, then probe
Step 5 → Validate outputs (schema, allowed values); retry or repair invalid output
Step 6 → Idempotency keys so retries never double-charge or double-write
Step 7 → Fallbacks (next topic) and graceful degradation when dependencies fail
Step 8 → Health checks, alerts on error budget burn, regular failure drills
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → SLO तय करो: availability (99.9%), p95 latency, valid-answer rate
Step 2 → हर network call पर timeout ताकि कुछ अटके नहीं
Step 3 → सिर्फ transient errors (429, 5xx, timeout) पर backoff + jitter के साथ retry
Step 4 → Circuit breaker: N failures के बाद cool-down तक call बंद, फिर probe
Step 5 → Output validate करो (schema, allowed values); invalid पर retry/repair
Step 6 → Idempotency key ताकि retry से double write/charge न हो
Step 7 → Fallbacks और graceful degradation
Step 8 → Health checks, error budget alerts, failure drills
```

---

## 🟡 Real World Example
**Tariff Classification System**: The LLM must return JSON `{"hs_code": "8517.13", "confidence": 0.93}`. Failure modes: provider 503, timeout, invalid JSON, or an HS code that does not exist in the official table. Reliability layers: retry on 503, schema validation, lookup of the code in a trusted table, and a human-review queue if validation fails twice. The customs filing is never submitted with an unvalidated code.

**Amazon-style**: If the AI "summarise reviews" service is down, the page shows the normal reviews instead of an error.

## 🟡 Real Example Hindi mein
**Tariff System**: LLM को JSON `{"hs_code": "8517.13", "confidence": 0.93}` लौटाना है। Failure modes: provider 503, timeout, invalid JSON, या ऐसा HS code जो official table में नहीं है। Layers: 503 पर retry, schema validation, trusted table में code lookup, और दो बार fail होने पर human-review queue। Unvalidated code से customs filing कभी submit नहीं होती।
**Amazon-style**: AI review summary service down हो तो page सामान्य reviews दिखाता है, error नहीं।

---

## 💻 Code Example — Basic
```python
# Retry with exponential backoff + output validation (pure Python, runs offline)
import json                                   # parse model output
import random                                 # jitter and fake failures
import time                                   # sleep between retries

VALID_CODES = {"8517.13", "6109.10", "8471.30"}   # trusted HS table (tiny demo)
random.seed(1)                                # make the demo repeatable

def flaky_llm(text: str) -> str:
    """Fake LLM that fails or returns junk sometimes."""
    r = random.random()                       # roll the dice
    if r < 0.3:                               # 30%: provider error
        raise ConnectionError("503 service unavailable")
    if r < 0.5:                               # 20%: invalid JSON
        return "Sure! The code is 8517.13"
    return json.dumps({"hs_code": "8517.13", "confidence": 0.93})   # good answer

def classify(text: str, max_attempts: int = 5) -> dict:
    """Call the LLM, retry on transient errors, validate output."""
    for attempt in range(1, max_attempts + 1):        # try several times
        try:
            raw = flaky_llm(text)                     # call the model
            data = json.loads(raw)                    # must be valid JSON
            if data["hs_code"] not in VALID_CODES:    # must exist in trusted table
                raise ValueError("unknown HS code")
            return data                               # success
        except (ConnectionError, json.JSONDecodeError, ValueError, KeyError) as exc:
            print(f"attempt {attempt} failed: {exc}")  # log the failure
            time.sleep(min(2 ** attempt * 0.01, 0.5) + random.random() * 0.01)   # backoff + jitter
    raise RuntimeError("giving up")                   # let caller route to human review

print(classify("smart phone"))                        # run the demo
```

## 💻 Code Example — Advanced
```python
# Circuit breaker + retry + timeout (async, type hints, error handling)
import asyncio                                         # async runtime
import random                                          # jitter
import time                                            # monotonic clock
from enum import Enum                                  # breaker states
from typing import Awaitable, Callable, TypeVar        # generics for reuse

T = TypeVar("T")                                       # return type of the wrapped call

class State(Enum):
    CLOSED = "closed"          # normal: calls allowed
    OPEN = "open"              # failing: calls blocked
    HALF_OPEN = "half_open"    # probing: one trial call allowed

class CircuitOpen(Exception):
    """Raised when the breaker blocks a call."""

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_after_s: float = 30.0) -> None:
        self.threshold = failure_threshold             # failures before opening
        self.reset_after = reset_after_s               # cool-down seconds
        self.failures = 0                              # consecutive failures
        self.state = State.CLOSED                      # start closed
        self.opened_at = 0.0                           # when it opened

    def _allow(self) -> bool:
        """Decide if a call may proceed."""
        if self.state == State.OPEN:                   # blocked state
            if time.monotonic() - self.opened_at >= self.reset_after:   # cool-down over?
                self.state = State.HALF_OPEN           # allow a probe
                return True
            return False                               # still blocked
        return True                                    # closed or half-open

    async def call(self, fn: Callable[[], Awaitable[T]], timeout_s: float = 10.0) -> T:
        """Run fn through the breaker with a timeout."""
        if not self._allow():                          # blocked?
            raise CircuitOpen("provider circuit open") # fail fast, no network
        try:
            result = await asyncio.wait_for(fn(), timeout_s)   # timeout guard
        except Exception:                              # any failure
            self.failures += 1                         # count it
            if self.state == State.HALF_OPEN or self.failures >= self.threshold:
                self.state = State.OPEN                # trip the breaker
                self.opened_at = time.monotonic()      # remember when
            raise                                      # re-raise to caller
        self.failures = 0                              # success resets the count
        self.state = State.CLOSED                      # close the breaker
        return result

async def retry(fn: Callable[[], Awaitable[T]], attempts: int = 3, base: float = 0.2) -> T:
    """Retry transient failures with exponential backoff and full jitter."""
    last: Exception | None = None                      # remember last error
    for i in range(attempts):                          # attempts loop
        try:
            return await fn()                          # try the call
        except CircuitOpen:                            # do not retry a blocked circuit
            raise
        except (asyncio.TimeoutError, ConnectionError) as exc:   # transient only
            last = exc                                 # keep it
            await asyncio.sleep(random.uniform(0, base * 2 ** i))   # full jitter
    raise RuntimeError(f"failed after {attempts} attempts") from last

async def demo() -> None:
    breaker = CircuitBreaker(failure_threshold=2, reset_after_s=0.3)   # tiny numbers for the demo
    async def down() -> str:                           # always failing provider
        raise ConnectionError("503")
    for i in range(4):                                 # keep calling it
        try:
            await retry(lambda: breaker.call(down), attempts=1)
        except Exception as e:
            print(i, type(e).__name__, breaker.state.value)   # see state changes
    await asyncio.sleep(0.35)                          # wait for cool-down
    async def ok() -> str:                             # provider recovered
        return "ok"
    print(await breaker.call(ok), breaker.state.value)   # probe succeeds, closes

if __name__ == "__main__":
    asyncio.run(demo())                                # run
```

---

## 🟠 FastAPI Integration
Map failures to correct HTTP codes: 503 with `Retry-After` when the circuit is open, 422 for bad input, 504 on timeout. Add `/health` (liveness) and `/ready` (dependencies OK) for orchestrators. Keep the breaker as app state.

```python
# FastAPI: reliability-aware route with proper error mapping and health checks
from fastapi import FastAPI, HTTPException                  # framework
from fastapi.responses import JSONResponse                  # custom response
from pydantic import BaseModel                              # validation

app = FastAPI()                                             # app
breaker = CircuitBreaker(failure_threshold=5, reset_after_s=30)   # from the advanced block

class Req(BaseModel):
    description: str                                        # product text

@app.exception_handler(CircuitOpen)
async def circuit_handler(request, exc: CircuitOpen) -> JSONResponse:
    """Tell clients to come back later."""
    return JSONResponse(status_code=503, content={"detail": "AI temporarily unavailable"},
                        headers={"Retry-After": "30"})

@app.post("/classify")
async def classify_route(req: Req) -> dict:
    """Classify with retries, breaker, and validation."""
    try:
        return await retry(lambda: breaker.call(lambda: call_and_validate(req.description)))   # call_and_validate = your LLM + schema check
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Upstream timeout")
    except RuntimeError:
        raise HTTPException(status_code=502, detail="Upstream failed validation")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "alive"}                              # process is running

@app.get("/ready")
async def ready() -> dict[str, str]:
    if breaker.state.value == "open":                       # dependency is bad
        raise HTTPException(status_code=503, detail="provider circuit open")
    return {"status": "ready"}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain chat models have `max_retries` and `timeout`. `Runnable.with_retry(...)` retries any runnable on chosen exceptions, and `with_fallbacks([...])` switches to other runnables. `PydanticOutputParser` or `with_structured_output` validates structure. LangGraph checkpointers (e.g. `MemorySaver`, or a Postgres saver in production) let a failed run resume from the last completed node instead of restarting and re-paying tokens.

```python
# LangChain: retry + structured validation
from langchain_openai import ChatOpenAI                       # model wrapper
from pydantic import BaseModel, Field                         # schema

class Hs(BaseModel):
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")           # format check
    confidence: float = Field(ge=0, le=1)                     # range check

llm = ChatOpenAI(model="gpt-4o-mini", timeout=10, max_retries=2)   # transport retries
chain = llm.with_structured_output(Hs).with_retry(stop_after_attempt=3)   # retry whole step
# result = await chain.ainvoke("HS code for smartphone")   # returns a validated Hs object
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Retrying everything immediately
✅ Correct: Retry only transient errors, with backoff and jitter.

```python
# Wrong — hammers a struggling provider, retries 400 errors too
while True:
    try: return call()
    except Exception: pass

# Right
for i in range(3):
    try: return call()
    except (TimeoutError, ConnectionError):
        time.sleep(random.uniform(0, 0.2 * 2 ** i))
```

❌ Mistake 2: Trusting model output without validation
✅ Correct: Validate shape and business rules.

```python
# Wrong
code = json.loads(raw)["hs_code"]; file_customs(code)

# Right
data = Hs.model_validate_json(raw)          # raises on bad shape
if data.hs_code not in VALID_CODES:         # business rule
    route_to_human(data)
```

---

## 🧠 Tricky Interview Question

**Q**: "The provider has a 10-minute outage. Your service retries 3 times with no jitter across 200 pods. When the provider recovers, it falls over again. What happened?"

**Answer**: A retry storm (thundering herd). All pods retry on the same schedule, multiplying load by up to 4x and synchronising spikes, so the recovering provider is overwhelmed again. Fixes: exponential backoff with full jitter, a circuit breaker that stops calls during the outage and probes slowly after, retry budgets (retries limited to about 10% of traffic), honouring `Retry-After`, queueing with bounded concurrency, and shedding low-priority load. The deeper point: retries are only safe if the whole system limits total amplification.

---

## ⚫ Interview Questions + Answers

Q1: Which errors are worth retrying? (Easy)
A1: Transient ones: timeouts, connection errors, 429, 500, 502, 503, 504. Do not retry 400/401/403/404 or content-policy rejections; they will fail again.

Q2: What is idempotency and why does it matter here? (Easy)
A2: Repeating an operation gives the same result as doing it once. Retries and at-least-once queues repeat requests, so writes need idempotency keys to avoid duplicates.

Q3: What does a circuit breaker do? (Medium)
A3: After repeated failures it opens and rejects calls instantly (fail fast), protecting your threads and the provider. After a cool-down it half-opens, lets a probe through, and closes if it succeeds.

Q4: How do you handle non-deterministic bad outputs? (Medium)
A4: Use structured output, validate with schemas and business rules, retry once with the error message fed back, lower temperature, fall back to rules or human review, and track the invalid-output rate as a metric.

Q5: Define an error budget and how it drives decisions. (Hard)
A5: With a 99.9% SLO you may fail 0.1% of requests (about 43 minutes per month). If the budget burns quickly, freeze risky launches and prioritise reliability work; if it is unused, you can ship faster. Alerts fire on burn rate (for example, 2% of budget in 1 hour), not on single errors. For AI add quality SLOs (valid-output rate, groundedness), not only availability.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Customers or downstream systems depend on the answer
- You rely on third-party model APIs
- Actions have side effects (filings, payments, emails)

❌ Avoid (heavy machinery) when:
- A throwaway prototype or internal demo
- Retries would break semantics and you cannot make calls idempotent (fix design first)

---

## 📊 Visual Diagram
```
Request
  │
  ▼
[Timeout]──▶[Retry w/ backoff+jitter]──▶[Circuit Breaker]──▶ LLM API
                                              │ open
                                              ▼
                                         [Fallback/Degrade]
  ▲
  │ valid?
[Schema + business-rule validation] ──no──▶ retry once ──no──▶ [Human review queue]
  │yes
  ▼
Response   (all metrics ──▶ SLO dashboard ──▶ error budget alerts)
```

---

## 💰 Cost Impact
- Every retry re-sends the full prompt: at a 10% retry rate you pay about 10% more input tokens. Illustrative: 1M calls x 1,000 input tokens = 1B tokens; 10% retries add 100M tokens, about $15 at $0.15/1M (example price).
- Circuit breakers save money during outages by not sending doomed calls. Validate cheaply first (regex, schema) before retrying with a large model.
- Retry with the error message appended costs extra tokens, so limit to one repair attempt; use checkpointing so failures do not redo completed expensive steps.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| SLO | Target reliability level | Reliability का लक्ष्य |
| Error budget | Allowed failure amount | Allowed failure की मात्रा |
| Backoff + jitter | Growing random wait before retry | बढ़ता random इंतज़ार |
| Circuit breaker | Stops calls to failing service | Failing service पर call रोकना |
| Idempotency key | Id that makes retries safe | Retry को safe बनाने वाला id |
| Retry storm | Retries overloading a service | Retries से बढ़ा overload |
| Graceful degradation | Reduced but working service | कम features पर भी चालू |

---

## ⚡ 3-Line Summary
English: Reliability means timeouts, smart retries, circuit breakers, validation and idempotency so failures do not reach users. Retry only transient errors with backoff and jitter to avoid retry storms. Track SLOs and error budgets, including output-quality SLOs.
Hindi: Reliability यानी timeouts, smart retries, circuit breakers, validation और idempotency ताकि failures user तक न पहुँचें। सिर्फ transient errors पर backoff + jitter से retry करो ताकि retry storm न बने। SLO और error budget (output-quality सहित) track करो।

---

## ➡️ Next Topic
**523. Fallback Strategies** — when retries fail, we need a plan B: backup models, cached answers, rules and humans.
