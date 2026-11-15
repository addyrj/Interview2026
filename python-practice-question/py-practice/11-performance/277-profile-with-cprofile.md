---

# Q277. Profile with cProfile
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
`main()` calls `slow_part()` 3 times and `fast_part()` 50 times. Use `cProfile` + `pstats` to find which function is the real bottleneck, and read call counts and cumulative time programmatically.

---

## 💡 Quick Concept (2 lines only)
`cProfile` records every function call: `ncalls`, `tottime` (own time) and `cumtime` (including callees). Optimise the function with the biggest `cumtime`, not the one called most.
हिंदी: `cProfile` हर function का call count और समय बताता है; ज़्यादा `cumtime` वाले function को optimise करें।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import cProfile  # Step 1: deterministic profiler
import io  # capture the text report
import pstats  # Step 2: analyse results


def slow_part() -> int:
    return sum(i * i for i in range(200_000))  # heavy work


def fast_part() -> int:
    return sum(range(100))  # light work


def main() -> None:
    for _ in range(3):  # slow function: few calls
        slow_part()  # ...but expensive
    for _ in range(50):  # fast function: many calls
        fast_part()  # ...but cheap


prof = cProfile.Profile()  # Step 3: create profiler
prof.enable()  # start recording
main()  # run the code under test
prof.disable()  # stop recording

stats = pstats.Stats(prof)  # wrap the data
by_name = {k[2]: v for k, v in stats.stats.items()}  # func name -> (cc, nc, tt, ct, callers)

# ============================================
# TEST CASES
# ============================================
print(by_name["slow_part"][1], by_name["fast_part"][1])  # Expected: 3 50   (ncalls)
print(by_name["slow_part"][3] > 100 * by_name["fast_part"][3])  # Expected: True (cumtime dominated by slow_part)
buf = io.StringIO()  # buffer for the printed table
pstats.Stats(prof, stream=buf).sort_stats("cumulative").print_stats(3)  # top 3 by cumtime
print("cumulative" in buf.getvalue())  # Expected: True
# Typical table (times and paths vary): main ~0.09s, slow_part ~0.09s (3 calls), fast_part ~0.00003s (50 calls)
```

---

## 🔍 Why This Works (3 lines max)
The profiler hooks every call/return, so counts are exact and times are per function. `slow_part` has fewer calls but ~1000x more cumulative time, so it is the bottleneck. In 3.13 the generator expression also shows as its own entry (600003 calls total).
हिंदी: कम बार चलने के बावजूद `slow_part` का कुल समय सबसे ज़्यादा है, इसलिए bottleneck वही है।

---

## ⚡ Alternative Solution
```python
# Quick one-liner style: cProfile.run + sort, or a context manager (3.8+)
import cProfile  # profiler
import pstats  # stats viewer


def work() -> int:
    return sum(i * i for i in range(50_000))  # sample work


with cProfile.Profile() as pr:  # profiler as a context manager
    work()  # profile this call
st = pstats.Stats(pr).sort_stats(pstats.SortKey.CUMULATIVE)  # sort by cumulative time
print(st.total_calls > 50_000)  # Expected: True  (genexpr called once per item)
# From the shell: python -m cProfile -s cumtime script.py
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: guessing the bottleneck / optimising the function with most calls
# fast_part is called 50 times, so "it must be the problem" - but it costs ~0.00003s total.

# ✅ Correct: sort by cumtime (or tottime), fix the top entry, then re-profile.
# Also: profiling adds overhead - use it for relative comparison, not absolute timing (use timeit for that).
```

---

## 🎯 Interview Tip (1 line)
Say: "Measure first: cProfile for where time goes, timeit for how long; optimise the top cumtime entry, then re-measure."

---

## 🔗 Related Questions
→ Q276 (timeit) | Q289 (tracemalloc) | Q290 (slow patterns)
