---

# Q164. Explain the GIL with Example
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What is the GIL? Show with code that threads do not speed up CPU-bound work but do help I/O-bound work, and what to use instead.

---

## 💡 Quick Concept (2 lines only)
The Global Interpreter Lock lets only ONE thread run Python bytecode at a time in standard CPython; it is released during blocking I/O and in many C extensions.
हिंदी: GIL की वजह से एक समय में सिर्फ़ एक thread Python bytecode चलाता है — CPU काम में threads तेज़ नहीं होते, I/O में होते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time                                         # Step 1: measure time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor   # Step 2: pools

def cpu_task(n: int) -> int:                        # Step 3: CPU-bound work (holds the GIL)
    total = 0                                       # accumulator
    for i in range(n):                              # pure-Python loop
        total += i * i                              # arithmetic only
    return total                                    # result

def io_task(_: int) -> None:                        # Step 4: I/O-bound work (releases the GIL)
    time.sleep(0.2)                                 # simulated network wait

def timed(label: str, fn) -> float:                 # Step 5: tiny timing helper
    start = time.perf_counter()                     # start clock
    fn()                                            # run the experiment
    elapsed = time.perf_counter() - start           # elapsed seconds
    print(f"{label}: {elapsed:.2f}s")               # print it
    return elapsed                                  # return for comparison

def run_cpu(pool_cls, workers: int = 4, n: int = 3_000_000) -> None:   # 4 CPU jobs
    with pool_cls(max_workers=workers) as pool:     # create the pool
        list(pool.map(cpu_task, [n] * 4))           # run 4 jobs and wait

def run_io(workers: int) -> None:                   # 4 sleeping jobs
    with ThreadPoolExecutor(max_workers=workers) as pool:   # threads
        list(pool.map(io_task, range(4)))           # run and wait

if __name__ == "__main__":                          # needed for multiprocessing on macOS/Windows
    # ============================================
    # TEST CASES  (timings vary per machine; relative order is what matters)
    # ============================================
    # One real run (multi-core Mac, Python 3.13.3; YOUR numbers will differ):
    #   CPU sequential: 0.53s | CPU 4 threads : 0.56s | CPU 4 procs   : 0.21s
    #   IO  1 thread  : 0.83s | IO  4 threads : 0.21s
    seq = timed("CPU sequential", lambda: run_cpu(ThreadPoolExecutor, workers=1))   # 1 thread
    thr = timed("CPU 4 threads ", lambda: run_cpu(ThreadPoolExecutor, workers=4))   # no gain
    prc = timed("CPU 4 procs   ", lambda: run_cpu(ProcessPoolExecutor, workers=4))  # real parallelism
    io1 = timed("IO  1 thread  ", lambda: run_io(1))                                # 4 x 0.2s
    io4 = timed("IO  4 threads ", lambda: run_io(4))                                # ~0.2s
    print("threads ~= sequential for CPU:", thr > seq * 0.7)   # Expected: True
    print("processes faster for CPU:", prc < seq)              # Expected: True (needs several cores)
    print("threads faster for IO:", io4 < io1 / 2)             # Expected: True
```

---

## 🔍 Why This Works (3 lines max)
CPU-bound threads fight over the GIL, so 4 threads take about as long as 1. `time.sleep` (and socket reads, file I/O) release the GIL, so I/O threads overlap. Processes each have their own interpreter and GIL, so they run truly in parallel.
हिंदी: Processes के पास अपना-अपना GIL होता है, इसलिए CPU काम के लिए `multiprocessing` चुनो।

---

## ⚡ Alternative Solution
```python
# asyncio: single thread, no GIL contention, great for many I/O waits
import asyncio                                      # event loop
import time                                         # timer

async def fake_io(i: int) -> int:                   # simulated I/O coroutine
    await asyncio.sleep(0.2)                        # yields control while "waiting"
    return i                                        # result

async def main() -> None:                           # driver
    start = time.perf_counter()                     # start clock
    results = await asyncio.gather(*(fake_io(i) for i in range(100)))   # 100 waits at once
    print(len(results), f"{time.perf_counter() - start:.1f}s")          # Expected: 100 0.2s (about)

asyncio.run(main())                                 # run

# Other escapes: C extensions that release the GIL (NumPy), or the free-threaded
# build of Python 3.13 (python3.13t, experimental, GIL disabled).
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: "add threads to make CPU code faster"
#   ThreadPoolExecutor(8).map(cpu_task, jobs)   -> no speedup (often slightly slower)

# ❌ Wrong: "the GIL makes my code thread-safe"
counter = 0
def inc():
    global counter
    for _ in range(100_000):
        counter += 1          # read + add + write: NOT atomic, a thread switch can lose updates

# ✅ Correct: use multiprocessing/ProcessPoolExecutor for CPU work, a threading.Lock for shared state
```

---

## 🎯 Interview Tip (1 line)
Say: "GIL = one bytecode thread at a time in CPython; threads/asyncio for I/O-bound, multiprocessing for CPU-bound, and locks are still needed for shared state."

---

## 🔗 Related Questions
→ Q125 (fix thread race) | Q284 (multiprocessing) | Q285 (threading for I/O) | Q298 (GIL classic) | Q299 (threading vs multiprocessing vs asyncio)
