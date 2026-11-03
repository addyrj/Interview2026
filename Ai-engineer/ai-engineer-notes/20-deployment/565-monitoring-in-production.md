---

# 565. Monitoring in Production
# हिंदी में: Production में Monitoring

---

## 🔵 Simple Definition (English)
Monitoring means continuously measuring a live AI app: latency, errors, token usage, cost, and answer quality, so you detect problems before users complain. It combines metrics (numbers), logs (events), and traces (one request's path through retrieval, LLM, and tools).

## 🔵 सरल परिभाषा (Hindi)
Monitoring का मतलब live AI app को लगातार मापना: latency, errors, token usage, cost और answer quality, ताकि users की शिकायत से पहले दिक्कत पकड़ में आए। इसमें metrics (numbers), logs (events) और traces (एक request का पूरा रास्ता: retrieval, LLM, tools) शामिल हैं।

---

## 🔴 Problem it Solves
Normal software fails loudly (HTTP 500). LLM apps fail silently: the API returns 200 OK but the answer is wrong, hallucinated, or truncated. Latency spikes, provider outages, retrieval returning nothing, prompt drift and cost explosions all go unnoticed without dedicated monitoring.

## 🔴 यह क्यों बना? (Hindi)
Normal software जोर से fail होता है (HTTP 500)। LLM apps चुपचाप fail होते हैं: API 200 OK देती है पर answer गलत, hallucinated या अधूरा होता है। बिना monitoring के latency spike, provider outage, खाली retrieval, prompt drift और cost explosion पता नहीं चलते।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Instrument each request: start a trace ID (request_id)
Step 2 → Record per-step spans: retrieval, rerank, LLM call, tools
Step 3 → Emit metrics: latency (p50/p95/p99), error rate, tokens in/out, cost, cache hit rate
Step 4 → Log structured JSON (request_id, model, prompt_version, status) - no raw PII
Step 5 → Sample responses for quality scoring (LLM-as-judge, user thumbs up/down)
Step 6 → Export to a backend (Prometheus + Grafana, OpenTelemetry, LangSmith, Langfuse)
Step 7 → Define SLOs and alerts (p95 < 4s, error rate < 1%, daily cost < budget)
Step 8 → On alert: dashboard -> trace -> root cause -> rollback or fix
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर request पर trace ID (request_id) बनाओ
Step 2 → हर step का span record करो: retrieval, rerank, LLM call, tools
Step 3 → Metrics भेजो: latency (p50/p95/p99), error rate, tokens, cost, cache hit rate
Step 4 → Structured JSON logs (request_id, model, prompt_version, status) - raw PII नहीं
Step 5 → Quality scoring के लिए responses sample करो (LLM-as-judge, thumbs up/down)
Step 6 → Backend में export: Prometheus + Grafana, OpenTelemetry, LangSmith, Langfuse
Step 7 → SLOs और alerts तय करो (p95 < 4s, error < 1%, daily cost < budget)
Step 8 → Alert आने पर dashboard -> trace -> root cause -> rollback/fix
```

---

## 🟡 Real World Example
**Tariff Classification System**: Dashboard shows p95 latency jumped from 3 s to 9 s at 14:00. The trace shows the vector DB step is fine but the LLM step is slow: provider degradation. An alert fires, the router switches to a fallback model. Separately, the "retrieval returned 0 chunks" rate rises from 1% to 12% after a new index load, caught by a custom metric, and the team rolls back the index.

**Zomato-style**: Monitoring "search -> LLM recommendation" shows the peak dinner hour doubles token usage; they add caching before the next peak.

## 🟡 Real Example Hindi mein
**Tariff System**: Dashboard में 14:00 पर p95 latency 3 s से 9 s हो गई। Trace दिखाता है कि vector DB ठीक है पर LLM step धीमा है: provider degradation। Alert आता है और router fallback model पर चला जाता है। अलग से, नए index load के बाद "retrieval ने 0 chunks दिए" rate 1% से 12% हो गया, custom metric ने पकड़ा, और team ने index rollback किया।

**Zomato-style**: "search -> LLM recommendation" की monitoring से दिखा कि dinner peak पर token usage दोगुना होता है; अगले peak से पहले caching जोड़ी गई।

---

## 💻 Code Example — Basic
```python
# Basic metrics collector (pure Python, runs directly)
import statistics                                # for percentiles
import time                                      # for timing
from collections import defaultdict              # counters


class Metrics:
    def __init__(self) -> None:
        self.latencies: list[float] = []         # seconds per request
        self.counters: dict[str, int] = defaultdict(int)   # named counters

    def record(self, seconds: float, ok: bool, tokens_in: int, tokens_out: int) -> None:
        self.latencies.append(seconds)                      # store latency
        self.counters["requests"] += 1                      # total count
        self.counters["errors"] += 0 if ok else 1           # failed count
        self.counters["tokens_in"] += tokens_in             # input tokens
        self.counters["tokens_out"] += tokens_out           # output tokens

    def p95(self) -> float:
        if len(self.latencies) < 2:                         # need at least 2 points
            return self.latencies[0] if self.latencies else 0.0
        return statistics.quantiles(self.latencies, n=20)[-1]   # 95th percentile

    def summary(self) -> dict[str, float]:
        n = self.counters["requests"] or 1                  # avoid divide by zero
        return {"p95_s": round(self.p95(), 3),
                "error_rate": self.counters["errors"] / n,
                "avg_tokens": (self.counters["tokens_in"] + self.counters["tokens_out"]) / n}


m = Metrics()                                               # create collector
for i in range(30):                                         # simulate 30 requests
    start = time.perf_counter()                             # start timer
    time.sleep(0.001)                                       # fake work
    m.record(time.perf_counter() - start, ok=(i % 10 != 0), tokens_in=500, tokens_out=120)
print(m.summary())                                          # print dashboard numbers
```

## 💻 Code Example — Advanced
```python
# Production style: async context-manager tracing + Prometheus metrics + structured logs
from __future__ import annotations
import contextlib                                # async context manager helper
import json                                      # structured logging
import logging                                   # stdlib logging
import time                                      # timing
import uuid                                      # request ids
from typing import AsyncIterator                 # type hint

# prometheus_client is a real, widely used library: pip install prometheus-client
from prometheus_client import Counter, Histogram

LLM_LATENCY = Histogram("llm_latency_seconds", "LLM call latency",
                        ["model", "prompt_version"],
                        buckets=(0.5, 1, 2, 4, 8, 16, 32))           # latency buckets
LLM_TOKENS = Counter("llm_tokens_total", "Tokens used", ["model", "direction"])
LLM_ERRORS = Counter("llm_errors_total", "LLM errors", ["model", "error_type"])

log = logging.getLogger("llm")                   # app logger


@contextlib.asynccontextmanager
async def traced_llm_call(model: str, prompt_version: str) -> AsyncIterator[dict]:
    """Wrap an LLM call: time it, count errors, emit one JSON log line."""
    ctx = {"request_id": str(uuid.uuid4()), "model": model,
           "prompt_version": prompt_version, "tokens_in": 0, "tokens_out": 0}
    start = time.perf_counter()                  # start timer
    try:
        yield ctx                                # caller fills tokens in ctx
        status = "ok"
    except Exception as exc:                     # classify and re-raise
        status = type(exc).__name__
        LLM_ERRORS.labels(model, status).inc()   # count error type
        raise
    finally:
        elapsed = time.perf_counter() - start    # total seconds
        LLM_LATENCY.labels(model, prompt_version).observe(elapsed)
        LLM_TOKENS.labels(model, "in").inc(ctx["tokens_in"])
        LLM_TOKENS.labels(model, "out").inc(ctx["tokens_out"])
        log.info(json.dumps({**ctx, "status": status, "latency_s": round(elapsed, 3)}))
```

---

## 🟠 FastAPI Integration
Add a middleware for request IDs and expose `/metrics` for Prometheus to scrape; wrap LLM calls with the tracer.

```python
from fastapi import FastAPI, Request, Response         # framework
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST   # exposition

app = FastAPI()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("x-request-id", str(uuid.uuid4()))   # reuse or create id
    response = await call_next(request)                            # run the route
    response.headers["x-request-id"] = rid                         # return id to client
    return response


@app.post("/classify")
async def classify(item: str) -> dict:
    async with traced_llm_call("gpt-4o-mini", "v3") as ctx:        # monitored section
        # resp = await client.chat.completions.create(...)
        ctx["tokens_in"], ctx["tokens_out"] = 480, 60              # fill from resp.usage
        return {"hs_code": "8517.13", "tokens": ctx["tokens_in"] + ctx["tokens_out"]}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)   # Prometheus scrape
```

---

## 🔗 LangChain / LangGraph Connection
Set LangSmith env vars (`LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY=...`) and every chain/graph run is traced automatically with per-node latency and token counts. Langfuse offers a `CallbackHandler` for the same. You can also write a custom callback handler to feed Prometheus.

```python
from langchain_core.callbacks import AsyncCallbackHandler   # base class


class MetricsHandler(AsyncCallbackHandler):
    async def on_llm_end(self, response, **kwargs) -> None:        # called after each LLM call
        usage = (response.llm_output or {}).get("token_usage", {}) # provider-dependent shape
        LLM_TOKENS.labels("langchain", "in").inc(usage.get("prompt_tokens", 0))
        LLM_TOKENS.labels("langchain", "out").inc(usage.get("completion_tokens", 0))

# await chain.ainvoke(inputs, config={"callbacks": [MetricsHandler()]})
```
(The token_usage shape varies by provider; illustrative.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Monitoring only HTTP status and latency.
✅ Correct: also track quality (empty retrieval rate, judge score, thumbs-down rate) and cost per request.

```python
# Wrong
if response.status_code == 200: ok += 1
# Right
if response.status_code == 200 and n_chunks > 0 and judge_score >= 0.7: good += 1
```

❌ Mistake 2: Logging raw prompts with customer data (PII, trade secrets).
✅ Correct: redact or hash, log IDs and metadata, sample full text under access control.

❌ Mistake 3: Alerting on averages. Use p95/p99, since a few very slow requests hurt users.

---

## 🧠 Tricky Interview Question
**Q**: "Dashboards are all green (latency, errors), but support says answers got worse this week. What do you check?"

**Answer**: Green infra metrics do not measure quality. Check: provider model alias changed silently, prompt or index version changed (log versions), retrieval hit-rate and chunk scores dropped, input distribution shifted (new product categories), context truncation (token counts near limit), and user feedback trends. Replay a golden set against production nightly and alert on score regression. Add online sampling with LLM-as-judge.

---

## ⚫ Interview Questions + Answers

Q1: What are the three pillars of observability?
A1: Metrics, logs, and traces.

Q2: Why p95 instead of average latency?
A2: Averages hide the slow tail. p95 means 95% of requests are faster than this value, which reflects user pain better.

Q3: What LLM-specific metrics matter?
A3: Tokens in/out, cost per request, time to first token (streaming), tool-call failure rate, retrieval hit rate, guardrail triggers, hallucination/judge scores, cache hit rate.

Q4: How do you monitor quality without labelled data?
A4: Sample production traffic, score with LLM-as-judge against rubrics, collect user feedback, track proxy signals (retries, rephrased questions, thumbs down), and compare versions on the same sample.

Q5: (Hard) How do you avoid privacy risk while debugging with traces?
A5: Redact PII before logging, store full traces short-term with access control, hash user IDs, keep retention limits, and let engineers view raw text only via audited tooling. Consider on-prem tracing for sensitive data.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production LLM app, especially with cost or compliance exposure

❌ Avoid when:
- Over-instrumenting a prototype; start with logs plus token counts

---

## 📊 Visual Diagram
```
 Request ─► API ─► Retrieval ─► LLM ─► Response
              │        │          │
              ▼        ▼          ▼
            spans    spans      spans + tokens
              └────────┴──────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Metrics         Logs          Traces
   (Prometheus)   (JSON, ELK)   (LangSmith/OTel)
        └──────────────┬──────────────┘
                       ▼
              Dashboard + Alerts ─► On-call ─► Rollback / Fix
```

---

## 💰 Cost Impact
- Telemetry is cheap, but LLM-as-judge scoring costs tokens: judging 5% of 1M requests/month with ~1,500 tokens each is 75M tokens (illustrative; at $0.15/1M input about $11).
- Optimise: sample, use a small judge model, judge only flagged requests (thumbs down, low retrieval score), batch offline jobs, keep log retention short.
- Monitoring itself finds waste: oversized prompts, missing cache, retry storms.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Metric | Numeric measurement over time | समय के साथ number |
| Trace | One request's path across steps | Request का पूरा रास्ता |
| Span | One step inside a trace | Trace का एक step |
| p95 | 95th percentile latency | 95% requests से धीमा नहीं |
| SLO | Target reliability goal | Reliability लक्ष्य |
| LLM-as-judge | LLM scores another LLM's answer | LLM से answer का मूल्यांकन |

---

## ⚡ 3-Line Summary
English: Monitor latency percentiles, errors, tokens, cost, and quality, not just HTTP status. Use traces to see each step and structured logs with version tags. Alert on SLOs and sampled quality scores, then roll back quickly.
Hindi: सिर्फ HTTP status नहीं, latency percentiles, errors, tokens, cost और quality monitor करो। हर step देखने के लिए traces और version tags वाले structured logs रखो। SLOs और quality scores पर alert लगाओ और जल्दी rollback करो।

---

## ➡️ Next Topic
**566. Cost Monitoring in Production** — zoom into the money side: per-request, per-user, and per-feature cost tracking with budgets and alerts.
