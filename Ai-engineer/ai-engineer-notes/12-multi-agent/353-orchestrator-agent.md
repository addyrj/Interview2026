---

# 353. Orchestrator Agent
# हिंदी में: Orchestrator Agent

---

## 🔵 Simple Definition (English)
An orchestrator agent takes a complex goal, breaks it into sub-tasks at run time, sends each sub-task to a worker or specialist, collects the results and synthesises one final answer. Unlike a fixed workflow, the sub-tasks are decided dynamically by the LLM. It is also called the orchestrator-worker pattern.

## 🔵 सरल परिभाषा (Hindi)
Orchestrator agent एक complex goal लेता है, run time पर उसे sub-tasks में तोड़ता है, हर sub-task worker/specialist को भेजता है, results जमा करता है और एक final answer बनाता है। Fixed workflow के उलट sub-tasks LLM dynamic रूप से तय करता है। इसे orchestrator-worker pattern भी कहते हैं।

---

## 🔴 Problem it Solves
- You do not know in advance how many sub-tasks a request needs (3 products or 30?).
- Static pipelines cannot adapt to the input.
- Someone must own the overall goal, merge outputs and handle partial failures.

## 🔴 यह क्यों बना? (Hindi)
- पहले से पता नहीं होता कि request में कितने sub-tasks होंगे (3 products या 30?)।
- Static pipelines input के हिसाब से adapt नहीं कर पातीं।
- किसी को overall goal own करना, outputs merge करना और partial failures संभालना होता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Orchestrator receives the goal
Step 2 → It decomposes the goal into a list of sub-tasks (structured JSON)
Step 3 → It dispatches sub-tasks to workers (in parallel when independent)
Step 4 → Workers return results (or errors)
Step 5 → Orchestrator checks completeness, retries failed items
Step 6 → It synthesises everything into one answer
Step 7 → Final answer + usage report returned
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Orchestrator को goal मिलता है
Step 2 → वह goal को sub-tasks की list (structured JSON) में तोड़ता है
Step 3 → Sub-tasks workers को भेजता है (independent हों तो parallel)
Step 4 → Workers results (या errors) लौटाते हैं
Step 5 → Completeness check, failed items retry
Step 6 → सबको जोड़कर एक answer बनाता है
Step 7 → Final answer + usage report वापस
```

---

## 🟡 Real World Example
**Tariff Classification System**: An importer uploads an invoice with 40 line items. The orchestrator splits it into 40 classification sub-tasks, dispatches them to classifier workers in parallel (batches of 10), retries failures, and produces one table with codes, duties and a list of low-confidence items for human review.

**Amazon**: orchestrator builds a product page by calling title, image and description workers. **Zomato**: assembling a "plan my week of meals" request.

## 🟡 Real Example Hindi mein
**Tariff System**: Importer 40 line items वाला invoice upload करता है। Orchestrator 40 classification sub-tasks बनाता है, classifier workers को 10-10 के batches में parallel भेजता है, failures retry करता है, और codes, duties और human review वाले low-confidence items की एक table बनाता है।

---

## 💻 Code Example — Basic
```python
# Orchestrator-worker with a rule-based planner (no LLM needed to run)


def plan(goal: str) -> list[str]:  # decompose: one sub-task per comma-separated item
    return [item.strip() for item in goal.split(",") if item.strip()]


def worker(item: str) -> dict[str, str]:  # classify one item (mock)
    return {"item": item, "code": "6109.10" if "shirt" in item else "8517.13"}


def synthesize(results: list[dict[str, str]]) -> str:  # merge results
    return "\n".join(f"{r['item']}: {r['code']}" for r in results)


goal = "cotton shirt, smartphone, silk shirt"  # invoice lines
subtasks = plan(goal)  # step 1: plan
results = [worker(t) for t in subtasks]  # step 2: delegate
print(synthesize(results))  # step 3: merge
```

## 💻 Code Example — Advanced
```python
# Async orchestrator: concurrency limit, retries with backoff, partial-failure report
import asyncio  # async runtime
import random  # for a flaky mock worker
from dataclasses import dataclass  # containers


@dataclass
class ItemResult:
    item: str  # input line
    code: str | None = None  # result
    error: str | None = None  # failure reason
    attempts: int = 0  # tries used


async def flaky_worker(item: str) -> str:  # mock LLM worker that sometimes fails
    await asyncio.sleep(0.01)
    if random.random() < 0.3:  # 30% failure
        raise RuntimeError("rate limit")
    return "6109.10" if "shirt" in item else "8517.13"


async def run_item(item: str, sem: asyncio.Semaphore, retries: int = 3) -> ItemResult:
    res = ItemResult(item)  # result holder
    async with sem:  # limit concurrent LLM calls
        for attempt in range(1, retries + 1):
            res.attempts = attempt
            try:
                res.code = await flaky_worker(item)  # call worker
                return res
            except RuntimeError as exc:
                res.error = str(exc)  # remember last error
                await asyncio.sleep(0.05 * 2 ** attempt)  # exponential backoff
    return res  # gave up; error is set


async def orchestrate(lines: list[str], concurrency: int = 5) -> list[ItemResult]:
    sem = asyncio.Semaphore(concurrency)  # shared limiter
    return await asyncio.gather(*(run_item(l, sem) for l in lines))


async def main() -> None:
    out = await orchestrate(["cotton shirt", "smartphone", "silk shirt"])
    ok = [r for r in out if r.code]  # successes
    bad = [r for r in out if not r.code]  # need human review
    print(f"{len(ok)} ok, {len(bad)} failed")
    for r in out:
        print(r)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🟠 FastAPI Integration
For long jobs, return a job id and let the client poll, instead of holding an HTTP request open.

```python
import uuid  # ids
from fastapi import FastAPI, BackgroundTasks, HTTPException  # framework
from pydantic import BaseModel  # models

app = FastAPI()  # app
JOBS: dict[str, dict] = {}  # job store (use Redis/DB in production)


class Invoice(BaseModel):
    lines: list[str]  # invoice lines


async def process(job_id: str, lines: list[str]) -> None:
    try:
        JOBS[job_id] = {"status": "done", "results": {l: "6109.10" for l in lines}}  # mock
    except Exception as exc:
        JOBS[job_id] = {"status": "failed", "error": str(exc)}


@app.post("/jobs", status_code=202)
async def create(inv: Invoice, bg: BackgroundTasks) -> dict:
    job_id = uuid.uuid4().hex  # new id
    JOBS[job_id] = {"status": "running"}
    bg.add_task(process, job_id, inv.lines)  # run after response
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict:
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="no such job")
    return JOBS[job_id]
```

---

## 🔗 LangChain / LangGraph Connection
LangGraph implements orchestrator-worker with the `Send` API: the orchestrator node returns a list of `Send("worker", {...})`, creating one worker run per sub-task, and results are merged with a reducer.

```python
import operator  # reducer helper
from typing import Annotated, TypedDict  # typing
from langgraph.graph import StateGraph, START, END  # graph
from langgraph.types import Send  # dynamic fan-out


class State(TypedDict):
    goal: str  # input
    results: Annotated[list[str], operator.add]  # reducer: worker outputs are concatenated


def orchestrator(s: State) -> list[Send]:  # conditional edge function
    items = [i.strip() for i in s["goal"].split(",")]  # plan
    return [Send("worker", {"item": i}) for i in items]  # one worker per item


def worker(payload: dict) -> dict:
    return {"results": [f"{payload['item']} -> classified"]}  # partial update


g = StateGraph(State)
g.add_node("worker", worker)
g.add_conditional_edges(START, orchestrator, ["worker"])
g.add_edge("worker", END)
print(g.compile().invoke({"goal": "shirt, phone", "results": []}))
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Unbounded fan-out.
✅ Correct: Limit concurrency.

```python
# Wrong: 500 parallel LLM calls -> rate limit errors
# await asyncio.gather(*(call(i) for i in items))
# Right
sem = None  # asyncio.Semaphore(5) and `async with sem:` around each call
```

❌ Mistake 2: Failing the whole job when one item fails.
✅ Correct: Collect partial results and report failures.

```python
# Wrong: results = [worker(i) for i in items]  # one exception kills all
# Right
results = []
for i in ["a", "b"]:
    try:
        results.append(("ok", i))
    except Exception as exc:
        results.append(("error", str(exc)))
```

---

## 🧠 Tricky Interview Question
**Q**: "The orchestrator's plan sometimes misses sub-tasks (35 of 40 invoice lines processed). How do you guarantee completeness?"

**Answer**: Do not trust the LLM for counting. Create sub-tasks deterministically in code when the structure is known (one per line). When the LLM must plan, validate the plan against the input (coverage check), compare the number of results with the number of expected items, reconcile by id, retry the missing ids, and fail loudly or flag for review if still missing. Give each sub-task a stable id.

---

## ⚫ Interview Questions + Answers

Q1: What is an orchestrator agent?
A1: An agent that plans sub-tasks dynamically, delegates them to workers and combines results.

Q2: Orchestrator versus supervisor?
A2: A supervisor loops and picks the next worker step by step; an orchestrator plans a set of sub-tasks up front (often parallel) and then synthesises. They are often combined.

Q3: Which LangGraph API creates a dynamic number of workers?
A3: `Send`, returned from a conditional edge, with a reducer (e.g. `operator.add`) in the state.

Q4: How do you handle partial failures?
A4: Per-item try/except, retries with backoff, return successes plus an error list, and queue failures for human review.

Q5: How do you control cost and rate limits for 1,000 sub-tasks?
A5: Concurrency semaphore, batching, cheap model for workers, caching duplicate items, Batch API for non-urgent jobs, backoff on 429, a token budget per job and progress tracking via job ids.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The number/type of sub-tasks is unknown upfront
- Sub-tasks are independent and parallelisable

❌ Avoid when:
- Steps are fixed and known (plain chain or code)
- Sub-tasks depend strictly on each other

---

## 📊 Visual Diagram
```
 Goal ─► ORCHESTRATOR ─► plan: [t1, t2, ... tn]
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
  worker1  worker2  workerN   (parallel, limited)
     └────────┼────────┘
              ▼
        collect + retry
              ▼
        synthesize ─► answer
```

---

## 💰 Cost Impact
Cost = 1 planning call + N worker calls + 1 synthesis call. Keep the planner and synthesizer small by passing ids and short results. Use gpt-4o-mini for workers, dedupe identical items, cache results, and use the OpenAI Batch API (about half price) for large offline jobs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Orchestrator | Plans and delegates | plan बनाकर बाँटने वाला |
| Worker | Does one sub-task | एक sub-task करने वाला |
| Decomposition | Splitting a goal | goal को तोड़ना |
| Fan-out / fan-in | Spread / collect | फैलाना / समेटना |
| Reducer | Merge rule for state | state merge करने का नियम |
| Send | LangGraph dynamic dispatch | dynamic dispatch API |

---

## ⚡ 3-Line Summary
English: The orchestrator plans sub-tasks at run time, sends them to workers and merges the results. It suits variable-size jobs, but needs concurrency limits, retries and completeness checks. LangGraph uses `Send` for this.
Hindi: Orchestrator run time पर sub-tasks बनाता है, workers को भेजता है और results merge करता है। यह variable-size jobs के लिए सही है, पर concurrency limits, retries और completeness checks चाहिए। LangGraph में इसके लिए `Send` है।

---

## ➡️ Next Topic
**354. Researcher + Writer Pattern** — a classic two-agent pipeline: gather facts, then write from them.
