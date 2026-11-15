---

# 492. Multiprocessing Example
# हिंदी में: Multiprocessing का Example (CPU-bound काम)

Full runnable solution: [main.py](main.py) (ProcessPoolExecutor, `mp.Process` + `Queue`, timing comparison).

---

## 🔵 Simple Definition (English)
Multiprocessing runs work in separate Python processes, each with its own interpreter and its own GIL, so CPU-heavy code can use several cores at the same time.

## 🔵 सरल परिभाषा (Hindi)
Multiprocessing काम को अलग-अलग Python processes में चलाता है; हर process का अपना interpreter और अपना GIL होता है, इसलिए CPU-भारी code कई cores पर एक साथ चल सकता है।

---

## 🔴 Problem it Solves
The GIL lets only one thread run Python bytecode at a time, so threads cannot speed up CPU-bound loops (image resize, prime search, ML preprocessing). Separate processes avoid the GIL.

## 🔴 यह क्यों बना? (Hindi)
GIL के कारण एक समय में सिर्फ़ एक thread Python bytecode चलाता है, इसलिए threads CPU-bound loops (image resize, prime search, ML preprocessing) को तेज़ नहीं कर सकते। अलग processes GIL से बच जाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent creates a pool of N worker processes
Step 2 → Function + arguments are pickled and sent to a worker
Step 3 → Each worker runs on its own core, own memory
Step 4 → Result is pickled and sent back to the parent
Step 5 → pool.map returns results in input order
Step 6 → `if __name__ == "__main__":` guard stops spawn from re-running the script
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent N worker processes का pool बनाता है
Step 2 → Function और arguments pickle होकर worker को जाते हैं
Step 3 → हर worker अपने core और अपनी memory पर चलता है
Step 4 → नतीजा pickle होकर parent को लौटता है
Step 5 → pool.map नतीजे input के क्रम में लौटाता है
Step 6 → `if __name__ == "__main__":` guard से spawn script को दोबारा नहीं चलाता
```

---

## 🟡 Real World Example
A Swiggy analytics job crunches 8 city files in parallel, one per core. An AI app preprocesses 10,000 images (resize, normalise) across cores before training. A FastAPI service offloads PDF/ML jobs to a `ProcessPoolExecutor` so the event loop stays free.

## 🟡 Real Example Hindi mein
Swiggy का analytics job 8 शहरों की files को हर core पर एक-एक करके parallel चलाता है। AI app training से पहले 10,000 images को cores में बाँटकर resize/normalise करता है। FastAPI service PDF/ML काम `ProcessPoolExecutor` को देती है ताकि event loop खाली रहे।

---

## 💻 Code Example — Basic
```python
# Square numbers in 2 worker processes
from concurrent.futures import ProcessPoolExecutor  # process pool

def square(n: int) -> int:  # must be top-level so it can be pickled
    return n * n  # CPU work stand-in

if __name__ == "__main__":  # required on macOS/Windows (spawn)
    with ProcessPoolExecutor(max_workers=2) as pool:  # start 2 processes
        print(list(pool.map(square, [1, 2, 3, 4])))  # ordered results
# Output: [1, 4, 9, 16]
```

## 💻 Code Example — Advanced
```python
# Excerpt from main.py: CPU-bound prime counting, serial vs parallel, Queue between processes
def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count

if __name__ == "__main__":
    limits = [250_000] * 4
    serial = [count_primes(n) for n in limits]
    with ProcessPoolExecutor(max_workers=4) as pool:
        parallel = list(pool.map(count_primes, limits))
    q = mp.Queue()
    procs = [mp.Process(target=worker, args=(q, i)) for i in range(4)]
    for p in procs: p.start()
    got = sorted(q.get() for _ in procs)  # read BEFORE join to avoid deadlock
    for p in procs: p.join()
```
Real output of `python main.py` (macOS, Python 3.13.3, start method `spawn`; times depend on your CPU):
```
[22044, 22044, 22044, 22044] True
serial 1.62s parallel 0.64s (timings vary)
[0, 1, 4, 9] start method: spawn
all ok
```
Note: with a small limit (60,000) parallel was not faster (0.23s vs 0.25s) because starting processes and pickling cost more than the work. Only parallelise big tasks.

---

## 🟠 JavaScript vs Python Comparison
Node.js has `worker_threads` (separate V8 isolates) and `child_process`/`cluster`. Python processes are the analogue of `cluster` workers; they share nothing and talk by messages (pickle).

```python
with ProcessPoolExecutor() as pool:
    results = list(pool.map(heavy, items))
```
```javascript
const { Worker } = require("worker_threads");
new Worker("./heavy.js", { workerData: item }); // message back with postMessage
```

---

## 🟠 FastAPI Connection
Heavy CPU work in an endpoint blocks the event loop. Use `loop.run_in_executor` with a `ProcessPoolExecutor`; or run Uvicorn/Gunicorn with several worker processes for request-level parallelism.

```python
import asyncio  # loop access
from concurrent.futures import ProcessPoolExecutor  # pool

pool = ProcessPoolExecutor(max_workers=4)  # created once at startup

@app.get("/primes/{n}")
async def primes(n: int) -> dict[str, int]:
    loop = asyncio.get_running_loop()  # current loop
    count = await loop.run_in_executor(pool, count_primes, n)  # off the event loop
    return {"count": count}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Missing `if __name__ == "__main__":` guard. On spawn platforms each child re-imports the script and tries to start more processes (RuntimeError).
✅ Correct: always guard the entry point.

❌ Mistake 2: Passing lambdas, nested functions or open sockets to workers; they cannot be pickled.
✅ Correct: top-level functions and simple arguments.

```python
# Wrong
pool.map(lambda x: x * 2, data)    # PicklingError
# Right
def double(x: int) -> int: return x * 2
pool.map(double, data)
```

❌ Mistake 3: Using processes for tiny tasks or I/O waiting.
✅ Correct: threads/async for I/O; processes only for heavy CPU.

---

## 🧠 Tricky Interview Question
```python
import multiprocessing as mp
counter = 0
def inc():
    global counter
    counter += 1
if __name__ == "__main__":
    ps = [mp.Process(target=inc) for _ in range(4)]
    [p.start() for p in ps]; [p.join() for p in ps]
    print(counter)
```
Answer: `0`. Each process has its own copy of `counter`; changes in children are invisible to the parent. Use `mp.Value`, `mp.Queue` or return values from a pool.

Version note: since Python 3.14 the default start method on Linux changes from `fork` to `forkserver`; macOS/Windows already use `spawn`. Write code that works under spawn.

---

## ⚫ Interview Questions + Answers

Q1: What is the GIL?
A1: A lock in CPython allowing one thread to execute bytecode at a time. Python 3.13 has an experimental free-threaded build, but it is not the default.

Q2: Threads vs processes vs asyncio?
A2: asyncio and threads for I/O waiting; processes for CPU work.

Q3: fork vs spawn?
A3: fork copies the parent (fast, unsafe with threads); spawn starts a fresh interpreter (safe, slower, needs the main guard).

Q4: How do processes share data?
A4: Queue/Pipe, `shared_memory`, `Manager`, files, or a database. Data is copied (pickled) otherwise.

Q5: How many workers?
A5: About `os.cpu_count()` for CPU-bound work.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- CPU-heavy, independent tasks: image/video, number crunching, data prep

❌ Avoid when:
- Task is I/O bound or tiny
- Tasks need lots of shared mutable state

---

## 📊 Visual Diagram
```
 parent ──pickle(args)──► worker 1 (core 1, own GIL) ──┐
        ──pickle(args)──► worker 2 (core 2, own GIL) ──┼─► results (ordered)
        ──pickle(args)──► worker 3 (core 3, own GIL) ──┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GIL | One-thread-at-a-time lock | एक समय में एक thread का lock |
| Process | Independent program instance | स्वतंत्र program |
| Pickle | Serialise Python objects | objects को bytes बनाना |
| spawn | Start fresh interpreter | नया interpreter शुरू करना |
| CPU-bound | Limited by computation | गणना पर निर्भर |

---

## ⚡ 3-Line Summary
English: Processes bypass the GIL and use many cores.
Data is pickled between them, so keep arguments simple.
Always use the __main__ guard.
Hindi: Processes GIL से बचकर कई cores इस्तेमाल करते हैं।
उनके बीच data pickle होता है, इसलिए arguments सरल रखो।
हमेशा __main__ guard लगाओ।

---

## ➡️ Next Topic
493. Threading Example: when the task waits on I/O rather than computing, threads are lighter than processes.

---
