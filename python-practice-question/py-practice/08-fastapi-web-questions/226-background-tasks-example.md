---

# Q226. Background tasks example
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐

---

## ❓ Question
Build a `/signup` endpoint that returns immediately and sends a welcome email AFTER the response using `BackgroundTasks`. Show that tasks run in the order added and can also be queued from a dependency.

---

## 💡 Quick Concept (2 lines only)
`BackgroundTasks` runs a function after the response is sent, in the same process. Good for emails, audit logs, cache warm-up — not for heavy or must-not-lose jobs.
हिंदी: Response पहले चला जाता है, उसके बाद task चलता है — user को wait नहीं करना पड़ता।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from fastapi import FastAPI, BackgroundTasks  # app + background helper
from fastapi.testclient import TestClient  # in-process client

app = FastAPI()  # create app
log: list[str] = []  # fake "email outbox" to observe side effects

def send_email(to: str, body: str) -> None:  # plain sync function = runs in threadpool
    log.append(f"email to {to}: {body}")  # simulate slow work by recording

@app.post("/signup")  # endpoint
async def signup(email: str, tasks: BackgroundTasks) -> dict[str, str]:  # FastAPI injects tasks
    tasks.add_task(send_email, email, "welcome!")  # Step 1: schedule, do NOT call
    log.append("response being built")  # Step 2: this runs first
    return {"status": "created"}  # Step 3: response goes out, THEN task runs

# ============================================
# TEST CASES
# ============================================
with TestClient(app) as client:  # context manager waits for tasks
    r = client.post("/signup", params={"email": "a@x.com"})  # call endpoint
    print(r.json())  # Expected: {'status': 'created'}
    print(log)  # Expected: ['response being built', 'email to a@x.com: welcome!']
```

---

## 🔍 Why This Works (3 lines max)
`add_task(func, *args)` only registers the call; FastAPI runs it after the response. Sync functions go to a threadpool, `async def` ones run on the event loop. A dependency receives the SAME `BackgroundTasks` object, so tasks from both are merged in order.
हिंदी: `add_task` सिर्फ register करता है, चलाता response के बाद है। Sync function threadpool में चलता है।

---

## ⚡ Alternative Solution
```python
# (same file as above — reuses its imports/names)
# ---- Alternative: async task + task added from a dependency ----
import asyncio  # for sleep
from fastapi import Depends  # dependency injection

app2 = FastAPI()  # second app
audit: list[str] = []  # audit trail

async def audit_log(msg: str) -> None:  # async background function
    await asyncio.sleep(0.01)  # simulated I/O
    audit.append(msg)  # record

def track(tasks: BackgroundTasks) -> None:  # dependency receives SAME BackgroundTasks
    tasks.add_task(audit_log, "dependency ran")  # queue from dependency

@app2.get("/items", dependencies=[Depends(track)])  # dependency queues a task
async def items(tasks: BackgroundTasks) -> list[int]:  # route queues another
    tasks.add_task(audit_log, "route ran")  # second task
    return [1, 2, 3]  # response

with TestClient(app2) as c2:  # client
    print(c2.get("/items").json())  # Expected: [1, 2, 3]
    print(audit)  # Expected: ['dependency ran', 'route ran'] (run in order added)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: calling the function instead of passing it -> runs NOW and blocks the response
tasks.add_task(send_email(email, "welcome!"))   # executes immediately, passes None
# ✅ Correct: pass function and args separately
tasks.add_task(send_email, email, "welcome!")

# ❌ Wrong: using BackgroundTasks for long CPU jobs or critical work (lost if the server restarts)
# ✅ Correct: use a real queue (Celery / RQ / arq) for heavy or must-not-lose work
```

---

## 🎯 Interview Tip (1 line)
Say: "BackgroundTasks is fire-and-forget in-process; for retries, persistence or heavy work I'd use a task queue like Celery."

---

## 🔗 Related Questions
→ Q222 (dependencies) | Q216 (producer-consumer) | Q225 (middleware) | Q240 (lifespan)
