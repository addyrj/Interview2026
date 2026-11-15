---

# 485. Build Background Job System
# हिंदी में: Background Job System बनाना (queue + workers + retry)

Full runnable solution: [main.py](main.py) (asyncio queue, workers, retries with backoff, asserts).

---

## 🔵 Simple Definition (English)
A background job system accepts work now, returns immediately, and lets worker tasks run it later from a queue. Failed jobs are retried a few times, and every job has a status you can look up.

## 🔵 सरल परिभाषा (Hindi)
Background job system काम अभी ले लेता है, तुरंत जवाब दे देता है, और असली काम workers बाद में queue से उठाकर करते हैं। फेल हुए jobs कुछ बार retry होते हैं और हर job का status देखा जा सकता है।

---

## 🔴 Problem it Solves
Sending an email, making a PDF or calling a slow API inside the request makes users wait and can time out. If the process crashes midway the work is lost. A queue separates "accept request" from "do work", smooths traffic spikes and allows retries.

## 🔴 यह क्यों बना? (Hindi)
Request के अंदर ही email भेजना, PDF बनाना या धीमी API call करना user को इंतज़ार कराता है और timeout हो सकता है। बीच में process crash हो तो काम खो जाता है। Queue "request लेना" और "काम करना" अलग कर देती है, traffic spike संभालती है और retry संभव बनाती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → enqueue(name, payload) creates Job(status="queued") and puts it in asyncio.Queue
Step 2 → API returns job.id immediately (HTTP 202)
Step 3 → Worker task: job = await queue.get(); status="running"
Step 4 → Run handlers[job.name](payload)
Step 5 → Success -> "done". Error -> if attempts <= max_retries: sleep backoff, re-queue
Step 6 → Too many errors -> "failed" and error text saved
Step 7 → queue.task_done(); queue.join() returns when all done
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → enqueue() Job(status="queued") बनाकर asyncio.Queue में डालता है
Step 2 → API तुरंत job.id लौटा देती है (HTTP 202)
Step 3 → Worker await queue.get() से job लेता है, status="running"
Step 4 → handlers[job.name](payload) चलता है
Step 5 → सफल तो "done"; error हो और retries बाकी हों तो backoff के बाद दोबारा queue में
Step 6 → retries खत्म तो "failed" और error सेव
Step 7 → task_done(); सब खत्म होने पर queue.join() वापस आता है
```

---

## 🟡 Real World Example
Zomato order placed: the API saves the order, enqueues "send_sms", "notify_restaurant" and "update_analytics" and answers in 50 ms. Workers run them; the SMS provider failing twice is fixed by retry. Production uses Celery, RQ, Arq or SQS so jobs survive restarts.

## 🟡 Real Example Hindi mein
Zomato में order place होते ही API order save करके "send_sms", "notify_restaurant", "update_analytics" jobs queue में डालती है और 50 ms में जवाब देती है। Workers इन्हें चलाते हैं; SMS provider दो बार फेल हो तो retry से ठीक हो जाता है। Production में Celery, RQ, Arq या SQS इस्तेमाल होते हैं ताकि restart पर jobs न खोएँ।

---

## 💻 Code Example — Basic
```python
# Smallest producer/consumer with asyncio.Queue
import asyncio  # event loop and queue

async def worker(q: asyncio.Queue[int]) -> None:  # consumer
    while True:  # run forever
        n = await q.get()  # wait for a job
        print("processed", n * 2)  # do the work
        q.task_done()  # tell the queue this job is finished

async def main() -> None:
    q: asyncio.Queue[int] = asyncio.Queue()  # the job queue
    task = asyncio.create_task(worker(q))  # start one worker
    for n in (1, 2, 3):  # producer side
        q.put_nowait(n)  # add jobs
    await q.join()  # wait until all are processed
    task.cancel()  # stop the infinite worker

asyncio.run(main())  # run the program
# Output:
# processed 2
# processed 4
# processed 6
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: retry with exponential backoff
async def _worker(self) -> None:
    while True:
        job = await self.queue.get()  # block until a job arrives
        job.status = "running"
        job.attempts += 1
        try:
            job.result = await self.handlers[job.name](job.payload)
            job.status = "done"
        except Exception as exc:
            if job.attempts <= self.max_retries:
                job.status = "queued"
                await asyncio.sleep(0.01 * 2 ** job.attempts)  # backoff 20ms, 40ms...
                self.queue.put_nowait(job)  # retry
            else:
                job.status, job.error = "failed", repr(exc)
        finally:
            self.queue.task_done()  # always, or join() hangs
```
Real output of `python main.py` (job ids differ per run, not printed):
```
square done 1 49 None
flaky done 3 ok after retries None
broken failed 3 None ValueError('always fails')
all ok
```

---

## 🟠 JavaScript vs Python Comparison
JS has BullMQ (Redis) and `queueMicrotask`; Python has Celery/RQ/Arq plus the built-in `asyncio.Queue`. Retry/backoff logic is the same idea.

```python
# Python way
job = queue.enqueue("send_email", to="a@b.com")  # returns at once
```
```javascript
// JavaScript way (BullMQ)
const job = await queue.add("send_email", { to: "a@b.com" }); // returns at once
```

---

## 🟠 FastAPI Connection
FastAPI has built-in `BackgroundTasks` for small jobs that run after the response, in the same process. For durable work use a queue and return `202 Accepted` with a job id.

```python
from fastapi import BackgroundTasks, FastAPI  # tools

app = FastAPI()  # app

def send_email(to: str) -> None:  # slow work
    print("sending to", to)  # pretend

@app.post("/signup", status_code=202)  # 202 = accepted, not finished
def signup(email: str, bg: BackgroundTasks) -> dict[str, str]:
    bg.add_task(send_email, email)  # runs after the response is sent
    return {"status": "queued"}  # user does not wait
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `task_done()` on error paths, so `queue.join()` never returns.
✅ Correct: call it in `finally`.

❌ Mistake 2: Retrying immediately forever; this hammers a failing service.
✅ Correct: cap retries, use exponential backoff plus jitter.

```python
# Wrong
while True:
    try: do(); break
    except Exception: pass
# Right
await asyncio.sleep(base * 2 ** attempt)  # and stop after max_retries
```

❌ Mistake 3: In-memory queue for money-critical work. A crash loses everything.
✅ Correct: use a persistent broker and make jobs idempotent.

---

## 🧠 Tricky Interview Question
```python
import asyncio
async def main():
    q = asyncio.Queue()
    q.put_nowait(1)
    await q.join()
    print("done")
asyncio.run(main())
```
Answer: It hangs forever. `join()` waits until `task_done()` has been called once per item, and no worker ever consumed the item. Add a consumer that calls `task_done()`.

---

## ⚫ Interview Questions + Answers

Q1: BackgroundTasks vs Celery?
A1: BackgroundTasks run in the web process after the response: simple but lost on crash, no retries. Celery uses a broker and separate workers: durable, retries, scheduling.

Q2: What does idempotent mean for jobs?
A2: Running it twice gives the same final result (e.g. dedupe on payment id), because retries and redelivery can run a job more than once.

Q3: Why exponential backoff?
A3: Gives a failing dependency time to recover and avoids a retry storm; add jitter so clients do not retry in sync.

Q4: At-most-once vs at-least-once?
A4: At-most-once may lose jobs, at-least-once may duplicate them. Most queues are at-least-once, so design idempotent handlers.

Q5: How to stop workers gracefully?
A5: `await queue.join()` for pending jobs, then cancel worker tasks and `gather(..., return_exceptions=True)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Work is slow, can fail, or can happen after the response (email, reports, webhooks)

❌ Avoid when:
- The user needs the result in the same response
- Work is tiny; the queue adds more complexity than value

---

## 📊 Visual Diagram
```
 API ──enqueue──► [ job | job | job ] ◄── worker 1
  │  (202 + id)        Queue          ◄── worker 2
  │                                       │ success -> done
  └── GET /jobs/{id} ◄── jobs dict ◄──────┤ error -> backoff -> re-queue
                                          └ too many -> failed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Queue | FIFO list of pending work | काम की कतार |
| Worker | Task that processes jobs | काम करने वाला task |
| Retry | Run a failed job again | फेल जॉब दोबारा चलाना |
| Backoff | Growing wait between retries | retries के बीच बढ़ता इंतज़ार |
| Idempotent | Safe to run twice | दो बार चलाना सुरक्षित |

---

## ⚡ 3-Line Summary
English: Accept work fast, run it later through a queue and workers.
Retry failures with backoff and keep a status per job.
Use a persistent broker (Celery/Arq/SQS) in production.
Hindi: काम जल्दी स्वीकारो और बाद में queue व workers से चलाओ।
फेल होने पर backoff के साथ retry करो और हर job का status रखो।
Production में persistent broker (Celery/Arq/SQS) इस्तेमाल करो।

---

## ➡️ Next Topic
486. Build Caching Layer: jobs reduce waiting; caching avoids repeating expensive work at all.

---
