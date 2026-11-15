---

# 403. Profiling with line_profiler
# हिंदी में: line_profiler से Profiling (हर line का समय)

---

## 🔵 Simple Definition (English)
`line_profiler` is a third-party tool (`pip install line_profiler`) that measures the time spent on EACH LINE of a function. cProfile tells you which function is slow; line_profiler tells you which line inside it is slow.

## 🔵 सरल परिभाषा (Hindi)
`line_profiler` एक third-party tool है (`pip install line_profiler`) जो function की हर LINE का समय नापता है। cProfile बताता है कौन सा function धीमा है; line_profiler बताता है उसके अंदर कौन सी line धीमी है।

---

## 🔴 Problem it Solves
After cProfile points to a 60-line function, you still do not know whether the slowness is the loop, the regex, the sort, or a hidden copy. Adding `time.time()` around every line is messy. line_profiler gives a per-line table (hits, time, % time) with zero changes to the function body.

## 🔴 यह क्यों बना? (Hindi)
cProfile 60 line के function तक पहुँचा देता है, पर यह नहीं बताता कि धीमापन loop में है, regex में, sort में या किसी छुपी copy में। हर line में `time.time()` लगाना गंदा तरीका है। line_profiler बिना function बदले हर line की table देता है (hits, time, % time)।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pip install line_profiler
Step 2 → Pick the suspect function (from cProfile)
Step 3 → Mark it: @profile (with kernprof) or LineProfiler()(func) in code
Step 4 → Run; the tracer timestamps each line event of ONLY that function
Step 5 → Read the table: Hits, Time, Per Hit, % Time
Step 6 → Fix the line with the biggest % Time and re-run
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pip install line_profiler
Step 2 → संदिग्ध function चुनें (cProfile से मिला)
Step 3 → उसे mark करें: @profile (kernprof के साथ) या code में LineProfiler()(func)
Step 4 → चलाएँ; tracer सिर्फ उसी function की हर line का timestamp लेता है
Step 5 → Table पढ़ें: Hits, Time, Per Hit, % Time
Step 6 → सबसे ज़्यादा % Time वाली line सुधारें और फिर चलाएँ
```

Two ways to run:
- CLI: `kernprof -l -v script.py` (the `@profile` decorator is injected by kernprof, no import needed)
- In code: `from line_profiler import LineProfiler`, as in the examples below

---

## 🟡 Real World Example
A Razorpay reconciliation function takes 4 seconds for 100k transactions. cProfile says `reconcile()` is the culprit. line_profiler shows 80% of time on one line: `if txn_id in processed_ids` where `processed_ids` is a list. Changing it to a set makes it 100x faster. Only the line-level view revealed it.

## 🟡 Real Example Hindi mein
Razorpay का reconciliation function 1 लाख transactions पर 4 second लेता है। cProfile `reconcile()` को दोषी बताता है। line_profiler दिखाता है कि 80% समय एक line पर है: `if txn_id in processed_ids`, जहाँ `processed_ids` list है। इसे set बनाते ही 100 गुना तेज़। यह बात सिर्फ line-level view से पता चली।

---

## 💻 Code Example — Basic
```python
# Basic line_profiler usage (needs: pip install line_profiler)
from typing import List  # type hints
from line_profiler import LineProfiler  # the profiler class


def slow(n: int) -> List[int]:  # function we want to inspect
    out: List[int] = []  # empty result list
    for i in range(n):  # loop n times
        if i % 2 == 0:  # only even numbers
            out.append(i ** 2)  # store the square
    total: int = sum(out)  # an extra line to see in the table
    return out  # return the list


lp: LineProfiler = LineProfiler()  # create the profiler
wrapped = lp(slow)  # wrap the function so its lines are timed
wrapped(1000)  # run it once
lp.print_stats()  # print the per-line table
# Output (times vary; the Hits column is stable):
# Timer unit: 1e-09 s
#
# Total time: 0.000441 s
# File: a403.py
# Function: slow at line 4
#
# Line #      Hits         Time  Per Hit   % Time  Line Contents
# ==============================================================
#      4                                           def slow(n: int) -> List[int]:
#      5         1          0.0      0.0      0.0      out: List[int] = []
#      6      1001     170000.0    169.8     38.5      for i in range(n):
#      7      1000     173000.0    173.0     39.2          if i % 2 == 0:
#      8       500      94000.0    188.0     21.3              out.append(i ** 2)
#      9         1       3000.0   3000.0      0.7      total = sum(out)
#     10         1       1000.0   1000.0      0.2      return out

stats = lp.get_stats()  # raw data object
for (_fn, _lineno, name), timings in stats.timings.items():  # one entry per function
    print(name, [(ln, hits) for ln, hits, _t in timings])  # (line number, hits)
# Output: slow [(5, 1), (6, 1001), (7, 1000), (8, 500), (9, 1), (10, 1)]
# Hits prove it: loop line 1001 (1000 + final check), `if` 1000, append 500.
```

Command-line version (verified with kernprof 5.x), file `k.py`:
```python
# k.py - no import needed, kernprof injects @profile
@profile
def work(n):
    total = 0
    for i in range(n):
        total += i
    return total
work(100)
# Run: kernprof -l -v k.py
# Shows the same table; also writes k.py.lprof (view later: python -m line_profiler k.py.lprof)
```

## 💻 Code Example — Advanced
```python
# Production style: reusable decorator that profiles a function and prints a short report
import functools  # keep the original function name
import io  # capture the report as text
from typing import Any, Callable, List, TypeVar  # type hints
from line_profiler import LineProfiler  # the profiler

F = TypeVar("F", bound=Callable[..., Any])  # generic "any function" type


def line_profile(func: F) -> F:  # decorator factory
    @functools.wraps(func)  # preserve __name__ and docs
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # replaces the original
        lp: LineProfiler = LineProfiler()  # fresh profiler for each call
        lp.add_function(func)  # make sure func is tracked
        try:  # always print the report
            return lp(func)(*args, **kwargs)  # run the wrapped function
        finally:  # even if func raised
            buf = io.StringIO()  # text buffer
            lp.print_stats(stream=buf, output_unit=1e-3)  # report in milliseconds
            keep = [l for l in buf.getvalue().splitlines() if "Hits" in l or "Timer" in l]  # header only
            print("\n".join(keep))  # print the header lines
            for (_f, _n, name), t in lp.get_stats().timings.items():  # per function
                worst = max(t, key=lambda r: r[2])  # line with max total time
                print(f"{name}: hottest line = {worst[0]} ({worst[1]} hits)")  # report it
    return wrapper  # type: ignore[return-value]  # keep the original type for callers


def helper(x: int) -> int:  # a helper called from the profiled function
    return x * 2  # simple work


@line_profile  # profile report is printed after each call
def report(n: int) -> List[int]:  # the function under test
    rows: List[int] = []  # collect results
    for i in range(n):  # loop
        rows.append(helper(i))  # call helper
    s: List[int] = sorted(rows, reverse=True)  # sort descending
    return s  # result


print(report(5)[:3])  # run it
# Output (the line number in "hottest line" depends on your file and layout):
# Timer unit: 0.001 s
# Line #      Hits         Time  Per Hit   % Time  Line Contents
# report: hottest line = 32 (5 hits)
# [8, 6, 4]
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: line_profiler gives hits + time per source line
# kernprof -l -v script.py
# Line #  Hits  Time  Per Hit  % Time  Line Contents
```

```javascript
// JavaScript (Node/Chrome DevTools): the Performance / Profiler tab shows
// time per function and, in the "Sources" panel, a per-line time annotation
// when you record with --inspect. In plain code you can only do:
console.time("loop");
for (let i = 0; i < 1e6; i++) {}
console.timeEnd("loop");   // single timer, not per line
```

Key differences: in JS you normally use a GUI (DevTools) that annotates source lines. In Python, line_profiler is explicit opt-in per function, because tracing every line of everything would be far too slow.

---

## 🟠 FastAPI Connection
Use line_profiler on the pure business-logic function a route calls (not on the route itself) so the numbers are clean and repeatable in a test.

```python
# FastAPI: profile the helper behind an endpoint (needs: pip install fastapi httpx line_profiler)
from typing import Dict, List  # type hints
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # in-process test client
from line_profiler import LineProfiler  # profiler

app: FastAPI = FastAPI()  # create app


def build_report(n: int) -> List[int]:  # pure logic, easy to profile
    return [i * i for i in range(n) if i % 3 == 0]  # CPU work


@app.get("/report")  # GET /report?n=100
def report(n: int = 100) -> Dict[str, int]:
    return {"count": len(build_report(n))}  # endpoint stays thin


lp: LineProfiler = LineProfiler()  # profiler
lp.add_function(build_report)  # watch only build_report
profiled_build = lp(build_report)  # wrapped version
profiled_build(10_000)  # run it directly (outside the server)
print(TestClient(app).get("/report?n=10").json())  # Output: {'count': 4}
lp.print_stats()  # per-line table for build_report
```
Tip: for a deployed server, `py-spy` or `pyinstrument` is safer than line_profiler.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Profiling the caller but expecting to see the callee's lines
```python
# Wrong - only `outer` lines are shown, `helper` is one opaque line
lp = LineProfiler(); lp(outer)(10)
# Verified: functions in the report -> ['outer']

# Right - register helper too
lp = LineProfiler(); lp.add_function(helper); lp(outer)(10)
# Verified: functions in the report -> ['helper', 'outer']
```

❌ Mistake 2: Leaving `@profile` in committed code
```python
# Wrong - NameError when run normally (profile is only injected by kernprof)
# @profile
# def work(): ...

# Right - use LineProfiler in code, or remove @profile before commit
```

❌ Mistake 3: Trusting absolute times
```python
# Wrong - line_profiler adds per-line overhead, so a 1 s function may show 3 s
# Right - read the % Time column and compare lines with each other
```

❌ Mistake 4: Profiling everything
```python
# Wrong - decorate 50 functions, drown in output
# Right - cProfile first, then line_profile only the top 1-2 functions
```

---

## 🧠 Tricky Interview Question

**Q**: Why is the Hits count of the `for` line 1001 and not 1000?

```python
for i in range(1000):   # Hits ?
    pass                # Hits ?
```

**Answer**: The `for` line is executed 1000 times to hand out values plus one extra time to discover the iterator is exhausted, so Hits = 1001. The body runs 1000 times. (We saw exactly this: `1001` for the loop line, `1000` for the `if`.) Same logic explains `while cond:` getting one more hit than its body.

---

## ⚫ Interview Questions + Answers

Q1: Difference between cProfile and line_profiler?
A1: cProfile is built in and works per function (calls and time). line_profiler is a package that works per line, but only for the functions you register.

Q2: What does `kernprof -l -v` do?
A2: `-l` turns on line profiling and injects `@profile` into builtins, `-v` prints the result after the script ends. Without `-v` the result is saved in `script.py.lprof` to view later with `python -m line_profiler`.

Q3: Why must you register functions explicitly?
A3: Tracing every line of every function would make the program unusably slow. Profiling only the suspect function keeps overhead small and the report readable.

Q4: Which column should you read first?
A4: `% Time`. The `Time` units can differ (the header shows `Timer unit`), but percentages are easy to compare.

Q5: A line shows 0.0 time but is clearly expensive (a C call). Why?
A5: Time of a call is attributed to the calling line, so a heavy `sum(out)` shows up on that line. Very small values are also below timer resolution.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- cProfile already identified one hot function
- The function is long and you need the exact slow line
- You are comparing two versions of a line

❌ Avoid when:
- You do not yet know which function is slow (start with cProfile)
- You must profile a live production service (use py-spy)
- You need memory data (use memory_profiler / tracemalloc)

---

## 📊 Visual Diagram

```
 cProfile                       line_profiler
 --------                       -------------
 slow_function()  3.2 s   -->   line 12  for row in rows:      10%
                                line 13    x = regex(row)      75%  <-- fix this
                                line 14    out.append(x)       15%
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Line profiler | Per-line timing tool | हर line का समय नापने वाला tool |
| Hits | How many times a line ran | line कितनी बार चली |
| % Time | Share of the function's time | function के समय का हिस्सा |
| kernprof | CLI that runs line_profiler | line_profiler चलाने वाला command |
| Timer unit | Unit of the Time column | Time column की इकाई |
| Overhead | Extra time added by profiling | profiling से जुड़ा अतिरिक्त समय |

---

## ⚡ 3-Line Summary
English: line_profiler shows hits and time for every line of the functions you register. Use cProfile to find the slow function, then line_profiler to find the slow line. Read `% Time`, not absolute time.
Hindi: line_profiler आपके चुने functions की हर line के hits और समय दिखाता है। धीमा function cProfile से और धीमी line line_profiler से खोजें। Absolute time नहीं, `% Time` पढ़ें।

---

## ➡️ Next Topic
**404. Memory Profiling** — speed is only half the story; find which line eats RAM with `tracemalloc` and `memory_profiler`.
