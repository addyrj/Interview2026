---

# Q125. Fix thread race condition
# Category: FIX THE BUG
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Four threads each increment a shared counter. The final total is sometimes less than expected. Fix the race condition.

```python
counter = 0
def worker(n):
    global counter
    for _ in range(n):
        tmp = counter        # read
        counter = tmp + 1    # write (another thread may have changed it in between)
```

---

## 💡 Quick Concept (2 lines only)
`counter += 1` is read -> add -> write: several bytecodes, and a thread switch between them loses updates. The GIL does NOT make it atomic; protect it with a `Lock`.
हिंदी: `+=` कई steps है, बीच में thread बदल सकता है — `Lock` से critical section बचाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import threading, time                                   # stdlib

counter = 0                                              # shared state

def run(worker, n=2000, threads=4):
    global counter
    counter = 0                                          # reset
    ts = [threading.Thread(target=worker, args=(n,)) for _ in range(threads)]  # create threads
    for t in ts: t.start()                               # start all
    for t in ts: t.join()                                # wait for all
    return counter

def worker_bad(n: int) -> None:
    global counter
    for _ in range(n):
        tmp = counter                                    # read
        time.sleep(0)                                    # yield GIL -> widens the race window (makes bug reproducible)
        counter = tmp + 1                                # write a possibly STALE value

lock = threading.Lock()                                  # ONE shared lock

def worker_fixed(n: int) -> None:
    global counter
    for _ in range(n):
        with lock:                                       # FIX: only one thread in this block at a time
            tmp = counter                                # read
            time.sleep(0)                                # even with a forced switch...
            counter = tmp + 1                            # ...no one else can interleave

# ============================================
# TEST CASES
# ============================================
print("buggy:", [run(worker_bad) for _ in range(3)], "expected 8000")
# Expected: values well below 8000, e.g. [2004, 2000, 2028]  (varies every run)
print("fixed:", [run(worker_fixed) for _ in range(3)])
# Expected: [8000, 8000, 8000]  (always)
```

---

## 🔍 Why This Works (3 lines max)
The lock makes read-modify-write one indivisible step, so no thread can overwrite another's update. I added `time.sleep(0)` only to force switches: a plain `counter += 1` loop of 800,000 increments did NOT lose updates in my CPython 3.13.3 run, but it is still not guaranteed safe (switch timing is version-dependent and free-threaded builds make it worse).
हिंदी: Lock से read-modify-write एक साथ होता है, इसलिए कोई update खोता नहीं।

---

## ⚡ Alternative Solution
```python
# Avoid shared state: each worker counts locally, then combine results
from concurrent.futures import ThreadPoolExecutor        # stdlib

def count_chunk(n: int) -> int:
    local = 0                                            # private to this call
    for _ in range(n):
        local += 1                                       # no sharing -> no race
    return local

with ThreadPoolExecutor(4) as ex:
    print(sum(ex.map(count_chunk, [200_000] * 4)))       # Output: 800000
# Other options: queue.Queue (thread-safe), threading.RLock, atomic types via multiprocessing.Value
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: creating a NEW lock inside the loop — each thread locks its own private lock
def worker_wrong(n):
    global counter
    for _ in range(n):
        l = threading.Lock()                # new lock every iteration protects nothing
        with l:
            tmp = counter; time.sleep(0); counter = tmp + 1
print([run(worker_wrong) for _ in range(3)])   # Output: values far below 8000, e.g. [2000, 2399, 2000] (varies)

# ✅ Correct: ONE lock shared by all threads (module-level or passed in)
```

---

## 🎯 Interview Tip (1 line)
Say: "The GIL protects interpreter internals, not my read-modify-write logic — I guard shared state with a single shared Lock, or avoid sharing with queues/per-thread results."

---

## 🔗 Related Questions
→ Q164 (the GIL) | Q298 (the GIL classic) | Q299 (threading vs multiprocessing vs asyncio) | Q285 (threading for I/O-bound)
