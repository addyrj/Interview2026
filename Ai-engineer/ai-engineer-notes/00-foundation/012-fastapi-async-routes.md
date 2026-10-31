---

# 012. FastAPI Async Routes
# हिंदी में: FastAPI Async Routes

---

## 🔵 Simple Definition (English)
An async route is a handler declared with `async def`. It runs on the event loop and can `await` slow I/O (LLM calls, DB, Redis) without blocking other requests. A plain `def` route runs in a threadpool. Picking the right one, and never blocking inside `async def`, decides your server's throughput.

## 🔵 सरल परिभाषा (Hindi)
Async route `async def` से बना handler है। यह event loop पर चलता है और slow I/O (LLM calls, DB, Redis) पर `await` कर सकता है, दूसरी requests को block किए बिना। साधारण `def` route threadpool में चलता है। सही चुनाव और `async def` में कभी block न करना server की throughput तय करता है।

---

## 🔴 Problem it Solves
An LLM call takes seconds. If a worker handles one request at a time, 20 concurrent users need 20 workers. With async routes, one worker interleaves hundreds of in-flight LLM calls because most of the time is spent waiting. But a single blocking call inside `async def` stops all of them.

## 🔴 यह क्यों बना? (Hindi)
LLM call में कई second लगते हैं। अगर worker एक बार में एक request संभाले तो 20 users के लिए 20 workers चाहिए। Async routes से एक worker सैकड़ों in-flight LLM calls को बारी-बारी चलाता है क्योंकि ज़्यादातर समय इंतज़ार में जाता है। लेकिन `async def` में एक भी blocking call सबको रोक देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Uvicorn runs one event loop per worker process
Step 2 → Request arrives; for `async def` routes FastAPI schedules the coroutine on the loop
Step 3 → At `await client.chat.completions.create(...)` the coroutine is suspended
Step 4 → Loop serves other requests while the HTTP response from the LLM is pending
Step 5 → When data arrives the coroutine resumes and returns a result
Step 6 → For plain `def` routes, FastAPI runs them in a threadpool (default about 40 threads) so they do not block the loop
Step 7 → CPU-heavy or blocking-library work: `await asyncio.to_thread(...)` or a process/worker
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Uvicorn हर worker process में एक event loop चलाता है
Step 2 → Request आने पर `async def` routes को FastAPI loop पर schedule करता है
Step 3 → `await client.chat.completions.create(...)` पर coroutine suspend होता है
Step 4 → LLM का HTTP response आने तक loop दूसरी requests संभालता है
Step 5 → Data आते ही coroutine resume होकर result देता है
Step 6 → साधारण `def` routes को FastAPI threadpool (default ~40 threads) में चलाता है ताकि loop block न हो
Step 7 → CPU-heavy या blocking library का काम: `await asyncio.to_thread(...)` या process/worker
```

---

## 🟡 Real World Example
**Tariff Classification System**: One request needs three things: an embedding call to find candidate HS codes, a DB query for duty rates and an LLM call to decide. The embedding and DB calls are independent, so the route runs them concurrently with `asyncio.gather`, and then calls the LLM. Latency drops from 1.5 s to 1.0 s. A PDF text extractor (CPU/blocking) is wrapped in `to_thread` so other users are not frozen.

**Zomato AI**: A search route fetches menu results, user history and promotions in parallel, then asks the LLM to rank them.

## 🟡 Real Example Hindi mein
**Tariff System**: एक request को तीन चीज़ें चाहिए: candidate HS codes के लिए embedding call, duty rates के लिए DB query, और फैसले के लिए LLM call। Embedding और DB independent हैं, इसलिए route उन्हें `asyncio.gather` से साथ चलाता है, फिर LLM call करता है। Latency 1.5 s से 1.0 s। PDF text extractor (CPU/blocking) `to_thread` में लपेटा जाता है ताकि दूसरे users न रुकें।

**Zomato AI**: Search route menu results, user history और promotions parallel में लाता है, फिर LLM से rank करवाता है।

---

## 💻 Code Example — Basic
```python
# Basic: async route vs sync route - needs fastapi + httpx
import asyncio  # async sleep
import time  # blocking sleep and timing

from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # tests

app = FastAPI()  # app


@app.get("/async-ok")  # good async route
async def async_ok() -> dict[str, str]:  # runs on the event loop
    await asyncio.sleep(0.2)  # non-blocking wait, simulates LLM call
    return {"mode": "async"}  # response


@app.get("/sync-ok")  # plain def route
def sync_ok() -> dict[str, str]:  # FastAPI runs this in a threadpool
    time.sleep(0.2)  # blocking is fine here because it is in a thread
    return {"mode": "sync-thread"}  # response


@app.get("/bad")  # anti-pattern
async def bad() -> dict[str, str]:  # async def...
    time.sleep(0.2)  # ...with blocking call: freezes the loop for everyone
    return {"mode": "blocked-loop"}  # response


client = TestClient(app)  # client
print(client.get("/async-ok").json())  # {'mode': 'async'}
print(client.get("/sync-ok").json())  # {'mode': 'sync-thread'}
print(client.get("/bad").json())  # works, but would hurt concurrency under load
```

## 💻 Code Example — Advanced
```python
# Production async route: concurrent I/O with gather, timeout, semaphore, to_thread, error handling
import asyncio  # async tools
import time  # timing
from typing import Annotated  # typing

from fastapi import Depends, FastAPI, HTTPException, Request  # tools
from fastapi.testclient import TestClient  # tests
from pydantic import BaseModel, Field  # models


class In(BaseModel):  # input
    description: str = Field(min_length=3, max_length=2000)  # bounded input


async def embed(text: str) -> list[float]:  # mock embedding call
    await asyncio.sleep(0.3)  # network time
    return [0.1, 0.2]  # fake vector


async def fetch_duties(chapter: str) -> dict[str, str]:  # mock DB query
    await asyncio.sleep(0.3)  # DB time
    return {"duty": "0%"}  # fake row


async def llm_decide(text: str, duty: dict[str, str]) -> str:  # mock LLM call
    await asyncio.sleep(0.4)  # model time
    return "8517.13"  # fake code


def extract_text_blocking(raw: bytes) -> str:  # blocking, CPU-ish function (e.g. PDF parse)
    time.sleep(0.2)  # pretend heavy work
    return raw.decode()  # fake text


def get_sem(request: Request) -> asyncio.Semaphore:  # dependency: shared concurrency limiter
    return request.app.state.sem  # one semaphore for all requests


app = FastAPI()  # app
app.state.sem = asyncio.Semaphore(20)  # at most 20 concurrent LLM calls per worker


@app.post("/classify")  # route
async def classify(body: In, sem: Annotated[asyncio.Semaphore, Depends(get_sem)]) -> dict:  # async handler
    start = time.perf_counter()  # measure
    try:  # protect external calls
        # independent I/O runs together: total ~0.3s, not 0.6s
        vector, duty = await asyncio.gather(embed(body.description), fetch_duties("85"))  # concurrent
        async with sem:  # limit parallel LLM calls (protect rate limit)
            code = await asyncio.wait_for(llm_decide(body.description, duty), timeout=2.0)  # per-call timeout
    except asyncio.TimeoutError:  # LLM too slow
        raise HTTPException(status_code=504, detail="LLM timeout")  # gateway timeout
    except ConnectionError as exc:  # provider issue
        raise HTTPException(status_code=502, detail=str(exc))  # bad gateway
    return {"hs_code": code, "ms": round((time.perf_counter() - start) * 1000)}  # include latency


@app.post("/upload-text")  # route with blocking work
async def upload_text(request: Request) -> dict[str, int]:  # async handler
    raw = await request.body()  # read upload without blocking
    text = await asyncio.to_thread(extract_text_blocking, raw)  # run blocking code in a thread
    return {"chars": len(text)}  # result


if __name__ == "__main__":  # demo
    c = TestClient(app)  # client
    print(c.post("/classify", json={"description": "Android phone"}).json())  # ms around 700, not 1000
    print(c.post("/upload-text", content=b"hello pdf").json())  # {'chars': 9}
```

---

## 🟠 FastAPI Integration
Run with `uvicorn app:app --workers N` (or Gunicorn with Uvicorn workers). One worker = one event loop, so scale CPU with workers and I/O concurrency with async. Use async clients everywhere (`AsyncOpenAI`, `httpx.AsyncClient`, `asyncpg`, `redis.asyncio`) and create them once at startup.

```python
# Shared async clients created once with lifespan
from contextlib import asynccontextmanager  # lifespan helper
from typing import AsyncIterator  # type

import httpx  # async HTTP client
from fastapi import FastAPI, Request  # tools


@asynccontextmanager  # startup/shutdown
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # hook
    app.state.http = httpx.AsyncClient(timeout=10)  # one pooled client
    yield  # serve requests
    await app.state.http.aclose()  # clean shutdown


app = FastAPI(lifespan=lifespan)  # app


@app.get("/ping-upstream")  # route
async def ping(request: Request) -> dict[str, int]:  # handler
    r = await request.app.state.http.get("https://example.com")  # reuse pooled connection
    return {"status": r.status_code}  # result
```

---

## 🔗 LangChain / LangGraph Connection
Use `ainvoke`, `astream`, `abatch` inside `async def` routes. Calling `invoke` (sync) inside an async route blocks the loop. LangGraph compiled graphs also have `ainvoke`/`astream`; nodes can be `async def` so parallel branches run concurrently.

```python
# Async chain call with bounded batch concurrency (needs API key)
from fastapi import FastAPI  # framework
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model

app = FastAPI()  # app
chain = ChatPromptTemplate.from_template("HS code for {item}") | ChatOpenAI(model="gpt-4o-mini")  # chain


@app.post("/batch")  # route
async def batch(items: list[str]) -> list[str]:  # many items
    msgs = await chain.abatch([{"item": i} for i in items], config={"max_concurrency": 5})  # async batch
    return [str(m.content) for m in msgs]  # answers
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sync LLM client inside `async def`
✅ Correct: async client, or plain `def`.

```python
# Wrong: blocks the event loop for the whole LLM call
@app.post("/ask")
async def ask(q: str):
    return client.chat.completions.create(...)   # sync OpenAI()
# Right
@app.post("/ask")
async def ask(q: str):
    return await async_client.chat.completions.create(...)   # AsyncOpenAI()
```

❌ Mistake 2: Awaiting independent calls one by one
✅ Correct: use `gather` for independent work.

```python
# Wrong: 0.3 + 0.3 = 0.6 s
a = await embed(text)
b = await fetch_duties("85")
# Right: about 0.3 s
a, b = await asyncio.gather(embed(text), fetch_duties("85"))
```

❌ Mistake 3: No limit on concurrency or timeout. One slow provider call can hold resources forever. Use `wait_for` and a semaphore.

---

## 🧠 Tricky Interview Question

**Q**: "You switched all routes to `async def` for speed, but under load the API got slower and `/health` times out. What is likely wrong?"

**Answer**: Some `async def` routes call blocking code (sync SDK, `requests`, a CPU-heavy parser, `time.sleep`). That blocks the single event loop thread, so every other request, including `/health`, waits. Before, plain `def` routes ran in a threadpool and hid the problem. Find blockers (enable asyncio debug mode or loop-lag monitoring), switch to async libraries, wrap unavoidable blocking calls in `asyncio.to_thread`, move CPU work to processes or workers, and run several Uvicorn workers.

---

## ⚫ Interview Questions + Answers

Q1: When should a FastAPI route be `async def`? (Easy)
A1: When it awaits non-blocking I/O such as an async LLM client, async DB driver, or async HTTP client.

Q2: What happens with a plain `def` route? (Easy)
A2: FastAPI runs it in a threadpool, so blocking code does not freeze the event loop, but you are limited by the number of threads.

Q3: How do you run two independent awaits at once? (Medium)
A3: `await asyncio.gather(a(), b())`, or `asyncio.TaskGroup` in Python 3.11+, which cancels siblings if one fails. Use `return_exceptions=True` with gather if you want partial results.

Q4: How do you handle a blocking library in an async route? (Medium)
A4: `await asyncio.to_thread(func, *args)` (uses the default thread pool). For CPU-bound work, use `ProcessPoolExecutor` or a task queue, because threads still share the GIL.

Q5: How do you protect an async API from overload when an LLM provider slows down? (Hard)
A5: Use timeouts on every outbound call, a semaphore (bulkhead) to cap in-flight calls, a bounded queue or load shedding (return 503 when queue is full), a circuit breaker, and backpressure to clients with `Retry-After`. Without limits, slow responses pile up as pending coroutines, memory grows and latency explodes (all requests become slow, not just a few). Monitor loop lag and in-flight request count.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The route mostly waits on network I/O (LLM, DB, cache)
- You expect many concurrent users per worker
- You stream responses

❌ Avoid when:
- The route is CPU-heavy (use workers/processes)
- You only have blocking libraries and no time to wrap them (use plain `def`)
- Mixing sync DB sessions into `async def` without `to_thread`

---

## 📊 Visual Diagram
```
 Event loop (1 thread)
 ──────────────────────────────────────────────────────────►
  req A: [parse]──await LLM...............──[resume][respond]
  req B:    [parse]──await embed...──[resume]──await LLM...──[respond]
  req C:       [parse]──await DB..──[resume][respond]
  (while A waits, loop runs B and C)

  BAD: req A: [parse]──time.sleep(2)═════════ everything else frozen ═══
```

---

## 💰 Cost Impact
Async does not reduce tokens, but it cuts infrastructure cost: one small worker serves many concurrent LLM calls, so you need fewer servers. Concurrency also raises the speed at which you hit provider rate limits, so cap it. Cancelled or timed-out requests may still be billed for tokens already generated, so set `max_tokens` and handle client disconnects. Example: handling 200 concurrent 3-second LLM calls takes about 1 async worker versus 200 blocking threads/workers; saving servers matters more than tokens here.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| async def | Coroutine function | coroutine function |
| Event loop | Scheduler for coroutines | coroutines का scheduler |
| Blocking call | Stops the loop while waiting | loop को रोकने वाली call |
| Threadpool | Threads for sync routes | sync routes के threads |
| to_thread | Run blocking code in a thread | blocking code thread में |
| gather | Run awaits concurrently | awaits साथ चलाना |
| Semaphore | Cap on concurrent work | concurrent काम की सीमा |
| Backpressure | Slow or reject when overloaded | overload पर धीमा/reject |

---

## ⚡ 3-Line Summary
English: Use `async def` with async clients for I/O-bound AI routes and `gather` for independent calls. Never block the event loop; use `to_thread` or workers for blocking and CPU work. Add timeouts and semaphores to stay safe under load.
Hindi: I/O-bound AI routes के लिए async clients के साथ `async def` लो और independent calls के लिए `gather`। Event loop को कभी block मत करो; blocking और CPU काम के लिए `to_thread` या workers लो। Load में सुरक्षित रहने के लिए timeouts और semaphores लगाओ।

---

## ➡️ Next Topic
**013. FastAPI Streaming Responses** — async routes make streaming possible: we send LLM tokens to the user as they are generated.
