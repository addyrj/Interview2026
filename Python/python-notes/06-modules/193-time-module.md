---

# 193. time Module
# हिंदी में: time Module (घड़ी, sleep और समय मापना)

---

## 🔵 Simple Definition (English)
`time` gives low level access to clocks: the current Unix timestamp (`time.time()`), a precise timer for measuring code (`perf_counter`), a clock that never goes back (`monotonic`), the ability to pause (`sleep`), and simple formatting of timestamps (`strftime`). For calendar dates and time zones use `datetime`.

## 🔵 सरल परिभाषा (Hindi)
`time` घड़ियों तक low level पहुँच देता है: मौजूदा Unix timestamp (`time.time()`), code मापने के लिए सटीक timer (`perf_counter`), कभी पीछे न जाने वाली घड़ी (`monotonic`), रुकना (`sleep`) और timestamps की सरल formatting (`strftime`)। Calendar dates और time zones के लिए `datetime` इस्तेमाल करें।

---

## 🔴 Problem it Solves
You need to answer "how long did this take?", "wait 2 seconds before retry", and "what is the timestamp right now?". Using the wall clock (`time.time`) for durations is wrong because the system clock can jump (NTP sync, manual change, daylight saving). `time` offers separate clocks for separate jobs.

## 🔴 यह क्यों बना? (Hindi)
आपको जवाब चाहिए: "इसमें कितना समय लगा?", "retry से पहले 2 सेकंड रुको", "अभी का timestamp क्या है?"। Duration के लिए wall clock (`time.time`) गलत है क्योंकि system clock कूद सकती है (NTP sync, हाथ से बदलाव, daylight saving)। `time` अलग कामों के लिए अलग घड़ियाँ देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → time.time()          wall clock, float seconds since 1970 UTC (can jump)
Step 2 → time.monotonic()     steady clock for timeouts / deadlines (never goes back)
Step 3 → time.perf_counter()  highest resolution, for benchmarking short code
Step 4 → time.process_time()  CPU time of this process (sleep is NOT counted)
Step 5 → time.sleep(s)        pauses ONLY the calling thread
Step 6 → gmtime / localtime → struct_time → strftime(fmt, struct) → text
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → time.time()          wall clock, 1970 UTC से float seconds (कूद सकती है)
Step 2 → time.monotonic()     timeouts / deadlines के लिए स्थिर घड़ी (पीछे नहीं जाती)
Step 3 → time.perf_counter()  सबसे ज़्यादा resolution, छोटे code के benchmark के लिए
Step 4 → time.process_time()  इस process का CPU time (sleep गिना नहीं जाता)
Step 5 → time.sleep(s)        सिर्फ calling thread को रोकता है
Step 6 → gmtime / localtime → struct_time → strftime(fmt, struct) → text
```

---

## 🟡 Real World Example
A Razorpay client retries a failed webhook delivery after 1s, 2s, 4s (`sleep` with backoff). A FastAPI middleware measures each request with `perf_counter` and sends it to Prometheus. A batch job polls a payment status until a `monotonic` deadline of 30 seconds is reached. An AI app logs how long each LLM call took.

## 🟡 Real Example Hindi mein
Razorpay client fail हुई webhook delivery को 1s, 2s, 4s बाद दोबारा भेजता है (backoff के साथ `sleep`)। FastAPI middleware हर request को `perf_counter` से मापकर Prometheus को भेजता है। Batch job payment status को 30 सेकंड की `monotonic` deadline तक poll करती है। AI app log करती है कि हर LLM call में कितना समय लगा।

---

## 💻 Code Example — Basic
```python
# Basic time examples - every line commented (values that change are shown as checks)
import time  # standard time library

now: float = time.time()  # seconds since 1970-01-01 UTC (the "epoch"), as float
print(type(now).__name__, now > 1_700_000_000)  # float True

print(time.gmtime(0))  # struct_time for the epoch itself (UTC)
print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(86400)))  # epoch + 1 day
print(time.strftime("%d %b %Y", time.gmtime(1_735_689_600)))  # fixed timestamp -> text
parsed = time.strptime("2025-11-10 09:30", "%Y-%m-%d %H:%M")  # text -> struct_time
print(parsed.tm_year, parsed.tm_mon, parsed.tm_mday, parsed.tm_hour)  # fields

start: float = time.perf_counter()  # high resolution timer for measuring
time.sleep(0.2)  # pause this thread for 0.2 seconds
elapsed: float = time.perf_counter() - start  # difference is the duration
print(0.19 < elapsed < 0.5)  # True (exact value varies)

m0: float = time.monotonic()  # clock that never goes backwards
time.sleep(0.05)  # small pause
print(time.monotonic() > m0)  # always True

ns: int = time.time_ns()  # integer nanoseconds (no float rounding)
print(type(ns).__name__, ns > 10**18)  # int True

cpu: float = time.process_time()  # CPU time of this process (sleep not counted)
print(cpu >= 0)  # True

print(time.get_clock_info("perf_counter").monotonic)  # True: perf_counter is monotonic
print(isinstance(time.localtime().tm_isdst, int))  # local time uses the machine time zone
```

Output (verified by running; ids/timestamps/paths may vary):
```
float True
time.struct_time(tm_year=1970, tm_mon=1, tm_mday=1, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3, tm_yday=1, tm_isdst=0)
1970-01-02 00:00:00
01 Jan 2025
2025 11 10 9
True
True
int True
True
True
True
```

## 💻 Code Example — Advanced
```python
# Production style: timer context manager, decorator, retry with backoff, timeouts, deadline
import functools  # wraps decorators
import time  # clocks
from contextlib import contextmanager  # context manager helper
from typing import Any, Callable, Iterator, Tuple, Type, TypeVar  # type hints

F = TypeVar("F", bound=Callable[..., Any])  # any function type


@contextmanager
def timer(label: str, sink: list) -> Iterator[None]:
    """Measure a block with perf_counter and store the result."""
    start: float = time.perf_counter()  # begin
    try:  # run the block
        yield  # caller code runs here
    finally:  # always record, even on error
        sink.append((label, time.perf_counter() - start))  # save duration


def timed(fn: F) -> F:
    """Decorator that adds .last_duration to the function."""
    @functools.wraps(fn)  # keep name/docstring
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        t0: float = time.perf_counter()  # start
        try:  # call real function
            return fn(*args, **kwargs)  # result passes through
        finally:  # record time
            wrapper.last_duration = time.perf_counter() - t0  # type: ignore[attr-defined]
    return wrapper  # type: ignore[return-value]


def retry(attempts: int, base_delay: float, exc: Tuple[Type[BaseException], ...] = (Exception,)) -> Callable[[F], F]:
    """Retry with exponential backoff: 0.01, 0.02, 0.04 ..."""
    def deco(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for i in range(attempts):  # try several times
                try:  # call
                    return fn(*args, **kwargs)  # success -> return
                except exc:  # allowed failure
                    if i == attempts - 1:  # last try
                        raise  # give up
                    time.sleep(base_delay * (2 ** i))  # wait longer each time
        return wrapper  # type: ignore[return-value]
    return deco


results: list = []  # collected timings
with timer("sleep", results):  # time a block
    time.sleep(0.1)  # work
print(results[0][0], 0.09 < results[0][1] < 0.4)  # sleep True


@timed
def work() -> int:
    time.sleep(0.05)  # pretend work
    return 42  # result


print(work(), work.last_duration > 0.04)  # 42 True

calls: list = []  # count attempts


@retry(attempts=3, base_delay=0.01, exc=(ConnectionError,))
def flaky() -> str:
    calls.append(1)  # record the call
    if len(calls) < 3:  # fail twice
        raise ConnectionError("temporary")  # transient failure
    return "ok"  # third time works


print(flaky(), len(calls))  # ok 3

deadline: float = time.monotonic() + 0.15  # absolute deadline (monotonic!)
loops: int = 0  # how many loops fit
while time.monotonic() < deadline:  # poll until time is up
    loops += 1  # work
    time.sleep(0.03)  # wait a bit
print(3 <= loops <= 6)  # True (machine dependent)

print(time.strftime("%H:%M:%S", time.gmtime(3725)))  # seconds -> hh:mm:ss : 01:02:05
print(f"{time.perf_counter_ns() % 1000 >= 0}")  # *_ns functions give exact integers
```

Output (verified by running; ids/timestamps/paths may vary):
```
sleep True
42 True
ok 3
True
01:02:05
True
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
import time
start = time.perf_counter()
time.sleep(1)                       # BLOCKS the thread
print(time.perf_counter() - start)  # ~1.0
print(time.time())                  # seconds (float)
```

```javascript
// JavaScript
const start = performance.now();
await new Promise(r => setTimeout(r, 1000));   // non blocking wait
console.log(performance.now() - start);        // ~1000 (milliseconds)
console.log(Date.now());                        // milliseconds (integer)
```

Key differences: Python measures in seconds (float), JavaScript in milliseconds. `time.sleep` blocks the whole thread, while `setTimeout` schedules a callback and never blocks. In async Python use `await asyncio.sleep()`; `time.sleep` inside `async def` freezes the event loop. `perf_counter` is the equivalent of `performance.now()`.

---

## 🟠 FastAPI Connection
FastAPI uses `perf_counter` in middleware to expose request latency (the `X-Process-Time` header from the official tutorial). Inside `async def` endpoints never use `time.sleep`; use `await asyncio.sleep`. In plain `def` endpoints FastAPI runs the function in a threadpool, so `time.sleep` blocks only that worker thread, but it still wastes a thread.

```python
# FastAPI: request timing middleware (pip install fastapi httpx)
import time  # clock
from typing import Awaitable, Callable, Dict  # type hints
from fastapi import FastAPI, Request, Response  # app + request

app: FastAPI = FastAPI()  # create app


@app.middleware("http")  # runs around every request
async def add_process_time(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start: float = time.perf_counter()  # start timer
    response: Response = await call_next(request)  # run the endpoint
    ms: float = (time.perf_counter() - start) * 1000  # duration in ms
    response.headers["X-Process-Time-Ms"] = f"{ms:.2f}"  # expose it
    return response  # send back


@app.get("/slow")  # GET /slow
async def slow() -> Dict[str, str]:
    import asyncio  # async sleep (time.sleep would BLOCK the event loop)
    await asyncio.sleep(0.05)  # non blocking wait
    return {"status": "done"}  # response
```

Output (verified by running; ids/timestamps/paths may vary):
```
{'status': 'done'} True
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Measuring durations with `time.time()`
```python
# Wrong - system clock can jump (NTP), giving negative or huge durations
# start = time.time(); ...; took = time.time() - start

# Correct
# start = time.perf_counter(); ...; took = time.perf_counter() - start
```

❌ Mistake 2: `time.sleep()` inside `async def`
```python
# Wrong - freezes ALL requests handled by the event loop
# async def handler(): time.sleep(2)

# Correct
# async def handler(): await asyncio.sleep(2)
```

❌ Mistake 3: Timeouts based on the wall clock, and sleeping as "waiting for a condition"
```python
# Wrong
# deadline = time.time() + 30
# while not ready(): time.sleep(5)       # up to 5s late, ignores clock changes

# Correct
# deadline = time.monotonic() + 30
# while time.monotonic() < deadline and not ready(): time.sleep(0.2)
# (even better: events, queues or asyncio instead of polling)
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import time
print(time.gmtime(0).tm_year, time.gmtime(0).tm_wday)
print(time.strftime("%j", time.gmtime(86400 * 59)))
print(type(time.time()), type(time.time_ns()))
print(time.sleep(0))
print(time.strftime("%H:%M", time.gmtime(3600 * 25)))
```

**Answer**:
```
1970 3
060
<class 'float'> <class 'int'>
None
01:00
```
The epoch is Thursday 1 January 1970, and `tm_wday` counts Monday as 0, so Thursday is 3. After 59 days it is 1 March 1970, which is day-of-year 060. `time_ns()` returns an integer, so there is no float rounding. `sleep` returns `None`. `strftime` shows only the clock part, so 25 hours wraps to `01:00`. (Verified by running.)

---

## ⚫ Interview Questions + Answers

Q1: `time.time()` vs `perf_counter()` vs `monotonic()`?
A1: `time()` is wall-clock time (for timestamps, may jump). `monotonic()` never goes back (timeouts, deadlines). `perf_counter()` has the best resolution for measuring short durations. Their zero points are undefined, so only compare differences.

Q2: Does `time.sleep` block other threads?
A2: It blocks only the calling thread; other threads run (it releases the GIL). In asyncio it blocks the entire event loop, so use `asyncio.sleep`.

Q3: How accurate is `time.sleep`?
A3: It sleeps at least the requested time, usually a bit more (scheduler delay). Do not use it for exact timing. A signal can interrupt it only in rare cases; since 3.5 it resumes unless the handler raises.

Q4: When do you use `process_time`?
A4: To measure CPU effort of your own code, without time spent waiting (sleep, I/O). Wall time much bigger than CPU time means the code is waiting.

Q5: `time` or `timeit` for benchmarking?
A5: `timeit` repeats the code many times and disables garbage collection to give a stable number. A single `perf_counter` measurement is fine for rough logging of long operations.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Measuring durations and request latency
- Short pauses and retry back-off in sync code
- Deadlines with `monotonic`

❌ Avoid when:
- Working with calendar dates, formatting for users or time zones (use `datetime` / `zoneinfo`)
- Waiting inside async code (use `asyncio`)
- Precise scheduling (use a scheduler like APScheduler, Celery beat, cron)

---

## 📊 Visual Diagram

```
 time.time()          ──► 1731200000.123   wall clock (epoch seconds) - may jump
 time.monotonic()     ──► 84321.5          steady, for timeouts
 time.perf_counter()  ──► 5123.000123      finest resolution, for benchmarks
 time.process_time()  ──► 0.42             CPU only (no sleep / I/O)

 start = perf_counter() ──── work ──── perf_counter() - start = duration
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Epoch | 1 Jan 1970 00:00 UTC | समय की शून्य तारीख |
| Timestamp | Seconds since the epoch | epoch से सेकंड |
| Monotonic | Never decreases | कभी घटने वाली नहीं |
| struct_time | Tuple-like broken-down time | टूटा हुआ समय (tuple जैसा) |
| Backoff | Waiting longer after each failure | हर failure पर ज़्यादा इंतज़ार |
| Blocking | Stops the thread until done | thread रोक देना |

---

## ⚡ 3-Line Summary
English: Use `perf_counter` to measure, `monotonic` for deadlines, `time()` for timestamps, and `sleep` only in synchronous code. Never use `time.sleep` in `async def`.
Hindi: मापने के लिए `perf_counter`, deadlines के लिए `monotonic`, timestamps के लिए `time()` और `sleep` सिर्फ synchronous code में इस्तेमाल करें। `async def` में कभी `time.sleep` न लगाएँ।

---

## ➡️ Next Topic
**194. re Module (Regular Expressions)** — search, validate and extract text by pattern.
