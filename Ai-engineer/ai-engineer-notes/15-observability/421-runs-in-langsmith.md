---

# 421. Runs in LangSmith
# हिंदी में: LangSmith में Runs

---

## 🔵 Simple Definition (English)
A run is the basic unit of LangSmith: one execution of one step, such as an LLM call, a retriever query, a tool call or a whole chain. It has an id, name, type, inputs, outputs, start/end time, status, tags, metadata, token counts and a parent. The root run of a request is called the trace.

## 🔵 सरल परिभाषा (Hindi)
Run LangSmith की बुनियादी इकाई है: किसी एक step का एक execution, जैसे LLM call, retriever query, tool call या पूरी chain। इसमें id, name, type, inputs, outputs, start/end time, status, tags, metadata, token counts और parent होता है। Request का root run ही trace कहलाता है।

---

## 🔴 Problem it Solves
- You need data, not just screenshots: to compute "average tokens of the retriever-to-LLM step" you need structured access to runs.
- Reproducing a bug requires the exact input of the failing step.
- Building datasets from production needs a way to select specific runs (errors, slow, thumbs-down).

## 🔴 यह क्यों बना? (Hindi)
- आपको सिर्फ़ screenshots नहीं, data चाहिए: "retriever से LLM step के औसत tokens" निकालने के लिए runs का structured access चाहिए।
- Bug reproduce करने के लिए fail हुए step का exact input चाहिए।
- Production से dataset बनाने के लिए खास runs (errors, slow, thumbs-down) चुनने का तरीका चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A step starts → run created with id, parent_run_id, trace_id, start_time
Step 2 → Step ends → outputs, end_time, status (success/error) are filled
Step 3 → For llm runs: prompt_tokens, completion_tokens, total_cost computed
Step 4 → Runs stored; query via UI filters or client.list_runs(...)
Step 5 → Filter with a query language: eq(name,"llm_classify"), gt(latency,"5s")
Step 6 → Read one run: client.read_run(run_id) → inputs/outputs/error
Step 7 → Reuse: save runs as dataset examples, attach feedback, or replay in Playground
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Step शुरू → run बनता है: id, parent_run_id, trace_id, start_time
Step 2 → Step खत्म → outputs, end_time, status (success/error) भरते हैं
Step 3 → llm runs में: prompt_tokens, completion_tokens, total_cost निकलते हैं
Step 4 → Runs save; UI filters या client.list_runs(...) से query
Step 5 → Query language: eq(name,"llm_classify"), gt(latency,"5s")
Step 6 → एक run पढ़ो: client.read_run(run_id) → inputs/outputs/error
Step 7 → दोबारा इस्तेमाल: dataset example बनाओ, feedback जोड़ो या Playground में replay करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: Every night a job queries the last 24h of runs named `llm_classify` with `error = true` or latency over 8s. It finds 37 failing runs, 30 of them with `RateLimitError`. The team adds retry with backoff and lowers concurrency. The remaining 7 are schema validation failures; their inputs are saved as dataset examples for regression tests.

**Amazon-style support bot**: Runs with `run_type="tool"` and name `refund_api` are aggregated to see which tool fails most.

## 🟡 Real Example Hindi mein
**Tariff System**: हर रात एक job पिछले 24 घंटे के `llm_classify` नाम के runs query करती है जिनमें `error = true` या latency 8s से ज़्यादा है। 37 failing runs मिलते हैं, 30 में `RateLimitError`। Team retry with backoff जोड़ती है और concurrency घटाती है। बाकी 7 schema validation failures हैं; उनके inputs regression tests के लिए dataset examples में सहेजे जाते हैं।

**Amazon-style support bot**: `run_type="tool"` और नाम `refund_api` वाले runs aggregate होकर दिखाते हैं कि कौन सा tool सबसे ज़्यादा fail होता है।

---

## 💻 Code Example — Basic
```python
# Basic: a Run record + simple filtering and stats (pure Python, offline)
from dataclasses import dataclass                             # structured record
from statistics import mean                                   # average helper

@dataclass
class Run:                                                    # shape similar to LangSmith's Run
    id: str                                                   # unique id
    name: str                                                 # step name
    run_type: str                                             # llm / retriever / tool / chain
    latency_s: float                                          # duration in seconds
    total_tokens: int = 0                                     # tokens for llm runs
    error: str | None = None                                  # error text or None

RUNS: list[Run] = [                                           # sample data
    Run("1", "llm_classify", "llm", 1.2, 1450),
    Run("2", "llm_classify", "llm", 9.5, 3100),
    Run("3", "llm_classify", "llm", 0.4, 0, "RateLimitError"),
    Run("4", "retrieve", "retriever", 0.3),
]

llm_runs = [r for r in RUNS if r.run_type == "llm"]           # select only llm runs
slow = [r.id for r in llm_runs if r.latency_s > 8]            # latency filter
errors = [r.id for r in llm_runs if r.error]                  # error filter
ok = [r for r in llm_runs if not r.error]                     # successful runs
print("slow:", slow, "errors:", errors)
print("avg tokens (ok runs):", mean(r.total_tokens for r in ok))
```

## 💻 Code Example — Advanced
```python
# Query real runs with the LangSmith client: filter, aggregate, export failures to a dataset
# pip install langsmith
import asyncio                                                # run blocking SDK off the event loop
from collections import Counter                               # count error types
from datetime import datetime, timedelta, timezone            # time window
from langsmith import Client                                  # SDK client

def fetch_failures(client: Client, project: str, hours: int = 24) -> list:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)  # window start
    runs = client.list_runs(
        project_name=project,                                 # which project
        run_type="llm",                                       # only LLM steps
        start_time=since,                                     # time filter
        error=True,                                           # only failed runs
        limit=200,                                            # cap the result size
    )
    return list(runs)                                         # materialise the iterator

def summarize(runs: list) -> dict[str, int]:
    counts = Counter((r.error or "unknown").split(":")[0][:40] for r in runs)  # group by error prefix
    return dict(counts.most_common(5))                        # top 5 error kinds

def failures_to_dataset(client: Client, runs: list, dataset_name: str) -> int:
    try:
        ds = client.read_dataset(dataset_name=dataset_name)   # reuse if it exists
    except Exception:                                         # not found -> create
        ds = client.create_dataset(dataset_name=dataset_name, description="Production failures")
    inputs = [r.inputs for r in runs if r.inputs]             # skip runs with no inputs
    client.create_examples(inputs=inputs, outputs=[{} for _ in inputs], dataset_id=ds.id)  # outputs to be labelled
    return len(inputs)                                        # how many were added

async def nightly(project: str) -> None:
    try:
        client = Client()                                     # needs LANGSMITH_API_KEY
        runs = await asyncio.to_thread(fetch_failures, client, project)  # blocking call in a thread
        print("top errors:", summarize(runs))
        n = await asyncio.to_thread(failures_to_dataset, client, runs, "tariff-failures")
        print("added examples:", n)
    except Exception as exc:                                  # a monitoring job must not crash loudly
        print("nightly job failed:", type(exc).__name__)

if __name__ == "__main__":
    asyncio.run(nightly("tariff-prod"))                       # prints a message if not configured
```

---

## 🟠 FastAPI Integration
Expose a small admin endpoint that returns recent failing runs for a dashboard, using `asyncio.to_thread` because the SDK client is synchronous.

```python
import asyncio                                                # thread offload
from fastapi import FastAPI, HTTPException                    # framework
from langsmith import Client                                  # SDK

app = FastAPI()                                               # app

@app.get("/admin/failures")                                   # protect with auth in production
async def failures(project: str = "tariff-prod", hours: int = 6) -> dict:
    try:
        client = Client()                                     # create client
        runs = await asyncio.to_thread(fetch_failures, client, project, hours)
    except Exception as exc:                                  # surface a clean error
        raise HTTPException(status_code=502, detail=f"LangSmith error: {type(exc).__name__}")
    return {"count": len(runs), "top_errors": summarize(runs),
            "run_ids": [str(r.id) for r in runs[:20]]}        # first 20 ids for drill-down
```

---

## 🔗 LangChain / LangGraph Connection
Every LCEL component and LangGraph node becomes a run, with `run_type` inferred (`llm`, `prompt`, `parser`, `retriever`, `tool`, `chain`). Use `config={"run_name": ..., "tags": [...]}` to name them. Callback handlers receive `run_id` and `parent_run_id` for each step, which is the same id seen in LangSmith.

```python
from langchain_core.callbacks import BaseCallbackHandler      # callback base

class RunLogger(BaseCallbackHandler):                         # logs each LLM start
    def on_llm_start(self, serialized, prompts, *, run_id, parent_run_id=None, **kwargs):
        print("llm run", run_id, "parent", parent_run_id)     # ids match LangSmith's run ids
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling `list_runs` without limits or filters on a busy project.
✅ Correct: always filter by time, name/type, and set `limit`.

```python
# Wrong
runs = list(client.list_runs(project_name="tariff-prod"))
# Right
runs = list(client.list_runs(project_name="tariff-prod", run_type="llm", error=True, limit=200))
```

❌ Mistake 2: Assuming `run.outputs` always exists.
✅ Correct: handle `None` for errored or in-progress runs.

```python
# Wrong
text = run.outputs["answer"]
# Right
text = (run.outputs or {}).get("answer", "")
```

---

## 🧠 Tricky Interview Question
**Q**: "The root run is marked success, but the user got a wrong answer. A child run has an error. How?"

**Answer**: Errors in child runs do not automatically fail the parent. If your code catches the exception (e.g. fallback answer), the root completes successfully while the child shows an error. This is why you should search for child errors, not only root status, and add explicit metadata such as `fallback_used=true` when you degrade gracefully. Also check output validity with an evaluator, because "success" only means no exception.

---

## ⚫ Interview Questions + Answers

Q1: What is a run? (Easy)
A1: One execution of a step (LLM, retriever, tool, chain) with inputs, outputs, timing and status.

Q2: How is a run related to a trace? (Easy)
A2: A trace is the root run plus all its descendants, tied by `trace_id`.

Q3: How do you find all slow LLM calls last week? (Medium)
A3: `client.list_runs(project_name=..., run_type="llm", start_time=..., filter='gt(latency, "5s")')`, then sort or aggregate.

Q4: How can you turn bad runs into tests? (Medium)
A4: Select runs by filter (error or thumbs-down), take `run.inputs`, and call `create_examples` into a dataset; a human fills the correct `outputs`.

Q5: How would you build a cost report per feature? (Hard)
A5: Tag/metadata every root run with `feature`. Query llm runs with `total_tokens`/`total_cost`, group by root-run metadata (join via `trace_id`), and sum per day. Handle missing token data for streaming and custom models, and sample if the volume is too high. Store results in a warehouse for dashboards.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Debugging a specific failing step
- Building monitoring jobs, cost reports and datasets from real traffic

❌ Avoid when:
- Pulling millions of runs through the API (use bulk export)
- Using runs as your only source of business logs

---

## 📊 Visual Diagram
```
 Run
 ├─ id, trace_id, parent_run_id
 ├─ name: "llm_classify"   run_type: llm
 ├─ inputs:  {messages: [...]}
 ├─ outputs: {content: "8507.60"}
 ├─ start/end → latency 1.2s
 ├─ prompt_tokens 1200 | completion_tokens 250 | cost $0.00033
 ├─ status: success | error
 ├─ tags, metadata
 └─ feedback: [correctness=1]
```

---

## 💰 Cost Impact
- Runs expose `prompt_tokens`, `completion_tokens`, and `total_cost`. Example: 10,000 llm runs/day averaging 1,450 tokens is 14.5M tokens/day, about $2-4 per day on gpt-4o-mini-class pricing; on a larger model it can be 30x higher.
- Optimise: find the runs in the top 5% by tokens, shrink their prompts; remove duplicated retries (many error runs = wasted tokens); cache answers for repeated inputs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Run | One step execution | एक step का execution |
| Trace ID | Id shared by a whole request | पूरी request का साझा id |
| Parent run | The caller run | Caller run |
| run_type | Kind of step | Step का प्रकार |
| Filter query | Expression to select runs | Runs चुनने की expression |
| Latency | Time from start to end | Start से end तक समय |

---

## ⚡ 3-Line Summary
English: A run is one step execution with inputs, outputs, timing, tokens and status; the root run is the trace. Query runs with `client.list_runs` and filters to find slow, failing or costly steps. Convert bad runs into dataset examples to build regression tests.
Hindi: Run एक step का execution है जिसमें inputs, outputs, timing, tokens और status होते हैं; root run ही trace है। `client.list_runs` और filters से धीमे, fail होने वाले या महँगे steps ढूँढो। खराब runs को dataset examples बनाकर regression tests तैयार करो।

---

## ➡️ Next Topic
**422. Feedback in LangSmith** — attaching user and automated scores to runs.
