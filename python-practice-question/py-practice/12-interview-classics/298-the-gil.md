---

# Q298. The GIL
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What is the GIL? Prove with code that threads do NOT speed up CPU-bound work in CPython but DO speed up I/O-bound work, and show how to get real CPU parallelism.

```python
# NOT RUN (question stub)
# 4 CPU tasks in 4 threads: faster than sequential?  4 sleeping tasks in 4 threads?
```

---

## 💡 Quick Concept (2 lines only)
The Global Interpreter Lock lets only ONE thread execute Python bytecode at a time in a standard CPython build. It is released during blocking I/O (sleep, sockets, files), so I/O threads overlap but CPU threads do not.
हिंदी: GIL एक समय में एक ही thread को Python bytecode चलाने देता है; I/O में release होता है, CPU काम में नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import sys, time                                    # timing + build info
from concurrent.futures import ThreadPoolExecutor   # thread pool

def cpu(n: int) -> int:
    total = 0                                       # accumulator
    for i in range(n):                              # pure-Python loop holds the GIL
        total += i * i                              # CPU work
    return total

def timed(label: str, fn) -> float:
    start = time.perf_counter()                     # start clock
    fn()                                            # run the work
    took = time.perf_counter() - start              # elapsed seconds
    print(f"{label:<22} {took:.2f}s")               # show timing (varies per machine)
    return took

N = 3_000_000                                       # work per task

# ============================================
# TEST CASES
# ============================================

print("GIL enabled:", sys._is_gil_enabled())        # 3.13 API; True on the standard build
seq = timed("cpu sequential x4", lambda: [cpu(N) for _ in range(4)])
def threaded():
    with ThreadPoolExecutor(4) as ex:               # 4 threads
        list(ex.map(cpu, [N] * 4))                  # same 4 tasks
thr = timed("cpu 4 threads", threaded)

def io(_: int) -> None:
    time.sleep(0.2)                                 # sleeping releases the GIL
seq_io = timed("io sequential x4", lambda: [io(0) for _ in range(4)])
def threaded_io():
    with ThreadPoolExecutor(4) as ex:               # 4 threads
        list(ex.map(io, range(4)))                  # sleeps overlap
thr_io = timed("io 4 threads", threaded_io)

print("cpu threads no real speedup:", thr > seq * 0.7)  # no real speedup for CPU
print("io threads much faster:", thr_io < seq_io / 2)   # big speedup for I/O

# Expected output (timings VARY per machine; the ordering is what matters):
# GIL enabled: True
# cpu sequential x4      0.51s
# cpu 4 threads          0.48s      <- about the same as sequential
# io sequential x4       0.82s
# io 4 threads           0.21s      <- ~4x faster
# cpu threads no real speedup: True
# io threads much faster: True
```

---

## 🔍 Why This Works (3 lines max)
The GIL protects CPython's reference counts and internals. A running thread gives the lock up on blocking I/O or after a switch interval, so waiting threads interleave, but two threads never run Python bytecode at the same instant. Python 3.13 has an optional free-threaded build (no GIL), but the default build still has it.
हिंदी: Threads I/O wait में overlap होते हैं, CPU loop में नहीं; CPU parallelism के लिए processes चाहिए।

---

## ⚡ Alternative Solution
```python
import time                                          # timing
from concurrent.futures import ProcessPoolExecutor   # processes: one GIL each

def cpu(n: int) -> int:
    total = 0                                        # accumulator
    for i in range(n):                               # CPU-bound loop
        total += i * i                               # work
    return total

if __name__ == "__main__":                           # required for the spawn start method
    N = 3_000_000                                    # work per task
    start = time.perf_counter()                      # start clock
    _ = [cpu(N) for _ in range(4)]                   # sequential baseline
    seq = time.perf_counter() - start                # elapsed
    start = time.perf_counter()                      # restart clock
    with ProcessPoolExecutor(4) as ex:               # 4 worker processes
        list(ex.map(cpu, [N] * 4))                   # same 4 tasks in parallel
    par = time.perf_counter() - start                # elapsed
    print(f"sequential {seq:.2f}s, processes {par:.2f}s")  # timings vary
    print("processes faster:", par < seq)            # True on a multi-core machine

# Expected output (timings vary; process startup cost matters for small tasks):
# sequential 0.52s, processes 0.28s
# processes faster: True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: "the GIL means Python threads are useless / thread-safe"
# - Threads ARE useful for I/O-bound work (HTTP calls, DB, files).
# - The GIL does NOT make `counter += 1` atomic: it is load, add, store,
#   and a thread switch can happen between those steps (race condition).

# ✅ Correct: protect shared state with threading.Lock
import threading

counter = 0                                          # shared state
lock = threading.Lock()                              # guard

def work() -> None:
    global counter
    for _ in range(100_000):                         # many increments
        with lock:                                   # one thread at a time
            counter += 1                             # safe read-modify-write

threads = [threading.Thread(target=work) for _ in range(4)]
for t in threads: t.start()                          # start all
for t in threads: t.join()                           # wait for all
print(counter)

# Expected output:
# 400000
```

---

## 🎯 Interview Tip (1 line)
Say: "GIL = one bytecode-executing thread at a time; use threads/asyncio for I/O, multiprocessing (or C extensions like NumPy that release the GIL) for CPU, and Python 3.13's free-threaded build is experimental."

---

## 🔗 Related Questions
→ Q125 (fix thread race condition) | Q299 (threading vs multiprocessing vs asyncio) | Q124 (blocking call in async) | Q286 (asyncio for many connections)
