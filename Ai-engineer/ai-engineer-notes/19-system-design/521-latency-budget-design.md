---

# 521. Latency Budget Design
# हिंदी में: Latency Budget Design

---

## 🔵 Simple Definition (English)
A latency budget is a total time allowed for a request (for example 3 seconds), divided among each step: retrieval, reranking, LLM, post-processing. Each step gets a time slice and a timeout. If a step is over budget, you cut work, run in parallel, or degrade gracefully.

## 🔵 सरल परिभाषा (Hindi)
Latency budget पूरी request के लिए allowed कुल समय है (जैसे 3 sec), जो हर step में बँटा होता है: retrieval, reranking, LLM, post-processing। हर step को time slice और timeout मिलता है। Budget से ऊपर जाए तो काम कम करो, parallel चलाओ या gracefully degrade करो।

---

## 🔴 Problem it Solves
AI pipelines chain many slow steps. Each looks fine alone (200ms + 300ms + 2s + 400ms) but p95 totals explode, because tail latencies add up and one slow dependency can hang the user. Without a budget nobody owns the number, and the product feels slow.

## 🔴 यह क्यों बना? (Hindi)
AI pipeline में कई slow steps जुड़ते हैं। अकेले हर step ठीक दिखता है (200ms + 300ms + 2s + 400ms), पर p95 में tail latency जुड़कर बहुत बढ़ जाती है और एक slow dependency user को hang कर देती है। Budget के बिना कोई number का owner नहीं होता।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define the user target (e.g. p95 first token under 1.5s, full answer under 5s)
Step 2 → Map the pipeline and measure each step's p50/p95 with tracing
Step 3 → Allocate a budget per step (sums to less than the target, keep 10-20% slack)
Step 4 → Enforce per-step timeouts and a total deadline passed down the call chain
Step 5 → Cut the critical path: parallelise independent steps, cache, use smaller models
Step 6 → Perceived speed: stream tokens, show progress, send partial results early
Step 7 → On budget overrun: degrade (skip rerank, fewer chunks, cached answer, fallback model)
Step 8 → Alert on budget breaches; review the slowest step every week
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → User target तय करो (जैसे p95 first token 1.5s, full answer 5s)
Step 2 → Pipeline map करो, हर step का p50/p95 tracing से नापो
Step 3 → हर step को budget दो (कुल target से कम, 10-20% slack)
Step 4 → Per-step timeout और पूरी chain में total deadline लागू करो
Step 5 → Critical path घटाओ: parallel, cache, छोटा model
Step 6 → Perceived speed: tokens stream करो, progress दिखाओ
Step 7 → Overrun पर degrade: rerank skip, कम chunks, cached answer, fallback model
Step 8 → Breach पर alert; हर हफ्ते सबसे slow step सुधारो
```

---

## 🟡 Real World Example
**Tariff Classification System** (interactive search, 4s target): embedding 80ms, vector search 120ms, rerank 250ms, LLM 2.2s, validation 50ms = 2.7s typical, leaving 1.3s slack for p95 spikes. If the vector DB is slow and 600ms are used, the system skips the reranker so the total deadline still holds.

**Zomato-style**: A voice assistant for ordering needs under 1.2s to first audio, so it streams the LLM into text-to-speech sentence by sentence.

## 🟡 Real Example Hindi mein
**Tariff System** (interactive search, 4 sec target): embedding 80ms, vector search 120ms, rerank 250ms, LLM 2.2s, validation 50ms = 2.7s, बाकी 1.3s slack। Vector DB slow हो और 600ms लगे तो reranker skip हो जाता है ताकि total deadline बचे।
**Zomato-style**: Voice assistant को first audio 1.2s में चाहिए, इसलिए LLM output को sentence-by-sentence TTS में stream करते हैं।

---

## 💻 Code Example — Basic
```python
# Latency budget tracker (pure Python, runs offline)
import time                                   # clock for timing steps
from contextlib import contextmanager         # to build a timing context manager
from typing import Iterator                   # type hint for generator

# Budget in milliseconds per step (sum = 2600 of a 3000 ms total target)
BUDGET_MS: dict[str, int] = {"embed": 100, "search": 200, "rerank": 300, "llm": 1800, "validate": 200}
TOTAL_MS = 3000                               # overall target
timings: dict[str, float] = {}                # measured ms per step

@contextmanager
def step(name: str) -> Iterator[None]:
    """Measure how long a block takes and store it."""
    start = time.perf_counter()               # start the clock
    try:
        yield                                 # run the step body
    finally:
        timings[name] = (time.perf_counter() - start) * 1000   # save elapsed ms

with step("embed"):    time.sleep(0.05)       # fake 50 ms
with step("search"):   time.sleep(0.25)       # fake 250 ms (over budget!)
with step("rerank"):   time.sleep(0.10)       # fake 100 ms
with step("llm"):      time.sleep(0.30)       # fake 300 ms
with step("validate"): time.sleep(0.01)       # fake 10 ms

for name, ms in timings.items():              # report each step
    flag = "OVER" if ms > BUDGET_MS[name] else "ok"   # compare to budget
    print(f"{name:9s} {ms:7.1f} ms / {BUDGET_MS[name]} ms  {flag}")
print(f"total {sum(timings.values()):.0f} ms / {TOTAL_MS} ms")   # overall
```

## 💻 Code Example — Advanced
```python
# Deadline propagation + graceful degradation (async, type hints, error handling)
import asyncio                                            # async runtime
import time                                               # monotonic clock
from dataclasses import dataclass, field                  # request context

@dataclass
class Deadline:
    """Absolute deadline shared by every step in a request."""
    total_s: float                                        # total seconds allowed
    start: float = field(default_factory=time.monotonic)  # creation time

    def remaining(self) -> float:
        """Seconds left (never negative)."""
        return max(0.0, self.total_s - (time.monotonic() - self.start))

async def with_budget(coro, step_budget_s: float, dl: Deadline, fallback=None):
    """Run a step within min(step budget, remaining deadline); return fallback on timeout."""
    limit = min(step_budget_s, dl.remaining())            # whichever is smaller
    if limit <= 0:                                        # no time left at all
        return fallback                                   # skip the step
    try:
        return await asyncio.wait_for(coro, timeout=limit)   # enforce the limit
    except asyncio.TimeoutError:                          # step too slow
        return fallback                                   # degrade instead of failing

async def pipeline(query: str, deadline_s: float = 3.0) -> dict[str, object]:
    """Retrieval -> optional rerank -> LLM, all inside one deadline."""
    dl = Deadline(deadline_s)                             # start the clock
    degraded: list[str] = []                              # which steps we skipped

    async def search() -> list[str]:                      # fake vector search
        await asyncio.sleep(0.15)
        return ["chunk-a", "chunk-b", "chunk-c"]

    async def rerank(chunks: list[str]) -> list[str]:     # fake slow reranker
        await asyncio.sleep(0.8)
        return list(reversed(chunks))

    async def llm(chunks: list[str]) -> str:              # fake LLM
        await asyncio.sleep(0.5)
        return f"answer from {len(chunks)} chunks"

    chunks = await with_budget(search(), 0.3, dl, fallback=[])   # retrieval budget 300 ms
    if not chunks:                                        # no context found
        degraded.append("search")
    reranked = await with_budget(rerank(chunks), 0.4, dl, fallback=None)   # rerank budget 400 ms
    if reranked is None:                                  # reranker timed out
        degraded.append("rerank")                         # note the degradation
        reranked = chunks[:2]                             # use top-2 raw chunks instead
    answer = await with_budget(llm(reranked), 1.5, dl, fallback="Please retry: system busy")
    return {"answer": answer, "degraded": degraded, "left_s": round(dl.remaining(), 2)}

if __name__ == "__main__":
    print(asyncio.run(pipeline("HS code for smartphone")))   # run and print
```

---

## 🟠 FastAPI Integration
Add a middleware that records total latency and emits a `Server-Timing` header; pass a `Deadline` into each service call; use streaming for perceived speed. Return partial or degraded results with a flag rather than a 504 where it is safe.

```python
# FastAPI: timing middleware + deadline-aware route
import time                                                   # timing
from fastapi import FastAPI, Request                          # framework
from pydantic import BaseModel                                # validation

app = FastAPI()                                               # app

@app.middleware("http")
async def timing(request: Request, call_next):
    """Measure total request time and expose it."""
    start = time.perf_counter()                               # start clock
    response = await call_next(request)                       # run the route
    ms = (time.perf_counter() - start) * 1000                 # elapsed ms
    response.headers["Server-Timing"] = f"total;dur={ms:.0f}" # standard header
    return response

class Q(BaseModel):
    query: str                                                # user query

@app.post("/search")
async def search(q: Q) -> dict[str, object]:
    """Answer within 3 seconds, degrading if needed."""
    return await pipeline(q.query, deadline_s=3.0)            # pipeline from the code above
```

---

## 🔗 LangChain / LangGraph Connection
Set per-model `timeout` and `max_retries` on `ChatOpenAI`. Use `RunnableParallel` for independent branches and `astream` / `astream_events` for token streaming. In LangGraph, parallel branches run in the same superstep; put slow optional nodes (rerank, tools) behind conditional edges that check remaining time stored in state. LangSmith traces show per-node latency for finding the critical path.

```python
# LangChain: timeouts, retries and parallel retrieval + parallel prompt prep
from langchain_openai import ChatOpenAI                       # model wrapper
from langchain_core.runnables import RunnableParallel, RunnableLambda   # parallel blocks

llm = ChatOpenAI(model="gpt-4o-mini", timeout=5, max_retries=1)   # hard limit per call

parallel = RunnableParallel(                                  # both run concurrently
    docs=RunnableLambda(lambda q: ["doc1", "doc2"]),          # stand-in for retriever
    rules=RunnableLambda(lambda q: "static tariff rules"),    # stand-in for another lookup
)
# chain = parallel | prompt | llm ; use chain.astream(...) to show tokens early
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Budgeting with averages
✅ Correct: Budget with p95/p99; averages hide the tail users feel.

```python
# Wrong
if avg_latency < 2.0: print("fine")

# Right
import statistics
p95 = statistics.quantiles(samples, n=20)[18]   # 95th percentile
if p95 < 2.0: print("fine")
```

❌ Mistake 2: Sequential calls and no timeouts
✅ Correct: Parallelise independent steps and set timeouts at every hop.

```python
# Wrong — one slow dependency hangs forever, steps run one by one
a = await get_a(); b = await get_b()

# Right
a, b = await asyncio.gather(
    asyncio.wait_for(get_a(), 0.5),
    asyncio.wait_for(get_b(), 0.5),
)
```

---

## 🧠 Tricky Interview Question

**Q**: "Each of your 5 pipeline steps has p95 of 400ms. Is the p95 of the whole pipeline 2 seconds?"

**Answer**: No, it is usually worse than the sum of p50s but not simply 5 x p95. Tail events are independent: the chance at least one step hits its p95 tail on a given request is 1 - 0.95^5, about 23%. So the total p95 is roughly the sum of medians plus a tail contribution from whichever step spikes. The practical lesson: tails compound (the "tail at scale" effect), so use per-step timeouts, hedged requests, caching and graceful degradation, and measure end-to-end p95 directly instead of adding step numbers.

---

## ⚫ Interview Questions + Answers

Q1: What is TTFT? (Easy)
A1: Time To First Token: how long until the first streamed token appears. It drives perceived speed; total generation time matters less for chat UX.

Q2: Why does stream-first improve UX? (Easy)
A2: Users see progress at once. A 6-second answer that starts at 0.5s feels much faster than a 4-second blank wait followed by full text.

Q3: Which LLM factors drive latency? (Medium)
A3: Model size, input length (prefill time), output length (decode time is per token), provider load, region distance, and structured output or tool loops. Cut output tokens first since decoding is sequential.

Q4: How do you reduce RAG latency? (Medium)
A4: Parallelise embedding and metadata lookups, use ANN indexes, cache embeddings and answers, retrieve fewer chunks, limit rerank candidates, use a fast reranker or skip it under load, and use a smaller model for generation.

Q5: Design the latency budget for a 4-step agent with a 10s limit. (Hard)
A5: Pass a single deadline through all steps. Allocate e.g. planner 1.5s, tools 3s (parallel), synthesis 3s, slack 2.5s. Each step gets timeout = min(slice, remaining). Limit loop iterations, stream intermediate progress, cache tool results, and define degraded modes (return best partial answer when time runs out). Trace per step and alert on p95 breaches.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- User-facing, interactive features (chat, search, voice)
- Multi-step pipelines or agents with many hops
- An SLA or SLO exists

❌ Avoid when:
- Offline batch jobs where throughput and cost matter more than speed
- Very early prototypes (measure first, then budget)

---

## 📊 Visual Diagram
```
Target: 4000 ms total (p95)
|embed|search|rerank|        LLM (stream)        |valid| slack |
| 100 | 200  | 300  |          2200              | 200 | 1000  |
  ▲      ▲      ▲               ▲                  ▲
 timeout timeout timeout     timeout           timeout
 Deadline = start + 4000ms is passed to every step.
 Overrun? ──▶ skip rerank / fewer chunks / fallback model / cached answer
```

---

## 💰 Cost Impact
- Latency fixes often reduce cost too: fewer output tokens, smaller prompts, and cache hits are both faster and cheaper. Illustrative: trimming output from 400 to 150 tokens at $0.60/1M output saves $0.00015 per call, or $150 per million calls, and cuts decode time by more than half.
- Costs added by latency tactics: hedged (duplicate) requests, speculative calls and parallel fan-out use extra tokens; keep them for the slow tail only. Premium or provisioned throughput tiers cost more (check provider pricing).
- Token usage: input tokens drive prefill time, so shorter prompts help both speed and bill.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Latency budget | Time allowed per step | हर step को मिला समय |
| p95 / p99 | Latency that 95% / 99% requests beat | 95% / 99% requests का worst समय |
| TTFT | Time to first token | पहला token आने का समय |
| Deadline propagation | Pass remaining time down the chain | बचा हुआ समय आगे भेजना |
| Critical path | Longest dependent chain | सबसे लंबी dependent chain |
| Hedged request | Duplicate request to cut tail | Tail घटाने को duplicate request |
| Graceful degradation | Reduce quality, keep working | Quality घटाकर चालू रहना |

---

## ⚡ 3-Line Summary
English: A latency budget splits the total time target into per-step slices with timeouts and one shared deadline. Use p95, parallelise, stream, and degrade gracefully instead of failing. Output tokens and the LLM step usually dominate, so cut them first.
Hindi: Latency budget कुल target को per-step slices, timeouts और एक shared deadline में बाँटता है। p95 नापो, parallel चलाओ, stream करो और fail होने की जगह gracefully degrade करो। LLM step और output tokens सबसे ज़्यादा समय लेते हैं, इन्हें पहले घटाओ।

---

## ➡️ Next Topic
**522. Reliability in AI Systems** — speed means little if the system fails; next we cover retries, timeouts, circuit breakers and SLOs.
