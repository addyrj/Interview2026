---

# 375. NumPy Operations
# हिंदी में: NumPy Operations (Vectorized Math, Aggregation, Sorting)

---

## 🔵 Simple Definition (English)
NumPy operations are fast, whole-array actions: arithmetic (`+ - * /`), comparisons, aggregations (`sum`, `mean`, `max` with an `axis`), sorting, searching (`where`, `argmax`), and linear algebra (`dot`, `@`). You write one line and NumPy loops in C for you.

## 🔵 सरल परिभाषा (Hindi)
NumPy operations पूरे array पर चलने वाली तेज़ क्रियाएं हैं: arithmetic (`+ - * /`), comparisons, aggregations (`sum`, `mean`, `max` और `axis`), sorting, searching (`where`, `argmax`), और linear algebra (`dot`, `@`)। आप एक line लिखते हैं और loop NumPy C में चला देता है।

---

## 🔴 Problem it Solves
With plain Python you write `for` loops for every calculation: sum a column, normalize values, find the best match. Loops are slow for millions of items and make code long. Vectorized operations give the same result in a single readable expression and run 10 to 100 times faster, which is why data science and ML code looks like math formulas.

## 🔴 यह क्यों बना? (Hindi)
सामान्य Python में हर calculation के लिए `for` loop लिखना पड़ता है: column का sum, values normalize करना, सबसे अच्छा match ढूंढना। लाखों items पर loops धीमे हैं और code लंबा हो जाता है। Vectorized operations वही नतीजा एक पढ़ने लायक expression में देते हैं और 10 से 100 गुना तेज चलते हैं, इसीलिए data science और ML code गणित के formulas जैसा दिखता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Operators (+, *, >) are universal functions ("ufuncs") applied element by element
Step 2 → Arrays must have the same shape OR be broadcastable (next topic)
Step 3 → Aggregations (sum, mean, max) collapse an axis: axis=0 down the rows, axis=1 across columns
Step 4 → keepdims=True keeps the collapsed axis as size 1, so results broadcast back easily
Step 5 → Comparisons return boolean arrays, which can be summed or used as masks
Step 6 → np.where(cond, a, b) is a vectorized if/else; argsort gives the sorting order
Step 7 → a @ b is matrix multiplication (BLAS), the core of ML
Step 8 → NaN handling: use nansum / nanmean, plain sum returns NaN
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Operators (+, *, >) universal functions ("ufuncs") हैं जो element-by-element चलते हैं
Step 2 → Arrays की shape एक जैसी हो या broadcastable हो (अगला topic)
Step 3 → Aggregations (sum, mean, max) एक axis को collapse करते हैं: axis=0 rows के ऊपर से नीचे, axis=1 columns के आर-पार
Step 4 → keepdims=True collapse हुए axis को size 1 रखता है, ताकि नतीजा आसानी से broadcast हो
Step 5 → Comparisons boolean arrays देते हैं, जिन्हें sum करके या mask की तरह इस्तेमाल किया जा सकता है
Step 6 → np.where(cond, a, b) vectorized if/else है; argsort sorting का क्रम देता है
Step 7 → a @ b matrix multiplication (BLAS) है, ML की बुनियाद
Step 8 → NaN: nansum / nanmean इस्तेमाल करें, सादा sum NaN लौटाता है
```

---

## 🟡 Real World Example
A Swiggy analytics job has a `(days, restaurants)` revenue matrix: `revenue.sum(axis=0)` gives per-restaurant totals, `revenue.mean(axis=1)` gives daily averages, and `np.where(revenue > 10000, "hit", "miss")` labels every cell. A RAG service scores 100,000 document vectors against a query with a single `docs @ query`.

## 🟡 Real Example Hindi mein
Swiggy के analytics job में `(days, restaurants)` revenue matrix है: `revenue.sum(axis=0)` हर restaurant का कुल देता है, `revenue.mean(axis=1)` रोज का औसत देता है, और `np.where(revenue > 10000, "hit", "miss")` हर cell को label करता है। एक RAG service 1,00,000 document vectors को query से एक ही `docs @ query` में score करती है।

---

## 💻 Code Example — Basic
```python
# Basic NumPy operations: element-wise math, aggregation with axis, where, sort, dot
import numpy as np                                           # numpy

a: np.ndarray = np.array([1, 2, 3, 4])                       # vector
b: np.ndarray = np.array([10, 20, 30, 40])                   # vector
print(a + b, a * b, a ** 2)                                  # element-wise (not list concat!)
print(a > 2, (a > 2).sum())                                  # comparison gives bool array
m: np.ndarray = np.array([[1, 2, 3], [4, 5, 6]])             # 2x3 matrix
print(m.sum(), m.sum(axis=0), m.sum(axis=1))                 # all, per column, per row
print(m.mean(axis=0), m.max(), m.argmax())                   # mean per column, max, flat index of max
print(np.where(a % 2 == 0, "even", "odd"))                   # vectorized if/else
print(np.sort([3, 1, 2]), np.argsort([30, 10, 20]))          # sorted values, and their order
print(np.cumsum(a))                                          # running total
print(np.dot(a, b), a @ b)                                   # dot product, same thing
print(np.unique([3, 1, 3, 2, 1], return_counts=True))        # unique values + counts
print(np.sqrt(np.array([4.0, 9.0])), np.round(np.pi, 3))     # ufuncs

# Output:
# [11 22 33 44] [ 10  40  90 160] [ 1  4  9 16]
# [False False  True  True] 2
# 21 [5 7 9] [ 6 15]
# [2.5 3.5 4.5] 6 5
# ['odd' 'even' 'odd' 'even']
# [1 2 3] [1 2 0]
# [ 1  3  6 10]
# 300 300
# (array([1, 2, 3]), array([2, 1, 2]))
# [2. 3.] 3.142
```
Verified: run with NumPy 2.5.4. (In NumPy 2 printing of `np.pi` rounded scalar may show `np.float64(3.142)` in `repr`, but `print` shows `3.142`.)

## 💻 Code Example — Advanced
```python
# Production style: vectorized scoring, z-score, cosine similarity search, NaN handling, loop-vs-vector check
from __future__ import annotations                           # forward refs
import time                                                  # timing
import numpy as np                                           # numpy
from numpy.typing import NDArray                             # typed arrays

F = NDArray[np.float64]                                      # alias for readability


def zscore(x: F, axis: int = 0) -> F:
    """Standardize columns: mean 0, std 1; constant columns become 0 (no division by zero)."""
    mu = x.mean(axis=axis, keepdims=True)                    # keepdims -> broadcastable shape
    sd = x.std(axis=axis, keepdims=True)                     # standard deviation
    sd = np.where(sd == 0, 1.0, sd)                          # guard against /0
    return (x - mu) / sd                                     # vectorized, no loops


def top_k_cosine(query: F, docs: F, k: int = 2) -> list[tuple[int, float]]:
    """Return (index, score) of k most similar document vectors (RAG-style retrieval)."""
    qn = query / np.linalg.norm(query)                       # unit query
    dn = docs / np.linalg.norm(docs, axis=1, keepdims=True)  # unit docs
    scores = dn @ qn                                         # one matrix-vector product
    idx = np.argsort(scores)[::-1][:k]                       # best first
    return [(int(i), round(float(scores[i]), 3)) for i in idx]


x = np.array([[1.0, 10.0, 5.0], [2.0, 20.0, 5.0], [3.0, 30.0, 5.0]])   # last column is constant
print(zscore(x).round(2))                                    # standardized

docs = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])        # three tiny "embeddings"
print(top_k_cosine(np.array([1.0, 0.1]), docs))              # closest to the first doc

v = np.array([1.0, np.nan, 3.0])                             # missing value
print(v.sum(), np.nansum(v), np.nanmean(v))                  # NaN poisons sum; nan* functions skip it

big = np.random.default_rng(0).random(1_000_000)             # 1M floats
t0 = time.perf_counter(); s_loop = 0.0
for val in big: s_loop += val                                # Python loop
t_loop = time.perf_counter() - t0
t0 = time.perf_counter(); s_vec = big.sum()                  # vectorized
t_vec = time.perf_counter() - t0
print(np.isclose(s_loop, s_vec), t_vec < t_loop)             # same answer, vectorized faster

# Output:
# [[-1.22 -1.22  0.  ]
#  [ 0.    0.    0.  ]
#  [ 1.22  1.22  0.  ]]
# [(0, 0.995), (2, 0.774)]
# nan 4.0 2.0
# True True
```
Verified: run with NumPy 2.5.4 (timings vary by machine, so only the comparison is printed).

---

## 🟠 JavaScript vs Python Comparison

| Task | Python (NumPy) | JavaScript |
|------|----------------|-----------|
| Add arrays | `a + b` | `a.map((x, i) => x + b[i])` |
| Sum | `a.sum()` | `a.reduce((s, x) => s + x, 0)` |
| Filter by condition | `a[a > 2]` | `a.filter(x => x > 2)` |
| Column sum | `m.sum(axis=0)` | nested loops / reduce |
| Matrix multiply | `A @ B` | library needed (mathjs) |

```python
# Python way
import numpy as np                                       # numpy
a = np.array([3, 1, 2])                                  # array
print((a * 10)[a > 1])                                   # [30 20] multiply then filter in one expression
```
```javascript
// JavaScript way
const a = [3, 1, 2];                                     // array
console.log(a.map(x => x * 10).filter((_, i) => a[i] > 1));   // [30, 20] chain map + filter
```

Key difference: JavaScript chains `map/filter/reduce` callbacks that run in the JS engine one element at a time. NumPy takes a whole-array expression and runs it in compiled code, with `axis` for 2-D data and operators like `@` for linear algebra.

---

## 🟠 FastAPI Connection
Vector search, scoring and statistics endpoints in FastAPI usually load a NumPy matrix once at startup and answer each request with one vectorized call. Keep the matrix in `app.state` or a module global, and return Python types.

```python
# FastAPI example — cosine-similarity search endpoint
from fastapi import FastAPI                                  # FastAPI
from fastapi.testclient import TestClient                    # test
import numpy as np                                           # numpy

app = FastAPI()                                              # app
DOCS = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])        # pretend vector store, loaded once at startup


@app.post("/similar")                                        # POST /similar
def similar(q: list[float]) -> dict[str, int]:
    v = np.asarray(q)                                        # body list -> array
    sims = (DOCS / np.linalg.norm(DOCS, axis=1, keepdims=True)) @ (v / np.linalg.norm(v))   # cosine
    return {"best": int(sims.argmax())}                      # cast numpy int -> python int


print(TestClient(app).post("/similar", json=[0.1, 1.0]).json())
# Output:
# {'best': 1}
```
Verified: run with TestClient. A plain `def` endpoint runs in a thread pool, which is right for CPU-bound NumPy work (NumPy releases the GIL in many operations).

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `*` expecting matrix multiplication
✅ Correct: `*` is element-wise, use `@` for matrix multiply

```python
import numpy as np
m = np.array([[1, 2], [3, 4]])
print(m * m)     # Wrong for matrix product: [[1 4] [9 16]]
print(m @ m)     # Right: [[7 10] [15 22]]
```

❌ Mistake 2: Mixing up `axis`
✅ Correct: `axis` is the dimension that DISAPPEARS

```python
import numpy as np
m = np.array([[1, 2], [3, 4]])
print(m.sum(axis=0))   # [4 6]  collapses rows -> one value per column
print(m.sum(axis=1))   # [3 7]  collapses columns -> one value per row
```

❌ Mistake 3: Ignoring NaN
✅ Correct: use `nan*` functions or clean data first

```python
import numpy as np
v = np.array([1.0, np.nan, 3.0])
print(v.sum())          # Wrong: nan
print(np.nansum(v))     # Right: 4.0
print(np.nan == np.nan) # False! use np.isnan(x)
```

❌ Mistake 4: Chained boolean conditions with `and` / `or`
✅ Correct: use `&`, `|` with parentheses

```python
import numpy as np
a = np.array([1, 5, 10])
# Wrong: a[(a > 2) and (a < 8)]   -> ValueError: truth value of an array is ambiguous
print(a[(a > 2) & (a < 8)])      # Right: [5]
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import numpy as np
a = np.array([1, 2, 3])
print(a * a, a @ a)
print(np.array([0.1, 0.2]).sum() == 0.3, np.isclose(np.array([0.1, 0.2]).sum(), 0.3))
print(np.nan == np.nan, np.array([np.nan]).max())
```
Answer: `[1 4 9] 14`, then `False True`, then `False nan`. `a * a` is element-wise squares, while `a @ a` for two 1-D vectors is the dot product 1+4+9 = 14. The float sum is 0.30000000000000004, so `== 0.3` is False and `isclose` is True. `NaN` is never equal to itself, and any max/sum that includes NaN becomes NaN (use `np.nanmax`). (Verified on NumPy 2.5.4.)

---

## ⚫ Interview Questions + Answers

Q1: What is a ufunc?
A1: A universal function is a compiled function that operates element by element on arrays and supports broadcasting, such as `np.add`, `np.sqrt`, `np.exp`. Operators like `+` call ufuncs. They also provide `.reduce`, `.accumulate` (e.g. `np.add.reduce` is `sum`).

Q2: What is the difference between `argsort` and `sort`?
A2: `np.sort` returns the sorted values. `np.argsort` returns the indices that would sort the array. Use `argsort` to reorder another array in the same way, or to find top-k: `idx = np.argsort(scores)[::-1][:k]`. For large arrays and small k, `np.argpartition` is faster (O(n)).

Q3: How does `np.where` work with one vs three arguments?
A3: `np.where(cond)` returns the indices where the condition is true (a tuple of arrays). `np.where(cond, x, y)` returns elements from `x` where true, else from `y`, like a vectorized ternary.

Q4: Why is `np.dot` / `@` important for ML?
A4: Neural network layers, embeddings similarity and linear regression are matrix multiplications. NumPy calls optimized BLAS libraries (OpenBLAS, MKL, Accelerate) using SIMD and multiple cores, far faster than Python loops.

Q5: When is a Python loop faster than NumPy?
A5: For very small arrays, the overhead of creating arrays and calling ufuncs can dominate, and for operations that cannot be vectorized (complex branching per item). In those cases use `numba`, Cython or restructure the algorithm.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Math over many numbers: stats, normalization, scoring
- Similarity search with embeddings (`docs @ query`)
- Replacing nested `for` loops over rows and columns
- Preprocessing before ML models

❌ Avoid when:
- You need labeled columns and mixed types (use Pandas)
- The logic per item is complicated and stateful (consider numba or plain Python)
- Exact decimal money math (use `decimal.Decimal` or integers)
- Arrays are tiny and used once

---

## 📊 Visual Diagram
```
 m = [[1, 2, 3],
      [4, 5, 6]]

 axis=0 (collapse rows)        axis=1 (collapse columns)
   1  2  3                        1  2  3  -> 6
   4  5  6                        4  5  6  -> 15
   ↓  ↓  ↓
   5  7  9

 a + b      : [1 2 3 4] + [10 20 30 40]  -> [11 22 33 44]
 a[a > 2]   : mask [F F T T]             -> [3 4]
 docs @ q   : (N,D) @ (D,) -> (N,) scores in one call
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ufunc | Element-wise compiled function | Element-wise compiled function |
| Aggregation | Reduce many values to one | कई values से एक नतीजा |
| axis | Dimension to collapse | जिस dimension को collapse करें |
| keepdims | Keep collapsed axis as size 1 | Collapsed axis को size 1 रखना |
| Mask | Boolean filter array | Boolean filter array |
| argsort | Indices that sort the array | Sort करने वाले indices |
| Dot product | Sum of element products | Elements के गुणनफल का योग |
| NaN | Not a Number (missing) | Number नहीं (missing) |

---

## ⚡ 3-Line Summary
English: NumPy operators and functions work on whole arrays: arithmetic, comparisons, aggregations by `axis`, `where`, `sort` and `@`. Use `keepdims` and `nan*` functions for safe normalization, and `&`/`|` for conditions. Vectorized code is shorter and 10 to 100 times faster than loops.
Hindi: NumPy के operators और functions पूरे arrays पर चलते हैं: arithmetic, comparisons, `axis` से aggregation, `where`, `sort` और `@`। सुरक्षित normalization के लिए `keepdims` और `nan*` functions, और conditions के लिए `&`/`|` इस्तेमाल करें। Vectorized code छोटा होता है और loops से 10 से 100 गुना तेज चलता है।

---

## ➡️ Next Topic
**376. NumPy Broadcasting** — the rule that lets arrays of different shapes work together (for example subtracting a column mean from a whole matrix).
