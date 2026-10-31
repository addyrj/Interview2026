---

# 001. Python async/await — Complete Guide
# हिंदी में: Python async/await — पूरी Guide

---

## 🔵 Simple Definition (English)
`async`/`await` lets one Python thread run many waiting jobs at the same time. While one job waits for the network (like an LLM API call), the event loop runs another job. An `async def` function returns a coroutine; `await` pauses it until the result is ready.

## 🔵 सरल परिभाषा (Hindi)
`async`/`await` से एक ही Python thread कई waiting jobs एक साथ चला सकता है। जब एक job network (जैसे LLM API call) का इंतज़ार करती है, तब event loop दूसरी job चला देता है। `async def` function एक coroutine return करता है; `await` उसे result आने तक pause करता है।

---

## 🔴 Problem it Solves
An LLM call takes 1-5 seconds, and almost all of that time is waiting on the network. With normal blocking code, 100 users means 100 calls one after another (about 300 seconds), or 100 threads (heavy memory). Async lets one process handle hundreds of waiting calls cheaply, so your FastAPI server stays fast.

## 🔴 यह क्यों बना? (Hindi)
एक LLM call में 1-5 second लगते हैं और ज़्यादातर समय network का इंतज़ार होता है। Blocking code में 100 users = 100 calls एक के बाद एक (~300 second) या 100 threads (ज़्यादा memory)। Async से एक process सैकड़ों waiting calls सस्ते में संभालता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → You define `async def fetch(...)` — calling it returns a coroutine object (nothing runs yet)
Step 2 → `asyncio.run(main())` starts the event loop
Step 3 → Loop runs a coroutine until it hits `await` on slow I/O
Step 4 → Coroutine is paused, loop switches to another ready coroutine
Step 5 → When the I/O finishes, loop resumes the paused coroutine
Step 6 → `asyncio.gather(...)` runs many coroutines concurrently and collects results
Step 7 → Token note: concurrency does NOT reduce tokens; it reduces wall-clock time
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → `async def` से coroutine बनता है (call करने पर अभी कुछ run नहीं होता)
Step 2 → `asyncio.run(main())` event loop शुरू करता है
Step 3 → Loop coroutine चलाता है जब तक वह slow I/O पर `await` न करे
Step 4 → Coroutine pause होता है, loop दूसरा ready coroutine चलाता है
Step 5 → I/O पूरा होते ही loop paused coroutine को resume करता है
Step 6 → `asyncio.gather(...)` कई coroutines को साथ चलाकर results देता है
Step 7 → Tokens कम नहीं होते; सिर्फ़ कुल समय कम होता है
```

---

## 🟡 Real World Example
**Tariff Classification System**: A customs officer uploads 20 product descriptions. Each needs one LLM call (about 2 seconds). Sequential: 40 seconds. With `asyncio.gather` and a semaphore of 5: about 8 seconds. Same tokens, same cost, 5x faster.

**Zomato AI**: For one search, the app calls an LLM to understand the query, a vector DB for dishes, and a rating service at the same time, then merges the answers.

## 🟡 Real Example Hindi mein
**Tariff System**: Officer 20 product descriptions upload करता है। हर एक के लिए 1 LLM call (~2 second)। एक-एक करके: 40 second। `asyncio.gather` + semaphore(5) से: ~8 second। Tokens और cost वही, speed 5 गुना।

**Zomato AI**: एक search में LLM, vector DB और rating service तीनों एक साथ call होते हैं, फिर results merge होते हैं।

---

## 💻 Code Example — Basic
```python
# Basic asyncio example - pure Python, runs directly
import asyncio  # standard library for async programming
import time  # to measure elapsed time


async def classify(product: str) -> str:  # coroutine function: returns a str when awaited
    await asyncio.sleep(1)  # simulate a 1-second LLM network wait without blocking the loop
    return f"{product} -> HS 8517"  # fake classification result


async def main() -> None:  # entry coroutine
    start = time.perf_counter()  # record start time
    products = ["phone", "laptop", "router"]  # three products to classify
    results = await asyncio.gather(*(classify(p) for p in products))  # run all 3 concurrently
    for line in results:  # loop over results (order is preserved)
        print(line)  # print each result
    print(f"Elapsed: {time.perf_counter() - start:.1f}s")  # about 1.0s, not 3.0s


if __name__ == "__main__":  # run only when executed as a script
    asyncio.run(main())  # create loop, run main, close loop
```

## 💻 Code Example — Advanced
```python
# Production style: bounded concurrency + timeout + retry + error isolation
import asyncio  # async primitives
import random  # to simulate flaky API
from dataclasses import dataclass  # simple result container
from typing import Optional  # for optional fields


@dataclass
class Result:  # result of one classification
    product: str  # input product
    code: Optional[str]  # HS code or None when failed
    error: Optional[str]  # error message when failed


async def fake_llm(product: str) -> str:  # stand-in for a real async LLM call
    await asyncio.sleep(random.uniform(0.1, 0.4))  # simulate latency
    if random.random() < 0.2:  # 20 percent chance of failure
        raise ConnectionError("upstream 503")  # simulate transient error
    return "8517.13"  # fake HS code


async def classify_one(product: str, sem: asyncio.Semaphore, retries: int = 3) -> Result:
    async with sem:  # limit concurrent calls (protects rate limit)
        for attempt in range(1, retries + 1):  # retry loop
            try:  # guard the call
                code = await asyncio.wait_for(fake_llm(product), timeout=2.0)  # timeout per call
                return Result(product, code, None)  # success
            except (ConnectionError, asyncio.TimeoutError) as exc:  # only retry transient errors
                if attempt == retries:  # out of retries
                    return Result(product, None, str(exc) or "timeout")  # return failure, do not crash batch
                await asyncio.sleep(0.2 * 2 ** attempt)  # exponential backoff (non-blocking)
    return Result(product, None, "unreachable")  # defensive default for type checker


async def classify_many(products: list[str], limit: int = 5) -> list[Result]:
    sem = asyncio.Semaphore(limit)  # shared semaphore for the batch
    tasks = [classify_one(p, sem) for p in products]  # build coroutines
    return await asyncio.gather(*tasks)  # gather; each task already handles its own errors


async def main() -> None:  # demo runner
    results = await classify_many([f"item-{i}" for i in range(10)])  # run 10 items
    ok = sum(1 for r in results if r.code)  # count successes
    print(f"{ok}/{len(results)} classified")  # summary line


if __name__ == "__main__":  # script entry
    asyncio.run(main())  # start event loop
```

---

## 🟠 FastAPI Integration
FastAPI runs on an event loop. An `async def` route runs directly on that loop, so every `await` inside lets other requests progress. Never call blocking code (`time.sleep`, `requests.get`) inside `async def` routes; it freezes all users.

```python
# FastAPI + async: batch classify endpoint
import asyncio  # async tools
from fastapi import FastAPI, HTTPException  # web framework
from pydantic import BaseModel, Field  # request validation

app = FastAPI()  # create app


class BatchRequest(BaseModel):  # request body
    products: list[str] = Field(min_length=1, max_length=50)  # 1 to 50 products


async def call_llm(text: str) -> str:  # placeholder async LLM call
    await asyncio.sleep(0.1)  # simulate network
    return f"HS-code-for:{text}"  # fake answer


@app.post("/classify-batch")  # POST route
async def classify_batch(req: BatchRequest) -> dict[str, list[str]]:  # async handler
    try:  # error handling
        codes = await asyncio.gather(*(call_llm(p) for p in req.products))  # concurrent calls
    except Exception as exc:  # unexpected failure
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")  # tell client upstream failed
    return {"codes": list(codes)}  # JSON response
```

---

## 🔗 LangChain / LangGraph Connection
Every LangChain Runnable has async twins: `ainvoke`, `abatch`, `astream`. `abatch` runs many inputs concurrently (control with `max_concurrency` in config). LangGraph nodes can be `async def`, and `graph.ainvoke` runs them without blocking the server.

```python
# LangChain async batch (needs langchain-openai and OPENAI_API_KEY)
import asyncio  # run loop
from langchain_openai import ChatOpenAI  # chat model
from langchain_core.prompts import ChatPromptTemplate  # prompt template


async def main() -> None:  # async entry
    prompt = ChatPromptTemplate.from_template("HS code for: {item}")  # simple prompt
    chain = prompt | ChatOpenAI(model="gpt-4o-mini")  # LCEL chain
    inputs = [{"item": "phone"}, {"item": "laptop"}]  # two inputs
    out = await chain.abatch(inputs, config={"max_concurrency": 5})  # concurrent, capped at 5
    print([m.content for m in out])  # print answers


asyncio.run(main())  # run it
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting `await` (you get a coroutine object, not a result)
✅ Correct: always `await` coroutines.

```python
# Wrong: result is a coroutine object, and Python warns "never awaited"
result = classify("phone")
# Right: await it inside an async function
result = await classify("phone")
```

❌ Mistake 2: Blocking call inside async code
✅ Correct: use async libraries or `asyncio.to_thread`.

```python
# Wrong: freezes the whole event loop for 2 seconds
import time
time.sleep(2)
# Right: non-blocking sleep, or push blocking work to a thread
await asyncio.sleep(2)
data = await asyncio.to_thread(blocking_pdf_parse, "file.pdf")
```

❌ Mistake 3: Unlimited `gather` on 10,000 items (rate-limit errors, memory spike).
✅ Correct: use `asyncio.Semaphore` as shown in the Advanced example.

---

## 🧠 Tricky Interview Question

**Q**: "You changed 50 sequential LLM calls to `asyncio.gather`. Latency is still 50x one call. Why?"

**Answer**: The calls are probably using a blocking client (sync `OpenAI()` or `requests`) inside `async def`, so each call blocks the loop and nothing overlaps. Fix: use `AsyncOpenAI` and `await`, or wrap the sync call in `asyncio.to_thread`. Also check if a lock or semaphore of size 1 is serialising the calls. Async only helps when the awaited work is truly non-blocking.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between a coroutine and a task? (Easy)
A1: A coroutine is the object returned by calling an `async def` function; it does nothing until awaited. A Task wraps a coroutine and schedules it on the event loop right away (`asyncio.create_task`), so it runs concurrently.

Q2: When is async useful and when is it not? (Easy)
A2: Useful for I/O-bound work (network, DB, files via async libs). Not useful for CPU-bound work (embedding math, PDF parsing) because one thread still does the computing. For CPU work use processes (`ProcessPoolExecutor`) or a worker queue.

Q3: What does `asyncio.gather` do on an exception? (Medium)
A3: By default the first exception propagates to the caller, while other tasks keep running (they are not cancelled). With `return_exceptions=True`, exceptions come back as values in the result list, so you can handle each one. For batch jobs, prefer handling errors inside each task as in our Advanced example.

Q4: How do you limit concurrency to respect OpenAI rate limits? (Medium)
A4: Use `asyncio.Semaphore(n)` around each call, or `max_concurrency` in LangChain config. Add retry with exponential backoff on 429 errors. Rate limits are in requests-per-minute and tokens-per-minute, so also budget tokens.

Q5: How would you run a CPU-heavy PDF parse inside an async FastAPI app? (Hard)
A5: `asyncio.to_thread` moves it to a thread, which frees the loop but the GIL still limits pure-Python CPU work. Libraries that release the GIL (C extensions) benefit. For real CPU work use `loop.run_in_executor` with a `ProcessPoolExecutor`, or push the job to Celery/ARQ and return a job id. Choose by job length: under 1 second thread, longer use a queue.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Calling LLM APIs, vector DBs, Redis, Postgres (all network I/O)
- Serving many concurrent users from one FastAPI process
- Streaming tokens to clients

❌ Avoid when:
- The work is CPU-bound (use processes or workers)
- A small one-off script that makes one call (sync is simpler)
- You depend on a library that has no async support and you cannot wrap it safely

---

## 📊 Visual Diagram
```
Sequential (blocking)            Async (event loop)
 call A ████████                  call A ████████
 call B         ████████          call B ████████
 call C                 ████████  call C ████████
 total = 3 x 2s = 6s              total = ~2s

Event loop:
  [A await] -> switch -> [B await] -> switch -> [C await]
       ^ I/O done: A resumes   ^ I/O done: B resumes
```

---

## 💰 Cost Impact
Async does not change token count, so the per-request cost stays the same. It cuts latency and server cost: one small server handles many users instead of many threads. Risk: unlimited concurrency can burst past rate limits and cause 429 retries (wasted calls). Optimise with a semaphore, backoff, caching repeated queries, and `max_tokens`. Example: 1,000 items x 700 tokens on gpt-4o-mini is about 0.7M tokens, roughly $0.2 whether sequential or async; async finishes in minutes instead of an hour.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coroutine | Object made by `async def` call | async function का object |
| Event loop | Scheduler that runs coroutines | coroutines का scheduler |
| await | Pause until result is ready | result तक रुको |
| Task | Scheduled coroutine | scheduled coroutine |
| gather | Run many coroutines together | कई coroutines साथ चलाना |
| Semaphore | Limits concurrent work | concurrency की सीमा |
| I/O-bound | Mostly waiting on network | ज़्यादातर इंतज़ार वाला काम |

---

## ⚡ 3-Line Summary
English: `async`/`await` lets one thread serve many waiting LLM calls. Use `gather` with a semaphore, timeouts and retries; never block the loop. It saves time, not tokens.
Hindi: `async`/`await` से एक thread कई waiting LLM calls संभालता है। `gather` के साथ semaphore, timeout और retry लगाओ; loop को कभी block मत करो। इससे समय बचता है, tokens नहीं।

---

## ➡️ Next Topic
**002. Python Decorators for AI Apps** — retry, timing and caching wrappers are built with decorators, and they must work with async functions you just learned.
