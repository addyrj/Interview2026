---

# 260. Performance Comparison
# हिंदी में: Performance तुलना (Sequential बनाम asyncio बनाम Threads बनाम Processes)

---

## 🔵 Simple Definition (English)
This topic measures how fast the same work runs in four styles: one after another (sequential), `asyncio`, threads, and processes. For waiting work (I/O) asyncio and threads win. For computing work (CPU) only processes win. Real numbers beat opinions, so always benchmark.

## 🔵 सरल परिभाषा (Hindi)
यह topic एक ही काम को चार तरीकों में चलाकर उसकी गति नापता है: एक के बाद एक (sequential), `asyncio`, threads और processes। इंतजार वाले काम (I/O) में asyncio और threads जीतते हैं। गणना वाले काम (CPU) में सिर्फ processes जीतते हैं। असली आंकड़े राय से बेहतर हैं, इसलिए हमेशा benchmark करें।

---

## 🔴 Problem it Solves
Teams argue "async is faster" or "threads are enough" without data. Wrong choices cost money: an I/O-heavy service stuck on sequential code needs 10x more servers, and a CPU-heavy service using threads gets no speedup at all. A small, honest benchmark shows which bottleneck you have and which tool fixes it.

## 🔴 यह क्यों बना? (Hindi)
Teams बिना data के बहस करती हैं: "async तेज़ है" या "threads काफी हैं"। गलत चुनाव में पैसा लगता है: sequential code पर अटकी I/O-भारी service को 10 गुना ज्यादा servers चाहिए, और threads इस्तेमाल करने वाली CPU-भारी service को कोई speedup नहीं मिलता। एक छोटा ईमानदार benchmark बताता है कि आपका bottleneck क्या है और कौन सा tool उसे ठीक करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define ONE workload (e.g. 50 HTTP calls, or 8 CPU jobs)
Step 2 → Run it sequentially to get a baseline
Step 3 → Run it with asyncio, threads, processes (same total work)
Step 4 → Time each with time.perf_counter() (monotonic, high resolution)
Step 5 → Repeat a few times; report the typical value, not the best
Step 6 → Compare: speedup = baseline_time / new_time
Step 7 → Choose the simplest tool that meets your target, then re-measure in production
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक ही workload तय करो (जैसे 50 HTTP calls, या 8 CPU jobs)
Step 2 → Baseline के लिए उसे sequentially चलाओ
Step 3 → वही कुल काम asyncio, threads, processes से चलाओ
Step 4 → हर एक को time.perf_counter() से नापो (monotonic, high resolution)
Step 5 → कुछ बार दोहराओ; सबसे अच्छा नहीं, सामान्य मान बताओ
Step 6 → तुलना: speedup = baseline_time / new_time
Step 7 → लक्ष्य पूरा करने वाला सबसे सरल tool चुनो, फिर production में फिर से नापो
```

---

## 🟡 Real World Example
An e-commerce price-checker calls 50 supplier APIs per product page. Sequentially, at 100 ms each, a page takes 5 s. With `asyncio.gather` it takes about 100 ms, a 50x speedup with no extra servers. The same company's nightly job that generates 8 thumbnail sizes per photo is CPU-bound: threads give nothing, so they use a process pool and finish in about a third of the time on 8 cores.

## 🟡 Real Example Hindi mein
E-commerce price-checker हर product page पर 50 supplier APIs बुलाता है। Sequentially, हर 100 ms पर, एक page 5 सेकंड लेता है। `asyncio.gather` से लगभग 100 ms, यानी 50 गुना speedup बिना अतिरिक्त servers के। उसी कंपनी का रात का job जो हर photo के 8 thumbnail sizes बनाता है CPU-bound है: threads से कुछ नहीं मिलता, इसलिए वे process pool इस्तेमाल करते हैं और 8 cores पर लगभग एक तिहाई समय में खत्म करते हैं।

---

## 💻 Code Example — Basic
```python
# Benchmark 1: I/O-bound — 50 HTTP calls to a local server that answers after 50 ms
# (verified: Python 3.13, aiohttp 3.14, 8-core Mac; numbers vary by machine)
import asyncio                                           # event loop
import time                                              # timer
import urllib.request                                    # BLOCKING http client (stdlib)
from concurrent.futures import ThreadPoolExecutor        # threads
import aiohttp                                           # async http client
from aiohttp import web                                  # tiny local server

N: int = 50                                              # number of requests
URL: str = "http://127.0.0.1:34160/"                     # local server URL


async def handler(request: web.Request) -> web.Response:
    await asyncio.sleep(0.05)                            # server "works" for 50 ms
    return web.Response(text="ok")                       # reply


def blocking_get(_: int) -> int:                         # sync request
    with urllib.request.urlopen(URL) as r:               # blocks this thread
        return len(r.read())                             # bytes received


async def async_get(session: aiohttp.ClientSession, _: int) -> int:
    async with session.get(URL) as r:                    # non-blocking request
        return len(await r.read())                       # bytes received


async def main() -> None:
    app: web.Application = web.Application()             # build server
    app.router.add_get("/", handler)                     # route
    runner: web.AppRunner = web.AppRunner(app)           # runner
    await runner.setup()                                 # prepare
    await web.TCPSite(runner, "127.0.0.1", 34160).start()   # listen
    loop = asyncio.get_running_loop()                    # for run_in_executor

    t: float = time.perf_counter()                       # --- asyncio
    async with aiohttp.ClientSession() as s:             # one shared session
        await asyncio.gather(*(async_get(s, i) for i in range(N)))   # 50 at once
    print(f"asyncio    {N} requests: {time.perf_counter() - t:.2f}s")

    t = time.perf_counter()                              # --- threads
    with ThreadPoolExecutor(N) as ex:                    # 50 threads
        await asyncio.gather(*(loop.run_in_executor(ex, blocking_get, i) for i in range(N)))
    print(f"threads    {N} requests: {time.perf_counter() - t:.2f}s")

    t = time.perf_counter()                              # --- sequential (only 5 requests!)
    for i in range(5):                                   # one after another
        await loop.run_in_executor(None, blocking_get, i)
    print(f"sequential 5 requests: {time.perf_counter() - t:.2f}s")
    await runner.cleanup()                               # stop server


asyncio.run(main())                                      # run

# Output (typical):
# asyncio    50 requests: 0.06s
# threads    50 requests: 0.08s
# sequential 5 requests: 0.26s      <- 5 requests alone take 0.26 s; 50 would take ~2.6 s
```

## 💻 Code Example — Advanced
```python
# Benchmark 2: CPU-bound — 8 jobs of pure-Python maths
# (verified: Python 3.13 standard build WITH the GIL, 8-core Mac)
import time                                              # timer
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor   # pools


def cpu(n: int) -> int:                                  # holds the GIL while computing
    return sum(i * i for i in range(n))                  # sum of squares


def bench(label: str, fn) -> None:                       # time any function
    t: float = time.perf_counter()                       # start
    fn()                                                 # run
    print(f"{label}: {time.perf_counter() - t:.2f}s")    # seconds


if __name__ == "__main__":                               # required for process pools
    M, JOBS = 3_000_000, 8                               # job size, job count

    def threads() -> None:
        with ThreadPoolExecutor(JOBS) as ex:             # 8 threads
            list(ex.map(cpu, [M] * JOBS))                # same work in threads

    def procs() -> None:
        with ProcessPoolExecutor(JOBS) as ex:            # 8 processes
            list(ex.map(cpu, [M] * JOBS))                # same work in processes

    bench("cpu sequential", lambda: [cpu(M) for _ in range(JOBS)])   # baseline
    bench("cpu threads   ", threads)                     # GIL: no real gain
    bench("cpu processes ", procs)                       # real parallelism

# Output (typical, two runs gave 1.12/1.07/0.43 and 1.16/1.10/0.41):
# cpu sequential: 1.12s
# cpu threads   : 1.07s       <- ~1.0x, no speedup
# cpu processes : 0.43s       <- ~2.6x on 8 cores (start-up + pickling overhead; bigger jobs scale better)
```

Results summary (this machine):

| Workload | Sequential | asyncio | Threads | Processes |
|----------|-----------|---------|---------|-----------|
| 50 I/O calls (50 ms each) | ~2.6 s (extrapolated from 5 calls = 0.26 s) | 0.06 s | 0.08 s | not needed |
| 8 CPU jobs | 1.12 s | n/a (blocks loop) | 1.07 s | 0.43 s |

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript (Node) |
|---------|--------|------------------|
| 50 I/O calls concurrently | `asyncio.gather` | `Promise.all` |
| Timing | `time.perf_counter()` | `performance.now()` / `console.time` |
| CPU parallelism | `ProcessPoolExecutor` | `worker_threads` |
| Threads speed up CPU? | NO (GIL) | YES with workers (separate isolates) |
| Benchmarks tool | `timeit`, `pytest-benchmark` | `benchmark.js`, `tinybench` |

```python
# Python way
t = time.perf_counter()
await asyncio.gather(*(fetch(i) for i in range(50)))
print(time.perf_counter() - t)
```
```javascript
// JavaScript way
const t = performance.now();
await Promise.all(Array.from({ length: 50 }, (_, i) => fetchOne(i)));
console.log(performance.now() - t);
```

Key difference: for I/O the two languages perform similarly because both use an event loop. For CPU work Node's `worker_threads` give real parallel threads, while Python needs separate processes (or the experimental free-threaded 3.13 build).

---

## 🟠 FastAPI Connection
In FastAPI the same comparison decides how you write each endpoint: `async def` with async libraries for I/O, plain `def` for blocking libraries (FastAPI runs them in a thread pool), and a process pool or a task queue (Celery/RQ/Arq) for CPU work. A blocking call inside `async def` is the worst case: it blocks the whole loop.

```python
# FastAPI example — measure the damage of blocking the event loop
import asyncio                                           # sleep
import time                                              # blocking sleep
import httpx                                             # test client
from fastapi import FastAPI                              # FastAPI

app: FastAPI = FastAPI()                                 # app


@app.get("/good")                                        # non-blocking
async def good() -> dict[str, str]:
    await asyncio.sleep(0.2)                             # yields to the loop
    return {"ok": "good"}                                # reply


@app.get("/bad")                                         # blocks the loop!
async def bad() -> dict[str, str]:
    time.sleep(0.2)                                      # freezes every other request
    return {"ok": "bad"}                                 # reply


async def hit(path: str, n: int = 10) -> float:
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://t") as c:
        t: float = time.perf_counter()                   # start
        await asyncio.gather(*(c.get(path) for _ in range(n)))   # n parallel requests
        return time.perf_counter() - t                   # elapsed


async def main() -> None:
    print(f"good: {await hit('/good'):.1f}s")            # about 0.2 s
    print(f"bad : {await hit('/bad'):.1f}s")             # about 2.0 s (10 x 0.2, one after another)


asyncio.run(main())                                      # run

# Output (verified, typical):
# good: 0.2s
# bad : 2.1s
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Benchmarking once, or including start-up in the timing
✅ Correct: warm up, repeat, and time only the work

```python
# Wrong — one run, includes imports and process start-up noise
t = time.time(); run(); print(time.time() - t)
# Right
t = time.perf_counter(); run(); print(time.perf_counter() - t)   # repeat several times
```

❌ Mistake 2: Comparing different amounts of work
✅ Correct: the SAME total work in every variant

```python
# Wrong — sequential does 5 jobs, asyncio does 50
# Right — both do 50 (or state clearly why extrapolating, as in the table above)
```

❌ Mistake 3: Using more workers than makes sense
✅ Correct: processes ≈ CPU cores; threads/async limited by the server (use a Semaphore)

```python
# Wrong — 1000 processes on 8 cores: memory explosion and slower
ProcessPoolExecutor(1000)
# Right
ProcessPoolExecutor(max_workers=os.cpu_count())
```

---

## 🧠 Tricky Interview Question

```python
# Which is faster for 4 CPU-bound jobs? Rank them.
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu(n: int) -> int:
    return sum(i * i for i in range(n))

async def with_asyncio() -> None:
    await asyncio.gather(*(asyncio.to_thread(cpu, 3_000_000) for _ in range(4)))
```
Answer: Processes are fastest. Sequential, threads and `asyncio.to_thread` come out about equal (measured: 0.57 s, 0.54 s vs 0.27 s for processes with 4 jobs). `asyncio.to_thread` just uses a thread, so the GIL still allows only one thread to run Python bytecode at a time. Async concurrency does not give parallel CPU. For real parallelism: `loop.run_in_executor(ProcessPoolExecutor(), cpu, n)`. (On a free-threaded Python 3.13t build threads could also scale, but that build is experimental.)

---

## ⚫ Interview Questions + Answers

Q1: Why are 50 asyncio requests nearly as fast as 1 request?
A1: The time is spent waiting on the network, not computing. While one request waits, the event loop starts the others, so all 50 wait together: total ≈ slowest single request.

Q2: Why are threads slightly slower than asyncio in the benchmark?
A2: Each thread costs memory and OS scheduling, and Python switches between threads under the GIL. asyncio switches only at `await` inside one thread, which is much cheaper. At 10,000 connections the gap becomes huge.

Q3: Why did processes give only ~2.6x on 8 cores?
A3: Process start-up, pickling arguments/results and the machine's real core mix (performance vs efficiency cores) limit scaling. Longer jobs scale closer to the core count.

Q4: How do you benchmark properly?
A4: Use `time.perf_counter()` or `timeit`, repeat runs, keep the same workload, test with realistic data, and measure p95/p99 latency in production for services, not only averages.

Q5: Does async speed up a single request?
A5: No. It improves throughput (many requests at once), not the latency of one request. One slow query still takes the same time.

---

## 🔷 When to Use + When Not to Use
✅ Use benchmarks when:
- Choosing between asyncio, threads and processes
- Justifying a refactor to async
- Sizing worker/pool counts

❌ Avoid when:
- Optimizing before you know the bottleneck (profile first with `cProfile`)
- Micro-benchmarks that do not match real workloads
- Comparing runs on different machines or loads

---

## 📊 Visual Diagram
```
I/O-bound, 50 calls x 100ms
sequential : ████████████████████████████████████████████  5.0 s
threads    : █                                              0.1 s
asyncio    : █                                              0.1 s

CPU-bound, 8 jobs (8 cores)
sequential : ████████████████████████  1.12 s
threads    : ███████████████████████   1.07 s   (GIL)
processes  : ██████████                0.43 s

Rule:  waiting  -> asyncio / threads
       computing -> processes
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Throughput | Work done per second | प्रति सेकंड किया गया काम |
| Latency | Time for one request | एक request का समय |
| Speedup | baseline time / new time | baseline समय / नया समय |
| Benchmark | Measure speed with real runs | असली runs से गति नापना |
| p95 / p99 | Slowest 5% / 1% latency | सबसे धीमे 5% / 1% का समय |
| Overhead | Extra cost of the tool itself | tool का अपना अतिरिक्त खर्च |

---

## ⚡ 3-Line Summary
English: Measured here: asyncio and threads turn 50 waiting calls into about one call's time, while only processes speed up CPU-bound Python (about 2.6x on 8 cores for these jobs). Blocking the event loop in `async def` ruins everything, so always measure.
Hindi: यहां नापा गया: asyncio और threads 50 इंतजार वाली calls को लगभग एक call के समय में कर देते हैं, जबकि CPU-bound Python सिर्फ processes से तेज होता है (इन jobs में 8 cores पर लगभग 2.6 गुना)। `async def` में event loop को block करना सब बिगाड़ देता है, इसलिए हमेशा नापें।

---

## ➡️ Next Topic
**261.** The next topic in the async-concurrency series, after this performance comparison (see the topic index in `How.md`).
