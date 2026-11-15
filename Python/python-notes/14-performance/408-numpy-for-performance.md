---

# 408. NumPy for Performance
# हिंदी में: Performance के लिए NumPy (vectorization)

---

## 🔵 Simple Definition (English)
NumPy stores numbers in a compact typed array and runs math on the whole array inside fast C code. This is called vectorization. One line like `a * 2` replaces a Python loop and is often 20-100x faster.

## 🔵 सरल परिभाषा (Hindi)
NumPy numbers को एक compact, typed array में रखता है और पूरे array पर math तेज़ C code में चलाता है। इसे vectorization कहते हैं। `a * 2` जैसी एक line Python loop की जगह ले लेती है और अक्सर 20-100 गुना तेज़ होती है।

---

## 🔴 Problem it Solves
A Python `list` holds pointers to separate int objects. Every `+` inside a loop checks types, allocates objects and runs bytecode. For numeric work (prices, sensor data, embeddings) this is very slow and memory heavy. NumPy keeps raw numbers side by side in memory and loops in C.

## 🔴 यह क्यों बना? (Hindi)
Python `list` में अलग-अलग int objects के pointers होते हैं। Loop में हर `+` पर type check, object allocation और bytecode चलता है। Numeric काम (prices, sensor data, embeddings) में यह बहुत धीमा और memory-भारी है। NumPy raw numbers को memory में साथ-साथ रखता है और loop C में चलाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → np.array allocates ONE contiguous block with a fixed dtype (e.g. float64)
Step 2 → a * 2 calls a precompiled C loop (ufunc) over that block
Step 3 → No Python object is created per element, no type check per element
Step 4 → Broadcasting lets shapes like (1000, 3) and (3,) combine without copying
Step 5 → CPU can use SIMD instructions on the contiguous memory
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → np.array एक ही contiguous block allocate करता है, fixed dtype के साथ
Step 2 → a * 2 पूरे block पर पहले से compile किया C loop (ufunc) चलाता है
Step 3 → हर element के लिए Python object या type check नहीं बनता
Step 4 → Broadcasting से अलग shapes बिना copy के मिल जाते हैं
Step 5 → Contiguous memory पर CPU SIMD instructions इस्तेमाल कर सकता है
```

---

## 🟡 Real World Example
Swiggy computes delivery distance from a rider to 50,000 restaurants: one vectorized haversine formula over arrays of latitudes and longitudes instead of 50,000 Python function calls. An AI app computes cosine similarity of a query vector against 100,000 stored embeddings with a single matrix multiplication.

## 🟡 Real Example Hindi mein
Swiggy एक rider से 50,000 restaurants की दूरी निकालता है: 50,000 Python function calls की जगह latitudes और longitudes के arrays पर एक vectorized haversine formula। AI app query vector का 1 लाख stored embeddings से cosine similarity एक matrix multiplication में निकालता है।

---

## 💻 Code Example — Basic
```python
# Basic NumPy performance (pip install numpy)
import timeit  # timer
from typing import List  # type hints

import numpy as np  # the library

N: int = 1_000_000  # one million numbers
py_list: List[float] = [float(i) for i in range(N)]  # Python list of floats
np_arr: np.ndarray = np.arange(N, dtype=np.float64)  # NumPy array, same values


def py_sum_squares() -> float:
    total: float = 0.0  # running total
    for x in py_list:  # Python loop, one object per step
        total += x * x  # multiply and add in bytecode
    return total  # result


def np_sum_squares() -> float:
    return float(np.sum(np_arr * np_arr))  # whole-array multiply, C loop


print(np.isclose(py_sum_squares(), np_sum_squares()))  # same answer (float tolerance)
# Output: True

t_py: float = min(timeit.repeat(py_sum_squares, number=3, repeat=3))  # best of 3
t_np: float = min(timeit.repeat(np_sum_squares, number=3, repeat=3))  # best of 3
print("numpy at least 10x faster:", t_py / t_np > 10)  # normally 30-100x
# Output: numpy at least 10x faster: True
# (exact speedup depends on your CPU - never hard-code seconds)

a: np.ndarray = np.array([1, 2, 3])  # small array
print(a * 2, a + 10)  # element-wise operations, no loop
# Output: [2 4 6] [11 12 13]
print(a.dtype, a.shape)  # fixed type and shape
# Output: int64 (3,)
```

## 💻 Code Example — Advanced
```python
# Production style: broadcasting, boolean masks, dtype memory, matrix math
from typing import Tuple

import numpy as np  # numpy

rng: np.random.Generator = np.random.default_rng(42)  # reproducible random numbers

# 1) Broadcasting: add a (3,) discount row to every row of a (4, 3) matrix
prices: np.ndarray = np.array([[100, 200, 300]] * 4, dtype=np.float64)  # shape (4, 3)
discount: np.ndarray = np.array([0.9, 0.8, 0.5])  # shape (3,)
print((prices * discount)[0])  # broadcast: each column scaled
# Output: [ 90. 160. 150.]

# 2) Boolean mask replaces a Python "if" in a loop
orders: np.ndarray = np.array([120, 5000, 80, 15000, 900])  # order amounts
big: np.ndarray = orders[orders > 1000]  # keep only amounts above 1000
print(big, big.sum())  # filtered values and their total
# Output: [ 5000 15000] 20000

# 3) dtype controls memory: float32 is half of float64
n: int = 1_000_000  # one million values
f64: np.ndarray = np.zeros(n, dtype=np.float64)  # 8 bytes each
f32: np.ndarray = np.zeros(n, dtype=np.float32)  # 4 bytes each
print(f64.nbytes, f32.nbytes)  # exact memory used by the data
# Output: 8000000 4000000

# 4) Cosine similarity of one query against many embeddings (RAG style)
embeddings: np.ndarray = rng.standard_normal((1000, 64))  # 1000 vectors of size 64
query: np.ndarray = embeddings[7] + 0.01 * rng.standard_normal(64)  # near vector 7


def cosine_scores(matrix: np.ndarray, q: np.ndarray) -> np.ndarray:
    norms: np.ndarray = np.linalg.norm(matrix, axis=1) * np.linalg.norm(q)  # length products
    return (matrix @ q) / norms  # one matrix-vector product, no Python loop


scores: np.ndarray = cosine_scores(embeddings, query)  # similarity to all 1000
best: int = int(np.argmax(scores))  # index of the closest vector
print(best, bool(scores[best] > 0.99))  # should find vector 7
# Output: 7 True

# 5) Views vs copies: slicing is free, fancy indexing copies
base: np.ndarray = np.arange(6)  # [0..5]
view: np.ndarray = base[1:4]  # a view, shares memory
view[0] = 99  # change the view
print(base)  # the original changed too
# Output: [ 0 99  2  3  4  5]
copy: np.ndarray = base[[1, 2]]  # fancy indexing makes a copy
copy[0] = -1  # change the copy
print(base[1])  # original untouched
# Output: 99
shape_info: Tuple[int, ...] = prices.shape  # shape is a tuple
print(shape_info)  # print it
# Output: (4, 3)
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python + NumPy: operate on the whole array
import numpy as np
a = np.array([1, 2, 3, 4])
print(a * 2)            # [2 4 6 8]
print(a[a > 2].sum())   # 7
```
```javascript
// JavaScript: map/filter/reduce (a JS loop each time) or typed arrays
const a = [1, 2, 3, 4];
console.log(a.map(x => x * 2));                          // [2, 4, 6, 8]
console.log(a.filter(x => x > 2).reduce((s, x) => s + x, 0)); // 7
const t = new Float64Array([1, 2, 3, 4]);                // typed array, but no vector math
```

Key differences: JavaScript's `Float64Array` is a typed array like NumPy's storage, but it has no built-in vectorized math, so you still write loops/`map`. NumPy applies the operator to the whole array in C. Python's closest JS libraries are TensorFlow.js or numeric.js.

---

## 🟠 FastAPI Connection
FastAPI handlers must stay fast. Doing a numeric calculation over thousands of rows with NumPy keeps the request short. Heavy NumPy functions release the GIL for much of their work, but for long jobs use a background worker so the event loop is not blocked. Plain `def` endpoints run in a threadpool, which is fine for NumPy.

```python
# FastAPI + NumPy (pip install fastapi httpx numpy)
from typing import Dict, List  # type hints

import numpy as np  # numeric library
from fastapi import FastAPI  # app
from fastapi.testclient import TestClient  # in-process test client
from pydantic import BaseModel, Field  # request validation

app: FastAPI = FastAPI()  # create app


class Prices(BaseModel):
    values: List[float] = Field(min_length=1)  # at least one price


@app.post("/stats")  # sync def -> runs in the threadpool
def stats(body: Prices) -> Dict[str, float]:
    arr: np.ndarray = np.asarray(body.values, dtype=np.float64)  # list -> array
    return {"mean": float(arr.mean()), "p95": float(np.percentile(arr, 95))}  # vectorized stats


client: TestClient = TestClient(app)  # test client
print(client.post("/stats", json={"values": [10, 20, 30, 40]}).json())  # call it
# Output: {'mean': 25.0, 'p95': 38.5}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Looping over a NumPy array in Python
```python
# Wrong - slower than a plain list in many cases:
total = 0
for x in np_arr:
    total += x * x

# Correct - vectorize:
total = (np_arr * np_arr).sum()
```

❌ Mistake 2: Growing an array with `np.append` in a loop
```python
# Wrong - copies the whole array every time (O(n^2)):
arr = np.array([])
for i in range(10_000):
    arr = np.append(arr, i)

# Correct - preallocate, or collect in a list and convert once:
arr = np.arange(10_000)
```

❌ Mistake 3: Silent dtype surprises (overflow, int vs float)
```python
# Wrong - int8 overflows silently:
print(np.array([100, 100], dtype=np.int8).sum(dtype=np.int8))   # -56

# Correct - pick a wide enough dtype:
print(np.array([100, 100], dtype=np.int64).sum())               # 200
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
import numpy as np
a = np.array([1, 2, 3])
b = a[:2]
b[0] = 100
print(a)
print(np.array([1, 2, 3]) + np.array([10]))
print(0.1 + 0.2 == 0.3, np.isclose(0.1 + 0.2, 0.3))
print(np.array([1, 2, 3], dtype=np.uint8) - 5)
```

**Answer**:
```
[100   2   3]
[11 12 13]
False True
[252 253 254]
```
Slicing gives a view, so changing `b` changes `a`. Shape (1,) broadcasts across (3,). Floats are inexact, so use `np.isclose`. The `uint8` subtraction wraps around (modulo 256) with NumPy 2.x when the Python int fits in the dtype; unsigned overflow is silent.

---

## ⚫ Interview Questions + Answers

Q1: Why is NumPy faster than Python lists?
A1: Contiguous typed memory, no per-element Python objects, and loops written in C (often with SIMD). A list stores pointers to boxed objects and runs interpreter bytecode per element.

Q2: What is broadcasting?
A2: A rule that lets arrays of different shapes work together by virtually stretching size-1 or missing dimensions, without copying data. Shapes are compared from the right.

Q3: View vs copy?
A3: Basic slicing returns a view (shared memory). Boolean masks and fancy indexing return copies. Use `.copy()` when you must not change the original.

Q4: When is NumPy NOT faster?
A4: For tiny arrays (call overhead dominates), for code with branching per element that cannot be vectorized, and when you convert between lists and arrays repeatedly.

Q5: How can you speed up code NumPy cannot vectorize?
A5: Use Numba `@njit`, Cython, or rewrite the hot loop in C/Rust. Also consider `float32` to halve memory and bandwidth.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You do math on thousands or millions of numbers
- You need matrix or statistics operations
- You process embeddings, images, or time series

❌ Avoid when:
- The data is tiny (a few items), a list is simpler
- Elements are mixed objects or strings with custom logic
- You build the array item by item in a loop

---

## 📊 Visual Diagram

```
Python list                          NumPy array
[ptr]->int(1)                        | 1 | 2 | 3 | 4 | ...   one block, 8 bytes each
[ptr]->int(2)   objects scattered    ^
[ptr]->int(3)                        a * 2  -> single C loop over the block
loop in Python bytecode              (SIMD, cache friendly)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Vectorization | Applying an operation to a whole array at once | पूरे array पर एक साथ operation |
| ufunc | Universal function compiled in C | C में compile हुआ universal function |
| Broadcasting | Auto-stretching shapes for operations | shapes का अपने आप मेल |
| dtype | Data type of every element | हर element का data type |
| View | Array sharing memory with another | memory साझा करने वाला array |
| Contiguous | Stored side by side in memory | memory में साथ-साथ |

---

## ⚡ 3-Line Summary
English: NumPy stores typed numbers in contiguous memory and loops in C, so vectorized code is 20-100x faster than Python loops. Avoid Python loops over arrays and avoid `np.append` in loops. Watch dtypes, views and copies.
Hindi: NumPy typed numbers को contiguous memory में रखकर C में loop चलाता है, इसलिए vectorized code Python loop से 20-100 गुना तेज़ है। Array पर Python loop और loop में `np.append` से बचें। dtype, view और copy का ध्यान रखें।

---

## ➡️ Next Topic
**409. Cython Basics** — compile typed Python-like code to C when NumPy cannot vectorize your loop.
