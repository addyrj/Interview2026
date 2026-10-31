---

# 331. Parallel Execution in LangGraph
# हिंदी में: LangGraph में Parallel Execution (एक साथ कई काम)

---

## 🔵 Simple Definition (English)
Parallel execution means several nodes run in the same super-step instead of one after another. You create it by adding more than one edge out of a node (fan-out) and joining them later (fan-in). For a dynamic number of branches you use `Send`, which is LangGraph's map-reduce. Because parallel nodes write to the same state keys, you need a **reducer** such as `operator.add`.

## 🔵 सरल परिभाषा (Hindi)
Parallel execution का मतलब है कि कई nodes एक के बाद एक नहीं, बल्कि एक ही super-step में साथ चलते हैं। इसे बनाने के लिए एक node से एक से ज़्यादा edges निकालते हैं (fan-out) और बाद में जोड़ते हैं (fan-in)। Branches की संख्या runtime पर तय हो तो `Send` use करते हैं, जो LangGraph का map-reduce है। Parallel nodes एक ही state keys में लिखते हैं, इसलिए `operator.add` जैसा **reducer** चाहिए।

---

## 🔴 Problem it Solves
Sequential LLM calls add up: 3 independent calls of 2 seconds each take 6 seconds in a row but only about 2 seconds in parallel. Many real tasks are independent: classify the product, check sanction lists, and look up the duty rate. Running them one by one wastes the user's time (latency), even though the total token cost is the same.

## 🔴 यह क्यों बना? (Hindi)
Sequential LLM calls जुड़ती जाती हैं: 2-2 सेकंड की 3 independent calls क्रम से 6 सेकंड लेती हैं, parallel में सिर्फ़ लगभग 2 सेकंड। असल में कई काम independent होते हैं: product classify करना, sanction list जाँचना, duty rate खोजना। इन्हें एक-एक करके चलाना user का समय (latency) बर्बाद करता है, जबकि कुल token cost वही रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define state with a reducer on shared keys: Annotated[list[str], operator.add]
Step 2 → Fan-out: add_edge(START, "a"); add_edge(START, "b")   (two edges from one node)
Step 3 → LangGraph runs a and b in the SAME super-step (async nodes truly overlap; sync nodes
         use a thread pool)
Step 4 → Each node returns a partial update; the reducer MERGES them (no overwrite conflict)
Step 5 → Fan-in: add_edge(["a", "b"], "join") -> "join" runs only after BOTH finished
Step 6 → Dynamic fan-out: a conditional edge returns [Send("worker", {...}), ...] (one per item)
Step 7 → Results of all Send workers are merged by the reducer, then the next node reads them
Step 8 → Control the load with config {"max_concurrency": N}
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Shared keys पर reducer वाला state: Annotated[list[str], operator.add]
Step 2 → Fan-out: add_edge(START, "a"); add_edge(START, "b")   (एक node से दो edges)
Step 3 → LangGraph a और b को एक ही super-step में चलाता है (async nodes सच में overlap होते हैं;
         sync nodes thread pool में चलते हैं)
Step 4 → हर node partial update देता है; reducer उन्हें MERGE करता है (overwrite conflict नहीं)
Step 5 → Fan-in: add_edge(["a", "b"], "join") -> "join" दोनों के खत्म होने के बाद ही चलता है
Step 6 → Dynamic fan-out: conditional edge [Send("worker", {...}), ...] लौटाती है (हर item के लिए एक)
Step 7 → सभी Send workers के results reducer merge करता है, फिर अगला node उन्हें पढ़ता है
Step 8 → Load control: config {"max_concurrency": N}
```

---

## 🟡 Real World Example
**Tariff Classification System**: For each shipment line the graph needs: (a) HS code from the LLM, (b) duty rate from the tariff database, (c) sanctions check on the origin country. These are independent, so fan-out to three nodes and join into a "decision" node. Latency drops from about 6 s to about 2 s. For a shipment with 40 line items, use `Send` to classify all 40 items in parallel (map), then combine them (reduce).

**Zomato-style**: To build a home screen, run "nearby restaurants", "offers", and "reorder suggestions" in parallel, then merge.

## 🟡 Real Example Hindi mein
**Tariff System**: हर shipment line के लिए graph को चाहिए: (a) LLM से HS code, (b) tariff database से duty rate, (c) origin country की sanctions check। ये independent हैं, इसलिए तीन nodes में fan-out करके "decision" node में join करते हैं। Latency लगभग 6 s से घटकर लगभग 2 s। 40 line items वाले shipment में `Send` से सभी 40 items parallel classify (map) करके फिर जोड़ते (reduce) हैं।

**Zomato-style**: Home screen बनाने के लिए "आस-पास के restaurants", "offers" और "reorder suggestions" parallel चलाकर merge करो।

---

## 💻 Code Example — Basic
```python
# Basic: fan-out to 3 checks, fan-in to a decision (offline, uses sleep instead of an LLM)
import operator                                         # operator.add merges lists
import time                                             # measure total time
from typing import Annotated, TypedDict                 # type hints

from langgraph.graph import END, START, StateGraph     # graph API


class State(TypedDict, total=False):                    # state
    product: str                                        # input
    results: Annotated[list[str], operator.add]         # REDUCER: parallel writes are concatenated
    decision: str                                       # final output


def classify(state: State) -> dict:                     # branch 1
    time.sleep(1)                                       # pretend this is a 1-second LLM call
    return {"results": ["hs=8517.13"]}                  # return partial update


def duty_lookup(state: State) -> dict:                  # branch 2
    time.sleep(1)                                       # pretend DB/API call
    return {"results": ["duty=20%"]}                    # partial update


def sanctions(state: State) -> dict:                    # branch 3
    time.sleep(1)                                       # pretend API call
    return {"results": ["sanctions=clear"]}             # partial update


def decide(state: State) -> dict:                       # join node
    return {"decision": " | ".join(sorted(state["results"]))}   # sorted: order of parallel results varies


builder = StateGraph(State)                             # create builder
for name, fn in [("classify", classify), ("duty", duty_lookup),
                 ("sanctions", sanctions), ("decide", decide)]:   # register nodes
    builder.add_node(name, fn)                          # add each node
for name in ["classify", "duty", "sanctions"]:          # FAN-OUT: three edges from START
    builder.add_edge(START, name)                       # all three start together
builder.add_edge(["classify", "duty", "sanctions"], "decide")   # FAN-IN: wait for all three
builder.add_edge("decide", END)                         # finish
app = builder.compile()                                 # compile

t0 = time.perf_counter()                                # start timer
out = app.invoke({"product": "smartphone"})             # run
print(out["decision"])                                  # duty=20% | hs=8517.13 | sanctions=clear
print(f"took {time.perf_counter() - t0:.1f}s (sequential would be ~3s)")   # ~1s because of parallelism
```

## 💻 Code Example — Advanced
```python
# Production style: map-reduce with Send, async, concurrency limit, error isolation, type hints
import asyncio                                          # async runtime
import logging                                          # logs
import operator                                         # reducer
from typing import Annotated, Any, TypedDict            # type hints

from langgraph.graph import END, START, StateGraph      # graph API
from langgraph.types import Send                        # dynamic fan-out

logger = logging.getLogger("tariff.parallel")           # logger


class LineResult(TypedDict):                            # one classified line
    item: str                                           # product text
    hs_code: str                                        # result
    ok: bool                                            # success flag


class State(TypedDict, total=False):                    # overall state
    items: list[str]                                    # shipment lines
    results: Annotated[list[LineResult], operator.add]  # merged results from all workers
    summary: str                                        # final text


class WorkerInput(TypedDict):                           # private input of each worker
    item: str                                           # the single line to classify


def fan_out(state: State) -> list[Send]:                # conditional edge returns Send objects
    return [Send("classify_line", {"item": i}) for i in state["items"]]   # one worker per item


async def classify_line(payload: WorkerInput) -> dict[str, Any]:   # runs once per Send
    item = payload["item"]                              # unpack
    try:                                                # isolate failures: one bad line must not kill all
        await asyncio.sleep(0.2)                        # placeholder for `await llm.ainvoke(...)`
        if "bad" in item:                               # simulate an LLM/tool error
            raise ValueError("model failed")            # raise inside the worker
        code = "8517.13" if "phone" in item else "8471.30"   # fake rule
        return {"results": [{"item": item, "hs_code": code, "ok": True}]}   # success record
    except Exception as exc:                            # catch per-item errors
        logger.warning("line %r failed: %s", item, exc)  # log
        return {"results": [{"item": item, "hs_code": "", "ok": False}]}   # failure record


def summarize(state: State) -> dict[str, Any]:          # reduce step
    good = [r for r in state["results"] if r["ok"]]     # successes
    bad = [r for r in state["results"] if not r["ok"]]  # failures needing a retry/human
    return {"summary": f"{len(good)} classified, {len(bad)} need review"}   # text


builder = StateGraph(State)                             # builder
builder.add_node("classify_line", classify_line)        # worker node
builder.add_node("summarize", summarize)                # reducer node
builder.add_conditional_edges(START, fan_out, ["classify_line"])   # dynamic fan-out from START
builder.add_edge("classify_line", "summarize")          # all workers feed summarize
builder.add_edge("summarize", END)                      # end
app = builder.compile()                                 # compile


async def main() -> None:                               # demo
    items = [f"phone model {i}" for i in range(20)] + ["bad item", "laptop"]   # 22 lines
    out = await app.ainvoke({"items": items},           # run
                            config={"max_concurrency": 5})   # at most 5 workers at once (rate limits!)
    print(out["summary"])                               # 21 classified, 1 need review


if __name__ == "__main__":                              # entry
    asyncio.run(main())                                 # run
```

---

## 🟠 FastAPI Integration
Use async nodes so the event loop is not blocked, and set `max_concurrency` to respect LLM rate limits (requests per minute). You can even stream branch results to the client as they finish.

```python
# FastAPI: parallel checks behind one endpoint, with streaming of finished branches
import asyncio                                                  # async sleep
import json                                                     # NDJSON lines
import operator                                                 # reducer
from typing import Annotated, TypedDict                         # type hints

from fastapi import FastAPI                                     # web framework
from fastapi.responses import StreamingResponse                 # streaming response
from langgraph.graph import END, START, StateGraph            # graph API
from pydantic import BaseModel, Field                           # models


class S(TypedDict, total=False):                                # state
    product: str                                                # input
    parts: Annotated[list[str], operator.add]                   # merged outputs


async def hs(s: S) -> dict:                                     # branch 1
    await asyncio.sleep(0.5)                                    # fake LLM
    return {"parts": ["hs=8517.13"]}


async def duty(s: S) -> dict:                                   # branch 2
    await asyncio.sleep(0.3)                                    # fake DB
    return {"parts": ["duty=20%"]}


b = StateGraph(S)                                               # graph
b.add_node("hs", hs)                                            # nodes
b.add_node("duty", duty)
b.add_edge(START, "hs")                                         # fan-out
b.add_edge(START, "duty")
b.add_edge("hs", END)                                           # both end the graph
b.add_edge("duty", END)
graph = b.compile()                                             # compile once

app = FastAPI(title="Parallel Tariff API")                      # app


class In(BaseModel):                                            # body
    product: str = Field(min_length=2, max_length=500)          # text


@app.post("/analyze")                                           # normal endpoint
async def analyze(body: In) -> dict[str, list[str]]:            # handler
    out = await graph.ainvoke({"product": body.product}, config={"max_concurrency": 4})   # run
    return {"parts": sorted(out["parts"])}                      # stable order for clients


@app.post("/analyze/stream")                                    # streaming endpoint
async def analyze_stream(body: In) -> StreamingResponse:        # handler
    async def gen():                                            # async generator of NDJSON lines
        async for chunk in graph.astream({"product": body.product}, stream_mode="updates"):
            yield json.dumps(chunk) + "\n"                      # faster branch arrives first
    return StreamingResponse(gen(), media_type="application/x-ndjson")   # stream to client
```

---

## 🔗 LangChain / LangGraph Connection
In LCEL, `RunnableParallel` (a dict of runnables) is the equivalent for chains, and `llm.abatch(inputs, config={"max_concurrency": n})` runs many prompts in parallel. LangGraph generalises this to stateful graphs: parallel branches, `Send` for map-reduce, and reducers (`operator.add`, `add_messages`) for merging. Parallel tool calls from the LLM (several `tool_calls` in one AI message) are also executed in parallel by `ToolNode`.

```python
# LCEL equivalent for simple cases
from langchain_core.runnables import RunnableLambda, RunnableParallel   # LCEL parts

chain = RunnableParallel(                                   # dict of runnables run together
    hs=RunnableLambda(lambda x: "8517.13"),                 # branch 1
    duty=RunnableLambda(lambda x: "20%"),                   # branch 2
)
print(chain.invoke("phone"))                                # {'hs': '8517.13', 'duty': '20%'}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: No reducer on a key written by parallel nodes
✅ Correct: add `Annotated[..., operator.add]` (or a custom reducer).

```python
# Wrong — two nodes write "results" in the same step
class State(TypedDict):
    results: list[str]                   # InvalidUpdateError: can receive only one value per step

# Right
class State(TypedDict):
    results: Annotated[list[str], operator.add]
```

❌ Mistake 2: Sync/blocking code in async nodes (time.sleep, requests.get)
✅ Correct: use `await asyncio.sleep`, `httpx.AsyncClient`, `llm.ainvoke`. Blocking calls freeze the event loop and kill the parallel speedup.

```python
# Wrong
async def node(s):
    requests.get(url)                    # blocks the loop

# Right
async def node(s):
    async with httpx.AsyncClient() as c:
        await c.get(url)
```

❌ Mistake 3: Unlimited fan-out to hundreds of LLM calls
✅ Correct: use `max_concurrency` plus retries to avoid HTTP 429.

```python
# Wrong: 500 items -> 500 simultaneous requests -> rate limit errors
# Right
await app.ainvoke(inp, config={"max_concurrency": 10})
```

---

## 🧠 Tricky Interview Question

**Q**: "You fan out to branches A (1 s) and B (5 s), then join. A teammate says 'A's result is ready at 1 s, so the join node should start at 1 s.' Is that right? And if A fails at 0.5 s, what happens to B?"

**Answer**: No. With `add_edge(["A","B"], "join")` the join waits for both. LangGraph also executes by super-steps: all nodes in a step must finish before the next step starts, so the join starts at about 5 s. (A separate `add_edge("A", "join")` and `add_edge("B", "join")` would trigger join after each, which is a different and usually unwanted behaviour.) If A raises, the exception fails the super-step: B is allowed to finish its work in that step, but the run raises and the join never runs. Writes of successful nodes in that step are saved in the checkpoint (when a checkpointer exists), so a retry only re-runs the failed node. To get "best effort" behaviour, catch errors inside the node and return a failure record.

---

## ⚫ Interview Questions + Answers

Q1: How do you run two nodes in parallel in LangGraph? (Easy)
A1: Add two edges from the same source node (e.g. both from START). They run in the same super-step. Join them with `add_edge([a, b], "join")`.

Q2: Why do parallel branches need a reducer? (Easy)
A2: When two nodes write the same state key in one step, LangGraph must know how to combine the values. Without a reducer it raises `InvalidUpdateError`. `operator.add` concatenates lists; `add_messages` merges chat messages.

Q3: What is `Send` and when do you use it? (Medium)
A3: `Send(node_name, payload)` creates a dynamic branch with its own private input. Use it when the number of parallel tasks is unknown until runtime (e.g. one task per line item or per document chunk). It is the map step of map-reduce.

Q4: Do sync nodes run in parallel too? (Medium)
A4: In `invoke`, sync nodes of one step run in a thread pool, so I/O-bound calls overlap, but CPU-bound Python code is limited by the GIL. In `ainvoke`, async nodes overlap on the event loop. Prefer async for I/O such as LLM and HTTP.

Q5: How do you design parallel LLM calls safely at scale? (Hard)
A5: Use `Send` for dynamic fan-out, `max_concurrency` and a rate limiter (token bucket) matching provider limits, retries with exponential backoff and jitter, per-branch error isolation (return failure records), timeouts, and a deterministic reduce (sort results). Keep branch payloads small to reduce checkpoint size. Track tokens per branch for cost. Remember parallelism reduces latency, not tokens, so combine it with caching and a small model for the map step.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tasks are independent (classification, validation, lookups)
- Processing many documents or line items (map-reduce)
- Latency matters more than the number of simultaneous requests

❌ Avoid when:
- Step B needs the output of step A (that is a sequence)
- You are close to API rate limits
- Branches write the same data and merging rules are unclear

---

## 📊 Visual Diagram
```
                 ┌──► [classify  1s] ──┐
 START ──────────┼──► [duty      1s] ──┼──► [decide] ──► END
                 └──► [sanctions 1s] ──┘
        fan-out        same super-step       fan-in (waits for all)
        total ≈ 1s, not 3s

 Dynamic (Send):  items=[i1,i2,i3,...]
 START ─► fan_out() ─► Send(worker,i1) ┐
                       Send(worker,i2) ├─► reducer (operator.add) ─► summarize
                       Send(worker,i3) ┘
```

---

## 💰 Cost Impact
Parallelism does NOT reduce tokens; it reduces waiting time. Three calls of 800 input + 150 output tokens on gpt-4o-mini cost about 3 x $0.00021 = $0.00063 either way. Risks: a burst of parallel calls can hit rate limits (429), causing retries that cost extra time (and sometimes extra tokens for repeated calls).

Optimise: use a small model for the map step and a stronger model only for the final reduce, avoid repeating the shared context in every branch (pass only the needed fields), cache identical sub-queries, and cap fan-out with `max_concurrency`. For non-urgent bulk work (nightly shipment batches) consider the provider's Batch API at about 50 percent lower price instead of live parallel calls.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fan-out | One node triggers many | एक से कई branches |
| Fan-in / join | Many branches merge into one node | कई branches का एक में मिलना |
| Super-step | One round of parallel node execution | Nodes के चलने का एक round |
| Reducer | Function to merge concurrent updates | Updates जोड़ने का function |
| Send | Dynamic branch with private input | Runtime पर बनने वाली branch |
| Map-reduce | Split work, process, combine | बाँटो, चलाओ, जोड़ो |
| max_concurrency | Limit of simultaneous tasks | एक साथ चलने वाले tasks की सीमा |

---

## ⚡ 3-Line Summary
English: Add several edges from one node to run branches in the same super-step, and join with `add_edge([a, b], "join")`. Use reducers for shared keys and `Send` for a dynamic number of branches (map-reduce). Parallel cuts latency, not token cost, so cap it with `max_concurrency`.
Hindi: एक node से कई edges जोड़ने पर branches एक ही super-step में चलती हैं, और `add_edge([a, b], "join")` से जुड़ती हैं। Shared keys के लिए reducer और branches की अनजान संख्या के लिए `Send` (map-reduce) use करो। Parallel latency घटाता है, token cost नहीं, इसलिए `max_concurrency` से सीमा रखो।

---

## ➡️ Next Topic
**332. Subgraphs** — package a group of nodes as a reusable graph and plug it into a bigger graph.
