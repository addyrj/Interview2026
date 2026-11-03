---

# 590. Build LangSmith Tracing
# हिंदी में: LangSmith Tracing बनाना

---

## 🔵 Simple Definition (English)
Tracing records every step of an LLM pipeline as a "span": its name, parent, inputs, outputs, latency and error. Together the spans form a tree, which is what the LangSmith UI shows. `main.py` builds a tiny version with a decorator and a ContextVar.

## 🔵 सरल परिभाषा (Hindi)
Tracing LLM pipeline के हर step को "span" की तरह record करता है: नाम, parent, inputs, outputs, latency और error। Spans मिलकर tree बनाते हैं, जो LangSmith UI में दिखता है। `main.py` में decorator और ContextVar से इसका छोटा version है।

---

## 🔴 Problem it Solves
When a RAG answer is slow or wrong, logs show only the final result. You cannot see which step (retriever or LLM) was slow, what it received, or which failed. Print debugging does not scale across async calls.

## 🔴 यह क्यों बना? (Hindi)
RAG का जवाब धीमा या गलत हो तो logs में सिर्फ़ final result दिखता है। पता नहीं चलता कि कौन सा step (retriever या LLM) धीमा था, उसे क्या मिला, या कौन fail हुआ। Async calls में print debugging काम नहीं करती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → @trace("name", run_type) wraps an async function
Step 2 → On call: create span {id, parent=_current.get(), name, type, inputs}
Step 3 → _current.set(span id): children now see this span as their parent
Step 4 → await the function; store outputs, or store repr(exception) and re-raise
Step 5 → finally: record ms latency, _current.reset(token), append to SPANS
Step 6 → print_tree() groups spans by parent and prints them nested
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → @trace("name", run_type) async function को wrap करता है
Step 2 → call पर span बनता है {id, parent=_current.get(), name, type, inputs}
Step 3 → _current.set(span id): children इसे अपना parent देखते हैं
Step 4 → function await करो; outputs रखो, या exception का repr रखकर दोबारा raise करो
Step 5 → finally: ms latency, _current.reset(token), SPANS में append
Step 6 → print_tree() spans को parent से group करके nested छापता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: a broker complains that classification takes too long. The trace shows `classify_pipeline` 32.2ms, of which `llm` 21.0ms and `retrieve` 11.1ms, so the LLM is the bottleneck (in production, seconds instead of milliseconds). The span inputs also show exactly which prompt produced a wrong HS code.

**Other**: Zomato support bot traces to find which tool call slowed a chat.

## 🟡 Real Example Hindi mein
**Tariff System**: broker शिकायत करता है कि classification में देर लगती है। Trace दिखाता है `classify_pipeline` 32.2ms, जिसमें `llm` 21.0ms और `retrieve` 11.1ms, यानी LLM bottleneck है। Span inputs से यह भी दिखता है कि किस prompt से गलत HS code बना।

**Other**: Zomato support bot में trace से पता चलता है कि कौन सी tool call ने chat धीमी की।

---

## 💻 Code Example — Basic
```python
import time


def timed(fn):
    def wrapper(*args):
        start = time.perf_counter()                       # start the clock
        out = fn(*args)                                   # run the function
        print(fn.__name__, round((time.perf_counter() - start) * 1000, 1), "ms")
        return out
    return wrapper


@timed
def add(a: int, b: int) -> int:
    return a + b


add(1, 2)
```

## 💻 Code Example — Advanced
Run: `python3 main.py`. Observed output of my run (latencies vary slightly per run):
```
classify_pipeline [chain] 32.2ms err=None
  llm [llm] 21.0ms err=None
  retrieve [retriever] 11.1ms err=None
```
Excerpt from `main.py` (the decorator; the file also decorates `retrieve`, `llm`, `pipeline`):
```python
import functools
import time
import uuid
from contextvars import ContextVar
from typing import Any, Awaitable, Callable

_current: ContextVar[str | None] = ContextVar("current_span", default=None)
SPANS: list[dict[str, Any]] = []


def trace(name: str, run_type: str = "chain"):
    def deco(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            span = {"id": uuid.uuid4().hex[:6], "parent": _current.get(), "name": name,
                    "type": run_type, "inputs": args, "error": None}
            token = _current.set(span["id"])              # children see us as parent
            start = time.perf_counter()
            try:
                out = await fn(*args, **kwargs)
                span["outputs"] = out
                return out
            except Exception as exc:
                span["error"] = repr(exc)                 # record, then re-raise
                raise
            finally:
                span["ms"] = round((time.perf_counter() - start) * 1000, 1)
                _current.reset(token)
                SPANS.append(span)
        return wrapper
    return deco
```
Why ContextVar: it keeps the "current span" separate per asyncio task, so concurrent requests do not mix up parents.

---

## 🟠 FastAPI Integration
Put a trace around the request handler; in real LangSmith use `langsmith.traceable` and set env vars.

```python
from fastapi import FastAPI

from main import pipeline, SPANS                          # our module

app = FastAPI()


@app.get("/classify")
async def classify(q: str) -> dict:
    answer = await pipeline(q)                            # spans recorded automatically
    return {"answer": answer, "spans_recorded": len(SPANS)}
```
For LangSmith: set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY`, then decorate with `@traceable(name="classify", run_type="chain")`.

---

## 🔗 LangChain / LangGraph Connection
LangChain and LangGraph trace automatically once the environment variables are set; every runnable and graph node becomes a span. For your own functions use `traceable`.

```python
# from langsmith import traceable
#
# @traceable(run_type="retriever", name="retrieve")
# async def retrieve(q: str) -> list[str]:
#     ...
#
# Env: LANGSMITH_TRACING=true, LANGSMITH_API_KEY=..., LANGSMITH_PROJECT=tariff-prod
ENV_VARS = ["LANGSMITH_TRACING", "LANGSMITH_API_KEY", "LANGSMITH_PROJECT"]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Swallowing exceptions inside the tracer, hiding real errors.
✅ Correct: record the error on the span and re-raise (as `main.py` does).

```python
# Wrong: error swallowed
try:
    out = await fn()
except Exception:
    pass
# Right: record on the span, then re-raise
try:
    out = await fn()
except Exception as exc:
    span["error"] = repr(exc)
    raise
```

❌ Mistake 2: Recording latency only on success. Use `finally` so failed calls are timed and stored.

❌ Mistake 3: Logging full PII or secrets in span inputs. Redact before sending to a tracing backend.

---

## 🧠 Tricky Interview Question
**Q**: "Two requests run concurrently. Why don't their spans get mixed up under a global variable?"

**Answer**: A plain global `current_span` would be overwritten by whichever task ran last. `ContextVar` has a separate value per asyncio task/context, and `reset(token)` restores the previous value on exit. So each request builds its own parent chain. Caveat: `asyncio.gather` copies the context into child tasks, so children correctly inherit the parent span.

---

## ⚫ Interview Questions + Answers

Q1: What is a span?
A1: One timed unit of work with name, parent, inputs, outputs and error.

Q2: Why does `print_tree` sort by ms descending?
A2: To show the slowest child first, making bottlenecks obvious.

Q3: What is `run_type` for?
A3: It labels the span kind (llm, retriever, chain, tool) so the UI can render and aggregate per kind.

Q4: Tracing vs logging?
A4: Logs are flat lines; traces keep parent/child structure, timing and inputs/outputs for one request.

Q5 (Hard): How do you trace in production without slowing requests?
A5: Send spans asynchronously in batches from a background queue, sample a percentage of healthy traffic but keep all errors, redact sensitive fields, and never let the tracing backend failure break the request.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging multi-step chains, agents, RAG
- Finding latency and cost hot spots

❌ Avoid when:
- Inputs are highly sensitive and cannot be redacted

---

## 📊 Visual Diagram
```
 classify_pipeline [chain]  32.2ms
   ├── llm        [llm]        21.0ms
   └── retrieve   [retriever]  11.1ms

 each box = span {id, parent, name, type, inputs, outputs, ms, error}
 ContextVar current_span:  None -> pipeline -> (retrieve | llm) -> back
```

---

## 💰 Cost Impact
Tracing adds tiny latency and storage cost but no LLM tokens. It saves money by showing which step uses the most tokens or time. Sample healthy traces (for example 10%), keep all errors, and trim large payloads.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Span | One recorded step | एक recorded step |
| Trace | Tree of spans for one request | एक request के spans का tree |
| ContextVar | Per-task variable | हर task का अलग variable |
| Run type | Kind of span (llm, tool...) | Span का प्रकार |
| Latency | Time taken | लगा हुआ समय |

---

## ⚡ 3-Line Summary
English: Wrap each step to record parent, inputs, outputs, latency and errors. Spans form a tree that shows where time and failures are. LangSmith does this automatically for LangChain.
Hindi: हर step को wrap करके parent, inputs, outputs, latency और errors record करो। Spans का tree दिखाता है कि समय और failure कहाँ है। LangChain के लिए LangSmith यह अपने आप करता है।

---

## ➡️ Next Topic
**591. Build Caching Layer for LLM** — traces reveal repeated identical calls; next we avoid paying for them.
