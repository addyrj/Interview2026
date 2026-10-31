---

# 266. LangChain Async
# हिंदी में: LangChain Async (एक साथ कई calls)

---

## 🔵 Simple Definition (English)
Async in LangChain means using the `a`-prefixed methods (`ainvoke`, `astream`, `abatch`) so that waiting for the network does not block your program. While one LLM call waits for the provider, the event loop can serve other requests or start other calls. Every Runnable supports both sync and async.

## 🔵 सरल परिभाषा (Hindi)
LangChain Async का मतलब है `a` से शुरू होने वाले methods (`ainvoke`, `astream`, `abatch`) use करना, ताकि network का इंतज़ार आपके program को block न करे। एक LLM call provider का जवाब ढूँढ रही हो, तब event loop दूसरी requests serve कर सकता है। हर Runnable sync और async दोनों support करता है।

---

## 🔴 Problem it Solves
An LLM call takes 1-10 seconds, and almost all of it is waiting. With sync code inside a FastAPI `async def` route, one call **freezes the whole server** - other users wait. And processing 100 tariff descriptions one by one takes 100 x 2 s = 200 s.

Async lets 1 process handle hundreds of in-flight calls, and lets you run 100 classifications in parallel (limited by rate limits) in ~10-15 s.

## 🔴 यह क्यों बना? (Hindi)
एक LLM call 1-10 सेकंड लेती है और ज़्यादातर समय सिर्फ इंतज़ार होता है। FastAPI के `async def` route में sync call पूरे server को **freeze** कर देती है - बाकी users रुक जाते हैं। 100 tariff descriptions एक-एक करके process करो तो 100 x 2 s = 200 s लगते हैं। Async से वही काम parallel में ~10-15 s में हो जाता है (rate limit के भीतर)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Every Runnable has sync (invoke) and async (ainvoke) methods
Step 2 → Native async models (ChatOpenAI) use an async HTTP client (httpx) in ainvoke
Step 3 → `await chain.ainvoke(x)` pauses ONLY this coroutine; event loop runs others
Step 4 → `chain.abatch(list, config={"max_concurrency": N})` runs many inputs in parallel
Step 5 → asyncio.gather / TaskGroup can run different chains side by side
Step 6 → Runnables without async support (plain functions) run in a thread executor
Step 7 → Rate limits (429) are the real ceiling -> cap with max_concurrency / Semaphore
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → हर Runnable में sync (invoke) और async (ainvoke) दोनों methods होते हैं
Step 2 → ChatOpenAI जैसे native async models ainvoke में async HTTP client (httpx) लेते हैं
Step 3 → `await chain.ainvoke(x)` सिर्फ इसी coroutine को रोकता है; event loop बाकी चलाता है
Step 4 → `chain.abatch(list, config={"max_concurrency": N})` कई inputs parallel चलाता है
Step 5 → asyncio.gather / TaskGroup से अलग-अलग chains साथ-साथ चलती हैं
Step 6 → जिन Runnables में async नहीं है (plain functions) वे thread executor में चलते हैं
Step 7 → असली सीमा rate limit (429) है -> max_concurrency / Semaphore से control करो
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs broker uploads an Excel sheet with 200 product descriptions. Sync loop: 200 x 2 s = ~7 min. With `abatch(..., max_concurrency=10)`: about 200/10 x 2 s = ~40 s. Each row that fails is returned as an error object instead of killing the whole job (`return_exceptions=True`).

**Zomato-style**: For one order the app calls "dish tagging", "allergen check" and "upsell suggestion" chains at the same time using `asyncio.gather` - latency = slowest of three, not the sum. **Amazon-style**: Product page generates 5 review summaries in parallel.

## 🟡 Real Example Hindi mein
**Tariff System**: Broker 200 product descriptions वाली Excel upload करता है। Sync loop: 200 x 2 s = ~7 मिनट। `abatch(..., max_concurrency=10)` से: लगभग 40 सेकंड। जो row fail हो वह error object बनकर लौटती है, पूरा job नहीं मरता (`return_exceptions=True`)।

**Zomato-style**: एक order के लिए "dish tagging", "allergen check", "upsell" chains `asyncio.gather` से एक साथ चलती हैं - latency = सबसे धीमी वाली, तीनों का जोड़ नहीं। **Amazon-style**: Product page पर 5 review summaries parallel बनती हैं।

---

## 💻 Code Example — Basic
```python
# Basic async batch with LangChain Core -- runs OFFLINE (simulated 0.5s "LLM")
# pip install langchain-core
import asyncio                                                     # async runtime
import time                                                        # to measure speed-up
from langchain_core.runnables import RunnableLambda                # wrap any function as a Runnable

async def fake_classify(product: str) -> str:                      # pretend LLM call (async function)
    await asyncio.sleep(0.5)                                       # simulate 0.5 s network wait
    return f"{product} -> HS 8518.30"                              # canned result

def fake_classify_sync(product: str) -> str:                       # same thing but blocking
    time.sleep(0.5)                                                # blocks the thread for 0.5 s
    return f"{product} -> HS 8518.30"                              # canned result

# RunnableLambda accepts (sync_func, async_func) so both invoke and ainvoke work
chain = RunnableLambda(fake_classify_sync, afunc=fake_classify)    # sync + async implementations
products: list[str] = [f"item-{i}" for i in range(10)]             # 10 products

# --- Sequential (what NOT to do): 10 x 0.5 s ---
start = time.perf_counter()                                        # start timer
seq = [chain.invoke(p) for p in products]                          # one after another
print(f"sequential: {time.perf_counter() - start:.1f}s")           # ~5.0 s

# --- Async batch: all 10 together ---
async def main() -> None:                                          # async entry
    t0 = time.perf_counter()                                       # start timer
    out = await chain.abatch(products, config={"max_concurrency": 5})  # at most 5 at a time
    print(f"abatch(5) : {time.perf_counter() - t0:.1f}s, {len(out)} results")  # ~1.0 s
    t1 = time.perf_counter()                                       # second timer
    out2 = await asyncio.gather(*(chain.ainvoke(p) for p in products))  # gather: no cap
    print(f"gather    : {time.perf_counter() - t1:.1f}s, first={out2[0]}")     # ~0.5 s

asyncio.run(main())                                                # run it
```

## 💻 Code Example — Advanced
```python
# Production: bounded concurrency, per-item errors, timeouts, retry, ordered results
# pip install langchain-openai langchain-core
import asyncio                                                     # concurrency primitives
import logging                                                     # logging
from dataclasses import dataclass                                  # light result container

from langchain_core.output_parsers import StrOutputParser          # parse to str
from langchain_core.prompts import ChatPromptTemplate              # prompt
from langchain_openai import ChatOpenAI                            # chat model

logger = logging.getLogger("tariff.async")                         # logger

prompt = ChatPromptTemplate.from_messages(                         # prompt template
    [("system", "Return only the HS code."), ("user", "{product}")]
)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=20, timeout=20)  # fast and cheap
chain = prompt | llm | StrOutputParser()                           # LCEL chain
chain = chain.with_retry(stop_after_attempt=3, wait_exponential_jitter=True)     # retry 429/5xx with jitter


@dataclass
class RowResult:                                                   # one result per input row
    product: str                                                   # original input
    hs_code: str | None = None                                     # success value
    error: str | None = None                                       # error text if failed


async def classify_all(products: list[str], concurrency: int = 10) -> list[RowResult]:
    """Classify many products in parallel; never raise because of one bad row."""
    sem = asyncio.Semaphore(concurrency)                           # max in-flight calls

    async def one(p: str) -> RowResult:                            # worker for one row
        async with sem:                                            # wait for a free slot
            try:
                code = await asyncio.wait_for(                     # per-call deadline
                    chain.ainvoke({"product": p}), timeout=30
                )
                return RowResult(product=p, hs_code=code.strip())  # success
            except asyncio.TimeoutError:                           # too slow
                return RowResult(product=p, error="timeout")       # record, do not crash
            except Exception as exc:                               # any provider error
                logger.warning("row failed %s: %s", p, exc)        # log it
                return RowResult(product=p, error=type(exc).__name__)  # keep type only

    return await asyncio.gather(*(one(p) for p in products))       # gather keeps input order


# Equivalent LangChain-native way (returns exceptions in the list, same order):
async def classify_all_native(products: list[str]) -> list[str | BaseException]:
    return await chain.abatch(                                     # parallel batch
        [{"product": p} for p in products],                        # list of inputs
        config={"max_concurrency": 10},                            # cap parallelism
        return_exceptions=True,                                    # errors become values
    )

# Usage: results = asyncio.run(classify_all(["earbuds", "laptop", "olive oil"]))
```

---

## 🟠 FastAPI Integration
FastAPI runs `async def` routes on one event loop. So a route must `await` async LangChain calls. If you call `chain.invoke()` (blocking) inside `async def`, you block every user. If you must use a sync-only library, use a plain `def` route (FastAPI runs it in a thread pool) or `await asyncio.to_thread(...)`.

```python
# FastAPI route that classifies many products concurrently
from fastapi import FastAPI, HTTPException                         # framework + errors
from pydantic import BaseModel, Field                              # validation (pydantic v2)

app = FastAPI()                                                    # app instance

class BulkRequest(BaseModel):                                      # input schema
    products: list[str] = Field(min_length=1, max_length=200)      # limit batch size

class BulkResponse(BaseModel):                                     # output schema
    results: list[dict[str, str | None]]                           # list of result rows

@app.post("/classify/bulk", response_model=BulkResponse)           # POST route
async def classify_bulk(body: BulkRequest) -> BulkResponse:
    try:
        rows = await classify_all(body.products, concurrency=10)   # function from Advanced above
    except Exception as exc:                                       # unexpected failure
        raise HTTPException(status_code=502, detail="LLM backend error") from exc
    return BulkResponse(                                           # map dataclass -> dict
        results=[{"product": r.product, "hs_code": r.hs_code, "error": r.error} for r in rows]
    )
```

---

## 🔗 LangChain / LangGraph Connection
- **LCEL**: `RunnableParallel({"hs": hs_chain, "duty": duty_chain})` runs branches concurrently on `ainvoke` automatically.
- **Sync vs async default**: if a Runnable only defines sync code, LangChain runs it with `run_in_executor` in `ainvoke` (works, but uses threads).
- **LangGraph**: use `async def` nodes and `await graph.ainvoke(...)`. Nodes on parallel branches (fan-out) run concurrently. Use `graph.abatch`/`config={"max_concurrency": n}`.

```python
# RunnableParallel: two chains at the same time (latency = slowest, not sum)
from langchain_core.runnables import RunnableParallel              # parallel container

both = RunnableParallel(hs=chain, reason=chain)                    # same input to both branches
# result = await both.ainvoke({"product": "earbuds"})              # {"hs": "...", "reason": "..."}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside an async route
```python
# Wrong -- freezes the event loop for every user
@app.post("/x")
async def x(b: Body):
    return chain.invoke({"product": b.p})        # sync call in async def

# Right
@app.post("/x")
async def x(b: Body):
    return await chain.ainvoke({"product": b.p}) # non-blocking
```

❌ Mistake 2: Unlimited `gather` over thousands of items
```python
# Wrong -- 5000 simultaneous calls -> 429 errors, memory spike
await asyncio.gather(*(chain.ainvoke(i) for i in items))

# Right -- bounded
await chain.abatch(items, config={"max_concurrency": 10}, return_exceptions=True)
```

❌ Mistake 3: `asyncio.run()` inside an already-running loop (Jupyter, FastAPI) -> `RuntimeError`. Just `await` the coroutine.

---

## 🧠 Tricky Interview Question

**Q**: "You switched a 500-item job from a sync loop to `asyncio.gather` and it became *slower overall* with many failures. Why?"

**Answer**: Unbounded concurrency hit the provider's rate limit (RPM/TPM). 429 errors trigger retries with backoff, and all retries land at the same time (thundering herd), so total time grows and many calls finally fail. Fix: cap concurrency (`max_concurrency` or `Semaphore`), use retry with **jitter**, and size the limit from your quota (e.g. RPM 500 and 2 s per call -> about 16 concurrent). Also use `return_exceptions=True` so one failure does not cancel the others, and consider the Batch API for non-urgent bulk jobs.

---

## ⚫ Interview Questions + Answers

Q1: What are the async methods on a Runnable?
A1: `ainvoke`, `astream`, `abatch`, `astream_events`, `abatch_as_completed`. They mirror `invoke`, `stream`, `batch`.

Q2: Why is async important for FastAPI + LLM apps?
A2: LLM calls are I/O-bound (waiting). Async lets one event loop serve many requests while calls wait. A sync call in an async route blocks the loop and stalls everyone.

Q3: How do you limit parallelism in `abatch`?
A3: `config={"max_concurrency": N}` (RunnableConfig). For custom code use `asyncio.Semaphore(N)`. Base N on provider rate limits.

Q4: `gather` vs `abatch` - which one?
A4: `abatch` is simplest for the same chain over many inputs (built-in concurrency cap, `return_exceptions`). `gather` is for *different* coroutines (different chains, DB calls, tool calls) or when you need custom per-item logic.

Q5 (Hard): How do you handle cancellation correctly in async LangChain code?
A5: When the client disconnects, the task gets `CancelledError`. Do not catch it with a bare `except Exception` that swallows it (in Python 3.8+ it is `BaseException`, but custom wrappers can still hide it); always re-raise it, and use `try/finally` for cleanup (close streams, release semaphores). With `asyncio.TaskGroup` (3.11+) one failing task cancels siblings - good for all-or-nothing work, bad for bulk jobs that should tolerate failures (use `gather(return_exceptions=True)` there). Cancelling stops reading the stream, which also stops token spend for streaming calls.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Serving web requests (FastAPI/Starlette)
- Many independent LLM/tool/DB calls
- Streaming responses
- Fan-out chains (parallel branches)

❌ Avoid when:
- A quick one-off script (sync is simpler)
- CPU-bound work (tokenizing huge text, local models) - async does not help; use processes/threads
- Code that must run strictly in order and depends on the previous result (no parallelism available)

---

## 📊 Visual Diagram
```
SYNC (one worker blocked)            ASYNC (one event loop)
req1 ──[wait 2s]──► done             req1 ──┐
req2 ......waiting......[wait 2s]    req2 ──┼─► all waits overlap
req3 ..................[wait 2s]     req3 ──┘   total ≈ 2s
total = 6s

abatch(max_concurrency=3) with 9 items:
 slot1: ▓▓▓ ▓▓▓ ▓▓▓
 slot2: ▓▓▓ ▓▓▓ ▓▓▓      9 calls x 2s / 3 slots = ~6s (not 18s)
 slot3: ▓▓▓ ▓▓▓ ▓▓▓
```

---

## 💰 Cost Impact
- Async does **not change the price per token** - it changes speed and server cost (fewer instances needed).
- Higher parallelism = higher **burn rate** ($/minute) and rate-limit risk. 200 items x (300 in + 20 out) tokens on gpt-4o-mini = 60,000 in x $0.15/1M + 4,000 out x $0.60/1M = about $0.0114 total, whether sequential or parallel.
- Retries cost tokens: every failed-then-retried call after a partial response may be billed again. Use `stop_after_attempt=3`, not unlimited.
- For big non-urgent jobs use the provider Batch API (about 50% cheaper) instead of real-time parallel calls.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Async / await | Non-blocking concurrency in Python | बिना रुके काम करना |
| Event loop | Scheduler that runs coroutines | Coroutines चलाने वाला scheduler |
| ainvoke | Async version of invoke | invoke का async रूप |
| abatch | Run many inputs in parallel | कई inputs parallel चलाना |
| max_concurrency | Cap on parallel calls | एक साथ calls की सीमा |
| Semaphore | Counter-based concurrency limiter | Concurrency सीमित करने वाला lock |
| Thundering herd | Many retries at the same moment | सब retries एक साथ टकराना |

---

## ⚡ 3-Line Summary
English: Use `ainvoke`, `astream` and `abatch` so waiting on the network never blocks the server. Cap parallelism with `max_concurrency` or a Semaphore, and return errors per item. Async saves time, not tokens.
Hindi: Network wait server को block न करे इसलिए `ainvoke`, `astream`, `abatch` use करो। Parallelism `max_concurrency` या Semaphore से सीमित करो और error हर item के हिसाब से लौटाओ। Async समय बचाता है, tokens नहीं।

---

## ➡️ Next Topic
**267. LangChain Error Handling** - retries, fallbacks, timeouts and output-parsing errors, so one bad call does not break the pipeline.
