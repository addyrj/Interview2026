---

# 269. LangChain Tracing
# हिंदी में: LangChain Tracing (हर step को देखना)

---

## 🔵 Simple Definition (English)
Tracing records every step of a chain run: the input, the final prompt, the model output, token counts, latency, errors and the parent-child tree of steps. In LangChain you get it from **callbacks** (your own code) or **LangSmith** (hosted trace UI, turned on with environment variables). It is the "debugger and profiler" of LLM apps.

## 🔵 सरल परिभाषा (Hindi)
Tracing chain के चलने के हर step को record करता है: input, final prompt, model का output, token counts, latency, errors और steps का parent-child tree। LangChain में यह **callbacks** (आपका अपना code) या **LangSmith** (hosted trace UI, environment variables से on) से मिलता है। यह LLM apps का "debugger और profiler" है।

---

## 🔴 Problem it Solves
LLM apps are non-deterministic and made of many hidden steps (prompt building, retrieval, model, parser, tools). When the answer is wrong or slow you cannot tell *which* step is guilty with `print()`. You also cannot answer "why did yesterday's bill double?" without per-request token data.

## 🔴 यह क्यों बना? (Hindi)
LLM apps non-deterministic होते हैं और कई छिपे steps से बने होते हैं (prompt बनाना, retrieval, model, parser, tools)। Answer गलत या धीमा हो तो `print()` से पता नहीं चलता कि कौन-सा step दोषी है। "कल का bill दोगुना क्यों हुआ?" का जवाब भी per-request token data के बिना नहीं मिल सकता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every Runnable run creates a "run" object with a run_id and parent_run_id
Step 2 → LangChain fires callback events: on_chain_start, on_llm_start, on_llm_end, on_tool_start, on_*_error
Step 3 → Callback handlers (yours or LangSmith's tracer) receive those events
Step 4 → LangSmith tracer batches runs and sends them in the background (non-blocking)
Step 5 → UI shows a tree: chain -> prompt -> model -> parser, with inputs/outputs/tokens/time
Step 6 → You add tags, metadata and run_name to filter traces (user_id, version, env)
Step 7 → Use traces for debugging, cost reports, datasets for evaluation and regression tests
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर Runnable run का एक "run" object बनता है जिसमें run_id और parent_run_id होता है
Step 2 → LangChain callback events चलाता है: on_chain_start, on_llm_start, on_llm_end, on_tool_start, on_*_error
Step 3 → Callback handlers (आपके या LangSmith के tracer) ये events receive करते हैं
Step 4 → LangSmith tracer runs को background में batch करके भेजता है (non-blocking)
Step 5 → UI में tree दिखता है: chain -> prompt -> model -> parser, inputs/outputs/tokens/time के साथ
Step 6 → tags, metadata और run_name जोड़ो ताकि filter कर सको (user_id, version, env)
Step 7 → Traces से debugging, cost report, evaluation datasets और regression tests बनते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A user complains "earbuds were classified as toys". In LangSmith you open the trace by `metadata.request_id`, see that the **retriever** returned chapter 95 (toys) chunks at the top, so the LLM was misled. The bug is in retrieval, not in the model - without tracing you might have wasted days tuning the prompt. The same dashboard shows p95 latency per step and cost per route.

**Zomato-style**: Trace shows the "allergen check" step takes 70% of the time. **Amazon-style**: Compare token cost of two prompt versions via tags `prompt_v1` vs `prompt_v2`.

## 🟡 Real Example Hindi mein
**Tariff System**: User शिकायत करता है "earbuds को toys में classify किया"। LangSmith में `metadata.request_id` से trace खोलकर दिखता है कि **retriever** ने सबसे ऊपर chapter 95 (toys) के chunks दिए थे, इसलिए LLM भटका। Bug retrieval में है, model में नहीं - tracing के बिना prompt tune करने में दिन बर्बाद हो सकते थे। वही dashboard हर step का p95 latency और route-wise cost दिखाता है।

**Zomato-style**: Trace बताता है "allergen check" में 70% समय जाता है। **Amazon-style**: Tags `prompt_v1` बनाम `prompt_v2` से दो prompts का token cost compare।

---

## 💻 Code Example — Basic
```python
# Basic tracing with a custom callback handler -- runs OFFLINE (fake model)
# pip install langchain-core
import time                                                        # to measure latency
from typing import Any                                             # type hints
from uuid import UUID                                              # run ids are UUIDs

from langchain_core.callbacks import BaseCallbackHandler           # base class for handlers
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel  # fake LLM
from langchain_core.messages import AIMessage                      # fake reply type
from langchain_core.output_parsers import StrOutputParser          # to str
from langchain_core.outputs import LLMResult                       # result passed to on_llm_end
from langchain_core.prompts import ChatPromptTemplate              # prompt


class TimingTracer(BaseCallbackHandler):                           # our mini "LangSmith"
    def __init__(self) -> None:
        self.starts: dict[UUID, float] = {}                        # run_id -> start time
        self.events: list[str] = []                                # collected trace lines

    def on_chain_start(self, serialized: Any, inputs: Any, *, run_id: UUID, **kwargs: Any) -> None:
        self.starts[run_id] = time.perf_counter()                  # remember start
        self.events.append(f"chain_start name={kwargs.get('name')} inputs={inputs}")  # log

    def on_chat_model_start(self, serialized: Any, messages: Any, *, run_id: UUID, **kwargs: Any) -> None:
        self.starts[run_id] = time.perf_counter()                  # chat models fire this, not on_llm_start
        self.events.append(f"model_start prompt={messages[0][-1].content!r}")  # log final prompt text

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs: Any) -> None:
        ms = (time.perf_counter() - self.starts.get(run_id, 0)) * 1000  # latency in ms
        text = response.generations[0][0].text                     # model output text
        self.events.append(f"model_end {ms:.1f}ms output={text!r}")  # log

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        self.events.append(f"ERROR {type(error).__name__}: {error}")  # log failures


llm = GenericFakeChatModel(messages=iter([AIMessage(content="HS 8518.30")]))  # fake model
chain = ChatPromptTemplate.from_template("Classify: {product}") | llm | StrOutputParser()  # LCEL chain

tracer = TimingTracer()                                            # create handler
result = chain.invoke(                                             # run the chain
    {"product": "earbuds"},
    config={"callbacks": [tracer], "run_name": "classify", "tags": ["demo"], "metadata": {"user": "u1"}},
)
print("RESULT:", result)                                           # final answer
for line in tracer.events:                                         # show collected trace
    print(" ", line)                                               # one line per event
```

## 💻 Code Example — Advanced
```python
# Production: LangSmith via env vars + per-request metadata + token/cost callback + sampling
# pip install langchain-openai langsmith
import logging                                                     # logging
import os                                                          # env access
import random                                                      # sampling
import uuid                                                        # request ids
from typing import Any                                             # hints

from langchain_core.callbacks import AsyncCallbackHandler          # async handler for async apps
from langchain_core.outputs import LLMResult                       # llm result
from langchain_core.output_parsers import StrOutputParser          # parser
from langchain_core.prompts import ChatPromptTemplate              # prompt
from langchain_openai import ChatOpenAI                            # model
from langsmith import traceable                                    # decorator for non-LangChain functions

logger = logging.getLogger("tariff.trace")                         # logger

# --- LangSmith switches (set in the environment / secret manager, not in code) ---
# LANGSMITH_TRACING=true            -> turn tracing on (older name: LANGCHAIN_TRACING_V2)
# LANGSMITH_API_KEY=<key>           -> auth
# LANGSMITH_PROJECT=tariff-prod     -> group traces per project
# LANGSMITH_TRACING_SAMPLING_RATE=0.1 can also be used by some SDK versions; below we sample ourselves.
os.environ.setdefault("LANGSMITH_PROJECT", "tariff-dev")          # default project for local runs

PRICE_IN, PRICE_OUT = 0.15 / 1_000_000, 0.60 / 1_000_000          # gpt-4o-mini $/token


class CostTracker(AsyncCallbackHandler):                           # records tokens + cost per request
    def __init__(self) -> None:
        self.input_tokens = 0                                      # running total
        self.output_tokens = 0                                     # running total

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        for gens in response.generations:                          # each prompt's generations
            for g in gens:
                usage = getattr(getattr(g, "message", None), "usage_metadata", None) or {}  # standard usage
                self.input_tokens += usage.get("input_tokens", 0)  # add input tokens
                self.output_tokens += usage.get("output_tokens", 0)  # add output tokens

    @property
    def cost_usd(self) -> float:
        return self.input_tokens * PRICE_IN + self.output_tokens * PRICE_OUT  # dollars


chain = (
    ChatPromptTemplate.from_messages([("system", "Return HS code."), ("user", "{product}")])
    | ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=50)
    | StrOutputParser()
)


@traceable(name="normalize_product", run_type="tool")              # non-LangChain code shows up in the trace tree
def normalize(text: str) -> str:
    return " ".join(text.lower().split())                          # simple normalization


async def classify(product: str, user_id: str) -> dict[str, Any]:
    tracker = CostTracker()                                        # one tracker per request
    request_id = str(uuid.uuid4())                                 # correlate logs <-> traces
    config: dict[str, Any] = {
        "run_name": "tariff_classify",                             # readable name in UI
        "tags": ["prod", "prompt_v3"],                             # filter by tag
        "metadata": {"user_id": user_id, "request_id": request_id},  # searchable metadata (no PII!)
        "callbacks": [tracker],                                    # attach our handler
    }
    try:
        answer = await chain.ainvoke({"product": normalize(product)}, config=config)  # traced run
    except Exception:
        logger.exception("request_id=%s failed", request_id)       # error is also visible in the trace
        raise                                                      # let caller map to HTTP error
    logger.info("request_id=%s tokens=%d/%d cost=$%.6f", request_id,
                tracker.input_tokens, tracker.output_tokens, tracker.cost_usd)  # your own metrics
    return {"answer": answer, "request_id": request_id, "cost_usd": round(tracker.cost_usd, 8)}
```

---

## 🟠 FastAPI Integration
Return the `request_id` to the client (header or body). When a user reports a problem, support pastes the id and you find the exact trace. Never put raw PII (names, ID numbers, full invoices) in tags/metadata - traces are stored by a third party unless self-hosted.

```python
# FastAPI + tracing metadata + request-id header
from fastapi import FastAPI, Header                                # framework
from pydantic import BaseModel, Field                              # validation

app = FastAPI()                                                    # app

class Req(BaseModel):                                              # input
    product: str = Field(min_length=2, max_length=300)             # bounds

@app.post("/classify")                                             # route
async def classify_route(req: Req, x_user_id: str = Header(default="anon")) -> dict[str, object]:
    return await classify(req.product, user_id=x_user_id)          # classify() from Advanced above
    # response includes request_id -> support can open the exact LangSmith trace
```

---

## 🔗 LangChain / LangGraph Connection
- **Config keys** accepted by every Runnable: `callbacks`, `tags`, `metadata`, `run_name`, `max_concurrency`. They propagate to child runs automatically.
- **`astream_events`** gives a live event feed of the same internal steps (good for UI progress).
- **LangGraph**: every node is a traced run; the trace shows the graph path, state updates and tool calls. With checkpointers you can replay/time-travel. LangGraph Studio uses the same traces.
- **Alternatives**: OpenTelemetry / Langfuse / Arize Phoenix via their LangChain callback handlers; self-hosted if data cannot leave your VPC.
- Debug quickly in dev: `from langchain_core.globals import set_debug; set_debug(True)` prints all steps to stdout (very verbose, never in prod).

```python
# Quick local debugging without any service
from langchain_core.globals import set_debug, set_verbose         # global debug switches
set_debug(True)                                                    # prints every run with inputs/outputs
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: 100% tracing with full payloads in production (cost + privacy)
```python
# Wrong -- every request, every document chunk, PII included, sent out
LANGSMITH_TRACING=true   # no sampling, no masking

# Right -- sample (e.g. 10%) + 100% of errors, and mask sensitive fields
# use sampling_rate, hide_inputs/hide_outputs on the LangSmith Client, or self-host
```

❌ Mistake 2: Forgetting to pass `config` into nested calls, so child runs are detached
```python
# Wrong -- inside a tool/function you call chain.invoke(x) without config: it appears as a separate root trace
def my_tool(q: str) -> str:
    return inner_chain.invoke(q)

# Right -- accept and forward config (RunnableConfig) so the tree stays connected
def my_tool(q: str, config: RunnableConfig) -> str:
    return inner_chain.invoke(q, config)
```

❌ Mistake 3: Relying on `print()` or `set_debug(True)` in production - unstructured, slow, leaks data.

---

## 🧠 Tricky Interview Question

**Q**: "Your traces show the LLM step takes only 1.2 s, but users see 6 s responses. Where do you look?"

**Answer**: The latency is outside the model step. In the trace tree check the *other* children and the gaps: retrieval (vector DB), reranker, tool calls, prompt formatting with a huge context, output parser, or sequential steps that could be parallel. Also look at time *before* the root run starts (queueing, cold start, auth middleware, DB lookups in FastAPI) - that is invisible to LangChain tracing and needs APM spans (OpenTelemetry) on the web layer. Compare the root run's duration with the sum of children to find "dark time". Also check whether tracing itself is blocking (a synchronous tracer or a slow callback handler can add latency; LangSmith sends in a background thread).

---

## ⚫ Interview Questions + Answers

Q1: What is a callback handler in LangChain?
A1: A class with methods like `on_chain_start`, `on_llm_end`, `on_tool_error` that LangChain calls during a run. You use it for logging, metrics, token counting or streaming.

Q2: How do you enable LangSmith tracing?
A2: Set env vars `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, and optionally `LANGSMITH_PROJECT` (older code uses `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`). No code change is required; all Runnables are traced automatically.

Q3: What is the difference between tags and metadata?
A3: Tags are simple string labels for filtering (`"prod"`, `"prompt_v3"`). Metadata is key-value data (`user_id`, `request_id`, `model_version`). Both are inherited by child runs.

Q4: How do you trace a plain Python function?
A4: Decorate it with `@traceable` from `langsmith` (or wrap it in `RunnableLambda`). It then appears as a node in the trace tree.

Q5 (Hard): Design an observability strategy for an LLM service with 1M requests/day and privacy constraints.
A5: Three layers. (1) Metrics for every request, cheap: latency, tokens, cost, status, tier/model, cache hit - exported to Prometheus/OpenTelemetry. (2) Traces for a sample (e.g. 5-10%) plus 100% of errors and slow requests (tail-based sampling), with PII masking (hide inputs/outputs or redact before sending) or a self-hosted tracer (LangSmith self-hosted, Langfuse, Phoenix). (3) Offline evaluation: save failed/low-rated traces to a dataset, replay with new prompt versions before release. Add request_id correlation between API logs and traces, retention limits, and access control. Alert on cost per request and error-rate drift.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging wrong answers or latency (always in dev/staging)
- Measuring cost and token use per route/user/version
- Building evaluation datasets from real traffic
- Multi-step agents and graphs (essential)

❌ Avoid / be careful when:
- Data is sensitive and the tracer is third-party hosted (mask or self-host)
- Very high traffic and 100% tracing (sample instead)
- Using it as the only monitoring - you still need normal APM and alerts

---

## 📊 Visual Diagram
```
 Request (request_id=ab12, tags=[prod,prompt_v3])
 └── tariff_classify                  total 2.9s   tokens 412   $0.00009
     ├── normalize_product            0.001s
     ├── ChatPromptTemplate           0.002s
     ├── retriever (vector DB)        0.8s    <- slow? look here
     ├── ChatOpenAI gpt-4o-mini       1.9s    in=380 out=32
     └── StrOutputParser              0.001s

 events ──► callbacks ──► [ your CostTracker ]  [ LangSmith tracer ] ──► UI
```

---

## 💰 Cost Impact
- Tracing adds **no LLM tokens**. LangSmith itself is billed by trace volume/retention (check current plan), so sampling reduces that bill; self-hosting trades money for ops work.
- Tracing is how you *find* savings: sort traces by token count to spot oversized prompts (e.g. a 6,000-token retrieval context when 1,500 is enough: 4,500 x $0.15/1M = $0.000675 saved per request; at 1M requests/day = $675/day).
- Track per-request cost = input_tokens x price_in + output_tokens x price_out (see CostTracker). Alert if the daily average rises by more than 20%.
- Keep trace payload small: do not attach huge documents as inputs (storage and privacy cost).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | Full record of one request | एक request का पूरा record |
| Run / span | One step inside a trace | Trace का एक step |
| Callback handler | Code called on lifecycle events | Events पर चलने वाला code |
| LangSmith | LangChain's hosted tracing/eval platform | LangChain का tracing platform |
| Tags / metadata | Labels and key-values for filtering | Filter के लिए labels |
| Sampling | Trace only a fraction of requests | कुछ ही requests trace करना |
| p95 latency | 95% of requests are faster than this | 95% requests इससे तेज़ |
| PII masking | Hiding personal data | निजी data छिपाना |

---

## ⚡ 3-Line Summary
English: Tracing records every step, token and latency of a chain, using callbacks or LangSmith (enabled by env vars). Add run_name, tags and metadata with a request_id so you can find any trace. Sample in production, mask PII, and use traces to cut cost and debug.
Hindi: Tracing chain के हर step, token और latency को record करता है - callbacks या LangSmith (env vars से on) के ज़रिए। run_name, tags और request_id वाला metadata जोड़ो ताकि कोई भी trace मिल सके। Production में sampling करो, PII mask करो, और traces से cost घटाओ व debug करो।

---

## ➡️ Next Topic
**270. LangChain Best Practices** - putting it all together: project structure, LCEL style, versioned prompts, testing and production checklists.
