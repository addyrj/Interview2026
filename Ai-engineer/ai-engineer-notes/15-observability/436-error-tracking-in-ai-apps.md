---

# 436. Error Tracking in AI Apps
# हिंदी में: AI Apps में Error Tracking

---

## 🔵 Simple Definition (English)
Error tracking in AI apps means capturing, classifying and counting every failure: **hard errors** (timeouts, 429 rate limits, 5xx, auth), **soft errors** (invalid JSON, schema violation, empty answer, refusal), and **silent errors** (confident wrong answer). Each is grouped, linked to a trace and alerted on.

## 🔵 सरल परिभाषा (Hindi)
AI apps में error tracking का मतलब हर failure को पकड़ना, वर्गीकृत करना और गिनना है: **hard errors** (timeout, 429, 5xx, auth), **soft errors** (गलत JSON, schema violation, खाली जवाब, refusal) और **silent errors** (आत्मविश्वास से गलत जवाब)। हर एक trace से जुड़ा होता है और उस पर alert लगता है।

---

## 🔴 Problem it Solves
- Traditional tools only see exceptions and HTTP 5xx. LLM apps often "succeed" (HTTP 200) with output that breaks the next step.
- Provider errors need different handling: retry 429/503, never retry 400/401.
- Without grouping, 10,000 identical errors look like 10,000 problems.

## 🔴 यह क्यों बना? (Hindi)
- पारंपरिक tools सिर्फ exceptions और HTTP 5xx देखते हैं। LLM apps अक्सर HTTP 200 के साथ "सफल" होते हैं पर output अगले step को तोड़ देता है।
- Provider errors का handling अलग है: 429/503 retry करो, 400/401 कभी नहीं।
- Grouping के बिना 10,000 एक जैसे errors 10,000 समस्याओं जैसे दिखते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Wrap every LLM/tool call in try/except; catch specific exception types
Step 2 → Classify: retryable (429, 5xx, timeout) vs non-retryable (400, 401, content filter)
Step 3 → Validate output: parse JSON, check pydantic schema, check HS code format
Step 4 → On failure: retry with backoff -> fallback model -> graceful message
Step 5 → Record error with context: request_id, model, prompt version, error class (no secrets)
Step 6 → Group by fingerprint (error class + step), count, send to Sentry/APM/trace
Step 7 → Alert on error rate and on new error types; review top errors weekly
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर LLM/tool call को try/except में रखो; specific exception types पकड़ो
Step 2 → वर्गीकरण: retryable (429, 5xx, timeout) बनाम non-retryable (400, 401, content filter)
Step 3 → Output validate करो: JSON parse, pydantic schema, HS code format
Step 4 → Failure पर: backoff के साथ retry -> fallback model -> graceful message
Step 5 → Context के साथ record करो: request_id, model, prompt version, error class (secrets नहीं)
Step 6 → Fingerprint (error class + step) से group, count, Sentry/APM/trace में भेजो
Step 7 → Error rate और नए error types पर alert; हर हफ्ते top errors review
```

---

## 🟡 Real World Example
**Tariff Classification System**: Error dashboard for one day: 61% `RateLimitError` at 9 AM (bulk uploads), 22% `ValidationError` (model returned "8518.2" instead of the 4.2 digit format), 9% timeouts, 8% other. Actions: add a queue and token-bucket limiter for bulk jobs, tighten the output schema with structured outputs, set per-step timeouts. The silent error (wrong but valid code) is caught by a nightly sampled review, not by exceptions.

**Amazon-style**: a product-description generator flags "refusal" outputs ("I cannot help with that") as a soft-error category.

## 🟡 Real Example Hindi mein
**Tariff System**: एक दिन का error dashboard: 61% `RateLimitError` सुबह 9 बजे (bulk uploads), 22% `ValidationError` (model ने सही format की जगह "8518.2" दिया), 9% timeouts, 8% अन्य। Actions: bulk jobs के लिए queue और token-bucket limiter, structured outputs से schema सख्त, हर step पर timeout। Silent error (गलत पर valid code) exceptions से नहीं, रात की sampled review से पकड़ी जाती है।

---

## 💻 Code Example — Basic
Error classification and counting in pure Python (run directly).

```python
# Classify errors into retryable / non-retryable / soft and count them
from collections import Counter                       # counts
import json                                           # parse model output
import re                                             # HS code check


class RateLimit(Exception): ...                       # stand-in for 429
class Timeout(Exception): ...                         # stand-in for timeout
class BadRequest(Exception): ...                      # stand-in for 400


def classify_error(exc: Exception) -> str:            # map exception -> category
    if isinstance(exc, (RateLimit, Timeout)):
        return "retryable"                            # safe to retry with backoff
    if isinstance(exc, BadRequest):
        return "non_retryable"                        # our bug: fix, do not retry
    return "unknown"                                  # alert on these


def validate_output(raw: str) -> str:                 # soft error detection
    data = json.loads(raw)                            # may raise JSONDecodeError
    code = str(data["hs_code"])                       # may raise KeyError
    if not re.fullmatch(r"\d{4}\.\d{2}", code):       # expect 8518.22 format
        raise ValueError(f"bad hs format: {code}")
    return code


COUNTS: Counter[str] = Counter()                      # fingerprint -> count
for exc in [RateLimit(), Timeout(), BadRequest()]:
    COUNTS[f"{type(exc).__name__}:{classify_error(exc)}"] += 1

for raw in ['{"hs_code": "8518.22"}', '{"hs_code": "8518.2"}', "not json", "{}"]:
    try:
        print("ok", validate_output(raw))
    except (json.JSONDecodeError, KeyError, ValueError) as e:   # soft errors
        COUNTS[f"soft:{type(e).__name__}"] += 1

print(dict(COUNTS))                                   # summary
```

## 💻 Code Example — Advanced
Typed async wrapper: retries on retryable errors, schema validation with pydantic v2, fallback model, structured error log.

```python
# Production error handling: retry + validate + fallback + structured record
import asyncio                                                  # sleep for backoff
import json                                                     # parse
import logging                                                  # logs
import random                                                   # jitter
from typing import Optional                                     # hints

from openai import (AsyncOpenAI, APITimeoutError, APIConnectionError,
                    RateLimitError, APIStatusError)             # error classes
from pydantic import BaseModel, Field, ValidationError          # pydantic v2

log = logging.getLogger("errors")                               # logger
client = AsyncOpenAI(timeout=15.0, max_retries=0)               # we control retries


class HSResult(BaseModel):                                      # expected output
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")             # 8518.22 format
    confidence: float = Field(ge=0, le=1)


class ClassifyFailed(Exception):                                # final failure for caller
    pass


async def _call(model: str, product: str) -> HSResult:
    r = await client.chat.completions.create(
        model=model, temperature=0, max_tokens=60,
        response_format={"type": "json_object"},                # JSON mode
        messages=[
            {"role": "system", "content": 'Reply JSON: {"hs_code":"NNNN.NN","confidence":0-1}'},
            {"role": "user", "content": product},
        ],
    )
    return HSResult.model_validate(json.loads(r.choices[0].message.content or "{}"))


async def classify(product: str, request_id: str) -> HSResult:
    models = ["gpt-4o-mini", "gpt-4o"]                          # primary then fallback
    last: Optional[Exception] = None
    for model in models:
        for attempt in range(3):                                # up to 3 tries per model
            try:
                return await _call(model, product)
            except (RateLimitError, APITimeoutError, APIConnectionError) as e:
                last = e                                        # retryable
                await asyncio.sleep(min(8, 2 ** attempt) + random.random())  # backoff + jitter
            except APIStatusError as e:
                last = e
                if e.status_code >= 500:                        # 5xx retryable
                    await asyncio.sleep(2 ** attempt)
                    continue
                break                                           # 4xx: do not retry, try fallback
            except (ValidationError, json.JSONDecodeError) as e:
                last = e                                        # soft error: retry again
            log.warning("llm_error", extra={"request_id": request_id, "model": model,
                                            "attempt": attempt, "error": type(last).__name__})
    raise ClassifyFailed(f"all attempts failed: {type(last).__name__}") from last
```

---

## 🟠 FastAPI Integration
Map internal failures to correct HTTP codes and attach `request_id` so support can find the trace.

```python
# FastAPI exception handler for AI failures
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from err_mod import classify, ClassifyFailed                    # advanced example

app = FastAPI()


class Req(BaseModel):
    product: str


@app.exception_handler(ClassifyFailed)
async def failed_handler(request: Request, exc: ClassifyFailed) -> JSONResponse:
    rid = getattr(request.state, "request_id", "unknown")
    return JSONResponse(status_code=503, headers={"Retry-After": "5"},
                        content={"error": "temporarily unavailable", "request_id": rid})


@app.post("/classify")
async def route(req: Req, request: Request) -> dict:
    request.state.request_id = uuid.uuid4().hex
    result = await classify(req.product, request.state.request_id)
    return {**result.model_dump(), "request_id": request.state.request_id}
```

---

## 🔗 LangChain / LangGraph Connection
LCEL has built-in `with_retry` and `with_fallbacks`; LangGraph lets you add an error branch.

```python
# LangChain retry + fallback + structured output validation
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class HS(BaseModel):
    hs_code: str

primary = ChatOpenAI(model="gpt-4o-mini", timeout=15).with_structured_output(HS)
backup = ChatOpenAI(model="gpt-4o").with_structured_output(HS)

chain = primary.with_retry(stop_after_attempt=3).with_fallbacks([backup])   # retry then fallback
print(chain.invoke("HS code for Bluetooth speaker"))

# LangGraph: conditional edge from "classify" node -> "fallback" or "human_review" node
# when state["error"] is set.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Retrying everything, including 400/401
✅ Correct: retry only transient errors, with bounded attempts.

```python
# Wrong: infinite retry on a bad prompt (400) burns money
while True:
    try:
        return await call()
    except Exception:
        continue
# Right: catch specific classes, bounded attempts (see Advanced example)
```

❌ Mistake 2: Swallowing errors and returning an empty string
✅ Correct: raise or return an explicit error state; log with context.

```python
# Wrong: downstream thinks "" is a valid HS code
try:
    code = await call()
except Exception:
    code = ""
# Right
try:
    code = await call()
except Exception as e:
    log.exception("classify failed")
    raise ClassifyFailed from e
```

---

## 🧠 Tricky Interview Question
**Q**: "Error rate is near zero but 8% of users report wrong results. How do you track this?"

**Answer**: These are silent errors. Track via quality signals: schema and range validation (soft errors), confidence thresholds, self-consistency checks (second call or rule-based validator against the tariff table), user feedback/escalations, and sampled human or LLM-judge review linked to traces. Treat "low confidence", "validator disagrees" and "user corrected" as first-class error events with counters and alerts.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): Which errors should you retry?
A1: Transient ones: 429, 5xx, timeouts, connection errors. Not 400, 401, 403, 404 or content-policy failures.

Q2 (Easy): What is exponential backoff with jitter?
A2: Waiting 1s, 2s, 4s... between retries plus random jitter, so many clients do not retry at the same instant.

Q3 (Medium): What is a fallback and what are its risks?
A3: Switch to another model/provider when the primary fails. Risks: different output quality, format and cost, so validate outputs and log which model answered.

Q4 (Medium): How do you stop a retry storm?
A4: Cap attempts, use jitter, add a circuit breaker that opens after repeated failures, and respect `Retry-After` headers.

Q5 (Hard): Design error handling for an agent that calls 5 tools.
A5: Each tool returns a typed result or error. Retry transient errors inside the tool with limits, feed non-transient errors back to the model as observations once, cap total steps and cost per run, and use a circuit breaker per tool. If the run fails, return partial results with a clear status and keep the full trace for debugging.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production LLM feature
- Output feeds another system (JSON, DB writes, customs filings)

❌ Avoid when:
- Over-engineering a demo with circuit breakers and multi-provider fallbacks
- Blind retries on non-idempotent tool calls (payments, emails) without idempotency keys

---

## 📊 Visual Diagram
```
 call LLM ─> error? ──no──> validate schema ──ok──> return
               │                 │fail (soft)
              yes                └──> retry ──> fallback
               │
        ┌──────┴────────┐
   retryable        non-retryable (400/401)
   (429/5xx/timeout)       │
        │               log + fix + alert
   backoff+jitter
        │
   attempts left? ─no─> fallback model ─no─> graceful error + request_id
```

---

## 💰 Cost Impact
- Retries cost tokens: each retry of a 500-input-token call on gpt-4o-mini costs about $0.00008. A retry storm of 1M extra calls is roughly $80.
- Failed streamed calls may still bill for generated tokens.
- Optimise: cap attempts, validate cheaply before retrying, use structured outputs to cut format errors, and set `max_tokens` so a runaway generation cannot burn budget.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Retryable error | Temporary failure | अस्थायी error |
| Soft error | Bad output with HTTP 200 | HTTP 200 पर खराब output |
| Silent error | Wrong but valid-looking answer | गलत पर सही दिखने वाला जवाब |
| Backoff | Increasing wait between retries | Retries के बीच बढ़ता इंतज़ार |
| Jitter | Random delay added | जोड़ी गई random देरी |
| Circuit breaker | Stops calls after repeated failures | बार-बार failure पर calls रोकना |
| Fingerprint | Key to group same errors | Same errors को group करने की key |

---

## ⚡ 3-Line Summary
English: Track hard, soft and silent errors separately. Retry only transient failures with backoff and jitter, validate outputs with schemas, and fall back safely. Log with request ids and alert on error types.
Hindi: Hard, soft और silent errors अलग track करो। सिर्फ transient failures को backoff और jitter से retry करो, schema से output validate करो और सुरक्षित fallback रखो। request id के साथ log करो और error types पर alert लगाओ।

---

## ➡️ Next Topic
**437. Token Usage Monitoring** — watching input/output/cached tokens to catch prompt bloat and cost spikes early.
