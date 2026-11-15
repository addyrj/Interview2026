---

# Q299. Threading vs multiprocessing vs asyncio
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Run 5 simulated network calls (0.3s each) using threads, processes and asyncio, and explain when to pick each one.

```python
# NOT RUN (question stub)
# fetch("a"), fetch("b"), ... -> how long does each approach take?
```

---

## 💡 Quick Concept (2 lines only)
Threading = OS threads sharing memory (I/O-bound, GIL limits CPU). Multiprocessing = separate processes, each with its own GIL (CPU-bound). asyncio = ONE thread, cooperative `await` switching (huge numbers of I/O tasks).
हिंदी: I/O → threads/asyncio, CPU → multiprocessing; asyncio एक thread में `await` पर switch करता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

import asyncio, time                                          # async + timing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor  # pools

def fetch_sync(name: str) -> str:
    time.sleep(0.3)                                           # simulated blocking I/O
    return f"{name}:ok"                                       # fake response

async def fetch_async(name: str) -> str:
    await asyncio.sleep(0.3)                                  # simulated NON-blocking I/O
    return f"{name}:ok"                                       # fake response

async def run_asyncio(names: list[str]) -> list[str]:
    return await asyncio.gather(*(fetch_async(n) for n in names))  # all concurrently

def timed(label: str, fn) -> list[str]:
    start = time.perf_counter()                               # start clock
    result = fn()                                             # run strategy
    print(f"{label:<12} {time.perf_counter() - start:.1f}s {result}")  # timing varies
    return result

if __name__ == "__main__":                                    # needed for processes (spawn)
    names = ["a", "b", "c", "d", "e"]                         # 5 "requests"

    # ============================================
    # TEST CASES
    # ============================================

    timed("sequential", lambda: [fetch_sync(n) for n in names])        # baseline: ~1.5s

    def threads() -> list[str]:
        with ThreadPoolExecutor(5) as ex:                     # 5 threads
            return list(ex.map(fetch_sync, names))            # overlap the sleeps
    timed("threads", threads)

    def procs() -> list[str]:
        with ProcessPoolExecutor(5) as ex:                    # 5 processes
            return list(ex.map(fetch_sync, names))            # works, but heavy startup
    timed("processes", procs)

    timed("asyncio", lambda: asyncio.run(run_asyncio(names))) # 1 thread, 5 tasks

# Expected output (timings VARY; sequential ~1.5s, threads/asyncio ~0.3s, processes higher from startup cost):
# sequential   1.5s ['a:ok', 'b:ok', 'c:ok', 'd:ok', 'e:ok']
# threads      0.3s ['a:ok', 'b:ok', 'c:ok', 'd:ok', 'e:ok']
# processes    0.5s ['a:ok', 'b:ok', 'c:ok', 'd:ok', 'e:ok']
# asyncio      0.3s ['a:ok', 'b:ok', 'c:ok', 'd:ok', 'e:ok']
```

---

## 🔍 Why This Works (3 lines max)
For waiting, all three overlap the sleeps, so they take ~0.3s instead of 1.5s. The difference is cost and scale: asyncio tasks are cheap (thousands fit), threads cost ~MBs each and need locks, processes are heavy but the only option for CPU-bound Python code.
हिंदी: Waiting में तीनों तेज़ हैं; फर्क cost और scale का है; CPU काम सिर्फ processes में parallel चलता है।

---

## ⚡ Alternative Solution
```python
# Decision cheat-sheet as code
def choose(io_bound: bool, many_connections: bool, library_is_async: bool) -> str:
    if not io_bound:                                          # CPU-bound work
        return "multiprocessing (or NumPy/C extension)"       # bypass the GIL
    if many_connections and library_is_async:                 # e.g. 10k sockets, httpx/aiohttp
        return "asyncio"                                      # lowest overhead
    return "threading"                                        # blocking libs (requests, DB drivers)

print(choose(False, False, False))
print(choose(True, True, True))
print(choose(True, False, False))

# Expected output:
# multiprocessing (or NumPy/C extension)
# asyncio
# threading
```

---

## ⚠️ Common Mistake
```python
import asyncio, time                                          # imports

# ❌ Wrong: blocking call inside async code freezes the whole event loop
async def bad(n: int) -> int:
    time.sleep(0.2)                                           # blocks the only thread!
    return n

# ✅ Correct: await a non-blocking call, or push blocking code to a thread
async def good(n: int) -> int:
    await asyncio.to_thread(time.sleep, 0.2)                  # runs in a worker thread
    return n

async def main() -> None:
    for fn in (bad, good):                                    # compare both
        start = time.perf_counter()                           # start clock
        await asyncio.gather(*(fn(i) for i in range(5)))      # 5 "concurrent" tasks
        print(fn.__name__, f"{time.perf_counter() - start:.1f}s")  # timing varies

asyncio.run(main())

# Expected output (timings vary):
# bad 1.0s     <- serialized, no concurrency at all
# good 0.2s    <- concurrent
```

---

## 🎯 Interview Tip (1 line)
Say: "I/O-bound and many connections: asyncio; I/O-bound with blocking libraries: threads; CPU-bound: multiprocessing. Never block the event loop."

---

## 🔗 Related Questions
→ Q298 (the GIL) | Q091 (implement asyncio.gather) | Q124 (blocking call in async) | Q286 (asyncio for many connections)
