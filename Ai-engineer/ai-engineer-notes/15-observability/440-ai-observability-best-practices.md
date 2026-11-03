
# 440. AI Observability Best Practices
# हिंदी में: AI Observability की Best Practices

---

## 🔵 Simple Definition (English)
AI observability best practices are the habits that let you see, measure and debug an LLM app in production: trace every request, track cost, latency, errors and quality, protect private data, alert on problems, and feed real failures back into tests.

## 🔵 सरल परिभाषा (Hindi)
AI observability best practices वे आदतें हैं जिनसे production में LLM app को देखा, मापा और debug किया जा सके: हर request trace करो, cost, latency, errors और quality track करो, private data बचाओ, problems पर alert लगाओ और असली failures को tests में वापस डालो।

---

## 🔴 Problem it Solves
LLM apps fail quietly: a wrong answer is still HTTP 200. Costs spike from one looping agent. Quality drifts after a prompt or model change. Without structured observability you learn about issues from angry users. Best practices make failures visible, attributable and repeatable.

## 🔴 यह क्यों बना? (Hindi)
LLM apps चुपचाप fail होते हैं: ग़लत answer भी HTTP 200 होता है। एक looping agent से cost अचानक बढ़ जाती है। Prompt या model बदलने पर quality drift होती है। Observability के बिना issues का पता नाराज़ users से चलता है। Best practices failures को दिखाने योग्य, ज़िम्मेदार तक पहुँचाने योग्य और दोहराने योग्य बनाती हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Instrument every request end to end: one trace id, nested spans (retrieve, rerank, LLM, tools)
Step 2 → Tag traces: env, app version, prompt version, model, user/tenant id, session id
Step 3 → Record tokens (in/out), cost, latency (p50/p95/p99), time to first token, errors, retries
Step 4 → Score quality: user feedback, rule checks, LLM-as-judge on a sample, human review of failures
Step 5 → Redact PII before logging; set retention limits; control access
Step 6 → Dashboards + alerts (error rate, p95 latency, cost per day, quality score drop)
Step 7 → Turn bad traces into dataset rows -> regression evals in CI before each release
Step 8 → Review weekly: top cost drivers, top failures, drift
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर request end-to-end instrument करो: एक trace id, nested spans (retrieve, rerank, LLM, tools)
Step 2 → Traces tag करो: env, app version, prompt version, model, user/tenant id, session id
Step 3 → Tokens (in/out), cost, latency (p50/p95/p99), time to first token, errors, retries record करो
Step 4 → Quality score करो: user feedback, rule checks, sample पर LLM-as-judge, failures की human review
Step 5 → Logging से पहले PII redact करो; retention limits रखो; access control रखो
Step 6 → Dashboards + alerts (error rate, p95 latency, daily cost, quality score drop)
Step 7 → Bad traces को dataset rows बनाओ -> हर release से पहले CI में regression evals
Step 8 → हर हफ़्ते review: top cost drivers, top failures, drift
```

---

## 🟡 Real World Example
**Tariff Classification System**: After a prompt tweak, HS-code accuracy drops 4% but nothing crashes. Because every trace carries `prompt_version`, the dashboard shows the drop starts exactly at v12. A cost alert also catches one importer's script sending 50-page PDFs in a loop. Wrong-code traces are exported to a dataset used in the CI eval gate.

**Zomato AI**: A p95 latency alert fires when a reranker slows; the span breakdown pinpoints it in minutes.

## 🟡 Real Example Hindi mein
**Tariff System**: Prompt tweak के बाद HS-code accuracy 4% गिरती है पर कुछ crash नहीं होता। हर trace में `prompt_version` होने से dashboard दिखाता है कि गिरावट ठीक v12 से शुरू हुई। Cost alert एक importer की script को भी पकड़ता है जो loop में 50-page PDFs भेज रही थी। ग़लत-code traces dataset में export होकर CI eval gate में use होते हैं।

**Zomato AI**: Reranker धीमा होने पर p95 latency alert बजता है; span breakdown से मिनटों में कारण मिलता है।

---

## 💻 Code Example — Basic
```python
# Pure-Python observability basics: structured log line with tokens, cost, latency (runs as is)
import json  # structured logs
import time  # timing
from typing import Any  # type hints

PRICE_IN = 0.15 / 1_000_000  # illustrative $ per input token
PRICE_OUT = 0.60 / 1_000_000  # illustrative $ per output token


def log_call(tokens_in: int, tokens_out: int, started: float, **tags: Any) -> dict[str, Any]:
    """Build one structured record for an LLM call."""
    record = {
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),  # elapsed time
        "tokens_in": tokens_in,  # prompt tokens
        "tokens_out": tokens_out,  # completion tokens
        "cost_usd": round(tokens_in * PRICE_IN + tokens_out * PRICE_OUT, 8),  # estimated cost
        **tags,  # env, prompt_version, user_id...
    }
    print(json.dumps(record))  # one JSON line (ship to your log system)
    return record  # return for tests


if __name__ == "__main__":
    t0 = time.perf_counter()  # start timer
    time.sleep(0.01)  # pretend LLM call
    log_call(500, 120, t0, env="prod", prompt_version="v12", user_id="imp-42")  # emit record
```

## 💻 Code Example — Advanced
```python
# Production wrapper: PII redaction, sampling, error capture, async (pure Python; plug in Langfuse/LangSmith/OTel as sink)
import asyncio  # async
import logging  # logs
import random  # sampling
import re  # redaction
import time  # timing
from typing import Any, Awaitable, Callable  # types

logger = logging.getLogger("obs")  # logger
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")  # simple email pattern


def redact(text: str) -> str:
    """Mask emails before storing text in traces."""
    return EMAIL.sub("[EMAIL]", text)  # replace matches


async def traced_call(
    fn: Callable[[str], Awaitable[dict[str, Any]]],  # async LLM function returning text + usage
    prompt: str,  # user prompt
    *,
    sample_rate: float = 1.0,  # fraction of successful traces to keep
    tags: dict[str, str] | None = None,  # metadata
) -> dict[str, Any]:
    """Call fn, record metrics, never let observability break the request."""
    start = time.perf_counter()  # timer
    status = "ok"  # default status
    try:
        result = await fn(prompt)  # real call
        return result  # return untouched
    except Exception as exc:  # capture failure
        status = f"error:{type(exc).__name__}"  # error label
        raise  # re-raise to the caller
    finally:
        try:
            if status != "ok" or random.random() < sample_rate:  # always keep errors
                logger.info("trace %s", {
                    "status": status,  # outcome
                    "latency_ms": round((time.perf_counter() - start) * 1000, 2),  # time
                    "prompt": redact(prompt)[:500],  # redacted + truncated
                    **(tags or {}),  # extra tags
                })
        except Exception:  # observability must never crash the app
            logger.exception("trace logging failed")  # log and continue
```
Token usage: record `usage.prompt_tokens` and `completion_tokens` from the provider response on every call; this is the foundation for cost dashboards.

---

## 🟠 FastAPI Integration
```python
import time  # timing
import uuid  # request ids
from fastapi import FastAPI, Request  # web framework

app = FastAPI()  # app


@app.middleware("http")
async def obs_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())  # correlation id
    start = time.perf_counter()  # start timer
    response = await call_next(request)  # run route
    ms = round((time.perf_counter() - start) * 1000, 2)  # latency
    response.headers["x-request-id"] = request_id  # return id so support can find the trace
    print({"id": request_id, "path": request.url.path, "status": response.status_code, "ms": ms})  # log line
    return response  # send response
```
Pass `request_id` into your trace tool so a user's complaint maps to one trace.

---

## 🔗 LangChain / LangGraph Connection
Use callbacks (LangSmith, Langfuse) or OpenTelemetry to trace chains and graphs. Add metadata and tags via the config so every run is filterable by version and tenant.

```python
from langchain_openai import ChatOpenAI  # LLM

llm = ChatOpenAI(model="gpt-4o-mini")  # model
llm.invoke(
    "HS code for a laptop?",
    config={"tags": ["tariff", "prod"], "metadata": {"prompt_version": "v12", "tenant": "acme"}},  # filterable
)
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Logging only errors, not successful-but-wrong answers
✅ Correct: Add quality scores and user feedback to traces.
```python
# Wrong: if exception: log
# Right: log every request + attach score (thumbs, judge, rule check)
trace = {"hs_code": "8518.30", "valid_format": True, "user_feedback": None}
```

❌ Mistake 2: Storing raw prompts with personal or customs-confidential data
✅ Correct: Redact first, restrict access, set retention.
```python
# Wrong: logger.info(prompt)
# Right: logger.info(redact(prompt)[:500])
```

---

## 🧠 Tricky Interview Question
**Q**: "All your dashboards are green (no errors, normal latency), yet users say answers got worse this week. What do you do?"

**Answer**: Green infrastructure metrics do not measure answer quality. Check quality signals: user feedback rate, LLM-judge scores on sampled traces, and eval on a fixed golden set. Compare traces by `prompt_version`, `model`, retrieval index version and data source. Likely culprits: a prompt or model version change, a stale or re-indexed vector store, upstream data drift, or a silent provider model update. Add quality alerts, pin model versions, and run the golden set in CI and on a schedule.

---

## ⚫ Interview Questions + Answers

Q1: What are the minimum fields to log per LLM call?
A1: Trace id, model, prompt version, input/output (redacted), tokens in/out, cost, latency, status/error, user or tenant id.

Q2: Why track p95 and p99 latency, not just average?
A2: Averages hide slow tail requests that users feel; LLM latency has long tails.

Q3: What is sampling and when to use it?
A3: Keeping only a fraction of traces to control cost and storage, while always keeping errors and flagged requests.

Q4: How do you detect quality drift without human labels on everything?
A4: Sample traces for LLM-as-judge or rule checks, collect implicit user signals, and run a golden dataset regularly; alert on score drops.

Q5: Design observability for a multi-tenant RAG API.
A5: One trace per request with spans for retrieval, rerank and generation. Tag tenant, plan, prompt/model/index versions. Per-tenant cost and rate dashboards with budgets and alerts. PII redaction at ingestion, tenant-scoped access to traces. Retrieval metrics (hit rate, empty results), faithfulness scores on samples, user feedback loop, and CI evals using exported failures. Trace failures never block requests.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything user-facing or paid goes to production
- Multiple prompts, models or agents are involved
- Cost or compliance matters

❌ Avoid over-engineering when:
- Early prototype with one developer (basic logging is enough)
- Tracing every token of huge payloads with no sampling

---

## 📊 Visual Diagram
```
 Request --> [trace id + tags]
     |-- span: retrieve   (ms, hits)
     |-- span: rerank     (ms)
     |-- span: LLM        (tokens, cost, ms)
     '-- span: validate   (pass/fail)
             |
             v
   metrics + logs + scores --> dashboards --> alerts
             |
             v
     bad traces --> dataset --> CI evals --> safer release
```

---

## 💰 Cost Impact
Observability tools add storage and vendor cost, but they usually pay for themselves by exposing waste: oversized prompts, retry loops, expensive models on easy tasks. Track cost per request, per user, per feature.

Optimise: sample successful traces, truncate large payloads, set retention, alert on cost per hour (catches loops early), and use cheaper judge models on small samples. Always record token counts: they are the base of cost analysis.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | Record of one request | एक request का record |
| Span | A step inside a trace | Trace का एक step |
| p95 latency | 95% of calls are faster | 95% calls इससे तेज़ |
| Sampling | Keep only some traces | कुछ traces ही रखना |
| Golden set | Fixed eval dataset | तय eval dataset |
| Redaction | Mask sensitive data | संवेदनशील data छुपाना |
| Drift | Quality or data change over time | समय के साथ बदलाव |

---

## ⚡ 3-Line Summary
English: Trace everything with version tags, track tokens, cost, latency and quality. Redact PII, sample sensibly and alert on cost, latency and quality drops. Feed failures into regression evals.
Hindi: हर चीज़ version tags के साथ trace करो, tokens, cost, latency और quality track करो। PII redact करो, समझदारी से sampling करो और cost, latency व quality drop पर alert लगाओ। Failures को regression evals में डालो।

---

## ➡️ Next Topic
**441. LLM Caching — What + Why** — the next big lever after observability: stop paying twice for the same answer.
