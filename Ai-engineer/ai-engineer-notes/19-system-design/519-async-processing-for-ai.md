---

# 519. Async Processing for AI
# हिंदी में: AI के लिए Async Processing

---

## 🔵 Simple Definition (English)
Async processing means your program does not sit idle while waiting for the LLM. While one request waits for the model, the same process serves other requests. It is perfect for AI because almost all time is spent waiting on the network.

## 🔵 सरल परिभाषा (Hindi)
Async processing का मतलब है कि LLM का जवाब आने तक आपका program खाली नहीं बैठता। एक request model का इंतज़ार करती है तो वही process दूसरी requests serve करता है। AI में ज़्यादातर समय network wait में जाता है, इसलिए async बहुत काम आता है।

---

## 🔴 Problem it Solves
A synchronous server handles one LLM call per thread. With 3-10 second calls, 50 threads serve only about 5-15 requests per second and the rest queue up. Thread memory is wasted on waiting. Sequential calls also add up: 3 calls of 2 seconds each take 6 seconds, while in parallel they take about 2 seconds.

## 🔴 यह क्यों बना? (Hindi)
Sync server एक thread पर एक LLM call संभालता है। 3-10 sec की calls के साथ 50 threads बस 5-15 requests/sec दे पाते हैं। 2-2 sec की 3 sequential calls = 6 sec, जबकि parallel में ~2 sec।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Request arrives; the event loop starts the handler coroutine
Step 2 → Handler hits `await llm_call()` and hands control back to the event loop
Step 3 → Event loop runs other coroutines while the network request is in flight
Step 4 → Response arrives; the loop resumes the first handler where it paused
Step 5 → Independent calls are grouped with asyncio.gather (parallel fan-out)
Step 6 → Long work goes to background tasks / queue; the client gets an early reply
Step 7 → Tokens can be streamed (SSE) so the user sees output before completion
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Request आती है; event loop handler coroutine शुरू करता है
Step 2 → `await llm_call()` पर handler control वापस event loop को देता है
Step 3 → Network request चलते समय loop दूसरी coroutines चलाता है
Step 4 → Response आने पर loop पहले handler को वहीं से resume करता है
Step 5 → Independent calls को asyncio.gather से parallel चलाते हैं
Step 6 → लंबा काम background task / queue में; client को जल्दी जवाब
Step 7 → Tokens stream (SSE) करो ताकि user को पहले से output दिखे
```

---

## 🟡 Real World Example
**Tariff Classification System**: One shipment has 3 independent checks: (1) HS code classification, (2) duty rate lookup, (3) restricted-goods screening. Sequentially: 2s + 1s + 2s = 5s. With `asyncio.gather` all three start together and finish in about 2s (the slowest). The API responds in 2s instead of 5s.

**Amazon-style**: A product page requests a review summary, a Q&A summary and a size-advice blurb in parallel, and shows each as soon as it arrives.

## 🟡 Real Example Hindi mein
**Tariff System**: एक shipment में 3 independent checks हैं: HS code, duty rate, restricted-goods screening। Sequential: 2+1+2 = 5 sec। `asyncio.gather` से तीनों साथ शुरू होकर ~2 sec में खत्म।
**Amazon-style**: Product page review summary, Q&A summary और size advice parallel मंगवाता है और जो पहले आए उसे पहले दिखाता है।

---

## 💻 Code Example — Basic
```python
# Sequential vs parallel async calls (pure Python, runs offline)
import asyncio                          # standard async library
import time                             # to measure elapsed time

async def fake_llm(name: str, seconds: float) -> str:
    """Pretend to call an LLM that takes `seconds` to answer."""
    await asyncio.sleep(seconds)        # non-blocking wait (the loop can do other work)
    return f"{name} done"               # return a fake answer

async def sequential() -> float:
    """Run three calls one after another."""
    start = time.perf_counter()         # start timer
    await fake_llm("classify", 0.2)     # wait 0.2s
    await fake_llm("duty", 0.1)         # wait 0.1s
    await fake_llm("screen", 0.2)       # wait 0.2s
    return time.perf_counter() - start  # total time

async def parallel() -> float:
    """Run the same three calls together."""
    start = time.perf_counter()         # start timer
    await asyncio.gather(               # start all three at once
        fake_llm("classify", 0.2),
        fake_llm("duty", 0.1),
        fake_llm("screen", 0.2),
    )
    return time.perf_counter() - start  # total time (about the slowest call)

async def main() -> None:
    seq = await sequential()            # measure sequential
    par = await parallel()              # measure parallel
    print(f"sequential={seq:.2f}s parallel={par:.2f}s")   # compare

asyncio.run(main())                     # start the event loop
```

## 💻 Code Example — Advanced
```python
# Production patterns: timeouts, bounded concurrency, partial failure, cancellation
import asyncio                                        # async runtime
from dataclasses import dataclass                     # result container
from typing import Awaitable, Callable                # type hints

@dataclass
class CallResult:
    """Outcome of one LLM sub-call."""
    name: str                                         # which check ran
    ok: bool                                          # did it succeed
    value: str | None = None                          # answer when ok
    error: str | None = None                          # error text when failed

async def guarded(name: str, fn: Callable[[], Awaitable[str]],
                  sem: asyncio.Semaphore, timeout: float = 10.0) -> CallResult:
    """Run one call with a concurrency slot and a timeout; never raise."""
    async with sem:                                   # limit parallel LLM calls
        try:
            value = await asyncio.wait_for(fn(), timeout=timeout)   # enforce timeout
            return CallResult(name, True, value=value)              # success
        except asyncio.TimeoutError:                  # too slow
            return CallResult(name, False, error="timeout")
        except Exception as exc:                      # any other failure
            return CallResult(name, False, error=repr(exc))

async def analyse_shipment(desc: str, llm: Callable[[str, str], Awaitable[str]]) -> dict[str, CallResult]:
    """Fan out three checks; one failure does not kill the others."""
    sem = asyncio.Semaphore(5)                        # at most 5 calls in flight
    tasks = {                                         # name -> coroutine
        "classify": guarded("classify", lambda: llm("classify", desc), sem),
        "duty":     guarded("duty",     lambda: llm("duty", desc), sem),
        "screen":   guarded("screen",   lambda: llm("screen", desc), sem),
    }
    results = await asyncio.gather(*tasks.values())   # run all (guarded never raises)
    return {r.name: r for r in results}               # index by name

async def first_good(coros: list[Awaitable[str]]) -> str:
    """Hedged request: return the first successful answer, cancel the rest."""
    pending = {asyncio.ensure_future(c) for c in coros}   # wrap as tasks
    try:
        while pending:                                # loop until something succeeds
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for d in done:                            # check finished tasks
                if d.exception() is None:             # success?
                    return d.result()                 # return first good result
        raise RuntimeError("all calls failed")        # nothing worked
    finally:
        for p in pending:                             # cancel stragglers (saves tokens)
            p.cancel()

async def demo() -> None:
    async def llm(kind: str, desc: str) -> str:       # fake model
        await asyncio.sleep(0.05)                     # latency
        if kind == "screen":                          # make one call fail
            raise RuntimeError("provider 500")
        return f"{kind}:{desc[:10]}"                  # fake answer
    out = await analyse_shipment("smart phone 128GB", llm)   # run
    print({k: (v.ok, v.value or v.error) for k, v in out.items()})   # show outcomes

if __name__ == "__main__":
    asyncio.run(demo())                               # run demo
```

---

## 🟠 FastAPI Integration
FastAPI is async-native. Use `async def` routes with an async client (`AsyncOpenAI`, `httpx.AsyncClient`). Never call blocking code (e.g. `requests`, sync SDK) inside `async def`; it freezes the event loop for every user. Use `BackgroundTasks` for short follow-ups and a real queue for long jobs. Use `StreamingResponse` for token streaming.

```python
# FastAPI: parallel fan-out, streaming, and a safe way to run blocking code
import asyncio                                           # async tools
from fastapi import FastAPI, BackgroundTasks            # framework
from fastapi.responses import StreamingResponse         # SSE style streaming
from pydantic import BaseModel                          # validation
from openai import AsyncOpenAI                          # async client

app = FastAPI()                                         # app instance
client = AsyncOpenAI()                                  # reads OPENAI_API_KEY from env

class Item(BaseModel):
    description: str                                    # product text

async def ask(system: str, text: str) -> str:
    """One async LLM call."""
    r = await client.chat.completions.create(
        model="gpt-4o-mini",                            # cheap model
        messages=[{"role": "system", "content": system}, {"role": "user", "content": text}],
        max_tokens=100,                                 # cap output tokens
    )
    return r.choices[0].message.content or ""           # text or empty string

@app.post("/analyse")
async def analyse(item: Item) -> dict[str, str]:
    """Run 2 independent calls in parallel."""
    code, duty = await asyncio.gather(
        ask("Return only the HS code.", item.description),
        ask("Return only the duty percent.", item.description),
    )
    return {"hs_code": code, "duty": duty}

@app.post("/stream")
async def stream(item: Item) -> StreamingResponse:
    """Stream tokens as they are generated."""
    async def gen():
        s = await client.chat.completions.create(
            model="gpt-4o-mini", stream=True,
            messages=[{"role": "user", "content": item.description}],
        )
        async for chunk in s:                           # each chunk has a small delta
            if chunk.choices and chunk.choices[0].delta.content:
                yield f"data: {chunk.choices[0].delta.content}\n\n"   # SSE format
    return StreamingResponse(gen(), media_type="text/event-stream")

def audit_log(msg: str) -> None:
    """Small blocking-free task run after the response."""
    print("audit:", msg)

@app.post("/log")
async def log(item: Item, bg: BackgroundTasks) -> dict[str, str]:
    bg.add_task(audit_log, item.description)            # runs after response is sent
    return {"status": "accepted"}

def heavy_cpu(text: str) -> int:
    return sum(ord(c) for c in text)                    # pretend CPU-heavy work

@app.post("/cpu")
async def cpu(item: Item) -> dict[str, int]:
    n = await asyncio.to_thread(heavy_cpu, item.description)   # move blocking work off the loop
    return {"n": n}
```

---

## 🔗 LangChain / LangGraph Connection
Every LangChain runnable has async twins: `ainvoke`, `abatch`, `astream`, `astream_events`. LangGraph runs independent branches in parallel automatically (fan-out edges execute in the same step) and supports `astream` for node-by-node updates.

```python
# LangChain async: parallel chains with RunnableParallel + streaming
from langchain_core.runnables import RunnableParallel        # run branches together
from langchain_core.prompts import ChatPromptTemplate         # prompts
from langchain_openai import ChatOpenAI                       # model

llm = ChatOpenAI(model="gpt-4o-mini")                         # cheap model
code = ChatPromptTemplate.from_template("HS code for {x}") | llm      # chain 1
duty = ChatPromptTemplate.from_template("Duty rate for {x}") | llm    # chain 2
both = RunnableParallel(code=code, duty=duty)                 # run both concurrently

async def run(x: str) -> dict:
    out = await both.ainvoke({"x": x})                        # one await, two parallel calls
    return {k: v.content for k, v in out.items()}             # extract text

async def stream_tokens(x: str) -> None:
    async for chunk in code.astream({"x": x}):                # token streaming
        print(chunk.content, end="")                          # print each piece
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Blocking call inside an async route
✅ Correct: Use the async client or `asyncio.to_thread`.

```python
# Wrong — blocks the whole event loop for every user
@app.post("/x")
async def x():
    r = requests.post(URL, json=body)      # blocking!
    return r.json()

# Right — async HTTP client
@app.post("/x")
async def x():
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(URL, json=body)
        return r.json()
```

❌ Mistake 2: Forgetting to await, or gather without limits
✅ Correct: Always `await`, and bound parallelism with a semaphore.

```python
# Wrong — coroutine never runs ("coroutine was never awaited")
result = ask("sys", "text")
# Wrong — 10,000 simultaneous calls
await asyncio.gather(*[ask("s", t) for t in texts])

# Right
result = await ask("sys", "text")
sem = asyncio.Semaphore(10)
async def lim(t):
    async with sem:
        return await ask("s", t)
await asyncio.gather(*[lim(t) for t in texts])
```

---

## 🧠 Tricky Interview Question

**Q**: "You switched to async and wrapped your code in `async def`, yet throughput did not improve. Why?"

**Answer**: `async def` alone does nothing. If the body calls blocking code (sync SDK, `requests`, `time.sleep`, heavy JSON/CPU work, a sync DB driver), the event loop is blocked and no other request can run. Async helps only when you `await` real non-blocking I/O. Fix: use async clients, `asyncio.to_thread` or a process pool for blocking/CPU work, and check with `asyncio` debug mode or loop-lag metrics. Also watch connection pool sizes and provider rate limits, which can be the real bottleneck.

---

## ⚫ Interview Questions + Answers

Q1: Why is async a good fit for LLM apps? (Easy)
A1: Work is I/O bound: most time is waiting for the provider. One event loop can overlap thousands of waits with little memory.

Q2: What does `asyncio.gather` do? (Easy)
A2: Runs several awaitables concurrently and returns their results in order. With `return_exceptions=True` one failure does not cancel the others.

Q3: Async vs threads vs multiprocessing? (Medium)
A3: Async: many I/O waits, one thread, cooperative. Threads: blocking libraries that cannot be async. Processes: CPU-bound work (parsing, embeddings on CPU) because of the GIL. Combine: async server plus process pool for CPU parts.

Q4: How do you handle a client disconnecting mid-LLM call? (Medium)
A4: Detect it (`request.is_disconnected()` or cancellation of the streaming generator) and cancel the upstream call so you stop paying for tokens. Use `try/finally` to release resources.

Q5: How would you cut p95 latency of a 3-step agent where steps 2 and 3 are independent? (Hard)
A5: Run steps 2 and 3 in parallel with `gather` (latency becomes step1 + max(step2, step3)). Add per-step timeouts, hedged requests for slow tails, streaming the first step's output, speculative execution of likely next steps, and caching. Measure per-step latency with tracing to find the true critical path.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many concurrent users or many LLM calls per request
- Independent sub-calls can run in parallel
- You need streaming responses

❌ Avoid when:
- A one-off script with a single call (plain sync is simpler)
- The work is CPU-bound (use processes)
- Your dependencies have no async version and you cannot wrap them safely

---

## 📊 Visual Diagram
```
SYNC (3 calls)                    ASYNC gather (3 calls)
t=0 ──[classify 2s]──┐            t=0 ─┬─[classify 2s]─┐
t=2 ──[duty 1s]──────┤ total 5s        ├─[duty 1s]─────┤ total 2s
t=3 ──[screen 2s]────┘                 └─[screen 2s]───┘

Event loop:  A waits... ▶ B runs ▶ C runs ▶ A resumes ▶ ...
             (one thread, many in-flight requests)
```

---

## 💰 Cost Impact
- Async does not change price per token, but fan-out can multiply tokens: 3 parallel calls with 500 input tokens each = 1,500 input tokens, versus 500 if one prompt did everything. Illustrative: at $0.15/1M input that is tiny per request, but at 1M requests/day it adds up to $225 vs $75.
- Savings: lower latency means fewer servers (one async process serves hundreds of waiting requests). Cancel abandoned calls to stop output tokens. Use `max_tokens`. Hedged requests double cost on the slow tail, so use them only for the slowest 5%.
- Provider batch endpoints are cheaper for non-urgent work (check current pricing).

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Event loop | Scheduler that runs coroutines | Coroutines चलाने वाला scheduler |
| Coroutine | Function defined with `async def` | Pause/resume होने वाला function |
| await | Pause until result is ready | नतीजे तक रुको, loop को चलने दो |
| gather | Run many awaitables together | कई कामों को साथ चलाना |
| Semaphore | Limit on concurrent tasks | Parallel tasks की सीमा |
| Streaming | Send tokens as generated | Tokens बनते ही भेजना |
| I/O bound | Time spent waiting, not computing | इंतज़ार वाला काम |

---

## ⚡ 3-Line Summary
English: AI apps mostly wait on the network, so async lets one process serve many requests at once. Use `gather` for independent calls, semaphores for limits, and streaming for fast first token. Never block the event loop.
Hindi: AI apps ज़्यादातर network का इंतज़ार करते हैं, इसलिए async से एक process कई requests संभालता है। Independent calls के लिए `gather`, limit के लिए semaphore और तेज़ first token के लिए streaming। Event loop को कभी block मत करो।

---

## ➡️ Next Topic
**520. Cost Architecture for AI** — now that calls are fast and parallel, we design the system so the bill stays under control.
