---

# Q284. Multiprocessing for CPU-bound Work
# Category: PERFORMANCE
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Run a CPU-heavy function on 4 inputs. Why don't threads speed it up in CPython, and how does `ProcessPoolExecutor` fix it?

---

## 💡 Quick Concept (2 lines only)
The GIL lets only one thread run Python bytecode at a time, so CPU-bound threads don't run in parallel. Processes have separate interpreters and GILs, so they use multiple cores (at the cost of pickling data and startup time).
हिंदी: GIL की वजह से threads CPU काम parallel नहीं करते; processes अलग cores पर चलते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time                                     # Step 1: for timing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor  # Step 2: pools

def cpu_task(n: int) -> int:                    # Step 3: pure-Python CPU work (must be top-level to pickle)
    total = 0                                   # accumulator
    for i in range(n):                          # busy loop
        total += i * i                          # arithmetic only, no I/O
    return total                                # result

def timed(fn):                                  # helper: run fn and return (result, seconds)
    start = time.perf_counter()                 # start clock
    result = fn()                               # run the work
    return result, time.perf_counter() - start  # elapsed seconds

if __name__ == "__main__":                      # Step 4: REQUIRED guard (spawn start method on macOS/Windows)
    inputs = [3_000_000] * 4                    # four equal chunks of work

    serial, t_serial = timed(lambda: [cpu_task(n) for n in inputs])  # baseline

    with ThreadPoolExecutor(max_workers=4) as tp:                    # threads (GIL-bound)
        threaded, t_thread = timed(lambda: list(tp.map(cpu_task, inputs)))

    with ProcessPoolExecutor(max_workers=4) as pp:                   # processes (parallel)
        pp.map(cpu_task, [10])                                       # warm-up: pay process start cost first
        processed, t_proc = timed(lambda: list(pp.map(cpu_task, inputs)))

    # ============================================
    # TEST CASES
    # ============================================
    print(serial == threaded == processed)      # Expected: True  (same answers)
    print(t_proc < t_serial)                    # Expected: True  (needs >1 CPU core)
    print(t_thread > t_serial * 0.7)            # Expected: True  (threads give no real speedup)
    # Measured on an 8-core Mac: serial ~0.8s, threads ~0.8s, processes ~0.2s (varies)
```

---

## 🔍 Why This Works (3 lines max)
Each worker process runs its own interpreter, so 4 tasks execute on 4 cores at once. Arguments/results are pickled between processes, so it pays off only when each task is heavy enough. Python 3.13 also has an experimental free-threaded build, but default builds still have the GIL.
हिंदी: हर process का अपना GIL होता है, इसलिए CPU काम सच में parallel चलता है।

---

## ⚡ Alternative Solution
```python
# multiprocessing.Pool with chunksize (good for many small tasks)
from multiprocessing import Pool                # classic API

def square(n: int) -> int:                      # tiny task (top-level so it can be pickled)
    return n * n                                # return the square

if __name__ == "__main__":                      # guard required
    with Pool(processes=2) as pool:             # 2 worker processes
        print(pool.map(square, range(10), chunksize=5))  # Expected: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no __main__ guard -> on spawn platforms each child re-imports the file
#    and tries to start more pools (RuntimeError: ... start a new process before
#    the current process has finished its bootstrapping phase). Not run here.
# from concurrent.futures import ProcessPoolExecutor
# with ProcessPoolExecutor() as pp:             # runs at import time in every child!
#     print(list(pp.map(abs, [-1, -2])))

# ✅ Correct: always wrap pool creation in the guard
from concurrent.futures import ProcessPoolExecutor  # pool import

if __name__ == "__main__":                      # only the parent runs this
    with ProcessPoolExecutor(max_workers=2) as pp:  # safe pool creation
        print(list(pp.map(abs, [-1, -2])))      # Expected: [1, 2]
```

---

## 🎯 Interview Tip (1 line)
Say: "CPU-bound -> multiprocessing (bypass GIL); I/O-bound -> threads or asyncio; and measure, because pickling and process startup can erase the gain for small tasks."

---

## 🔗 Related Questions
→ Q285 (threading for I/O) | Q286 (asyncio) | Q298 (the GIL) | Q299 (threading vs multiprocessing vs asyncio)
