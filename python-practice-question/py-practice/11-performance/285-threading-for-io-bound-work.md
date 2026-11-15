---

# Q285. Threading for I/O-bound Work
# Category: PERFORMANCE
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fetch 10 "URLs" where each call waits 0.2 seconds (simulated with `time.sleep`). Sequentially it takes ~2s. Make it take ~0.2s with threads. Why does it work despite the GIL?

---

## 💡 Quick Concept (2 lines only)
Blocking I/O (network, disk, `sleep`) releases the GIL while waiting, so other threads run meanwhile. Waiting overlaps; total time ≈ the slowest call, not the sum.
हिंदी: I/O में wait के समय GIL छूट जाता है, इसलिए threads का wait एक साथ overlap होता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import time                                     # Step 1: sleep + timing
from concurrent.futures import ThreadPoolExecutor  # Step 2: thread pool

def fake_fetch(url_id: int) -> str:             # Step 3: simulated blocking I/O call
    time.sleep(0.2)                             # releases the GIL while waiting
    return f"page-{url_id}"                     # pretend response body

ids = list(range(10))                           # ten "URLs"

start = time.perf_counter()                     # Step 4: sequential baseline
seq = [fake_fetch(i) for i in ids]              # one after another
t_seq = time.perf_counter() - start             # ~2.0s

start = time.perf_counter()                     # Step 5: threaded version
with ThreadPoolExecutor(max_workers=10) as pool:  # 10 threads
    par = list(pool.map(fake_fetch, ids))       # results keep input order
t_par = time.perf_counter() - start             # ~0.2s

# ============================================
# TEST CASES
# ============================================
print(seq == par)                               # Expected: True
print(par[:3])                                  # Expected: ['page-0', 'page-1', 'page-2']
print(t_seq > 1.8)                              # Expected: True  (about 2.0s)
print(t_par < 0.6)                              # Expected: True  (about 0.2s; timings vary)
```

---

## 🔍 Why This Works (3 lines max)
`time.sleep` (like socket reads and file I/O) drops the GIL, so all 10 waits happen concurrently. `pool.map` returns results in input order even if threads finish out of order. Threads are heavier than coroutines (~MBs of stack each), so use asyncio for thousands of connections.
हिंदी: Wait के दौरान GIL छूटता है, इसलिए 10 calls साथ-साथ इंतज़ार करती हैं।

---

## ⚡ Alternative Solution
```python
# as_completed: handle results as soon as each one finishes
import time                                     # sleep
from concurrent.futures import ThreadPoolExecutor, as_completed  # pool + iterator

def fake_fetch(n: int) -> str:                  # simulated call, later ids finish sooner
    time.sleep(0.3 - n * 0.1)                   # id 0 -> 0.3s, id 1 -> 0.2s, id 2 -> 0.1s
    return f"page-{n}"                          # response

with ThreadPoolExecutor(max_workers=3) as pool:  # 3 threads
    futures = [pool.submit(fake_fetch, n) for n in range(3)]  # start all
    print([f.result() for f in as_completed(futures)])  # Expected: ['page-2', 'page-1', 'page-0']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using threads for CPU-bound work expecting speedup (GIL blocks it)
# ❌ Wrong: shared counter without a lock -> race condition
import threading                                # threading import

counter = 0                                     # shared state
lock = threading.Lock()                         # protects the counter

def work() -> None:                             # increments the counter
    global counter                              # modify module-level variable
    for _ in range(100_000):                    # many increments
        with lock:                              # ✅ correct: guard read-modify-write
            counter += 1                        # not atomic without the lock

threads = [threading.Thread(target=work) for _ in range(4)]  # four threads
for t in threads: t.start()                     # start them
for t in threads: t.join()                      # wait for all
print(counter)                                  # Expected: 400000
```

---

## 🎯 Interview Tip (1 line)
Say: "Threads are fine for I/O-bound work because blocking calls release the GIL; I use ThreadPoolExecutor and protect shared state with locks."

---

## 🔗 Related Questions
→ Q284 (multiprocessing) | Q286 (asyncio) | Q125 (thread race condition) | Q298 (the GIL)
