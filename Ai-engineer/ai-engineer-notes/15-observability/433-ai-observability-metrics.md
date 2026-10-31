---

# 433. AI Observability Metrics
# हिंदी में: AI Observability Metrics (कौन से numbers नापें)

---

## 🔵 Simple Definition (English)
AI observability metrics are the numbers you track to know if an LLM app is healthy: **latency** (TTFT, total), **throughput**, **tokens**, **cost**, **error rate**, **cache hit rate**, and **quality** (accuracy, groundedness, user feedback). Good teams group them into the four golden signals plus AI-specific ones.

## 🔵 सरल परिभाषा (Hindi)
AI observability metrics वे numbers हैं जिनसे पता चलता है कि LLM app स्वस्थ है या नहीं: **latency** (TTFT, total), **throughput**, **tokens**, **cost**, **error rate**, **cache hit rate** और **quality** (accuracy, groundedness, user feedback)। अच्छी teams इन्हें four golden signals और AI-specific metrics में बाँटती हैं।

---

## 🔴 Problem it Solves
- Classic metrics (CPU, 200 vs 500) say the service is "up" while the model silently returns wrong HS codes.
- Cost can explode with no error at all (a longer prompt shipped on Friday).
- Without agreed metrics and targets (SLOs), every incident turns into opinions.

## 🔴 यह क्यों बना? (Hindi)
- Classic metrics (CPU, 200/500) कहते हैं service "up" है जबकि model चुपचाप गलत HS codes दे रहा है।
- Cost बिना किसी error के बढ़ सकती है (शुक्रवार को लंबा prompt ship हुआ)।
- सहमत metrics और targets (SLO) के बिना हर incident राय का झगड़ा बन जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pick user journeys (classify product, chat answer) and define what "good" means
Step 2 → For each, choose metrics in 4 groups:
          Reliability: error rate, timeouts, rate-limit (429) count
          Performance: p50/p95/p99 latency, TTFT, tokens/sec
          Cost:        input/output tokens, $ per request, $ per user per day
          Quality:     exact-match accuracy, groundedness, thumbs-up ratio, refusal rate
Step 3 → Emit as counters / histograms / gauges with LOW-cardinality labels (model, route, version)
Step 4 → Set SLOs (e.g. 99% of requests < 3 s; accuracy >= 85%) and error budgets
Step 5 → Dashboard + alerts on burn rate, not on every blip
Step 6 → Review weekly: top costly prompts, worst quality segments
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → User journeys चुनो और तय करो "अच्छा" क्या है
Step 2 → 4 groups में metrics चुनो:
          Reliability: error rate, timeouts, 429 count
          Performance: p50/p95/p99 latency, TTFT, tokens/sec
          Cost:        input/output tokens, $ प्रति request, $ प्रति user प्रति दिन
          Quality:     accuracy, groundedness, thumbs-up ratio, refusal rate
Step 3 → Counter/histogram/gauge के रूप में कम-cardinality labels (model, route, version) के साथ भेजो
Step 4 → SLO तय करो (जैसे 99% requests < 3 s; accuracy >= 85%)
Step 5 → Dashboard और alerts (हर छोटे blip पर नहीं, burn rate पर)
Step 6 → हर हफ्ते review: सबसे महँगे prompts, सबसे खराब segments
```

---

## 🟡 Real World Example
**Tariff Classification System**: Dashboard panels: (1) p95 latency by route, (2) tokens per request by prompt version, (3) cost per 1,000 classifications, (4) exact-match accuracy on a daily sampled-and-reviewed set, (5) "low confidence" rate (answers where the model says unsure). One day panel 2 jumps 40% after a prompt change, and panel 4 stays flat, so the team knows the longer prompt added cost without benefit and rolls it back.

**Zomato-style**: TTFT is the key metric for the chat assistant because users watch streaming text; total latency matters less.

## 🟡 Real Example Hindi mein
**Tariff System**: Dashboard panels: (1) route के हिसाब से p95 latency, (2) prompt version के हिसाब से tokens/request, (3) 1,000 classifications की cost, (4) रोज़ sample की हुई set पर accuracy, (5) "low confidence" rate। एक दिन panel 2 में 40% उछाल आता है पर panel 4 वैसा ही रहता है, यानी लंबे prompt ने cost बढ़ाई बिना फायदे के, और rollback हो जाता है।

---

## 💻 Code Example — Basic
Compute percentiles, error rate and cost from a list of request records (pure Python, run directly).

```python
# Compute core AI metrics from request records
from dataclasses import dataclass            # record type
from statistics import quantiles             # percentile helper


@dataclass
class Rec:                                   # one request record
    latency_ms: float
    in_tok: int
    out_tok: int
    ok: bool


RECS: list[Rec] = [                          # sample data
    Rec(800, 420, 12, True), Rec(950, 450, 14, True), Rec(700, 400, 10, True),
    Rec(4200, 1800, 15, True), Rec(300, 0, 0, False), Rec(880, 430, 13, True),
]

PRICE_IN, PRICE_OUT = 0.15 / 1e6, 0.60 / 1e6  # gpt-4o-mini $/token (example prices)

lat = sorted(r.latency_ms for r in RECS if r.ok)       # latencies of successful calls
p = quantiles(lat, n=100, method="inclusive")          # 99 cut points
p50, p95 = p[49], p[94]                                # pick percentiles

err_rate = sum(not r.ok for r in RECS) / len(RECS)     # error rate
cost = sum(r.in_tok * PRICE_IN + r.out_tok * PRICE_OUT for r in RECS)  # total $
avg_in = sum(r.in_tok for r in RECS) / len(RECS)       # average input tokens

print(f"p50={p50:.0f}ms p95={p95:.0f}ms")              # latency
print(f"error_rate={err_rate:.1%}")                    # reliability
print(f"cost=${cost:.6f}  avg_in_tokens={avg_in:.0f}") # cost + tokens
```

## 💻 Code Example — Advanced
Prometheus metrics with `prometheus_client` (`pip install prometheus-client`), async wrapper with error handling.

```python
# Production metrics: Prometheus histogram/counters around an async LLM call
import time                                                     # timing
from typing import Awaitable, Callable                          # type hints

from prometheus_client import Counter, Histogram, Gauge         # metric types

LLM_LATENCY = Histogram(                                        # latency distribution
    "llm_request_seconds", "LLM latency", ["model", "route"],
    buckets=(0.25, 0.5, 1, 2, 3, 5, 10, 30),                    # buckets around the 3 s SLO
)
LLM_TOKENS = Counter("llm_tokens_total", "Tokens", ["model", "direction"])  # in / out
LLM_COST = Counter("llm_cost_usd_total", "Spend in USD", ["model"])         # money
LLM_ERRORS = Counter("llm_errors_total", "Errors", ["model", "type"])       # failures
INFLIGHT = Gauge("llm_inflight_requests", "Concurrent LLM calls")           # saturation

PRICES = {"gpt-4o-mini": (0.15e-6, 0.60e-6)}                    # (in, out) USD per token


async def measured_call(
    model: str, route: str,
    call: Callable[[], Awaitable[tuple[str, int, int]]],        # returns (text, in_tok, out_tok)
) -> str:
    INFLIGHT.inc()                                              # one more in flight
    start = time.perf_counter()                                 # start timer
    try:
        text, tin, tout = await call()                          # do the LLM call
        LLM_TOKENS.labels(model, "input").inc(tin)              # count input tokens
        LLM_TOKENS.labels(model, "output").inc(tout)            # count output tokens
        pin, pout = PRICES.get(model, (0.0, 0.0))               # unknown model -> 0 (log it!)
        LLM_COST.labels(model).inc(tin * pin + tout * pout)     # money
        return text
    except Exception as exc:                                    # classify error by type name
        LLM_ERRORS.labels(model, type(exc).__name__).inc()
        raise
    finally:
        LLM_LATENCY.labels(model, route).observe(time.perf_counter() - start)
        INFLIGHT.dec()                                          # always decrement
```

---

## 🟠 FastAPI Integration
Expose `/metrics` for Prometheus to scrape.

```python
# FastAPI exposes /metrics and uses measured_call
from fastapi import FastAPI                                     # framework
from prometheus_client import make_asgi_app                     # ASGI app serving metrics
from pydantic import BaseModel                                  # validation

from metrics_mod import measured_call                           # from advanced example

app = FastAPI()                                                 # app
app.mount("/metrics", make_asgi_app())                          # GET /metrics


class Req(BaseModel):
    product: str


async def fake_llm() -> tuple[str, int, int]:                   # replace with real OpenAI call
    return "8518.22", 420, 12


@app.post("/classify")
async def classify(req: Req) -> dict[str, str]:
    code = await measured_call("gpt-4o-mini", "classify", fake_llm)
    return {"hs_code": code}
```

---

## 🔗 LangChain / LangGraph Connection
A callback handler reads `usage_metadata` after each LLM call and updates the same Prometheus counters.

```python
# LangChain callback that feeds token metrics
from langchain_core.callbacks import BaseCallbackHandler          # base class
from langchain_core.outputs import LLMResult                      # result type
from prometheus_client import Counter

TOK = Counter("lc_tokens_total", "LangChain tokens", ["direction"])


class MetricsHandler(BaseCallbackHandler):
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:   # called after every LLM call
        for gens in response.generations:                          # list of lists
            for g in gens:
                msg = getattr(g, "message", None)                  # chat message if chat model
                um = getattr(msg, "usage_metadata", None) or {}    # {"input_tokens":..,"output_tokens":..}
                TOK.labels("input").inc(um.get("input_tokens", 0))
                TOK.labels("output").inc(um.get("output_tokens", 0))

# usage: chain.invoke(x, config={"callbacks": [MetricsHandler()]})
# LangGraph: same handler works for every LLM node in the graph.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Alerting on average latency
✅ Correct: use percentiles; averages hide the slow tail.

```python
# Wrong: mean looks fine (1.1 s) while 5% of users wait 12 s
avg = sum(lat) / len(lat)
# Right: p95 / p99
p95 = quantiles(lat, n=100)[94]
```

❌ Mistake 2: Only technical metrics, no quality metric
✅ Correct: add at least one sampled quality score (accuracy, thumbs ratio).

```python
# Wrong: dashboard shows 0 errors -> "all good" while accuracy fell to 60%
# Right: daily job scores 100 sampled traces and exports gauge tariff_accuracy
ACCURACY.set(correct / total)
```

---

## 🧠 Tricky Interview Question
**Q**: "Error rate is 0.1%, p95 is 1.2 s, cost is flat, but customers complain. What is missing?"

**Answer**: Quality metrics. An LLM can return HTTP 200 with a wrong or hallucinated answer. You need output-level metrics: sampled accuracy vs human labels, groundedness/faithfulness scores, refusal rate, fallback rate, thumbs-down ratio, and per-segment breakdown (language, product category). Also check for silent changes: model version updated by provider, data drift in inputs.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What is TTFT?
A1: Time To First Token: delay until the first streamed token arrives. It drives perceived speed in chat UIs.

Q2 (Easy): Why track input and output tokens separately?
A2: They have different prices (output is usually 3-5x more), and they point to different fixes (long context vs verbose answers).

Q3 (Medium): What is an SLO and an error budget in this context?
A3: SLO is a target, e.g. 99% of classifications under 3 s. Error budget is the allowed 1% failure; if burned too fast, stop feature releases and fix reliability.

Q4 (Medium): Why must metric labels be low-cardinality?
A4: Each unique label combination creates a time series. user_id or prompt text creates millions of series, breaking storage and queries. Put those on traces instead.

Q5 (Hard): Design the metric set for an agent that calls tools in a loop.
A5: Per-run: steps count histogram, total tokens, total cost, success rate, wall time. Per-tool: call count, latency, error rate. Safety: max-step-hit rate (runaway loops), repeated-identical-call rate. Quality: task success vs golden set. Alert on step count p99 and cost per run because loops cause cost explosions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything in production with real users or a budget
- You need SLOs, capacity planning or cost allocation

❌ Avoid when:
- Throw-away demos (a few logs are enough)
- Measuring everything: too many metrics hide the important ones

---

## 📊 Visual Diagram
```
            ┌───────────── AI Observability Metrics ─────────────┐
 Reliability│ error rate | timeouts | 429s | fallback rate       │
 Performance│ p50/p95/p99 | TTFT | tokens/s | queue time         │
 Cost       │ in/out tokens | $/request | $/user/day | cache hit │
 Quality    │ accuracy | groundedness | thumbs | refusal rate     │
            └──────────────────────┬─────────────────────────────┘
                                   ▼
                    SLO  ──>  alert on burn rate  ──>  on-call
```

---

## 💰 Cost Impact
- Metrics are cheap (a few time series), unlike traces. They do not consume LLM tokens.
- They are how you find savings: if `output tokens / request` rises from 120 to 300, then at 1M requests on gpt-4o-mini you pay about $108 more per day; a `max_tokens` cap or terser prompt fixes it.
- Quality judges consume tokens; run them on a sample (for example 1-5%).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| p95 | 95% of requests are faster than this | 95% requests इससे तेज़ |
| TTFT | Time to first token | पहला token आने का समय |
| SLO | Target level of service | Service का लक्ष्य |
| Error budget | Allowed failures | अनुमत failures |
| Cardinality | Unique label combos | Unique label combinations |
| Histogram | Distribution metric | Distribution वाला metric |
| Saturation | How full the system is | System कितना भरा है |

---

## ⚡ 3-Line Summary
English: Track reliability, performance, cost and quality together; HTTP 200 does not mean a correct answer. Use percentiles, low-cardinality labels, and SLOs with burn-rate alerts. Always add a sampled quality metric.
Hindi: Reliability, performance, cost और quality चारों साथ track करो; HTTP 200 का मतलब सही जवाब नहीं। Percentiles, कम-cardinality labels और SLO के साथ burn-rate alerts use करो। हमेशा एक sampled quality metric जोड़ो।

---

## ➡️ Next Topic
**434. Cost Tracking per Request** — turning token metrics into dollars per request, user and feature.
