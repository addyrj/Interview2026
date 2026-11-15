---

# 402. Profiling with cProfile
# हिंदी में: cProfile से Profiling (कोड कहाँ धीमा है पता करना)

---

## 🔵 Simple Definition (English)
`cProfile` is Python's built-in profiler. It runs your code and records how many times each function was called and how much time it used. It tells you WHICH function is slow, so you do not have to guess.

## 🔵 सरल परिभाषा (Hindi)
`cProfile` Python का built-in profiler है। यह आपका code चलाकर हर function के call की गिनती और उसमें लगा समय record करता है। इससे पता चलता है कि कौन सा function धीमा है, अंदाज़ा नहीं लगाना पड़ता।

---

## 🔴 Problem it Solves
Developers "optimize" the wrong code because they guess. Usually 90% of the time is spent in 10% of the code. Without measurement you can spend a week speeding up a function that takes 1% of the total time. cProfile gives hard numbers per function, written in C so the overhead is small.

## 🔴 यह क्यों बना? (Hindi)
Developer अंदाज़े से गलत code optimize कर देते हैं। आमतौर पर 90% समय 10% code में जाता है। Measure किए बिना आप ऐसे function पर हफ्ता लगा सकते हैं जो कुल समय का सिर्फ 1% लेता है। cProfile हर function के असली numbers देता है और C में लिखा होने से overhead कम है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Start the profiler (cProfile.run, Profile().enable(), or python -m cProfile)
Step 2 → On every function call/return, a C hook records a timestamp
Step 3 → It builds a table: ncalls, tottime, cumtime per function
Step 4 → pstats sorts the table (cumulative, tottime, calls)
Step 5 → Read the top rows: that is where time goes
Step 6 → Fix the top function, profile AGAIN, compare
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Profiler शुरू करें (cProfile.run, Profile().enable() या python -m cProfile)
Step 2 → हर function call/return पर C hook timestamp लिखता है
Step 3 → हर function के लिए ncalls, tottime, cumtime की table बनती है
Step 4 → pstats table को sort करता है (cumulative, tottime, calls)
Step 5 → ऊपर की rows देखें: समय वहीं जा रहा है
Step 6 → ऊपर वाला function सुधारें, फिर से profile करें, तुलना करें
```

Column meaning:
- `ncalls`: number of calls (`1973/1` means 1973 total, 1 primitive = recursion)
- `tottime`: time inside the function ITSELF, excluding sub-calls
- `cumtime`: time including everything it called
- `percall`: the time divided by the calls

---

## 🟡 Real World Example
Swiggy's `/restaurants` endpoint takes 1.8 seconds. The team profiles it with cProfile and sees `json.loads` called 5000 times and `parse_menu` using 70% of the cumulative time. They cache the parsed menu and the endpoint drops to 200 ms. Without the profile they would have blamed the database.

## 🟡 Real Example Hindi mein
Swiggy का `/restaurants` endpoint 1.8 second लेता है। Team cProfile चलाती है तो दिखता है कि `json.loads` 5000 बार call हुआ और `parse_menu` ने cumulative समय का 70% लिया। वे parsed menu cache कर देते हैं और endpoint 200 ms पर आ जाता है। Profile न होता तो वे database को दोष देते।

---

## 💻 Code Example — Basic
```python
# Basic cProfile usage - every line commented
import cProfile  # built-in profiler module
from typing import List  # type hints


def slow_sum(n: int) -> int:  # CPU heavy function
    total: int = 0  # running total
    for i in range(n):  # loop n times
        total += i * i  # square and add
    return total  # give the result back


def build(n: int) -> List[int]:  # builds a list
    return [i for i in range(n)]  # simple comprehension


def work() -> int:  # the code we want to measure
    build(50_000)  # small job
    return slow_sum(200_000) + slow_sum(100_000)  # called twice


cProfile.run("work()", sort="tottime")  # run work() and print sorted by own time
# Output (times vary per machine; ncalls are stable):
#          7 function calls in 0.013 seconds
#
#    Ordered by: internal time
#
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#         2    0.012    0.006    0.012    0.006 t402.py:4(slow_sum)
#         1    0.001    0.001    0.001    0.001 t402.py:10(build)
#         1    0.000    0.000    0.013    0.013 t402.py:13(work)
#         1    0.000    0.000    0.013    0.013 {built-in method builtins.exec}
#         1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
#         1    0.000    0.000    0.013    0.013 <string>:1(<module>)
# Note: on Python 3.12+ list comprehensions are inlined (PEP 709), so no <listcomp> row.
# From the command line you can also do:  python -m cProfile -s cumulative app.py
```

## 💻 Code Example — Advanced
```python
# Production style: context manager + save to file + read back with pstats
import cProfile  # the profiler
import io  # in-memory text buffer
import os  # remove temp file
import pstats  # read and sort profile data
import tempfile  # safe temp directory
from contextlib import contextmanager  # build a with-block helper
from typing import Iterator, List  # type hints


def parse_row(row: str) -> List[int]:  # parse "1,2,3" into ints
    return [int(x) for x in row.split(",")]  # convert each piece


def load_rows(n: int) -> List[List[int]]:  # parse n rows
    data: List[str] = ["1,2,3,4,5"] * n  # fake CSV lines
    return [parse_row(r) for r in data]  # one parse per row


def total(rows: List[List[int]]) -> int:  # add up everything
    return sum(sum(r) for r in rows)  # nested sum


def pipeline() -> int:  # the real job
    return total(load_rows(20_000))  # load then total


@contextmanager  # lets us write: with profiled(): ...
def profiled(top: int = 5, sort: str = "cumulative") -> Iterator[cProfile.Profile]:
    pr = cProfile.Profile()  # create profiler object
    pr.enable()  # start measuring
    try:  # make sure we always stop
        yield pr  # run the user's code here
    finally:  # even if the code raised an error
        pr.disable()  # stop measuring
        buf = io.StringIO()  # capture the report as text
        stats = pstats.Stats(pr, stream=buf).strip_dirs().sort_stats(sort)  # shorten paths, sort
        stats.print_stats(top)  # keep only the top rows
        print(buf.getvalue())  # show the report


with profiled(top=4) as pr:  # profile this block
    result: int = pipeline()  # run the pipeline
print("result:", result)  # normal output still works
# Output (times vary):
#          80009 function calls (60009 primitive calls) in 0.023 seconds
#
#    Ordered by: cumulative time
#    List reduced from 11 to 4 due to restriction <4>
#
#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#         1    0.000    0.000    0.023    0.023 a402.py:24(pipeline)
#         1    0.002    0.002    0.017    0.017 a402.py:15(load_rows)
#     20000    0.013    0.000    0.015    0.000 a402.py:11(parse_row)
#         1    0.000    0.000    0.006    0.006 a402.py:20(total)
#
# result: 300000

path: str = os.path.join(tempfile.gettempdir(), "pipeline_demo.prof")  # file for raw stats
pr.dump_stats(path)  # save binary profile (open later in snakeviz / pstats)
loaded = pstats.Stats(path)  # load it back
print("loaded from file:", loaded.total_calls > 0, type(loaded).__name__)  # sanity check
# Output: loaded from file: True Stats
loaded.strip_dirs().sort_stats("tottime").print_callers("parse_row")  # who calls parse_row?
# Output:
# Function               was called by...
#                            ncalls  tottime  cumtime
# a402.py:11(parse_row)  <-   20000    0.013    0.015  a402.py:15(load_rows)
os.remove(path)  # clean up the temp file
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: built-in, no install needed
import cProfile
cProfile.run("work()", sort="cumulative")   # text table
# CLI: python -m cProfile -o out.prof app.py ; then: snakeviz out.prof
```

```javascript
// JavaScript (Node.js): built-in V8 profiler
// node --prof app.js          -> writes isolate-*.log
// node --prof-process isolate-*.log   -> text report
// or: node --inspect  + Chrome DevTools "Performance" tab
// or: console.time("work"); work(); console.timeEnd("work");  (quick timing only)
```

Key differences: Python's `cProfile` is a deterministic profiler (it hooks every call), so it adds overhead (often 1.5-3x slower) and distorts very tiny functions. Node's `--prof` is a sampling profiler (low overhead). For Python sampling, use `py-spy`.

---

## 🟠 FastAPI Connection
Profile one slow endpoint at a time. A middleware can switch the profiler on with `?profile=1` (only in dev/staging, never public production).

```python
# FastAPI: profile middleware (needs: pip install fastapi httpx)
import cProfile  # profiler
import io  # text buffer
import pstats  # report builder
from typing import Awaitable, Callable, Dict  # type hints
from fastapi import FastAPI, Request, Response  # FastAPI types
from fastapi.testclient import TestClient  # test without a server

app: FastAPI = FastAPI()  # create app


@app.middleware("http")  # runs for every request
async def profile_mw(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    if request.query_params.get("profile") != "1":  # profile only when asked
        return await call_next(request)  # normal fast path
    pr = cProfile.Profile()  # new profiler per request
    pr.enable()  # start
    response: Response = await call_next(request)  # run the endpoint
    pr.disable()  # stop
    buf = io.StringIO()  # capture report
    pstats.Stats(pr, stream=buf).sort_stats("cumulative").print_stats(3)  # top 3
    print("PROFILE for", request.url.path)  # log it (use a real logger in prod)
    return response  # return the normal response


@app.get("/sum")  # sync endpoint
def sum_endpoint(n: int = 1000) -> Dict[str, int]:
    return {"total": sum(i * i for i in range(n))}  # CPU work


client = TestClient(app)  # in-process client
print(client.get("/sum?n=10&profile=1").json())  # Output: {'total': 285}
```
Verified: runs and prints `PROFILE for /sum`. Caveat: a plain `def` endpoint runs in a thread pool, and `cProfile` only tracks the thread that enabled it, so the report mostly shows the async plumbing. To profile the function body itself, call it directly in a test, or use `py-spy` / `pyinstrument` against the running server.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Sorting by the wrong column
```python
# Wrong - cumulative always shows main() on top, it hides the real culprit
# cProfile.run("main()", sort="cumulative")

# Right - tottime shows who burns CPU by itself; use both views
# cProfile.run("main()", sort="tottime")
```

❌ Mistake 2: Profiling tiny code once, or comparing runs with different profiler overhead
```python
# Wrong - one run of a 1 ms function is noise
# Right - use timeit for micro-benchmarks, cProfile for finding the hot function
```

❌ Mistake 3: Leaving the profiler on in production
```python
# Wrong - cProfile slows every call (1.5-3x)
# Right - enable only on demand (a flag, a staging server), or use sampling tools (py-spy)
```

❌ Mistake 4: Optimizing before measuring
```python
# Wrong - "I think the loop is slow", rewrite it
# Right - profile, fix the top row, profile again, confirm improvement
```

---

## 🧠 Tricky Interview Question

**Q**: What does `1973/1` in the `ncalls` column mean?

```python
import cProfile, pstats

def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

with cProfile.Profile() as pr:
    fib(15)
pstats.Stats(pr).sort_stats(pstats.SortKey.CALLS).print_stats(2)
```

**Answer**: The first row prints `1973/1`. 1973 is the TOTAL number of calls to `fib` (including recursive ones). The `/1` is the count of PRIMITIVE calls: calls that were not made from inside another `fib` call. Only one outside call started the recursion. For a non-recursive function the two numbers are equal, so only one is shown. Also note `tottime` is the function's own time, while `cumtime` for a recursive function counts only the outermost call to avoid double counting.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `tottime` and `cumtime`?
A1: `tottime` is time spent inside the function only, not in functions it calls. `cumtime` includes sub-calls. A function with high `cumtime` but low `tottime` is just a coordinator; look at what it calls.

Q2: cProfile vs profile module?
A2: `profile` is pure Python and slow; `cProfile` is a C extension with the same API and far lower overhead. Always use `cProfile`.

Q3: Is cProfile a sampling profiler?
A3: No. It is deterministic: it hooks every call and return. Sampling profilers (py-spy, pyinstrument) look at the stack every few milliseconds and have lower overhead.

Q4: How do you visualize the results?
A4: Save with `python -m cProfile -o out.prof app.py`, then open with `snakeviz out.prof` (flame/icicle chart) or convert with `gprof2dot`. `pstats` gives a text view.

Q5: Does cProfile show line-level information?
A5: No, only per function. For lines use `line_profiler` (next topic).

Q6: Can cProfile profile async code well?
A6: Partly. Time while a coroutine waits on `await` is attributed to the event loop, and coroutines look like many short calls. Prefer `pyinstrument` (supports async) or logging timestamps for I/O waits.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You do not know which function is slow
- You want call counts (a function called 1 million times is suspicious)
- You want a quick no-install first look

❌ Avoid when:
- You need line-level detail (use line_profiler)
- You need to profile a live production server (use py-spy)
- You are timing one tiny expression (use timeit)

---

## 📊 Visual Diagram

```
 your code
    |
    v   call / return events
 +-----------+      +------------------------+
 | cProfile  | ---> | table per function     |
 | (C hook)  |      | ncalls tottime cumtime |
 +-----------+      +------------------------+
                               |
              pstats.sort_stats("cumulative" | "tottime" | "calls")
                               |
                               v
                       fix top row, repeat
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Profiler | Tool that measures where time goes | समय कहाँ जा रहा है मापने वाला tool |
| Deterministic | Records every call | हर call record करना |
| tottime | Time in the function itself | function के अपने अंदर का समय |
| cumtime | Time including sub-calls | sub-calls समेत कुल समय |
| ncalls | Number of calls | call की संख्या |
| Hot spot | Code that uses most time | जहाँ सबसे ज़्यादा समय लगता है |

---

## ⚡ 3-Line Summary
English: cProfile is the built-in deterministic profiler. It shows calls and time per function; sort by `tottime` to find CPU hogs and `cumulative` to see the call tree. Always measure, fix the top row, then measure again.
Hindi: cProfile built-in deterministic profiler है। यह हर function के calls और समय दिखाता है; CPU खाने वाले के लिए `tottime` और call tree के लिए `cumulative` से sort करें। हमेशा पहले measure करें, ऊपर वाला सुधारें, फिर दोबारा measure करें।

---

## ➡️ Next Topic
**403. Profiling with line_profiler** — once cProfile names the slow function, see which exact LINE inside it is slow.
