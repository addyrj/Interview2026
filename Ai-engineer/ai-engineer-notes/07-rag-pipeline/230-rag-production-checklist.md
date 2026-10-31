---

# 230. RAG Production Checklist
# हिंदी में: RAG Production Checklist

---

## 🔵 Simple Definition (English)
A RAG production checklist is a list of checks across data, retrieval, generation, safety, performance, cost and monitoring that must pass before a RAG system serves real users.

## 🔵 सरल परिभाषा (Hindi)
RAG production checklist data, retrieval, generation, safety, performance, cost और monitoring की जाँचों की सूची है, जो real users को serve करने से पहले पास होनी चाहिए।

---

## 🔴 Problem it Solves
A RAG demo with 10 questions looks great, then fails in production: stale data, prompt injection, slow p95, runaway cost, no way to know when quality drops. Teams ship without evaluation or observability. The checklist turns "it works on my laptop" into repeatable engineering.

## 🔴 यह क्यों बना? (Hindi)
10 सवालों वाला RAG demo बढ़िया दिखता है, पर production में fail होता है: पुराना data, prompt injection, धीमा p95, बेकाबू cost, और quality गिरने का पता ही नहीं। Checklist "मेरे laptop पर चलता है" को repeatable engineering बनाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → DATA: source of truth, dedupe, PII removal, versioning, freshness
Step 2 → INDEX: chunk size tested, metadata, re-index job, ACL filters
Step 3 → RETRIEVAL: hybrid + rerank, recall@k measured on golden set
Step 4 → GENERATION: grounded prompt, citations, "I don't know" path, JSON schema
Step 5 → SAFETY: prompt-injection defence, output filters, access control
Step 6 → PERFORMANCE: timeouts, retries, streaming, caching, p95 target
Step 7 → COST: token budget, model routing, per-tenant limits
Step 8 → OBSERVABILITY: traces, eval in CI, feedback loop, alerts, rollback
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → DATA: source of truth, dedupe, PII हटाना, versioning, freshness
Step 2 → INDEX: chunk size test, metadata, re-index job, ACL filters
Step 3 → RETRIEVAL: hybrid + rerank, golden set पर recall@k
Step 4 → GENERATION: grounded prompt, citations, "पता नहीं" path, JSON schema
Step 5 → SAFETY: prompt-injection बचाव, output filters, access control
Step 6 → PERFORMANCE: timeouts, retries, streaming, caching, p95 target
Step 7 → COST: token budget, model routing, per-tenant limits
Step 8 → OBSERVABILITY: traces, CI में eval, feedback loop, alerts, rollback
```

---

## 🟡 Real World Example
**Tariff Classification System** go-live: golden set of 500 historical classifications (accuracy gate 90 percent), index versioned by notification date, validator rejects unknown HS codes, per-user rate limit, LangSmith traces, alert if review-queue rate jumps above 25 percent. **Zomato AI**: before launching a support bot, they require citation rate, refusal correctness, and p95 under 3 seconds.

## 🟡 Real Example Hindi mein
**Tariff System** go-live: 500 historical classifications का golden set (accuracy gate 90%), notification date से versioned index, unknown HS codes reject करने वाला validator, per-user rate limit, LangSmith traces, और review-queue rate 25% से ऊपर जाए तो alert।

---

## 💻 Code Example — Basic
```python
# A tiny pre-deploy gate: run golden questions and fail if metrics are below thresholds
from dataclasses import dataclass

@dataclass
class Golden:
    question: str
    expected_code: str

GOLDEN: list[Golden] = [
    Golden("wireless headphones", "8518.30"),
    Golden("smartphone", "8517.13"),
]

def fake_system(q: str) -> str:
    # Stand-in for the real RAG pipeline
    return {"wireless headphones": "8518.30", "smartphone": "8517.12"}.get(q, "")

def run_gate(min_acc: float = 0.9) -> bool:
    correct = sum(fake_system(g.question) == g.expected_code for g in GOLDEN)  # count hits
    acc = correct / len(GOLDEN)  # accuracy
    print(f"accuracy={acc:.2f} (need {min_acc})")
    return acc >= min_acc  # deploy only if True

if not run_gate():
    print("DEPLOY BLOCKED")  # in CI: sys.exit(1)
```

## 💻 Code Example — Advanced
```python
# Production wrapper: timeout, retry, cache, token budget, structured logging
import asyncio, hashlib, json, logging, time
from typing import Awaitable, Callable

log = logging.getLogger("rag")
CACHE: dict[str, dict] = {}  # swap for Redis in prod

def cache_key(q: str) -> str:
    return hashlib.sha256(q.strip().lower().encode()).hexdigest()  # normalised key

async def with_retry(fn: Callable[[], Awaitable[dict]], tries: int = 3, base: float = 0.5) -> dict:
    for i in range(tries):
        try:
            return await asyncio.wait_for(fn(), timeout=20)  # hard timeout
        except Exception as exc:  # narrow to API errors in prod
            if i == tries - 1:
                raise
            await asyncio.sleep(base * 2 ** i)  # exponential backoff
            log.warning("retry %d after %s", i + 1, exc)
    raise RuntimeError("unreachable")

async def serve(q: str, pipeline: Callable[[str], Awaitable[dict]], max_query_chars: int = 500) -> dict:
    if len(q) > max_query_chars:
        return {"error": "query_too_long"}  # input budget
    key = cache_key(q)
    if key in CACHE:
        return {**CACHE[key], "cached": True}  # zero LLM cost
    t0 = time.perf_counter()
    try:
        result = await with_retry(lambda: pipeline(q))  # guarded call
    except Exception:
        log.exception("pipeline failed")
        return {"error": "temporarily_unavailable"}  # graceful degradation
    CACHE[key] = result
    log.info(json.dumps({"event": "rag", "ms": round((time.perf_counter() - t0) * 1000),
                         "tokens": result.get("tokens"), "sources": result.get("sources")}))
    return result
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}  # liveness; add /ready that pings vector DB + LLM

@app.post("/ask")
async def ask(payload: dict, request: Request) -> JSONResponse:
    out = await serve(payload.get("question", ""), my_pipeline)  # wrapper above
    status = 200 if "error" not in out else 503
    return JSONResponse(out, status_code=status, headers={"X-Cache": str(out.get("cached", False))})
```

---

## 🔗 LangChain / LangGraph Connection
Use LangSmith (or Langfuse/OpenTelemetry) for tracing: set `LANGSMITH_TRACING=true` and each chain/graph run is captured with latency, tokens and retrieved docs. LangGraph checkpointers give durable state and human-in-the-loop interrupts. Run evals in CI with a dataset.

```python
# Env-driven tracing, no code change needed:
#   LANGSMITH_TRACING=true  LANGSMITH_API_KEY=...  LANGSMITH_PROJECT=tariff-rag
# Runtime limits on a chain:
# chain = (prompt | llm).with_retry(stop_after_attempt=3).with_config({"timeout": 20})
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No evaluation set
```python
# Wrong: "looks good" after 5 manual tries
# Right: golden set + metrics (recall@k, faithfulness, accuracy) as a CI gate
```

❌ Mistake 2: Ignoring access control
```python
# Wrong: retriever.invoke(q)   # every user sees every doc
# Right: retriever with metadata filter {"tenant_id": user.tenant, "acl": user.groups}
```

---

## 🧠 Tricky Interview Question
**Q**: "Quality was great at launch and degrades silently over 3 months. What do you check?"

**Answer**: Data drift (new doc types, stale index), embedding or LLM version change by the provider, query distribution shift, broken ingestion (empty chunks), prompt edits. Add monitoring: sampled online evals (LLM-judge on traces), retrieval hit-rate, thumbs-down rate, index freshness lag, alerts on refusal and review rates, and pin model versions.

---

## ⚫ Interview Questions + Answers

Q1: Name three things to monitor in RAG. (Easy)
A1: Latency (p50/p95), token cost per query, and quality signals (thumbs, refusal rate, faithfulness samples).

Q2: Why version your index? (Easy)
A2: To roll back a bad re-index and to reproduce answers for audits.

Q3: How do you defend against prompt injection in documents? (Medium)
A3: Treat retrieved text as data: delimit it, tell the model not to follow instructions in it, strip suspicious patterns, restrict tools, validate outputs, and limit privileges.

Q4: How to do zero-downtime re-indexing? (Medium)
A4: Build a new index alongside (blue/green), run eval on golden set, switch alias, keep old index for rollback.

Q5: How do you set a cost budget per tenant? (Hard)
A5: Count tokens per request (usage field), store per-tenant counters, enforce quotas with rate limiting, route cheap queries to small models, cache, and alert on anomalies. Fail closed with a clear error when over budget.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Before every launch and major change (new model, new chunking)
- As a PR template for the RAG team

❌ Avoid when:
- Prototype or hackathon (apply a lite version: eval set + logging)

---

## 📊 Visual Diagram
```
 [Data]──►[Index]──►[Retrieval]──►[Generation]──►[Safety]
   │         │          │             │             │
 fresh     versioned   recall@k    grounded      injection
 PII-free  ACL         rerank      citations     filters
   └──────────────┬─────────────────────────────────┘
                  ▼
   [Perf: timeout/cache]  [Cost: budget/routing]  [Observability: traces/evals/alerts]
```

---

## 💰 Cost Impact
Checklist items cut cost directly: caching (often 20-40 percent hits on repeated questions), token budgets (limit chunks to 4-5), model routing (small model default), batch API for offline jobs (50 percent cheaper), and prompt caching for long system prompts. Monitoring tokens per query catches regressions early (e.g., a chunking change doubling context).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Golden set | Labelled test questions | जाँच के लिए सही-जवाब वाले सवाल |
| p95 latency | 95 percent faster than this | 95% requests इतनी देर में |
| Blue/green | Two index versions | दो versions की अदला-बदली |
| ACL | Access control list | Access नियम |
| Tracing | Record each step of a run | हर step का record |

---

## ⚡ 3-Line Summary
English: A RAG is production-ready only when data, retrieval, generation, safety, performance, cost and monitoring are all covered. Gate releases with a golden-set evaluation. Watch quality, latency and token cost continuously.
Hindi: RAG तभी production-ready है जब data, retrieval, generation, safety, performance, cost और monitoring सब कवर हों। Golden-set evaluation से release gate लगाओ। Quality, latency और token cost लगातार देखो।

---

## ➡️ Next Topic
**231. LangChain: What + Why** — begins the LangChain section: the framework that wires all these RAG pieces together.
