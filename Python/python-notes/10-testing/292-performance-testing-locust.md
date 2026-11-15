---

# 292. Performance Testing (locust)
# हिंदी में: Performance Testing (locust से load testing)

---

## 🔵 Simple Definition (English)
Performance testing checks how fast and how stable your API is under many users at the same time. `locust` is a Python tool where you write user behaviour as normal Python code, then it spawns thousands of fake users and reports requests per second, response times and failures.

## 🔵 सरल परिभाषा (Hindi)
Performance testing यह जाँचती है कि बहुत सारे users एक साथ आएँ तो आपका API कितना तेज़ और stable रहता है। `locust` एक Python tool है जिसमें आप user का behaviour सामान्य Python code में लिखते हैं, और वह हज़ारों नकली users बनाकर requests per second, response time और failures की report देता है।

---

## 🔴 Problem it Solves
Unit tests prove that one request works. They do not tell you what happens when 5,000 people open your app together. Many bugs show up only under load: slow database queries, exhausted connection pools, blocking code inside `async def`, memory leaks. Without load testing you find these on the sale day, in production.

## 🔴 यह क्यों बना? (Hindi)
Unit test सिर्फ यह बताता है कि एक request सही चलती है। जब 5,000 लोग एक साथ आते हैं तब क्या होगा, यह नहीं बताता। कई bugs सिर्फ load में दिखते हैं: धीमी database queries, खत्म हुआ connection pool, `async def` के अंदर blocking code, memory leak। Load test न हो तो ये bugs sale वाले दिन production में पता चलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Write a locustfile.py with a class that extends HttpUser
Step 2 → Mark actions with @task(weight); heavier weight = called more often
Step 3 → wait_time = between(a, b) makes each fake user "think" like a human
Step 4 → Run: locust -f locustfile.py --host http://localhost:8000
Step 5 → Locust spawns N users at a spawn rate (ramp up slowly, not instantly)
Step 6 → Each user runs tasks in a loop; Locust measures every request
Step 7 → Read RPS, median/95th/99th percentile latency and failure %
Step 8 → Fix the bottleneck, run again, compare numbers
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → locustfile.py लिखें, उसमें HttpUser को extend करने वाली class बनाएँ
Step 2 → @task(weight) से actions चिह्नित करें; ज़्यादा weight = ज़्यादा बार call
Step 3 → wait_time = between(a, b) से हर user इंसान की तरह रुककर चलता है
Step 4 → चलाएँ: locust -f locustfile.py --host http://localhost:8000
Step 5 → Locust spawn rate के हिसाब से N users बनाता है (धीरे-धीरे बढ़ाएँ)
Step 6 → हर user loop में tasks चलाता है; Locust हर request नापता है
Step 7 → RPS, median/95th/99th percentile latency और failure % पढ़ें
Step 8 → bottleneck ठीक करें, दोबारा चलाएँ, numbers की तुलना करें
```

---

## 🟡 Real World Example
Swiggy before a big cricket match: they simulate 50,000 users, where 60% browse the menu, 30% add to cart and 10% place an order. Locust tasks with weights 6, 3 and 1 copy that mix. They watch the 95th percentile latency of `/checkout`. If it crosses 800 ms they add database indexes or more workers before the match.

## 🟡 Real Example Hindi mein
Swiggy बड़े cricket match से पहले 50,000 users simulate करता है: 60% menu देखते हैं, 30% cart में डालते हैं और 10% order करते हैं। Locust के tasks में weight 6, 3 और 1 रखकर यही mix बनता है। वे `/checkout` की 95th percentile latency देखते हैं। अगर वह 800 ms से ऊपर जाए तो match से पहले database index या ज़्यादा workers जोड़ देते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: a tiny FastAPI app + a locustfile (verified with locust 2.47, Python 3.13)
# Install: pip install fastapi uvicorn locust

# ---------- app.py ----------
from fastapi import FastAPI  # web framework to test

app: FastAPI = FastAPI()  # create the app we will load test


@app.get("/health")  # simple endpoint, no database
def health() -> dict[str, str]:  # returns a small JSON
    return {"status": "ok"}  # response body


@app.get("/products/{pid}")  # endpoint with a path parameter
def product(pid: int) -> dict[str, int]:  # pid is validated as int
    return {"id": pid, "price": pid * 10}  # fake price calculation


# ---------- locustfile.py ----------
import random  # to pick random product ids
from locust import HttpUser, task, between  # locust building blocks


class ShopUser(HttpUser):  # one instance = one fake user
    wait_time = between(0.1, 0.3)  # each user waits 0.1-0.3 s between tasks

    @task(1)  # weight 1 -> called less often
    def health(self) -> None:  # task method
        self.client.get("/health")  # self.client is a requests-like session

    @task(3)  # weight 3 -> 3x more often than health
    def product(self) -> None:  # browse a product
        pid: int = random.randint(1, 100)  # random product id
        self.client.get(f"/products/{pid}", name="/products/[id]")  # group stats under one name

# Run server:  uvicorn app:app --port 8000
# Run test UI: locust -f locustfile.py --host http://127.0.0.1:8000
# Open http://localhost:8089 and choose users + spawn rate
```

## 💻 Code Example — Advanced
```python
# Production style: validate responses, login once, headless run for CI
import random  # random ids
from locust import HttpUser, task, between, events  # events for pass/fail hooks


class ShopUser(HttpUser):  # a realistic user
    wait_time = between(0.1, 0.3)  # think time

    def on_start(self) -> None:  # runs once per user when it starts
        # login here if your API needs a token, e.g.
        # token = self.client.post("/login", json={...}).json()["token"]
        # self.client.headers["Authorization"] = f"Bearer {token}"
        pass  # no auth in this demo app

    @task(3)  # most common action
    def product(self) -> None:
        pid: int = random.randint(1, 100)  # random product
        # catch_response lets US decide whether the request passed or failed
        with self.client.get(
            f"/products/{pid}", name="/products/[id]", catch_response=True
        ) as resp:
            if resp.status_code != 200:  # HTTP level check
                resp.failure(f"status {resp.status_code}")  # mark as failure
            elif resp.json()["id"] != pid:  # body level check
                resp.failure("wrong product returned")  # mark as failure
            else:
                resp.success()  # explicitly mark success


@events.quitting.add_listener  # runs when the test is ending
def fail_ci_if_slow(environment, **kwargs) -> None:  # environment holds stats
    stats = environment.stats.total  # aggregated stats of all requests
    if stats.fail_ratio > 0.01:  # more than 1% failures
        environment.process_exit_code = 1  # CI job fails
    elif stats.get_response_time_percentile(0.95) > 500:  # p95 above 500 ms
        environment.process_exit_code = 1  # CI job fails

# Headless (no browser) run used in CI:
# locust -f locustfile.py --headless -u 10 -r 5 -t 6s --host http://127.0.0.1:8000 --only-summary
#
# Real summary from this exact run on my machine (numbers vary per run):
# Type  Name              # reqs  # fails |  Avg  Min  Max  Med | req/s
# GET   /health               86  0(0.00%) |    2    0   38    2 | 14.76
# GET   /products/[id]       184  0(0.00%) |    2    0   21    2 | 31.59
#       Aggregated           270  0(0.00%) |    2    0   38    2 | 46.35
# Note: /products is 184 vs 86 for /health: weight 3 vs 1 gives roughly 2-3x traffic
```

---

## 🟠 JavaScript vs Python Comparison
In the JavaScript world the popular load tools are `k6` (scripts in JS) and `autocannon` (Node CLI). Locust gives you the same power but with plain Python classes, so you can reuse your Python models and helpers.

```python
# Python (locust): behaviour is a class with weighted tasks
class ShopUser(HttpUser):
    wait_time = between(1, 3)
    @task(3)
    def browse(self) -> None:
        self.client.get("/products")
```
```javascript
// JavaScript (k6): behaviour is an exported default function
import http from 'k6/http';
import { sleep } from 'k6';
export const options = { vus: 10, duration: '6s' };
export default function () {
  http.get('http://localhost:8000/products');
  sleep(1);
}
```

Key differences: k6 runs your JS in a Go runtime (not Node), so npm packages do not work. Locust runs real Python, so you can import any library. Locust uses greenlets (gevent) so one process can simulate thousands of users.

---

## 🟠 FastAPI Connection
FastAPI is often chosen for speed, and locust is how you prove it. Typical findings: a `def` endpoint doing slow I/O saturates the threadpool, or an `async def` endpoint calling a blocking library freezes the event loop (see topic 298). Always run FastAPI with `uvicorn` or `gunicorn -k uvicorn.workers.UvicornWorker` on the target machine, not with `--reload`.

```python
# FastAPI: endpoints worth load testing (needs: pip install fastapi)
import asyncio  # for the non-blocking sleep
from fastapi import FastAPI  # framework

app: FastAPI = FastAPI()  # app instance


@app.get("/slow-db")  # pretend this calls a database
async def slow_db() -> dict[str, str]:
    await asyncio.sleep(0.05)  # simulates a 50 ms async query
    return {"rows": "many"}  # locust will show ~50 ms median here
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Testing against your laptop dev server with `--reload`
✅ Correct: Test a production-like setup (multiple workers, no reload, similar DB).

```python
# Wrong: uvicorn app:app --reload   (single process, file watcher)
# Right: uvicorn app:app --workers 4  (or gunicorn with uvicorn workers)
```

❌ Mistake 2: Every URL gets its own stat row (`/products/1`, `/products/2`, ...)
✅ Correct: pass `name="/products/[id]"` so all of them are grouped.

```python
# Wrong
self.client.get(f"/products/{pid}")  # 100 separate rows in the report
# Right
self.client.get(f"/products/{pid}", name="/products/[id]")  # one row
```

❌ Mistake 3: Only checking the status code, or ramping 10,000 users in one second
✅ Correct: Validate the body with `catch_response=True` and ramp slowly (`-r 10`). Also remember the load generator itself can be the bottleneck: run it on a different machine.

---

## 🧠 Tricky Interview Question

**Q**: Your locust test shows 200 ms median but 4 seconds at the 99th percentile. Average is only 300 ms. What does this mean and why is average a bad metric?

```python
# Think about this distribution of 100 requests:
latencies_ms: list[int] = [200] * 98 + [4000, 4000]  # 2 very slow requests
avg: float = sum(latencies_ms) / len(latencies_ms)  # mean
median: float = sorted(latencies_ms)[len(latencies_ms) // 2]  # middle value
print(round(avg), median)  # average vs median
```

**Answer**:
```
276 200
```
The average (276 ms) hides the 2% of users who wait 4 seconds. Percentiles (p95, p99) show the "tail". Tail latency is usually caused by a lock, a cold cache, garbage collection or one slow query. In an SLA you promise p95/p99, not the average.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between load, stress, spike and soak testing?
A1: Load = expected traffic. Stress = beyond capacity to find the breaking point. Spike = sudden jump in users. Soak = moderate load for many hours to find memory leaks.

Q2: Why does locust use gevent?
A2: Gevent greenlets are cheap, so one process can simulate thousands of users that mostly wait for I/O. For more CPU use `--processes` or distributed mode (`--master` / `--worker`).

Q3: What does `@task(3)` mean?
A3: The task has weight 3. If another task has weight 1, the first is chosen about three times as often.

Q4: Which metrics matter most?
A4: RPS (throughput), p95/p99 latency, failure rate, and server side CPU, memory and DB connections.

Q5: Can you run locust in CI?
A5: Yes. Use `--headless -u -r -t` and set `environment.process_exit_code` in a quitting listener so the pipeline fails when thresholds are broken.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Before launch, a sale or any expected traffic spike
- Comparing two versions (e.g. sync vs async endpoint, with or without cache)
- Finding the maximum users one instance can handle

❌ Avoid when:
- Testing correctness (use pytest instead)
- Hitting a third-party API you do not own (you may get banned or billed)
- Running against production without agreement (you can take the site down)

---

## 📊 Visual Diagram

```
 locustfile.py
      │  spawn N users (rate r)
      ▼
 ┌─────────┐  ┌─────────┐  ┌─────────┐
 │ User 1  │  │ User 2  │  │ User N  │   each loops: task → wait → task
 └────┬────┘  └────┬────┘  └────┬────┘
      └────────────┼────────────┘
                   ▼
          FastAPI (uvicorn workers)
                   │
                   ▼
        DB / cache / external APIs
                   │
   Stats: RPS, p50/p95/p99, failures ──► report / CI gate
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Load test | Test with expected traffic | अपेक्षित traffic के साथ test |
| RPS | Requests per second | प्रति सेकंड requests |
| Percentile (p95) | 95% requests were faster than this | 95% requests इससे तेज़ थीं |
| Spawn rate | New users per second | प्रति सेकंड नए users |
| Think time | Pause between user actions | users के actions के बीच ठहराव |
| Tail latency | Slowest few percent of requests | सबसे धीमी कुछ % requests |

---

## ⚡ 3-Line Summary
English: Locust lets you describe user behaviour in Python and replay it with thousands of fake users. Judge the result by p95/p99 latency, RPS and failure rate, not the average. Use `--headless` in CI and test a production-like setup.
Hindi: Locust में आप user का behaviour Python में लिखते हैं और हज़ारों नकली users से चलाते हैं। नतीजा average से नहीं, p95/p99 latency, RPS और failure rate से जाँचें। CI में `--headless` इस्तेमाल करें और production जैसा setup test करें।

---

## ➡️ Next Topic
**293. Test Organization Best Practices** — folder layout, naming, markers and how to keep a big test suite clean.
