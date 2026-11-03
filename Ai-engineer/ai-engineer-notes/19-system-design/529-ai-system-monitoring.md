
---

# 529. AI System Monitoring
# हिंदी में: AI System Monitoring

---

## 🔵 Simple Definition (English)
AI system monitoring means measuring a live LLM app so you know when it is slow, broken, expensive or giving worse answers. You track normal service metrics (latency, errors) plus AI-specific ones (tokens, cost, quality, guardrail blocks, retrieval hit quality) and alert on problems.

## 🔵 सरल परिभाषा (Hindi)
AI system monitoring का मतलब चलते हुए LLM app को measure करना है ताकि पता चले कब वह slow, broken, महँगा या खराब जवाब देने वाला हो गया। आप सामान्य service metrics (latency, errors) के साथ AI-specific metrics (tokens, cost, quality, guardrail blocks, retrieval quality) track करते हैं और समस्या पर alert लगाते हैं।

---

## 🔴 Problem it Solves
- LLM apps fail quietly: HTTP 200 with a wrong or hallucinated answer.
- Costs can double overnight from one prompt change or one noisy user.
- Without traces you cannot tell which step is slow: retrieval, reranker or the LLM.
- Model providers change behaviour and have outages; you need to notice first.

## 🔴 यह क्यों बना? (Hindi)
- LLM apps चुपचाप fail होते हैं: HTTP 200 पर गलत या hallucinated जवाब।
- एक prompt बदलाव या एक noisy user से cost रातों-रात दोगुनी हो सकती है।
- Traces के बिना पता नहीं चलता कौन सा step slow है: retrieval, reranker या LLM।
- Model providers behaviour बदलते हैं और outage होते हैं; आपको पहले पता चलना चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Instrument each request: request id, user/tenant id, model, prompt version
Step 2 → Record per-step timings (guard, retrieve, rerank, LLM) as spans (tracing)
Step 3 → Record counters: input tokens, output tokens, cost, errors, cache hits
Step 4 → Record quality signals: thumbs up/down, override rate, sampled LLM-judge score
Step 5 → Export to a metrics store (Prometheus, Datadog, CloudWatch, LangSmith, etc.)
Step 6 → Dashboards: p50/p95 latency, error rate, cost per request, quality over time
Step 7 → Alerts with thresholds (error > 2%, p95 > 5s, daily cost > budget, quality drop)
Step 8 → Review samples of real traffic weekly; add failures to the eval set
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → हर request instrument करो: request id, user/tenant id, model, prompt version
Step 2 → हर step का समय span की तरह record करो (guard, retrieve, rerank, LLM)
Step 3 → Counters record करो: input tokens, output tokens, cost, errors, cache hits
Step 4 → Quality signals record करो: thumbs up/down, override rate, sample का LLM-judge score
Step 5 → Metrics store में export करो (Prometheus, Datadog, CloudWatch, LangSmith आदि)
Step 6 → Dashboards: p50/p95 latency, error rate, cost per request, quality trend
Step 7 → Thresholds पर alerts (error > 2%, p95 > 5s, daily cost > budget, quality गिरे)
Step 8 → हर हफ्ते real traffic के samples देखो; failures को eval set में जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Dashboard shows p95 latency jumped from 3s to 9s at 2 pm. Per-step spans show the reranker is fine, but the LLM step grew because a new prompt version added a long legal appendix (input tokens per request jumped from 1,800 to 5,200). An alert on "tokens per request > 1.5x baseline" would have caught it in minutes. Separately, the "officer override rate" metric slowly rises after a tariff schedule update: the knowledge base is stale, so the team re-indexes.

**Amazon-style AI**: Monitor "answer groundedness" on a 2% sample of shopping-assistant answers using an LLM judge, and alert when the daily average drops.

## 🟡 Real Example Hindi mein
**Tariff System**: Dashboard दिखाता है कि दोपहर 2 बजे p95 latency 3s से 9s हो गई। Per-step spans बताते हैं reranker ठीक है, पर LLM step बढ़ा क्योंकि नए prompt version में लंबा legal appendix जुड़ गया (input tokens per request 1,800 से 5,200)। "tokens per request > 1.5x baseline" का alert मिनटों में पकड़ लेता। अलग से, tariff schedule update के बाद "officer override rate" धीरे-धीरे बढ़ता है: knowledge base पुराना है, इसलिए team re-index करती है।

**Amazon-style AI**: Shopping assistant के 2% sample पर LLM judge से "answer groundedness" monitor करो और daily average गिरे तो alert।

---

## 💻 Code Example — Basic
```python
# Basic: in-memory metrics collector (pure Python, no packages)
import statistics                                      # for percentiles
import time                                            # for timing
from collections import defaultdict                    # grouped lists

class Metrics:
    def __init__(self) -> None:
        self.latencies: list[float] = []               # seconds per request
        self.tokens: dict[str, int] = defaultdict(int) # 'input'/'output' totals
        self.errors = 0                                # failed requests
        self.requests = 0                              # all requests

    def record(self, seconds: float, in_tok: int, out_tok: int, ok: bool) -> None:
        self.requests += 1                             # count request
        self.latencies.append(seconds)                 # save latency
        self.tokens["input"] += in_tok                 # add input tokens
        self.tokens["output"] += out_tok               # add output tokens
        if not ok:
            self.errors += 1                           # count failure

    def p95(self) -> float:
        """95th percentile latency."""
        if len(self.latencies) < 2:
            return self.latencies[0] if self.latencies else 0.0
        return statistics.quantiles(self.latencies, n=20)[-1]  # last of 20 cuts = p95

    def cost(self, in_price: float, out_price: float) -> float:
        """Cost in USD, prices per 1M tokens (pass your own)."""
        return (self.tokens["input"] * in_price + self.tokens["output"] * out_price) / 1_000_000

if __name__ == "__main__":
    m = Metrics()                                      # new collector
    for i in range(50):                                # fake 50 requests
        m.record(0.5 + i * 0.02, 1800, 200, ok=(i % 25 != 0))
    print(f"requests={m.requests} errors={m.errors} p95={m.p95():.2f}s")
    print(f"cost=${m.cost(1.0, 4.0):.4f} (illustrative prices)")
```

## 💻 Code Example — Advanced
```python
# Advanced: async tracing context manager + threshold alerts (mock LLM, offline)
import asyncio                                         # async runtime
import logging                                         # emit structured logs
import time                                            # perf counter
from contextlib import asynccontextmanager             # async context manager
from dataclasses import dataclass, field               # trace container
from typing import AsyncIterator

log = logging.getLogger("monitor")

@dataclass
class Trace:
    request_id: str                                    # id tying all spans together
    spans: dict[str, float] = field(default_factory=dict)  # step -> seconds
    in_tokens: int = 0                                 # filled after LLM call
    out_tokens: int = 0

@asynccontextmanager
async def span(trace: Trace, name: str) -> AsyncIterator[None]:
    """Time one pipeline step, even if it raises."""
    start = time.perf_counter()                        # start timer
    try:
        yield                                          # run the step
    finally:
        trace.spans[name] = time.perf_counter() - start  # always record

ALERTS = {"max_total_s": 5.0, "max_in_tokens": 4000}   # example thresholds

def check_alerts(t: Trace) -> list[str]:
    """Return alert messages for this trace."""
    out: list[str] = []
    if sum(t.spans.values()) > ALERTS["max_total_s"]:  # too slow overall
        out.append("slow_request")
    if t.in_tokens > ALERTS["max_in_tokens"]:          # prompt too big
        out.append("token_spike")
    return out

async def handle(request_id: str) -> Trace:
    t = Trace(request_id)                              # new trace
    try:
        async with span(t, "retrieve"):
            await asyncio.sleep(0.02)                  # pretend vector search
        async with span(t, "llm"):
            await asyncio.sleep(0.05)                  # pretend LLM call
            t.in_tokens, t.out_tokens = 5200, 150      # token counts from usage field
    except Exception:
        log.exception("request failed id=%s", request_id)  # error is also a signal
        raise
    for alert in check_alerts(t):                      # evaluate thresholds
        log.warning("ALERT %s id=%s spans=%s", alert, request_id, t.spans)
    return t

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)            # show logs
    trace = asyncio.run(handle("req-1"))
    print({k: round(v, 3) for k, v in trace.spans.items()}, trace.in_tokens)
```

---

## 🟠 FastAPI Integration
Add one middleware that creates a request id and records latency, and expose a `/metrics` endpoint. The `prometheus_client` package is the common choice.

```python
# FastAPI + prometheus_client (pip install prometheus-client)
import time
from fastapi import FastAPI, Request, Response
from prometheus_client import (CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest)

app = FastAPI()
REQS = Counter("llm_requests_total", "Requests", ["route", "status"])   # counter
LAT = Histogram("llm_latency_seconds", "Latency", ["route"])            # histogram
TOKENS = Counter("llm_tokens_total", "Tokens", ["kind", "model"])       # in/out tokens

@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    start = time.perf_counter()                        # start timer
    status = "500"                                     # default if it raises
    try:
        response = await call_next(request)            # run route
        status = str(response.status_code)             # actual status
        return response
    finally:
        route = request.url.path                       # keep labels low-cardinality!
        LAT.labels(route).observe(time.perf_counter() - start)
        REQS.labels(route, status).inc()               # count by status

@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)  # scrape endpoint

# Inside a route after the LLM call, record tokens from the provider's usage field:
# TOKENS.labels("input", "my-model").inc(usage.prompt_tokens)
```
Keep labels low-cardinality: never use user id or prompt text as a metric label. Put those in logs or traces.

---

## 🔗 LangChain / LangGraph Connection
- **LangSmith** (hosted) or open-source tracers record each chain/graph run with inputs, outputs, latency, token counts and cost, including every node in a LangGraph.
- Enable tracing through environment variables (`LANGSMITH_TRACING=true` plus an API key; verify current variable names in the docs).
- **Callbacks** (`BaseCallbackHandler`) let you push custom metrics to Prometheus from any chain.

```python
# LangChain callback that counts tokens into your own metrics (illustrative)
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

class TokenMetrics(BaseCallbackHandler):
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        usage = (response.llm_output or {}).get("token_usage", {})  # provider dependent
        # TOKENS.labels("input", "my-model").inc(usage.get("prompt_tokens", 0))
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Monitoring only uptime and latency
✅ Correct: Add tokens, cost, quality and guardrail metrics.

❌ Mistake 2: High-cardinality labels
```python
# Wrong: one time series per user, Prometheus memory explodes
REQS.labels(user_id, route, status).inc()
# Right: bounded labels, user id goes to logs/traces
REQS.labels(route, status).inc()
```

❌ Mistake 3: Logging full prompts and answers with PII
✅ Correct: Log ids, counts and masked snippets; keep raw text only where policy allows, with short retention.

---

## 🧠 Tricky Interview Question

**Q**: "All dashboards are green: errors 0.2%, p95 2s. Yet support says users complain answers got worse since Tuesday. How do you investigate?"

**Answer**: Green infrastructure metrics do not measure answer quality. Steps: (1) check what changed Tuesday: prompt version, model alias (providers can update an alias), retrieval index refresh, embeddings, data source; (2) compare quality signals before and after: feedback rate, override rate, judge score on sampled traffic; (3) replay the golden set against the current system; (4) inspect traces of complaint cases: was retrieval empty, were chunks irrelevant, did the model refuse? (5) pin model versions (use dated model ids when available) so silent changes cannot happen, and add a quality alert so this is caught automatically next time.

---

## ⚫ Interview Questions + Answers

Q1: What is p95 latency and why not average?
A1: 95% of requests are faster than the p95 value. Averages hide slow tails; LLM latency has long tails, and users feel the slow ones.

Q2: Name three AI-specific metrics.
A2: Tokens per request, cost per request, and a quality metric (feedback or judge score). Others: cache hit rate, guardrail block rate, retrieval empty-result rate.

Q3: Logs, metrics and traces: what is each for?
A3: Metrics show that something is wrong (aggregates, alerts). Traces show where (per-step timing for one request). Logs show why (details and errors).

Q4: How do you monitor quality without labelled data?
A4: Proxy signals (thumbs, retries, overrides, abandonment), plus an LLM-as-judge on a small sample with a rubric, plus periodic human review. Calibrate the judge against human labels occasionally.

Q5 (Hard): Design alerting for cost so you catch a runaway loop in under 10 minutes without paging on normal peaks.
A5: Track tokens per minute per tenant and globally. Use a baseline for the same hour of the previous weeks and alert on a ratio (for example above 3x baseline for 5 minutes), plus a hard daily budget alert at 50% and 80%, plus a per-user rate limit that auto-blocks outliers. Add a circuit breaker that stops agent loops by max steps. Route low-severity budget alerts to chat and only the fast-burn alert to the pager.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production LLM app (start with latency, errors, tokens, cost)
- You change prompts or models often
- You need audit and cost reports per tenant

❌ Avoid when:
- Collecting everything with no plan: too much data is noise and cost
- Storing raw sensitive text in logs without a retention policy

---

## 📊 Visual Diagram
```
 Request --> [Guard] --> [Retrieve] --> [Rerank] --> [LLM] --> [Output guard]
              span1       span2          span3       span4       span5
                \           |              |           |          /
                 +----------+------ traces / metrics / logs -----+
                                          |
                                +---------v----------+
                                | Metrics store      |
                                | Prometheus / APM   |
                                +----+-----------+---+
                                     |           |
                               Dashboards      Alerts --> chat / pager
                       (p95, cost, quality)   (error, tokens, quality)
```

---

## 💰 Cost Impact
- Monitoring prevents surprise bills: a tokens-per-request alert catches prompt bloat early. Example: 1M requests per month, +3,000 input tokens each is +3B tokens; at an illustrative $1 per 1M input tokens that is about $3,000 extra per month.
- Monitoring itself costs money: metrics storage, trace retention and LLM-judge calls. Judge 1-5% of traffic, not 100%.
- Use sampling for traces on healthy traffic and keep 100% of errors.
- Report cost per tenant and per feature to find where money goes, then apply caching, smaller models or shorter prompts.
- All prices here are illustrative; use your provider's current pricing.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Observability | Seeing inside a running system | चलते system के अंदर देखना |
| Trace / span | Timeline of one request and its steps | एक request और उसके steps की timeline |
| p95 | 95% of requests are faster | 95% requests इससे तेज़ |
| Cardinality | Number of distinct label values | Label के अलग-अलग मानों की संख्या |
| SLO | Target level of service | Service का लक्ष्य स्तर |
| LLM-as-judge | A model scores answers | Model से answers की scoring |
| Alert | Automatic warning | अपने-आप चेतावनी |

---

## ⚡ 3-Line Summary
English: Monitor service metrics plus AI metrics: tokens, cost, quality and guardrail blocks. Use traces to find the slow step and alerts with baselines to catch regressions. Keep labels low-cardinality and never log raw sensitive text.
Hindi: Service metrics के साथ AI metrics भी monitor करो: tokens, cost, quality और guardrail blocks। Slow step पकड़ने के लिए traces और regressions के लिए baseline वाले alerts use करो। Labels low-cardinality रखो और raw sensitive text log मत करो।

---

## ➡️ Next Topic
**530. AI System Security** — protecting the whole system: network, data, identity, and the LLM-specific threats.
