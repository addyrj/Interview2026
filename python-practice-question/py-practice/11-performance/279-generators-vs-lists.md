---

# Q279. Generators vs Lists
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
You need the sum of squares of 1,000,000 numbers. Compare a list comprehension with a generator expression in terms of memory and early exit. Which is better and why?

---

## 💡 Quick Concept (2 lines only)
A list builds every item in memory at once; a generator produces one item at a time on demand, so its memory stays constant.
हिंदी: List सब कुछ memory में रखती है, generator एक-एक करके value देता है — memory बचती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys  # Step 1: for getsizeof
import timeit  # Step 2: for timing

N = 1_000_000  # Step 3: number of items

squares_list = [i * i for i in range(N)]  # Step 4: list comp -> all items built now
squares_gen = (i * i for i in range(N))  # Step 5: generator expr -> nothing computed yet

# ============================================
# TEST CASES
# ============================================
print(sys.getsizeof(squares_list) > 8_000_000)  # Expected: True (list pointer array ~8.4 MB)
print(sys.getsizeof(squares_gen))  # Expected: 200 (constant, independent of N; may differ by build)
print(sum(squares_gen))  # Expected: 333332833333500000

nums = list(range(N))  # data for the early-exit demo
t_gen = timeit.timeit(lambda: any(x == 3 for x in nums), number=100)  # generator stops at 4th item
t_list = timeit.timeit(lambda: any([x == 3 for x in nums]), number=100)  # list builds all 1M first
print(t_gen < t_list)  # Expected: True (timings vary, ordering is stable)
```

---

## 🔍 Why This Works (3 lines max)
`sys.getsizeof` of a generator only measures the generator object (frame + state), not data, so it stays tiny. With `any()` the generator stops at the first match, while the list comprehension must finish first.
हिंदी: Generator lazy है — जितना चाहिए उतना ही compute करता है, और जल्दी रुक सकता है।

---

## ⚡ Alternative Solution
```python
import itertools  # islice for taking a slice from a lazy stream


def fib():  # infinite generator function
    a, b = 0, 1  # starting values
    while True:  # never ends -> impossible as a list
        yield a  # hand out one value at a time
        a, b = b, a + b  # advance state


print(list(itertools.islice(fib(), 10)))  # Expected: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

gen = (i for i in range(3))  # generator is single-use
print(list(gen), list(gen))  # Expected: [0, 1, 2] []
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: wrapping a generator in a list "just in case" - defeats the purpose
total = sum([i * i for i in range(1_000_000)])  # builds a full 8 MB list first

# ✅ Correct: pass the generator directly (no extra brackets)
total = sum(i * i for i in range(1_000_000))  # constant memory

# ❌ Also wrong: iterating a generator twice and expecting data the 2nd time (it is exhausted)
```

---

## 🎯 Interview Tip (1 line)
Say: "Use generators for large or streaming data, one pass; use a list when I need len, indexing or multiple passes."

---

## 🔗 Related Questions
→ Q025 (generator exhaustion) | Q026 (genexpr laziness) | Q165 (generators) | Q297 (generators vs iterators)
