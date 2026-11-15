---

# 491. Async Concurrent Requests
# हिंदी में: Async से एक साथ कई Requests (gather + Semaphore)

Full runnable solution: [main.py](main.py) (httpx with an offline `MockTransport`, so it runs without internet).

---

## 🔵 Simple Definition (English)
Async concurrency lets one thread start many network requests and wait for all of them together, so total time is about the slowest request instead of the sum of all.

## 🔵 सरल परिभाषा (Hindi)
Async concurrency में एक thread कई network requests एक साथ शुरू करता है और सबका इंतज़ार साथ में करता है, इसलिए कुल समय सब का जोड़ नहीं बल्कि सबसे धीमी request के आसपास होता है।

---

## 🔴 Problem it Solves
Calling 10 APIs one after another, each 100 ms, takes 1 second; the CPU mostly sleeps waiting for the network. Concurrency overlaps the waiting. But unlimited concurrency can overload the target or hit rate limits, so you also need a limit and timeouts.

## 🔴 यह क्यों बना? (Hindi)
10 APIs को एक के बाद एक बुलाना (हर एक 100 ms) 1 सेकंड लेता है, जबकि CPU ज़्यादातर network का इंतज़ार करता रहता है। Concurrency इंतज़ार को overlap कर देती है। पर असीमित concurrency target को overload या rate limit में फँसा सकती है, इसलिए सीमा और timeout भी चाहिए।

---

## 🟢 How it Works — Step by Step

```
Step 1 → async def fetch(): await client.get(url) yields control while waiting
Step 2 → asyncio.gather(*coros) schedules all as tasks on the event loop
Step 3 → Semaphore(5): only 5 inside the `async with` at once
Step 4 → return_exceptions=True: failures are returned, not raised
Step 5 → wait_for / timeout stops slow calls
Step 6 → Total time ≈ ceil(N / limit) x slowest call
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → async def fetch(): await client.get(url) इंतज़ार के दौरान control छोड़ता है
Step 2 → asyncio.gather(*coros) सबको event loop पर tasks बनाकर चलाता है
Step 3 → Semaphore(5): एक समय में सिर्फ़ 5 अंदर
Step 4 → return_exceptions=True: failures raise नहीं होते, लौटाए जाते हैं
Step 5 → wait_for / timeout धीमी calls रोकता है
Step 6 → कुल समय ≈ ceil(N / limit) x सबसे धीमी call
```

---

## 🟡 Real World Example
A travel aggregator queries 8 airline APIs for one search and shows results in about the slowest one's time. A dashboard calls user, orders and wallet services together. An LLM app embeds 100 chunks with at most 10 requests in flight to respect the provider limit.

## 🟡 Real Example Hindi mein
Travel aggregator एक search के लिए 8 airline APIs बुलाता है और सबसे धीमी API जितने समय में results दिखा देता है। Dashboard user, orders और wallet services एक साथ बुलाता है। LLM app 100 chunks embed करते समय provider limit के लिए एक समय में 10 requests रखता है।

---

## 💻 Code Example — Basic
```python
# Sequential vs concurrent with asyncio.sleep as fake network
import asyncio  # event loop
import time  # timing

async def call(n: int) -> int:  # fake API call
    await asyncio.sleep(0.1)  # waiting for network
    return n * 2  # the "response"

async def main() -> None:
    t0 = time.perf_counter()  # start timer
    results = await asyncio.gather(*(call(n) for n in range(5)))  # all at once
    print(results, round(time.perf_counter() - t0, 1))  # list and seconds

asyncio.run(main())  # start the loop
# Output: [0, 2, 4, 6, 8] 0.1
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: bounded concurrency + per-task errors + 3.11+ TaskGroup
async def fetch(client: httpx.AsyncClient, sem: asyncio.Semaphore, n: int) -> dict:
    async with sem:  # at most 5 in flight
        await asyncio.sleep(0.1)  # pretend latency
        r = await client.get(f"http://api.test/{n}")
        r.raise_for_status()  # 500 -> HTTPStatusError
        return r.json()

results = await asyncio.gather(*(fetch(client, sem, n) for n in range(1, 11)),
                               return_exceptions=True)  # one failure does not cancel the rest
async with asyncio.TaskGroup() as tg:  # structured concurrency (3.11+)
    t1 = tg.create_task(asyncio.sleep(0.01, "a"))
```
Real output of `python main.py` (10 tasks, 5 at a time = 2 batches of ~0.1 s; timings vary):
```
9 ok; 1 failed: HTTPStatusError
elapsed ~ 0.2 s (sequential would be ~1.0s)
timeout handled
a b
all ok
```

---

## 🟠 JavaScript vs Python Comparison
`Promise.all` fails fast; `Promise.allSettled` collects everything. Python's `gather` fails fast by default and `return_exceptions=True` is like `allSettled`. JS has no built-in semaphore (use `p-limit`).

```python
results = await asyncio.gather(*tasks, return_exceptions=True)
```
```javascript
const results = await Promise.allSettled(promises);
```

---

## 🟠 FastAPI Connection
In an `async def` endpoint, fan-out to other services with `httpx.AsyncClient` and `gather`. Create one shared client at startup (lifespan) to reuse connection pools; never use blocking `requests` inside `async def`.

```python
@app.get("/dashboard")
async def dashboard() -> dict:
    async with httpx.AsyncClient(timeout=3) as c:  # production: shared client
        a, b = await asyncio.gather(c.get("http://users/1"), c.get("http://orders/1"))
    return {"user": a.json(), "orders": b.json()}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `await` inside a loop, which runs sequentially.
✅ Correct: build coroutines, then `gather`.

```python
# Wrong: 1.0 s
for n in range(10): await call(n)
# Right: ~0.1 s
await asyncio.gather(*(call(n) for n in range(10)))
```

❌ Mistake 2: Blocking calls (`requests.get`, `time.sleep`) in async code freeze the loop.
✅ Correct: `httpx.AsyncClient`, `asyncio.sleep`, or `asyncio.to_thread`.

❌ Mistake 3: No timeout and no concurrency limit.
✅ Correct: client timeout plus a Semaphore.

---

## 🧠 Tricky Interview Question
```python
async def main():
    await asyncio.gather(asyncio.sleep(1), asyncio.sleep(1), asyncio.sleep(1))
```
How long does it take?

Answer: about 1 second, not 3. All three sleeps wait at the same time. But if one raised an exception, `gather` (without `return_exceptions`) re-raises it at once while the others keep running in the background.

---

## ⚫ Interview Questions + Answers

Q1: gather vs TaskGroup?
A1: TaskGroup (3.11+) cancels siblings when one fails and groups errors in `ExceptionGroup`; gather is older and looser.

Q2: Is asyncio parallel?
A2: No, it is concurrent on one thread. Great for I/O; CPU work needs processes.

Q3: Why Semaphore?
A3: To cap in-flight requests and respect rate limits.

Q4: How to run blocking code in async app?
A4: `await asyncio.to_thread(func, ...)` or a threadpool.

Q5: What does `asyncio.TimeoutError` equal now?
A5: Since 3.11 it is an alias of built-in `TimeoutError`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Many independent I/O calls (HTTP, DB with async driver)

❌ Avoid when:
- CPU-bound work (use multiprocessing)
- Calls depend on each other's results

---

## 📊 Visual Diagram
```
 Sequential: |--A--||--B--||--C--|      total = A+B+C
 Concurrent: |--A--|
             |--B--|                   total = max(A,B,C)
             |--C--|
 Semaphore(2): A,B run; C waits until one finishes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Coroutine | async def function call | async function का object |
| Event loop | Scheduler of tasks | tasks चलाने वाला scheduler |
| gather | Run many, wait for all | सब चलाओ, सबका इंतज़ार |
| Semaphore | Limit concurrency | एक साथ चलने की सीमा |
| Timeout | Max wait time | अधिकतम इंतज़ार |

---

## ⚡ 3-Line Summary
English: gather overlaps waiting so total time is the slowest call.
Add a Semaphore and timeouts to stay safe.
Use return_exceptions=True or TaskGroup to handle failures.
Hindi: gather इंतज़ार को overlap करता है, कुल समय सबसे धीमी call जितना।
सुरक्षा के लिए Semaphore और timeout लगाओ।
failures संभालने के लिए return_exceptions=True या TaskGroup इस्तेमाल करो।

---

## ➡️ Next Topic
492. Multiprocessing Example: async fixes waiting; for CPU-heavy work we need real parallelism across processes.

---
