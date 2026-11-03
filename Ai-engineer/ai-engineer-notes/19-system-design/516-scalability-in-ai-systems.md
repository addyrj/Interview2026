---

# 516. Scalability in AI Systems
# हिंदी में: AI Systems में Scalability

---

## 🔵 Simple Definition (English)
Scalability is the ability to handle more users, data and tokens without breaking latency or cost targets. AI systems scale differently from normal web apps: the bottlenecks are model rate limits (requests and tokens per minute), slow long-running calls, GPU capacity and vector index size.

## 🔵 सरल परिभाषा (Hindi)
Scalability का मतलब है ज़्यादा users, data और tokens को latency और cost targets तोड़े बिना संभालना। AI systems normal web apps से अलग scale होते हैं: bottleneck होते हैं model rate limits (requests और tokens प्रति मिनट), धीमी लंबी calls, GPU capacity और vector index का आकार।

---

## 🔴 Problem it Solves
A demo that works for 5 users fails at 5,000: provider returns 429 rate-limit errors, requests pile up while each waits 8 seconds for a model, memory fills up, and a spike creates a huge bill.

## 🔴 यह क्यों बना? (Hindi)
5 users पर चलने वाला demo 5,000 पर फेल होता है: provider 429 rate-limit errors देता है, हर request 8 सेकंड model का इंतज़ार करती है तो ढेर लग जाता है, memory भर जाती है, और spike से बड़ा bill बनता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Find the bottleneck with load tests (LLM rate limit? DB? CPU? network?)
Step 2 → Keep the API stateless -> add replicas horizontally
Step 3 → Use async I/O so one worker holds thousands of waiting calls
Step 4 → Protect providers: concurrency limits (semaphore), rate limiter, retry with backoff + jitter
Step 5 → Move slow/heavy work to queues + workers (ingestion, batch jobs, long agents)
Step 6 → Scale data layer: shard/replicate vector DB, read replicas, caching
Step 7 → Add backpressure: queue limits, 429/503 with Retry-After, load shedding, graceful degradation
Step 8 → Autoscale on the right signal (queue depth, in-flight requests), not just CPU
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Load test से bottleneck खोजो (LLM rate limit? DB? CPU?)
Step 2 → API stateless रखो → replicas बढ़ाओ
Step 3 → Async I/O से एक worker हज़ारों waiting calls संभाले
Step 4 → Provider की सुरक्षा: semaphore, rate limiter, backoff + jitter के साथ retry
Step 5 → भारी काम queues + workers में (ingestion, batch jobs, लंबे agents)
Step 6 → Data layer scale: shard/replicate vector DB, read replicas, caching
Step 7 → Backpressure: queue limit, 429/503, load shedding, graceful degradation
Step 8 → सही signal (queue depth, in-flight requests) पर autoscale
```

---

## 🟡 Real World Example
**Tariff Classification System**: Month-end, customs brokers upload 20,000 invoices within an hour. Real-time classification stays on the fast path with a concurrency cap; bulk uploads go to a queue where workers process at a pace under the provider's tokens-per-minute limit. Users get a job id and poll or receive a webhook. If the provider slows down, low-confidence cases wait in the queue instead of failing.
**Zomato-style example**: Dinner-time spike for support chat: queue non-urgent tickets, keep chat low latency.

## 🟡 Real Example Hindi mein
**Tariff System**: Month-end पर customs brokers एक घंटे में 20,000 invoices upload करते हैं। Real-time classification fast path पर concurrency cap के साथ रहता है; bulk uploads queue में जाते हैं जहाँ workers provider की tokens-per-minute limit के नीचे चलते हैं। Users को job id मिलता है, वे poll करते हैं या webhook पाते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: bounded concurrency with a semaphore so we never exceed a provider limit (offline demo)
import asyncio  # async runtime
import time  # timing


async def fake_llm(i: int) -> str:  # stand-in for a model call
    await asyncio.sleep(0.1)  # 100 ms latency
    return f"done-{i}"  # result


async def main() -> None:  # driver
    sem = asyncio.Semaphore(5)  # at most 5 calls in flight

    async def limited(i: int) -> str:  # wrapper that respects the limit
        async with sem:  # wait for a slot
            return await fake_llm(i)  # call

    t0 = time.perf_counter()  # start
    results = await asyncio.gather(*(limited(i) for i in range(20)))  # 20 tasks
    print(len(results), "results in", round(time.perf_counter() - t0, 2), "s")  # about 0.4 s (4 waves)


asyncio.run(main())  # run
```

## 💻 Code Example — Advanced
```python
# Advanced: token-bucket rate limiter + queue workers + retry with jitter + load shedding (offline)
import asyncio  # async runtime
import random  # jitter
import time  # clock


class TokenBucket:  # limits tokens per second (models rate-limit by tokens per minute)
    def __init__(self, rate_per_sec: float, capacity: float) -> None:  # configure
        self.rate, self.capacity = rate_per_sec, capacity  # store
        self.tokens, self.last = capacity, time.monotonic()  # state

    async def acquire(self, cost: float) -> None:  # wait until enough budget exists
        while True:  # loop until allowed
            now = time.monotonic()  # current time
            self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)  # refill
            self.last = now  # update clock
            if self.tokens >= cost:  # enough budget
                self.tokens -= cost  # spend
                return  # go
            await asyncio.sleep((cost - self.tokens) / self.rate)  # wait for the shortfall


async def call_model(job: int) -> str:  # mock model that sometimes fails like a 429
    await asyncio.sleep(0.01)  # latency
    if random.random() < 0.2:  # 20% fail
        raise ConnectionError("429 rate limited")  # simulated error
    return f"ok-{job}"  # success


async def worker(name: str, q: asyncio.Queue[int], bucket: TokenBucket, out: list[str]) -> None:  # consume jobs
    while True:  # loop forever
        job = await q.get()  # next job
        try:
            await bucket.acquire(cost=200)  # pretend each job costs 200 tokens
            for attempt in range(4):  # retries
                try:
                    out.append(await call_model(job))  # try
                    break  # success
                except ConnectionError:  # transient
                    await asyncio.sleep(0.02 * 2 ** attempt + random.random() * 0.01)  # backoff + jitter
            else:
                out.append(f"failed-{job}")  # give up, record failure
        finally:
            q.task_done()  # always mark done


async def main() -> None:  # driver
    q: asyncio.Queue[int] = asyncio.Queue(maxsize=50)  # bounded queue = backpressure
    bucket, out = TokenBucket(rate_per_sec=5000, capacity=2000), []  # limiter and results
    workers = [asyncio.create_task(worker(f"w{i}", q, bucket, out)) for i in range(4)]  # 4 workers
    shed = 0  # shed counter
    for j in range(80):  # try to enqueue 80 jobs
        try:
            q.put_nowait(j)  # non-blocking enqueue
        except asyncio.QueueFull:  # queue is full
            shed += 1  # load shedding: tell client to retry later (HTTP 429/503)
    await q.join()  # wait for all accepted jobs
    for w in workers:  # stop workers
        w.cancel()  # cancel
    print("processed", len(out), "shed", shed)  # summary


if __name__ == "__main__":
    asyncio.run(main())  # run
```

---

## 🟠 FastAPI Integration
Keep handlers async and stateless, cap concurrency, and offload bulk work. Run multiple processes with a server such as uvicorn/gunicorn workers behind a load balancer.

```python
import asyncio  # semaphore
from fastapi import FastAPI, HTTPException  # app, errors
from pydantic import BaseModel  # schema

app = FastAPI()  # app
SEM = asyncio.Semaphore(20)  # per-process cap on concurrent model calls
JOBS: dict[str, str] = {}  # job store (use Redis/DB in production)


class Item(BaseModel):  # request
    text: str  # invoice text


@app.post("/classify")  # real-time route
async def classify(item: Item) -> dict[str, str]:
    if SEM.locked():  # no capacity left
        raise HTTPException(status_code=503, detail="busy", headers={"Retry-After": "2"})  # shed load
    async with SEM:  # take a slot
        await asyncio.sleep(0.01)  # replace with an LLM call
        return {"hs_code": "8517.13"}  # answer


@app.post("/bulk", status_code=202)  # bulk route
async def bulk(items: list[Item]) -> dict[str, str]:
    job_id = "job-1"  # generate a real id in production
    JOBS[job_id] = "queued"  # enqueue to a real queue (Celery, RQ, SQS...)
    return {"job_id": job_id}  # client polls /jobs/{id}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain runnables support `abatch` with `max_concurrency` in the config, and built-in retry via `.with_retry()`. LangGraph with a persistent checkpointer lets long workflows resume after worker restarts.

```python
import asyncio  # run async code
from langchain_core.runnables import RunnableLambda  # offline runnable

async def classify(text: str) -> str:  # async function acting as a chain
    await asyncio.sleep(0.01)  # latency
    return f"code-for-{text}"  # result

chain = RunnableLambda(classify).with_retry(stop_after_attempt=3)  # real retry wrapper
results = asyncio.run(chain.abatch(["phone", "shirt", "laptop"], config={"max_concurrency": 2}))  # bounded batch
print(results)  # outputs
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Unbounded concurrency
✅ Correct: semaphore or queue limits.
```python
# Wrong
await asyncio.gather(*(llm(x) for x in 10_000_items))  # 429 storm
# Right
async with sem: await llm(x)  # bounded, with retries and backoff
```

❌ Mistake 2: Retrying without backoff or jitter
✅ Correct: exponential backoff plus jitter, and a retry cap.
```python
# Wrong
while True: try_call()  # hammering a struggling provider
# Right
for i in range(4): sleep(2**i + random())  # polite retries
```

---

## 🧠 Tricky Interview Question
**Q**: "Traffic doubles. You double API replicas but throughput barely moves and errors rise. Why?"

**Answer**: The bottleneck is not your API CPU; it is the provider's rate limit (tokens per minute) or the vector DB. More replicas just send more requests into the same limit, causing 429s and retries. Fix by globally limiting calls (shared rate limiter in Redis), queueing, caching, routing to a cheaper model or second provider/quota, and scaling the real bottleneck.

---

## ⚫ Interview Questions + Answers

Q1: Horizontal vs vertical scaling? (Easy)
A1: Horizontal adds more instances; vertical makes one instance bigger. Stateless APIs scale horizontally.

Q2: Why async for LLM apps? (Easy)
A2: Calls are I/O-bound and slow; async lets one process handle many waiting calls efficiently.

Q3: What is backpressure? (Medium)
A3: Signalling producers to slow down when the system is saturated (bounded queues, 429/503, Retry-After) instead of accepting unlimited work.

Q4: How do you handle provider rate limits across many replicas? (Medium)
A4: A shared limiter (Redis token bucket), central queue, per-tenant quotas, retry with jitter, and multiple provider keys/regions or fallback models.

Q5: Design for 100x traffic growth on an LLM chat app. (Hard)
A5: Stateless replicas with autoscaling on in-flight requests, streaming responses, cache layers, model routing, queue for non-interactive work, sharded vector DB with replicas, conversation state in Redis/DB, quotas per tenant, observability (token usage, p95, error rate), load tests, and graceful degradation plans.

---

## 🔷 When to Use + When Not to Use
✅ Invest in scaling when:
- Traffic is growing, spiky or tied to deadlines

❌ Avoid over-engineering when:
- Internal tool with a few users; simple deployment is enough

---

## 📊 Visual Diagram
```
 Clients
   │
   ▼
 Load balancer ─▶ API replicas (stateless, async) ─▶ Rate limiter / semaphore ─▶ LLM provider
                        │                                   ▲
                        ├─▶ Cache (Redis) ──────────────────┘
                        ├─▶ Vector DB (shards + replicas)
                        └─▶ Queue ─▶ Workers (bulk, ingestion)  [bounded: backpressure]
```

---

## 💰 Cost Impact
Scaling raises token spend linearly with traffic and adds infrastructure cost (replicas, queues, DB). Retries multiply tokens when requests fail after partial work; unbounded agent loops can multiply cost during spikes.
Optimise: cache, route to small models, cap tokens and loop steps, use batch APIs for non-urgent work (providers often discount batch processing; check current terms), autoscale down at night, set per-tenant budgets and alerts.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stateless | No local session data | स्थानीय state नहीं |
| Rate limit | Provider request/token cap | दर सीमा |
| Backpressure | Slow producers when busy | दबाव नियंत्रण |
| Load shedding | Reject excess work | अतिरिक्त काम अस्वीकार |
| Queue | Buffer of pending jobs | कतार |
| Autoscaling | Adding/removing instances automatically | स्वचालित scaling |

---

## ⚡ 3-Line Summary
English: AI systems usually bottleneck on model rate limits and slow calls, not CPU.
Use stateless async APIs, shared rate limiting, queues, caches and backpressure.
Load test to find the real bottleneck before adding hardware.
Hindi: AI systems में bottleneck अक्सर model rate limits और धीमी calls होते हैं, CPU नहीं।
Stateless async API, shared rate limiting, queues, caches और backpressure इस्तेमाल करो।
Hardware बढ़ाने से पहले load test से असली bottleneck खोजो।

---

## ➡️ Next Topic
**517. Load Balancing for AI** — spreading requests across replicas, models and providers.
