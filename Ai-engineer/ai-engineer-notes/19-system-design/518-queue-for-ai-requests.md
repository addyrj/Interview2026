---

# 518. Queue for AI Requests
# हिंदी में: AI Requests के लिए Queue

---

## 🔵 Simple Definition (English)
A queue is a waiting line between the API and the workers that call the LLM. The API accepts a request, puts a job in the queue, and returns a job ID at once. Workers pick jobs at their own speed, so traffic spikes and rate limits do not crash the system.

## 🔵 सरल परिभाषा (Hindi)
Queue एक waiting line है जो API और LLM call करने वाले workers के बीच होती है। API request लेकर job queue में डालती है और तुरंत job ID लौटा देती है। Workers अपनी speed से job उठाते हैं, इसलिए traffic spike और rate limit से system crash नहीं होता।

---

## 🔴 Problem it Solves
LLM calls are slow (2-30 seconds) and providers enforce rate limits (requests/min and tokens/min). If 5,000 users hit your API together, direct calls give HTTP 429 errors, timeouts, and lost requests. Holding HTTP connections open for 30 seconds also eats your server threads. A queue smooths bursts, retries failures, and protects your token budget.

## 🔴 यह क्यों बना? (Hindi)
LLM call slow होती है (2-30 sec) और provider rate limit लगाता है। 5,000 users एक साथ आए तो direct call से 429 error, timeout और lost requests मिलते हैं। Queue burst को smooth करती है, failure retry करती है और token budget बचाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Client sends POST /classify with product description
Step 2 → API validates input, creates job {id, payload, status=queued}
Step 3 → API pushes job into queue (Redis / SQS / RabbitMQ) and returns 202 + job_id
Step 4 → Worker pool pulls jobs (bounded concurrency, e.g. 10 at a time)
Step 5 → Worker calls the LLM, respecting the rate limit
Step 6 → On success: store result, status=done. On failure: retry with backoff
Step 7 → After max retries: move job to Dead Letter Queue (DLQ)
Step 8 → Client polls GET /jobs/{id} (or gets a webhook / WebSocket push)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Client product description के साथ POST /classify भेजता है
Step 2 → API input validate करके job बनाती है {id, payload, status=queued}
Step 3 → Job queue में जाती है, API 202 + job_id लौटाती है
Step 4 → Worker pool सीमित concurrency (जैसे 10) से job उठाता है
Step 5 → Worker rate limit मानते हुए LLM call करता है
Step 6 → Success पर result save; failure पर backoff के साथ retry
Step 7 → Max retries के बाद job Dead Letter Queue (DLQ) में
Step 8 → Client GET /jobs/{id} poll करता है (या webhook मिलता है)
```

---

## 🟡 Real World Example
**Tariff Classification System**: Customs brokers upload 20,000 product lines at month end. Each line needs an HS code from the LLM. Direct calls would hit the 429 limit within seconds. With a queue, the API returns 20,000 job IDs in a few seconds, and 10 workers classify them at a steady rate, retrying failures. A dashboard shows progress (done / queued / failed).

**Zomato-style**: During the IPL final, millions of review-summary requests arrive. A queue with priority lanes serves paying restaurants first and bulk jobs later.

## 🟡 Real Example Hindi mein
**Tariff System**: Month end पर brokers 20,000 product lines upload करते हैं। Direct call से कुछ ही seconds में 429 आ जाएगा। Queue में API कुछ seconds में 20,000 job ID लौटा देती है और 10 workers steady speed से classify करते हैं, failure retry होती है।
**Zomato-style**: IPL final में लाखों review-summary requests आती हैं। Priority lanes वाली queue पहले paying restaurants को serve करती है।

---

## 💻 Code Example — Basic
```python
# Basic in-memory queue with workers (pure Python, runs offline)
import queue                      # thread-safe queue from the standard library
import threading                  # to run workers in parallel
import time                       # to simulate LLM latency
from typing import Optional       # type hint for optional values

# Shared queue that holds (job_id, text) tuples
jobs: "queue.Queue[Optional[tuple[int, str]]]" = queue.Queue()
# Dictionary that stores finished results by job id
results: dict[int, str] = {}

def fake_llm(text: str) -> str:
    """Pretend LLM call: returns an HS code after a short delay."""
    time.sleep(0.05)              # simulate network + model latency
    return "8517.13" if "phone" in text else "9999.99"   # toy rule

def worker() -> None:
    """Pull jobs until a None sentinel arrives."""
    while True:                   # keep working forever
        item = jobs.get()         # block until a job is available
        if item is None:          # sentinel means shut down
            jobs.task_done()      # mark sentinel as handled
            break                 # exit the loop
        job_id, text = item       # unpack the job
        try:
            results[job_id] = fake_llm(text)   # call the model, save result
        except Exception as exc:               # never let one job kill the worker
            results[job_id] = f"error: {exc}"  # store the error text
        finally:
            jobs.task_done()      # tell the queue this job is complete

# Start 3 worker threads
threads = [threading.Thread(target=worker) for _ in range(3)]
for t in threads:                 # start each thread
    t.start()

# Producer: the "API" enqueues 6 jobs and returns immediately
for i, text in enumerate(["smart phone", "cotton shirt"] * 3):
    jobs.put((i, text))           # enqueue without waiting for the LLM

for _ in threads:                 # one sentinel per worker
    jobs.put(None)
jobs.join()                       # wait until all jobs are processed
print(sorted(results.items()))    # show results sorted by job id
```

## 💻 Code Example — Advanced
```python
# Production style: asyncio queue, bounded concurrency, retry with backoff, DLQ, rate limit
import asyncio                                   # async runtime
import random                                    # jitter for backoff
import time                                      # timestamps
from dataclasses import dataclass, field         # simple job model
from typing import Awaitable, Callable           # type hints for the LLM function

@dataclass
class Job:
    """A unit of work for the queue."""
    job_id: str                                  # unique id returned to the client
    payload: str                                 # product description
    attempts: int = 0                            # how many times we tried
    status: str = "queued"                       # queued | running | done | failed
    result: str | None = None                    # LLM answer when done
    error: str | None = None                     # last error message

class AIQueue:
    """Async job queue with retries, DLQ and a requests-per-second limit."""

    def __init__(self, llm: Callable[[str], Awaitable[str]], workers: int = 5,
                 max_retries: int = 3, rps: float = 10.0) -> None:
        self.llm = llm                           # async function that calls the model
        self.q: asyncio.Queue[Job] = asyncio.Queue(maxsize=1000)  # bounded queue = backpressure
        self.dlq: list[Job] = []                 # dead letter queue for permanent failures
        self.jobs: dict[str, Job] = {}           # job store (use Redis in production)
        self.workers = workers                   # number of worker tasks
        self.max_retries = max_retries           # retry budget per job
        self.min_gap = 1.0 / rps                 # minimum seconds between LLM calls
        self._last_call = 0.0                    # time of last LLM call
        self._lock = asyncio.Lock()              # protects the rate limiter
        self._tasks: list[asyncio.Task[None]] = []   # worker handles

    async def submit(self, job: Job) -> str:
        """Enqueue a job; raises QueueFull when overloaded (caller returns 429/503)."""
        self.jobs[job.job_id] = job              # remember the job
        self.q.put_nowait(job)                   # fail fast if the queue is full
        return job.job_id                        # client uses this id to poll

    async def _throttle(self) -> None:
        """Simple rate limiter: spaces out LLM calls."""
        async with self._lock:                   # one waiter at a time
            wait = self._last_call + self.min_gap - time.monotonic()  # time left
            if wait > 0:                         # too soon?
                await asyncio.sleep(wait)        # wait the remaining gap
            self._last_call = time.monotonic()   # record this call

    async def _run_one(self, job: Job) -> None:
        """Process a single job with retry + DLQ logic."""
        job.status = "running"                   # mark as running
        while job.attempts < self.max_retries:   # retry loop
            job.attempts += 1                    # count the attempt
            try:
                await self._throttle()           # respect provider rate limit
                job.result = await asyncio.wait_for(self.llm(job.payload), timeout=30)  # timeout guard
                job.status = "done"              # success
                return                           # leave the retry loop
            except Exception as exc:             # network, 429, timeout, ...
                job.error = repr(exc)            # keep the last error
                delay = (2 ** job.attempts) * 0.1 + random.random() * 0.1  # backoff + jitter
                await asyncio.sleep(delay)       # wait before retry
        job.status = "failed"                    # all retries used
        self.dlq.append(job)                     # park it for manual review

    async def _worker(self) -> None:
        """Worker loop: take a job, process it, repeat."""
        while True:                              # run until cancelled
            job = await self.q.get()             # wait for a job
            try:
                await self._run_one(job)         # process it
            finally:
                self.q.task_done()               # always mark done

    def start(self) -> None:
        """Start worker tasks."""
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.workers)]

    async def stop(self) -> None:
        """Drain the queue then cancel workers (graceful shutdown)."""
        await self.q.join()                      # wait for pending jobs
        for t in self._tasks:                    # cancel each worker
            t.cancel()

async def demo() -> None:
    """Run the queue with a flaky fake LLM."""
    calls = {"n": 0}                             # counter to make the fake flaky

    async def fake_llm(text: str) -> str:
        calls["n"] += 1                          # count calls
        if calls["n"] % 4 == 0:                  # every 4th call fails
            raise RuntimeError("429 rate limited")
        await asyncio.sleep(0.01)                # simulate latency
        return "8517.13"                         # fixed HS code

    aq = AIQueue(fake_llm, workers=3, rps=50)    # build the queue
    aq.start()                                   # start workers
    for i in range(8):                           # submit 8 jobs
        await aq.submit(Job(job_id=f"j{i}", payload="smart phone"))
    await aq.stop()                              # wait for completion
    print({j.job_id: j.status for j in aq.jobs.values()})   # show final statuses

if __name__ == "__main__":
    asyncio.run(demo())                          # run the async demo
```

---

## 🟠 FastAPI Integration
FastAPI is the front door. The route only validates and enqueues, returning `202 Accepted`. A second route lets clients poll. In production the in-process queue becomes Redis (RQ, Arq, Celery) or SQS so jobs survive restarts.

```python
# FastAPI route that enqueues and a route that polls (uses the AIQueue idea above)
import uuid                                          # to create job ids
from contextlib import asynccontextmanager          # lifespan helper
from fastapi import FastAPI, HTTPException          # web framework
from pydantic import BaseModel, Field               # request validation

class ClassifyRequest(BaseModel):
    description: str = Field(min_length=3, max_length=2000)   # input limit protects tokens

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start workers at startup, stop them at shutdown."""
    app.state.queue = AIQueue(my_llm_call, workers=10, rps=20)   # my_llm_call = your async LLM function
    app.state.queue.start()                          # start workers
    yield                                            # app runs here
    await app.state.queue.stop()                     # graceful drain

app = FastAPI(lifespan=lifespan)                     # attach lifespan

@app.post("/classify", status_code=202)
async def classify(req: ClassifyRequest) -> dict[str, str]:
    """Accept the work and return a job id immediately."""
    job = Job(job_id=str(uuid.uuid4()), payload=req.description)   # new job
    try:
        await app.state.queue.submit(job)            # enqueue
    except asyncio.QueueFull:                        # overloaded
        raise HTTPException(status_code=503, detail="Queue full, retry later")
    return {"job_id": job.job_id, "status": job.status}

@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, str | None]:
    """Poll the job status."""
    job = app.state.queue.jobs.get(job_id)           # look up job
    if job is None:                                  # unknown id
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": job.status, "result": job.result, "error": job.error}
```

---

## 🔗 LangChain / LangGraph Connection
LangChain runnables have `abatch` with `max_concurrency`, which is a lightweight in-process queue. For durable work, a worker pops a job from Redis and runs a LangGraph graph; use a checkpointer so a half-finished graph can resume after a crash.

```python
# LangChain: bounded concurrency over many inputs (acts like a worker pool)
from langchain_openai import ChatOpenAI                  # chat model wrapper
from langchain_core.prompts import ChatPromptTemplate    # prompt template

prompt = ChatPromptTemplate.from_template("Give the HS code for: {item}")   # simple prompt
chain = prompt | ChatOpenAI(model="gpt-4o-mini", max_retries=3)             # built-in retries

async def classify_many(items: list[str]) -> list[str]:
    """Run many items with at most 10 parallel LLM calls."""
    msgs = await chain.abatch([{"item": i} for i in items], config={"max_concurrency": 10})
    return [m.content for m in msgs]                      # extract text
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Unbounded queue and unbounded workers
✅ Correct: Bound both. A bounded queue gives backpressure (return 503), bounded workers respect rate limits.

```python
# Wrong — thousands of tasks hit the provider at once
await asyncio.gather(*[call_llm(x) for x in items])

# Right — semaphore limits parallel calls
sem = asyncio.Semaphore(10)                  # max 10 at a time
async def limited(x: str) -> str:
    async with sem:                          # wait for a free slot
        return await call_llm(x)
await asyncio.gather(*[limited(x) for x in items])
```

❌ Mistake 2: Retrying forever, no dead letter queue
✅ Correct: Cap retries, use exponential backoff with jitter, then move to a DLQ and alert.

```python
# Wrong — infinite retry burns tokens on a poison message
while True:
    try: return await call_llm(x)
    except Exception: continue

# Right — capped retries then DLQ
for attempt in range(3):
    try: return await call_llm(x)
    except Exception: await asyncio.sleep(2 ** attempt)
dlq.append(x)
```

---

## 🧠 Tricky Interview Question

**Q**: "A worker crashes after the LLM call succeeded but before saving the result. The queue redelivers the job. What goes wrong and how do you prevent it?"

**Answer**: Most queues give at-least-once delivery, so the job runs twice: you pay for tokens twice and may write duplicate rows or send two emails. Fix with idempotency: use the job ID as an idempotency key, check "already done?" before calling the LLM, and write the result with an upsert. Also store the result before acknowledging the message (ack after save), and set a visibility timeout longer than the LLM timeout.

---

## ⚫ Interview Questions + Answers

Q1: Why use a queue for LLM calls? (Easy)
A1: LLM calls are slow and rate limited. A queue decouples the API from workers, absorbs bursts, enables retries and keeps HTTP requests short.

Q2: What is a Dead Letter Queue? (Easy)
A2: A separate queue for jobs that failed after max retries. Engineers inspect it, fix the bug or data, and replay. It stops poison jobs from blocking the main queue.

Q3: How do you control concurrency against a provider rate limit? (Medium)
A3: Limit worker count, use a semaphore, add a token-bucket limiter, and track tokens per minute (not only requests per minute). Honour the `Retry-After` header on 429 responses and add jitter to backoff.

Q4: Polling vs webhook vs WebSocket for results? (Medium)
A4: Polling is simplest and works everywhere but wastes calls. Webhooks suit server-to-server integrations. WebSocket or SSE gives live progress for browsers. Many systems offer polling plus an optional webhook.

Q5: Design a priority queue where paid users are not starved by a bulk upload, yet bulk work still finishes. (Hard)
A5: Use separate queues per tier (or weighted fair queuing): workers pull e.g. 8 interactive jobs for every 2 bulk jobs. Add per-tenant concurrency caps so one tenant cannot fill the queue, age-based priority boost so old bulk jobs eventually run, and autoscale workers on queue depth and oldest-message age. Monitor p95 wait time per tier.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Work takes more than a few seconds (batch classification, long agents)
- Traffic is bursty or provider rate limits are tight
- You need retries, audit trail, or priority lanes

❌ Avoid when:
- A chat UI needs token streaming now (use streaming, not a queue)
- Volume is tiny and latency matters more than resilience
- You cannot make jobs idempotent (fix that first)

---

## 📊 Visual Diagram
```
 Client ──POST──▶ [ FastAPI ] ──push──▶ [ Queue ] ──pull──▶ [ Worker 1 ]──┐
    ▲   202+id        │                    │  │             [ Worker 2 ]──┼──▶ LLM API
    │                 ▼                    │  └──pull──────▶ [ Worker N ]──┘   (rate limited)
    │            [ Job Store ] ◀───result───┘          │ fails 3x
    └──GET /jobs/{id}──┘                               ▼
                                                  [ Dead Letter Queue ]
```

---

## 💰 Cost Impact
- Tokens: queue itself uses zero tokens, but retries re-send the whole prompt. Example: 20,000 jobs x 600 input + 100 output tokens = 12M input + 2M output tokens. Illustrative price of $0.15 / $0.60 per 1M gives about $1.80 + $1.20 = $3.00. A 10% retry rate adds about $0.30.
- Optimisation: cap retries; cache results by prompt hash so duplicate jobs cost nothing; route bulk (non-urgent) jobs to a provider batch API (often about 50% cheaper, check current pricing); validate and truncate input before enqueue; drop jobs older than their usefulness (TTL).
- Run few workers: a queue lets you size infrastructure for average load, not peak.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Queue | Ordered waiting line of jobs | Jobs की waiting line |
| Worker | Process that executes jobs | Job चलाने वाला process |
| Backpressure | Rejecting work when full | Full होने पर नया काम मना करना |
| DLQ | Queue for permanently failed jobs | Fail हुई jobs की queue |
| Idempotency | Same job twice = same effect | दो बार चलाने पर भी एक जैसा असर |
| At-least-once | Message delivered one or more times | कम से कम एक बार delivery |
| Backoff | Growing wait between retries | Retry के बीच बढ़ता इंतज़ार |

---

## ⚡ 3-Line Summary
English: A queue sits between your API and the LLM workers so bursts and rate limits do not break the system. Return 202 with a job ID, retry with backoff, and park poison jobs in a DLQ. Make jobs idempotent because delivery is at-least-once.
Hindi: Queue API और LLM workers के बीच बैठकर burst और rate limit संभालती है। 202 + job ID लौटाओ, backoff से retry करो और खराब jobs DLQ में डालो। Delivery at-least-once है, इसलिए jobs idempotent बनाओ।

---

## ➡️ Next Topic
**519. Async Processing for AI** — queues are one form of async work; next we cover asyncio, streaming and background tasks to keep latency low.
