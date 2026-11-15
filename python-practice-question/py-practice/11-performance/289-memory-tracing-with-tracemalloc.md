---

# Q289. Memory Tracing with tracemalloc
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
How do you find which line of code allocates the most memory, and compare the memory of two approaches, using `tracemalloc`?

---

## 💡 Quick Concept (2 lines only)
`tracemalloc` records every Python memory allocation with its traceback; take snapshots and compare or rank by line.
हिंदी: `tracemalloc` बताता है कि कौन सी line ने कितनी memory allocate की।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import tracemalloc  # stdlib memory tracer


def build_list() -> list[int]:
    return [i for i in range(200_000)]  # allocates a big list of ints


def build_gen_sum() -> int:
    return sum(i for i in range(200_000))  # constant memory


def peak_kb(fn) -> int:  # Step 1: measure peak memory of a function
    tracemalloc.start()  # Step 2: begin tracing
    fn()  # Step 3: run workload
    _current, peak = tracemalloc.get_traced_memory()  # Step 4: (current, peak) bytes
    tracemalloc.stop()  # Step 5: stop tracing
    return peak // 1024  # KB


# ============================================
# TEST CASES
# ============================================
print(peak_kb(build_list) > 1000)  # Expected: True (list of 200k ints uses MBs)
print(peak_kb(build_gen_sum) < 10)  # Expected: True (generator uses almost nothing)

tracemalloc.start()  # trace for the snapshot demo
data = build_list()  # keep result alive so it shows in the snapshot
snap = tracemalloc.take_snapshot()  # Step 6: snapshot of live allocations
top = snap.statistics("lineno")[0]  # Step 7: biggest allocating line
print(top.traceback[0].lineno, top.size // 1024 > 1000)  # Expected: 8 True (line of the list comp inside build_list in this snippet)
tracemalloc.stop()  # always stop tracing
```

---

## 🔍 Why This Works (3 lines max)
`tracemalloc` hooks Python's allocator, so it sees Python objects (not C-extension raw memory like some NumPy buffers). `get_traced_memory` gives current and peak; `take_snapshot().statistics("lineno")` ranks lines by size.
हिंदी: Peak memory और line-wise ranking दोनों मिलते हैं — leak ढूँढने में काम आता है।

---

## ⚡ Alternative Solution
```python
import tracemalloc  # stdlib

tracemalloc.start()  # begin
before = tracemalloc.take_snapshot()  # snapshot A
keep = [str(i) * 10 for i in range(50_000)]  # allocate stuff
after = tracemalloc.take_snapshot()  # snapshot B
diff = after.compare_to(before, "lineno")  # what grew between A and B
print(diff[0].size_diff > 100_000)  # Expected: True (leak-hunting technique)
tracemalloc.stop()  # stop
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using sys.getsizeof on a list and thinking it is the total
import sys
print(sys.getsizeof([str(i) for i in range(1000)]))  # only the pointer array, not the strings

# ✅ Correct: measure real allocation with tracemalloc (includes the element objects)
```

---

## 🎯 Interview Tip (1 line)
Say: "For leaks I take two tracemalloc snapshots and compare_to - it points at the exact file and line that grew."

---

## 🔗 Related Questions
→ Q279 (generators vs lists) | Q280 (__slots__) | Q307 (memory management and GC) | Q277 (cProfile)
