---

# 373. NumPy — Complete Guide
# हिंदी में: NumPy — पूरी Guide

---

## 🔵 Simple Definition (English)
NumPy (Numerical Python) is the foundation library for numerical computing in Python. Key: `ndarray` — N-dimensional array stored as contiguous memory block (unlike Python lists). NumPy operations are **vectorized** — executed in C, 10-100x faster than Python loops. Used in: data science, ML, embeddings math, image processing.

## 🔵 सरल परिभाषा (Hindi)
NumPy Python में numerical computing का foundation है। Key: `ndarray` — N-dimensional array contiguous memory में। Operations **vectorized** हैं — C में execute, Python loops से 10-100x fast। Data science, ML, embeddings math में use।

---

## 💻 Code Example — Basic
```python
import numpy as np

# ─── Creating arrays ─────────────────────────────────────────────
a = np.array([1, 2, 3, 4, 5])           # 1D array from list
b = np.array([[1, 2, 3], [4, 5, 6]])     # 2D array (2×3 matrix)

print(a.shape)    # (5,)    — shape is a tuple
print(b.shape)    # (2, 3)  — 2 rows, 3 columns
print(a.dtype)    # int64   — element type
print(a.ndim)     # 1       — number of dimensions
print(a.size)     # 5       — total number of elements

# Specialized creation:
np.zeros((3, 4))          # 3×4 array of zeros
np.ones((2, 2))           # 2×2 array of ones
np.eye(3)                 # 3×3 identity matrix
np.arange(0, 10, 2)       # [0, 2, 4, 6, 8] — like range()
np.linspace(0, 1, 5)      # [0, 0.25, 0.5, 0.75, 1.0] — 5 evenly spaced
np.random.rand(3, 3)      # 3×3 uniform random [0, 1)
np.random.randn(3, 3)     # 3×3 standard normal distribution

# ─── Indexing and slicing ─────────────────────────────────────────
a = np.array([10, 20, 30, 40, 50])
print(a[0])        # 10
print(a[-1])       # 50
print(a[1:4])      # [20, 30, 40]
print(a[::2])      # [10, 30, 50]

# 2D indexing:
m = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(m[1, 2])     # 6 — row 1, col 2
print(m[0, :])     # [1, 2, 3] — entire row 0
print(m[:, 1])     # [2, 5, 8] — entire column 1
print(m[1:, 1:])   # [[5,6],[8,9]] — submatrix

# Boolean indexing:
a = np.array([1, -2, 3, -4, 5])
print(a[a > 0])    # [1, 3, 5] — only positive values
a[a < 0] = 0       # set negative values to 0: [1, 0, 3, 0, 5]

# ─── Vectorized operations (NO loops needed!) ─────────────────────
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print(a + b)        # [5, 7, 9]  — element-wise
print(a * b)        # [4, 10, 18]
print(a ** 2)       # [1, 4, 9]
print(np.sqrt(a))   # [1.0, 1.41, 1.73]

# Broadcasting — operations between different shapes:
matrix = np.array([[1, 2, 3], [4, 5, 6]])   # (2, 3)
row = np.array([10, 20, 30])                  # (3,)
print(matrix + row)   # [[11, 22, 33], [14, 25, 36]] — row added to each row
```

## 💻 Code Example — Advanced (AI/ML relevant)
```python
import numpy as np

# ─── Cosine Similarity (critical for embeddings!) ─────────────────
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

# Two embedding vectors:
emb1 = np.array([0.1, 0.2, 0.9, 0.3])
emb2 = np.array([0.1, 0.2, 0.8, 0.3])
print(cosine_similarity(emb1, emb2))   # ~0.997 — very similar!

# Batch cosine similarity (all pairwise):
def batch_cosine_similarity(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
    """Similarity between one query and many corpus vectors."""
    # Normalize:
    query_norm = query / np.linalg.norm(query)
    corpus_norms = corpus / np.linalg.norm(corpus, axis=1, keepdims=True)
    return np.dot(corpus_norms, query_norm)   # (n,) array of similarities

# ─── Matrix operations ────────────────────────────────────────────
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

# Matrix multiplication:
print(A @ B)          # [[19,22],[43,50]] — matmul
print(np.dot(A, B))   # same as @

# Transpose:
print(A.T)            # [[1,3],[2,4]]

# Inverse:
print(np.linalg.inv(A))    # [[-2, 1], [1.5, -0.5]]

# Eigenvalues (used in PCA):
eigenvalues, eigenvectors = np.linalg.eig(A)

# ─── Reshape and stacking ─────────────────────────────────────────
a = np.arange(12)          # [0, 1, 2, ..., 11]

# Reshape:
matrix = a.reshape(3, 4)   # 3×4 matrix
flat = matrix.flatten()    # back to 1D (copy)
view = matrix.ravel()      # back to 1D (view — no copy)

# Stack arrays:
v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])
np.vstack([v1, v2])     # [[1,2,3],[4,5,6]] — vertical stack (adds rows)
np.hstack([v1, v2])     # [1,2,3,4,5,6]    — horizontal stack
np.stack([v1, v2])      # [[1,2,3],[4,5,6]] — new axis

# ─── Aggregations ─────────────────────────────────────────────────
data = np.array([[1, 2, 3], [4, 5, 6]])

print(data.sum())          # 21 — all elements
print(data.sum(axis=0))    # [5, 7, 9] — sum each column
print(data.sum(axis=1))    # [6, 15] — sum each row

print(data.mean())         # 3.5
print(data.std())          # 1.708...
print(data.max())          # 6
print(data.argmax())       # 5 — index of max element

# ─── Performance: NumPy vs Python loop ───────────────────────────
import time

n = 1_000_000

# Python loop:
start = time.perf_counter()
result = sum(x**2 for x in range(n))
py_time = time.perf_counter() - start

# NumPy vectorized:
arr = np.arange(n)
start = time.perf_counter()
result = (arr ** 2).sum()
np_time = time.perf_counter() - start

print(f"Python: {py_time:.3f}s, NumPy: {np_time:.3f}s")
# NumPy is ~10-100x faster!

# ─── Real use case: process embedding batch ───────────────────────
def find_top_k_similar(query_emb: np.ndarray, doc_embs: np.ndarray, k: int = 5) -> list[int]:
    """Find indices of k most similar documents to query."""
    # All cosine similarities in one vectorized call:
    similarities = doc_embs @ query_emb / (
        np.linalg.norm(doc_embs, axis=1) * np.linalg.norm(query_emb)
    )
    top_k_indices = np.argsort(similarities)[-k:][::-1]   # top k, descending
    return top_k_indices.tolist()
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python NumPy:
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
result = a + b    # [5, 7, 9] — vectorized
dot = np.dot(a, b)    # 32
```

```javascript
// JavaScript — no native vectorized math:
const a = [1, 2, 3], b = [4, 5, 6];
const result = a.map((x, i) => x + b[i]);   // manual loop needed
const dot = a.reduce((acc, x, i) => acc + x * b[i], 0);

// Use ml5.js or TensorFlow.js for vectorized math:
const tensor = tf.tensor([1, 2, 3]);
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Python list vs NumPy array
```python
# Wrong — lists don't support vectorized operations:
a = [1, 2, 3]
b = [4, 5, 6]
print(a + b)    # [1, 2, 3, 4, 5, 6] — concatenation, not addition!

# Correct:
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(a + b)    # [5, 7, 9] — element-wise addition
```

❌ Mistake 2: Confusing copy vs view
```python
a = np.array([1, 2, 3, 4, 5])
b = a[1:4]      # SLICE = VIEW (not copy!)
b[0] = 99
print(a)        # [1, 99, 3, 4, 5] ← original changed!

# Get a copy:
b = a[1:4].copy()
b[0] = 99
print(a)        # [1, 2, 3, 4, 5] ← unchanged
```

---

## 🧠 Tricky Interview Question

**Q**: What is broadcasting in NumPy?

**Answer**: Broadcasting allows NumPy to operate on arrays of **different shapes** without copying data. Rules: (1) Dimensions are compared right-to-left. (2) Dimensions match if equal OR one of them is 1. (3) The size-1 dimension is "stretched" to match the other. Example: `(3,4) + (4,)` — the `(4,)` is broadcast to `(3,4)` by repeating 3 times. This enables `matrix + row_vector` without explicit `np.tile()`. Fails if shapes aren't broadcastable: `(3,4) + (3,)` → error (wrong dimension).

---

## ⚫ Interview Questions + Answers

Q1: Why is NumPy faster than Python lists for numerical computation?
A1: (1) **Contiguous memory**: ndarray stores elements in a single block (like C array). Python list stores pointers to objects — cache-unfriendly. (2) **C implementation**: NumPy operations execute in optimized C code — no Python interpreter overhead per element. (3) **Vectorization**: single function call on array vs Python loop per element. (4) **No type overhead**: Python int is an object (28 bytes each). NumPy int64 is 8 bytes. For 1M elements: Python ~28MB, NumPy ~8MB. (5) **SIMD**: NumPy leverages CPU SIMD instructions for parallel element processing.

Q2: What is the difference between `np.dot()` and `@` operator?
A2: For 2D matrices: identical — both do matrix multiplication. For 1D vectors: `np.dot(a, b)` computes the dot product (scalar). `a @ b` for 1D also gives dot product. For N-D arrays: `np.dot` has specific rules about sum along last axis; `@` follows standard matrix multiplication rules. `@` was added in Python 3.5 and is the recommended modern syntax for matmul. For clarity: `@` for matrix multiplication, `*` for element-wise, `np.dot()` for explicit dot product.

Q3: What is `dtype` and why does it matter?
A3: `dtype` is the data type of array elements. Default: `int64` for integers, `float64` for floats. Matters for: (1) Memory: `float32` uses half memory of `float64` — important for large ML datasets. (2) Precision: `float32` has ~7 decimal digits; `float64` ~15. (3) GPU computation: most GPUs prefer `float32`. (4) Interoperability: OpenAI embeddings are `float32`. Specify dtype: `np.array([1.0, 2.0], dtype=np.float32)`. Convert: `arr.astype(np.float32)`.

Q4: How do you normalize vectors for cosine similarity?
A4: Normalization = divide each vector by its L2 norm so all vectors have magnitude 1. Then cosine similarity = just dot product. `norms = np.linalg.norm(vectors, axis=1, keepdims=True); normalized = vectors / norms`. Pre-normalize if you'll compute many similarities — `dot_product` is faster than full cosine similarity. Vector databases like Pinecone auto-normalize when using cosine similarity metric. For embeddings: always normalize before storing for efficient lookup.

Q5: What is `axis` parameter in NumPy aggregations?
A5: `axis=0`: aggregate along rows (collapse rows → result has shape of one row). `axis=1`: aggregate along columns (collapse columns → result has shape of one column). For `data.sum(axis=0)` on shape `(3, 4)`: sum down each column → result shape `(4,)`. For `data.sum(axis=1)`: sum across each row → result shape `(3,)`. Mnemonic: "axis 0 = along dimension 0 (rows) = compressing rows". `None` (default): aggregate everything → scalar.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ndarray | N-dimensional array | N-dimensional array |
| dtype | Data type of elements | Elements का data type |
| shape | Dimensions of array | Array के dimensions |
| vectorization | Operations without loops | Loops बिना operations |
| broadcasting | Operations on diff shapes | Different shapes पर operations |
| axis | Dimension to aggregate along | किस dimension पर aggregate करें |
| view | Slice sharing memory | Memory share करने वाला slice |

---

## ⚡ 3-Line Summary
English: NumPy's `ndarray` stores data in contiguous C memory — vectorized operations are 10-100x faster than Python loops. Use `ndarray` for all numerical work: matrix math, cosine similarity for embeddings, image processing. Key: `axis=0` aggregates along rows, `axis=1` along columns; slices are views (not copies) — use `.copy()` if you need independence.
Hindi: NumPy `ndarray` C memory में store — vectorized operations 10-100x fast। Numerical work, embeddings cosine similarity, image processing के लिए। `axis=0` = rows, `axis=1` = columns। Slices views हैं — copy के लिए `.copy()`।

---

## ➡️ Next Topic
**374. NumPy Advanced** — fancy indexing, structured arrays, memmap. **377. Pandas** — DataFrames, Series, data analysis. **386. OpenAI SDK** — embeddings with numpy arrays.
