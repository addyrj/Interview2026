---

# 267. LangChain Error Handling
# हिंदी में: LangChain Error Handling (Retry, Fallback, Timeout)

---

## 🔵 Simple Definition (English)
LangChain error handling is the set of tools that keep a chain alive when something fails: `.with_retry()` (try again), `.with_fallbacks()` (switch to a backup model/chain), timeouts and `max_retries` on models, `OutputParserException` handling for bad LLM output, and `return_exceptions=True` for batches.

## 🔵 सरल परिभाषा (Hindi)
LangChain error handling उन tools का set है जो कुछ fail होने पर भी chain को ज़िंदा रखते हैं: `.with_retry()` (दोबारा कोशिश), `.with_fallbacks()` (backup model/chain पर switch), timeouts और model पर `max_retries`, खराब LLM output के लिए `OutputParserException` handling, और batch में `return_exceptions=True`।

---

## 🔴 Problem it Solves
LLM apps fail in many ways that normal APIs do not: rate limit (429), provider outage (5xx), timeouts, content-filter refusals, context-length errors, and the model returning invalid JSON. Without handling, one failure becomes a 500 error for the user or kills a 500-row batch job.

## 🔴 यह क्यों बना? (Hindi)
LLM apps कई ऐसे तरीकों से fail होते हैं जो सामान्य APIs में नहीं होते: rate limit (429), provider outage (5xx), timeout, content-filter refusal, context-length error, और model का invalid JSON लौटाना। Handling के बिना एक failure user को 500 error देता है या 500-row batch job को मार देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Classify the error: transient (429, 5xx, timeout) vs permanent (400, auth, bad prompt)
Step 2 → Transient: retry with exponential backoff + jitter  -> .with_retry(...)
Step 3 → Still failing: switch to a fallback (other model/provider/cached answer) -> .with_fallbacks([...])
Step 4 → Bad output format: catch OutputParserException, retry once with the error shown to the LLM
Step 5 → Set timeouts everywhere (model timeout + overall deadline)
Step 6 → Batch: return_exceptions=True so one row cannot kill the batch
Step 7 → Log + count errors (traces, metrics) and return a safe message to the user
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Error पहचानो: transient (429, 5xx, timeout) या permanent (400, auth, गलत prompt)
Step 2 → Transient: exponential backoff + jitter के साथ retry -> .with_retry(...)
Step 3 → फिर भी fail: fallback (दूसरा model/provider/cached answer) -> .with_fallbacks([...])
Step 4 → Output format गलत: OutputParserException पकड़ो, error दिखाकर LLM से एक बार फिर माँगो
Step 5 → हर जगह timeout लगाओ (model timeout + पूरी request का deadline)
Step 6 → Batch: return_exceptions=True ताकि एक row पूरे batch को न मारे
Step 7 → Error log/count करो और user को safe message दो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Primary model `gpt-4o` returns 429 during peak hours. The chain retries twice (1 s, 2 s + jitter), then falls back to `gpt-4o-mini`, and if that also fails, to a deterministic keyword lookup table ("earbuds" -> 8518.30). The officer always gets *some* answer, flagged "low confidence". If the LLM returns broken JSON like `{"hs_code": "8518.30"` (cut off), the parser raises `OutputParserException`; the chain retries once with the error message appended.

**Zomato-style**: If the AI recommender times out, show the "popular near you" list. **Amazon-style**: If the summary model fails, show raw top reviews.

## 🟡 Real Example Hindi mein
**Tariff System**: Peak hours में primary model `gpt-4o` 429 देता है। Chain दो बार retry करती है (1 s, 2 s + jitter), फिर `gpt-4o-mini` पर fallback, और वह भी fail हो तो deterministic keyword table ("earbuds" -> 8518.30) से जवाब। Officer को हमेशा कुछ न कुछ answer मिलता है, "low confidence" flag के साथ। LLM अधूरा JSON लौटाए तो parser `OutputParserException` देता है; chain error message जोड़कर एक बार फिर कोशिश करती है।

**Zomato-style**: AI recommender timeout हो तो "आपके पास popular" list दिखाओ। **Amazon-style**: Summary model fail हो तो top reviews दिखाओ।

---

## 💻 Code Example — Basic
```python
# Basic retry + fallback -- runs OFFLINE with fake functions (no API key)
# pip install langchain-core
from langchain_core.runnables import RunnableLambda               # wrap functions as Runnables

calls: dict[str, int] = {"primary": 0}                            # counter to show retries

def flaky_primary(product: str) -> str:                           # pretend "gpt-4o" that fails twice
    calls["primary"] += 1                                         # count the attempt
    if calls["primary"] < 3:                                      # first 2 attempts fail
        raise TimeoutError("simulated provider timeout")          # transient error
    return f"{product}: HS 8518.30 (primary)"                     # 3rd attempt works

def always_down(product: str) -> str:                             # pretend a dead model
    raise ConnectionError("provider down")                        # permanent failure here

def backup_model(product: str) -> str:                            # cheap backup
    return f"{product}: HS 8518.30 (backup)"                      # always works

# 1) with_retry: retry only on TimeoutError, 3 tries, no sleeping so the demo is fast
primary = RunnableLambda(flaky_primary).with_retry(
    retry_if_exception_type=(TimeoutError,),                      # only retry transient errors
    stop_after_attempt=3,                                         # total attempts (incl. first)
    wait_exponential_jitter=False,                                # disable waits for the demo
)
print(primary.invoke("earbuds"), "| attempts:", calls["primary"]) # works on attempt 3

# 2) with_fallbacks: if the main runnable raises, try the next one
chain = RunnableLambda(always_down).with_fallbacks([RunnableLambda(backup_model)])
print(chain.invoke("laptop"))                                     # served by backup

# 3) Permanent errors must NOT be retried: ValueError is not in the retry list
def bad_input(product: str) -> str:                               # raises a permanent error
    raise ValueError("empty product")                             # bug in input, retry is useless
try:
    RunnableLambda(bad_input).with_retry(
        retry_if_exception_type=(TimeoutError,), stop_after_attempt=3, wait_exponential_jitter=False
    ).invoke("")                                                  # fails immediately
except ValueError as exc:                                         # surfaced at once
    print("not retried ->", exc)                                  # confirms no retry
```

## 💻 Code Example — Advanced
```python
# Production: retry -> model fallback -> rule-based fallback, parser repair, async, safe result
# pip install langchain-openai langchain-core pydantic
import asyncio                                                    # async runtime
import logging                                                    # logging
from typing import Literal                                        # literal types

import httpx                                                      # transport errors raised by SDKs
from langchain_core.exceptions import OutputParserException       # bad LLM output error
from langchain_core.output_parsers import PydanticOutputParser    # parse JSON -> model
from langchain_core.prompts import ChatPromptTemplate             # prompt
from langchain_core.runnables import RunnableLambda               # wrap functions
from langchain_openai import ChatOpenAI                           # model
from openai import APIConnectionError, APITimeoutError, RateLimitError  # real exception classes
from pydantic import BaseModel, Field                             # pydantic v2

logger = logging.getLogger("tariff.errors")                       # logger


class HSResult(BaseModel):                                        # expected structure
    hs_code: str = Field(pattern=r"^\d{4}\.\d{2}$")               # e.g. 8518.30
    confidence: float = Field(ge=0, le=1)                         # 0..1


parser = PydanticOutputParser(pydantic_object=HSResult)           # validates the LLM JSON
prompt = ChatPromptTemplate.from_messages([                       # prompt includes format rules
    ("system", "Classify the product. {format_instructions}"),
    ("user", "{product}"),
]).partial(format_instructions=parser.get_format_instructions())

TRANSIENT = (RateLimitError, APITimeoutError, APIConnectionError, httpx.TransportError)  # retry-worthy

# max_retries=0 on the model: we control retries ONCE, in the chain (avoid retry x retry)
big = ChatOpenAI(model="gpt-4o", temperature=0, timeout=20, max_retries=0)
small = ChatOpenAI(model="gpt-4o-mini", temperature=0, timeout=20, max_retries=0)

def keyword_fallback(inputs: dict[str, str]) -> HSResult:         # last resort: no LLM
    table = {"earbuds": "8518.30", "laptop": "8471.30"}           # tiny lookup table
    for word, code in table.items():                              # scan keywords
        if word in inputs["product"].lower():                     # simple match
            return HSResult(hs_code=code, confidence=0.4)         # low confidence flag
    return HSResult(hs_code="9999.00", confidence=0.0)            # "unknown" marker

def make(llm: ChatOpenAI):                                        # build one tier of the chain
    return (prompt | llm | parser).with_retry(                    # retry the whole tier
        retry_if_exception_type=TRANSIENT,                        # only transient errors
        wait_exponential_jitter=True,                             # backoff with jitter
        stop_after_attempt=3,                                     # max 3 tries
    )

chain = make(big).with_fallbacks(                                 # fallbacks are tried in order
    [make(small), RunnableLambda(keyword_fallback)],              # then mini, then rules
    exceptions_to_handle=(Exception,),                            # which errors trigger fallback
)


async def classify_safe(product: str) -> tuple[HSResult, Literal["ok", "degraded"]]:
    """Never raises: always returns (result, status)."""
    try:
        res = await asyncio.wait_for(chain.ainvoke({"product": product}), timeout=60)  # overall deadline
        return res, "ok"                                          # normal path
    except OutputParserException as exc:                          # every tier gave bad JSON
        logger.error("parse failure: %s", exc)                    # log
    except asyncio.TimeoutError:                                  # deadline hit
        logger.error("deadline exceeded")                         # log
    except Exception:                                             # anything else
        logger.exception("classification failed")                 # log with traceback
    return keyword_fallback({"product": product}), "degraded"     # safe default
```

---

## 🟠 FastAPI Integration
Map internal errors to the right HTTP codes: validation -> 422 (automatic), upstream rate limit -> 503 + `Retry-After`, timeout -> 504, parse failure -> 502. Never return raw provider messages (they can leak keys/prompt details).

```python
# FastAPI + safe error mapping
from fastapi import FastAPI, HTTPException                        # framework
from fastapi.responses import JSONResponse                        # custom responses
from openai import RateLimitError                                 # SDK error type
from pydantic import BaseModel, Field                             # validation

app = FastAPI()                                                   # app instance

class Req(BaseModel):                                             # input
    product: str = Field(min_length=2, max_length=300)            # bounds

@app.exception_handler(RateLimitError)                            # global handler for 429 from provider
async def rate_limit_handler(request, exc: RateLimitError) -> JSONResponse:
    return JSONResponse(                                          # tell the client to retry later
        status_code=503,
        content={"detail": "Model busy, retry shortly"},
        headers={"Retry-After": "5"},
    )

@app.post("/classify")                                            # route
async def classify(req: Req) -> dict[str, object]:
    result, status = await classify_safe(req.product)             # from Advanced above (never raises)
    if status == "degraded":                                      # still useful but weaker
        return {"hs_code": result.hs_code, "confidence": result.confidence, "degraded": True}
    return {"hs_code": result.hs_code, "confidence": result.confidence, "degraded": False}
```

---

## 🔗 LangChain / LangGraph Connection
- **Runnable level**: `.with_retry()`, `.with_fallbacks()`, `RunnableConfig(callbacks=...)`; `chain.with_config(run_name="classify")` helps find failures in traces.
- **Model level**: `ChatOpenAI(max_retries=..., timeout=...)` retries inside the SDK. Pick ONE place to retry; otherwise 3 x 3 = 9 attempts.
- **Parser level**: `OutputFixingParser` / `RetryOutputParser` (in `langchain` package) call the LLM again to repair bad output. Or use `.with_structured_output(HSResult)`, which relies on the provider's JSON/tool mode and fails less.
- **LangGraph**: wrap a node with a `RetryPolicy` (`graph.add_node("n", fn, retry_policy=RetryPolicy(max_attempts=3))`), or add a conditional edge to an "error_handler" node. Checkpointers let you resume from the failed step instead of restarting.

```python
# LangGraph node retry policy (current API)
from langgraph.types import RetryPolicy                           # retry config for nodes
# builder.add_node("classify", classify_node, retry_policy=RetryPolicy(max_attempts=3))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Retrying everything, including permanent errors
```python
# Wrong -- retries a 400 "context length exceeded" 3 times, wasting time and money
chain.with_retry(stop_after_attempt=3)          # default retries on any Exception

# Right -- only retry transient errors
chain.with_retry(retry_if_exception_type=(RateLimitError, APITimeoutError), stop_after_attempt=3)
```

❌ Mistake 2: Nested retries (SDK retries x chain retries)
```python
# Wrong -- 3 SDK retries inside 3 chain retries = up to 9 calls per request
llm = ChatOpenAI(max_retries=3); chain = (prompt | llm).with_retry(stop_after_attempt=3)

# Right -- one layer
llm = ChatOpenAI(max_retries=0); chain = (prompt | llm).with_retry(stop_after_attempt=3)
```

❌ Mistake 3: `except Exception: pass` - silent failures. Always log and return an explicit degraded status.

---

## 🧠 Tricky Interview Question

**Q**: "You added `.with_fallbacks([gpt-4o-mini])` to a chain `prompt | gpt-4o | parser`. Yet when `gpt-4o` returns bad JSON, the user still gets an error. Why, and what is the fix?"

**Answer**: The fallback was attached only to the LLM step, but the failure happens later, in the **parser**. Fallbacks protect only the runnable they wrap. Because `with_fallbacks` was applied to the model alone, the parser exception is outside it. Fix: wrap the whole unit `(prompt | llm | parser).with_fallbacks([(prompt | small | parser)])` so a parse failure triggers the fallback tier, or use `exceptions_to_handle` to include `OutputParserException`. Also better: use `with_structured_output` to reduce parse failures at the source.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `with_retry` and `with_fallbacks`?
A1: `with_retry` runs the *same* runnable again (good for transient errors). `with_fallbacks` switches to a *different* runnable (backup model/chain) after the main one fails (good for outages or persistent failures).

Q2: Which errors should be retried?
A2: Transient ones: 429 rate limit, 5xx, timeouts, connection resets. Not retried: 400 bad request, 401/403 auth, context-length exceeded, validation errors - they will fail the same way.

Q3: What is exponential backoff with jitter?
A3: Wait time doubles each attempt (1 s, 2 s, 4 s) plus a random amount. Jitter stops many clients from retrying at the same instant (thundering herd). LangChain's `wait_exponential_jitter=True` does this.

Q4: How do you handle invalid JSON from an LLM?
A4: Prefer `with_structured_output(PydanticModel)` (provider-enforced). Otherwise catch `OutputParserException`, retry once with the error message in the prompt (or `OutputFixingParser`), validate with Pydantic, and have a degraded fallback.

Q5 (Hard): Design error handling for a 100K-row batch classification job.
A5: Use `abatch(..., max_concurrency=N, return_exceptions=True)` (or the provider Batch API); retry transient errors with jitter inside each item; write results to storage as they complete (checkpoint) so a crash resumes instead of restarts; collect failed rows into a dead-letter list for a second pass with a different model; keep a circuit breaker (stop sending if error rate > X% for Y seconds); log metrics (success rate, retries, cost). Idempotent writes (keyed by row id) make re-runs safe.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Calling any external LLM (always set timeout + limited retries)
- A user-facing path needs high availability (fallback tiers)
- Bulk jobs (per-item error isolation)

❌ Avoid when:
- Retrying non-idempotent tool calls (e.g. "send email", "charge card") - a retry can duplicate the action
- Infinite retries - they hide outages and burn money
- Fallback to a model with a very different quality without flagging it to the user

---

## 📊 Visual Diagram
```
 request
    │
    ▼
┌───────────────┐ fail (429/5xx) ┌───────────────────────────┐
│ gpt-4o tier   │───────────────►│ retry x3 (1s, 2s, 4s+jit) │
└──────┬────────┘                └─────────────┬─────────────┘
       │ ok                                    │ still failing
       ▼                                       ▼
   response ◄──────────────────────── ┌───────────────┐
       ▲                              │ gpt-4o-mini   │ (fallback 1)
       │                              └──────┬────────┘
       │                                     │ fails
       │                              ┌──────▼────────┐
       └──────────────────────────────│ keyword table │ (fallback 2, degraded=true)
                                      └───────────────┘
```

---

## 💰 Cost Impact
- Each retry of a call that reached the model can be billed again (input tokens at least). Max 3 attempts keeps worst case at ~3x for failing calls only.
- Failed 429s before processing usually cost nothing, but timeouts after a long generation may still be billed.
- Fallback to `gpt-4o-mini` is also a cost saver (about 30x cheaper than gpt-4o) but accuracy may drop - log the tier used.
- Parser-repair calls add tokens (original prompt + bad output + instructions). Use `with_structured_output` to avoid them. Rough number: a repair retry adds ~500 input tokens = $0.000075 on gpt-4o-mini.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Retry | Run again after failure | फिर से कोशिश |
| Fallback | Backup option if main fails | Backup विकल्प |
| Transient error | Temporary failure (429, 5xx) | अस्थायी error |
| Backoff + jitter | Growing random wait between tries | बढ़ता random इंतज़ार |
| Timeout | Max time allowed for a call | समय सीमा |
| OutputParserException | LLM output could not be parsed | Output parse नहीं हुआ |
| Degraded mode | Weaker but working answer | कमज़ोर पर चालू जवाब |
| Circuit breaker | Stop calling a failing service | खराब service को कुछ देर बंद रखना |

---

## ⚡ 3-Line Summary
English: Retry only transient errors, with backoff and jitter, in ONE layer. Use `with_fallbacks` for backup models or rule-based answers and wrap the full prompt-model-parser unit. Always set timeouts, isolate per-item errors in batches, and return a safe message.
Hindi: सिर्फ transient errors को retry करो, backoff और jitter के साथ, और सिर्फ एक layer में। Backup model या rule-based answer के लिए `with_fallbacks` use करो और पूरा prompt-model-parser unit wrap करो। Timeout हमेशा लगाओ, batch में हर item का error अलग रखो और user को safe message दो।

---

## ➡️ Next Topic
**268. LangChain Caching** - avoid paying twice for the same prompt using in-memory, SQLite and Redis caches.
