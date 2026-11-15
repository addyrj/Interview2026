---

# 341. Celery with FastAPI
# हिंदी में: FastAPI के साथ Celery (Background Task Queue)

---

## 🔵 Simple Definition (English)
Celery is a distributed task queue. Your FastAPI route sends a task message to a broker (Redis or RabbitMQ) and returns immediately; separate Celery worker processes pick the message up and run the function. You can check the result later through a result backend.

## 🔵 सरल परिभाषा (Hindi)
Celery एक distributed task queue है। आपका FastAPI route एक task message broker (Redis या RabbitMQ) को भेजकर तुरंत return कर देता है; अलग Celery worker processes वह message उठाकर function चलाते हैं। Result बाद में result backend से देखा जा सकता है।

---

## 🔴 Problem it Solves
Some work is too slow or too important to do inside a request: sending emails, generating PDFs, resizing images, calling flaky third-party APIs, running ML jobs. If done inline, the user waits and a timeout loses the work. FastAPI's `BackgroundTasks` runs in the same process (lost if the server restarts, no retries, no scaling). Celery gives durable queues, retries, scheduling, separate scaling and monitoring.

## 🔴 यह क्यों बना? (Hindi)
कुछ काम request के अंदर करने के लिए बहुत धीमे या बहुत महत्वपूर्ण होते हैं: emails भेजना, PDF बनाना, images resize करना, अस्थिर third-party APIs call करना, ML jobs। इन्हें inline करने पर user इंतजार करता है और timeout से काम खो जाता है। FastAPI का `BackgroundTasks` उसी process में चलता है (server restart पर खो जाता है, retries नहीं, scaling नहीं)। Celery टिकाऊ queues, retries, scheduling, अलग scaling और monitoring देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Celery app is created with a broker URL and a result backend URL
Step 2 → @celery_app.task marks a function as a task
Step 3 → Route calls send_invoice.delay(order_id) -> message goes to the broker queue
Step 4 → Route returns 202 Accepted with the task_id immediately
Step 5 → A worker (celery -A app worker) takes the message from the queue
Step 6 → Worker runs the function; on failure it can retry with backoff
Step 7 → Result (or error) is stored in the result backend under the task_id
Step 8 → Client calls GET /tasks/{task_id}; API reads AsyncResult(task_id).state
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Celery app broker URL और result backend URL के साथ बनता है
Step 2 → @celery_app.task function को task बनाता है
Step 3 → Route send_invoice.delay(order_id) call करता है -> message broker queue में जाता है
Step 4 → Route तुरंत task_id के साथ 202 Accepted लौटाता है
Step 5 → Worker (celery -A app worker) queue से message लेता है
Step 6 → Worker function चलाता है; फेल होने पर backoff के साथ retry कर सकता है
Step 7 → Result (या error) task_id के नाम से result backend में रखा जाता है
Step 8 → Client GET /tasks/{task_id} करता है; API AsyncResult(task_id).state पढ़ती है
```

---

## 🟡 Real World Example
After a Razorpay payment succeeds, the API must send the invoice PDF by email, update the CRM and notify the seller. The checkout request returns `202` in 50 ms; Celery workers do the rest. If the email provider is down, the task retries with exponential backoff (1 s, 2 s, 4 s...) up to 3 times instead of failing the checkout. Nightly reports run via Celery Beat (cron-like scheduler).

## 🟡 Real Example Hindi mein
Razorpay payment सफल होने पर API को invoice PDF email करना, CRM update करना और seller को notify करना होता है। Checkout request 50 ms में `202` लौटा देती है; बाकी काम Celery workers करते हैं। Email provider बंद हो तो task checkout फेल करने की बजाय exponential backoff (1 s, 2 s, 4 s...) के साथ 3 बार तक retry करता है। रात की reports Celery Beat (cron जैसा scheduler) से चलती हैं।

---

## 💻 Code Example — Basic
```python
# Basic: tasks, chain, group, retry (verified in "eager" mode: tasks run locally, no broker needed)
from celery import Celery, chain, group                          # core Celery API

app = Celery("t", broker="memory://", backend="cache+memory://") # in-memory broker/backend for the demo
app.conf.task_always_eager = True                                # run tasks immediately in this process (tests only)


@app.task                                                        # a plain task
def add(x: int, y: int) -> int:                                  # arguments must be JSON-serializable
    return x + y                                                 # result stored in the backend


@app.task(bind=True, max_retries=2)                              # bind=True gives access to "self"
def flaky(self, n: int) -> str:                                  # task that fails twice
    if self.request.retries < 2:                                 # how many retries happened so far
        raise self.retry(countdown=0, exc=ConnectionError("down"))   # schedule a retry
    return f"ok after {self.request.retries} retries"            # success on the 3rd attempt


print(add.delay(2, 3).get())                                     # delay() = send task, get() = wait for result
print(chain(add.s(1, 2), add.s(10))().get())                     # (1+2) then +10: result is piped on
print(group(add.s(i, i) for i in range(3))().get())              # run several tasks in parallel
print(flaky.delay(1).get())                                      # retried automatically
print(add.apply_async((1, 2), countdown=60).state)               # countdown ignored in eager mode

# Output (verified, Celery 5.7):
# 5
# 13
# [0, 2, 4]
# ok after 2 retries
# SUCCESS
```

## 💻 Code Example — Advanced
```python
# Production style: FastAPI enqueues, a real Celery worker executes, API polls the result
# Verified with an embedded worker thread (memory broker). Production: Redis broker + `celery worker` process.
from celery import Celery                                        # Celery app class
from celery.contrib.testing.worker import start_worker           # embedded worker (for tests/demo)
from celery.result import AsyncResult                            # look up a task by id
from fastapi import FastAPI                                      # FastAPI
from fastapi.testclient import TestClient                        # test client

# production: broker="redis://localhost:6379/0", backend="redis://localhost:6379/1"
celery_app = Celery("tasks", broker="memory://", backend="cache+memory://")   # broker + result store
celery_app.conf.update(                                          # sensible production settings
    task_track_started=True,                                     # expose the STARTED state
    task_serializer="json",                                      # safe serializer (never pickle for user data)
    result_serializer="json",                                    # same for results
)


@celery_app.task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True, max_retries=3)
def send_invoice(self, order_id: int) -> dict[str, object]:      # idempotent task: safe to run twice
    return {"order_id": order_id, "sent": True}                  # pretend: render PDF + send email


@celery_app.task                                                 # simple second task
def add(x: int, y: int) -> int:                                  # typed arguments
    return x + y                                                 # result


app: FastAPI = FastAPI()                                         # create web app


@app.post("/orders/{order_id}/invoice", status_code=202)         # 202 Accepted = "queued"
def enqueue(order_id: int) -> dict[str, str]:                    # returns immediately
    task = send_invoice.delay(order_id)                          # put a message on the queue
    return {"task_id": task.id}                                  # client keeps this id


@app.get("/tasks/{task_id}")                                     # polling endpoint
def status(task_id: str) -> dict[str, object]:                   # look up state
    res = AsyncResult(task_id, app=celery_app)                   # handle to the stored result
    return {"state": res.state, "result": res.result if res.successful() else None}   # PENDING/STARTED/SUCCESS/FAILURE


if __name__ == "__main__":                                       # demo
    with start_worker(celery_app, perform_ping_check=False, pool="solo", loglevel="ERROR"):   # worker thread
        c = TestClient(app)                                      # web client
        r = c.post("/orders/42/invoice")                         # enqueue
        print(r.status_code, sorted(r.json()))                   # 202 ['task_id']
        tid: str = r.json()["task_id"]                           # the id
        AsyncResult(tid, app=celery_app).get(timeout=10)         # wait until the worker is done
        print(c.get(f"/tasks/{tid}").json())                     # poll the API
        print(add.delay(2, 3).get(timeout=10))                   # another task through the worker

# Output (verified; the task_id is a random UUID):
# 202 ['task_id']
# {'state': 'SUCCESS', 'result': {'order_id': 42, 'sent': True}}
# 5
```
Real deployment (not run here, no Redis server): `celery -A app.worker.celery_app worker --loglevel=INFO --concurrency=4` in its own container, plus `celery -A app.worker.celery_app beat` for schedules, and `celery flower` for monitoring.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (Celery) | JavaScript |
|---------|-----------------|-----------|
| Task queue | Celery | BullMQ, Bee-Queue |
| Broker | Redis / RabbitMQ | Redis (BullMQ) |
| Enqueue | `task.delay(args)` | `queue.add("name", data)` |
| Worker | `celery worker` process | `new Worker("queue", handler)` |
| Retries | `autoretry_for`, `retry_backoff` | `attempts`, `backoff` |
| Scheduler | Celery Beat | repeatable jobs |

```python
# Python way
send_invoice.delay(order_id)                 # enqueue; a worker runs it
```
```javascript
// JavaScript way (BullMQ)
await invoiceQueue.add("send-invoice", { orderId });   // enqueue; a Worker processes it
```

Key difference: BullMQ workers are usually Node code in the same repo and run with the same event loop; Celery workers are separate Python processes (prefork by default) that scale with `--concurrency` and are ideal for CPU-heavy tasks.

---

## 🟠 FastAPI Connection
Use FastAPI's `BackgroundTasks` for tiny, non-critical jobs (write a log, clear a cache). Use Celery when a job must survive restarts, be retried, take more than a few seconds, run on other machines, or be scheduled. The pattern: `POST` returns `202` + `task_id`; `GET /tasks/{id}` returns the state. Keep the Celery app in its own module (`worker.py`) imported by both the API and the worker, and pass IDs (not big objects) as task arguments.

```python
# FastAPI example — BackgroundTasks (same process) vs Celery (separate worker)
from fastapi import BackgroundTasks                              # built-in lightweight option


@app.post("/signup")                                             # signup endpoint
def signup(email: str, bg: BackgroundTasks) -> dict[str, str]:   # BackgroundTasks injected
    bg.add_task(print, f"welcome {email}")                       # runs after the response, same process, no retry
    send_invoice.delay(1)                                        # durable: survives restarts, retries
    return {"ok": "yes"}                                         # response is sent immediately
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing non-serializable or huge objects (ORM objects, files) as task arguments
✅ Correct: pass IDs; the worker loads data itself

```python
# Wrong — ORM object / bytes cannot be JSON-serialized (or is huge)
send_invoice.delay(order_object)
# Right
send_invoice.delay(order.id)
```

❌ Mistake 2: Blocking on a result inside the request (`.get()`)
✅ Correct: return the `task_id`; poll or use webhooks

```python
# Wrong — defeats the purpose, can deadlock the worker pool
result = send_invoice.delay(1).get()
# Right
task = send_invoice.delay(1)
return {"task_id": task.id}
```

❌ Mistake 3: Non-idempotent tasks with retries (a payment captured twice)
✅ Correct: design tasks so running twice is safe (check status or use an idempotency key)

```python
# Wrong
def charge(order_id): gateway.capture(order_id)
# Right
def charge(order_id):
    if not already_captured(order_id):
        gateway.capture(order_id)
```

---

## 🧠 Tricky Interview Question

```python
# Why might this task run twice, and what does "acks_late" change?
@celery_app.task(acks_late=True)
def process(job_id: int) -> None: ...
```
Answer: By default Celery acknowledges a message when the worker receives it ("early ack"), so a crash mid-task loses the job (at-most-once). With `acks_late=True` the ack is sent after the task finishes, so a crashed worker's message goes back to the queue and another worker re-runs it (at-least-once). That means the task can run twice, so it must be idempotent. Celery therefore gives you at-least-once at best; exactly-once needs idempotent logic or deduplication.

---

## ⚫ Interview Questions + Answers

Q1: What are the Celery components?
A1: Producer (your FastAPI app), broker (Redis/RabbitMQ, holds messages), worker (executes tasks), result backend (stores results/state), and optionally Beat (periodic scheduler) and Flower (monitoring UI).

Q2: Celery vs FastAPI `BackgroundTasks`?
A2: `BackgroundTasks` runs in the web process after the response: simple, but no persistence, retries, scheduling or separate scaling. Celery is a separate, durable, scalable system for heavy or critical work.

Q3: Why does Celery not natively support `async def` tasks?
A3: Celery workers use prefork/threads and run normal functions. Calling async code needs `asyncio.run()` inside the task or a library like ARQ/Dramatiq-async; do not share FastAPI's event loop with workers. (Celery's task functions themselves are sync.)

Q4: How do you make tasks reliable?
A4: Idempotent tasks, `autoretry_for` + `retry_backoff`, `acks_late=True`, time limits (`soft_time_limit`), dead-letter handling, and monitoring with Flower or Sentry.

Q5: Which broker should I choose?
A5: Redis is simple and good enough for most apps, but can lose messages in some failure modes. RabbitMQ gives stronger delivery guarantees, routing and priorities. Both are widely used.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Slow work: emails, PDFs, image/video processing, ML inference, data exports
- Calls to unreliable third-party APIs needing retries
- Scheduled jobs and fan-out workloads that must scale independently

❌ Avoid when:
- A 50 ms side effect: `BackgroundTasks` is enough
- You need real-time results in the same request (use async I/O instead)
- Tiny project where operating broker + workers costs more than it saves

---

## 📊 Visual Diagram
```
 Client ─POST─► FastAPI ──delay()──► Broker (Redis)
   ▲               │                     │ message
   │ 202 + task_id │                     ▼
   │               │               Celery worker(s) ── runs function
   │               │                     │ result
   └─GET /tasks/id─┴──── reads ◄── Result backend (Redis)

 Celery Beat ──(schedule)──► Broker ──► worker
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Broker | Message queue holding tasks | Tasks रखने वाली message queue |
| Worker | Process that runs tasks | Tasks चलाने वाला process |
| Result backend | Stores task results | Task results का भंडार |
| `delay()` | Send task to queue | Task को queue में भेजना |
| Idempotent | Safe to run many times | कई बार चलाना सुरक्षित |
| Celery Beat | Periodic task scheduler | समय-समय पर tasks का scheduler |

---

## ⚡ 3-Line Summary
English: Celery runs slow or important work in separate worker processes fed by a broker like Redis. FastAPI enqueues with `.delay()`, returns `202` + `task_id`, and clients poll for the result. Make tasks idempotent, pass IDs not objects, and use retries with backoff.
Hindi: Celery धीमा या महत्वपूर्ण काम Redis जैसे broker से जुड़े अलग worker processes में चलाता है। FastAPI `.delay()` से enqueue करता है, `202` + `task_id` लौटाता है, और clients result के लिए poll करते हैं। Tasks idempotent रखें, objects की जगह IDs दें, और backoff के साथ retries उपयोग करें।

---

## ➡️ Next Topic
**342. FastAPI + Docker** — package the API, worker, database and Redis into containers and run them together with Docker Compose.
