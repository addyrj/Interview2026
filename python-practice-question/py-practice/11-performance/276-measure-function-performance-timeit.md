---

# Q276. Measure Function Performance (timeit)
# Category: Performance
# Difficulty: ⭐ Easy

---

## ❓ Question
Which is faster for squaring numbers 0..999: a `for` loop with `append`, or a list comprehension? Measure it correctly with `timeit` (not with a single `time.time()` call) and report the relative result.

---

## 💡 Quick Concept (2 lines only)
`timeit` runs a snippet many times with the best available clock and disables GC, so noise is small. Use `repeat()` and take the MINIMUM — it is the least disturbed run.
हिंदी: `timeit` code को कई बार चलाकर सही समय नापता है; `repeat()` में सबसे छोटा (min) समय असली माना जाता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import timeit  # Step 1: stdlib benchmarking tool


def loop_version() -> list[int]:
    out: list[int] = []  # result list
    for i in range(1000):  # plain loop
        out.append(i * i)  # append each square
    return out  # return list


def comp_version() -> list[int]:
    return [i * i for i in range(1000)]  # list comprehension


def best_time(fn, number: int = 2000, repeat: int = 5) -> float:
    runs = timeit.repeat(fn, number=number, repeat=repeat)  # Step 2: several runs
    return min(runs) / number  # Step 3: min of runs, seconds per call


# ============================================
# TEST CASES
# ============================================
assert loop_version() == comp_version()  # same result first - then compare speed
t_loop = best_time(loop_version)  # time the loop
t_comp = best_time(comp_version)  # time the comprehension
print(f"loop: {t_loop * 1e6:.1f} us, comp: {t_comp * 1e6:.1f} us")
# Output varies by machine. Measured on my runs: loop: 35-45 us, comp: 32-38 us
print(f"ratio loop/comp = {t_loop / t_comp:.2f}")  # Varies: ~1.1x on 3.13 (comp usually a bit faster; can flip on a noisy machine)
```

---

## 🔍 Why This Works (3 lines max)
`repeat` runs the batch several times; background noise only ever makes a run slower, so `min` is the best estimate. Dividing by `number` gives per-call time. Always check results are equal before comparing speed.
हिंदी: Noise सिर्फ समय बढ़ाता है, इसलिए min सबसे सही है; और speed से पहले दोनों का result बराबर जाँचें।

---

## ⚡ Alternative Solution
```python
# String-based timeit + setup, and a tiny decorator for quick checks
import timeit  # benchmarking
from functools import wraps  # keep function metadata
from time import perf_counter  # high-resolution clock

t = timeit.timeit("sum(x * x for x in data)", setup="data = range(1000)", number=1000)  # snippet form
print(t > 0)  # Expected: True  (value itself varies)


def timed(fn):
    @wraps(fn)  # keep name and docstring
    def wrapper(*a, **k):
        start = perf_counter()  # start clock
        result = fn(*a, **k)  # run the function
        wrapper.last = perf_counter() - start  # store elapsed seconds
        return result  # pass result through
    return wrapper


@timed
def work() -> int:
    return sum(range(100_000))  # some work


print(work(), work.last > 0)  # Expected: 4999950000 True
# In IPython/Jupyter you can also write: %timeit comp_version()
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: one-shot timing with time.time() - noisy, low resolution, includes warm-up
import time  # coarse clock
s = time.time()  # start
sum(range(1000))  # tiny work
print(time.time() - s)  # Output varies wildly (may even print 0.0)

# ✅ Correct: timeit.repeat(..., number=N) and take min(); use perf_counter for manual timing
```

---

## 🎯 Interview Tip (1 line)
Say: "I benchmark with `timeit.repeat` and take the min, compare equal results, and profile (cProfile) before optimising anything."

---

## 🔗 Related Questions
→ Q277 (cProfile) | Q279 (generators vs lists) | Q282 (concat vs join) | Q290 (slow patterns)
