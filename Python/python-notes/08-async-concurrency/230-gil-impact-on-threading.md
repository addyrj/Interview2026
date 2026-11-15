---

# 230. GIL — Impact on Threading
# हिंदी में: GIL - Threading पर असर

---

## 🔵 Simple Definition (English)
The Global Interpreter Lock (GIL) in standard CPython lets only one thread execute Python bytecode at a time. So threads do not speed up CPU-bound Python code, but they still help I/O-bound code because a thread that waits for the network or disk releases the GIL.

## 🔵 सरल परिभाषा (Hindi)
Standard CPython में Global Interpreter Lock (GIL) एक समय में सिर्फ एक thread को Python bytecode चलाने देता है। इसलिए threads CPU-bound Python code को तेज़ नहीं करते, पर I/O-bound code में मदद करते हैं क्योंकि network या disk का इंतज़ार करने वाला thread GIL छोड़ देता है।

---

## 🔴 Problem it Solves
Why does the GIL exist? CPython manages memory with reference counts; without a lock, two threads changing a count at the same time would corrupt memory. One big lock made the interpreter simple and fast for single-threaded code. The cost is the impact on threading, which you must understand to pick the right tool.

## 🔴 यह क्यों बना? (Hindi)
GIL क्यों है? CPython memory को reference counts से संभालता है; lock के बिना दो threads एक ही समय में count बदलें तो memory खराब हो सकती है। एक बड़े lock से interpreter सरल और single-thread में तेज़ रहा। कीमत threading पर असर है, जिसे सही tool चुनने के लिए समझना ज़रूरी है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → A thread must hold the GIL to run Python bytecode
Step 2 → After the switch interval (5 ms by default) it is asked to give the GIL up
Step 3 → Blocking I/O (socket, file, sleep) and many C extensions release the GIL
Step 4 → Another waiting thread grabs the GIL and runs
Step 5 → CPU-bound threads just take turns -> no speedup; I/O threads overlap their waits
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Python bytecode चलाने के लिए thread के पास GIL होना चाहिए
Step 2 → Switch interval (default 5 ms) के बाद उससे GIL छोड़ने को कहा जाता है
Step 3 → Blocking I/O (socket, file, sleep) और कई C extensions GIL छोड़ देते हैं
Step 4 → इंतज़ार कर रहा दूसरा thread GIL लेकर चलता है
Step 5 → CPU-bound threads बारी-बारी चलते हैं -> कोई speedup नहीं; I/O threads के इंतज़ार overlap होते हैं
```

---

## 🟡 Real World Example
A Zomato image service resizes uploads with pure-Python code on 8 threads: it uses one core and is no faster than 1 thread, so they switch to a process pool (or Pillow/NumPy code that releases the GIL). The same service calls 8 restaurant APIs on 8 threads and gets a real 8x speedup because the time is spent waiting. A password-hashing endpoint using `hashlib` scales with threads because hashlib releases the GIL for large inputs.

## 🟡 Real Example Hindi mein
Zomato की image service pure-Python code से 8 threads पर uploads resize करती है: वह एक core इस्तेमाल करती है और 1 thread से तेज़ नहीं है, इसलिए वे process pool (या ऐसा Pillow/NumPy code जो GIL छोड़ता है) लगाते हैं। वही service 8 restaurant APIs 8 threads पर call करती है और सचमुच 8 गुना तेज़ होती है क्योंकि समय इंतज़ार में जाता है। `hashlib` वाला password-hashing endpoint threads से scale करता है क्योंकि बड़े input पर hashlib GIL छोड़ देता है।

---

## 💻 Code Example — Basic
```python
# Basic: observe the GIL's effect - every line commented
import sys  # interpreter info
import sysconfig  # build configuration
import threading  # threads
import time  # timing

print(sys.version_info[:2])  # which Python?
# Output: (3, 13)
print(sys._is_gil_enabled())  # Python 3.13+: is the GIL on? (private but documented in the 3.13 notes)
# Output: True
print(sysconfig.get_config_var("Py_GIL_DISABLED"))  # 1 only on free-threaded builds (python3.13t)
# Output: 0
print(sys.getswitchinterval())  # seconds between GIL hand-over requests
# Output: 0.005


def cpu(n: int) -> int:  # CPU-bound loop in pure Python
    c: int = 0  # accumulator
    for i in range(n):  # many bytecodes
        c += i  # arithmetic
    return c  # result


N: int = 5_000_000  # work size
t0: float = time.perf_counter()  # start
cpu(N); cpu(N)  # two runs, one after another
seq: float = time.perf_counter() - t0  # elapsed

t0 = time.perf_counter()  # start again
ts = [threading.Thread(target=cpu, args=(N,)) for _ in range(2)]  # two threads
[t.start() for t in ts]  # start
[t.join() for t in ts]  # wait
thr: float = time.perf_counter() - t0  # elapsed
print("threads not faster for CPU:", thr > seq * 0.8)  # same speed or worse
# Output: True


def io() -> None:  # I/O-bound: sleeping releases the GIL
    time.sleep(0.2)  # wait


t0 = time.perf_counter()  # start
ts = [threading.Thread(target=io) for _ in range(4)]  # four waiting threads
[t.start() for t in ts]; [t.join() for t in ts]  # run and wait
print("io threads overlap:", time.perf_counter() - t0 < 0.5)  # 0.2s, not 0.8s
# Output: True
```

## 💻 Code Example — Advanced
```python
# Production style: GIL-releasing C code scales with threads; pure Python does not; processes do
import hashlib  # hashing releases the GIL for large buffers
import threading  # threads
import time  # timing
from concurrent.futures import ProcessPoolExecutor  # separate processes
from typing import Callable, List  # type hints

DATA: bytes = b"a" * 50_000_000  # 50 MB of data


def sha() -> None:  # C code: GIL released while hashing a big buffer
    hashlib.sha256(DATA).hexdigest()  # heavy but GIL-free


def pure(n: int) -> int:  # pure Python: holds the GIL
    return sum(i * i for i in range(n))  # bytecode loop


def timed(fn: Callable[[], None]) -> float:  # time a callable
    t0: float = time.perf_counter()  # start
    fn()  # run
    return time.perf_counter() - t0  # seconds


def threads(fn: Callable[[], None], k: int) -> None:  # run fn in k threads
    ts: List[threading.Thread] = [threading.Thread(target=fn) for _ in range(k)]  # create
    [t.start() for t in ts]  # start
    [t.join() for t in ts]  # wait


if __name__ == "__main__":  # needed for process pools on macOS/Windows
    one_by_one: float = timed(lambda: [sha(), sha()])  # two hashes sequentially
    in_threads: float = timed(lambda: threads(sha, 2))  # two hashes in two threads
    print("hashlib threads speedup:", in_threads < one_by_one * 0.8)  # real overlap
    # Output: True   (about 2.9x faster on an 8-core Mac)

    t_seq: float = timed(lambda: [pure(3_000_000) for _ in range(4)])  # pure Python sequential
    t_thr: float = timed(lambda: threads(lambda: pure(3_000_000), 4))  # pure Python in threads
    with ProcessPoolExecutor(4) as pool:  # four processes = four GILs
        t_proc: float = timed(lambda: list(pool.map(pure, [3_000_000] * 4)))  # pure Python in processes
    print("threads ~ sequential:", t_thr > 0.7 * t_seq)  # GIL: no gain
    print("processes faster:", t_proc < t_seq)  # real parallelism
    # Output: threads ~ sequential: True / processes faster: True

    import sys  # refcount demo (kept inside the guard so child processes do not print it)
    x: list = []  # a fresh list
    print(sys.getrefcount(x))  # 2 = the name x + the temporary argument; this is what the GIL protects
    # Output: 2
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: threads share memory, but only one runs Python code at a time (GIL)
from concurrent.futures import ProcessPoolExecutor   # for CPU parallelism
```

```javascript
// JavaScript: one thread runs your JS (like the GIL, but by design); workers are separate isolates
const { Worker } = require("worker_threads");
new Worker("./cpu.js");     // true parallelism, separate memory, message passing
```

Key differences: Node avoids shared-memory races by having one JS thread; Python allows shared memory but serializes bytecode with the GIL. Python 3.13 adds an experimental free-threaded build (`python3.13t`, PEP 703) and 3.14 makes it officially supported, but the default build and most libraries still assume the GIL, so treat it as optional and test carefully.

---

## 🟠 FastAPI Connection
Sync endpoints run in a threadpool (about 40 threads by default). Because of the GIL, a pure-Python CPU-heavy endpoint blocks other requests' Python code even though it runs "in a thread". I/O endpoints and GIL-releasing C libraries (hashlib, bcrypt, NumPy, Pillow) are fine.

```python
import hashlib, time  # hashing releases the GIL
from concurrent.futures import ProcessPoolExecutor  # processes
from typing import Dict  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process client

app: FastAPI = FastAPI()  # create app

def slow_hash(password: str) -> str:  # CPU heavy (PBKDF2 releases the GIL, pure python wouldn't)
    return hashlib.pbkdf2_hmac("sha256", password.encode(), b"salt", 200_000).hex()[:16]  # derive key

@app.post("/hash")  # sync endpoint -> threadpool; hashlib frees the GIL so threads do scale
def hash_pw(password: str) -> Dict[str, str]:
    return {"hash": slow_hash(password)}  # response

@app.get("/pure-python-cpu")  # pure Python loop holds the GIL -> blocks other threads
def pure(n: int = 100_000) -> Dict[str, int]:
    return {"sum": sum(i * i for i in range(n))}  # GIL-bound work

client = TestClient(app)
print(client.post("/hash", params={"password": "x"}).json())
# Output: {'hash': 'b33b2be21322236a'}
print(client.get("/pure-python-cpu").json())
# Output: {'sum': 333328333350000}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Adding threads to speed up a pure-Python loop
```python
# Wrong - same speed (or slower from switching)
with ThreadPoolExecutor(8) as ex:
    list(ex.map(parse_row, rows))

# Correct
with ProcessPoolExecutor(8) as ex:
    list(ex.map(parse_row, rows, chunksize=1000))
```

❌ Mistake 2: Believing the GIL makes your code thread-safe
```python
# Wrong - the GIL protects the interpreter, not your logic
if key not in cache:        # another thread can run here
    cache[key] = compute()

# Correct
with lock:
    if key not in cache:
        cache[key] = compute()
```

❌ Mistake 3: Blaming the GIL for slow I/O
```python
# Wrong assumption: "threads are useless in Python"
# Correct: I/O-bound threads work well because blocking calls release the GIL
```

---

## 🧠 Tricky Interview Question

**Q**: A service runs 4 threads of a pure-Python CPU task on a 4-core server and is no faster than one thread. Which change gives a real speedup: more threads, `asyncio`, or `multiprocessing`? Why does `time.sleep` in threads still overlap?

**Answer**:
```
multiprocessing (or moving the hot loop to C / NumPy that releases the GIL).
More threads: no (GIL). asyncio: no (single thread, CPU work blocks the loop).
time.sleep releases the GIL while waiting, so sleeping threads overlap.
```
Each process has its own interpreter and its own GIL, so four processes can use four cores. Data crosses process boundaries by pickling, which adds overhead.

---

## ⚫ Interview Questions + Answers

Q1: What is the GIL?
A1: A mutex in CPython that allows only one thread to execute Python bytecode at a time, protecting reference counts and internal state.

Q2: When do threads still help?
A2: For I/O-bound work (network, disk, `sleep`) and for C extensions that release the GIL (hashlib on big data, NumPy, Pillow, many DB drivers).

Q3: How do you get true parallelism?
A3: `multiprocessing` / `ProcessPoolExecutor`, native extensions (Cython, Rust via PyO3, NumPy), or the experimental free-threaded Python build.

Q4: What is the switch interval?
A4: `sys.getswitchinterval()`, default 5 ms: how long a thread may run before being asked to release the GIL when others are waiting.

Q5: What is changing about the GIL?
A5: PEP 703: Python 3.13 ships an optional experimental free-threaded build (`python3.13t`); 3.14 officially supports it. The default build still has the GIL, and many packages need updates for free-threading.

---

## 🔷 When to Use + When Not to Use

✅ Threads are fine when:
- Waiting on network/disk, or calling GIL-releasing libraries

❌ Threads are wrong when:
- Pure-Python number crunching, parsing, or image loops (use processes)
- You need 10k connections (use asyncio)

---

## 📊 Visual Diagram

```
 CPU-bound threads:        T1 ████░░░░████░░░░
                           T2 ░░░░████░░░░████     one at a time (GIL)

 I/O-bound threads:        T1 █▒▒▒▒▒▒▒▒█         █ = running Python
                           T2 █▒▒▒▒▒▒▒▒█         ▒ = waiting (GIL released)
                           waits overlap -> big speedup
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GIL | One bytecode-runner at a time | एक समय में एक bytecode चलाने वाला lock |
| CPU-bound | Limited by computation | गणना से सीमित |
| I/O-bound | Limited by waiting | इंतज़ार से सीमित |
| Switch interval | GIL hand-over period | GIL बदलने का अंतराल |
| Free-threaded | Build without the GIL | बिना GIL वाला build |
| Reference count | Number of references to an object | object के references की गिनती |

---

## ⚡ 3-Line Summary
English: The GIL lets one thread run Python bytecode at a time, so threads help I/O-bound work but not CPU-bound pure Python. Use processes or GIL-releasing C libraries for CPU work. Free-threaded Python is experimental in 3.13.
Hindi: GIL एक समय में एक thread को Python bytecode चलाने देता है, इसलिए threads I/O-bound काम में मदद करते हैं, CPU-bound pure Python में नहीं। CPU काम के लिए processes या GIL छोड़ने वाली C libraries लें। Free-threaded Python 3.13 में experimental है।

---

## ➡️ Next Topic
**231. Multiprocessing in Python** — real parallelism with separate processes and pools.
