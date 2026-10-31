---

# 429. Langfuse Tracing
# हिंदी में: Langfuse Tracing (हर LLM call का हिसाब)

---

## 🔵 Simple Definition (English)
Langfuse is an open-source LLM observability platform. Tracing means recording every step of one user request (prompt, retrieval, LLM call, tool call) as a **trace** made of nested **spans** and **generations**, with latency, tokens, cost and errors attached. You can then open any request in a UI and see exactly what happened.

## 🔵 सरल परिभाषा (Hindi)
Langfuse एक open-source LLM observability platform है। Tracing का मतलब है एक user request के हर step (prompt, retrieval, LLM call, tool call) को **trace** के अंदर nested **spans** और **generations** के रूप में record करना, साथ में latency, tokens, cost और errors। फिर UI में किसी भी request को खोलकर देख सकते हैं कि अंदर क्या हुआ।

---

## 🔴 Problem it Solves
- A normal log line says "request failed". An LLM app has 5-10 hidden steps (rewrite query, retrieve, rerank, generate, validate). Without tracing you cannot tell which step produced the bad HS code.
- LLM output is non-deterministic: you cannot reproduce a bug from the input alone, you need the exact prompt, model, temperature and retrieved context that were used.
- Cost and latency are per-step, not per-request. Without traces you cannot see that retrieval takes 2 s while the LLM takes 0.8 s.

## 🔴 यह क्यों बना? (Hindi)
- Normal log कहता है "request failed"। LLM app में 5-10 छुपे steps होते हैं। Tracing के बिना पता नहीं चलता कि गलत HS code किस step ने दिया।
- LLM output non-deterministic है, bug reproduce करने के लिए exact prompt, model, temperature और retrieved context चाहिए।
- Cost और latency हर step की अलग होती है, trace से दिखता है कि retrieval 2 s ले रहा है और LLM सिर्फ 0.8 s।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives; a TRACE is opened (trace_id, user_id, session_id)
Step 2 → Each function decorated with @observe becomes a SPAN (nested automatically)
Step 3 → LLM calls are recorded as GENERATION (model, prompt, output, tokens, cost)
Step 4 → SDK buffers events in memory and sends them in background batches (async, non-blocking)
Step 5 → Langfuse server stores traces; UI shows tree + timeline + cost
Step 6 → You attach scores (user feedback, eval result) to the trace for later analysis
Step 7 → On shutdown call flush() so buffered events are not lost
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Request आती है, TRACE खुलता है (trace_id, user_id, session_id)
Step 2 → @observe लगा हर function एक SPAN बनता है (अपने आप nested)
Step 3 → LLM call GENERATION के रूप में record होती है (model, prompt, output, tokens, cost)
Step 4 → SDK events को memory में buffer करके background में batch भेजता है (non-blocking)
Step 5 → Server trace store करता है; UI में tree, timeline और cost दिखते हैं
Step 6 → Trace पर score (user feedback, eval) जोड़ सकते हैं
Step 7 → Shutdown पर flush() ज़रूर करो ताकि events खोएं नहीं
```

---

## 🟡 Real World Example
**Tariff Classification System**: User sends "Bluetooth speaker, plastic body, 20W". The pipeline is: `normalize_input` -> `retrieve_hs_chunks` -> `classify_llm` -> `validate_code`. A customs officer complains that the code returned was wrong. In Langfuse you open that trace and see: retrieval returned chapter 85 chunks but the correct heading (8518) was ranked 9th and cut by `top_k=5`. Fix is in retrieval, not the prompt. Without the trace, the team would have wasted days tuning the prompt.

**Zomato-style**: "Show me spicy veg dishes under 300" - a trace shows the intent-parser LLM produced a wrong price filter, so the search service returned nothing.

## 🟡 Real Example Hindi mein
**Tariff System**: User लिखता है "Bluetooth speaker, plastic body, 20W"। Pipeline: `normalize_input` -> `retrieve_hs_chunks` -> `classify_llm` -> `validate_code`। Customs officer कहता है code गलत है। Langfuse में वह trace खोलने पर दिखता है कि सही heading (8518) 9वीं रैंक पर थी और `top_k=5` ने उसे काट दिया। Fix retrieval में है, prompt में नहीं। Trace के बिना टीम दिन भर prompt ही बदलती रहती।

---

## 💻 Code Example — Basic
Pure-Python mini tracer that shows the idea behind `@observe` (runs offline, no Langfuse needed).

```python
# Mini tracer: same idea as Langfuse's @observe decorator
import time                                   # for measuring latency
import uuid                                   # for unique span ids
import functools                              # to keep function metadata in decorator
from typing import Any, Callable              # type hints

TRACE: list[dict[str, Any]] = []              # in-memory store of finished spans
_STACK: list[str] = []                        # stack of currently open span ids (for nesting)


def observe(name: str) -> Callable:           # decorator factory taking a span name
    def deco(fn: Callable) -> Callable:       # real decorator
        @functools.wraps(fn)                  # keep original name/docstring
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            span_id = uuid.uuid4().hex[:8]    # short unique id for this span
            parent = _STACK[-1] if _STACK else None  # parent is the span on top of stack
            _STACK.append(span_id)            # we are now inside this span
            start = time.perf_counter()       # start timer
            error: str | None = None          # no error yet
            try:
                return fn(*args, **kwargs)    # run the real function
            except Exception as exc:          # capture any error
                error = repr(exc)             # remember error text
                raise                         # re-raise: tracing must not hide errors
            finally:
                _STACK.pop()                  # leave span
                TRACE.append({                # store the span record
                    "id": span_id, "parent": parent, "name": name,
                    "ms": round((time.perf_counter() - start) * 1000, 2),
                    "error": error,
                })
        return wrapper
    return deco


@observe("retrieve")                          # span 1
def retrieve(q: str) -> list[str]:
    time.sleep(0.02)                          # fake DB latency
    return ["8518: loudspeakers", "8517: phones"]


@observe("classify")                          # span 2 (fake LLM)
def classify(q: str, ctx: list[str]) -> str:
    time.sleep(0.05)                          # fake LLM latency
    return "8518.22"


@observe("pipeline")                          # root span
def pipeline(q: str) -> str:
    return classify(q, retrieve(q))           # nested calls become child spans


print(pipeline("Bluetooth speaker"))          # run the pipeline
for s in TRACE:                               # print the recorded spans
    print(s)
```

## 💻 Code Example — Advanced
Real Langfuse Python SDK v3 (`pip install langfuse openai`). Needs `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`, `OPENAI_API_KEY`.

```python
# Production tracing with Langfuse SDK v3 + OpenAI (async, typed, safe)
import asyncio                                      # to run the async demo
import logging                                      # log tracing problems, never crash on them
from typing import Any                              # type hints

from langfuse import get_client, observe            # Langfuse v3 entry points
from langfuse.openai import AsyncOpenAI             # drop-in OpenAI client that auto-traces generations

logger = logging.getLogger("tariff")                # module logger
langfuse = get_client()                             # singleton client (reads env vars)
client = AsyncOpenAI()                              # traced OpenAI client (tokens + cost captured)


@observe(name="retrieve_hs_chunks")                 # span for retrieval step
async def retrieve(query: str) -> list[str]:
    await asyncio.sleep(0.01)                       # replace with real vector search
    return ["8518 Loudspeakers", "8517 Telephone sets"]  # fake chunks


@observe(as_type="generation", name="classify_llm") # mark as LLM generation
async def classify(query: str, chunks: list[str]) -> str:
    resp = await client.chat.completions.create(    # normal OpenAI call; Langfuse wraps it
        model="gpt-4o-mini",                        # cheap model
        temperature=0,                              # deterministic classification
        max_tokens=60,                              # cap output cost
        messages=[
            {"role": "system", "content": "Return only the best HS code."},
            {"role": "user", "content": f"Product: {query}\nCandidates: {chunks}"},
        ],
    )
    return resp.choices[0].message.content or ""    # text answer (may be None)


@observe(name="tariff_request")                     # root span = the trace
async def classify_product(query: str, user_id: str, session_id: str) -> dict[str, Any]:
    langfuse.update_current_trace(                  # attach searchable metadata to the trace
        user_id=user_id, session_id=session_id,
        tags=["tariff", "prod"], metadata={"feature": "hs-classify"},
    )
    try:
        chunks = await retrieve(query)              # step 1
        code = await classify(query, chunks)        # step 2
        return {"hs_code": code, "trace_id": langfuse.get_current_trace_id()}
    except Exception as exc:                        # log and re-raise, trace records the error
        logger.exception("classification failed: %s", exc)
        raise


if __name__ == "__main__":
    print(asyncio.run(classify_product("Bluetooth speaker", "u1", "s1")))  # run once
    langfuse.flush()                                # send buffered events before exit
```

---

## 🟠 FastAPI Integration
Return `trace_id` to the client so support can paste it and find the exact trace. Flush on shutdown with `lifespan`.

```python
# FastAPI + Langfuse: trace id in response, flush at shutdown
from contextlib import asynccontextmanager          # for lifespan
from fastapi import FastAPI, HTTPException          # web framework
from pydantic import BaseModel                      # request validation (v2)
from langfuse import get_client                     # langfuse client

from tariff_service import classify_product         # the traced function from above


@asynccontextmanager
async def lifespan(app: FastAPI):                   # startup/shutdown hook
    yield                                           # app runs here
    get_client().flush()                            # make sure last traces are sent


app = FastAPI(lifespan=lifespan)                    # create app


class Req(BaseModel):                               # input schema
    product: str
    user_id: str = "anon"
    session_id: str = "default"


@app.post("/classify")                              # POST /classify
async def classify_route(req: Req) -> dict:
    try:
        return await classify_product(req.product, req.user_id, req.session_id)
    except Exception as exc:                        # hide internals from the client
        raise HTTPException(status_code=502, detail="classification failed") from exc
```

---

## 🔗 LangChain / LangGraph Connection
Langfuse ships a LangChain `CallbackHandler`. Pass it in `config` and every chain/graph node becomes a span automatically.

```python
# LangChain / LangGraph with Langfuse callback (v3 import path)
from langfuse.langchain import CallbackHandler                 # callback handler
from langchain_openai import ChatOpenAI                        # chat model
from langchain_core.prompts import ChatPromptTemplate          # prompt template

handler = CallbackHandler()                                    # reads env keys
prompt = ChatPromptTemplate.from_template("HS code for: {p}")  # simple prompt
chain = prompt | ChatOpenAI(model="gpt-4o-mini")               # LCEL chain

out = chain.invoke({"p": "Bluetooth speaker"},                 # run chain
                   config={"callbacks": [handler]})            # enable tracing for this call
print(out.content)

# LangGraph: same config works -> graph.invoke(state, config={"callbacks": [handler]})
# Each node shows as a span, each LLM call as a generation.
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Not flushing in short-lived scripts / serverless
✅ Correct: call `flush()` (or `shutdown()`) before the process ends.

```python
# Wrong: process exits, buffered traces lost
result = asyncio.run(classify_product("speaker", "u1", "s1"))

# Right: flush before exit
result = asyncio.run(classify_product("speaker", "u1", "s1"))
get_client().flush()
```

❌ Mistake 2: Logging raw PII / secrets inside traces
✅ Correct: mask inputs before they are recorded.

```python
# Wrong: full customer email and address stored in trace input
@observe()
def f(email: str) -> str: ...

# Right: disable capture for sensitive args and pass a masked copy
@observe(capture_input=False)
def f(email: str) -> str: ...
```

---

## 🧠 Tricky Interview Question
**Q**: "Tracing is on, but p99 latency of your API increased by 200 ms after adding Langfuse. Why and how do you fix it?"

**Answer**: Langfuse SDK sends events in a background thread, so it should not block. Likely causes: (1) calling `flush()` inside the request path, (2) `capture_input/output` of huge documents (serialisation cost on the hot path), (3) synchronous custom exporter. Fix: flush only at shutdown, truncate/mask big payloads, use sampling (e.g. trace 10% of traffic, but 100% of errors), and keep the Langfuse host close to the app.

---

## ⚫ Interview Questions + Answers

Q1 (Easy): What is the difference between a trace, a span and a generation?
A1: A trace is one end-to-end request. A span is one timed step inside it. A generation is a special span for an LLM call that also stores model, prompt, completion, token usage and cost.

Q2 (Easy): Why not just use print/logging?
A2: Logs are flat and unlinked. Traces keep parent-child structure, timings, tokens and cost per step, and let you search by user or session and replay the exact inputs.

Q3 (Medium): How do you trace a multi-turn chat conversation?
A3: Set the same `session_id` on every trace of that conversation. Langfuse groups them into a session view so you can read the whole dialogue and see where it went wrong.

Q4 (Medium): How do you control tracing cost and volume in production?
A4: Use sampling (`sample_rate`), always keep error traces, truncate large inputs, mask PII, set retention, and self-host Langfuse if data cannot leave your network.

Q5 (Hard): Design tracing for a RAG agent with parallel tool calls so that latency of each branch is visible.
A5: Wrap each tool and retrieval in its own `@observe` span. With async code the context is propagated through `contextvars`, so parallel `asyncio.gather` tasks become sibling spans under the same parent and the timeline shows overlap. For threads or queues, pass the trace context explicitly (trace_id / parent observation id), otherwise spans become orphan traces.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-step pipelines (RAG, agents) where you must find the failing step
- You need cost and latency per user, feature or prompt version
- You need a data set of real production traces for later evaluation

❌ Avoid when:
- A single one-off script with one LLM call (simple logs are enough)
- Data is so sensitive that it cannot be stored and masking is not possible (self-host or redact)

---

## 📊 Visual Diagram
```
 Trace: tariff_request  (user=u1, session=s1)   total 1.9 s, $0.0004
 │
 ├── span: retrieve_hs_chunks        ████░░░░░░░░░░░░  0.6 s
 │
 ├── generation: classify_llm        ░░░░████████░░░░  1.1 s
 │        model=gpt-4o-mini  in=420 out=12  $0.00007
 │
 └── span: validate_code             ░░░░░░░░░░░░░░██  0.2 s

 App ──(batch, async)──> Langfuse server ──> UI / API / scores
```

---

## 💰 Cost Impact
- Langfuse itself is free if self-hosted; cloud has event-based pricing, so fewer events = lower bill.
- Tracing does not add LLM tokens. It records `prompt_tokens` and `completion_tokens` so you can find expensive steps. Example: 420 input + 12 output tokens on gpt-4o-mini is about $0.00007 per request.
- Optimise: sample non-critical traffic, truncate big context fields, avoid tracing tiny helper functions, use traces to find prompts with too many tokens and shorten them.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | One full request | एक पूरी request का record |
| Span | Timed step inside a trace | Trace का एक timed step |
| Generation | Span for an LLM call | LLM call का record |
| Session | Group of traces (a conversation) | बातचीत के traces का group |
| Score | Numeric/label feedback on a trace | Trace पर rating/eval |
| Flush | Force-send buffered events | Buffer का data भेज देना |
| Sampling | Trace only a % of requests | कुछ % requests ही trace करना |

---

## ⚡ 3-Line Summary
English: Langfuse records each request as a trace of nested spans and generations with latency, tokens and cost. Use `@observe`, the OpenAI drop-in client or the LangChain callback, and always set user and session ids. Flush on shutdown, mask PII and sample high traffic.
Hindi: Langfuse हर request को trace के रूप में record करता है, nested spans और generations के साथ latency, tokens और cost। `@observe`, OpenAI drop-in client या LangChain callback use करो और user/session id ज़रूर लगाओ। Shutdown पर flush करो, PII mask करो और ज़्यादा traffic में sampling करो।

---

## ➡️ Next Topic
**430. Langfuse Evaluation** — tracing shows what happened; evaluation scores whether it was good (LLM-as-judge, user feedback, datasets).
