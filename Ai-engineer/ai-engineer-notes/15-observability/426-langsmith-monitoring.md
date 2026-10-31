---

# 426. LangSmith Monitoring
# हिंदी में: LangSmith Monitoring

---

## 🔵 Simple Definition (English)
Monitoring is watching your live LLM app over time. LangSmith gives project dashboards (trace volume, error rate, latency percentiles, token usage, cost, feedback scores), plus alerts and automation rules (for example, send 5% of runs to an LLM-judge, or add negative-feedback runs to an annotation queue).

## 🔵 सरल परिभाषा (Hindi)
Monitoring का मतलब अपने live LLM app को समय के साथ देखते रहना। LangSmith project dashboards देता है (trace volume, error rate, latency percentiles, token usage, cost, feedback scores), साथ में alerts और automation rules (जैसे 5% runs को LLM-judge को भेजना, या negative-feedback runs को annotation queue में डालना)।

---

## 🔴 Problem it Solves
- Offline evals show quality on yesterday's data; production changes daily (new products, model updates, traffic spikes).
- Silent failures: latency creeping up, costs doubling, a provider outage, retrieval returning nothing.
- You find out from angry users instead of from a dashboard.

## 🔴 यह क्यों बना? (Hindi)
- Offline evals कल के data पर quality दिखाते हैं; production रोज़ बदलता है (नए products, model updates, traffic spikes)।
- Silent failures: latency धीरे-धीरे बढ़ना, cost दोगुनी होना, provider outage, retrieval का खाली लौटना।
- Dashboard की जगह नाराज़ users से पता चलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Traces from production stream into a project
Step 2 → Monitoring tab aggregates by time bucket: count, errors, p50/p99 latency
Step 3 → Token + cost charts per model/prompt (from run metadata)
Step 4 → Feedback charts: avg correctness, thumbs-down rate
Step 5 → Automation rules: filter (e.g. 5% of runs) → action (run evaluator, add to dataset/queue)
Step 6 → Alerts: threshold on metric (error rate > 5% for 10 min) → Slack/PagerDuty/webhook
Step 7 → Investigate: click spike → filtered traces → root cause
Step 8 → Fix, deploy, watch the chart recover
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Production के traces project में आते रहते हैं
Step 2 → Monitoring tab समय के bucket में aggregate करता है: count, errors, p50/p99 latency
Step 3 → Model/prompt के हिसाब से token + cost charts
Step 4 → Feedback charts: औसत correctness, thumbs-down दर
Step 5 → Automation rules: filter (जैसे 5% runs) → action (evaluator चलाओ, dataset/queue में डालो)
Step 6 → Alerts: metric पर threshold (error rate > 5%, 10 मिनट) → Slack/PagerDuty/webhook
Step 7 → जाँच: spike पर click → filtered traces → root cause
Step 8 → Fix, deploy, chart का ठीक होना देखो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Monday 9am, the dashboard shows p99 latency jumping from 4s to 14s and error rate from 1% to 9%. Filtering error traces shows `RateLimitError` from the provider after a customs deadline caused a traffic spike. The team lowers concurrency, adds retry with jittered backoff and a fallback model. An alert now fires when error rate > 3% for 5 min. An automation rule runs a groundedness LLM-judge on 5% of runs; its average fell from 0.91 to 0.84 after a tariff PDF update, revealing stale embeddings.

**Amazon-style assistant**: Daily cost chart per feature revealed that a "summary" feature consumed 55% of tokens.

## 🟡 Real Example Hindi mein
**Tariff System**: सोमवार सुबह 9 बजे dashboard में p99 latency 4s से 14s और error rate 1% से 9% दिखता है। Error traces filter करने पर provider से `RateLimitError` मिलता है, क्योंकि customs deadline से traffic बढ़ा था। Team concurrency घटाती है, jitter वाला retry और fallback model जोड़ती है। अब error rate > 3% (5 मिनट) पर alert आता है। Automation rule 5% runs पर groundedness LLM-judge चलाता है; tariff PDF update के बाद इसका औसत 0.91 से 0.84 हुआ, जिससे stale embeddings पकड़े गए।

**Amazon-style assistant**: Feature-wise daily cost chart से पता चला कि "summary" feature 55% tokens खाता है।

---

## 💻 Code Example — Basic
```python
# Basic: compute dashboard metrics from raw run records and fire a simple alert (offline)
from dataclasses import dataclass                             # record type

@dataclass
class RunRec:                                                 # minimal run record
    latency_s: float                                          # duration
    error: bool                                               # failed?
    tokens: int                                               # tokens used

def percentile(values: list[float], p: float) -> float:       # simple percentile
    if not values:                                            # avoid crash on empty list
        return 0.0
    s = sorted(values)                                        # sort ascending
    return s[min(len(s) - 1, int(p * len(s)))]                # pick p-th element

def metrics(runs: list[RunRec]) -> dict[str, float]:
    n = len(runs) or 1                                        # avoid divide-by-zero
    return {"count": float(len(runs)),
            "error_rate": sum(r.error for r in runs) / n,
            "p50": percentile([r.latency_s for r in runs], 0.50),
            "p99": percentile([r.latency_s for r in runs], 0.99),
            "avg_tokens": sum(r.tokens for r in runs) / n}

def alerts(m: dict[str, float]) -> list[str]:
    out: list[str] = []
    if m["error_rate"] > 0.05: out.append(f"error_rate {m['error_rate']:.0%} > 5%")
    if m["p99"] > 10: out.append(f"p99 {m['p99']}s > 10s")
    return out

data = [RunRec(1.0, False, 1400)] * 90 + [RunRec(14.0, True, 0)] * 10   # simulated bad window
m = metrics(data); print(m); print("ALERTS:", alerts(m))
```

## 💻 Code Example — Advanced
```python
# Poll LangSmith for the last window, compute metrics, post to Slack-compatible webhook; async + safe
# pip install langsmith httpx
import asyncio                                                # async runtime
import os                                                     # env
from datetime import datetime, timedelta, timezone            # window
import httpx                                                  # async HTTP for the webhook
from langsmith import Client                                  # SDK

WEBHOOK = os.getenv("ALERT_WEBHOOK_URL", "")                  # Slack incoming webhook (secret)

def window_stats(project: str, minutes: int = 15) -> dict[str, float]:
    client = Client()                                         # needs LANGSMITH_API_KEY
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    runs = list(client.list_runs(project_name=project, is_root=True, start_time=since, limit=1000))
    n = len(runs)
    if n == 0:
        return {"count": 0.0, "error_rate": 0.0, "avg_tokens": 0.0}
    errors = sum(1 for r in runs if r.error)                  # runs with an error
    tokens = sum((r.total_tokens or 0) for r in runs)         # token totals when available
    return {"count": float(n), "error_rate": errors / n, "avg_tokens": tokens / n}

async def notify(text: str) -> None:
    if not WEBHOOK:                                           # not configured => just print
        print("ALERT:", text); return
    async with httpx.AsyncClient(timeout=5) as http:          # short timeout
        try:
            await http.post(WEBHOOK, json={"text": text})     # Slack format
        except httpx.HTTPError as exc:                        # alerting must never crash the job
            print("webhook failed:", type(exc).__name__)

async def check(project: str) -> None:
    try:
        stats = await asyncio.to_thread(window_stats, project)   # blocking SDK in a thread
    except Exception as exc:
        await notify(f"MONITOR BROKEN for {project}: {type(exc).__name__}")  # monitor the monitor
        return
    if stats["count"] >= 20 and stats["error_rate"] > 0.05:   # ignore tiny samples
        await notify(f"{project}: error rate {stats['error_rate']:.1%} over {int(stats['count'])} runs")

if __name__ == "__main__":
    asyncio.run(check("tariff-prod"))                         # run from cron/Kubernetes CronJob
```

---

## 🟠 FastAPI Integration
Add a lightweight `/metrics`-style JSON endpoint and always log the prompt version, model, and tenant as trace metadata so dashboards can be grouped by them.

```python
import time                                                   # latency
from fastapi import FastAPI, Request                          # framework
from langsmith import traceable                               # tracing

app = FastAPI()                                               # app

@traceable(name="classify", metadata={"prompt": "v4", "model": "gpt-4o-mini"})
async def classify(product: str) -> str:
    return "8507.60"

@app.middleware("http")
async def timing(request: Request, call_next):                # simple server-side latency header
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-latency-ms"] = str(round((time.perf_counter() - start) * 1000))
    return response

@app.get("/classify")
async def route(product: str) -> dict[str, str]:
    return {"hs_code": await classify(product)}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain/LangGraph traces feed the dashboards automatically. Add `metadata` and `tags` via `config` to slice charts (model, tenant, graph version). Online evaluators (automation rules) can score a sample of production runs with the same evaluators you use offline.

```python
config = {"tags": ["prod"], "metadata": {"graph_version": "2.3", "tenant": "acme"}}
# await graph.ainvoke({"product": "power bank"}, config=config)   # charts can group by metadata
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Alerting on averages only.
✅ Correct: alert on percentiles (p95/p99) and error rates; averages hide tail pain.

```python
# Wrong
if avg_latency > 5: alert()
# Right
if p99_latency > 10 or error_rate > 0.05: alert()
```

❌ Mistake 2: Alerting on tiny samples, causing noisy pages at night.
✅ Correct: minimum count and a sustained window.

```python
# Wrong
if error_rate > 0.05: page()            # 1 error out of 5 requests = 20%
# Right
if n >= 20 and error_rate > 0.05 and sustained_minutes >= 5: page()
```

---

## 🧠 Tricky Interview Question
**Q**: "Error rate is 0.5%, latency is normal, cost is normal. Yet users complain answers got worse. What does monitoring need that you lack?"

**Answer**: Quality monitoring. Infra metrics only show the app runs, not that answers are right. You need online evaluators on sampled traces (groundedness, format validity, an LLM-judge), user feedback trends, retrieval-quality signals (empty retrieval rate, average similarity score), and drift detection on input distribution. Then alert on those quality metrics too.

---

## ⚫ Interview Questions + Answers

Q1: What metrics should an LLM app dashboard show? (Easy)
A1: Traffic, error rate, latency percentiles, tokens, cost, and quality/feedback scores.

Q2: Why percentiles instead of averages? (Easy)
A2: Averages hide slow outliers; p95/p99 reflect what the worst-served users experience.

Q3: What are automation rules in LangSmith? (Medium)
A3: Rules that match runs by filter (and sampling rate) and trigger actions: run an online evaluator, add to a dataset or annotation queue, or send a webhook.

Q4: How do you detect a provider model update that hurt quality? (Medium)
A4: Pin dated model versions, track metrics by model metadata, run online evaluators on a sample, and compare feedback/judge scores before and after; keep an offline golden set for quick confirmation.

Q5: Design an alerting strategy for an LLM service. (Hard)
A5: Tiered: (1) page on user-visible outages (error rate, p99 sustained), (2) ticket on slow degradation (quality score trend, cost per request +30%), (3) daily report for token spend by feature. Use multi-window thresholds, minimum sample sizes, per-tenant breakdowns, runbooks with links to filtered traces, and alerts on the monitor itself (no data received for 10 minutes).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Anything live with real users
- Controlling cost and catching drift

❌ Avoid when:
- Dashboards without owners or actions (alert fatigue)
- Monitoring PII-heavy data without masking

---

## 📊 Visual Diagram
```
 Prod traces ─► LangSmith project "tariff-prod"
                 │
   ┌─────────────┼───────────────────────────┐
   ▼             ▼                           ▼
 Charts       Automation rules           Alerts
 count        5% sample → LLM judge      error>3% 5min → Slack
 p99 latency  thumbs-down → queue        cost/req +30% → ticket
 tokens/cost  failures → dataset         no data 10min → page
   └─────────────┴──────────► click spike → traces → root cause → fix
```

---

## 💰 Cost Impact
- The cost chart is the main tool for cutting spend. Example: 100K requests/day x 1,500 tokens = 150M tokens/day. If monitoring reveals 20% of requests are repeat questions, caching saves about 30M tokens/day (roughly $4.50/day on gpt-4o-mini rates, much more on larger models).
- Online LLM-judges cost tokens too: 5% sampling x 1,200 tokens x 100K requests = 6M tokens/day. Keep sampling low, use tiny outputs, and prefer rule checks.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dashboard | Charts of live metrics | Live metrics के charts |
| p99 latency | 99% requests faster than this | 99% requests इससे तेज़ |
| Alert | Notification on threshold breach | Threshold टूटने पर सूचना |
| Automation rule | Filter + action on runs | Runs पर filter + action |
| Online evaluator | Scores live traces | Live traces को score करने वाला |
| Drift | Data/behaviour changes over time | समय के साथ data/behaviour का बदलना |

---

## ⚡ 3-Line Summary
English: LangSmith monitoring shows traffic, errors, latency percentiles, tokens, cost and feedback for live projects. Add automation rules for online evaluation and alerts on error rate, tail latency, cost and quality. Monitor quality, not only uptime.
Hindi: LangSmith monitoring live projects के लिए traffic, errors, latency percentiles, tokens, cost और feedback दिखाता है। Online evaluation के लिए automation rules और error rate, tail latency, cost व quality पर alerts लगाओ। सिर्फ़ uptime नहीं, quality भी monitor करो।

---

## ➡️ Next Topic
**427. Langfuse — Alternative** — an open-source, self-hostable platform covering the same ground.
