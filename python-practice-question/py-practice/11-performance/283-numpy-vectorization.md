---

# Q283. NumPy Vectorization
# Category: PERFORMANCE
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Compute the sum of squares of 1,000,000 numbers. Compare a pure-Python loop with a NumPy vectorized version. Why is NumPy faster?

---

## 💡 Quick Concept (2 lines only)
NumPy runs the loop in compiled C over a contiguous typed array, skipping per-item Python object and bytecode overhead. Operate on whole arrays, not element by element.
हिंदी: NumPy loop को C में चलाता है, इसलिए Python for-loop से बहुत तेज़ है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import timeit                                   # Step 1: timing helper
import numpy as np                              # Step 2: pip install numpy

N = 1_000_000                                   # Step 3: number of items
py_list = list(range(N))                        # plain Python list of ints
arr = np.arange(N, dtype=np.int64)              # NumPy array (int64 avoids overflow here)

def py_sum_squares() -> int:                    # Step 4: pure Python loop
    total = 0                                   # accumulator
    for x in py_list:                           # one bytecode loop iteration per item
        total += x * x                          # Python int multiply + add
    return total                                # result

def np_sum_squares() -> int:                    # Step 5: vectorized
    return int(np.sum(arr * arr))               # whole-array multiply, then C-level sum

# ============================================
# TEST CASES
# ============================================
print(py_sum_squares() == np_sum_squares())     # Expected: True
print(np_sum_squares())                         # Expected: 333332833333500000
t_py = timeit.timeit(py_sum_squares, number=5)  # time Python loop
t_np = timeit.timeit(np_sum_squares, number=5)  # time NumPy
print(t_np < t_py)                              # Expected: True
print(t_py / t_np > 10)                         # Expected: True  (measured well above 10x; varies by machine)
```

---

## 🔍 Why This Works (3 lines max)
`arr * arr` and `np.sum` run tight C loops on raw 8-byte integers (often with SIMD), while the Python loop boxes every int and executes bytecode per item. Gain is largest for big arrays; for tiny arrays NumPy call overhead can make it slower.
हिंदी: NumPy raw numbers पर C में काम करता है, Python हर number को object बनाकर चलाता है।

---

## ⚡ Alternative Solution
```python
# Pure-Python but better: let built-ins do the looping, and use np.dot for squares
import numpy as np                              # numpy import

arr = np.arange(1_000_000, dtype=np.int64)      # input array
print(int(np.dot(arr, arr)))                    # Expected: 333332833333500000  (dot = sum of x*x, no temp array)
print(sum(x * x for x in range(1_000_000)))     # Expected: 333332833333500000  (generator: no list, still Python speed)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: Python loop over a NumPy array (slower than a plain list loop!)
import numpy as np                              # numpy import

a = np.arange(5)                                # small array
total = 0                                       # accumulator
for x in a:                                     # each x is a np.int64 scalar (slow to create)
    total += x * x                              # scalar arithmetic is slower than int arithmetic

# ✅ Correct: stay vectorized
print(total == int((a * a).sum()))              # Expected: True
print((a * a).sum())                            # Expected: 30
```

---

## 🎯 Interview Tip (1 line)
Say: "Vectorize: push loops into NumPy/C, avoid Python-level loops over arrays, and beware overflow with small dtypes like int32."

---

## 🔗 Related Questions
→ Q276 (timeit) | Q277 (cProfile) | Q290 (avoiding slow patterns) | Q279 (generators vs lists)
