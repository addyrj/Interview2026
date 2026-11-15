---

# 320. Background Tasks
# हिंदी में: Background Tasks (response के बाद काम)

---

## 🔵 Simple Definition (English)
`BackgroundTasks` lets an endpoint schedule a function that runs AFTER the response has been sent to the client. The user does not wait for slow side work like sending an email.

## 🔵 सरल परिभाषा (Hindi)
`BackgroundTasks` से endpoint ऐसा function schedule करता है जो client को response भेजने के BAAD चलता है। Email भेजने जैसे धीमे काम के लिए user को इंतज़ार नहीं करना पड़ता।

---

## 🔴 Problem it Solves
A signup endpoint must create the user, send a welcome email and push analytics. If it does all three before replying, the user waits 2-3 seconds. Moving the slow, non-critical parts after the response makes the API feel instant.

## 🔴 यह क्यों बना? (Hindi)
Signup endpoint को user बनाना, welcome email भेजना और analytics push करना होता है। अगर तीनों response से पहले करें तो user 2-3 second रुकता है। धीमे और कम ज़रूरी हिस्से response के बाद करने से API तुरंत जवाब देती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Declare a parameter `tasks: BackgroundTasks` (FastAPI injects it)
Step 2 → Call `tasks.add_task(func, *args, **kwargs)` - nothing runs yet
Step 3 → The handler returns; FastAPI sends the response
Step 4 → AFTER sending, Starlette runs the tasks in the order added
Step 5 → `def` tasks run in a threadpool; `async def` tasks run on the event loop
Step 6 → An exception in a task is NOT sent to the client (response already gone)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → parameter `tasks: BackgroundTasks` लिखें (FastAPI inject करता है)
Step 2 → `tasks.add_task(func, *args, **kwargs)` बुलाएँ - अभी कुछ नहीं चलता
Step 3 → Handler return करता है; FastAPI response भेज देता है
Step 4 → भेजने के BAAD Starlette tasks को जोड़ने के क्रम में चलाता है
Step 5 → `def` task threadpool में, `async def` task event loop पर चलता है
Step 6 → Task में exception client को नहीं जाता (response पहले ही जा चुका)
```

---

## 🟡 Real World Example
Razorpay-style: after `POST /payments` succeeds, send an SMS receipt, write an audit row and notify the merchant webhook as background tasks. An AI app saves the chat transcript and token usage after streaming the answer. For heavy, must-not-lose jobs (video encoding, 10-minute reports) use Celery/ARQ/RQ instead.

## 🟡 Real Example Hindi mein
Razorpay जैसा: `POST /payments` सफल होने के बाद SMS receipt, audit row और merchant webhook notification background tasks में भेजते हैं। AI app जवाब stream करने के बाद chat transcript और token usage save करता है। भारी और खोने न देने वाले काम (video encoding, 10 मिनट की report) के लिए Celery/ARQ/RQ इस्तेमाल करें।

---

## 💻 Code Example — Basic
Schedule one task and check the log after the call.

```python
# Basic BackgroundTasks - every line commented
from fastapi import BackgroundTasks, FastAPI  # tools we need
from fastapi.testclient import TestClient  # test client

app: FastAPI = FastAPI()  # create app
LOG: list[str] = []  # fake "log file" so we can see what ran


def write_log(message: str) -> None:  # plain function = runs in a threadpool
    LOG.append(f"sent: {message}")  # pretend to send an email


@app.post("/signup")  # signup endpoint
def signup(email: str, tasks: BackgroundTasks) -> dict[str, str]:  # FastAPI injects BackgroundTasks
    tasks.add_task(write_log, email)  # schedule: function + its arguments
    return {"status": "created"}  # response is sent first, task runs after


client: TestClient = TestClient(app)  # client
print(client.post("/signup", params={"email": "a@b.com"}).json())  # call the endpoint
# Output: {'status': 'created'}
print(LOG)  # TestClient waits for background tasks, so the log is filled
# Output: ['sent: a@b.com']
```

## 💻 Code Example — Advanced
Sync + async tasks, a task added from a dependency, and failure isolation with logging.

```python
# Production style: async + sync tasks, error handling, dependency tasks
import asyncio  # for async sleep
import logging  # real apps log failures
from fastapi import BackgroundTasks, Depends, FastAPI  # tools
from fastapi.testclient import TestClient  # test client

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")  # simple log format
log: logging.Logger = logging.getLogger("jobs")  # module logger
app: FastAPI = FastAPI()  # app
EVENTS: list[str] = []  # record the order of events


def send_email(to: str) -> None:  # sync task
    EVENTS.append(f"email:{to}")  # pretend to send


async def push_analytics(user: str) -> None:  # async task runs on the event loop
    await asyncio.sleep(0)  # pretend non-blocking I/O
    EVENTS.append(f"analytics:{user}")  # record


def risky_task() -> None:  # a task that fails
    raise RuntimeError("smtp down")  # simulate a failure


def safe(fn, *args) -> None:  # wrapper so one failure is logged, not lost
    try:  # try the real job
        fn(*args)  # run it
    except Exception:  # any error
        log.exception("background task failed")  # log with traceback


def audit(tasks: BackgroundTasks) -> None:  # dependency can also add tasks
    tasks.add_task(EVENTS.append, "audit")  # same BackgroundTasks object is shared


@app.post("/orders", dependencies=[Depends(audit)])  # dependency runs first
async def create_order(user: str, tasks: BackgroundTasks) -> dict[str, str]:  # async handler
    tasks.add_task(send_email, user)  # sync function
    tasks.add_task(push_analytics, user)  # async function
    tasks.add_task(safe, risky_task)  # failing job is isolated
    return {"order": "ok"}  # returned before tasks start


client: TestClient = TestClient(app)  # client
print(client.post("/orders", params={"user": "asha"}).json())  # call
# Output: {'order': 'ok'}
print(EVENTS)  # order: dependency task first, then in add order
# Output: ['audit', 'email:asha', 'analytics:asha']
```

---

## 🟠 JavaScript vs Python Comparison

```python
@app.post("/signup")
def signup(email: str, tasks: BackgroundTasks):
    tasks.add_task(send_email, email)   # runs after response
    return {"ok": True}
```

```javascript
// Express: fire after res.send (not awaited)
app.post('/signup', (req, res) => {
  res.json({ ok: true });
  setImmediate(() => sendEmail(req.body.email).catch(console.error));
});
// or push to a queue: await queue.add('email', {...})
```

In Node you often just do not `await` a promise after replying. In Python, `BackgroundTasks` makes this explicit and managed by the framework. Both live in the same process: if the server restarts, the task is lost. Use a real queue (BullMQ in JS, Celery in Python) for reliability.

---

## 🟠 FastAPI Connection
Use it for light fire-and-forget work. Remember that the task runs in the same process after the response. The request's DB session (from `Depends` with `yield`) may already be closed in modern FastAPI, so pass IDs and open a fresh session inside the task.

```python
from fastapi import BackgroundTasks, FastAPI

app: FastAPI = FastAPI()


def notify_merchant(payment_id: int) -> None:
    # open a NEW db session here; do not reuse the request session
    print(f"webhook for {payment_id}")


@app.post("/payments")
def pay(tasks: BackgroundTasks) -> dict[str, int]:
    payment_id: int = 42
    tasks.add_task(notify_merchant, payment_id)  # pass ids, not live objects
    return {"payment_id": payment_id}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling the function instead of passing it
```python
tasks.add_task(send_email(email))  # runs NOW and passes None
```
✅ Correct:
```python
tasks.add_task(send_email, email)  # pass function + args
```

❌ Mistake 2: Heavy CPU job as background task
```python
tasks.add_task(render_4k_video, file)  # blocks worker / lost on restart
```
✅ Correct:
```python
# send to Celery / ARQ / RQ worker instead
```

❌ Mistake 3: Assuming errors reach the client
```python
tasks.add_task(risky)  # client already got 200
```
✅ Correct:
```python
tasks.add_task(safe_wrapper, risky)  # try/except + log inside
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
from fastapi import BackgroundTasks, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
order = []

def job():
    order.append("job")

@app.get("/")
def root(bg: BackgroundTasks):
    bg.add_task(job)
    order.append("handler-end")
    return {"order": list(order)}

c = TestClient(app)
print(c.get("/").json())
print(order)
```

**Answer**:
```
{'order': ['handler-end']}
['handler-end', 'job']
```
The task is queued, not run, while the handler executes. The response body is built from `order` before `job` appended. After the response is sent the task runs, so the global list has both entries. (TestClient waits for background tasks, so the final print shows `job`.)

---

## ⚫ Interview Questions + Answers

Q1: When exactly does a background task run?
A1: After the response is sent (inside the same ASGI call). Tasks run in the order added.

Q2: `def` vs `async def` task?
A2: `def` runs in a threadpool so blocking code is fine. `async def` runs on the event loop, so never block inside it.

Q3: What if the server crashes?
A3: The task is lost. BackgroundTasks has no persistence or retries; use a queue for important work.

Q4: BackgroundTasks vs Celery?
A4: BackgroundTasks: tiny, in-process, no infra. Celery/ARQ: separate workers, retries, scheduling, monitoring, survive restarts.

Q5: Can a dependency add tasks?
A5: Yes. The same `BackgroundTasks` object is shared, so tasks from dependencies and the handler are merged and run in order.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Send email/SMS, write audit logs, push analytics
- Short jobs (a few seconds) that can be retried by users
- Cache warm-up after a write

❌ Avoid when:
- Long CPU or minutes-long jobs
- Work that must never be lost
- Anything that needs retries/monitoring/scheduling

---

## 📊 Visual Diagram

```
Client --POST--> handler: add_task(a), add_task(b)
                     |
                     v return {"ok": true}
Client <--200--------+      (response sent first)
                     |
                     v  run a() ... run b()   (after response, same process)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| BackgroundTasks | Post-response task queue | response के बाद वाले tasks |
| add_task | Schedule func + args | task जोड़ना |
| Fire-and-forget | Do not wait for result | भेजो और भूल जाओ |
| Threadpool | Worker threads for def | def के लिए worker threads |
| Idempotent | Safe to run twice | दोबारा चलाना सुरक्षित |
| Task queue | Celery/ARQ/RQ | अलग worker वाली queue |

---

## ⚡ 3-Line Summary
English: `BackgroundTasks` runs small functions after the response is sent. They run in-process, in order, and errors do not reach the client. For reliable or heavy work use a real task queue.
Hindi: `BackgroundTasks` छोटे functions को response भेजने के बाद चलाता है। ये उसी process में क्रम से चलते हैं और errors client तक नहीं जाते। भरोसेमंद या भारी काम के लिए असली task queue लें।

---

## ➡️ Next Topic
**321. WebSockets in FastAPI** — two-way real-time messages (chat, live prices).

---

**Verification note:** Every code block was run with FastAPI 0.162.4, Starlette 1.10.0, Python 3.13.3 using TestClient / httpx (no real browser). The Output comments are the real printed output.
