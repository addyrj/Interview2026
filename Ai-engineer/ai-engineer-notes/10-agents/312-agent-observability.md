---

# 312. Agent Observability
# हिंदी में: Agent Observability (agent के अंदर क्या हुआ, देखना)

---

## 🔵 Simple Definition (English)
Agent observability means recording everything the agent does: each LLM call, prompt, tool call, latency, token count, cost and error, linked together as one **trace**. Then you can answer "why did the agent give this answer?" and "why was this request slow or expensive?".

## 🔵 सरल परिभाषा (Hindi)
Agent observability का मतलब है agent जो भी करता है उसे record करना: हर LLM call, prompt, tool call, latency, token, cost और error, सब एक **trace** में जुड़े हुए। इससे आप जवाब दे सकते हैं कि "agent ने यह जवाब क्यों दिया?" और "यह request धीमी या महँगी क्यों थी?"

---

## 🔴 Problem it Solves
Agents are non-deterministic and multi-step. A normal log line "request failed" tells nothing. Bugs hide in a wrong tool argument at step 3, a long prompt, or a loop. Costs creep up silently. Without traces you guess; with traces you see the exact path.

## 🔴 यह क्यों बना? (Hindi)
Agents non-deterministic और multi-step होते हैं। सामान्य log "request failed" कुछ नहीं बताता। Bug step 3 के गलत tool argument, लंबे prompt या loop में छिपा होता है। Cost चुपचाप बढ़ती है। Trace के बिना अंदाज़ा लगाना पड़ता है; trace से सटीक रास्ता दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a trace_id for each user request
Step 2 → Wrap each unit of work in a span (llm_call, tool_call, retrieval)
Step 3 → Record inputs, outputs, start/end time, model, tokens, errors per span
Step 4 → Link spans in a tree (parent_id) so you see the full agent path
Step 5 → Export to a backend (LangSmith, Langfuse, OpenTelemetry collector)
Step 6 → Build dashboards: latency p95, cost per request, error rate, tool usage
Step 7 → Alert on anomalies (cost spike, loops, high error rate)
Step 8 → Use bad traces to create eval test cases
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर user request के लिए trace_id बनाओ
Step 2 → हर काम (llm_call, tool_call, retrieval) को span में लपेटो
Step 3 → हर span में input, output, समय, model, tokens, error लिखो
Step 4 → parent_id से spans को tree में जोड़ो
Step 5 → Backend में भेजो (LangSmith, Langfuse, OpenTelemetry)
Step 6 → Dashboard: latency p95, cost per request, error rate
Step 7 → Anomaly पर alert (cost spike, loop, ज़्यादा errors)
Step 8 → खराब traces से eval test cases बनाओ
```

---

## 🟡 Real World Example
**Tariff Classification System**: A broker complains "the agent gave the wrong duty." In the trace you see: step 1 retrieval returned an outdated tariff chunk, step 2 the LLM trusted it, step 3 the duty tool was called with the wrong country code. You fix retrieval freshness. The dashboard also shows that 5% of requests loop 8+ steps and cost 10x the average.

**Amazon-style**: find which support conversations cost the most and why.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker शिकायत करता है "duty गलत मिली।" Trace में दिखता है: retrieval ने पुराना tariff chunk दिया, LLM ने उस पर भरोसा किया, duty tool गलत country code से चला। आप retrieval freshness ठीक करते हैं। Dashboard यह भी दिखाता है कि 5% requests 8+ steps loop करती हैं और औसत से 10 गुना महँगी हैं।
**Amazon**: कौन सी support बातचीत सबसे महँगी है और क्यों।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny tracer using a context manager (pure Python, offline).
import time                                      # timing
import uuid                                      # ids
from contextlib import contextmanager            # with-statement helper
from typing import Any, Iterator

TRACE: list[dict[str, Any]] = []                 # in-memory span store
_stack: list[str] = []                           # current parent span ids

@contextmanager
def span(name: str, **attrs: Any) -> Iterator[dict[str, Any]]:
    record: dict[str, Any] = {
        "id": uuid.uuid4().hex[:8],              # span id
        "parent": _stack[-1] if _stack else None,# parent span
        "name": name, "attrs": attrs,            # what + metadata
        "start": time.perf_counter(),            # start time
        "error": None,
    }
    _stack.append(record["id"])                  # become the current parent
    try:
        yield record                             # run the wrapped code
    except Exception as exc:                     # record failures
        record["error"] = repr(exc)
        raise
    finally:
        record["ms"] = round((time.perf_counter() - record["start"]) * 1000, 1)  # duration
        _stack.pop()                             # leave span
        TRACE.append(record)                     # store it

if __name__ == "__main__":
    with span("agent_run", question="bluetooth speaker"):
        with span("llm_call", model="gpt-4o-mini") as s:
            s["attrs"]["tokens"] = 350           # attach token usage
        with span("tool_call", tool="search_hs_code"):
            time.sleep(0.05)                     # tool latency
    for r in TRACE:                              # print the spans
        print(r["name"], r["parent"], r["ms"], r["attrs"])
```

## 💻 Code Example — Advanced
```python
# Production: async decorator that records spans, tokens, cost and structured JSON logs.
import asyncio
import contextvars                               # async-safe current trace/span
import functools
import json
import logging
import time
import uuid
from typing import Any, Awaitable, Callable, TypeVar

log = logging.getLogger("obs")
T = TypeVar("T")
trace_id: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")
parent_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("parent_id", default=None)

PRICES = {"gpt-4o-mini": (0.15, 0.60)}           # USD per 1M tokens (check current pricing)

def cost_usd(model: str, tin: int, tout: int) -> float:
    pin, pout = PRICES.get(model, (0.0, 0.0))    # unknown model -> 0
    return (tin * pin + tout * pout) / 1_000_000

def traced(name: str) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    def deco(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            sid, start = uuid.uuid4().hex[:8], time.perf_counter()
            token = parent_id.set(sid)           # children will see us as parent
            parent = None
            err = None
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:             # log then re-raise
                err = repr(exc)
                raise
            finally:
                parent_id.reset(token)
                log.info(json.dumps({            # one JSON line per span
                    "trace": trace_id.get(), "span": sid, "name": name,
                    "ms": round((time.perf_counter() - start) * 1000, 1), "error": err}))
        return wrapper
    return deco

@traced("llm_call")
async def llm_call(prompt: str) -> dict[str, Any]:
    await asyncio.sleep(0.05)                    # pretend network
    usage = {"input": 400, "output": 60}
    log.info(json.dumps({"trace": trace_id.get(), "cost_usd": cost_usd("gpt-4o-mini", 400, 60)}))
    return {"text": "8518.22", "usage": usage}

@traced("agent_run")
async def agent_run(question: str) -> str:
    trace_id.set(uuid.uuid4().hex[:12])          # new trace per request
    out = await llm_call(question)
    return out["text"]

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print(asyncio.run(agent_run("bluetooth speaker")))
```

---

## 🟠 FastAPI Integration
```python
from fastapi import FastAPI, Request             # framework
import uuid

app = FastAPI()

@app.middleware("http")
async def add_trace(request: Request, call_next):
    tid = request.headers.get("x-trace-id", uuid.uuid4().hex[:12])   # reuse upstream id if present
    trace_id.set(tid)                                                 # contextvar for this request
    response = await call_next(request)                               # run the route
    response.headers["x-trace-id"] = tid                              # return id for support tickets
    return response

@app.get("/ask")
async def ask(q: str) -> dict:
    return {"answer": await agent_run(q), "trace_id": trace_id.get()}
```
Give users the `trace_id` in responses and errors. Support can paste it and you can find the exact run.

---

## 🔗 LangChain / LangGraph Connection
LangSmith tracing is switched on with environment variables, with no code change:

```python
import os
os.environ["LANGSMITH_TRACING"] = "true"               # enable tracing (older name: LANGCHAIN_TRACING_V2)
os.environ["LANGSMITH_API_KEY"] = "<your-key>"         # from LangSmith settings
os.environ["LANGSMITH_PROJECT"] = "tariff-agent"       # group runs

# Every chain/graph invoke is now traced: nodes, LLM calls, tools, tokens, latency.
# Per-request metadata:
# agent.invoke(inputs, config={"tags": ["prod"], "metadata": {"user_id": "u1"}, "run_name": "classify"})
```
Alternatives: Langfuse (open source, `CallbackHandler`), OpenTelemetry with OpenInference instrumentation, Arize Phoenix.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Logging full prompts with customer PII to a third party.
✅ Correct: redact PII, sample, and set retention limits.

```python
# Wrong
log.info(prompt)
# Right
log.info(redact(prompt)[:500])
```

❌ Mistake 2: Only tracking averages.
✅ Correct: track p95/p99 latency and cost per request. Averages hide the 5% runaway runs.

❌ Mistake 3: No trace id across services.
✅ Correct: propagate `x-trace-id` through every call.

---

## 🧠 Tricky Interview Question
**Q**: "Average cost per request looks fine, but the monthly bill doubled. How does observability find the cause?"

**Answer**: Averages hide a long tail. Group traces by user, route, agent version and number of steps. Likely causes: a prompt change that increased tokens, a loop in 3% of requests, one tenant sending huge documents, or a new tool that returns large outputs that are resent every step. Look at cost percentiles, the top-N most expensive traces, and tokens per span, then add budgets and alerts on that metric.

---

## ⚫ Interview Questions + Answers

Q1: Trace vs span?
A1: A trace is the whole request; a span is one step inside it (LLM call, tool call). Spans form a tree.

Q2: What should you log for each LLM call?
A2: Model, prompt/response (redacted), token counts, latency, cost, finish reason, errors, and the prompt version.

Q3: Logging vs tracing vs metrics?
A3: Logs are discrete events; traces show causal flow of a request; metrics are aggregated numbers over time (latency p95, error rate).

Q4: Name tools for LLM observability.
A4: LangSmith, Langfuse, Arize Phoenix, Helicone, and OpenTelemetry-based setups.

Q5: (Hard) How do you debug non-determinism?
A5: Store the full inputs (prompt version, model, temperature, seed if supported, retrieved docs, tool outputs) in the trace, so you can replay a run. Set temperature 0 for tests, turn bad traces into regression cases, and compare runs side by side.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Any production agent
- You pay per token and need cost control
- You need to debug quality issues

❌ Avoid (or limit) when:
- Data is too sensitive to store; log metadata only
- High traffic and tracing 100% is too costly; sample

---

## 📊 Visual Diagram
```
trace_id=abc123
└─ agent_run                      2.8s   $0.0021
   ├─ retrieval                   0.3s
   ├─ llm_call (plan)             0.9s   in=520 out=40
   ├─ tool_call: search_hs_code   0.2s
   ├─ tool_call: get_duty_rate    0.4s   ERROR timeout
   └─ llm_call (answer)           1.0s   in=700 out=90
        │
        ▼ export → dashboard (p95 latency, cost/request, error rate) → alerts
```

---

## 💰 Cost Impact
Observability does not call the LLM, but storing full prompts and responses has storage cost, and some vendors charge per trace. Use sampling (for example 10% of success, 100% of errors), truncate long payloads, and set retention. The big win is savings: spotting loops and heavy prompts commonly cuts bills noticeably. Track cost per request, per user and per tool.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | Full record of one request | एक request का पूरा रिकॉर्ड |
| Span | One step in a trace | Trace का एक step |
| Metric | Aggregated number | समेकित संख्या |
| p95 latency | 95% of requests are faster | 95% requests इससे तेज़ |
| Sampling | Record only some traces | कुछ ही traces रखना |
| Redaction | Hiding sensitive data | संवेदनशील डेटा छिपाना |

---

## ⚡ 3-Line Summary
English: Observability records every LLM call, tool call, token and error as a linked trace. It lets you debug wrong answers and control cost and latency. Redact sensitive data and track percentiles, not just averages.
Hindi: Observability हर LLM call, tool call, token और error को जुड़े हुए trace में record करती है। इससे गलत जवाब debug और cost/latency control होती है। संवेदनशील डेटा redact करो और सिर्फ average नहीं, percentiles देखो।

---

## ➡️ Next Topic
**313. Agent Evaluation** — measuring if the agent is actually correct, using test sets and metrics.
