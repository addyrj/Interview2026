---

# 028. OpenAI API — Sync vs Async Client
# हिंदी में: OpenAI API — Sync बनाम Async Client

---

## 🔵 Simple Definition (English)
The `openai` package gives two clients. `OpenAI` is synchronous: your code waits (blocks) until the response arrives. `AsyncOpenAI` is asynchronous: you `await` the call, and while waiting, Python can run other tasks. LLM calls take seconds, so async lets one process serve many users at once.

## 🔵 सरल परिभाषा (Hindi)
`openai` package दो clients देता है। `OpenAI` synchronous है: response आने तक आपका code रुका रहता है (block)। `AsyncOpenAI` asynchronous है: आप call को `await` करते हैं, और इंतज़ार के दौरान Python दूसरे tasks चला सकता है। LLM calls में कई seconds लगते हैं, इसलिए async से एक process कई users को एक साथ serve कर सकता है।

---

## 🔴 Problem it Solves
A normal LLM call is network-bound: 95 percent of the time is spent waiting. With a sync client inside an async web server, one slow call freezes the whole event loop, and all other users wait. Async removes that waiting cost and enables parallel calls such as classifying 50 products at the same time.

## 🔴 यह क्यों बना? (Hindi)
सामान्य LLM call network-bound है: 95 प्रतिशत समय बस इंतज़ार में जाता है। Async web server के अंदर sync client रखो तो एक धीमी call पूरा event loop freeze कर देती है और बाकी सब users इंतज़ार करते हैं। Async से यह waiting cost हटती है और parallel calls संभव होती हैं, जैसे 50 products एक साथ classify करना।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Sync: client.create() sends request, thread sleeps until reply
Step 2 → Async: await client.create() sends request, then yields control
Step 3 → Event loop runs other coroutines while the network waits
Step 4 → When the reply arrives, the coroutine resumes after the await
Step 5 → asyncio.gather() starts many coroutines together
Step 6 → Semaphore limits how many run at once (protect rate limits)
Step 7 → Results return in input order; exceptions can be captured per task
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Sync: client.create() request भेजता है, reply तक thread सोता है
Step 2 → Async: await client.create() request भेजकर control छोड़ देता है
Step 3 → Network के इंतज़ार में event loop दूसरी coroutines चलाता है
Step 4 → Reply आने पर coroutine await के बाद से आगे चलती है
Step 5 → asyncio.gather() कई coroutines एक साथ शुरू करता है
Step 6 → Semaphore एक समय में चलने वाली calls limit करता है (rate limit बचाने के लिए)
Step 7 → Results input के क्रम में आते हैं; exceptions हर task के हिसाब से पकड़ सकते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs broker uploads a CSV of 200 products. 
- Sync loop: 200 calls x 2 s = about 400 s.
- Async with concurrency 10: about 40 s.
Inside the FastAPI server, an async endpoint lets other brokers keep using the API during this time.

**Zomato AI**: At dinner peak, thousands of chat requests arrive. The async client lets each worker overlap waits instead of handling one user at a time.

## 🟡 Real Example Hindi mein
**Tariff Classification System**: Customs broker 200 products की CSV upload करता है।
- Sync loop: 200 calls x 2 s = लगभग 400 s।
- Async, concurrency 10 के साथ: लगभग 40 s।
FastAPI server के अंदर async endpoint से इस दौरान बाकी brokers भी API चला पाते हैं।

**Zomato AI**: Dinner peak पर हज़ारों chat requests आते हैं। Async client से हर worker waits को overlap करता है, एक-एक user के पीछे नहीं अटकता।

---

## 💻 Code Example — Basic
```python
# Sync vs async timing demo WITHOUT an API key: we fake the network wait with sleep
import asyncio                                   # async tools
import time                                      # timing

def fake_llm_sync(item: str) -> str:
    time.sleep(0.5)                              # pretend network wait (blocks)
    return f"HS for {item}"                      # fake answer

async def fake_llm_async(item: str) -> str:
    await asyncio.sleep(0.5)                     # pretend network wait (does not block)
    return f"HS for {item}"                      # fake answer

items = [f"product-{i}" for i in range(6)]      # six products

t0 = time.perf_counter()                         # start timer
sync_results = [fake_llm_sync(i) for i in items]   # one after another
print(f"sync : {time.perf_counter() - t0:.2f}s")   # about 3.0s

async def run_async() -> list[str]:
    return await asyncio.gather(*(fake_llm_async(i) for i in items))   # all together

t0 = time.perf_counter()                         # restart timer
async_results = asyncio.run(run_async())         # run the event loop
print(f"async: {time.perf_counter() - t0:.2f}s")   # about 0.5s

# Real client usage looks the same:
# from openai import OpenAI, AsyncOpenAI
# OpenAI().chat.completions.create(...)                    # sync
# await AsyncOpenAI().chat.completions.create(...)         # async
```

## 💻 Code Example — Advanced
```python
# Production: bounded-concurrency batch classification with per-item error capture
import asyncio                                           # async tools
import logging                                           # logs
from typing import Dict, List, Union                     # type hints

from openai import APIError, AsyncOpenAI, OpenAI         # clients + base error

logger = logging.getLogger(__name__)                     # logger
aclient = AsyncOpenAI(timeout=30.0, max_retries=3)       # one shared async client
sclient = OpenAI(timeout=30.0, max_retries=3)            # sync client for scripts


async def classify_one(product: str, sem: asyncio.Semaphore) -> Dict[str, str]:
    async with sem:                                      # wait for a free slot
        try:
            r = await aclient.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"HS code (digits only): {product}"}],
                temperature=0,
                max_tokens=20,
            )
            return {"product": product, "hs": (r.choices[0].message.content or "").strip()}
        except APIError as exc:                          # capture, do not crash the batch
            logger.error("failed %s: %s", product, exc)
            return {"product": product, "error": type(exc).__name__}


async def classify_many(products: List[str], concurrency: int = 10) -> List[Dict[str, str]]:
    sem = asyncio.Semaphore(concurrency)                 # cap parallel calls
    tasks = [classify_one(p, sem) for p in products]     # build coroutines
    return await asyncio.gather(*tasks)                  # run all, keep order


def classify_sync(product: str) -> str:
    # Use only in scripts, notebooks, or normal def endpoints
    r = sclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"HS code (digits only): {product}"}],
        max_tokens=20,
    )
    return r.choices[0].message.content or ""


if __name__ == "__main__":
    out = asyncio.run(classify_many(["cotton t-shirt", "power bank", "steel bottle"], 2))
    print(out)
```

---

## 🟠 FastAPI Integration
Rule: `async def` endpoint means use `AsyncOpenAI` with `await`. A plain `def` endpoint runs in a thread pool, where the sync client is acceptable.

```python
from typing import List                          # type hints
import asyncio                                   # semaphore
from fastapi import FastAPI                      # framework
from pydantic import BaseModel                   # models
from openai import AsyncOpenAI, OpenAI           # both clients

app = FastAPI()                                  # app
aclient = AsyncOpenAI()                          # shared async client
sclient = OpenAI()                               # shared sync client
SEM = asyncio.Semaphore(8)                       # global concurrency guard


class Batch(BaseModel):
    products: List[str]                          # many products


async def one(p: str) -> str:
    async with SEM:                              # limit concurrent upstream calls
        r = await aclient.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"HS code digits only: {p}"}],
            max_tokens=20)
        return r.choices[0].message.content or ""


@app.post("/classify-batch")
async def classify_batch(b: Batch) -> dict:       # async endpoint
    codes = await asyncio.gather(*(one(p) for p in b.products))
    return dict(zip(b.products, codes))


@app.post("/classify-sync")
def classify_sync(p: str) -> dict:                # plain def: FastAPI runs it in a thread
    r = sclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"HS code digits only: {p}"}],
        max_tokens=20)
    return {"hs": r.choices[0].message.content}
```

---

## 🔗 LangChain / LangGraph Connection
Every LangChain Runnable has sync (`invoke`, `stream`, `batch`) and async (`ainvoke`, `astream`, `abatch`) methods. LangGraph compiled graphs support `ainvoke` and `astream` too.

```python
import asyncio
from langchain_openai import ChatOpenAI                 # wrapper

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)    # one model object

async def main() -> None:
    # abatch runs many inputs concurrently; max_concurrency protects rate limits
    prompts = ["HS code: cotton t-shirt", "HS code: power bank"]
    results = await llm.abatch(prompts, config={"max_concurrency": 5})
    for r in results:
        print(r.content)

# asyncio.run(main())     # needs OPENAI_API_KEY
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using the sync client inside `async def`
✅ Correct: Use `AsyncOpenAI` and `await`.

```python
# Wrong — blocks the event loop; all users freeze during the call
@app.post("/x")
async def x():
    return client.chat.completions.create(...)   # sync client
# Right
@app.post("/x")
async def x2():
    return await aclient.chat.completions.create(...)
```

❌ Mistake 2: Unbounded `gather` over thousands of items
✅ Correct: Use a `Semaphore`, or you will hit 429 rate limits and memory spikes.

❌ Mistake 3: Calling `asyncio.run()` inside a running loop (Jupyter, FastAPI)
✅ Correct: Inside a loop use `await`. In Jupyter, use top-level `await`.

---

## 🧠 Tricky Interview Question

**Q**: "You switched to AsyncOpenAI and use gather over 1,000 products, yet throughput got worse and you see many 429 errors. Why?"

**Answer**: Async removes client-side waiting, not provider limits. Launching 1,000 simultaneous requests blows through requests-per-minute and tokens-per-minute limits. The SDK retries 429s, which adds more load. Use a semaphore (for example 10-20), a token-aware limiter, and backoff with jitter; or send big offline jobs through the Batch API. Concurrency should be tuned to the account's limits, not maximised.

---

## ⚫ Interview Questions + Answers

Q1: [Easy] Why prefer AsyncOpenAI in FastAPI?
A1: It does not block the event loop, so the server handles many requests while LLM calls wait on the network.

Q2: [Easy] Do both clients return the same objects?
A2: Yes. Only the call style differs (`await` or not).

Q3: [Medium] How do you limit parallel calls?
A3: `asyncio.Semaphore(n)` around each call, or `max_concurrency` in LangChain's config.

Q4: [Medium] How do you avoid one failure killing a whole `gather`?
A4: Catch exceptions inside each task and return an error record, or use `gather(..., return_exceptions=True)`.

Q5: [Hard] A sync library you must use is blocking your async server. What do you do?
A5: Run it in a worker thread with `asyncio.to_thread` or `run_in_executor`, or declare the endpoint as plain `def` so FastAPI uses its thread pool; for CPU-heavy work use a process pool or a separate worker service.

---

## 🔷 When to Use + When Not to Use
✅ Use async when:
- Web servers (FastAPI), many concurrent users
- Batch jobs with many independent calls
- Streaming responses to clients

❌ Use sync when:
- Simple scripts, notebooks, one-off tools
- Code paths that are already in plain `def` and low traffic

---

## 📊 Visual Diagram
```
SYNC (6 calls x 0.5s)                 ASYNC (6 calls, gathered)
|--call1--|--call2--|--call3--| ...    |--call1--|
                                       |--call2--|
total = 3.0 s                          |--call3--|   all overlap
                                       |--call4--|
                                       |--call5--|
                                       |--call6--|
                                       total = ~0.5 s

Semaphore(2): at most 2 boxes open at a time  ->  safe for rate limits
```

---

## 💰 Cost Impact
- Async does not reduce price per token; it reduces wall-clock time and server cost (fewer workers needed).
- Faster parallelism can raise your token-per-minute burn, which may trigger 429s and wasted retries. Cap concurrency.
- Optimise: tune concurrency to rate limits, avoid duplicate calls with caching, and use Batch API (about 50 percent cheaper, 24-hour window) for non-urgent bulk jobs.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Blocking | Code waits and does nothing else | Code रुककर इंतज़ार करता है |
| Event loop | Scheduler for coroutines | Coroutines का scheduler |
| Coroutine | Function defined with async def | async def वाला function |
| gather | Run many coroutines together | कई coroutines एक साथ चलाना |
| Semaphore | Limits parallel tasks | Parallel tasks की limit |
| Concurrency | Many tasks in progress | कई tasks एक साथ progress में |

---

## ⚡ 3-Line Summary
English: Use `AsyncOpenAI` with `await` in async servers so slow LLM calls do not block other users. Combine `asyncio.gather` with a semaphore for fast but rate-limit-safe batches. Sync is fine for scripts and plain `def` endpoints.
Hindi: Async servers में `AsyncOpenAI` और `await` use करो ताकि धीमी LLM calls बाकी users को block न करें। `asyncio.gather` और semaphore मिलाकर तेज़ और rate-limit-safe batches चलाओ। Scripts और plain `def` endpoints में sync ठीक है।

---

## ➡️ Next Topic
**029. OpenAI API — Streaming** — send tokens to the user as they are generated for a faster-feeling UI.
