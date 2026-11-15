---

# 231. Multiprocessing in Python
# हिंदी में: Python में Multiprocessing (कई processes से असली parallelism)

---

## 🔵 Simple Definition (English)
The `multiprocessing` module runs Python code in separate operating-system processes. Each process has its own interpreter, its own memory and its own GIL, so CPU-bound work can truly run in parallel on several cores. Data moves between processes by pickling (queues, pipes, shared memory).

## 🔵 सरल परिभाषा (Hindi)
`multiprocessing` module Python code को अलग-अलग operating-system processes में चलाता है। हर process का अपना interpreter, अपनी memory और अपना GIL होता है, इसलिए CPU-bound काम कई cores पर सचमुच parallel चल सकता है। Processes के बीच data pickling (queues, pipes, shared memory) से जाता है।

---

## 🔴 Problem it Solves
The GIL stops threads from using more than one core for Python code. For CPU-bound jobs (parsing, image work, data crunching) that leaves 7 of 8 cores idle. Multiprocessing sidesteps the GIL by using one interpreter per core.

## 🔴 यह क्यों बना? (Hindi)
GIL threads को Python code के लिए एक से ज़्यादा core इस्तेमाल करने नहीं देता। CPU-bound jobs (parsing, image काम, data crunching) में 8 में से 7 cores खाली रहते हैं। Multiprocessing हर core के लिए एक interpreter चलाकर GIL को बायपास करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Parent starts N child processes (fork / spawn / forkserver)
Step 2 → Each child has its own memory; the target function is sent by NAME (must be importable)
Step 3 → Arguments and results travel as pickles (Pool.map, Queue, Pipe)
Step 4 → Children run on different cores at the same time
Step 5 → Parent collects results and joins/terminates the children
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Parent N child processes शुरू करता है (fork / spawn / forkserver)
Step 2 → हर child की अपनी memory; target function नाम से भेजा जाता है (importable होना चाहिए)
Step 3 → Arguments और results pickle होकर जाते हैं (Pool.map, Queue, Pipe)
Step 4 → Children अलग cores पर एक साथ चलते हैं
Step 5 → Parent results इकट्ठा करके children को join/terminate करता है
```

---

## 🟡 Real World Example
A Swiggy ML team preprocesses 10 million order records before training: they split into chunks and run `Pool(8).map(clean_chunk, chunks)` for a near 8x speedup on an 8-core box. A media app converts uploaded images to thumbnails with a process pool. Gunicorn runs a FastAPI app as several worker processes for the same reason.

## 🟡 Real Example Hindi mein
Swiggy की ML team training से पहले 1 करोड़ order records preprocess करती है: chunks में बाँटकर `Pool(8).map(clean_chunk, chunks)` चलाती है और 8-core machine पर लगभग 8 गुना speedup पाती है। Media app uploaded images के thumbnails process pool से बनाता है। Gunicorn भी इसी कारण FastAPI app को कई worker processes में चलाता है।

---

## 💻 Code Example — Basic
```python
# Basic multiprocessing.Pool - every line commented
import multiprocessing as mp  # the module
from typing import List  # type hints


def square(n: int) -> int:  # worker function: MUST be defined at module level (picklable)
    return n * n  # simple computation


if __name__ == "__main__":  # REQUIRED on macOS/Windows because children re-import this file
    print(mp.get_start_method())  # how children are created on this OS
    # Output: spawn   (macOS/Windows default; Linux 3.13 default is "fork", 3.14 uses "forkserver")

    with mp.Pool(processes=4) as pool:  # 4 worker processes, cleaned up by "with"
        print(pool.map(square, range(8)))  # split the list across workers, ordered results
        # Output: [0, 1, 4, 9, 16, 25, 36, 49]

        print(pool.starmap(pow, [(2, 3), (3, 2)]))  # each tuple becomes arguments: pow(2,3), pow(3,2)
        # Output: [8, 9]

        res = pool.apply_async(square, (9,))  # run ONE call asynchronously
        print(res.get(timeout=5))  # wait for the result (re-raises worker errors)
        # Output: 81

        unordered: List[int] = list(pool.imap_unordered(square, range(4), chunksize=2))  # results as they finish
        print(len(unordered))  # order not guaranteed, so we only count
        # Output: 4
```

## 💻 Code Example — Advanced
```python
# Production style: spawn context, shared Value with a lock, Queue results, ProcessPoolExecutor, pickling limits
import multiprocessing as mp  # processes
from concurrent.futures import ProcessPoolExecutor  # high level API
from typing import List  # type hints


def bump(v, n: int) -> None:  # increments a shared counter n times (module level!)
    for _ in range(n):  # repeat
        with v.get_lock():  # shared Value has its own lock
            v.value += 1  # read-modify-write needs the lock across processes too


def worker(n: int, q) -> None:  # puts a result on a queue
    q.put(n * n)  # results come back through the queue


counter_global: int = 0  # a module global to prove memory is NOT shared


def change_global() -> None:  # child modifies its OWN copy
    global counter_global  # module variable
    counter_global = 99  # visible only inside the child


def square(n: int) -> int:  # for ProcessPoolExecutor
    return n * n  # computation


if __name__ == "__main__":  # entry guard
    ctx = mp.get_context("spawn")  # explicit, portable start method (same behaviour everywhere)

    v = ctx.Value("i", 0)  # shared int in shared memory
    ps: List = [ctx.Process(target=bump, args=(v, 100)) for _ in range(4)]  # four processes
    [p.start() for p in ps]  # start
    [p.join() for p in ps]  # wait
    print(v.value)  # no lost updates because of the lock
    # Output: 400

    child = ctx.Process(target=change_global)  # child that changes a global
    child.start(); child.join()  # run to completion
    print(counter_global)  # parent copy is unchanged: separate memory
    # Output: 0

    q = ctx.Queue()  # process-safe queue
    ws = [ctx.Process(target=worker, args=(i, q)) for i in range(4)]  # four workers
    [w.start() for w in ws]  # start
    print(sorted(q.get(timeout=10) for _ in ws))  # collect BEFORE join (a full pipe can block join)
    # Output: [0, 1, 4, 9]
    [w.join() for w in ws]  # now join
    print([w.exitcode for w in ws])  # 0 = clean exit
    # Output: [0, 0, 0, 0]

    with ProcessPoolExecutor(2) as ex:  # Future-based API, same as ThreadPoolExecutor
        print(list(ex.map(square, [1, 2, 3])))  # works with module-level functions
        # Output: [1, 4, 9]

    try:  # lambdas cannot be pickled
        with mp.Pool(1) as pool:  # a pool
            pool.map(lambda x: x, [1])  # fails
    except Exception as e:  # pickling error
        print(type(e).__name__)  # error class
        # Output: PicklingError
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: Pool.map across processes
with mp.Pool(4) as pool:
    results = pool.map(square, range(1000))
```

```javascript
// Node.js: worker_threads (or the child_process / cluster modules)
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");
if (isMainThread) {
  const w = new Worker(__filename, { workerData: 9 });
  w.on("message", (r) => console.log(r));       // 81
} else {
  parentPort.postMessage(workerData * workerData);
}
```

Key differences: Both use separate memory and message passing. Python's `Pool.map` hides the messaging; in Node you write the messages yourself (or use Piscina). Python must pickle arguments, so lambdas and open sockets cannot be sent.

---

## 🟠 FastAPI Connection
FastAPI's event loop must never run heavy CPU work. Offload it to a `ProcessPoolExecutor` with `run_in_executor`. Production servers also use multiple worker processes (`uvicorn --workers 4` or Gunicorn) so that the whole app uses all cores.

```python
import asyncio  # event loop
from concurrent.futures import ProcessPoolExecutor  # process pool
from typing import Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

def resize_image(size: int) -> int:  # CPU heavy, module level (picklable)
    return sum(i % 7 for i in range(size))  # stand-in for real image work

app: FastAPI = FastAPI()  # create app

@app.post("/resize")  # POST /resize
async def resize(size: int = 1_000_000) -> Dict[str, int]:
    loop = asyncio.get_running_loop()  # running loop
    with ProcessPoolExecutor(max_workers=2) as pool:  # real parallelism
        out: int = await loop.run_in_executor(pool, resize_image, size)  # non-blocking
    return {"result": out}  # response

if __name__ == "__main__":  # needed: spawn re-imports this module
    print(TestClient(app).post("/resize", params={"size": 1000}).json())
# Output: {'result': 2997}
```
(In a real app create the pool once at startup, not per request, and size it to your cores.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Missing `if __name__ == "__main__":`
```python
# Wrong - with spawn each child re-imports the file and tries to start more processes (RuntimeError)
pool = mp.Pool(4)
pool.map(square, range(10))

# Correct
if __name__ == "__main__":
    with mp.Pool(4) as pool:
        pool.map(square, range(10))
```

❌ Mistake 2: Passing lambdas or nested functions
```python
# Wrong - PicklingError (a nested function target also fails under spawn:
# "AttributeError: Can't get attribute 'bump' on <module '__mp_main__'>")
pool.map(lambda x: x * 2, data)

# Correct - module-level function
def double(x: int) -> int:
    return x * 2
pool.map(double, data)
```

❌ Mistake 3: Expecting shared memory
```python
# Wrong - each process changes its own copy
results = []
def work(x): results.append(x)

# Correct - return values (Pool.map), a Queue, or multiprocessing.Value/Array/shared_memory
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print on macOS (spawn) and why?

```python
import multiprocessing as mp
total = 0
def add(n):
    global total
    total += n
if __name__ == "__main__":
    ps = [mp.Process(target=add, args=(i,)) for i in range(1, 4)]
    [p.start() for p in ps]; [p.join() for p in ps]
    print(total)
```

**Answer**:
```
0
```
Each child changes its own copy of `total`; the parent's variable is never touched. Return the values (Pool.map), or use `mp.Value`, a Queue or shared memory.

---

## ⚫ Interview Questions + Answers

Q1: Multiprocessing vs multithreading in Python?
A1: Processes have separate memory and GILs, so they run CPU-bound code in parallel but cost more memory and need pickling. Threads share memory and are lighter but share one GIL.

Q2: fork vs spawn vs forkserver?
A2: `fork` copies the parent (fast, Linux/Unix, unsafe with threads), `spawn` starts a fresh interpreter and re-imports the module (default on macOS/Windows), `forkserver` forks from a clean helper process (the Linux default from Python 3.14). Use `mp.get_context("spawn")` for portable behaviour.

Q3: How do processes share data?
A3: `Queue`, `Pipe`, `Value`/`Array` (shared ctypes), `shared_memory.SharedMemory` (zero copy buffers), or a `Manager` (proxy objects, slower).

Q4: Why is the `__main__` guard needed?
A4: Spawn imports your module in every child; without the guard the child would run the process-creation code again.

Q5: How many processes should I start?
A5: About `os.cpu_count()` for CPU-bound work. More only adds overhead.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- CPU-bound work that splits into independent chunks
- You need isolation (a crash in a child does not kill the parent)

❌ Avoid when:
- Tasks are tiny (process start and pickling cost more than the work)
- Work is I/O-bound (threads or asyncio are cheaper)
- You must share large mutable objects (use shared memory or redesign)

---

## 📊 Visual Diagram

```
 Parent ──spawn──► Child 1 [own memory, own GIL] ─► core 1 ┐
        ──spawn──► Child 2 [own memory, own GIL] ─► core 2 ├─► results via Queue / Pool.map
        ──spawn──► Child 3 [own memory, own GIL] ─► core 3 ┘
             (arguments and results are pickled between processes)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Process | Program instance with own memory | अपनी memory वाला program instance |
| Pool | Fixed group of workers | workers का समूह |
| Pickling | Converting objects to bytes | objects को bytes में बदलना |
| spawn / fork | Ways to create a child | child बनाने के तरीके |
| IPC | Inter-process communication | processes के बीच संवाद |
| Shared memory | Memory visible to many processes | कई processes को दिखने वाली memory |

---

## ⚡ 3-Line Summary
English: `multiprocessing` gives real parallelism with one interpreter and GIL per process. Use module-level functions, the `__main__` guard, and explicit data sharing (Queue, Value, shared_memory). Choose it for CPU-bound work only.
Hindi: `multiprocessing` हर process में अलग interpreter और GIL देकर असली parallelism देता है। Module-level functions, `__main__` guard और साफ data sharing (Queue, Value, shared_memory) इस्तेमाल करें। इसे सिर्फ CPU-bound काम के लिए चुनें।

---

## ➡️ Next Topic
**232. Process Class** — create, join, terminate and subclass `multiprocessing.Process`.
