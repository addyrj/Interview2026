---

# 493. Threading Example
# हिंदी में: Threading का Example (I/O-bound, Lock, Queue)

Full runnable solution: [main.py](main.py) (ThreadPoolExecutor, Lock-protected counter, producer/consumer with Queue).

---

## 🔵 Simple Definition (English)
Threads run several flows of work inside one process and share its memory. While one thread waits for disk or network I/O (the GIL is released), another can run.

## 🔵 सरल परिभाषा (Hindi)
Threads एक ही process के अंदर कई काम के flow चलाते हैं और memory share करते हैं। जब एक thread disk या network I/O का इंतज़ार करता है (GIL छूट जाता है), दूसरा चल सकता है।

---

## 🔴 Problem it Solves
Blocking libraries (`requests`, DB drivers, file reads) stall the whole program while waiting. Threads overlap those waits without rewriting everything in async. But shared memory brings race conditions, which locks and queues solve.

## 🔴 यह क्यों बना? (Hindi)
Blocking libraries (`requests`, DB drivers, file reads) इंतज़ार के दौरान पूरे program को रोक देती हैं। Threads इस इंतज़ार को overlap करते हैं और सब कुछ async में दोबारा लिखना नहीं पड़ता। पर shared memory से race condition आती है, जिसे locks और queues सुलझाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → ThreadPoolExecutor(max_workers=5) starts 5 threads
Step 2 → pool.map(fn, items) hands each item to a free thread
Step 3 → A thread blocks on I/O -> releases the GIL -> others run
Step 4 → Shared data changes? wrap in `with lock:`
Step 5 → Threads talk through queue.Queue (thread-safe)
Step 6 → Results come back in order; leaving `with` joins all threads
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → ThreadPoolExecutor(max_workers=5) 5 threads शुरू करता है
Step 2 → pool.map(fn, items) हर item किसी खाली thread को देता है
Step 3 → Thread I/O पर रुकता है -> GIL छोड़ता है -> बाकी चलते हैं
Step 4 → Shared data बदलना हो तो `with lock:` में रखो
Step 5 → Threads आपस में queue.Queue (thread-safe) से बात करते हैं
Step 6 → नतीजे क्रम में मिलते हैं; `with` खत्म होने पर सब threads join होते हैं
```

---

## 🟡 Real World Example
A script that downloads 200 product images: 20 threads cut a 10-minute sequential run to about 30 seconds. A logging thread reads a Queue and writes to disk so request handlers never wait for the disk. FastAPI itself runs your plain `def` routes in a threadpool.

## 🟡 Real Example Hindi mein
200 product images download करने वाली script: 20 threads 10 मिनट के sequential काम को लगभग 30 सेकंड में कर देते हैं। Logging thread Queue पढ़कर disk में लिखता है ताकि request handlers disk का इंतज़ार न करें। FastAPI खुद आपके सामान्य `def` routes को threadpool में चलाता है।

---

## 💻 Code Example — Basic
```python
# Race condition fixed with a Lock
import threading  # threads and locks

count = 0  # shared variable
lock = threading.Lock()  # protects the variable

def work() -> None:  # runs in every thread
    global count  # modify the module-level variable
    for _ in range(10_000):  # many small updates
        with lock:  # only one thread inside at a time
            count += 1  # read-modify-write is now safe

threads = [threading.Thread(target=work) for _ in range(4)]  # 4 threads
for t in threads: t.start()  # start all
for t in threads: t.join()  # wait for all to finish
print(count)  # exact result because of the lock
# Output: 40000
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: thread pool for I/O + bounded Queue producer/consumer
def producer(q: "queue.Queue[int | None]", n: int) -> None:
    for i in range(n):
        q.put(i)  # blocks when the queue is full (back-pressure)
    q.put(None)  # sentinel: no more work

def consumer(q: "queue.Queue[int | None]", out: list[int]) -> None:
    while (item := q.get()) is not None:
        out.append(item * 10)

with ThreadPoolExecutor(max_workers=5) as pool:
    res = list(pool.map(fake_io, range(5)))  # 5 x 0.2s sleeps overlap -> ~0.2s
```
Real output of `python main.py` (timing varies):
```
[0, 2, 4, 6, 8] took ~ 0.2 s (sequential: 1.0s)
locked counter: 200000
[0, 10, 20, 30, 40]
all ok
```

---

## 🟠 JavaScript vs Python Comparison
JS is single-threaded with an event loop; its async/await is closer to Python's asyncio. Python threads are real OS threads but share the GIL for bytecode. A thread pool is like `worker_threads` pool or libuv's threadpool behind `fs`.

```python
with ThreadPoolExecutor(10) as pool:
    results = list(pool.map(download, urls))
```
```javascript
const results = await Promise.all(urls.map(download)); // event loop, not threads
```

---

## 🟠 FastAPI Connection
Plain `def` endpoints and dependencies run in a threadpool (AnyIO, default 40 threads), so blocking DB calls do not freeze the app. Use `await asyncio.to_thread(blocking_fn)` or `run_in_threadpool` for blocking code in `async def`.

```python
@app.get("/report")
async def report() -> dict[str, int]:
    n = await asyncio.to_thread(slow_blocking_function)  # off the event loop
    return {"n": n}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming `count += 1` is atomic. It is read, add, write; threads can interleave.
✅ Correct: use a Lock (or a Queue/atomic structure).

❌ Mistake 2: Using threads for CPU-bound work: no speedup because of the GIL.
✅ Correct: processes.

```python
# Wrong: threads for heavy math, same speed as serial
ThreadPoolExecutor().map(count_primes, limits)
# Right
ProcessPoolExecutor().map(count_primes, limits)
```

❌ Mistake 3: Locks acquired in different orders by two threads: deadlock.
✅ Correct: always acquire in the same order, or use one lock; use `timeout`.

---

## 🧠 Tricky Interview Question
```python
import threading
n = 0
def f():
    global n
    for _ in range(1_000_000): n += 1
ts = [threading.Thread(target=f) for _ in range(2)]
[t.start() for t in ts]; [t.join() for t in ts]
print(n)
```
Answer: Not guaranteed to be `2000000`. It is a data race; the result may be lower and differs per run and per Python version (3.13's changes to the eval loop made it less visible in some builds, but it is still not safe). The GIL protects the interpreter's internals, not your logic. Add a Lock.

---

## ⚫ Interview Questions + Answers

Q1: Does the GIL make threads useless?
A1: No. It is released during blocking I/O, so threads still speed up I/O-bound work.

Q2: Lock vs RLock vs Semaphore?
A2: Lock: one owner. RLock: same thread can re-acquire. Semaphore: allows N holders.

Q3: Daemon threads?
A3: They die when the main thread exits without cleanup; do not use for work that must finish.

Q4: Why queue.Queue?
A4: It is thread-safe, supports blocking get/put and a max size for back-pressure.

Q5: Threads vs asyncio?
A5: Threads work with blocking libraries but cost memory and need locks; asyncio is lighter and scales to thousands of waits but needs async libraries.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Blocking I/O with sync libraries; background housekeeping

❌ Avoid when:
- CPU-bound work
- Thousands of connections (use asyncio)

---

## 📊 Visual Diagram
```
 time ──►
 T1: [req][..wait..][done]
 T2:  [req][..wait..][done]     waits overlap
 T3:   [req][..wait..][done]
 Shared counter: T1 read(5) T2 read(5) T1 write(6) T2 write(6)  -> lost update!
 With Lock:  T1 [read write] then T2 [read write] -> 7
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Thread | Lightweight flow in a process | process के अंदर हल्का flow |
| Race condition | Result depends on timing | समय पर निर्भर गलत नतीजा |
| Lock | Mutual exclusion | एक समय में एक thread |
| Deadlock | Threads wait on each other | आपस में अटक जाना |
| Back-pressure | Slow producer when full | भरी queue पर producer रुकता है |

---

## ⚡ 3-Line Summary
English: Threads overlap I/O waits inside one process.
Shared data needs Locks or Queues to avoid races.
For CPU-bound work use processes instead.
Hindi: Threads एक process में I/O का इंतज़ार overlap करते हैं।
Shared data के लिए Lock या Queue चाहिए ताकि race न हो।
CPU-bound काम के लिए processes इस्तेमाल करो।

---

## ➡️ Next Topic
494. Custom Exception Hierarchy: concurrent code fails in many ways; a clean exception design makes those failures manageable.

---
