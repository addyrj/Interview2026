---

# 010. FastAPI Background Tasks
# हिंदी में: FastAPI Background Tasks

---

## 🔵 Simple Definition (English)
A background task is a function FastAPI runs after it has already sent the response. The user gets the answer fast, while slow side jobs (saving logs, tracking token usage, sending an email) finish afterwards. It is built in via `BackgroundTasks`.

## 🔵 सरल परिभाषा (Hindi)
Background task ऐसा function है जिसे FastAPI response भेजने के बाद चलाता है। User को जवाब जल्दी मिलता है, और धीमे side काम (logs save करना, token usage track करना, email भेजना) बाद में पूरे होते हैं। यह `BackgroundTasks` से built-in मिलता है।

---

## 🔴 Problem it Solves
After an LLM answer you often must write an audit log, update usage counters, or push to analytics. Doing it before responding adds latency the user feels. Background tasks move non-critical work out of the request path without adding a queue system.

## 🔴 यह क्यों बना? (Hindi)
LLM answer के बाद अक्सर audit log लिखना, usage counters update करना या analytics में भेजना होता है। यह response से पहले करने पर user को देरी महसूस होती है। Background tasks बिना queue system जोड़े non-critical काम को request path से बाहर ले जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Route takes a parameter `background_tasks: BackgroundTasks`
Step 2 → Route calls background_tasks.add_task(func, arg1, arg2, key=value)
Step 3 → Route returns its response normally
Step 4 → FastAPI/Starlette sends the response to the client
Step 5 → AFTER sending, it runs the queued functions (async ones on the loop, sync ones in a threadpool)
Step 6 → Exceptions inside tasks do NOT change the response (already sent); they must be logged by you
Step 7 → Tasks live in the same process: if the server restarts, queued tasks are lost
```

## 🟢 कैसे काम करता है? (Hindi)

```
Step 1 → Route में parameter `background_tasks: BackgroundTasks` लो
Step 2 → background_tasks.add_task(func, arg1, arg2, key=value) call करो
Step 3 → Route सामान्य रूप से response return करता है
Step 4 → FastAPI/Starlette response client को भेजता है
Step 5 → भेजने के BAAD queued functions चलते हैं (async loop पर, sync threadpool में)
Step 6 → Task के अंदर exception response नहीं बदलता (वह जा चुका है); log आपको करना है
Step 7 → Tasks उसी process में हैं: server restart हुआ तो queued tasks खो जाते हैं
```

---

## 🟡 Real World Example
**Tariff Classification System**: `POST /classify` returns the HS code immediately. In the background: save the request and response to the audit table (customs needs a record), add the token count to the user's daily usage, and push a metric. If the audit write is critical (legal requirement), use a durable queue instead.

**Zomato AI**: After returning recommendations, log which restaurants were shown so the ranking model can learn later.

## 🟡 Real Example Hindi mein
**Tariff System**: `POST /classify` HS code तुरंत लौटाता है। Background में: request-response audit table में save करना (customs को record चाहिए), user के daily usage में token count जोड़ना, और metric भेजना। Audit write अगर legally ज़रूरी है तो durable queue use करो।

**Zomato AI**: Recommendations लौटाने के बाद log करो कि कौन से restaurants दिखाए गए, ताकि ranking model बाद में सीख सके।

---

## 💻 Code Example — Basic
```python
# Basic BackgroundTasks - needs fastapi + httpx for the test client
import time  # to measure order of events
from fastapi import BackgroundTasks, FastAPI  # tools
from fastapi.testclient import TestClient  # tests

app = FastAPI()  # app
events: list[str] = []  # records order of events for the demo


def write_audit(user: str, hs_code: str) -> None:  # normal (sync) function, runs after response
    time.sleep(0.2)  # pretend slow DB write
    events.append(f"audit saved for {user}: {hs_code}")  # record that it happened


@app.post("/classify")  # route
async def classify(user: str, background_tasks: BackgroundTasks) -> dict[str, str]:  # FastAPI injects BackgroundTasks
    hs_code = "8517.13"  # fake LLM answer
    background_tasks.add_task(write_audit, user, hs_code)  # schedule, does not run yet
    events.append("response being returned")  # runs first
    return {"hs_code": hs_code}  # response goes out, then the task runs


client = TestClient(app)  # test client runs background tasks before returning
print(client.post("/classify?user=alice").json())  # {'hs_code': '8517.13'}
print(events)  # ['response being returned', 'audit saved for alice: 8517.13']
```

## 💻 Code Example — Advanced
```python
# Production style: async background task with its own error handling, usage tracking,
# retry, and a dependency that adds tasks
import asyncio  # async tools
import logging  # logging for failures
from typing import Annotated  # typing

from fastapi import BackgroundTasks, Depends, FastAPI  # tools
from fastapi.testclient import TestClient  # tests
from pydantic import BaseModel  # body

log = logging.getLogger("bg")  # logger
usage_db: dict[str, int] = {}  # fake storage: user -> tokens
flaky = {"fail_once": True}  # makes the first save fail to show retry


async def save_usage(user: str, tokens: int, attempts: int = 3) -> None:  # async task
    for attempt in range(1, attempts + 1):  # retry loop
        try:  # tasks must never raise silently
            if flaky["fail_once"]:  # simulate transient DB error once
                flaky["fail_once"] = False  # only the first time
                raise ConnectionError("db busy")  # error
            usage_db[user] = usage_db.get(user, 0) + tokens  # persist usage
            return  # success
        except ConnectionError as exc:  # catch transient errors
            log.warning("save_usage attempt %s failed: %s", attempt, exc)  # log it
            await asyncio.sleep(0.05 * attempt)  # small backoff
    log.error("save_usage permanently failed for %s", user)  # final failure: alert here


class Body(BaseModel):  # request
    description: str  # text


class Tracker:  # dependency that lets any route schedule tracking
    def __init__(self, background_tasks: BackgroundTasks) -> None:  # same BackgroundTasks object as the route
        self.bg = background_tasks  # keep reference

    def track(self, user: str, tokens: int) -> None:  # schedule helper
        self.bg.add_task(save_usage, user, tokens)  # queue the work


app = FastAPI()  # app


@app.post("/classify")  # route
async def classify(body: Body, user: str, tracker: Annotated[Tracker, Depends(Tracker)]) -> dict[str, str | int]:  # DI
    tokens = 500 + len(body.description) // 4  # fake token estimate
    tracker.track(user, tokens)  # schedule usage saving, no waiting
    return {"hs_code": "8517.13", "tokens": tokens}  # return immediately


with TestClient(app) as c:  # run demo
    print(c.post("/classify?user=bob", json={"description": "Android phone"}).json())  # response
    print(usage_db)  # {'bob': 503} saved after one retry
```

---

## 🟠 FastAPI Integration
`BackgroundTasks` is a FastAPI feature. It fits short, non-critical work in the same process. For long jobs (summarising 500 pages, bulk embeddings), return a job id (HTTP 202) and use a real worker (Celery, ARQ, RQ, or a cloud queue) so jobs survive restarts and can be retried and monitored.

```python
# 202 Accepted pattern: start a job, poll for status (in-memory demo)
import asyncio  # async tools
import uuid  # job ids
from fastapi import BackgroundTasks, FastAPI, HTTPException  # tools

app = FastAPI()  # app
jobs: dict[str, dict] = {}  # job store (use Redis/DB in production)


async def run_job(job_id: str, text: str) -> None:  # long work
    jobs[job_id]["status"] = "running"  # update status
    await asyncio.sleep(1)  # pretend summarisation
    jobs[job_id] = {"status": "done", "result": text[:20]}  # store result


@app.post("/summarize", status_code=202)  # 202 = accepted, not finished
async def summarize(text: str, bg: BackgroundTasks) -> dict[str, str]:  # route
    job_id = uuid.uuid4().hex  # new id
    jobs[job_id] = {"status": "queued"}  # initial state
    bg.add_task(run_job, job_id, text)  # start after response
    return {"job_id": job_id}  # client polls with this


@app.get("/jobs/{job_id}")  # polling route
async def job(job_id: str) -> dict:  # status
    if job_id not in jobs:  # unknown id
        raise HTTPException(404, "job not found")  # not found
    return jobs[job_id]  # status or result
```

---

## 🔗 LangChain / LangGraph Connection
Callbacks and tracing (LangSmith) already send data in the background. For your own post-processing (store the LLM output, update counters), use a background task after `chain.ainvoke`. For long LangGraph runs, start the graph in a worker and stream or poll its state using a `thread_id` and a checkpointer.

```python
# Background logging of a chain result (needs an API key to run the chain)
from fastapi import BackgroundTasks, FastAPI  # tools
from langchain_core.prompts import ChatPromptTemplate  # prompt
from langchain_openai import ChatOpenAI  # model

app = FastAPI()  # app
chain = ChatPromptTemplate.from_template("HS code for {item}") | ChatOpenAI(model="gpt-4o-mini")  # chain


def log_result(item: str, answer: str) -> None:  # sync task
    print("LOG", item, answer)  # replace with DB write


@app.get("/hs")  # route
async def hs(item: str, bg: BackgroundTasks) -> dict[str, str]:  # route
    msg = await chain.ainvoke({"item": item})  # get answer
    bg.add_task(log_result, item, str(msg.content))  # log later
    return {"answer": str(msg.content)}  # respond now
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using BackgroundTasks for critical or very long jobs
✅ Correct: use a durable queue with retries.

```python
# Wrong: a 10-minute embedding job in BackgroundTasks; deploy restarts and the job vanishes
bg.add_task(embed_all_documents)
# Right: enqueue to Celery/ARQ and return job id
await queue.enqueue("embed_all_documents", doc_ids)
```

❌ Mistake 2: Letting exceptions disappear
✅ Correct: wrap the task body with try/except and log.

```python
# Wrong: error is lost, nobody knows audit failed
def audit(x):
    db.insert(x)
# Right
def audit(x):
    try:
        db.insert(x)
    except Exception:
        logger.exception("audit failed")
```

❌ Mistake 3: Blocking code in an `async def` task (freezes the loop). Use a plain `def` task (runs in a threadpool) for blocking work.

---

## 🧠 Tricky Interview Question

**Q**: "Your background task writes usage to the DB, but sometimes the user's next request shows old usage. Why?"

**Answer**: The task runs after the response is sent, so a fast follow-up request can arrive before the write finishes (eventual consistency). If the budget check depends on up-to-date usage, do the atomic increment in the request path (Redis `INCRBY`, which is fast) and only do the slow durable DB write in the background. Also a request from a different worker process will not see in-memory state, so use shared storage.

---

## ⚫ Interview Questions + Answers

Q1: When does a background task run? (Easy)
A1: After the response has been sent to the client, in the same process.

Q2: Can a background task change the response? (Easy)
A2: No. The response is already sent. Errors in the task do not reach the user.

Q3: BackgroundTasks vs Celery? (Medium)
A3: BackgroundTasks is simple and in-process: no broker, no retries, lost on crash, not visible in monitoring. Celery/ARQ use a broker (Redis/RabbitMQ), run in separate workers, support retries, scheduling and scaling. Use BackgroundTasks for light side-effects (logs, metrics), a queue for long or must-not-lose jobs.

Q4: Sync vs async functions as tasks? (Medium)
A4: An `async def` task runs on the event loop, so it must not block. A plain `def` task is run in a threadpool, so blocking libraries are fine there. Pick according to what the function calls.

Q5: How do you design a reliable "summarise this 500-page tariff PDF" feature? (Hard)
A5: Return 202 with a job id after saving the upload to object storage. Enqueue a durable job; the worker splits the document into chunks, summarises chunks in parallel with a semaphore (map step), then merges them (reduce step), saving progress so retries resume instead of restarting (token savings). Store status in Redis/DB; clients poll or use SSE/webhook. Make jobs idempotent, add timeouts and a dead-letter queue, and track tokens per job for cost control.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Short, non-critical side jobs: logs, metrics, emails, cache warm-up
- You want a fast response without extra infrastructure
- Failure of the task is acceptable or can be retried manually

❌ Avoid when:
- Work takes minutes or must never be lost
- You need retries, scheduling or monitoring
- The task is CPU-heavy (it will slow the server for other users)

---

## 📊 Visual Diagram
```
 Client ── POST /classify ──►  route:  LLM call → add_task(save_usage) → return
    ▲                                         │
    └────────── 200 JSON (fast) ◄─────────────┘
                                              │ after response is sent
                                              ▼
                                   save_usage(user, tokens)   (same process)

 Long job:  POST → 202 {job_id} ; worker queue runs it ; GET /jobs/{id} → status
```

---

## 💰 Cost Impact
Background tasks do not change token usage, but they help control cost: usage tracking and logging happen without delaying responses, so you can report per-user spend. They also reduce latency-related timeouts that cause client retries (each retry is a repeated LLM call). For big jobs, a queue with checkpoints avoids redoing completed chunks after a crash: if a 300K-token job fails at 90 percent and restarts from zero you pay 570K extra tokens (about $0.09 on gpt-4o-mini input pricing, far more on bigger models); with per-chunk checkpoints you pay about 30K.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BackgroundTasks | Run work after response | response के बाद काम चलाना |
| add_task | Queue a function call | function call queue करना |
| 202 Accepted | Work accepted, not done | काम मिला, पूरा नहीं |
| Job id | Handle to track a job | job ट्रैक करने की id |
| Worker | Separate process doing jobs | job करने वाला अलग process |
| Broker | Message store between app and worker | app और worker के बीच संदेश store |
| Idempotent | Safe to run again | दोबारा चलाना सुरक्षित |
| Dead-letter queue | Place for failed jobs | fail jobs की जगह |

---

## ⚡ 3-Line Summary
English: BackgroundTasks run functions after the response is sent, ideal for logs and usage tracking. They are in-process and not durable, so long or critical jobs need a real queue. Always catch and log errors inside tasks.
Hindi: BackgroundTasks response भेजने के बाद functions चलाते हैं, logs और usage tracking के लिए बढ़िया। ये उसी process में हैं और durable नहीं, इसलिए लंबे या ज़रूरी jobs के लिए असली queue लो। Tasks के अंदर errors हमेशा पकड़कर log करो।

---

## ➡️ Next Topic
**011. FastAPI Error Responses** — next we make sure failures (including those in LLM calls) are turned into clear, consistent HTTP errors.
