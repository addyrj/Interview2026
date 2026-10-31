---

# 419. Tracing in LangSmith
# हिंदी में: LangSmith में Tracing

---

## 🔵 Simple Definition (English)
Tracing means recording the full tree of steps behind one request: parent run, child runs (retriever, LLM, tools), with inputs, outputs, timings, token counts and errors. In LangSmith you get this automatically for LangChain/LangGraph, and with `@traceable` or `wrap_openai` for your own code.

## 🔵 सरल परिभाषा (Hindi)
Tracing का मतलब एक request के पीछे के सभी steps का पूरा tree record करना: parent run, child runs (retriever, LLM, tools), inputs, outputs, timing, token counts और errors के साथ। LangSmith में LangChain/LangGraph के लिए यह अपने-आप होता है, और अपने code के लिए `@traceable` या `wrap_openai` से।

---

## 🔴 Problem it Solves
- A final wrong answer hides which step went wrong.
- Logs from different async tasks get interleaved and cannot be tied back to one user request.
- Without timing per step, you guess which part is slow; without token counts per step, you guess which part is expensive.

## 🔴 यह क्यों बना? (Hindi)
- Final answer गलत हो तो पता नहीं चलता कौन सा step गलत था।
- अलग async tasks के logs आपस में मिल जाते हैं और एक user request से जोड़ना मुश्किल होता है।
- हर step का timing न हो तो धीमा हिस्सा अंदाज़े से ढूँढना पड़ता है; token count न हो तो महँगा हिस्सा भी अंदाज़े से।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request enters; a ROOT run is created (run_id, start time)
Step 2 → Each decorated function / chain step creates a CHILD run (parent_run_id)
Step 3 → Context variables (contextvars) track "current run" across async calls
Step 4 → On finish, run stores outputs, end time, error (if any), token usage
Step 5 → Runs are batched and sent to LangSmith in a background thread
Step 6 → UI rebuilds the tree: waterfall of latency, tokens, cost
Step 7 → Add tags + metadata (user_id, version) to filter later
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Request आती है; ROOT run बनता है (run_id, start time)
Step 2 → हर decorated function / chain step एक CHILD run बनाता है (parent_run_id)
Step 3 → Async calls में "current run" को contextvars track करते हैं
Step 4 → Finish पर run में outputs, end time, error, token usage save होता है
Step 5 → Runs batch होकर background thread में LangSmith भेजे जाते हैं
Step 6 → UI tree बनाता है: latency, tokens, cost का waterfall
Step 7 → बाद में filter के लिए tags + metadata (user_id, version) जोड़ो
```

---

## 🟡 Real World Example
**Tariff Classification System**: One request creates this trace tree:
`classify_request (2.1s)` -> `rewrite_query (0.5s, 180 tok)` -> `retrieve (0.4s)` -> `llm_classify (1.1s, 1,450 tok)` -> `validate_code (3ms)`. A broker complains about a slow answer; the waterfall shows the slow part is `llm_classify` because the prompt carries 8 retrieved chunks. The team reduces to 4 chunks, latency falls to 1.3s and tokens by 40%. Tag `tier=pro` lets them compare latency by customer plan.

**Amazon-style assistant**: Traces carry `session_id` so the whole multi-turn conversation can be opened as a thread.

## 🟡 Real Example Hindi mein
**Tariff System**: एक request से यह trace tree बनता है:
`classify_request (2.1s)` -> `rewrite_query (0.5s, 180 tok)` -> `retrieve (0.4s)` -> `llm_classify (1.1s, 1,450 tok)` -> `validate_code (3ms)`। Broker धीमे answer की शिकायत करता है; waterfall में दिखता है कि `llm_classify` धीमा है क्योंकि prompt में 8 chunks हैं। Team 4 chunks कर देती है, latency 1.3s और tokens 40% कम। Tag `tier=pro` से customer plan के हिसाब से latency compare होती है।

**Amazon-style assistant**: Traces में `session_id` रहता है, ताकि पूरी multi-turn बातचीत एक thread की तरह खुल सके।

---

## 💻 Code Example — Basic
```python
# Basic: build a nested trace tree by hand to understand parent/child runs (offline)
import contextvars                                            # tracks current run across calls
import time                                                   # timings
import uuid                                                   # run ids
from typing import Any, Callable                              # typing

current_run: contextvars.ContextVar[str | None] = contextvars.ContextVar("current_run", default=None)
RUNS: list[dict[str, Any]] = []                               # flat list; parent_id builds the tree

def traced(name: str, tags: list[str] | None = None) -> Callable:   # mini @traceable
    def deco(fn: Callable) -> Callable:
        def wrapper(*a: Any, **k: Any) -> Any:
            rid = uuid.uuid4().hex[:6]                        # new run id
            run = {"id": rid, "parent": current_run.get(), "name": name, "tags": tags or []}  # link to parent
            token = current_run.set(rid)                      # children will see this as parent
            t0 = time.perf_counter()                          # start timer
            try:
                out = fn(*a, **k)                             # execute the step
                run["output"] = out                           # record output
                return out
            except Exception as exc:                          # record error then re-raise
                run["error"] = repr(exc); raise
            finally:
                run["ms"] = round((time.perf_counter() - t0) * 1000, 2)  # duration
                current_run.reset(token)                      # restore previous parent
                RUNS.append(run)                              # save
        return wrapper
    return deco

@traced("retrieve")
def retrieve(q: str) -> list[str]: return ["chapter 85 note"]

@traced("classify", tags=["tariff"])
def classify(q: str) -> str:
    docs = retrieve(q)                                        # becomes a child of classify
    return f"8507 from {len(docs)} doc"

classify("power bank")                                        # run the pipeline

def show(parent: str | None = None, depth: int = 0) -> None:  # print the tree
    for r in RUNS:                                            # scan all runs
        if r["parent"] == parent:                             # children of this parent
            print("  " * depth + f"{r['name']} ({r['ms']}ms)")
            show(r["id"], depth + 1)                          # recurse
show()
```

## 💻 Code Example — Advanced
```python
# Real LangSmith tracing: nested @traceable, tags/metadata, token usage, errors, async
# pip install langsmith
import asyncio                                                # async runtime
from langsmith import traceable, tracing_context              # tracing helpers
from langsmith.run_helpers import get_current_run_tree        # access current run

@traceable(run_type="llm", name="fake_llm")                   # mark as LLM so UI shows tokens
async def fake_llm(prompt: str) -> dict:
    await asyncio.sleep(0.01)                                 # pretend network time
    # Returning usage_metadata lets LangSmith compute token counts and cost for custom models
    return {"choices": [{"message": {"role": "assistant", "content": "8507.60"}}],
            "usage_metadata": {"input_tokens": len(prompt.split()), "output_tokens": 3, "total_tokens": len(prompt.split()) + 3}}

@traceable(run_type="retriever", name="retrieve")
async def retrieve(q: str) -> list[dict]:
    return [{"page_content": "Chapter 85: batteries", "metadata": {"source": "hs2022.pdf"}}]

@traceable(run_type="chain", name="classify_request", tags=["tariff"])
async def classify(product: str, user_id: str) -> str:
    rt = get_current_run_tree()                               # current (root) run
    if rt:
        rt.metadata["user_id"] = user_id                      # attach searchable metadata
    docs = await retrieve(product)                            # child run
    try:
        out = await fake_llm(f"Product: {product}. Context: {docs[0]['page_content']}")  # child LLM run
        return out["choices"][0]["message"]["content"]
    except Exception as exc:                                  # exception is recorded on the run
        raise RuntimeError("classification failed") from exc

async def main() -> None:
    with tracing_context(enabled=False):                      # run offline: no data is sent
        print(await classify("power bank", "u42"))
    # with tracing_context(enabled=True): ...                 # enable for a real traced run
    # Per-call options also exist: classify(..., langsmith_extra={"tags": ["vip"], "metadata": {"ab": "B"}})

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
Trace each request, attach `user_id` and a request id, and return the trace run id in a response header so support can paste it into LangSmith.

```python
from fastapi import FastAPI, Request, Response               # framework
from langsmith import traceable                               # tracing
from langsmith.run_helpers import get_current_run_tree        # run id access

app = FastAPI()                                               # app

@traceable(name="api_request", tags=["api"])                  # root run per request
async def process(product: str) -> tuple[str, str]:
    rt = get_current_run_tree()                               # current run
    answer = await classify(product, "anon")                  # nested pipeline above
    return answer, str(rt.id) if rt else ""

@app.get("/classify")
async def route(product: str, request: Request, response: Response) -> dict[str, str]:
    answer, run_id = await process(product)                   # traced work
    response.headers["x-trace-id"] = run_id                   # support can search this id
    return {"hs_code": answer}
```

---

## 🔗 LangChain / LangGraph Connection
LCEL runnables and LangGraph nodes are traced automatically. Pass `run_name`, `tags`, and `metadata` in the `config` dict to label a run. In LangGraph, each node is a child run, so conditional edges and loops are visible in the tree.

```python
from langchain_core.runnables import RunnableLambda           # simple runnable

step = RunnableLambda(lambda x: x.upper())                    # a one-step chain
result = step.invoke("hs code", config={"run_name": "shout", "tags": ["demo"], "metadata": {"ab": "A"}})
print(result)                                                 # HS CODE (traced if env vars are set)
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Running sync code in a thread pool or `asyncio.create_task` and losing the parent link in older Python (<3.11) so runs show up as separate root traces.
✅ Correct: pass `parent` explicitly via `langsmith_extra`, or use Python 3.11+ where context is propagated, and use `asyncio.to_thread` which copies context.

```python
# Wrong (Python 3.10): run is orphaned
loop.run_in_executor(None, traced_fn, x)
# Right
await asyncio.to_thread(traced_fn, x)        # copies contextvars
```

❌ Mistake 2: Tracing everything, including tiny helpers, producing noisy trees.
✅ Correct: trace meaningful steps only.

```python
# Wrong
@traceable
def add(a, b): return a + b
# Right: no decorator on trivial helpers; decorate retriever, LLM, tools, chain
```

---

## 🧠 Tricky Interview Question
**Q**: "A streamed response shows 0 output tokens in the trace. Why, and how do you fix it?"

**Answer**: Streaming APIs return usage only if requested. With OpenAI use `stream_options={"include_usage": True}`; with `wrap_openai` or LangChain's `ChatOpenAI(stream_usage=True)` the final chunk contains token counts that LangSmith can record. Otherwise LangSmith cannot compute cost. For custom models, return or set `usage_metadata` on the run.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a trace and a span/run? (Easy)
A1: A trace is the whole request; runs (spans) are the individual steps in it, linked by parent ids.

Q2: What are tags and metadata for? (Easy)
A2: Tags are free labels, metadata are key-value pairs. Both are used to filter and group traces (e.g. `tier=pro`, `prompt_version=v3`).

Q3: What is `run_type` and why set it? (Medium)
A3: A hint like `llm`, `chain`, `tool`, `retriever`. The UI renders them differently and computes token/cost only for `llm` runs.

Q4: How do you trace a non-LangChain function and keep nesting? (Medium)
A4: Decorate with `@traceable`. Nesting works through contextvars, so decorated functions that call each other form a tree.

Q5: How would you debug an intermittent slow request from a trace? (Hard)
A5: Filter traces by latency > p95, open the waterfall, compare slow vs normal traces of the same chain. Look for large retrieved context (token count), retries (repeated child runs), cold vector DB calls, or rate-limit backoff. Add metadata such as model name and chunk count to confirm the pattern, then fix (reduce `k`, add timeouts, cache) and verify with the same filter.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Multi-step RAG, agents, tool calling
- Investigating latency, cost or wrong answers

❌ Avoid when:
- Tracing PII without masking
- Instrumenting every micro function (noise and cost)

---

## 📊 Visual Diagram
```
 classify_request  ████████████████████████████ 2.1s
 ├─ rewrite_query  ████ 0.5s   180 tok
 ├─ retrieve       ███ 0.4s    4 docs
 ├─ llm_classify   ██████████████ 1.1s  1,450 tok  $0.00031
 └─ validate_code  ▏ 3ms
 tags: [tariff, tier=pro]   metadata: {user_id: u42, prompt: v3}
```

---

## 💰 Cost Impact
- Tracing shows `prompt_tokens` and `completion_tokens` per run and total cost per trace, so you can find expensive steps. Example: 1,450 tokens at gpt-4o-mini rates (about $0.15 in / $0.60 out per 1M) is roughly $0.0003 per request, or $300 per million requests.
- Optimise: remove unused chunks, shorten system prompts, cache repeated queries, and use trace filters ("tokens > 3000") to find outliers. Sample traces to cut platform cost.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Trace | Tree of runs for a request | Request के runs का tree |
| Run / span | One step | एक step |
| Parent run | Run that called others | जिसने दूसरे runs बुलाए |
| Tag | Label to filter | Filter के लिए label |
| Metadata | Key-value info on a run | Run पर key-value जानकारी |
| run_type | llm / chain / tool / retriever | Run का प्रकार |

---

## ⚡ 3-Line Summary
English: Tracing captures every step of a request as a tree of runs with inputs, outputs, tokens, latency and errors. LangChain/LangGraph are traced automatically; other code uses `@traceable` and `wrap_openai`. Use tags and metadata so traces can be filtered by user, version or tier.
Hindi: Tracing request के हर step को runs के tree के रूप में inputs, outputs, tokens, latency और errors के साथ पकड़ती है। LangChain/LangGraph अपने-आप trace होते हैं; बाकी code में `@traceable` और `wrap_openai` इस्तेमाल करो। Tags और metadata से user, version या tier के हिसाब से traces filter करो।

---

## ➡️ Next Topic
**420. Projects in LangSmith** — organising traces by app and environment.
