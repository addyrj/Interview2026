---

# 374. NumPy Arrays
# हिंदी में: NumPy Arrays (तेज़ N-dimensional Arrays)

---

## 🔵 Simple Definition (English)
A NumPy array (`ndarray`) is a fixed-type, N-dimensional grid of numbers stored in one block of memory. Because all items have the same type, NumPy can do math on the whole array at C speed instead of looping in Python.

## 🔵 सरल परिभाषा (Hindi)
NumPy array (`ndarray`) संख्याओं का एक fixed-type, N-dimensional grid है जो memory के एक ही block में रखा जाता है। सभी items का type एक जैसा होने से NumPy पूरे array पर C की speed से math कर सकता है, Python में loop चलाने की जरूरत नहीं पड़ती।

---

## 🔴 Problem it Solves
A Python list stores pointers to separate Python objects. A list of 1 million floats uses a lot of memory and every operation needs a Python-level loop, which is slow. Lists also have no shape: there is no built-in 2-D matrix, no column slicing, no vectorized math. Machine learning needs fast math on millions of numbers (images, embeddings, features), so NumPy was created as the base layer for Pandas, scikit-learn, PyTorch and TensorFlow.

## 🔴 यह क्यों बना? (Hindi)
Python list अलग-अलग Python objects के pointers रखती है। 10 लाख floats की list बहुत memory लेती है और हर operation के लिए Python का loop चाहिए, जो धीमा है। List में shape भी नहीं होती: 2-D matrix, column slicing या vectorized math built-in नहीं है। Machine learning में लाखों संख्याओं (images, embeddings, features) पर तेज math चाहिए, इसलिए NumPy बना, जो Pandas, scikit-learn, PyTorch और TensorFlow की नींव है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → np.array([...]) copies data into ONE contiguous block of memory
Step 2 → Every element has the same dtype (int64, float32, bool, uint8 ...)
Step 3 → shape tells the dimensions, e.g. (2, 3) = 2 rows, 3 columns
Step 4 → strides tell how many bytes to jump per axis (this makes reshape/transpose free)
Step 5 → Basic slicing a[1:4] returns a VIEW (same memory, no copy)
Step 6 → Fancy / boolean indexing a[[0,2]] or a[a>2] returns a COPY
Step 7 → Operations run in compiled C loops over the whole block (vectorization)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → np.array([...]) data को memory के एक ही contiguous block में copy करता है
Step 2 → हर element का dtype एक ही होता है (int64, float32, bool, uint8 ...)
Step 3 → shape dimensions बताती है, जैसे (2, 3) = 2 rows, 3 columns
Step 4 → strides बताते हैं कि हर axis पर कितने bytes आगे जाना है (इसी से reshape/transpose मुफ्त है)
Step 5 → Basic slicing a[1:4] एक VIEW देता है (वही memory, कोई copy नहीं)
Step 6 → Fancy / boolean indexing a[[0,2]] या a[a>2] एक COPY देता है
Step 7 → Operations पूरे block पर compiled C loops में चलते हैं (vectorization)
```

---

## 🟡 Real World Example
An AI app stores 1,000 text embeddings of 768 numbers each as a `(1000, 768)` float32 array and finds similar ones with one matrix multiplication. A photo-filter service holds an image as a `(height, width, 3)` uint8 array and brightens it with `img * 1.2`. A Razorpay fraud model keeps a `(n_transactions, n_features)` matrix for fast scoring.

## 🟡 Real Example Hindi mein
एक AI app 1,000 text embeddings, हर एक 768 संख्याओं का, `(1000, 768)` float32 array में रखता है और एक matrix multiplication से मिलते-जुलते embeddings ढूंढता है। Photo-filter service image को `(height, width, 3)` uint8 array में रखती है और `img * 1.2` से brighten करती है। Razorpay का fraud model तेज scoring के लिए `(n_transactions, n_features)` matrix रखता है।

---

## 💻 Code Example — Basic
```python
# Basic NumPy arrays: creation, attributes, indexing, slicing, boolean mask
import numpy as np                                           # standard alias

a: np.ndarray = np.array([1, 2, 3, 4, 5, 6])                 # from a list
print(a.dtype, a.shape, a.ndim, a.size)                      # type, shape, dims, count
m: np.ndarray = a.reshape(2, 3)                              # 2 rows x 3 cols (a view, no copy)
print(m)                                                     # matrix view
print(m[1, 2], m[:, 0], m[0, 1:])                            # element, column, partial row
print(np.zeros((2, 2)), np.ones(3), np.arange(0, 10, 3))     # common constructors
print(np.linspace(0, 1, 5))                                  # 5 evenly spaced points
print(a[a % 2 == 0])                                         # boolean mask: even numbers
f: np.ndarray = a.astype(np.float32)                         # convert dtype (makes a copy)
print(f.dtype, f.nbytes, a.nbytes)                           # float32 uses half the bytes of int64
print(np.array([1, 2.5, 3]).dtype)                           # mixed ints and floats -> float64

# Output:
# int64 (6,) 1 6
# [[1 2 3]
#  [4 5 6]]
# 6 [1 4] [2 3]
# [[0. 0.]
#  [0. 0.]] [1. 1. 1.] [0 3 6 9]
# [0.   0.25 0.5  0.75 1.  ]
# [2 4 6]
# float32 24 48
# float64
```
Verified: run with NumPy 2.5.4 on Python 3.13.3 (default int is int64 on 64-bit macOS/Linux; on Windows with NumPy 1.x it was int32).

## 💻 Code Example — Advanced
```python
# Production style: image-like batch handling, views vs copies, memory layout, safe validation
from __future__ import annotations                           # forward refs
import numpy as np                                           # numpy
from numpy.typing import NDArray                             # typed arrays


def normalize_batch(batch: NDArray[np.uint8]) -> NDArray[np.float32]:
    """uint8 images (N,H,W,C) -> float32 in [0,1]; validates shape and dtype."""
    if batch.ndim != 4:                                      # fail early with clear message
        raise ValueError(f"expected 4-D (N,H,W,C), got {batch.ndim}-D")
    if batch.dtype != np.uint8:                              # dtype contract
        raise TypeError(f"expected uint8, got {batch.dtype}")
    return batch.astype(np.float32) / 255.0                  # one vectorized pass, no loop


rng = np.random.default_rng(42)                              # modern seeded generator
imgs: NDArray[np.uint8] = rng.integers(0, 256, size=(2, 4, 4, 3), dtype=np.uint8)   # fake images
out = normalize_batch(imgs)                                  # normalize
print(out.shape, out.dtype, bool(out.min() >= 0 and out.max() <= 1))   # shape/type/range check

try:
    normalize_batch(imgs[0])                                 # wrong ndim
except ValueError as e:                                      # handled
    print("ValueError:", e)

base = np.arange(10)                                         # 0..9
view = base[2:5]                                             # slice = VIEW (shares memory)
view[0] = 99                                                 # write through the view
print(base[:6], np.shares_memory(base, view))                # base changed too
cp = base[2:5].copy()                                        # explicit copy
cp[0] = -1                                                   # does not touch base
print(base[2], np.shares_memory(base, cp))                   # still 99, no shared memory

fancy = base[[0, 2, 4]]                                      # fancy indexing = COPY
print(np.shares_memory(base, fancy))                         # False

mat = np.arange(6).reshape(2, 3)                             # C-order (row-major)
print(mat.flags["C_CONTIGUOUS"], mat.T.flags["C_CONTIGUOUS"])   # transpose is a view, not contiguous
print(mat.strides, mat.T.strides)                            # bytes to step per axis (int64 = 8 bytes)

# Output:
# (2, 4, 4, 3) float32 True
# ValueError: expected 4-D (N,H,W,C), got 3-D
# [ 0  1 99  3  4  5] True
# 99 False
# False
# True False
# (24, 8) (8, 24)
```
Verified: run as shown with NumPy 2.5.4.

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python (NumPy) | JavaScript |
|---------|---------------|-----------|
| Array of numbers | `np.array([1,2,3])` | `new Float64Array([1,2,3])` (typed array) |
| Normal list/array | `list` holds anything, slow math | `Array` holds anything, slow math |
| Multi-dimensional | `shape=(2,3)` built in | no built-in; array of arrays |
| Vector math | `a * 2` works on all items | `a.map(x => x * 2)` loop needed |
| Libraries | NumPy, Pandas, PyTorch | TensorFlow.js, mathjs, ndarray (npm) |

```python
# Python way — NumPy
import numpy as np                                       # import
a = np.array([1, 2, 3])                                  # array
print(a * 2)                                             # [2 4 6] (every element)
print([1, 2, 3] * 2)                                     # [1, 2, 3, 1, 2, 3] (plain list repeats!)
```
```javascript
// JavaScript way
const a = new Float64Array([1, 2, 3]);                   // typed array (closest to ndarray)
console.log(a.map(x => x * 2));                          // Float64Array [2, 4, 6]  (needs map)
console.log([1, 2, 3].map(x => x * 2));                  // [2, 4, 6] normal array also needs map
```

Key difference: JavaScript typed arrays are only 1-D and have no vectorized operators, so you always write loops or `map`. NumPy gives N-dimensional arrays with operators (`*`, `+`, `@`) that work on whole arrays at once.

---

## 🟠 FastAPI Connection
NumPy appears in FastAPI ML endpoints: convert the request list to an array, run the model or math, and return plain Python types. Important: NumPy scalar types (`np.float64`, `np.int64`) are not always JSON serializable by FastAPI's default encoder, so cast with `float()` / `int()` or use `.tolist()` for arrays.

```python
# FastAPI example — statistics endpoint backed by NumPy
from fastapi import FastAPI                                  # FastAPI
from fastapi.testclient import TestClient                    # test client
from pydantic import BaseModel, Field                        # validation
import numpy as np                                           # numpy

app = FastAPI()                                              # app


class Scores(BaseModel):
    values: list[float] = Field(min_length=1)                # JSON list in


@app.post("/stats")                                          # POST /stats
def stats(s: Scores) -> dict[str, float]:
    arr = np.asarray(s.values, dtype=np.float64)             # list -> ndarray
    return {"mean": float(arr.mean()), "max": float(arr.max())}   # cast numpy floats to python floats


print(TestClient(app).post("/stats", json={"values": [1, 2, 3, 6]}).json())
# Output:
# {'mean': 3.0, 'max': 6.0}
```
Verified: run with TestClient.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Thinking a slice is a copy
✅ Correct: use `.copy()` when you need an independent array

```python
import numpy as np
a = np.arange(5)
b = a[1:3]            # Wrong assumption: independent copy
b[0] = 100            # changes a too!  a = [0 100 2 3 4]
c = a[1:3].copy()     # Right: independent
```

❌ Mistake 2: Looping over an array in Python
✅ Correct: use vectorized operations

```python
import numpy as np
a = np.arange(1_000_000)
total = 0
for x in a: total += x    # Wrong: slow (Python loop, creates numpy scalars)
total = a.sum()           # Right: one C call
```

❌ Mistake 3: Ignoring dtype (overflow and silent truncation)
✅ Correct: pick the dtype on purpose

```python
import numpy as np
x = np.array([1, 2, 3], dtype=np.uint8)
print(x - 5)                          # Wrong: [252 253 254]  (wraps around, no error)
print(x.astype(np.int16) - 5)         # Right: [-4 -3 -2]
```

❌ Mistake 4: Comparing floats with `==`
✅ Correct: use `np.isclose` / `np.allclose`

```python
import numpy as np
s = np.array([0.1, 0.2]).sum()
print(s == 0.3)                       # Wrong: False
print(np.isclose(s, 0.3))             # Right: True
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import numpy as np
a = np.arange(6)
b = a[1:4]
b[:] = 0
c = a[[1, 2]]
c[:] = 7
print(a)
x = np.array([1, 2, 3], dtype=np.uint8)
print(x - 5)
print([1, 2] * 2, np.array([1, 2]) * 2)
```
Answer: `[0 0 0 0 4 5]`, `[252 253 254]`, then `[1, 2, 1, 2] [2 4]`. `b = a[1:4]` is a view, so `b[:] = 0` zeroes items 1 to 3 of `a`. `c = a[[1, 2]]` is fancy indexing, which makes a copy, so `c[:] = 7` does not change `a`. With NumPy 2, `uint8` array minus Python int 5 stays `uint8`, so 1 - 5 wraps to 252 (no error). A plain list times 2 repeats the list, while an array times 2 multiplies each element. (Verified on NumPy 2.5.4.)

---

## ⚫ Interview Questions + Answers

Q1: Why is NumPy faster than Python lists?
A1: Elements are stored contiguously in one typed block (no per-item Python objects), operations run in compiled C/SIMD loops, and there is no interpreter overhead per element. Memory is also smaller: an int64 array uses 8 bytes per item, while a list of ints uses pointers plus object overhead (about 28+ bytes each).

Q2: What is the difference between a view and a copy?
A2: A view shares memory with the original (basic slicing, `reshape`, `.T`), so changing one changes the other. A copy has its own memory (fancy/boolean indexing, `.copy()`, `astype`). Use `np.shares_memory(a, b)` to check, and `.copy()` when you must not mutate the source.

Q3: What do shape, dtype and strides mean?
A3: `shape` is the size of each dimension, `dtype` is the element type, and `strides` is the number of bytes to step to the next element along each axis. For int64 shape `(2,3)` the strides are `(24, 8)`. Transpose just swaps strides, so it is free.

Q4: What is the difference between `np.array` and `np.asarray`?
A4: `np.array` copies by default. `np.asarray` returns the same object if the input is already an ndarray with the right dtype (no copy), so it is the usual choice at the start of a function.

Q5: When do you use `reshape(-1)`, `flatten()` and `ravel()`?
A5: `reshape(-1)` and `ravel()` return a view when possible (flat 1-D); `flatten()` always returns a copy. `-1` in reshape means "figure this dimension out", for example `a.reshape(-1, 3)`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You do math on large numeric data (features, images, embeddings, signals)
- You need matrices, slicing by column/row and linear algebra
- You feed data to Pandas, scikit-learn, PyTorch, OpenCV

❌ Avoid when:
- Data is mixed types or text records (use Pandas or plain lists/dataclasses)
- Arrays grow one item at a time (`np.append` copies every time; build a list then convert)
- Data is tiny and readability matters more than speed
- Data is bigger than RAM (use memmap, Dask or a database)

---

## 📊 Visual Diagram
```
 a = np.arange(6).reshape(2, 3)

 memory (one block, int64 = 8 bytes each):
 [ 0 | 1 | 2 | 3 | 4 | 5 ]

 shape (2,3)   strides (24, 8)
        col0 col1 col2
 row0 [  0    1    2 ]      a[0, 1] -> 1
 row1 [  3    4    5 ]      a[:, 0] -> [0 3]

 view:  b = a[:, 1]   ──shares memory──►  a
 copy:  c = a[[0,1]]  ──own memory────►   (new block)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ndarray | N-dimensional array object | N-dimensional array object |
| dtype | Element data type | Element का data type |
| shape | Size of each dimension | हर dimension का आकार |
| axis | A dimension index | Dimension का index |
| view | Array sharing memory | Memory बांटने वाला array |
| copy | Array with own memory | अपनी memory वाला array |
| mask | Boolean array used to filter | Filter करने वाला boolean array |
| vectorization | Whole-array operations | पूरे array पर एक साथ operation |

---

## ⚡ 3-Line Summary
English: A NumPy `ndarray` stores same-type numbers in one block, so math on whole arrays runs at C speed. Know `shape`, `dtype`, indexing, and that basic slices are views while fancy indexing makes copies. Avoid Python loops and watch dtype overflow.
Hindi: NumPy `ndarray` एक ही type की संख्याएं एक block में रखता है, इसलिए पूरे array पर math C की speed से चलता है। `shape`, `dtype`, indexing समझें, और याद रखें कि basic slice view है जबकि fancy indexing copy बनाता है। Python loops से बचें और dtype overflow का ध्यान रखें।

---

## ➡️ Next Topic
**375. NumPy Operations** — arithmetic, aggregation with `axis`, sorting, `where`, dot products and the vectorized tools you use every day.
